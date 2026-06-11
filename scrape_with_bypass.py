#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用反检测策略爬取比赛
"""

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright
from data_importer.pbp_storage import PBPDataStorage


def scrape_with_bypass(pbp_url):
    """使用反检测策略爬取"""
    game_id = pbp_url.split('/')[-1].replace('.html', '')
    
    print(f"爬取比赛: {game_id}")
    
    # 加载游戏信息
    season_end = 2026
    games_file = f"CSV/{season_end}_season/all_games_{season_end}.csv"
    games_df = pd.read_csv(games_file, encoding='utf-8-sig')
    game_row = games_df[games_df['boxscore_url'].str.contains(game_id)]
    
    if len(game_row) == 0:
        game_info = {'game_id': game_id, 'boxscore_url': pbp_url.replace('/pbp/', '/')}
    else:
        game_info = game_row.iloc[0].to_dict()
        game_info['game_id'] = game_id
    
    print(f"比赛: {game_info.get('visitor_team', 'Unknown')} @ {game_info.get('home_team', 'Unknown')}")
    
    with sync_playwright() as p:
        # 使用更多反检测设置
        browser = p.chromium.launch(
            headless=False,  # 使用有头模式更容易通过检测
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--start-maximized',
            ]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York',
        )
        
        page = context.new_page()
        
        # 注入反检测脚本
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
        
        try:
            print("加载页面...")
            response = page.goto(pbp_url, wait_until="networkidle", timeout=120000)
            
            # 等待可能的 Cloudflare 验证
            page.wait_for_timeout(15000)
            
            # 检查是否被重定向
            final_url = page.url
            print(f"最终 URL: {final_url}")
            
            # 检查状态
            if response.status != 200:
                print(f"状态码: {response.status}")
                browser.close()
                return False
            
            # 查找表格
            tables = page.query_selector_all("table")
            print(f"找到表格数: {len(tables)}")
            
            pbp_table = None
            for table in tables:
                tid = table.get_attribute("id") or ""
                if "pbp" in tid.lower():
                    pbp_table = table
                    print(f"找到 PBP 表格: {tid}")
                    break
            
            if not pbp_table:
                print("❌ 未找到 PBP 表格")
                # 保存调试 HTML
                html = page.content()
                with open(f"{game_id}_debug.html", "w", encoding="utf-8") as f:
                    f.write(html)
                browser.close()
                return False
            
            # 解析数据
            rows = pbp_table.query_selector_all("tr")
            pbp_data = []
            
            for j, row in enumerate(rows):
                cells = row.query_selector_all("td, th")
                cell_texts = [c.inner_text().strip() for c in cells]
                if len(cell_texts) >= 4:
                    pbp_data.append({"row": j, "cells": cell_texts})
            
            print(f"解析到 {len(pbp_data)} 条记录")
            
            # 保存
            storage = PBPDataStorage()
            result = storage.process_single_game(game_info, pbp_data)
            storage.close()
            
            if result['success']:
                print(f"✅ 成功!")
                browser.close()
                return True
            else:
                print(f"❌ 失败: {result.get('errors')}")
                browser.close()
                return False
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            browser.close()
            return False


if __name__ == "__main__":
    url = "https://www.basketball-reference.com/boxscores/pbp/202606030SAS.html"
    print("=" * 60)
    print("使用反检测策略爬取")
    print(f"URL: {url}")
    print("=" * 60)
    
    success = scrape_with_bypass(url)
    
    if success:
        print("\n✅ 爬取完成!")
    else:
        print("\n❌ 爬取失败!")
