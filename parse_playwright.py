
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用 Playwright 仔细解析页面结构
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright
import time


def parse_pbp_page():
    """仔细解析 PBP 页面"""
    test_url = "https://www.basketball-reference.com/boxscores/pbp/202510210OKC.html"
    print(f"解析 PBP 页面: {test_url}\n")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        print("正在加载页面...")
        page.goto(test_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(4000)
        
        # 查找所有表格
        all_tables = page.query_selector_all('table')
        print(f"找到 {len(all_tables)} 个表格\n")
        
        for i, table in enumerate(all_tables):
            table_id = table.get_attribute('id') or "(no id)"
            print(f"表格 {i}: id='{table_id}'")
            
            # 打印表格的内容预览
            if table_id:
                # 获取表格的 HTML
                table_html = table.inner_html()
                print(f"  HTML 长度: {len(table_html)} chars")
                if 'pbp' in table_id:
                    print(f"  这是 PBP 表格!")
                    
                    # 获取所有 tr
                    rows = table.query_selector_all('tr')
                    print(f"  总行数: {len(rows)}")
                    
                    for j, row in enumerate(rows[:15]):  # 只打印前15行
                        cells = row.query_selector_all('td, th')
                        cell_texts = []
                        for cell in cells:
                            cell_texts.append(repr(cell.inner_text().strip()))
                        print(f"    行 {j}: {' | '.join(cell_texts)}")
                    
                    break
        
        print("\n" + "="*80)
        print("等待 20 秒让你查看浏览器, 然后会自动关闭...")
        time.sleep(20)
        browser.close()


if __name__ == "__main__":
    parse_pbp_page()
