#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 curl_cffi 爬取 PBP 数据 - 模拟真实浏览器 TLS 指纹
"""

import sys
import os
import time
import random
import logging
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from curl_cffi import requests
from bs4 import BeautifulSoup
from data_importer.pbp_storage import get_pbp_storage

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CurlPBPCrawler:
    """使用 curl_cffi 的 PBP 爬虫"""
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    ]
    
    def __init__(self, season_end=2026, delay=30, run_minutes=30, rest_minutes=5):
        self.season_end = season_end
        self.min_delay = delay
        self.max_delay = delay * 1.5
        self.run_duration = timedelta(minutes=run_minutes)
        self.rest_duration = timedelta(minutes=rest_minutes)
        
        self.storage = get_pbp_storage(season_end=season_end)
        self.session = None
        
    def _init_session(self):
        """初始化请求会话"""
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
        }
    
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
    
    def _fetch_page(self, url):
        """获取页面内容"""
        try:
            response = self.session.get(
                url,
                impersonate="chrome120",
                timeout=60
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"获取页面失败: {e}")
            return None
    
    def _parse_pbp_data(self, content, game_id):
        """解析 PBP 数据"""
        soup = BeautifulSoup(content, 'html.parser')
        
        pbp_table = soup.find('table', id='pbp')
        if not pbp_table:
            pbp_table = soup.find('table', {'id': lambda x: x and 'pbp' in x.lower()})
        
        if not pbp_table:
            logger.warning(f"未找到 PBP 表格: {game_id}")
            return None
        
        pbp_data = []
        
        headers = []
        header_row = pbp_table.find('thead')
        if header_row:
            for th in header_row.find_all('th'):
                headers.append(th.get_text(strip=True))
        
        rows = pbp_table.find('tbody').find_all('tr') if pbp_table.find('tbody') else pbp_table.find_all('tr')
        
        for idx, row in enumerate(rows):
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
        logger.info(f"开始使用 curl_cffi 爬取 {self.season_end} 赛季 PBP 数据")
        logger.info("=" * 60)
        
        self._init_session()
        
        games = self._get_game_list_from_csv()
        if not games:
            logger.error("没有游戏数据可爬取")
            return
        
        total_games = len(games)
        start_time = datetime.now()
        run_session_start = datetime.now()
        
        for idx, game in enumerate(games):
            if max_games and idx >= max_games:
                logger.info(f"已达到最大爬取数量 {max_games}")
                break
            
            boxscore_url = game.get('boxscore_url', '')
            if not boxscore_url:
                continue
            
            game_id = self._extract_game_id(boxscore_url)
            
            if self.storage.is_game_processed(game_id):
                logger.info(f"游戏已处理，跳过: {game_id}")
                continue
            
            if self._check_run_time(run_session_start):
                logger.info(f"休息 {self.rest_duration.total_seconds()} 秒...")
                time.sleep(self.rest_duration.total_seconds())
                run_session_start = datetime.now()
            
            visitor_team = game.get('visitor_team', 'Unknown')
            home_team = game.get('home_team', 'Unknown')
            
            logger.info(f"\n处理: {visitor_team} @ {home_team} ({game_id})")
            
            try:
                pbp_url = boxscore_url.replace('/boxscores/', '/boxscores/pbp/')
                
                if not pbp_url.startswith('https://'):
                    pbp_url = 'https://www.basketball-reference.com' + pbp_url
                
                logger.info(f"获取页面: {pbp_url}")
                content = self._fetch_page(pbp_url)
                
                if content:
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
                            logger.info("✓ 保存成功")
                        else:
                            logger.error(f"✗ 保存失败: {result.get('error')}")
                    else:
                        logger.warning("未获取到 PBP 数据")
                else:
                    logger.warning("无法获取页面内容")
                    
            except Exception as e:
                logger.error(f"爬取失败: {e}")
            
            elapsed = datetime.now() - start_time
            logger.info(f"进度: {idx+1}/{total_games} | 耗时: {elapsed}")
            
            if (idx + 1) % 5 == 0:
                summary = self.storage.get_import_summary()
                logger.info(f"导入摘要: {summary}")
            
            if idx < total_games - 1:
                self._random_delay()
        
        elapsed = datetime.now() - start_time
        summary = self.storage.get_import_summary()
        
        logger.info("=" * 60)
        logger.info(f"爬取完成!")
        logger.info(f"总耗时: {elapsed}")
        logger.info(f"导入摘要: {summary}")
        logger.info("=" * 60)
        
        self.storage.close()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='使用 curl_cffi 爬取 PBP 数据')
    parser.add_argument('--season', type=int, default=2026, help='赛季结束年份')
    parser.add_argument('--max-games', type=int, default=None, help='最大爬取数量')
    parser.add_argument('--delay', type=int, default=30, help='请求间隔秒数')
    parser.add_argument('--run-minutes', type=int, default=30, help='单次运行分钟数')
    parser.add_argument('--rest-minutes', type=int, default=5, help='休息分钟数')
    
    args = parser.parse_args()
    
    crawler = CurlPBPCrawler(
        season_end=args.season,
        delay=args.delay,
        run_minutes=args.run_minutes,
        rest_minutes=args.rest_minutes
    )
    
    crawler.crawl_season_pbp(max_games=args.max_games)


if __name__ == "__main__":
    main()
