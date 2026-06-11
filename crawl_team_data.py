#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
球队数据爬取主程序
控制爬取顺序：先最近4年，再往前推移
支持断点续传
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'crawler'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'storage'))

from team_data_crawler import TeamDataCrawler
from team_data_storage import TeamDataStorage
import logging
from datetime import datetime
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('team_crawler.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class TeamDataCrawlerManager:
    """球队数据爬取管理器"""
    
    def __init__(self):
        self.crawler = TeamDataCrawler()
        self.storage = TeamDataStorage()
        self.seasons = ['2025-26', '2024-25', '2023-24', '2022-23']
        self.teams = [
            'ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN',
            'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA',
            'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHX',
            'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS'
        ]
    
    def crawl_team_season(self, team_abbr, season):
        """爬取单个球队单个赛季的数据"""
        logger.info(f"开始爬取 {team_abbr} {season} 赛季数据...")
        
        csv_file = self.crawler.scrape_team_season_data(team_abbr, season)
        
        if csv_file and Path(csv_file).exists():
            logger.info(f"爬取成功，正在存储到数据库...")
            inserted = self.storage.insert_from_csv(csv_file, team_abbr, season)
            logger.info(f"存储完成: {inserted} 条数据")
            
            self.crawler.save_progress(team_abbr, season, 'completed')
            return True
        else:
            logger.warning(f"爬取失败或无数据")
            return False
    
    def crawl_all_recent_data(self, resume=True):
        """爬取所有球队最近4年数据"""
        logger.info("=" * 60)
        logger.info("开始爬取所有球队最近4年数据")
        logger.info("=" * 60)
        
        total_operations = len(self.seasons) * len(self.teams)
        current_operation = 0
        
        for season in self.seasons:
            logger.info(f"\n{'=' * 60}")
            logger.info(f"赛季: {season}")
            logger.info(f"{'=' * 60}")
            
            for team_abbr in self.teams:
                current_operation += 1
                
                if resume and self.crawler.is_already_completed(team_abbr, season):
                    logger.info(f"[{current_operation}/{total_operations}] {team_abbr} {season} - 已完成，跳过")
                    continue
                
                logger.info(f"[{current_operation}/{total_operations}] 正在爬取 {team_abbr} {season}...")
                
                success = self.crawl_team_season(team_abbr, season)
                
                if success:
                    logger.info(f"✓ {team_abbr} {season} 完成")
                else:
                    logger.warning(f"✗ {team_abbr} {season} 失败")
                
                time.sleep(1)
        
        logger.info("\n" + "=" * 60)
        logger.info("所有数据爬取完成！")
        logger.info("=" * 60)
    
    def crawl_single_team_all_seasons(self, team_abbr):
        """爬取单个球队所有4个赛季的数据"""
        logger.info(f"\n开始爬取 {team_abbr} 所有赛季数据...")
        
        for season in self.seasons:
            self.crawl_team_season(team_abbr, season)
            time.sleep(1)
        
        logger.info(f"{team_abbr} 所有赛季数据爬取完成！")
    
    def crawl_single_season_all_teams(self, season):
        """爬取单个赛季所有球队的数据"""
        logger.info(f"\n开始爬取 {season} 赛季所有球队数据...")
        
        for team_abbr in self.teams:
            self.crawl_team_season(team_abbr, season)
            time.sleep(1)
        
        logger.info(f"{season} 赛季所有球队数据爬取完成！")
    
    def show_statistics(self):
        """显示数据库统计信息"""
        logger.info("\n数据库统计:")
        
        teams = self.storage.get_all_teams()
        logger.info(f"已爬取球队数: {len(teams)}")
        
        seasons = self.storage.get_all_seasons()
        logger.info(f"已爬取赛季数: {len(seasons)}")
        
        for team in teams:
            count = self.storage.get_statistics(team_abbr=team)
            logger.info(f"  {team}: {count} 条数据")
        
        for season in seasons:
            count = self.storage.get_statistics(season=season)
            logger.info(f"  {season}: {count} 条数据")

def main():
    """主函数"""
    print("=" * 60)
    print("NBA球队数据爬取工具")
    print("=" * 60)
    print("\n请选择操作:")
    print("1. 爬取所有球队最近4年数据（推荐：缓慢谨慎）")
    print("2. 爬取单个球队所有赛季数据")
    print("3. 爬取单个赛季所有球队数据")
    print("4. 显示数据库统计信息")
    print("5. 测试爬虫（爬取1个球队1个赛季）")
    print("q. 退出")
    
    choice = input("\n请输入选项: ").strip()
    
    manager = TeamDataCrawlerManager()
    
    if choice == '1':
        logger.info("\n开始爬取所有球队最近4年数据...")
        logger.info("这可能需要较长时间，请耐心等待...")
        logger.info("程序会每10秒显示一次进度...")
        manager.crawl_all_recent_data(resume=True)
        manager.show_statistics()
    
    elif choice == '2':
        team = input("请输入球队缩写（如 GSW）: ").strip().upper()
        manager.crawl_single_team_all_seasons(team)
    
    elif choice == '3':
        season = input("请输入赛季（如 2025-26）: ").strip()
        manager.crawl_single_season_all_teams(season)
    
    elif choice == '4':
        manager.show_statistics()
    
    elif choice == '5':
        logger.info("\n测试模式：爬取1个球队1个赛季")
        manager.crawl_team_season('OKC', '2025-26')
    
    elif choice.lower() == 'q':
        print("退出程序")
        return
    
    else:
        print("无效选项")

if __name__ == '__main__':
    main()