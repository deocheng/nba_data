#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动验证后自动爬取 - 使用持久化浏览器会话
"""
import os
import sys
import time
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


def has_clearance_cookie(context):
    """检查是否有cf_clearance Cookie"""
    cookies = context.cookies()
    for cookie in cookies:
        if cookie['name'] == 'cf_clearance':
            return True
    return False


def verify_and_crawl():
    """先验证后爬取主函数"""
    logger.info("=" * 60)
    logger.info("手动验证后自动爬取 - PBP数据")
    logger.info("=" * 60)
    
    storage = get_pbp_storage(season_end=2026)
    
    # 加载游戏列表
    import pandas as pd
    games_df = pd.read_csv('CSV/2026_season/all_games_2026.csv', encoding='utf-8-sig')
    
    # 找到未处理的游戏
    unprocessed_games = []
    for _, row in games_df.iterrows():
        game_id = row['boxscore_url'].split('/')[-1].replace('.html', '')
        if not storage.is_game_processed(game_id):
            unprocessed_games.append((game_id, row))
    
    logger.info(f"\n总游戏数: {len(games_df)}")
    logger.info(f"已处理: {len(games_df) - len(unprocessed_games)}")
    logger.info(f"待处理: {len(unprocessed_games)}")
    
    if not unprocessed_games:
        logger.info("所有游戏都已处理完成！")
        storage.close()
        return
    
    # 启动浏览器
    with sync_playwright() as p:
        user_data_dir = os.path.join(os.path.dirname(__file__), 'browser_profile')
        os.makedirs(user_data_dir, exist_ok=True)
        
        logger.info("\n启动浏览器...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--disable-web-security",
                "--allow-running-insecure-content",
                "--disable-dev-shm-usage"
            ],
            viewport={"width": 1920, "height": 1080},
            locale="en-US"
        )
        
        page = context.new_page()
        
        # 步骤1: 先访问主页，等待用户完成验证
        logger.info("\n>>> 正在打开 Basketball Reference 主页...")
        logger.info(">>> 请在浏览器中完成验证（如果需要）")
        logger.info(">>> 验证完成后，请在终端按 Enter 键继续...")
        
        page.goto('https://www.basketball-reference.com', wait_until='domcontentloaded', timeout=120000)
        
        # 等待用户确认
        input("\n>>> 验证完成后，请按 Enter 键继续爬取...")
        
        # 检查是否有clearance cookie
        if has_clearance_cookie(context):
            logger.info("✓ 检测到 cf_clearance Cookie，会话已通过验证")
        else:
            logger.warning("⚠️ 未检测到 cf_clearance Cookie，可能需要重新验证")
        
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
                    page.goto(pbp_url, wait_until='domcontentloaded', timeout=60000)
                    
                    # 等待页面稳定
                    time.sleep(8)
                    
                    # 查找PBP表格 - 使用多种方法
                    pbp_table = None
                    
                    # 方法1: 通过ID匹配
                    pbp_table = page.query_selector('table#pbp')
                    
                    # 方法2: 通过ID包含pbp
                    if not pbp_table:
                        pbp_table = page.query_selector('table[id*="pbp"]')
                    
                    # 方法3: 通过class匹配
                    if not pbp_table:
                        pbp_table = page.query_selector('table.stats_table')
                    
                    # 方法4: 通过caption匹配
                    if not pbp_table:
                        captions = page.query_selector_all('caption')
                        for caption in captions:
                            if 'Play-by-Play' in caption.inner_text():
                                pbp_table = caption.query_selector('..')
                                break
                    
                    # 方法5: 找最长的表格
                    if not pbp_table:
                        all_tables = page.query_selector_all('table')
                        if len(all_tables) > 0:
                            max_rows = 0
                            for table in all_tables:
                                rows = table.query_selector_all('tr')
                                if len(rows) > max_rows:
                                    max_rows = len(rows)
                                    pbp_table = table
                    
                    if not pbp_table:
                        logger.error("❌ 未找到PBP表格")
                        fail_count += 1
                        
                        if idx < len(unprocessed_games) - 1:
                            logger.info("等待 30 秒...")
                            time.sleep(30)
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
                        logger.warning("❌ 未解析到有效数据")
                        fail_count += 1
                        
                        if idx < len(unprocessed_games) - 1:
                            time.sleep(30)
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
                        logger.info(f"\n等待 30 秒...")
                        time.sleep(30)
                
                except Exception as e:
                    logger.error(f"处理游戏 {game_id} 时出错: {e}")
                    import traceback
                    traceback.print_exc()
                    fail_count += 1
                    
                    if idx < len(unprocessed_games) - 1:
                        time.sleep(60)
            
            logger.info("\n\n" + "=" * 60)
            logger.info("爬取完成！")
            logger.info(f"总计: 成功 {success_count}, 失败 {fail_count}")
            logger.info(f"总耗时: {datetime.now() - start_time}")
            logger.info(f"最终摘要: {storage.get_import_summary()}")
            logger.info("=" * 60)
            
        finally:
            context.close()
            storage.close()


if __name__ == "__main__":
    verify_and_crawl()
