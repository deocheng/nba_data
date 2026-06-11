#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进版PBP爬虫 - 使用持久化浏览器配置，先测试单日期爬取
"""

import sys
import os
import time
import random
import pandas as pd
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright
from data_importer.pbp_storage import get_pbp_storage
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ImprovedPBPCrawler:
    def __init__(self, season_end=2026, delay=30, run_minutes=30, rest_minutes=5):
        self.season_end = season_end
        self.min_delay = delay
        self.max_delay = delay * 1.5
        self.run_duration = timedelta(minutes=run_minutes)
        self.rest_duration = timedelta(minutes=rest_minutes)
        
        self.storage = get_pbp_storage(season_end=season_end)
        self.user_data_dir = os.path.join(os.path.dirname(__file__), 'browser_profile')
        os.makedirs(self.user_data_dir, exist_ok=True)
        
        logger.info(f"使用持久化浏览器配置目录: {self.user_data_dir}")
    
    def load_games(self):
        """加载游戏列表"""
        games_df = pd.read_csv('CSV/2026_season/all_games_2026.csv', encoding='utf-8-sig')
        logger.info(f"加载游戏列表: {len(games_df)} 场")
        return games_df
    
    def get_games_by_date(self, games_df, target_date):
        """获取指定日期的游戏"""
        games_on_date = []
        for _, row in games_df.iterrows():
            game_id = row['boxscore_url'].split('/')[-1].replace('.html', '')
            if game_id.startswith(target_date):
                games_on_date.append(row)
        return games_on_date
    
    def crawl_single_game(self, page, game_info):
        """爬取单个游戏的PBP数据"""
        game_id = game_info['boxscore_url'].split('/')[-1].replace('.html', '')
        
        logger.info(f"\n处理: {game_info['visitor_team']} @ {game_info['home_team']} ({game_id})")
        
        # 检查是否已处理
        if self.storage.is_game_processed(game_id):
            logger.info(f"游戏已处理，跳过: {game_id}")
            return True
        
        try:
            # 构建PBP URL
            pbp_url = game_info['boxscore_url'].replace('/boxscores/', '/boxscores/pbp/')
            logger.info(f"加载页面: {pbp_url}")
            
            # 导航到页面 - 使用domcontentloaded而不是networkidle以更快加载
            page.goto(pbp_url, wait_until='domcontentloaded', timeout=120000)
            
            # 等待页面内容加载
            max_wait = 30  # 最多等待30秒
            waited = 0
            
            while waited < max_wait:
                content = page.content()
                
                # 检查是否有Cloudflare验证
                is_challenge = False
                challenge_keywords = ['Checking your browser', 'Just a moment', 'Cloudflare', 'security verification']
                for keyword in challenge_keywords:
                    if keyword in content:
                        is_challenge = True
                        break
                
                if is_challenge:
                    logger.info("检测到Cloudflare验证，请手动完成...")
                    time.sleep(5)
                    waited += 5
                    continue
                
                # 检查是否有PBP内容
                if 'Play-by-Play' in content.lower():
                    logger.info("页面加载成功！")
                    break
                
                # 继续等待
                time.sleep(2)
                waited += 2
            
            # 获取页面内容
            content = page.content()
            
            # 查找PBP表格
            pbp_table = (
                page.query_selector('table#pbp') or 
                page.query_selector('table[id*="pbp"]') or 
                page.query_selector('table.stats_table') or
                page.query_selector('table')
            )
            
            if not pbp_table:
                logger.warning(f"未找到PBP表格: {game_id}")
                # 保存调试HTML
                debug_path = os.path.join('debug', f'{game_id}_debug.html')
                os.makedirs('debug', exist_ok=True)
                with open(debug_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"已保存调试HTML到: {debug_path}")
                return False
            
            # 解析PBP数据
            rows = pbp_table.query_selector_all('tr')
            pbp_data = []
            
            for idx, row_elem in enumerate(rows):
                try:
                    cells = row_elem.query_selector_all('td, th')
                    cell_texts = [cell.inner_text().strip() for cell in cells]
                    
                    if len(cell_texts) >= 4:
                        pbp_data.append({
                            'row': idx,
                            'cells': cell_texts
                        })
                except Exception as e:
                    logger.warning(f"解析行 {idx} 失败: {e}")
            
            if not pbp_data:
                logger.warning(f"未解析到PBP记录: {game_id}")
                return False
            
            logger.info(f"解析到 {len(pbp_data)} 条PBP记录")
            
            # 保存到数据库
            result = self.storage.process_single_game(game_info.to_dict(), pbp_data)
            
            if result.get('success'):
                logger.info("✓ 保存成功！")
                return True
            else:
                logger.error(f"✗ 保存失败: {result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"爬取游戏 {game_id} 失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_single_date(self, target_date):
        """测试爬取单个日期的游戏"""
        logger.info("=" * 60)
        logger.info(f"测试爬取日期 {target_date} 的游戏")
        logger.info("=" * 60)
        
        # 加载游戏列表
        games_df = self.load_games()
        
        # 获取指定日期的游戏
        games_on_date = self.get_games_by_date(games_df, target_date)
        
        if not games_on_date:
            logger.error(f"没有找到日期 {target_date} 的游戏")
            return
        
        logger.info(f"找到 {len(games_on_date)} 场游戏在 {target_date}")
        
        # 启动浏览器
        with sync_playwright() as p:
            # 使用持久化上下文
            context = p.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=False,  # 非无头模式，方便手动验证
                channel='chrome',
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--start-maximized',
                    '--window-size=1920,1080'
                ],
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York'
            )
            
            page = context.new_page()
            
            try:
                # 先访问主页建立会话
                logger.info("正在访问主页建立会话...")
                page.goto('https://www.basketball-reference.com', wait_until='domcontentloaded', timeout=60000)
                
                logger.info("\n请在浏览器中完成Cloudflare验证（如果需要），然后按Enter继续...")
                input()
                
                # 爬取该日期的游戏
                success_count = 0
                failed_count = 0
                
                for idx, game_info in enumerate(games_on_date):
                    logger.info(f"\n进度: {idx + 1}/{len(games_on_date)}")
                    
                    if self.crawl_single_game(page, game_info):
                        success_count += 1
                    else:
                        failed_count += 1
                    
                    # 不是最后一个游戏时才等待
                    if idx < len(games_on_date) - 1:
                        delay = random.uniform(self.min_delay, self.max_delay)
                        logger.info(f"等待 {delay:.1f} 秒...")
                        time.sleep(delay)
                
                logger.info("\n" + "=" * 60)
                logger.info(f"测试完成！成功: {success_count}, 失败: {failed_count}")
                logger.info("=" * 60)
                
            finally:
                context.close()
        
        self.storage.close()
    
    def crawl_all(self, start_date=None):
        """批量爬取所有游戏"""
        logger.info("=" * 60)
        logger.info("开始批量爬取PBP数据")
        logger.info("=" * 60)
        
        # 加载游戏列表
        games_df = self.load_games()
        
        # 如果指定了开始日期，筛选之后的游戏
        if start_date:
            filtered_games = []
            for _, row in games_df.iterrows():
                game_id = row['boxscore_url'].split('/')[-1].replace('.html', '')
                if game_id >= start_date:
                    filtered_games.append(row)
            games_df = pd.DataFrame(filtered_games)
            logger.info(f"筛选后剩余 {len(games_df)} 场游戏")
        
        if games_df.empty:
            logger.error("没有游戏需要爬取")
            return
        
        # 启动浏览器
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=False,
                channel='chrome',
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--start-maximized',
                    '--window-size=1920,1080'
                ],
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = context.new_page()
            
            try:
                total_games = len(games_df)
                success_count = 0
                failed_count = 0
                skipped_count = 0
                start_time = datetime.now()
                run_session_start = datetime.now()
                
                for idx, game_info in games_df.iterrows():
                    # 检查是否需要休息
                    if self._check_run_time(run_session_start):
                        logger.info(f"已运行 {datetime.now() - run_session_start}, 休息 {self.rest_duration.total_seconds()} 秒...")
                        time.sleep(self.rest_duration.total_seconds())
                        run_session_start = datetime.now()
                    
                    game_id = game_info['boxscore_url'].split('/')[-1].replace('.html', '')
                    
                    # 检查是否已处理
                    if self.storage.is_game_processed(game_id):
                        skipped_count += 1
                        continue
                    
                    logger.info(f"\n进度: {idx + 1}/{total_games} | 成功: {success_count} | 失败: {failed_count} | 跳过: {skipped_count}")
                    
                    if self.crawl_single_game(page, game_info):
                        success_count += 1
                    else:
                        failed_count += 1
                    
                    # 不是最后一个游戏时才等待
                    if idx < total_games - 1:
                        delay = random.uniform(self.min_delay, self.max_delay)
                        logger.info(f"等待 {delay:.1f} 秒...")
                        time.sleep(delay)
                
                elapsed = datetime.now() - start_time
                summary = self.storage.get_import_summary()
                
                logger.info("\n" + "=" * 60)
                logger.info(f"爬取完成！")
                logger.info(f"总耗时: {elapsed}")
                logger.info(f"成功: {success_count} | 失败: {failed_count} | 跳过: {skipped_count}")
                logger.info(f"导入摘要: {summary}")
                logger.info("=" * 60)
                
            finally:
                context.close()
        
        self.storage.close()
    
    def _check_run_time(self, start_time):
        """检查是否需要休息"""
        elapsed = datetime.now() - start_time
        return elapsed > self.run_duration

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='改进版PBP爬虫')
    parser.add_argument('--mode', choices=['test', 'crawl'], default='test', help='运行模式：test测试单日期，crawl批量爬取')
    parser.add_argument('--date', type=str, default='20251022', help='测试日期格式: YYYYMMDD')
    parser.add_argument('--start-date', type=str, default=None, help='批量爬取起始日期')
    parser.add_argument('--delay', type=int, default=30, help='请求间隔秒数')
    parser.add_argument('--run-minutes', type=int, default=30, help='单次运行分钟数')
    parser.add_argument('--rest-minutes', type=int, default=5, help='休息分钟数')
    
    args = parser.parse_args()
    
    crawler = ImprovedPBPCrawler(
        season_end=2026,
        delay=args.delay,
        run_minutes=args.run_minutes,
        rest_minutes=args.rest_minutes
    )
    
    if args.mode == 'test':
        crawler.test_single_date(args.date)
    else:
        crawler.crawl_all(start_date=args.start_date)

if __name__ == '__main__':
    main()
