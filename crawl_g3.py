#!/usr/bin/env python3
"""爬取G3总决赛"""

import sys
sys.path.insert(0, '.')

from playwright.sync_api import sync_playwright
from data_importer.database import DatabaseManager
import time
import json
import re

def main():
    game_id = '202606080NYK'
    pbp_url = 'https://www.basketball-reference.com/boxscores/pbp/202606080NYK.html'
    
    with sync_playwright() as p:
        try:
            browser_context = p.launch_persistent_context(
                user_data_dir='./browser_profile',
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )
        except:
            # 如果持久化失败，使用普通浏览器
            browser_context = p.chromium.launch_persistent_context(
                user_data_dir='./browser_profile',
                headless=False
            )
        
        page = browser_context.pages[0] if browser_context.pages else browser_context.new_page()
        
        try:
            print(f"访问PBP页面: {pbp_url}")
            page.goto(pbp_url, timeout=60000)
            time.sleep(5)
            
            # 等待表格
            page.wait_for_selector('#pbp', timeout=30000)
            
            # 调试：打印页面标题
            title = page.title()
            print(f"页面标题: {title}")
            
            # 检查表格是否存在
            pbp_table = page.query_selector('#pbp')
            print(f"PBP表格存在: {pbp_table is not None}")
            
            # 检查表格结构
            all_rows = page.query_selector_all('#pbp tr')
            print(f"#pbp tr 行数: {len(all_rows)}")
            
            tbody_rows = page.query_selector_all('#pbp tbody tr')
            print(f"#pbp tbody tr 行数: {len(tbody_rows)}")
            
            # 调试：检查前几行数据
            for i, row in enumerate(tbody_rows[1:6]):
                cells = row.query_selector_all('td')
                if len(cells) >= 6:
                    print(f"行{i+1}:")
                    for j in range(len(cells)):
                        print(f"  td[{j}]: {cells[j].inner_text().strip()[:40]}")
            
            # 提取数据
            records = []
            
            for row in tbody_rows:
                cells = row.query_selector_all('td')
                if len(cells) < 4:
                    continue
                
                # 检查第一个td是否是时间格式
                time_str = cells[0].inner_text().strip()
                
                # 检查时间格式 (如 "11:38")
                if ':' in time_str:
                    parts = time_str.split(':')
                    if len(parts) == 2 and parts[0].isdigit():
                        record = {
                            'game_id': game_id,
                            'time_remaining': time_str,
                            'visitor_score': cells[3].inner_text().strip() if len(cells) > 3 else '',
                            'home_score': cells[3].inner_text().strip() if len(cells) > 3 else '',
                            'action': cells[1].inner_text().strip() if len(cells) > 1 else '',
                            'details': cells[2].inner_text().strip() if len(cells) > 2 else '',
                        }
                        records.append(record)
            
            print(f"解析到 {len(records)} 条记录")
            
            # 保存JSON
            with open(f'CSV/2026_season/pbp/{game_id}_pbp.json', 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            
            # 保存到数据库
            db = DatabaseManager()
            with db.get_cursor() as cur:
                # 检查是否已存在
                cur.execute("SELECT game_id FROM game_metadata WHERE game_id = %s", (game_id,))
                if cur.fetchone():
                    print(f"比赛 {game_id} 已存在，跳过")
                else:
                    # 插入元数据
                    cur.execute("""
                        INSERT INTO game_metadata (game_id, game_date, visitor_team, home_team, pbp_saved, location)
                        VALUES (%s, '2026-06-08', 'San Antonio Spurs', 'New York Knicks', true, 'Regular Season')
                    """, (game_id,))
                    
                    # 插入PBP
                    for r in records:
                        # 解析分数（取第一个数字）
                        def parse_score(s):
                            if not s:
                                return None
                            try:
                                return int(s.split('-')[0].strip())
                            except:
                                return None
                        
                        v_score = parse_score(r['visitor_score'])
                        h_score = parse_score(r['home_score'])
                        
                        cur.execute("""
                            INSERT INTO play_by_play (game_id, game_clock, visitor_score, home_score, visitor_action, score_change)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (game_id, r['time_remaining'], v_score, h_score, r['action'], None))
                    
                    print(f"✅ 已保存到数据库: {game_id} ({len(records)}条)")
            
        except Exception as e:
            print(f"❌ 错误: {e}")
        finally:
            browser_context.close()

if __name__ == '__main__':
    main()
