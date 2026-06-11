#!/usr/bin/env python3
"""重新爬取失败的两场总决赛比赛"""

import sys
sys.path.insert(0, '.')

from playwright.sync_api import sync_playwright
from data_importer.database import DatabaseManager
import time
import json

def parse_pbp(browser_context, game_id):
    """爬取单场比赛的PBP数据"""
    pbp_url = f'https://www.basketball-reference.com/boxscores/pbp/{game_id}.html'
    
    try:
        # 获取或创建新页面
        if browser_context.pages:
            page = browser_context.pages[0]
        else:
            page = browser_context.new_page()
        
        print(f"访问: {pbp_url}")
        page.goto(pbp_url, timeout=60000)
        time.sleep(5)
        
        # 等待表格加载
        page.wait_for_selector('#pbp', timeout=30000)
        
        # 提取数据
        tbody_rows = page.query_selector_all('#pbp tbody tr')
        records = []
        
        for row in tbody_rows:
            cells = row.query_selector_all('td')
            if len(cells) < 4:
                continue
            
            time_str = cells[0].inner_text().strip()
            if ':' in time_str:
                parts = time_str.split(':')
                if len(parts) == 2 and parts[0].isdigit():
                    record = {
                        'game_id': game_id,
                        'game_clock': time_str,
                        'visitor_action': cells[1].inner_text().strip() if len(cells) > 1 else '',
                        'home_action': cells[4].inner_text().strip() if len(cells) > 4 else '',
                        'score': cells[3].inner_text().strip() if len(cells) > 3 else '',
                    }
                    records.append(record)
        
        print(f"  解析到 {len(records)} 条记录")
        return records
        
    except Exception as e:
        print(f"  ❌ 解析失败: {e}")
        return None

def save_to_database(game_id, records, visitor_team, home_team, game_date):
    """保存到数据库"""
    db = DatabaseManager()
    with db.get_cursor() as cur:
        # 删除旧记录
        cur.execute("DELETE FROM play_by_play WHERE game_id = %s", (game_id,))
        cur.execute("DELETE FROM game_metadata WHERE game_id = %s", (game_id,))
        
        # 插入元数据
        cur.execute("""
            INSERT INTO game_metadata (game_id, game_date, visitor_team, home_team, pbp_saved, location)
            VALUES (%s, %s, %s, %s, true, 'Regular Season')
        """, (game_id, game_date, visitor_team, home_team))
        
        # 插入PBP数据
        for r in records:
            def parse_score(s):
                if not s:
                    return None
                try:
                    parts = s.split('-')
                    return (int(parts[0].strip()), int(parts[1].strip())) if len(parts) == 2 else (None, None)
                except:
                    return (None, None)
            
            v_score, h_score = parse_score(r['score'])
            
            cur.execute("""
                INSERT INTO play_by_play (game_id, game_clock, visitor_score, home_score, visitor_action, home_action, score_change)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (game_id, r['game_clock'], v_score, h_score, r['visitor_action'], r['home_action'], None))
        
        print(f"  ✅ 已保存到数据库")

def main():
    # 失败的比赛列表
    failed_games = [
        {'game_id': '202606030SAS', 'visitor_team': 'New York Knicks', 'home_team': 'San Antonio Spurs', 'game_date': '2026-06-03'},
        {'game_id': '202606050SAS', 'visitor_team': 'New York Knicks', 'home_team': 'San Antonio Spurs', 'game_date': '2026-06-05'},
    ]
    
    with sync_playwright() as p:
        browser_context = None
        try:
            # 启动持久化浏览器
            browser_context = p.chromium.launch_persistent_context(
                user_data_dir='./browser_profile',
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            for game in failed_games:
                print(f"\n{'='*60}")
                print(f"处理: {game['game_date']} - {game['visitor_team']} @ {game['home_team']} ({game['game_id']})")
                print('='*60)
                
                # 重试机制
                max_retries = 2
                for attempt in range(max_retries):
                    try:
                        records = parse_pbp(browser_context, game['game_id'])
                        if records and len(records) > 0:
                            save_to_database(game['game_id'], records, game['visitor_team'], game['home_team'], game['game_date'])
                            break
                        else:
                            print(f"  尝试 {attempt+1}/{max_retries} 失败，重试中...")
                            time.sleep(10)
                            
                    except Exception as e:
                        print(f"  尝试 {attempt+1}/{max_retries} 异常: {e}")
                        # 重建浏览器上下文
                        if browser_context:
                            browser_context.close()
                        browser_context = p.chromium.launch_persistent_context(
                            user_data_dir='./browser_profile',
                            headless=False,
                            args=['--disable-blink-features=AutomationControlled']
                        )
                        time.sleep(5)
                        
                else:
                    print(f"  ❌ 所有重试均失败")
                    
        finally:
            if browser_context:
                browser_context.close()

if __name__ == '__main__':
    main()
