
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试页面结构
"""
import sys
import os

# 确保能找到 crawler 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler.play_by_play_scraper import PlayByPlayScraper
from playwright.sync_api import sync_playwright


def test_pbp_page():
    """测试 play-by-play 页面结构"""
    scraper = PlayByPlayScraper(headless=False, min_delay=2, max_delay=3)
    
    test_url = "https://www.basketball-reference.com/boxscores/pbp/202510210OKC.html"
    print(f"\n测试 URL: {test_url}\n")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(user_agent=scraper.user_agent)
            page = context.new_page()
            
            page.goto(test_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            
            # 打印页面的 HTML 结构
            print("="*80)
            print("查找所有表格")
            tables = page.query_selector_all('table')
            print(f"找到 {len(tables)} 个表格")
            for i, table in enumerate(tables):
                table_id = table.get_attribute('id') or '(no id)'
                print(f"表格 {i}: id={table_id}")
                if table_id:
                    # 打印前 10 行的内容
                    rows = table.query_selector_all('tbody tr')
                    print(f"  行数: {len(rows)}")
                    if rows:
                        first_row_html = rows[0].inner_html()
                        print(f"  第一行 HTML: {first_row_html[:200]}")
            
            print("\n" + "="*80)
            print("查找所有有 data-stat 属性的 td")
            test_tds = page.query_selector_all('td[data-stat]')
            seen_stats = set()
            for td in test_tds[:30]:
                stat = td.get_attribute('data-stat')
                if stat not in seen_stats:
                    seen_stats.add(stat)
                    print(f"  data-stat: {stat}")
            
            print("\n" + "="*80)
            print("等待你查看页面...")
            print("按 Enter 键关闭浏览器...")
            input()
            
            browser.close()
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


def test_boxscore_page():
    """测试 boxscore 页面结构"""
    print("\n" + "="*80)
    print("测试 boxscore 页面")
    print("="*80)
    
    test_url = "https://www.basketball-reference.com/boxscores/202510210OKC.html"
    print(f"\n测试 URL: {test_url}\n")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(user_agent="Mozilla/5.0")
            page = context.new_page()
            
            page.goto(test_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            
            print("="*80)
            print("查找所有表格")
            tables = page.query_selector_all('table')
            print(f"找到 {len(tables)} 个表格")
            for i, table in enumerate(tables):
                table_id = table.get_attribute('id') or '(no id)'
                print(f"表格 {i}: id={table_id}")
            
            print("\n" + "="*80)
            print("等待你查看页面...")
            print("按 Enter 键关闭浏览器...")
            input()
            
            browser.close()
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_pbp_page()
    # test_boxscore_page()
