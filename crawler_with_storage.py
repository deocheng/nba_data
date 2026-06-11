#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的 Play-by-Play 爬虫 - 即时保存文件 + 即时导入数据库
"""

import sys
import os
import time
import json
import random
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright
from data_importer.pbp_storage import PBPDataStorage, get_pbp_storage

# 尝试导入 playwright_stealth
try:
    from playwright_stealth import stealth_sync
    STEALTH_AVAILABLE = True
    logger.info("✓ playwright_stealth 已加载")
except ImportError:
    STEALTH_AVAILABLE = False
    logger.warning("✗ playwright_stealth 未安装，将尝试其他方法隐藏自动化特征")

# 随机 User-Agent 列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
]


class CrawlerWithStorage:
    """带即时存储的 Play-by-Play 爬虫"""
    
    def __init__(self, 
                 season_end: int = 2026,
                 min_delay: int = 40,
                 max_delay: int = 40,
                 headless: bool = True,
                 run_duration_minutes: int = 30,
                 rest_duration_minutes: int = 5):
        """
        初始化爬虫
        
        :param season_end: 赛季结束年份
        :param min_delay: 最小请求间隔（秒）
        :param max_delay: 最大请求间隔（秒）
        :param headless: 是否无头模式
        :param run_duration_minutes: 单次运行持续时间（分钟）
        :param rest_duration_minutes: 休息时间（分钟）
        """
        self.season_end = season_end
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.headless = headless
        self.run_duration = timedelta(minutes=run_duration_minutes)
        self.rest_duration = timedelta(minutes=rest_duration_minutes)
        
        # 加载游戏列表
        self.games_df = self._load_game_list()
        
        # 初始化存储系统
        self.storage = get_pbp_storage(season_end=season_end)
        
        # 统计
        self.stats = {
            'processed': 0,
            'success': 0,
            'failed': 0,
            'started_at': datetime.now()
        }
        
        logger.info(f"爬虫初始化完成: {len(self.games_df)} 场游戏待处理")
    
    def _load_game_list(self) -> pd.DataFrame:
        """加载游戏列表"""
        csv_path = os.path.join(os.path.dirname(__file__), 'CSV', f'{self.season_end}_season', f'all_games_{self.season_end}.csv')
        
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
            logger.info(f"加载游戏列表: {len(df)} 场")
            return df
        else:
            logger.warning(f"游戏列表文件不存在: {csv_path}")
            return pd.DataFrame()
    
    def _random_delay(self):
        """随机延迟"""
        delay = random.uniform(self.min_delay, self.max_delay)
        logger.info(f"等待 {delay:.1f} 秒...")
        time.sleep(delay)
    
    def _check_run_time(self, start_time: datetime) -> bool:
        """检查是否需要休息"""
        elapsed = datetime.now() - start_time
        if elapsed > self.run_duration:
            logger.info(f"已运行 {elapsed}, 需要休息 {self.rest_duration}")
            return True
        return False
    
    def _get_game_id(self, boxscore_url: str) -> str:
        """从 URL 中获取游戏 ID"""
        return boxscore_url.split('/')[-1].replace('.html', '')
    
    def crawl_single_game(self, row: pd.Series, page) -> Dict[str, Any]:
        """
        爬取单个游戏
        
        :param row: 游戏数据行
        :param page: Playwright 页面对象
        :return: 爬取结果
        """
        game_info = row.to_dict()
        game_id = self._get_game_id(game_info['boxscore_url'])
        
        logger.info(f"正在处理: {game_info['visitor_team']} @ {game_info['home_team']} ({game_id})")
        
        try:
            # 构建完整的 PBP URL
            boxscore_url = game_info['boxscore_url']
            if not boxscore_url.startswith('https://'):
                boxscore_url = 'https://' + boxscore_url.lstrip('/')
            
            pbp_url = boxscore_url.replace('/boxscores/', '/boxscores/pbp/')
            
            # 确保 URL 完整
            if not pbp_url.startswith('https://'):
                pbp_url = 'https://www.basketball-reference.com' + pbp_url
            
            logger.info(f"加载页面: {pbp_url}")
            page.goto(pbp_url, wait_until='domcontentloaded', timeout=180000)
            
            # 等待 Cloudflare 验证 - 使用更强大的等待策略
            max_wait_time = 180  # 最大等待180秒
            start_time = time.time()
            verification_passed = False
            
            while time.time() - start_time < max_wait_time:
                content = page.content()
                
                # 检查是否仍在验证页面
                is_challenge = False
                challenge_keywords = ["Checking your browser", "Just a moment", "security verification", 
                                    "Performing security verification", "cf-turnstile"]
                for keyword in challenge_keywords:
                    if keyword in content:
                        is_challenge = True
                        break
                
                if is_challenge:
                    logger.info("检测到 Cloudflare 验证，等待通过...")
                    # 尝试点击可能存在的验证按钮
                    try:
                        # 尝试找到并点击 Turnstile 验证按钮
                        turnstile_button = page.query_selector('button[data-action="challenge"]') or \
                                          page.query_selector('.ctp-button') or \
                                          page.query_selector('input[type="submit"]')
                        if turnstile_button:
                            logger.info("找到验证按钮，尝试点击...")
                            turnstile_button.click()
                    except:
                        pass
                    time.sleep(5)
                    continue
                
                # 检查页面是否真正加载完成（包含 PBP 相关内容）
                if "Play-by-Play" in content or "pbp" in content.lower():
                    # 检查是否有实际的表格内容
                    tables = page.query_selector_all('table')
                    if len(tables) > 0:
                        verification_passed = True
                        logger.info("✓ Cloudflare 验证通过，页面加载完成")
                        break
                
                time.sleep(3)
            
            if not verification_passed:
                logger.error("Cloudflare 验证超时或页面未正确加载")
                # 保存调试页面
                try:
                    html_path = os.path.join('debug', f'{game_id}_timeout.html')
                    os.makedirs('debug', exist_ok=True)
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(page.content())
                    logger.info(f"超时页面内容已保存到: {html_path}")
                except:
                    pass
                return {'success': False, 'error': 'Cloudflare 验证超时', 'game_id': game_id}
            
            # 查找 PBP 表格 - 使用多种选择器
            pbp_table = None
            selectors = ['table#pbp', 'table[id*="pbp"]', 'table.stats_table', 'table']
            
            for selector in selectors:
                tables = page.query_selector_all(selector)
                for table in tables:
                    # 检查表格是否包含 PBP 数据
                    headers = table.query_selector_all('thead th')
                    header_texts = [h.inner_text().strip().lower() for h in headers]
                    if any('time' in h or 'period' in h or 'score' in h for h in header_texts):
                        pbp_table = table
                        logger.info(f"找到 PBP 表格: {selector}")
                        break
                if pbp_table:
                    break
            
            if not pbp_table:
                logger.warning(f"未找到 PBP 表格: {game_id}")
                # 尝试获取页面内容来调试
                try:
                    html_path = os.path.join('debug', f'{game_id}.html')
                    os.makedirs('debug', exist_ok=True)
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(page.content())
                    logger.info(f"页面内容已保存到: {html_path}")
                except:
                    pass
                return {'success': False, 'error': '未找到 PBP 表格', 'game_id': game_id}
            
            # 解析表格
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
            
            logger.info(f"解析到 {len(pbp_data)} 条 PBP 记录")
            
            # 使用存储系统即时保存
            result = self.storage.process_single_game(game_info, pbp_data)
            
            return result
            
        except Exception as e:
            logger.error(f"爬取游戏 {game_id} 失败: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e), 'game_id': game_id}
    
    def crawl(self, max_games: int = None):
        """
        开始爬取
        
        :param max_games: 最大爬取数量（None 表示全部）
        """
        if self.games_df.empty:
            logger.error("没有游戏数据可爬取")
            return
        
        total_games = len(self.games_df)
        processed = 0
        start_time = datetime.now()
        run_session_start = datetime.now()
        
        with sync_playwright() as p:
            # 创建持久化浏览器Profile目录
            user_data_dir = os.path.join(os.path.dirname(__file__), 'browser_profile')
            os.makedirs(user_data_dir, exist_ok=True)
            logger.info(f"使用持久化浏览器Profile: {user_data_dir}")
            
            # 使用 launch_persistent_context 创建持久化会话
            context = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=self.headless,
                channel="chrome",
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-extensions",
                    "--no-sandbox",
                    "--start-maximized",
                    "--window-size=1920,1080",
                ],
                user_agent=random.choice(USER_AGENTS),
                viewport={"width": 1920, "height": 1080},
                locale="en-US",
                timezone_id="America/New_York",
                geolocation={"latitude": 40.7128, "longitude": -74.0060},
                permissions=["geolocation"],
            )
            
            page = context.new_page()
            
            # 应用 stealth 隐藏自动化特征
            if STEALTH_AVAILABLE:
                logger.info("✓ 应用 stealth 隐藏自动化特征")
                stealth_sync(page)
            
            try:
                for idx, row in self.games_df.iterrows():
                    game_id = self._get_game_id(row['boxscore_url'])
                    
                    # 检查是否已处理
                    if self.storage.is_game_processed(game_id):
                        logger.info(f"游戏已处理，跳过: {game_id}")
                        continue
                    
                    # 检查是否需要休息
                    if self._check_run_time(run_session_start):
                        logger.info(f"休息 {self.rest_duration.total_seconds()} 秒...")
                        time.sleep(self.rest_duration.total_seconds())
                        run_session_start = datetime.now()
                    
                    # 爬取
                    result = self.crawl_single_game(row, page)
                    
                    # 更新统计
                    self.stats['processed'] += 1
                    if result.get('success'):
                        self.stats['success'] += 1
                    else:
                        self.stats['failed'] += 1
                    
                    # 打印进度
                    elapsed = datetime.now() - start_time
                    logger.info(
                        f"进度: {self.stats['processed']}/{total_games if not max_games else max_games} "
                        f"| 成功: {self.stats['success']} "
                        f"| 失败: {self.stats['failed']} "
                        f"| 耗时: {elapsed}"
                    )
                    
                    # 打印摘要
                    if self.stats['processed'] % 5 == 0:
                        summary = self.storage.get_import_summary()
                        logger.info(f"导入摘要: {summary}")
                    
                    # 检查是否达到最大数量
                    if max_games and self.stats['processed'] >= max_games:
                        logger.info(f"已达到最大爬取数量 {max_games}")
                        break
                    
                    # 延迟
                    if self.stats['processed'] < total_games:
                        self._random_delay()
                
            finally:
                # 清理
                browser.close()
                self.storage.close()
        
        # 最终统计
        elapsed = datetime.now() - self.stats['started_at']
        summary = self.storage.get_import_summary()
        
        logger.info("=" * 60)
        logger.info(f"爬取完成!")
        logger.info(f"总耗时: {elapsed}")
        logger.info(f"处理: {self.stats['processed']} | 成功: {self.stats['success']} | 失败: {self.stats['failed']}")
        logger.info(f"导入摘要: {summary}")
        logger.info("=" * 60)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        summary = self.storage.get_import_summary()
        return {
            'crawler': self.stats,
            'storage': summary
        }


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Play-by-Play 数据爬虫 - 即时保存和导入')
    parser.add_argument('--season', type=int, default=2026, help='赛季结束年份')
    parser.add_argument('--max-games', type=int, default=5, help='最大爬取数量（用于测试）')
    parser.add_argument('--delay', type=int, default=40, help='请求间隔秒数')
    parser.add_argument('--no-headless', action='store_true', help='显示浏览器窗口')
    parser.add_argument('--run-minutes', type=int, default=30, help='单次运行分钟数')
    parser.add_argument('--rest-minutes', type=int, default=5, help='休息分钟数')
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("Play-by-Play 爬虫启动")
    logger.info("=" * 60)
    
    crawler = CrawlerWithStorage(
        season_end=args.season,
        min_delay=args.delay,
        max_delay=args.delay,
        headless=not args.no_headless,
        run_duration_minutes=args.run_minutes,
        rest_duration_minutes=args.rest_minutes
    )
    
    crawler.crawl(max_games=args.max_games)


if __name__ == "__main__":
    main()
