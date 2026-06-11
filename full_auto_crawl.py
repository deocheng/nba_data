#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整批量爬取脚本
"""
import os
import sys
import time
import random
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from playwright.sync_api import sync_playwright
from data_importer.pbp_storage import get_pbp_storage

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def full_auto_crawl():
    """完整批量爬取"""
    logger.info("=" * 60)
    logger.info("开始完整批量爬取PBP数据")
    logger.info("=" * 60)
    
    storage = get_pbp_storage(season_end=2026)
    
    # 加载游戏列表
    import pandas as pd
    games_df = pd.read_csv('CSV/2026_season/all_games_2026.csv', encoding='utf-8-sig')
    
    # 找到未处理的游戏
    all_games = []
    unprocessed_games = []
    
    for _, row in games_df.iterrows():
        game_id = row['boxscore_url'].split('/')[-1].replace('.html', '')
        all_games.append((game_id, row))
        
        if not storage.is_game_processed(game_id):
            unprocessed_games.append((game_id, row))
    
    logger.info(f"\n总游戏数: {len(all_games)}")
    logger.info(f"已处理: {len(all_games) - len(unprocessed_games)}")
    logger.info(f"待处理: {len(unprocessed_games)}")
    
    if not unprocessed_games:
        logger.info("所有游戏都已经处理完毕！")
        storage.close()
        return
    
    # 启动浏览器
    with sync_playwright() as p:
        user_data_dir = os.path.join(os.path.dirname(__file__), 'browser_profile')
        os.makedirs(user_data_dir, exist_ok=True)
        
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
        
        success_count = 0
        fail_count = 0
        start_time = datetime.now()
        
        try:
            for idx, (game_id, game_info) in enumerate(unprocessed_games):
                logger.info(f"\n\n" + "=" * 60)
                logger.info(f"进度: {idx + 1}/{len(unprocessed_games)}")
                logger.info(f"处理: {game_info['visitor_team']} @ {game_info['home_team']} ({game_id})")
                logger.info("=" * 60)
                
                try:
                    # 构建PBP URL
                    pbp_url = game_info['boxscore_url'].replace('/boxscores/', '/boxscores/pbp/')
                    
                    logger.info(f"打开页面: {pbp_url}")
                    
                    # 导航
                    page.goto(pbp_url, wait_until='domcontentloaded', timeout=60000)
                    
                    # 等待验证
                    verification_passed = False
                    max_wait = 300  # 5分钟
                    
                    for wait_time in range(max_wait):
                        time.sleep(3)
                        
                        try:
                            content = page.content()
                            
                            # 检查是否有验证页面
                            is_verification = False
                            verification_keywords = ['Just a moment', 'Checking your browser', 
                                               'Cloudflare', 'challenge']
                            if any(kw in content for kw in verification_keywords):
                                is_verification = True
                            
                            if is_verification:
                                if wait_time % 10 == 0:
                                    logger.info(f"等待验证... ({wait_time * 3}/{max_wait * 3}秒)")
                                continue
                            
                            # 检查是否有内容
                            if 'Play-by-Play' in content or len(page.query_selector_all('table')) > 5:
                                verification_passed = True
                                break
                        except Exception as e:
                            logger.warning(f"检查验证状态时出错: {e}")
                    
                    if not verification_passed:
                        logger.warning("⚠️ 验证等待超时，继续尝试...")
                    
                    # 等待页面稳定
                    time.sleep(10)
                    
                    # 查找PBP表格
                    logger.info("\n查找PBP表格...")
                    
                    all_tables = page.query_selector_all('table')
                    logger.info(f"页面共 {len(all_tables)} 个表格")
                    
                    pbp_table = None
                    
                    # 方法1: ID匹配
                    for idx_table, table in enumerate(all_tables):
                        table_id = table.get_attribute('id') or ''
                        if table_id == 'pbp' or 'pbp' in table_id.lower():
                            logger.info(f"✓ 通过ID找到PBP表格 (表格 {idx_table + 1})")
                            pbp_table = table
                            break
                    
                    # 方法2: 通过行数判断
                    if not pbp_table:
                        for idx_table, table in enumerate(all_tables):
                            rows = table.query_selector_all('tr')
                            if len(rows) > 100:  # PBP表格通常比较长
                                logger.info(f"✓ 通过行数找到PBP表格 (表格 {idx_table + 1}, {len(rows)} 行)")
                                pbp_table = table
                                break
                    
                    # 方法3: 找最后一个大表格
                    if not pbp_table:
                        logger.warning("尝试查找最后一个表格...")
                        if len(all_tables) > 0:
                            pbp_table = all_tables[-1]
                    
                    if not pbp_table:
                        logger.error("❌ 未找到PBP表格")
                        fail_count += 1
                        
                        # 等待时间短一点
                        if idx < len(unprocessed_games) - 1:
                            logger.info("等待10秒...")
                            time.sleep(10)
                        continue
                    
                    # 解析数据
                    logger.info("解析PBP数据...")
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
                        logger.warning("未解析到有效数据")
                        fail_count += 1
                        
                        if idx < len(unprocessed_games) - 1:
                            logger.info("等待10秒...")
                            time.sleep(10)
                        continue
                    
                    logger.info(f"✓ 解析到 {len(pbp_data)} 条记录")
                    
                    # 保存到数据库
                    result = storage.process_single_game(game_info.to_dict(), pbp_data)
                    
                    if result.get('success'):
                        logger.info("✅ 保存成功！")
                        success_count += 1
                    else:
                        logger.error(f"❌ 保存失败: {result.get('error')}")
                        fail_count += 1
                    
                    # 打印进度
                    elapsed = datetime.now() - start_time
                    logger.info(f"\n累计: 成功 {success_count}, 失败 {fail_count}, 耗时 {elapsed}")
                    
                    summary = storage.get_import_summary()
                    logger.info(f"数据库摘要: {summary}")
                    
                    # 间隔时间
                    if idx < len(unprocessed_games) - 1:
                        wait_seconds = 30  # 30秒间隔
                        logger.info(f"\n等待 {wait_seconds} 秒...")
                        time.sleep(wait_seconds)
                
                except Exception as e:
                    logger.error(f"处理游戏 {game_id} 时出错: {e}")
                    import traceback
                    traceback.print_exc()
                    fail_count += 1
                    
                    # 出错后多等待一会儿
                    if idx < len(unprocessed_games) - 1:
                        logger.info("等待60秒后继续...")
                        time.sleep(60)
            
            logger.info("\n\n" + "=" * 60)
            logger.info("批量爬取完成！")
            logger.info(f"总计: 成功 {success_count}, 失败 {fail_count}")
            logger.info(f"总耗时: {datetime.now() - start_time}")
            logger.info(f"最终数据库摘要: {storage.get_import_summary()}")
            logger.info("=" * 60)
            
        finally:
            context.close()
            storage.close()


if __name__ == "__main__":
    full_auto_crawl()
