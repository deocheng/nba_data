#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增量更新模块 - 用于增量爬取和更新数据
"""
import os
import time
import logging
import pandas as pd
from datetime import datetime, timedelta
from nba_data.crawler.data_source_selector import DataSourceSelector
from nba_data.processor.data_cleaner import DataCleaner
from nba_data.storage.file_storage import FileStorage

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IncrementalUpdater:
    """增量更新类"""
    
    def __init__(self):
        """
        初始化增量更新器
        """
        self.selector = DataSourceSelector()
        self.cleaner = DataCleaner()
        self.storage = FileStorage()
    
    def check_update_needed(self, file_path, days_threshold=7):
        """
        检查是否需要更新
        
        Args:
            file_path: 文件路径
            days_threshold: 天数阈值
            
        Returns:
            bool: 是否需要更新
        """
        if not os.path.exists(file_path):
            logger.info(f"文件不存在，需要更新: {file_path}")
            return True
        
        # 检查文件修改时间
        mtime = os.path.getmtime(file_path)
        mtime_date = datetime.fromtimestamp(mtime)
        current_date = datetime.now()
        days_since_update = (current_date - mtime_date).days
        
        if days_since_update >= days_threshold:
            logger.info(f"文件已超过 {days_threshold} 天未更新，需要更新: {file_path}")
            return True
        else:
            logger.info(f"文件最近 {days_since_update} 天内已更新，不需要更新: {file_path}")
            return False
    
    def update_team_stats(self, team_abbr, season, team_id):
        """
        更新球队统计数据
        
        Args:
            team_abbr: 球队缩写
            season: 赛季
            team_id: 球队ID
        """
        # 检查是否需要更新
        file_path = os.path.join('nba_data', team_abbr, 'team_stats', f'team_stats_{season}.csv')
        if not self.check_update_needed(file_path):
            return
        
        # 获取球队统计数据
        data = self.selector.get_team_stats(team_id, team_abbr, season)
        
        # 清洗数据
        cleaned_data = self.cleaner.clean_team_stats(data)
        
        # 保存数据
        self.storage.save_team_stats(team_abbr, season, cleaned_data)
        
        logger.info(f"球队 {team_abbr} 的 {season} 赛季数据已更新")
    
    def update_team_schedule(self, team_abbr, season):
        """
        更新球队赛程
        
        Args:
            team_abbr: 球队缩写
            season: 赛季
        """
        # 检查是否需要更新
        file_path = os.path.join('nba_data', team_abbr, 'schedule', f'schedule_{season}.csv')
        if not self.check_update_needed(file_path):
            return
        
        # 获取球队赛程数据
        data = self.selector.get_team_schedule(team_abbr, season)
        
        # 清洗数据
        cleaned_data = self.cleaner.clean_schedule(data)
        
        # 保存数据
        self.storage.save_team_schedule(team_abbr, season, cleaned_data)
        
        logger.info(f"球队 {team_abbr} 的 {season} 赛季赛程已更新")
    
    def update_standings(self, season):
        """
        更新赛季排名
        
        Args:
            season: 赛季
        """
        # 检查是否需要更新
        file_path = os.path.join('nba_data', 'season', season, f'standings_{season}.csv')
        if not self.check_update_needed(file_path):
            return
        
        # 获取赛季排名数据
        data = self.selector.get_standings(season)
        
        # 清洗数据
        if isinstance(data, dict) and 'east' in data and 'west' in data:
            cleaned_east = self.cleaner.clean_standings(data['east'])
            cleaned_west = self.cleaner.clean_standings(data['west'])
            cleaned_data = {'east': cleaned_east, 'west': cleaned_west}
        else:
            cleaned_data = self.cleaner.clean_standings(data)
        
        # 保存数据
        self.storage.save_standings(season, cleaned_data)
        
        logger.info(f"{season} 赛季排名已更新")
    
    def incremental_update(self, teams_data, season):
        """
        增量更新所有数据
        
        Args:
            teams_data: 球队数据
            season: 赛季
        """
        logger.info(f"开始增量更新 {season} 赛季的数据")
        
        # 更新所有球队的统计数据
        for team in teams_data:
            team_abbr = team['abbreviation']
            team_id = team['id']
            try:
                self.update_team_stats(team_abbr, season, team_id)
                self.update_team_schedule(team_abbr, season)
            except Exception as e:
                logger.error(f"更新 {team_abbr} 数据失败: {e}")
            
            # 避免请求过于频繁
            time.sleep(1)
        
        # 更新赛季排名
        try:
            self.update_standings(season)
        except Exception as e:
            logger.error(f"更新赛季排名失败: {e}")
        
        logger.info(f"{season} 赛季的数据增量更新完成")

if __name__ == "__main__":
    # 测试增量更新模块
    import json
    
    # 加载球队数据
    with open('nba_data/teams.json', 'r', encoding='utf-8') as f:
        teams_data = json.load(f)
    
    updater = IncrementalUpdater()
    
    # 测试增量更新
    updater.incremental_update(teams_data, '2023-24')