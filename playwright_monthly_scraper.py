#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 Playwright 抓取 NBA 2026 赛季月度赛程数据
防屏蔽策略：间隔30秒，每30分钟暂停5分钟
"""
import sys
import os
import time
import random
import logging
import json
import pandas as pd
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MonthlyScheduleScraper:
    """月度赛程爬虫 - 使用 Playwright"""
    
    def __init__(self, min_delay=30, max_delay=30, run_interval=30*60, rest_interval=5*60):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.run_interval = run_interval
        self.rest_interval = rest_interval
        self.start_time = None
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        
    def _check_and_rest(self):
        """检查是否需要休息"""
        if self.start_time is None:
            self.start_time = time.time()
            return
        
        elapsed = time.time() - self.start_time
        if elapsed >= self.run_interval:
            logger.info("=" * 80)
            logger.info(f"已运行 {elapsed/60:.1f} 分钟，休息 {self.rest_interval/60:.0f} 分钟...")
            logger.info("=" * 80)
            time.sleep(self.rest_interval)
            logger.info("休息结束，继续运行...")
            self.start_time = time.time()
    
    def scrape_month(self, year, month, output_dir=None):
        """
        抓取指定月份的赛程数据
        
        Args:
            year: 赛季结束年份 (如 2026 表示 2025-26 赭季)
            month: 月份名称 (如 'october', 'november' 等)
            output_dir: 输出目录
        """
        url = f"https://www.basketball-reference.com/leagues/NBA_{year}_games-{month}.html"
        logger.info(f"正在访问: {url}")
        
        try:
            with sync_playwright() as p:
                # 启动浏览器（非无头模式，更容易通过 Cloudflare）
                browser = p.chromium.launch(headless=False)
                context = browser.new_context(
                    user_agent=self.user_agent,
                    viewport={"width": 1920, "height": 1080}
                )
                page = context.new_page()
                
                # 访问页面 - 使用 domcontentloaded 更快
                page.goto(url, wait_until="domcontentloaded", timeout=90000)
                
                # 等待页面稳定
                logger.info("等待页面加载...")
                time.sleep(10)  # 给 Cloudflare 验证足够时间
                
                # 检查是否在验证页面
                content = page.content()
                if "安全验证" in content or "Checking your browser" in content or "Just a moment" in content:
                    logger.info("检测到 Cloudflare 验证，等待通过...")
                    # 等待验证完成（最多60秒）
                    for i in range(12):
                        time.sleep(5)
                        content = page.content()
                        if "安全验证" not in content and "Checking your browser" not in content:
                            logger.info("✓ Cloudflare 验证通过")
                            break
                        logger.info(f"等待验证... ({i+1}/12)")
                    time.sleep(3)  # 额外等待
                
                # 查找赛程表格
                table = None
                selectors = [
                    "table#schedule",
                    "table#games",
                    "table[id*='schedule']",
                    "table.stats_table"
                ]
                
                for selector in selectors:
                    try:
                        table = page.query_selector(selector)
                        if table:
                            logger.info(f"找到表格: {selector}")
                            break
                    except:
                        continue
                
                if not table:
                    # 尝试查找任何表格
                    tables = page.query_selector_all("table")
                    logger.info(f"页面共有 {len(tables)} 个表格")
                    for t in tables:
                        rows = t.query_selector_all("tbody tr")
                        if len(rows) > 0:
                            table = t
                            logger.info(f"使用表格，包含 {len(rows)} 行数据")
                            break
                
                if not table:
                    logger.warning(f"⚠️ 找不到 {month} 的赛程表格")
                    browser.close()
                    return pd.DataFrame()
                
                # 提取表头
                headers = []
                th_elements = table.query_selector_all("thead tr th")
                for th in th_elements:
                    headers.append(th.inner_text().strip())
                
                logger.info(f"表头: {headers}")
                
                # 提取数据行
                rows = table.query_selector_all("tbody tr:not(.thead)")
                game_data = []
                
                for row in rows:
                    cells = row.query_selector_all("th, td")
                    row_data = [cell.inner_text().strip() for cell in cells]
                    
                    # 过滤空行
                    if row_data and len(row_data) > 5:
                        game_data.append(row_data)
                
                browser.close()
                
                # 转换为 DataFrame
                if game_data:
                    df = pd.DataFrame(game_data)
                    if len(headers) == df.shape[1]:
                        df.columns = headers
                    df['Month'] = month.capitalize()
                    df['Season'] = f"{year-1}-{year}"
                    
                    logger.info(f"✅ {month} 抓取完成，共 {len(game_data)} 场比赛")
                    
                    # 保存数据
                    if output_dir:
                        os.makedirs(output_dir, exist_ok=True)
                        filepath = os.path.join(output_dir, f"nba_schedule_{year}_{month}.csv")
                        df.to_csv(filepath, index=False, encoding='utf-8-sig')
                        logger.info(f"✓ 已保存到: {filepath}")
                    
                    return df
                else:
                    logger.warning(f"⚠️ {month} 无有效数据")
                    return pd.DataFrame()
                    
        except Exception as e:
            logger.error(f"❌ 抓取 {month} 失败: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def scrape_season(self, year, months, output_dir=None):
        """抓取整个赛季的月度数据"""
        all_games = []
        progress_file = os.path.join(output_dir or '.', 'scraping_progress.json')
        
        # 加载进度
        completed = []
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                progress = json.load(f)
                completed = progress.get('completed_months', [])
        
        for month in months:
            if month in completed:
                logger.info(f"跳过已完成的月份: {month}")
                continue
            
            logger.info("=" * 80)
            logger.info(f"开始抓取 {month}")
            logger.info("=" * 80)
            
            df = self.scrape_month(year, month, output_dir)
            
            if not df.empty:
                all_games.append(df)
                completed.append(month)
                
                # 保存进度
                with open(progress_file, 'w') as f:
                    json.dump({'completed_months': completed}, f)
            
            # 检查休息
            self._check_and_rest()
            
            # 延迟
            if month != months[-1]:
                delay = random.uniform(self.min_delay, self.max_delay)
                logger.info(f"等待 {delay:.1f} 秒...")
                time.sleep(delay)
        
        if all_games:
            full_df = pd.concat(all_games, ignore_index=True)
            logger.info(f"✅ 爬取完成！总共 {len(full_df)} 场比赛")
            return full_df
        return pd.DataFrame()

def main():
    print("=" * 80)
    print("使用 Playwright 抓取 NBA 2026 赛季月度赛程")
    print("=" * 80)
    
    scraper = MonthlyScheduleScraper(
        min_delay=30,
        max_delay=30,
        run_interval=30*60,
        rest_interval=5*60
    )
    
    # 月份列表
    months = ['october', 'november', 'december', 'january', 'february', 'march', 'april', 'may']
    
    # 输出目录
    output_dir = 'CSV/2026_season/monthly'
    
    df = scraper.scrape_season(2026, months, output_dir)
    
    if not df.empty:
        print("\n数据预览:")
        print(df.head(10))

if __name__ == '__main__':
    main()