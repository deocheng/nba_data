#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试Playwright是否能绕过Cloudflare反爬"""
from playwright.sync_api import sync_playwright
import time
import random

def test_cloudflare_bypass():
    url = "https://www.basketball-reference.com/leagues/NBA_2026_games-october.html"
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
            ]
        )
        
        user_agent = random.choice(user_agents)
        context = browser.new_context(
            user_agent=user_agent,
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York',
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        
        # 注入反检测脚本
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        """)
        
        page = context.new_page()
        
        try:
            print(f"尝试访问: {url}")
            print(f"User-Agent: {user_agent}")
            
            response = page.goto(url, wait_until="networkidle", timeout=120000)
            
            if response:
                print(f"状态码: {response.status}")
            
            # 等待页面加载
            time.sleep(10)
            
            # 检查页面标题
            title = page.title()
            print(f"页面标题: {title}")
            
            # 检查是否有Cloudflare相关内容
            if "Just a moment" in title or "Cloudflare" in title:
                print("❌ 仍然被Cloudflare拦截")
                return False
            
            # 尝试获取页面内容
            content = page.content()
            
            # 检查是否包含比赛数据
            if "schedule" in content.lower() or "October" in content:
                print("✅ 成功绕过Cloudflare！")
                print(f"页面长度: {len(content)}")
                
                # 尝试查找表格
                tables = page.query_selector_all('table')
                print(f"找到 {len(tables)} 个表格")
                
                for i, table in enumerate(tables):
                    table_id = table.get_attribute('id')
                    print(f"  表格 {i}: id={table_id}")
                
                return True
            else:
                print("❌ 页面内容异常")
                return False
                
        except Exception as e:
            print(f"❌ 访问失败: {e}")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    print("=" * 60)
    print("测试Playwright绕过Cloudflare")
    print("=" * 60)
    
    success = test_cloudflare_bypass()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 成功！可以继续爬取数据")
    else:
        print("❌ 失败！IP仍然被封禁")
        print("建议等待24-48小时后再试")
    print("=" * 60)
