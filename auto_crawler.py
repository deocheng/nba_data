#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动爬取PBP数据 - 使用持久化浏览器会话
"""
import os
import sys
import time
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from playwright.sync_api import sync_playwright, Page, BrowserContext
from data_importer.pbp_storage import get_pbp_storage

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def is_challenge_page(page: Page) -> bool:
    """检测是否为Cloudflare验证页面"""
    try:
        title = page.title()
        if title and ('Just a moment' in title or '请稍候' in title):
            return True
        
        content = page.content()
        challenge_keywords = [
            'Checking your browser',
            'Cloudflare',
            'cdn-cgi/challenge-platform',
            'cf-challenge'
        ]
        if any(kw in content for kw in challenge_keywords):
            return True
        
        if '/cdn-cgi/' in page.url:
            return True
        
        return False
    except Exception as e:
        logger.warning(f"检测验证页面时出错: {e}")
        return False


def has_clearance_cookie(context: BrowserContext) -> bool:
    """检查是否有cf_clearance Cookie"""
    cookies = context.cookies()
    for cookie in cookies:
        if cookie['name'] == 'cf_clearance':
            logger.debug(f"找到 cf_clearance Cookie: {cookie['domain']}")
            return True
    return False


def wait_for_challenge_completion(page: Page, context: BrowserContext, max_wait: int = 300) -> bool:
    """等待Cloudflare验证完成"""
    logger.info("等待验证完成...")
    
    for wait_time in range(max_wait):
        time.sleep(1)
        
        if has_clearance_cookie(context):
            logger.info("✓ 检测到 cf_clearance Cookie，验证完成！")
            return True
        
        if not is_challenge_page(page):
            title = page.title()
            if title and 'Just a moment' not in title and '请稍候' not in title:
                logger.info("✓ 页面标题正常，验证完成！")
                return True
        
        if wait_time % 30 == 0 and wait_time > 0:
            logger.info(f"等待中... ({wait_time}/{max_wait}秒)")
    
    logger.warning("等待验证超时")
    return False


def find_pbp_table(page: Page):
    """查找PBP表格"""
    methods = [
        ('table#pbp', 'ID匹配'),
        ('table[id*="pbp"]', 'ID包含pbp'),
        ('table.stats_table', 'class匹配'),
        ('table.sortable', 'sortable表格')
    ]
    
    for selector, method_name in methods:
        table = page.query_selector(selector)
        if table:
            logger.info(f"✓ 通过{method_name}找到表格")
            return table
    
    logger.info("尝试通过行数查找...")
    all_tables = page.query_selector_all('table')
    if len(all_tables) > 0:
        max_rows = 0
        best_table = None
        for table in all_tables:
            rows = table.query_selector_all('tr')
            if len(rows) > max_rows:
                max_rows = len(rows)
                best_table = table
        
        if best_table and max_rows > 50:
            logger.info(f"✓ 通过行数找到表格 ({max_rows}行)")
            return best_table
    
    return None


def parse_pbp_table(table) -> list:
    """解析PBP表格数据"""
    pbp_data = []
    rows = table.query_selector_all('tr')
    
    for row_elem in rows:
        try:
            cells = row_elem.query_selector_all('td, th')
            cell_texts = [cell.inner_text().strip() for cell in cells]
            
            if len(cell_texts) >= 4:
                pbp_data.append({
                    'row': len(pbp_data),
                    'cells': cell_texts
                })
        except Exception as e:
            logger.debug(f"解析行时出错: {e}")
            continue
    
    return pbp_data


def auto_crawl():
    """自动爬取主函数"""
    logger.info("=" * 60)
    logger.info("自动PBP爬虫启动")
    logger.info("=" * 60)
    
    storage = get_pbp_storage(season_end=2026)
    
    import pandas as pd
    games_df = pd.read_csv('CSV/2026_season/all_games_2026.csv', encoding='utf-8-sig')
    
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
    
    user_data_dir = os.path.join(os.path.dirname(__file__), 'browser_profile')
    os.makedirs(user_data_dir, exist_ok=True)
    
    success_count = 0
    fail_count = 0
    start_time = datetime.now()
    challenge_count = 0
    max_challenges = 3
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--disable-web-security",
                "--allow-running-insecure-content",
                "--disable-dev-shm-usage",
                "--no-sandbox"
            ],
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = context.new_page()
        
        try:
            for idx, (game_id, game_info) in enumerate(unprocessed_games):
                logger.info(f"\n\n" + "=" * 60)
                logger.info(f"进度: {idx + 1}/{len(unprocessed_games)}")
                logger.info(f"处理: {game_info['visitor_team']} @ {game_info['home_team']} ({game_id})")
                logger.info("=" * 60)
                
                try:
                    pbp_url = game_info['boxscore_url'].replace('/boxscores/', '/boxscores/pbp/')
                    
                    logger.info(f"打开页面: {pbp_url}")
                    page.goto(pbp_url, wait_until='domcontentloaded', timeout=120000)
                    
                    if is_challenge_page(page):
                        challenge_count += 1
                        logger.warning(f"⚠️ 第 {challenge_count} 次遇到Cloudflare验证")
                        
                        if challenge_count > max_challenges:
                            logger.error("❌ 遇到多次验证，暂停爬取")
                            break
                        
                        if not wait_for_challenge_completion(page, context):
                            logger.error("❌ 验证超时")
                            fail_count += 1
                            
                            if idx < len(unprocessed_games) - 1:
                                time.sleep(60)
                            continue
                        
                        challenge_count = 0
                    
                    time.sleep(5)
                    
                    pbp_table = find_pbp_table(page)
                    
                    if not pbp_table:
                        logger.error("❌ 未找到PBP表格")
                        fail_count += 1
                        
                        if idx < len(unprocessed_games) - 1:
                            time.sleep(30)
                        continue
                    
                    pbp_data = parse_pbp_table(pbp_table)
                    
                    if not pbp_data:
                        logger.warning("❌ 未解析到有效数据")
                        fail_count += 1
                        
                        if idx < len(unprocessed_games) - 1:
                            time.sleep(30)
                        continue
                    
                    logger.info(f"✓ 解析到 {len(pbp_data)} 条记录")
                    
                    result = storage.process_single_game(game_info.to_dict(), pbp_data)
                    
                    if result.get('success'):
                        logger.info("✅ 保存成功！")
                        success_count += 1
                    else:
                        logger.error(f"❌ 保存失败: {result.get('error')}")
                        fail_count += 1
                    
                    elapsed = datetime.now() - start_time
                    logger.info(f"\n累计: 成功 {success_count}, 失败 {fail_count}, 耗时 {elapsed}")
                    summary = storage.get_import_summary()
                    logger.info(f"数据库摘要: {summary}")
                    
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
    auto_crawl()
