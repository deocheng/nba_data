#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NBA赛程数据爬取与导入完整流程
从Basketball Reference抓取真实比赛数据并导入数据库
"""
from playwright.sync_api import sync_playwright
import pandas as pd
import time
import logging
import os
import random
import json
import psycopg2
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NBAScheduleScraper:
    """NBA赛程爬虫类"""

    def __init__(self, headless=True, min_delay=5, max_delay=10):
        self.headless = headless
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.base_url = "https://www.basketball-reference.com"
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

    def _random_delay(self):
        """随机延迟防止被封"""
        delay = random.uniform(self.min_delay, self.max_delay)
        logger.info(f"休眠 {delay:.1f} 秒...")
        time.sleep(delay)

    def scrape_month_schedule(self, year, month):
        """抓取指定年月的NBA比赛数据"""
        url = f"{self.base_url}/leagues/NBA_{year}_games-{month}.html"
        logger.info(f"正在抓取: {url}")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context(user_agent=self.user_agent)
                page = context.new_page()

                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                try:
                    page.wait_for_selector("table#schedule", timeout=15000)
                except Exception:
                    logger.warning(f"⚠️ 找不到 {month} 月的数据，可能尚未排期")
                    browser.close()
                    return pd.DataFrame()

                headers = []
                th_elements = page.query_selector_all("table#schedule thead tr th")
                headers = [th.inner_text().strip() for th in th_elements]

                rows = page.query_selector_all("table#schedule tbody tr:not(.thead)")
                game_data = []
                
                for row in rows:
                    cells = row.query_selector_all("th, td")
                    row_vals = [cell.inner_text().strip() for cell in cells]
                    
                    if row_vals and len(row_vals) > 5:
                        game_data.append(row_vals)

                browser.close()

                if game_data:
                    df = pd.DataFrame(game_data)
                    if len(headers) == df.shape[1]:
                        df.columns = headers
                    else:
                        df.columns = headers[:df.shape[1]]
                    
                    df = df.rename(columns={"": "Notes/BoxScore"})
                    df['Year'] = year
                    df['Month'] = month.capitalize()
                    
                    logger.info(f"✅ {month.capitalize()} 月抓取完成，共 {len(game_data)} 场比赛")
                    return df
                else:
                    logger.info(f"⚠️ {month.capitalize()} 月无有效数据")
                    return pd.DataFrame()

        except Exception as e:
            logger.error(f"❌ 抓取失败: {e}")
            return pd.DataFrame()

    def scrape_full_season(self, year):
        """抓取完整赛季数据"""
        months = ["october", "november", "december", "january", 
                  "february", "march", "april", "may", "june"]
        
        all_games = []
        logger.info(f"开始抓取 {year}-{year+1} 赛季...")

        for month in months:
            month_df = self.scrape_month_schedule(year, month)
            if not month_df.empty:
                all_games.append(month_df)
            if month != months[-1]:
                self._random_delay()

        if all_games:
            full_df = pd.concat(all_games, ignore_index=True)
            logger.info(f"🎉 赛季抓取完成，总计 {len(full_df)} 场比赛")
            return full_df
        else:
            return pd.DataFrame()

def clean_and_transform_data(df):
    """清理和转换数据"""
    if df.empty:
        return df

    logger.info("开始清理数据...")
    
    # 选择需要的列
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
    
    # 重命名列
    df = df.rename(columns={
        'Date': 'game_date',
        'Visitor/Neutral': 'away_team',
        'PTS': 'away_score',
        'Home/Neutral': 'home_team',
        'PTS.1': 'home_score',
        'OT': 'overtime',
        'Attend.': 'attendance',
        'Arena': 'arena'
    })
    
    # 过滤无效数据（球队名称不能为空）
    df = df.dropna(subset=['home_team', 'away_team'])
    df = df[df['home_team'] != df['away_team']]
    
    # 转换分数为整数
    df['home_score'] = pd.to_numeric(df['home_score'], errors='coerce').fillna(0).astype(int)
    df['away_score'] = pd.to_numeric(df['away_score'], errors='coerce').fillna(0).astype(int)
    
    # 生成唯一game_id
    df['game_id'] = df['game_date'].str.replace('-', '') + '_' + \
                   df['home_team'].str[:3].str.upper() + '_' + \
                   df['away_team'].str[:3].str.u