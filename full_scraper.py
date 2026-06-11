
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整爬取所有比赛的 play-by-play 数据
"""
import sys
import os
import time
import json
import pandas as pd
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright


def main():
    print("="*80)
    print("完整爬取所有比赛 play-by-play 数据")
    print("="*80)
    
    season_end = 2026
    games_file = f"CSV/{season_end}_season/all_games_{season_end}.csv"
    
    if not os.path.exists(games_file):
        print(f"File not found: {games_file}")
        return
    
    games_df = pd.read_csv(games_file, encoding="utf-8-sig")
    print(f"Total games: {len(games_df)}")
    
    output_dir = f"CSV/{season_end}_season"
    pbp_dir = os.path.join(output_dir, "pbp")
    os.makedirs(pbp_dir, exist_ok=True)
    
    progress_file = os.path.join(output_dir, "full_progress.json")
    processed = set()
    if os.path.exists(progress_file):
        processed = set(json.load(open(progress_file, "r", encoding="utf-8")))
    print(f"Already processed: {len(processed)}, To process: {len(games_df) - len(processed)}")
    
    # 时间控制
    start_time = datetime.now()
    run_duration = timedelta(minutes=30)
    rest_duration = timedelta(minutes=5)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0")
        
        processed_count = 0
        
        for idx, row in games_df.iterrows():
            game_id = row['boxscore_url'].split('/')[-1].replace('.html', '')
            
            if game_id in processed:
                continue
            
            # 检查是否需要休息
            elapsed = datetime.now() - start_time
            if elapsed > run_duration:
                print(f"\n{'='*80}")
                print(f"已运行 {elapsed}, 休息 {rest_duration}...")
                print(f"{'='*80}")
                time.sleep(rest_duration.total_seconds())
                start_time = datetime.now()
            
            print(f"\n[{processed_count+1}/{len(games_df)-len(processed)}] {row['visitor_team']} @ {row['home_team']} ({row['date']})")
            
            try:
                pbp_url = row['boxscore_url'].replace("/boxscores/", "/boxscores/pbp/")
                print(f"  Loading: {pbp_url}")
                
                page = context.new_page()
                page.goto(pbp_url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(4000)
                
                pbp_table = None
                all_tables = page.query_selector_all("table")
                
                for table in all_tables:
                    tid = table.get_attribute("id") or ""
                    if "pbp" in tid.lower():
                        pbp_table = table
                        break
                
                if not pbp_table:
                    print("  No table found - saving debug HTML")
                    html = page.content()
                    with open(os.path.join(pbp_dir, f"{game_id}_debug.html"), "w", encoding="utf-8") as f:
                        f.write(html)
                    page.close()
                    time.sleep(10)
                    continue
                
                rows = pbp_table.query_selector_all("tr")
                pbp_data = []
                
                for j, r in enumerate(rows):
                    try:
                        cells = r.query_selector_all("td, th")
                        cell_texts = [c.inner_text().strip() for c in cells]
                        if len(cell_texts) >= 4:
                            pbp_data.append({"row": j, "cells": cell_texts})
                    except Exception as e:
                        pass
                
                out_file = os.path.join(pbp_dir, f"{game_id}_pbp.json")
                with open(out_file, "w", encoding="utf-8") as f:
                    json.dump(pbp_data, f, ensure_ascii=False, indent=2)
                
                print(f"  Saved {len(pbp_data)} rows -> {os.path.basename(out_file)}")
                
                processed.add(game_id)
                with open(progress_file, "w", encoding="utf-8") as f:
                    json.dump(list(processed), f)
                
                processed_count += 1
                page.close()
                
                print(f"  Waiting 40s...")
                time.sleep(40)
                
            except Exception as e:
                print(f"  Error: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(30)
        
        browser.close()
    
    print(f"\n{'='*80}")
    print(f"Complete! Total processed: {len(processed)}")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
