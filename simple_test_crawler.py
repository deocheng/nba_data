#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试爬虫 - 爬取20251126日期的游戏
"""

import sys
import os
import time
import random
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright
from data_importer.pbp_storage import get_pbp_storage
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    storage = get_pbp_storage(season_end=2026)
    
    # 加载游戏列表
    games_df = pd.read_csv('CSV/2026_season/all_games_2026.csv', encoding='utf-8-sig')
    
    # 获取20251126日期的游戏
    target_date = '20251126'
    games_on_date = []
    
    for _, row in games_df.iterrows():
        game_id = row['boxscore_url'].split('/')[-1].replace('.html', '')
        if game_id.startswith(target_date):
            games_on_date.append(row)
    
    logger.info(f"找到 {len(games_on_date)} 场游戏在 {target_date}")
    
    # 显示这一天的游戏
    logger.info("\n这一天的游戏列表:")
    for i, game_info in enumerate(games_on_date):
        game_id = game_info['boxscore_url'].split('/')[-1].replace('.html', '')
        status = "✓ 已处理" if storage.is_game_processed(game_id) else "✗ 未处理"
        logger.info(f"{i+1}. {status} - {game_info['visitor_team']} @ {game_info['home_team']} ({game_id})")
    
    # 只爬取未处理的游戏
    unprocessed_games = []
    for game_info in games_on_date:
        game_id = game_info['boxscore_url'].split('/')[-1].replace('.html', '')
        if not storage.is_game_processed(game_id):
            unprocessed_games.append(game_info)
    
    logger.info(f"\n未处理游戏数: {len(unprocessed_games)}")
    
    if not unprocessed_games:
        logger.info("该日期的游戏都已处理完毕！")
        storage.close()
        return
    
    # 启动浏览器
    with sync_playwright() as p:
        user_data_dir = os.path.join(os.path.dirname(__file__), 'browser_profile')
        os.makedirs(user_data_dir, exist_ok=True)
        
        logger.info(f"\n使用持久化浏览器配置: {user_data_dir}")
        logger.info("请在浏览器中完成Cloudflare验证...")
        
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            channel='chrome',
            args=[
                '--disable-blink-features=AutomationControlled',
                '--start-maximized'
            ],
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = context.new_page()
        
        try:
            # 先访问主页
            page.goto('https://www.basketball-reference.com', wait_until='domcontentloaded', timeout=60000)
            logger.info("\n请在浏览器中完成Cloudflare验证...")
            logger.info("验证完成后，我会自动开始爬取...")
            
            # 等待页面稳定，给用户时间完成验证
            time.sleep(10)
            
            # 爬取游戏
            success_count = 0
            failed_count = 0
            
            for idx, game_info in enumerate(unprocessed_games):
                game_id = game_info['boxscore_url'].split('/')[-1].replace('.html', '')
                
                logger.info(f"\n进度: {idx + 1}/{len(unprocessed_games)}")
                logger.info(f"处理: {game_info['visitor_team']} @ {game_info['home_team']} ({game_id})")
                
                try:
                    pbp_url = game_info['boxscore_url'].replace('/boxscores/', '/boxscores/pbp/')
                    logger.info(f"加载页面: {pbp_url}")
                    
                    page.goto(pbp_url, wait_until='domcontentloaded', timeout=120000)
                    
                    # 等待验证完成或页面加载
                    logger.info("等待Cloudflare验证完成或页面加载...")
                    max_wait = 60  # 最多等待60秒
                    waited = 0
                    content = ""
                    
                    while waited < max_wait:
                        content = page.content()
                        
                        # 检查是否还有验证
                        is_verification = (
                            "Just a moment" in content or
                            "Checking your browser" in content or
                            "Cloudflare" in content and "challenge" in content.lower()
                        )
                        
                        if is_verification:
                            logger.info("仍在验证中，请手动完成...")
                            time.sleep(3)
                            waited += 3
                            continue
                        
                        # 检查是否有PBP内容
                        if "Play-by-Play" in content or "pbp" in content.lower():
                            logger.info("验证完成，页面加载成功！")
                            break
                        
                        time.sleep(2)
                        waited += 2
                    
                    # 查找PBP表格，使用多种方式
                    pbp_table = (
                        page.query_selector('table#pbp') or 
                        page.query_selector('table[id*="pbp"]') or 
                        page.query_selector('table.stats_table') or
                        page.query_selector('table.sortable') or
                        page.query_selector('table')
                    )
                    
                    if not pbp_table:
                        logger.warning(f"未找到PBP表格，保存调试信息")
                        # 保存页面内容用于调试
                        debug_dir = os.path.join(os.path.dirname(__file__), 'debug')
                        os.makedirs(debug_dir, exist_ok=True)
                        debug_file = os.path.join(debug_dir, f'{game_id}_debug.html')
                        with open(debug_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        logger.info(f"已保存调试页面到: {debug_file}")
                        failed_count += 1
                        continue
                    
                    # 解析数据
                    rows = pbp_table.query_selector_all('tr')
                    pbp_data = []
                    
                    for row_idx, row_elem in enumerate(rows):
                        cells = row_elem.query_selector_all('td, th')
                        cell_texts = [cell.inner_text().strip() for cell in cells]
                        
                        if len(cell_texts) >= 4:
                            pbp_data.append({
                                'row': row_idx,
                                'cells': cell_texts
                            })
                    
                    if not pbp_data:
                        logger.warning(f"未解析到PBP记录，跳过")
                        failed_count += 1
                        continue
                    
                    logger.info(f"解析到 {len(pbp_data)} 条记录")
                    
                    # 保存到数据库
                    result = storage.process_single_game(game_info.to_dict(), pbp_data)
                    
                    if result.get('success'):
                        logger.info("✓ 保存成功！")
                        success_count += 1
                    else:
                        logger.error(f"✗ 保存失败: {result.get('error')}")
                        failed_count += 1
                    
                except Exception as e:
                    logger.error(f"爬取失败: {e}")
                    import traceback
                    traceback.print_exc()
                    failed_count += 1
                
                # 等待
                if idx < len(unprocessed_games) - 1:
                    delay = random.uniform(25, 35)
                    logger.info(f"等待 {delay:.1f} 秒...")
                    time.sleep(delay)
            
            logger.info("\n" + "=" * 60)
            logger.info(f"测试完成！成功: {success_count}, 失败: {failed_count}")
            logger.info("=" * 60)
            
        finally:
            context.close()
    
    storage.close()

if __name__ == '__main__':
    main()
