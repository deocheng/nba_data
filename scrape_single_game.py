#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单独爬取指定的比赛
"""

import os
import sys
import time
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright
from data_importer.pbp_storage import PBPDataStorage


def scrape_single_game(pbp_url):
    """爬取单个比赛的 PBP 数据"""
    game_id = pbp_url.split('/')[-1].replace('.html', '')
    
    print(f"爬取比赛: {game_id}")
    print(f"URL: {pbp_url}")
    
    # 加载游戏列表找匹配的游戏信息
    season_end = 2026
    games_file = f"CSV/{season_end}_season/all_games_{season_end}.csv"
    
    if not os.path.exists(games_file):
        print(f"游戏列表不存在: {games_file}")
        return False
    
    games_df = pd.read_csv(games_file, encoding='utf-8-sig')
    game_row = games_df[games_df['boxscore_url'].str.contains(game_id)]
    
    if len(game_row) == 0:
        print(f"找不到匹配的游戏信息")
        game_info = {'game_id': game_id, 'boxscore_url': pbp_url.replace('/pbp/', '/')}
    else:
        game_info = game_row.iloc[0].to_dict()
        game_info['game_id'] = game_id
    
    print(f"比赛信息: {game_info.get('visitor_team', 'Unknown')} @ {game_info.get('home_team', 'Unknown')}")
    
    # 爬取数据
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0")
        page = context.new_page()
        
        try:
            print("加载页面...")
            page.goto(pbp_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(4000)
            
            # 找表格
            pbp_table = None
            all_tables = page.query_selector_all("table")
            
            for table in all_tables:
                tid = table.get_attribute("id") or ""
                if "pbp" in tid.lower():
                    pbp_table = table
                    print(f"找到表格: {tid}")
                    break
            
            if not pbp_table:
                print("❌ 未找到 PBP 表格")
                browser.close()
                return False
            
            # 解析
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
                print(f"✅ 成功! 文件: {result['file_saved']}, DB: {result['db_imported']} ({result['records_imported']} 条)")
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
    print(f"单独爬取比赛")
    print(f"URL: {url}")
    print("=" * 60)
    
    success = scrape_single_game(url)
    
    if success:
        print("\n✅ 爬取完成!")
    else:
        print("\n❌ 爬取失败!")
