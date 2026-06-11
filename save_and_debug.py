#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
先保存页面调试，再尝试解析
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

def save_and_debug():
    """保存页面并调试"""
    logger.info("=" * 60)
    logger.info("保存页面并调试 - 自动检测验证")
    logger.info("=" * 60)
    
    storage = get_pbp_storage(season_end=2026)
    
    # 加载游戏信息
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
            logger.info("我会自动检测...")
            
            verification_passed = False
            max_wait = 300
            
            for wait_time in range(max_wait):
                time.sleep(3)
                content = page.content()
                
                is_verification = False
                verification_keywords = ['Just a moment', 'Checking your browser', 
                                    'Cloudflare', 'challenge']
                if any(kw in content for kw in verification_keywords):
                    is_verification = True
                
                if is_verification:
                    if wait_time % 10 == 0:
                        logger.info(f"等待验证... ({wait_time * 3}/{max_wait * 3}秒)")
                    continue
                
                if 'Play-by-Play' in content or len(page.query_selector_all('table')) > 5:
                    logger.info("✓ 验证通过！")
                    verification_passed = True
                    break
            
            # 等待页面完全加载
            logger.info("\n等待页面稳定（15秒）...")
            time.sleep(15)
            
            # 保存页面
            debug_dir = os.path.join(os.path.dirname(__file__), 'debug')
            os.makedirs(debug_dir, exist_ok=True)
            debug_file = os.path.join(debug_dir, f'{TEST_GAME_ID}_full.html')
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(page.content())
            logger.info(f"页面已保存到: {debug_file}")
            
            # 打印页面信息
            logger.info("\n" + "=" * 60)
            logger.info("页面信息:")
            logger.info("=" * 60)
            
            # 查找所有表格
            all_tables = page.query_selector_all('table')
            logger.info(f"表格总数: {len(all_tables)}")
            
            pbp_table = None
            
            for idx, table in enumerate(all_tables):
                table_id = table.get_attribute('id') or 'no-id'
                table_classes = table.get_attribute('class') or 'no-classes'
                
                headers = table.query_selector_all('th')
                header_texts = [h.inner_text().strip() for h in headers]
                
                # 打印前几个表格的信息
                if idx < 10:
                    logger.info(f"\n表格 {idx + 1}:")
                    logger.info(f"  id: {table_id}")
                    logger.info(f"  classes: {table_classes}")
                    logger.info(f"  headers: {header_texts[:10]}")
                
                # 判断是否是PBP表格
                if (table_id == 'pbp' or 
                    'pbp' in table_id.lower() or 
                    any('quarter' in h.lower() or 'time' in h.lower() or 
                        'score' in h.lower() for h in header_texts)):
                    logger.info(f"\n✓ 找到 PBP 表格（表格 {idx + 1}）!")
                    pbp_table = table
                    break
            
            if not pbp_table:
                logger.warning("\n未直接找到PBP表格，让我尝试其他方法...")
                
                # 尝试找到所有有很多行的表格
                for idx, table in enumerate(all_tables):
                    rows = table.query_selector_all('tr')
                    if len(rows) > 100:  # PBP表格通常有很多行
                        logger.info(f"\n找到有 {len(rows)} 行的表格（表格 {idx+1}），可能是PBP表格")
                        pbp_table = table
                        break
            
            if not pbp_table:
                logger.error("\n❌ 未找到PBP表格")
                return
            
            logger.info("\n开始解析数据...")
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
            
            # 预览
            logger.info("\n前5条:")
            for i, d in enumerate(pbp_data[:5]):
                logger.info(f"  {i+1}. {d['cells']}")
            
            # 保存
            logger.info("\n保存到数据库...")
            result = storage.process_single_game(test_game_info.to_dict(), pbp_data)
            
            if result.get('success'):
                logger.info("\n✅ 保存成功！")
                logger.info(f"导入摘要: {storage.get_import_summary()}")
            else:
                logger.error(f"❌ 保存失败: {result.get('error')}")
            
        finally:
            context.close()
            storage.close()
        
        logger.info("\n完成！")

if __name__ == "__main__":
    save_and_debug()
