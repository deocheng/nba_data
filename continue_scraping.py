#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
继续爬取 NBA 2026 赛季数据
使用 br-scraper 专用爬虫
防屏蔽策略：间隔30秒，每30分钟暂停5分钟
"""
import sys
import os
import time
import random
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from basketball_reference_web_scraper import client
from basketball_reference_web_scraper.data import Team, OutputType

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    print('=' * 80)
    print('继续爬取 NBA 2026 赛季数据')
    print('=' * 80)
    print()
    
    # 配置参数
    season_end_year = 2026
    min_delay = 30  # 最小延迟30秒
    max_delay = 30  # 最大延迟30秒
    run_interval = 30 * 60  # 运行30分钟
    rest_interval = 5 * 60   # 休息5分钟
    
    # 月份列表（从 october 到 may）
    months = ['october', 'november', 'december', 'january', 'february', 'march', 'april', 'may']
    
    # 检查已爬取的进度
    progress_file = 'CSV/2026_season/scraping_progress.json'
    if os.path.exists(progress_file):
        import json
        with open(progress_file, 'r') as f:
            progress = json.load(f)
        completed_months = progress.get('completed_months', [])
        logger.info(f'已完成月份: {completed_months}')
    else:
        completed_months = []
    
    # 开始爬取
    start_time = time.time()
    total_games = 0
    
    for month in months:
        if month in completed_months:
            logger.info(f'跳过已完成的月份: {month}')
            continue
        
        logger.info('=' * 80)
        logger.info(f'开始爬取 {month} 月份数据')
        logger.info('=' * 80)
        
        try:
            # 使用 br-scraper 获取月份数据
            # 注意：br-scraper 可能没有直接的月份API，需要使用其他方法
            
            # 方法1：使用 season_schedule 获取整个赛季数据
            # 方法2：使用 Playwright 爬取月份页面
            
            # 这里我们使用已有的 schedule_scraper
            from crawler.schedule_scraper import ScheduleScraper
            
            scraper = ScheduleScraper(
                headless=True,
                min_delay=min_delay,
                max_delay=max_delay
            )
            
            # 爬取该月份
            df = scraper.scrape_month_schedule(2025, month, output_dir='CSV/2026_season/monthly')
            
            if not df.empty:
                total_games += len(df)
                logger.info(f'✅ {month} 月爬取完成: {len(df)} 场比赛')
                
                # 记录进度
                completed_months.append(month)
                progress = {'completed_months': completed_months, 'total_games': total_games}
                with open(progress_file, 'w') as f:
                    json.dump(progress, f)
            
            # 检查是否需要休息
            elapsed = time.time() - start_time
            if elapsed >= run_interval:
                logger.info('=' * 80)
                logger.info(f'已运行 {elapsed/60:.1f} 分钟，休息 {rest_interval/60:.0f} 分钟...')
                logger.info('=' * 80)
                time.sleep(rest_interval)
                start_time = time.time()
            
            # 防屏蔽延迟
            if month != months[-1]:
                delay = random.uniform(min_delay, max_delay)
                logger.info(f'等待 {delay:.1f} 秒...')
                time.sleep(delay)
                
        except Exception as e:
            logger.error(f'❌ 爬取 {month} 月失败: {e}')
            import traceback
            traceback.print_exc()
            continue
    
    logger.info('=' * 80)
    logger.info(f'✅ 爬取完成！总共获取 {total_games} 场比赛')
    logger.info('=' * 80)

if __name__ == '__main__':
    main()