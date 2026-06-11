#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全 PBP 爬虫 - 使用高级反爬机制，支持 Cloudflare 验证
"""

import sys
import os
import time
import random
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright
from data_importer.pbp_storage import get_pbp_storage

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SafePBPCrawler:
    """安全的 PBP 数据爬虫"""
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
    ]
    
    def __init__(self, season_end=2026, delay=30, run_minutes=30, rest_minutes=5):
        self.season_end = season_end
        self.min_delay = delay
        self.max_delay = delay * 1.5
        self.run_duration = timedelta(minutes=run_minutes)
        self.rest_duration = timedelta(minutes=rest_minutes)
        
        self.storage = get_pbp_storage(season_end=season_end)
        self.stats = {
            'processed': 0,
            'success': 0,
            'failed': 0,
            'started_at': datetime.now()
        }
        
        # 游戏列表缓存
        self.games_list = None
    
    def _random_delay(self):
        """随机延迟"""
        delay = random.uniform(self.min_delay, self.max_delay)
        logger.info(f"等待 {delay:.1f} 秒...")
        time.sleep(delay)
    
    def _check_run_time(self, start_time):
        """检查是否需要休息"""
        elapsed = datetime.now() - start_time
        if elapsed > self.run_duration:
            logger.info(f"已运行 {elapsed}, 需要休息 {self.rest_duration}")
            return True
        return False
    
    def _simulate_human_behavior(self, page):
        """模拟真实用户行为"""
        try:
            # 随机滚动
            for _ in range(random.randint(1, 3)):
                page.mouse.wheel(0, random.randint(100, 300))
                time.sleep(random.uniform(0.3, 0.8))
            
            # 随机暂停
            time.sleep(random.uniform(0.5, 1.5))
        except:
            pass
    
    def _get_random_user_agent(self):
        """获取随机 User-Agent"""
        return random.choice(self.USER_AGENTS)
    
    def _get_game_list_from_csv(self):
        """从 CSV 文件加载游戏列表"""
        import pandas as pd
        
        csv_path = os.path.join(os.path.dirname(__file__), 'CSV', f'{self.season_end}_season', f'all_games_{self.season_end}.csv')
        
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
            logger.info(f"加载游戏列表: {len(df)} 场")
            return df.to_dict('records')
        else:
            logger.warning(f"游戏列表文件不存在: {csv_path}")
            return []
    
    def _extract_game_id(self, boxscore_url):
        """从 URL 提取游戏 ID"""
        return boxscore_url.split('/')[-1].replace('.html', '')
    
    def _crawl_pbp_page(self, page, pbp_url):
        """爬取单个 PBP 页面"""
        # 使用随机 User-Agent
        page.set_extra_http_headers({
            'User-Agent': self._get_random_user_agent()
        })
        
        logger.info(f"加载页面: {pbp_url}")
        
        # 导航到页面
        page.goto(pbp_url, wait_until='domcontentloaded', timeout=180000)
        
        # 等待 Cloudflare 验证
        max_wait_time = 180
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            content = page.content()
            
            # 检查是否仍在验证页面
            challenge_keywords = ["Checking your browser", "Just a moment", 
                                "security verification", "Performing security verification",
                                "cf-turnstile", "Cloudflare"]
            is_challenge = any(keyword in content for keyword in challenge_keywords)
            
            if is_challenge:
                logger.info("检测到 Cloudflare 验证，等待通过...")
                time.sleep(5)
                continue
            
            # 检查页面是否真正加载完成
            if "Play-by-Play" in content or "pbp" in content.lower():
                tables = page.query_selector_all('table')
                if len(tables) > 0:
                    logger.info("✓ Cloudflare 验证通过，页面加载完成")
                    break
            
            time.sleep(3)
        
        # 模拟人类行为
        self._simulate_human_behavior(page)
        
        return page.content()
    
    def _parse_pbp_data(self, content, game_id):
        """解析 PBP 数据"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # 查找 PBP 表格
        pbp_table = soup.find('table', id='pbp')
        if not pbp_table:
            # 尝试其他选择器
            pbp_table = soup.find('table', {'id': lambda x: x and 'pbp' in x.lower()})
        
        if not pbp_table:
            logger.warning(f"未找到 PBP 表格: {game_id}")
            return None
        
        pbp_data = []
        
        # 获取表头
        headers = []
        header_row = pbp_table.find('thead')
        if header_row:
            for th in header_row.find_all('th'):
                headers.append(th.get_text(strip=True))
        
        # 解析数据行
        rows = pbp_table.find('tbody').find_all('tr') if pbp_table.find('tbody') else pbp_table.find_all('tr')
        
        for row in rows:
            try:
                cells = row.find_all(['td', 'th'])
                row_data = {}
                
                for i, cell in enumerate(cells):
                    if i < len(headers):
                        row_data[headers[i]] = cell.get_text(strip=True)
                    else:
                        row_data[f'col_{i}'] = cell.get_text(strip=True)
                
                if row_data:
                    pbp_data.append(row_data)
            except Exception as e:
                logger.warning(f"解析行失败: {e}")
        
        logger.info(f"解析到 {len(pbp_data)} 条 PBP 记录")
        return pbp_data
    
    def crawl_season_pbp(self, max_games=None):
        """爬取赛季 PBP 数据"""
        logger.info("=" * 60)
        logger.info(f"开始使用安全爬虫爬取 {self.season_end} 赛季 PBP 数据")
        logger.info("=" * 60)
        
        # 获取游戏列表
        games = self._get_game_list_from_csv()
        if not games:
            logger.error("没有游戏数据可爬取")
            return
        
        total_games = len(games)
        start_time = datetime.now()
        run_session_start = datetime.now()
        
        with sync_playwright() as p:
            # 启动浏览器（非无头模式更易通过验证）
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            try:
                for game in games:
                    if max_games and self.stats['processed'] >= max_games:
                        logger.info(f"已达到最大爬取数量 {max_games}")
                        break
                    
                    boxscore_url = game.get('boxscore_url', '')
                    if not boxscore_url:
                        continue
                    
                    game_id = self._extract_game_id(boxscore_url)
                    
                    # 检查是否已处理
                    if self.storage.is_game_processed(game_id):
                        logger.info(f"游戏已处理，跳过: {game_id}")
                        continue
                    
                    # 检查是否需要休息
                    if self._check_run_time(run_session_start):
                        logger.info(f"休息 {self.rest_duration.total_seconds()} 秒...")
                        time.sleep(self.rest_duration.total_seconds())
                        run_session_start = datetime.now()
                    
                    visitor_team = game.get('visitor_team', 'Unknown')
                    home_team = game.get('home_team', 'Unknown')
                    
                    logger.info(f"\n处理: {visitor_team} @ {home_team} ({game_id})")
                    
                    try:
                        # 构建 PBP URL
                        pbp_url = boxscore_url.replace('/boxscores/', '/boxscores/pbp/')
                        
                        # 爬取页面
                        content = self._crawl_pbp_page(page, pbp_url)
                        
                        # 解析数据
                        pbp_data = self._parse_pbp_data(content, game_id)
                        
                        if pbp_data:
                            game_metadata = {
                                'game_id': game_id,
                                'date': game.get('date', ''),
                                'visitor_team': visitor_team,
                                'home_team': home_team,
                                'boxscore_url': boxscore_url
                            }
                            
                            result = self.storage.process_single_game(game_metadata, pbp_data)
                            
                            if result.get('success'):
                                self.stats['success'] += 1
                                logger.info("✓ 保存成功")
                            else:
                                self.stats['failed'] += 1
                                logger.error(f"✗ 保存失败: {result.get('error')}")
                        else:
                            self.stats['failed'] += 1
                            logger.warning("未获取到 PBP 数据")
                            
                    except Exception as e:
                        self.stats['failed'] += 1
                        logger.error(f"爬取失败: {e}")
                    
                    self.stats['processed'] += 1
                    
                    elapsed = datetime.now() - start_time
                    logger.info(
                        f"进度: {self.stats['processed']}/{total_games} "
                        f"| 成功: {self.stats['success']} "
                        f"| 失败: {self.stats['failed']} "
                        f"| 耗时: {elapsed}"
                    )
                    
                    if self.stats['processed'] % 5 == 0:
                        summary = self.storage.get_import_summary()
                        logger.info(f"导入摘要: {summary}")
                    
                    if self.stats['processed'] < total_games:
                        self._random_delay()
            
            finally:
                browser.close()
        
        elapsed = datetime.now() - self.stats['started_at']
        summary = self.storage.get_import_summary()
        
        logger.info("=" * 60)
        logger.info(f"爬取完成!")
        logger.info(f"总耗时: {elapsed}")
        logger.info(f"处理: {self.stats['processed']} | 成功: {self.stats['success']} | 失败: {self.stats['failed']}")
        logger.info(f"导入摘要: {summary}")
        logger.info("=" * 60)
        
        self.storage.close()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='安全 PBP 数据爬虫')
    parser.add_argument('--season', type=int, default=2026, help='赛季结束年份')
    parser.add_argument('--max-games', type=int, default=None, help='最大爬取数量')
    parser.add_argument('--delay', type=int, default=30, help='请求间隔秒数')
    parser.add_argument('--run-minutes', type=int, default=30, help='单次运行分钟数')
    parser.add_argument('--rest-minutes', type=int, default=5, help='休息分钟数')
    
    args = parser.parse_args()
    
    crawler = SafePBPCrawler(
        season_end=args.season,
        delay=args.delay,
        run_minutes=args.run_minutes,
        rest_minutes=args.rest_minutes
    )
    
    crawler.crawl_season_pbp(max_games=args.max_games)


if __name__ == "__main__":
    main()
