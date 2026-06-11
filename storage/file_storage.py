#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件存储模块 - 用于将数据保存到文件中
"""
import os
import json
import csv
import pandas as pd
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FileStorage:
    """文件存储类"""
    
    def __init__(self, base_dir="nba_data"):
        """
        初始化文件存储
        
        Args:
            base_dir: 基础目录
        """
        self.base_dir = base_dir
        self._ensure_directories()
    
    def _ensure_directories(self):
        """
        确保目录结构存在
        """
        # 确保基础目录存在
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
            logger.info(f"创建基础目录: {self.base_dir}")
    
    def save_team_stats(self, team_abbr, season, data):
        """
        保存球队统计数据
        
        Args:
            team_abbr: 球队缩写
            season: 赛季
            data: 球队统计数据
        """
        # 确保球队目录存在
        team_dir = os.path.join(self.base_dir, team_abbr, "team_stats")
        if not os.path.exists(team_dir):
            os.makedirs(team_dir, exist_ok=True)
            logger.info(f"创建球队目录: {team_dir}")
        
        # 保存为CSV文件
        file_path = os.path.join(team_dir, f"team_stats_{season}.csv")
        
        if isinstance(data, pd.DataFrame):
            data.to_csv(file_path, index=False)
        else:
            # 如果不是DataFrame，尝试转换
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False)
        
        logger.info(f"球队统计数据保存到: {file_path}")
        return file_path
    
    def save_player_stats(self, team_abbr, player_name, season, data):
        """
        保存球员统计数据
        
        Args:
            team_abbr: 球队缩写
            player_name: 球员姓名
            season: 赛季
            data: 球员统计数据
        """
        # 确保球员目录存在
        player_dir = os.path.join(self.base_dir, team_abbr, "players", player_name.replace(' ', '_'))
        if not os.path.exists(player_dir):
            os.makedirs(player_dir, exist_ok=True)
            logger.info(f"创建球员目录: {player_dir}")
        
        # 保存为CSV文件
        file_path = os.path.join(player_dir, f"player_stats_{season}.csv")
        
        if isinstance(data, pd.DataFrame):
            data.to_csv(file_path, index=False)
        else:
            # 如果不是DataFrame，尝试转换
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False)
        
        logger.info(f"球员统计数据保存到: {file_path}")
        return file_path
    
    def save_player_gamelog(self, team_abbr, player_name, season, data):
        """
        保存球员比赛日志
        
        Args:
            team_abbr: 球队缩写
            player_name: 球员姓名
            season: 赛季
            data: 球员比赛日志数据
        """
        # 确保球员目录存在
        player_dir = os.path.join(self.base_dir, team_abbr, player_name.replace(' ', '_'), "gamelog")
        if not os.path.exists(player_dir):
            os.makedirs(player_dir, exist_ok=True)
            logger.info(f"创建球员比赛日志目录: {player_dir}")
        
        # 保存为CSV文件
        file_path = os.path.join(player_dir, f"gamelog_{season}.csv")
        
        if isinstance(data, pd.DataFrame):
            data.to_csv(file_path, index=False)
        else:
            # 如果不是DataFrame，尝试转换
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False)
        
        logger.info(f"球员比赛日志保存到: {file_path}")
        return file_path
    
    def save_team_schedule(self, team_abbr, season, data):
        """
        保存球队赛程
        
        Args:
            team_abbr: 球队缩写
            season: 赛季
            data: 球队赛程数据
        """
        # 确保球队目录存在
        team_dir = os.path.join(self.base_dir, team_abbr, "schedule")
        if not os.path.exists(team_dir):
            os.makedirs(team_dir, exist_ok=True)
            logger.info(f"创建球队赛程目录: {team_dir}")
        
        # 保存为CSV文件
        file_path = os.path.join(team_dir, f"schedule_{season}.csv")
        
        if isinstance(data, pd.DataFrame):
            data.to_csv(file_path, index=False)
        else:
            # 如果不是DataFrame，尝试转换
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False)
        
        logger.info(f"球队赛程保存到: {file_path}")
        return file_path
    
    def save_standings(self, season, data):
        """
        保存赛季排名
        
        Args:
            season: 赛季
            data: 赛季排名数据
        """
        # 确保赛季目录存在
        season_dir = os.path.join(self.base_dir, "season", season)
        if not os.path.exists(season_dir):
            os.makedirs(season_dir, exist_ok=True)
            logger.info(f"创建赛季目录: {season_dir}")
        
        # 保存为CSV文件
        if isinstance(data, dict) and 'east' in data and 'west' in data:
            # 保存东部联盟排名
            east_file_path = os.path.join(season_dir, f"standings_east_{season}.csv")
            data['east'].to_csv(east_file_path, index=False)
            logger.info(f"东部联盟排名保存到: {east_file_path}")
            
            # 保存西部联盟排名
            west_file_path = os.path.join(season_dir, f"standings_west_{season}.csv")
            data['west'].to_csv(west_file_path, index=False)
            logger.info(f"西部联盟排名保存到: {west_file_path}")
            
            return {'east': east_file_path, 'west': west_file_path}
        else:
            # 保存为单一文件
            file_path = os.path.join(season_dir, f"standings_{season}.csv")
            
            if isinstance(data, pd.DataFrame):
                data.to_csv(file_path, index=False)
            else:
                # 如果不是DataFrame，尝试转换
                df = pd.DataFrame(data)
                df.to_csv(file_path, index=False)
            
            logger.info(f"赛季排名保存到: {file_path}")
            return file_path
    
    def save_json(self, file_path, data):
        """
        保存JSON数据
        
        Args:
            file_path: 文件路径
            data: JSON数据
        """
        # 确保目录存在
        dir_path = os.path.dirname(file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"创建目录: {dir_path}")
        
        # 保存为JSON文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"JSON数据保存到: {file_path}")
        return file_path
    
    def load_csv(self, file_path):
        """
        加载CSV文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            DataFrame对象
        """
        if os.path.exists(file_path):
            logger.info(f"加载CSV文件: {file_path}")
            return pd.read_csv(file_path)
        else:
            logger.warning(f"文件不存在: {file_path}")
            return None
    
    def load_json(self, file_path):
        """
        加载JSON文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            JSON数据
        """
        if os.path.exists(file_path):
            logger.info(f"加载JSON文件: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.warning(f"文件不存在: {file_path}")
            return None

if __name__ == "__main__":
    # 测试文件存储模块
    storage = FileStorage()
    
    # 创建测试数据
    test_data = pd.DataFrame({
        'team': ['Lakers', 'Celtics'],
        'w': [50, 45],
        'l': [32, 37],
        'w_pct': [0.610, 0.549],
        'pts': [110.5, 108.2]
    })
    
    # 测试保存球队统计数据
    file_path = storage.save_team_stats('LAL', '2023-24', test_data)
    print(f"数据保存到: {file_path}")
    
    # 测试加载数据
    loaded_data = storage.load_csv(file_path)
    print("\n加载的数据:")
    print(loaded_data)