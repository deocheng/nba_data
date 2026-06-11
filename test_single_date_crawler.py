#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试爬虫 - 测试爬取指定日期的PBP数据
"""

import sys
import os
import time
import random
import pandas as pd
from datetime import datetime
from playwright.sync_api import sync_playwright
from data_importer.pbp_storage import get_pbp_storage

def crawl_single_game_test():
    """测试爬取指定日期的PBP数据"""
    
    storage = get_pbp_storage(season_end=2026)
    
    # 读取游戏列表
    games_df = pd.read_csv('CSV/2026_season/all_games_2026.csv', encoding='utf-8-sig')
    
    # 筛选出指定日期的游戏 - 20251022
    target_date = '20251022'
    
    # 获取该日期的游戏
    games_on_date = []
    for _, row in games_df.iterrows():
        game_id = row['boxscore_url'].split('/')[-1].replace('.html', '')
        if game_id.startswith(target_date):
            games_on_date.append(row)
    
    if not games_on_date:
        print(f"没有找到日期 {target_date} 的游戏")
        return
    
    print(f"找到 {len(games_on_date)} 场游戏在 {target_date}")
    
    # 只取前3场来测试
    test_games = games_on_date[:3]
    
    print("\n开始爬取测试游戏...")
    
    # 启动浏览器
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        # 只测试第一个游戏
        game_info = test_games[0]
        game_id = game_info['boxscore_url'].split('/')[-1].replace('.html', '')
        
        print(f"\n处理: {game_info['visitor_team']} @ {game_info['home_team']} ({game_id})")
        
        try:
            # 导航到PBP页面
            pbp_url = game_info['boxscore_url'].replace('/boxscores/', '/boxscores/pbp/')
            print(f"加载页面: {pbp_url}")
            
            # 打开页面
            page.goto(pbp_url, wait_until='networkidle', timeout=120000)
            
            # 让用户手动完成Cloudflare验证
            print("请在浏览器中完成Cloudflare验证...")
            time.sleep(30)  # 给用户足够时间完成验证
            
            # 检查页面
            content = page.content()
            if 'Play-by-Play' in content.lower():
                print("页面加载成功！")
                
                # 保存HTML用于调试
                with open(f'debug/test_{game_id}.html', 'w', encoding='utf-8') as f:
                    f.write(page.content())
                print(f"已保存HTML到 debug/test_{game_id}.html")
                
                # 查找PBP表格
                pbp_table = page.query_selector('table#pbp') or page.query_selector('table')
                
                if pbp_table:
                    print("找到PBP表格！")
                    
                    # 解析PBP数据
                    rows = pbp_table.query_selector_all('tr')
                    pbp_data = []
                    
                    for idx, row_elem in enumerate(rows):
                        try:
                            cells = row_elem.query_selector_all('td, th')
                            cell_texts = [cell.inner_text().strip() for cell in cells]
                            
                            if len(cell_texts) >= 4:
                                pbp_data.append({
                                    'row': idx,
                                    'cells': cell_texts
                                })
                        except Exception as e:
                            print(f"解析行 {idx} 失败: {e}")
                    
                    print(f"解析到 {len(pbp_data)} 条记录")
                    
                    if pbp_data:
                        result = storage.process_single_game(game_info.to_dict(), pbp_data)
                        print(f"保存结果: {result}")
                    
                else:
                    print("找不到PBP表格")
                    
            else:
                print("未成功加载PBP内容")
                
        except Exception as e:
            print(f"爬取失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 保持浏览器打开，让用户可以查看
        print("\n浏览器保持打开，您可以继续查看页面。按 Ctrl+C 退出...")
        try:
            time.sleep(300)  # 保持5分钟
        except KeyboardInterrupt:
            pass
        
        browser.close()
    storage.close()

if __name__ == '__main__':
    crawl_single_game_test()
