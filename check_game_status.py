#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查比赛页面状态
"""

from playwright.sync_api import sync_playwright

def check_page(url):
    print(f"检查页面: {url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0")
        page = context.new_page()
        
        try:
            response = page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)
            
            print(f"状态码: {response.status}")
            
            # 检查页面内容
            title = page.title()
            print(f"页面标题: {title}")
            
            # 查找表格
            tables = page.query_selector_all("table")
            print(f"找到表格数: {len(tables)}")
            
            for i, table in enumerate(tables):
                tid = table.get_attribute("id") or "(no id)"
                tclass = table.get_attribute("class") or "(no class)"
                print(f"  表格 {i}: id={tid}, class={tclass}")
            
            # 检查是否有错误消息
            error_text = page.inner_text('body')[:500]
            print(f"\n页面内容预览: {error_text}")
            
        except Exception as e:
            print(f"错误: {e}")
        finally:
            browser.close()


if __name__ == "__main__":
    url = "https://www.basketball-reference.com/boxscores/pbp/202606030SAS.html"
    print("=" * 60)
    print("检查比赛页面状态")
    print("=" * 60)
    check_page(url)
    
    # 也检查一下 boxscore 页面
    print("\n" + "=" * 60)
    print("检查 boxscore 页面")
    print("=" * 60)
    boxscore_url = url.replace("/pbp/", "/")
    check_page(boxscore_url)
