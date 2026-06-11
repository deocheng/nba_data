#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
先完成验证，再自动爬取的方案
"""
import os
import sys
import time
import logging
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from playwright.sync_api import sync_playwright
from data_importer.pbp_storage import get_pbp_storage

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_and_crawl():
    """先验证，再爬取"""
    
    logger.info("=" * 60)
    logger.info("NBA PBP 爬虫 - 验证优先模式")
    logger.info("=" * 60)
    
    # 初始化存储
    storage = get_pbp_storage(season_end=2026)
    
    # 加载游戏列表
    import pandas as pd
    games_df = pd.read_csv('CSV/2026_season/all_games_2026.csv', encoding='utf-8-sig')
    
    # 获取未处理的游戏
    unprocessed = []
    for _, row in games_df.iterrows():
        game_id = row['boxscore_url'].split('/')[-1].replace('.html', '')
        if not storage.is_game_processed(game_id):
            unprocessed.append(row)
    
    logger.info(f"总游戏数: {len(games_df)}")
    logger.info(f"已处理: {len(games_df) - len(unprocessed)}")
    logger.info(f"待处理: {len(unprocessed)}")
    
    if not unprocessed:
        logger.info("所有游戏都已处理完成！")
        return
    
    # 启动浏览器
    with sync_playwright() as p:
        user_data_dir = os.path.join(os.path.dirname(__file__), 'browser_profile')
        os.makedirs(user_data_dir, exist_ok=True)
        
        logger.info(f"使用浏览器Profile: {user_data_dir}")
        
        # 使用持久化上下文
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ],
            viewport={"width": 1920, "height": 1080},
            locale="en-US"
        )
        
        page = context.new_page()
        
        try:
            # 步骤1: 先访问主页，等待您完成验证
            logger.info("\n正在打开 Basketball Reference 主页...")
            logger.info("请在浏览器中完成验证（如果需要）")
            logger.info("验证完成后，请在终端按任意键继续...")
            
            page.goto('https://www.basketball-reference.com', wait_until='domcontentloaded', timeout=60000)
            
            # 等待用户确认
            input("\n>>> 验证完成后，请按 Enter 键继续爬取...")
            
            logger.info("\n开始爬取...")
            
            success_count = 0
            failed_count = 0
            
            for idx, game_info in enumerate(unprocessed):
                game_id = game_info['boxscore_url'].split('/')[-1].replace('.html', '')
                
                logger.info(f"\n[{idx + 1}/{len(unprocessed)}] 处理: {game_info['visitor_team']} @ {game_info['home_team']} ({game_id})")
                
                try:
                    # 访问 PBP 页面
                    pbp_url = game_info['boxscore_url'].replace('/boxscores/', '/boxscores/pbp/')
                    page.goto(pbp_url, wait_until='domcontentloaded', timeout=60000)
                    
                    # 等待页面加载
                    time.sleep(3)
                    
                    # 查找 PBP 表格
                    pbp_table = None
                    selectors = ['table#pbp', 'table[id*="pbp"]', 'table.stats_table', 'table']
                    
                    for selector in selectors:
                        tables = page.query_selector_all(selector)
                        for table in tables:
                            headers = table.query_selector_all('thead th')
                            header_texts = [h.inner_text().strip().lower() for h in headers]
                            if any('time' in h or 'period' in h or 'score' in h for h in header_texts):
                                pbp_table = table
                                logger.info(f"✓ 找到PBP表格")
                                break
                        if pbp_table:
                            break
                    
                    if not pbp_table:
                        logger.warning("未找到PBP表格，跳过")
                        failed_count += 1
                        continue
                    
                    # 解析数据
                    rows = pbp_table.query_selector_all('tr')
                    pbp_data = []
                    
                    for row_elem in rows:
                        try:
                            cells = row_elem.query_selector_all('td, th')
                            cell_texts = [cell.inner_text().strip() for cell in cells]
                            
                            if len(cell_texts) >= 4:
                                pbp_data.append({
                                    'row': len(pbp_data),
                                    'cells': cell_texts
                                })
                        except:
                            continue
                    
                    if not pbp_data:
                        logger.warning("未解析到数据，跳过")
                        failed_count += 1
                        continue
                    
                    # 保存到数据库
                    result = storage.process_single_game(game_info.to_dict(), pbp_data)
                    
                    if result.get('success'):
                        logger.info(f"✓ 成功保存 {len(pbp_data)} 条记录")
                        success_count += 1
                    else:
                        logger.error(f"✗ 保存失败: {result.get('error')}")
                        failed_count += 1
                    
                except Exception as e:
                    logger.error(f"爬取失败: {e}")
                    import traceback
                    traceback.print_exc()
                    failed_count += 1
                
                # 不是最后一个游戏时延迟
                if idx < len(unprocessed) - 1:
                    delay = 30
                    logger.info(f"等待 {delay} 秒...")
                    time.sleep(delay)
                
                # 每爬5个游戏打印进度
                if (idx + 1) % 5 == 0:
                    summary = storage.get_import_summary()
                    logger.info(f"\n当前进度: 成功 {success_count} | 失败 {failed_count}")
                    logger.info(f"导入摘要: {summary}")
                    
                    # 询问是否继续
                    choice = input("\n>>> 是否继续？(Y/n): ").strip().lower()
                    if choice == 'n':
                        logger.info("用户停止爬取")
                        break
            
            logger.info("\n" + "=" * 60)
            logger.info("爬取完成!")
            logger.info(f"成功: {success_count} | 失败: {failed_count}")
            logger.info(f"最终摘要: {storage.get_import_summary()}")
            logger.info("=" * 60)
            
        finally:
            context.close()
            storage.close()

if __name__ == "__main__":
    setup_and_crawl()
