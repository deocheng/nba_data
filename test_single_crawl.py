#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试单场比赛爬取
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

# 测试的未处理比赛 - 用您提到的格式类似的未处理比赛
TEST_GAME_URL = 'https://www.basketball-reference.com/boxscores/pbp/202511260OKC.html'
TEST_GAME_ID = '202511260OKC'

def test_single_crawl():
    """测试单场比赛爬取"""
    logger.info("=" * 60)
    logger.info("测试单场比赛爬取")
    logger.info(f"目标游戏: {TEST_GAME_ID}")
    logger.info("=" * 60)
    
    storage = get_pbp_storage(season_end=2026)
    
    # 检查是否已处理
    if storage.is_game_processed(TEST_GAME_ID):
        logger.info(f"游戏 {TEST_GAME_ID} 已经处理过了！")
        storage.close()
        return
    
    # 加载游戏列表获取游戏信息
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
    
    logger.info(f"\n比赛信息:")
    logger.info(f"  {test_game_info['visitor_team']} @ {test_game_info['home_team']}")
    
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
            logger.info("\n打开页面...")
            logger.info(f"URL: {TEST_GAME_URL}")
            
            page.goto(TEST_GAME_URL, wait_until='domcontentloaded', timeout=60000)
            
            logger.info("\n请在浏览器中完成验证（如果需要）")
            logger.info("验证完成后，我会等待5秒然后尝试解析...")
            input("\n>>> 按 Enter 键继续...")
            
            # 等待页面稳定
            logger.info("\n等待5秒让页面稳定...")
            time.sleep(5)
            
            # 获取页面内容
            content = page.content()
            
            # 保存页面到调试文件
            debug_dir = os.path.join(os.path.dirname(__file__), 'debug')
            os.makedirs(debug_dir, exist_ok=True)
            debug_file = os.path.join(debug_dir, f'{TEST_GAME_ID}_debug.html')
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"页面已保存到: {debug_file}")
            
            # 查找 PBP 表格
            logger.info("\n查找 PBP 表格...")
            pbp_table = None
            
            selectors = ['table#pbp', 'table[id*="pbp"]', 'table.stats_table', 'table']
            
            for selector in selectors:
                tables = page.query_selector_all(selector)
                logger.info(f"选择器 '{selector}': 找到 {len(tables)} 个表格")
                
                for idx, table in enumerate(tables):
                    # 检查表格头部
                    headers = table.query_selector_all('thead th')
                    header_texts = [h.inner_text().strip().lower() for h in headers]
                    
                    logger.info(f"  表格 {idx+1} 头部: {header_texts[:5]}")
                    
                    if any('time' in h or 'period' in h or 'score' in h or 'quarter' in h for h in header_texts):
                        pbp_table = table
                        logger.info(f"✓ 找到 PBP 表格！使用选择器: {selector}")
                        break
                if pbp_table:
                    break
            
            if not pbp_table:
                logger.error("❌ 未找到 PBP 表格")
                logger.info("让我列出所有表格信息帮助调试:")
                
                all_tables = page.query_selector_all('table')
                logger.info(f"\n页面上共有 {len(all_tables)} 个表格")
                for idx, table in enumerate(all_tables):
                    table_id = table.get_attribute('id') or 'no-id'
                    table_classes = table.get_attribute('class') or 'no-classes'
                    headers = table.query_selector_all('th')
                    header_preview = [h.inner_text().strip() for h in headers[:5]]
                    logger.info(f"表格 {idx+1}: id='{table_id}', classes='{table_classes}', headers={header_preview}")
                
                return
            
            # 解析数据
            logger.info("\n解析 PBP 数据...")
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
                except Exception as e:
                    logger.warning(f"解析行失败: {e}")
                    continue
            
            logger.info(f"\n✓ 解析到 {len(pbp_data)} 条记录")
            
            if not pbp_data:
                logger.warning("未解析到有效数据")
                return
            
            # 预览前几条数据
            logger.info("\n前5条数据预览:")
            for idx, data in enumerate(pbp_data[:5]):
                logger.info(f"{idx+1}. {data['cells']}")
            
            # 保存到数据库
            logger.info("\n保存到数据库...")
            result = storage.process_single_game(test_game_info.to_dict(), pbp_data)
            
            if result.get('success'):
                logger.info("✅ 保存成功！")
                logger.info(f"导入摘要: {storage.get_import_summary()}")
            else:
                logger.error(f"❌ 保存失败: {result.get('error')}")
            
        finally:
            context.close()
            storage.close()
        
        logger.info("\n" + "=" * 60)
        logger.info("测试完成！")
        logger.info("=" * 60)

if __name__ == "__main__":
    test_single_crawl()
