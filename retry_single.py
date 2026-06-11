#!/usr/bin/env python3
"""单独爬取失败的第二场比赛"""

import sys
sys.path.insert(0, '.')

from playwright.sync_api import sync_playwright
from data_importer.database import DatabaseManager
import time

def main():
    game = {'game_id': '202606050SAS', 'visitor_team': 'New York Knicks', 'home_team': 'San Antonio Spurs', 'game_date': '2026-06-05'}
    
    with sync_playwright() as p:
        browser = None
        try:
            # 启动新浏览器
            browser = p.chromium.launch(
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            page = browser.new_page()
            pbp_url = f'https://www.basketball-reference.com/boxscores/pbp/{game["game_id"]}.html'
            
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
                        records.append({
                            'game_id': game['game_id'],
                            'game_clock': time_str,
                            'visitor_action': cells[1].inner_text().strip() if len(cells) > 1 else '',
                            'home_action': cells[4].inner_text().strip() if len(cells) > 4 else '',
                            'score': cells[3].inner_text().strip() if len(cells) > 3 else '',
                        })
            
            print(f"解析到 {len(records)} 条记录")
            
            # 保存到数据库
            db = DatabaseManager()
            with db.get_cursor() as cur:
                cur.execute("DELETE FROM play_by_play WHERE game_id = %s", (game['game_id'],))
                cur.execute("DELETE FROM game_metadata WHERE game_id = %s", (game['game_id'],))
                
                cur.execute("""
                    INSERT INTO game_metadata (game_id, game_date, visitor_team, home_team, pbp_saved, location)
                    VALUES (%s, %s, %s, %s, true, 'Regular Season')
                """, (game['game_id'], game['game_date'], game['visitor_team'], game['home_team']))
                
                for r in records:
                    def parse_score(s):
                        if not s:
                            return (None, None)
                        try:
                            parts = s.split('-')
                            return (int(parts[0].strip()), int(parts[1].strip())) if len(parts) == 2 else (None, None)
                        except:
                            return (None, None)
                    
                    v_score, h_score = parse_score(r['score'])
                    
                    cur.execute("""
                        INSERT INTO play_by_play (game_id, game_clock, visitor_score, home_score, visitor_action, home_action)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (game['game_id'], r['game_clock'], v_score, h_score, r['visitor_action'], r['home_action']))
            
            print(f"✅ 已保存到数据库")
            
        except Exception as e:
            print(f"❌ 失败: {e}")
        finally:
            if browser:
                browser.close()

if __name__ == '__main__':
    main()
