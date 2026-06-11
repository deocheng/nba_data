#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动检测验证状态，不需要手动输入
"""
import os
import sys
import time
import logging

sys.path.insert(0, os.path.dirname(__file__))

from playwright.sync_api import sync_playwright
from data_importer.pbp_storage import get_pbp_storage

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 测试的未处理比赛
TEST_GAME_URL = 'https://www.basketball-reference.com/boxscores/pbp/202511260OKC.html'
TEST_GAME_ID = '202511260OKC'

def auto_test():
    """自动测试，不需要手动输入"""
    logger.info("=" * 60)
    logger.info("测试单场比赛爬取 - 自动检测验证状态")
    logger.info(f"目标游戏: {TEST_GAME_ID}")
    logger.info("=" * 60)
    
    storage = get_pbp_storage(season_end=2026)
    
    # 检查是否已处理
    if storage.is_game_processed(TEST_GAME_ID):
        logger.info(f"游戏 {TEST_GAME_ID} 已经处理过了！")
        storage.close()
        return
    
    # 加载游戏列表
    import pandas as pd
    games_df = pd.read_csv('CSV/2026_season/all_games_2026.csv', encoding='utf-8-sig')
    test_game_info = None
    for _, row in games_df.iterrows():
        game_id = row['boxscore_url'].split('/')[-1].replace('.html', '')
        if game_id == TEST_GAME_ID:
            test_game_info = row
            break
    
    if test_game_info is None:
        logger.error(f"找不到游戏信息: {TEST_GAME_ID}")
        storage.close()
        return
    
    logger.info(f"\n比赛信息: {test_game_info['visitor_team']} @ {test_game_info['home_team']}")
    
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
        
        try:
            logger.info("\n正在打开页面...")
            page.goto(TEST_GAME_URL, wait_until='domcontentloaded', timeout=60000)
            
            logger.info("\n请在浏览器中完成验证（如果需要）")
            logger.info("我会每3秒自动检测一次验证状态...")
            
            verification_passed = False
            max_wait = 300  # 最多等待5分钟
            
            for wait_time in range(max_wait):
                time.sleep(3)
                content = page.content()
                
                # 检查是否有验证页面
                is_verification = False
                verification_keywords = ['Just a moment', 'Checking your browser', 
                                    'Cloudflare', 'challenge']
                if any(kw in content for kw in verification_keywords):
                    is_verification = True
                
                if is_verification:
                    if wait_time % 10 == 0:  # 每30秒提示一次
                        logger.info(f"等待验证... ({wait_time * 3}/{max_wait * 3}秒)")
                    continue
                
                # 检查是否有 PBP 内容
                if 'Play-by-Play' in content or 'pbp' in content.lower() or len(page.query_selector_all('table')) > 2:
                    logger.info("✓ 验证通过或无验证，继续！")
                    verification_passed = True
                    break
            
            if not verification_passed:
                logger.warning("⚠️ 验证等待超时，但我继续尝试解析...")
            
            logger.info("\n等待页面稳定...")
            time.sleep(5)
            
            # 查找 PBP 表格
            logger.info("\n查找 PBP 表格...")
            pbp_table = None
            
            selectors = ['table#pbp', 'table[id*="pbp"]', 'table.stats_table', 'table']
            
            for selector in selectors:
                tables = page.query_selector_all(selector)
                logger.info(f"选择器 '{selector}': 找到 {len(tables)} 个表格")
                
                for idx, table in enumerate(tables):
                    headers = table.query_selector_all('thead th')
                    header_texts = [h.inner_text().strip().lower() for h in headers]
                    
                    if any('time' in h or 'period' in h or 'score' in h or 'quarter' in h for h in header_texts):
                        pbp_table = table
                        logger.info(f"✓ 找到 PBP 表格！")
                        break
                if pbp_table:
                    break
            
            if not pbp_table:
                logger.error("❌ 未找到 PBP 表格")
                
                all_tables = page.query_selector_all('table')
                logger.info(f"\n页面共有 {len(all_tables)} 个表格")
                for idx, table in enumerate(all_tables[:5]):  # 显示前5个表格的信息
                    table_id = table.get_attribute('id') or 'no-id'
                    logger.info(f"表格 {idx+1}: id='{table_id}'")
                return
            
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
            
            logger.info(f"\n✓ 解析到 {len(pbp_data)} 条记录")
            
            if not pbp_data:
                logger.warning("未解析到有效数据")
                return
            
            # 保存到数据库
            logger.info("\n保存到数据库...")
            result = storage.process_single_game(test_game_info.to_dict(), pbp_data)
            
            if result.get('success'):
                logger.info("✅ 保存成功！")
                logger.info(f"当前摘要: {storage.get_import_summary()}")
            else:
                logger.error(f"❌ 保存失败: {result.get('error')}")
            
        finally:
            context.close()
            storage.close()
        
        logger.info("\n" + "=" * 60)
        logger.info("测试完成！")
        logger.info("=" * 60)

if __name__ == "__main__":
    auto_test()
