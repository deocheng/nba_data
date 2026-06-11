
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
保存页面 HTML 用于分析
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler.play_by_play_scraper import PlayByPlayScraper
from playwright.sync_api import sync_playwright


def save_html():
    """保存测试页面 HTML"""
    
    scraper = PlayByPlayScraper(headless=True, min_delay=2, max_delay=2)
    
    # 保存 play-by-play 页面
    pbp_url = "https://www.basketball-reference.com/boxscores/pbp/202510210OKC.html"
    print(f"保存 PBP 页面: {pbp_url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=scraper.user_agent)
        page = context.new_page()
        
        page.goto(pbp_url, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(5000)
        
        html = page.content()
        with open("test_pbp_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        print(f"✅ 保存成功: test_pbp_page.html")
        
        # 保存 boxscore 页面
        box_url = "https://www.basketball-reference.com/boxscores/202510210OKC.html"
        print(f"保存 boxscore 页面: {box_url}")
        
        page.goto(box_url, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(5000)
        
        html = page.content()
        with open("test_box_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        print(f"✅ 保存成功: test_box_page.html")
        
        browser.close()


if __name__ == "__main__":
    save_html()
