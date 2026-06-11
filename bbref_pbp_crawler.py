#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 basketball_reference_web_scraper 专用爬虫库爬取 PBP 数据
"""

import sys
import os
import time
import random
import logging
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from basketball_reference_web_scraper import client
from basketball_reference_web_scraper.data import Team
from data_importer.pbp_storage import PBPDataStorage, get_pbp_storage

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BBRefPBPCrawler:
    """使用专用爬虫库的 PBP 爬虫"""
    
    def __init__(self, season_end=2026, delay=30, run_minutes=30, rest_minutes=5):
        self.season_end = season_end
        self.min_delay = delay
        self.max_delay = delay
        self.run_duration = timedelta(minutes=run_minutes)
        self.rest_duration = timedelta(minutes=rest_minutes)
        
        self.storage = get_pbp_storage(season_end=season_end)
        self.stats = {
            'processed': 0,
            'success': 0,
            'failed': 0,
            'started_at': datetime.now()
        }
    
    def _random_delay(self):
        delay = random.uniform(self.min_delay, self.max_delay)
        logger.info(f"等待 {delay:.1f} 秒...")
        time.sleep(delay)
    
    def _check_run_time(self, start_time):
        elapsed = datetime.now() - start_time
        if elapsed > self.run_duration:
            logger.info(f"已运行 {elapsed}, 需要休息 {self.rest_duration}")
            return True
        return False
    
    def crawl_season_pbp(self, max_games=None):
        """爬取赛季 PBP 数据"""
        logger.info("=" * 60)
        logger.info(f"开始使用专用爬虫库爬取 {self.season_end} 赛季 PBP 数据")
        logger.info("=" * 60)
        
        try:
            schedule = client.season_schedule(season_end_year=self.season_end)
            logger.info(f"获取到 {len(schedule)} 场比赛")
        except Exception as e:
            logger.error(f"获取赛程失败: {e}")
            return
        
        total_games = len(schedule)
        start_time = datetime.now()
        run_session_start = datetime.now()
        
        for idx, game_info in enumerate(schedule):
            if max_games and self.stats['processed'] >= max_games:
                logger.info(f"已达到最大爬取数量 {max_games}")
                break
            
            date_obj = game_info['date']
            home_team = game_info['home_team']
            away_team = game_info['away_team']
            
            game_id = f"{date_obj.strftime('%Y%m%d')}{home_team.value[:3]}"
            
            if self.storage.is_game_processed(game_id):
                logger.info(f"游戏已处理，跳过: {game_id}")
                continue
            
            if self._check_run_time(run_session_start):
                logger.info(f"休息 {self.rest_duration.total_seconds()} 秒...")
                time.sleep(self.rest_duration.total_seconds())
                run_session_start = datetime.now()
            
            logger.info(f"\n处理: {away_team.value} @ {home_team.value} ({game_id})")
            logger.info(f"日期: {date_obj.strftime('%Y-%m-%d')}")
            
            try:
                pbp_data = client.play_by_play(
                    home_team=home_team,
                    day=date_obj.day,
                    month=date_obj.month,
                    year=date_obj.year
                )
                
                if pbp_data:
                    logger.info(f"获取到 {len(pbp_data)} 条 PBP 记录")
                    
                    game_metadata = {
                        'game_id': game_id,
                        'date': date_obj,
                        'visitor_team': away_team.value,
                        'home_team': home_team.value,
                        'boxscore_url': f"https://www.basketball-reference.com/boxscores/{game_id}.html"
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
    
    parser = argparse.ArgumentParser(description='使用专用爬虫库爬取 PBP 数据')
    parser.add_argument('--season', type=int, default=2026, help='赛季结束年份')
    parser.add_argument('--max-games', type=int, default=None, help='最大爬取数量')
    parser.add_argument('--delay', type=int, default=30, help='请求间隔秒数')
    parser.add_argument('--run-minutes', type=int, default=30, help='单次运行分钟数')
    parser.add_argument('--rest-minutes', type=int, default=5, help='休息分钟数')
    
    args = parser.parse_args()
    
    crawler = BBRefPBPCrawler(
        season_end=args.season,
        delay=args.delay,
        run_minutes=args.run_minutes,
        rest_minutes=args.rest_minutes
    )
    
    crawler.crawl_season_pbp(max_games=args.max_games)


if __name__ == "__main__":
    main()
