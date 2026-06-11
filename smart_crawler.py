#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能季后赛爬虫 - 先检查数据库已有数据，再爬取缺失的比赛
"""
import os
import sys
import time
import logging
from datetime import datetime
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))

from playwright.sync_api import sync_playwright, Page, BrowserContext
from data_importer.pbp_storage import get_pbp_storage

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_database_dates(storage):
    """检查数据库中已有的比赛日期"""
    logger.info("=" * 60)
    logger.info("检查数据库已有数据...")
    logger.info("=" * 60)
    
    # 获取所有已处理的比赛
    with storage.db_manager.get_cursor() as cur:
        cur.execute("""
            SELECT game_id, game_date, visitor_team, home_team 
            FROM game_metadata 
            WHERE game_date >= '2026-04-01'
            ORDER BY game_date
        """)
        processed_games = cur.fetchall()
    
    # 按日期分组统计
    date_stats = {}
    for game in processed_games:
        game_date = str(game[1])
        if game_date not in date_stats:
            date_stats[game_date] = {'count': 0, 'games': []}
        date_stats[game_date]['count'] += 1
        date_stats[game_date]['games'].append(f"{game[2]} @ {game[3]}")
    
    logger.info(f"\n数据库中已有 {len(processed_games)} 场季后赛比赛")
    logger.info("\n按日期统计:")
    
    for date in sorted(date_stats.keys()):
        stats = date_stats[date]
        logger.info(f"  {date}: {stats['count']} 场比赛")
    
    return processed_games, date_stats


def get_missing_games(all_games_df, processed_games):
    """获取缺失的比赛"""
    processed_ids = set([game[0] for game in processed_games])
    
    missing_games = []
    for _, row in all_games_df.iterrows():
        game_id = row['boxscore_url'].split('/')[-1].replace('.html', '')
        if game_id not in processed_ids:
            missing_games.append((game_id, row))
    
    logger.info(f"\n待爬取比赛数: {len(missing_games)}")
    
    # 按日期分组显示缺失的比赛
    missing_by_date = {}
    for game_id, game_info in missing_games:
        game_date = game_info['game_date'].strftime('%Y-%m-%d')
        if game_date not in missing_by_date:
            missing_by_date[game_date] = []
        missing_by_date[game_date].append(f"{game_info['visitor_team']} @ {game_info['home_team']}")
    
    logger.info("\n缺失比赛按日期分布:")
    for date in sorted(missing_by_date.keys()):
        games = missing_by_date[date]
        logger.info(f"  {date}: {len(games)} 场")
        for game in games[:3]:  # 只显示前3场
            logger.info(f"    - {game}")
        if len(games) > 3:
            logger.info(f"    ... 还有 {len(games) - 3} 场")
    
    return missing_games


def is_challenge_page(page: Page) -> bool:
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
    cookies = context.cookies()
    for cookie in cookies:
        if cookie['name'] == 'cf_clearance':
            return True
    return False


def wait_for_challenge_completion(page: Page, context: BrowserContext, max_wait: int = 300) -> bool:
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


def create_browser_context(p, user_data_dir):
    """创建浏览器上下文"""
    return p.chromium.launch_persistent_context(
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


def smart_crawl():
    """智能爬取主函数"""
    logger.info("=" * 60)
    logger.info("智能季后赛PBP爬虫启动")
    logger.info("=" * 60)
    
    storage = get_pbp_storage(season_end=2026)
    
    # 步骤1: 检查数据库已有数据
    processed_games, date_stats = check_database_dates(storage)
    
    # 步骤2: 加载所有季后赛比赛
    games_df = pd.read_csv('CSV/2026_season/all_games_2026.csv', encoding='utf-8-sig')
    
    games_df['game_date'] = games_df['boxscore_url'].str.extract(r'/(\d{8})')[0]
    games_df['game_date'] = pd.to_datetime(games_df['game_date'], format='%Y%m%d')
    
    playoff_games_df = games_df[games_df['game_date'] >= '2026-04-01']
    
    logger.info(f"\n季后赛总比赛数: {len(playoff_games_df)}")
    
    # 步骤3: 获取缺失的比赛（按日期从新到旧排序，从6月份开始往前爬取）
    missing_games = get_missing_games(playoff_games_df, processed_games)
    missing_games.reverse()  # 反转：从最新日期开始往前爬取
    
    if not missing_games:
        logger.info("\n✅ 所有季后赛比赛都已处理完成！")
        storage.close()
        return
    
    # 步骤4: 开始爬取缺失的比赛
    logger.info("\n" + "=" * 60)
    logger.info("开始爬取缺失的比赛...")
    logger.info("=" * 60)
    
    user_data_dir = os.path.join(os.path.dirname(__file__), 'browser_profile')
    os.makedirs(user_data_dir, exist_ok=True)
    
    success_count = 0
    fail_count = 0
    start_time = datetime.now()
    challenge_count = 0
    max_challenges = 3
    browser_restart_count = 0
    
    p = sync_playwright().start()
    context = None
    page = None
    
    try:
        for idx, (game_id, game_info) in enumerate(missing_games):
            logger.info(f"\n\n" + "=" * 60)
            logger.info(f"爬取进度: {idx + 1}/{len(missing_games)}")
            logger.info(f"处理: {game_info['game_date'].strftime('%Y-%m-%d')} - {game_info['visitor_team']} @ {game_info['home_team']} ({game_id})")
            logger.info("=" * 60)
            
            try:
                pbp_url = game_info['boxscore_url'].replace('/boxscores/', '/boxscores/pbp/')
                
                logger.info(f"打开页面: {pbp_url}")
                
                # 检查浏览器是否正常工作
                browser_ok = False
                if context and page:
                    try:
                        page.title()
                        browser_ok = True
                    except Exception:
                        browser_ok = False
                
                if not browser_ok:
                    logger.info("浏览器/页面已关闭，重新启动...")
                    if context:
                        try:
                            context.close()
                        except:
                            pass
                    
                    browser_restart_count += 1
                    logger.info(f"第 {browser_restart_count} 次重启浏览器")
                    
                    context = create_browser_context(p, user_data_dir)
                    page = context.new_page()
                
                try:
                    page.goto(pbp_url, wait_until='domcontentloaded', timeout=60000)
                    time.sleep(10)
                except Exception as nav_error:
                    logger.warning(f"导航警告: {nav_error}")
                    page = context.new_page()
                    time.sleep(5)
                    try:
                        page.goto(pbp_url, wait_until='domcontentloaded', timeout=60000)
                        time.sleep(10)
                    except Exception as e:
                        logger.error(f"重新导航失败: {e}")
                        fail_count += 1
                        
                        if idx < len(missing_games) - 1:
                            time.sleep(60)
                        continue
                
                is_challenge = False
                try:
                    is_challenge = is_challenge_page(page)
                except Exception as e:
                    logger.warning(f"检测验证页面时出错: {e}")
                
                if is_challenge:
                    challenge_count += 1
                    logger.warning(f"⚠️ 第 {challenge_count} 次遇到Cloudflare验证")
                    
                    if challenge_count > max_challenges:
                        logger.error("❌ 遇到多次验证，暂停爬取")
                        break
                    
                    if not wait_for_challenge_completion(page, context):
                        logger.error("❌ 验证超时")
                        fail_count += 1
                        
                        if idx < len(missing_games) - 1:
                            time.sleep(60)
                        continue
                    
                    challenge_count = 0
                
                time.sleep(5)
                
                pbp_table = None
                try:
                    pbp_table = find_pbp_table(page)
                except Exception as e:
                    logger.error(f"查找表格时出错: {e}")
                
                if not pbp_table:
                    logger.error("❌ 未找到PBP表格")
                    fail_count += 1
                    
                    if idx < len(missing_games) - 1:
                        time.sleep(30)
                    continue
                
                pbp_data = parse_pbp_table(pbp_table)
                
                if not pbp_data:
                    logger.warning("❌ 未解析到有效数据")
                    fail_count += 1
                    
                    if idx < len(missing_games) - 1:
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
                
                if idx < len(missing_games) - 1:
                    logger.info(f"\n等待 30 秒...")
                    time.sleep(30)
            
            except Exception as e:
                logger.error(f"处理游戏 {game_id} 时出错: {e}")
                import traceback
                traceback.print_exc()
                fail_count += 1
                
                try:
                    if context:
                        context.close()
                except:
                    pass
                
                context = None
                page = None
                
                if idx < len(missing_games) - 1:
                    time.sleep(60)
        
        logger.info("\n\n" + "=" * 60)
        logger.info("爬取完成！")
        logger.info(f"总计: 成功 {success_count}, 失败 {fail_count}")
        logger.info(f"浏览器重启次数: {browser_restart_count}")
        logger.info(f"总耗时: {datetime.now() - start_time}")
        logger.info(f"最终摘要: {storage.get_import_summary()}")
        logger.info("=" * 60)
        
    finally:
        if context:
            try:
                context.close()
            except:
                pass
        p.stop()
        storage.close()


if __name__ == "__main__":
    smart_crawl()