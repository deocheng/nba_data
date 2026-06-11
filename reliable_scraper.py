
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可靠的比赛数据爬取脚本
"""
import sys
import os
import time
import json
import random
import pandas as pd
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright


def main():
    print("="*80)
    print("可靠的比赛详细数据爬取")
    print("="*80)
    
    # 加载比赛列表
    season_end = 2026
    games_file = f"CSV/{season_end}_season/all_games_{season_end}.csv"
    if not os.path.exists(games_file):
        print(f"❌ 文件不存在: {games_file}")
        return
    
    games_df = pd.read_csv(games_file, encoding="utf-8-sig")
    print(f"✅ 加载了 {len(games_df)} 场比赛")
    
    # 输出目录
    output_dir = f"CSV/{season_end}_season"
    pbp_dir = os.path.join(output_dir, "pbp")
    os.makedirs(pbp_dir, exist_ok=True)
    
    # 进度
    progress_file = os.path.join(output_dir, "reliable_progress.json")
    processed = set()
    if os.path.exists(progress_file):
        processed = set(json.load(open(progress_file, "r", encoding="utf-8")))
    print(f"已处理: {len(processed)}, 待处理: {len(games_df) - len(processed)}")
    
    # 测试前 3 场
    test_count = 0
    max_test = 3
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        for idx, row in games_df.iterrows():
            if test_count >= max_test:
                break
                
            game_id = row['boxscore_url'].split('/')[-1].replace('.html', '')
            if game_id in processed:
                continue
            
            print(f"\n第 {test_count+1}/{max_test} 场: {row['visitor_team']} @ {row['home_team']}")
            
            try:
                # PBP URL
                pbp_url = row['boxscore_url'].replace("/boxscores/", "/boxscores/pbp/")
                print(f"  加载 PBP 页面: {pbp_url}")
                
                page = context.new_page()
                page.goto(pbp_url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(4000)
                
                # 找 PBP 表格
                pbp_table = None
                all_tables = page.query_selector_all("table")
                
                for table in all_tables:
                    tid = table.get_attribute("id") or ""
                    if "pbp" in tid.lower():
                        pbp_table = table
                        print(f"  ✅ 找到 PBP 表格: id={tid}")
                        break
                
                if not pbp_table:
                    print(f"  ⚠️  没找到 PBP 表格，保存 HTML 调试")
                    html = page.content()
                    with open(f"{pbp_dir}/{game_id}_debug.html", "w", encoding="utf-8") as f:
                        f.write(html)
                    page.close()
                    continue
                
                # 解析表格
                print(f"  解析表格...")
                rows = pbp_table.query_selector_all("tr")
                pbp_data = []
                
                for j, row in enumerate(rows):
                    try:
                        cells = row.query_selector_all("td, th")
                        cell_texts = []
                        for c in cells:
                            cell_texts.append(c.inner_text().strip())
                        
                        if len(cell_texts) &gt;= 4:
                            pbp_data.append({
                                "row_idx": j,
                                "cells": cell_texts
                            })
                    except Exception as e:
                        print(f"  跳过坏行 {j}: {e}")
                
                print(f"  解析了 {len(pbp_data)} 行")
                
                # 保存
                out_file = os.path.join(pbp_dir, f"{game_id}_pbp.json")
                with open(out_file, "w", encoding="utf-8") as f:
                    json.dump(pbp_data, f, ensure_ascii=False, indent=2)
                print(f"  ✅ 保存到: {out_file}")
                
                # 保存进度
                processed.add(game_id)
                with open(progress_file, "w", encoding="utf-8") as f:
                    json.dump(list(processed), f)
                
                test_count += 1
                page.close()
                
                # 等待
                print(f"  等待 40 秒...")
                time.sleep(40)
                
            except Exception as e:
                print(f"  ❌ 错误: {e}")
                import traceback
                traceback.print_exc()
        
        browser.close()
    
    print("\n" + "="*80)
    print("测试完成!")
    print("="*80)


if __name__ == "__main__":
    main()
