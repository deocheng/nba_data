#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据清洗模块 - 用于清洗和预处理数据
"""
import pandas as pd
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataCleaner:
    """数据清洗类"""
    
    def clean_team_stats(self, df):
        """
        清洗球队统计数据
        
        Args:
            df: 球队统计数据DataFrame
            
        Returns:
            清洗后的球队统计数据
        """
        logger.info("开始清洗球队统计数据")
        
        # 复制数据以避免修改原始数据
        cleaned_df = df.copy()
        
        # 处理缺失值
        cleaned_df = cleaned_df.fillna(0)
        
        # 处理列名
        cleaned_df.columns = [col.lower().replace(' ', '_') for col in cleaned_df.columns]
        
        # 转换数据类型
        numeric_columns = [
            'gp', 'w', 'l', 'w_pct', 'min', 'fgm', 'fga', 'fg_pct',
            'fg3m', 'fg3a', 'fg3_pct', 'ftm', 'fta', 'ft_pct',
            'orb', 'drb', 'trb', 'ast', 'stl', 'blk', 'tov', 'pf', 'pts'
        ]
        
        for col in numeric_columns:
            if col in cleaned_df.columns:
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
        
        logger.info(f"球队统计数据清洗完成，形状: {cleaned_df.shape}")
        return cleaned_df
    
    def clean_player_stats(self, df):
        """
        清洗球员统计数据
        
        Args:
            df: 球员统计数据DataFrame
            
        Returns:
            清洗后的球员统计数据
        """
        logger.info("开始清洗球员统计数据")
        
        # 复制数据以避免修改原始数据
        cleaned_df = df.copy()
        
        # 处理缺失值
        cleaned_df = cleaned_df.fillna(0)
        
        # 处理列名
        cleaned_df.columns = [col.lower().replace(' ', '_') for col in cleaned_df.columns]
        
        # 转换数据类型
        numeric_columns = [
            'age', 'gp', 'gs', 'mp', 'fgm', 'fga', 'fg_pct',
            'fg3m', 'fg3a', 'fg3_pct', 'ftm', 'fta', 'ft_pct',
            'orb', 'drb', 'trb', 'ast', 'stl', 'blk', 'tov', 'pf', 'pts'
        ]
        
        for col in numeric_columns:
            if col in cleaned_df.columns:
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
        
        logger.info(f"球员统计数据清洗完成，形状: {cleaned_df.shape}")
        return cleaned_df
    
    def clean_gamelog(self, df):
        """
        清洗比赛日志数据
        
        Args:
            df: 比赛日志数据DataFrame
            
        Returns:
            清洗后的比赛日志数据
        """
        logger.info("开始清洗比赛日志数据")
        
        # 复制数据以避免修改原始数据
        cleaned_df = df.copy()
        
        # 处理缺失值
        cleaned_df = cleaned_df.fillna(0)
        
        # 处理列名
        cleaned_df.columns = [col.lower().replace(' ', '_') for col in cleaned_df.columns]
        
        # 转换数据类型
        numeric_columns = [
            'age', 'gp', 'gs', 'mp', 'fgm', 'fga', 'fg_pct',
            'fg3m', 'fg3a', 'fg3_pct', 'ftm', 'fta', 'ft_pct',
            'orb', 'drb', 'trb', 'ast', 'stl', 'blk', 'tov', 'pf', 'pts',
            'plus_minus'
        ]
        
        for col in numeric_columns:
            if col in cleaned_df.columns:
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
        
        # 处理日期列
        if 'date' in cleaned_df.columns:
            cleaned_df['date'] = pd.to_datetime(cleaned_df['date'], errors='coerce')
        elif 'game_date' in cleaned_df.columns:
            cleaned_df['game_date'] = pd.to_datetime(cleaned_df['game_date'], errors='coerce')
        
        logger.info(f"比赛日志数据清洗完成，形状: {cleaned_df.shape}")
        return cleaned_df
    
    def clean_schedule(self, df):
        """
        清洗赛程数据
        
        Args:
            df: 赛程数据DataFrame
            
        Returns:
            清洗后的赛程数据
        """
        logger.info("开始清洗赛程数据")
        
        # 复制数据以避免修改原始数据
        cleaned_df = df.copy()
        
        # 处理缺失值
        cleaned_df = cleaned_df.fillna(0)
        
        # 处理列名
        cleaned_df.columns = [col.lower().replace(' ', '_') for col in cleaned_df.columns]
        
        # 转换数据类型
        numeric_columns = ['pts', 'opp_pts', 'w', 'l']
        
        for col in numeric_columns:
            if col in cleaned_df.columns:
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
        
        # 处理日期列
        if 'date' in cleaned_df.columns:
            cleaned_df['date'] = pd.to_datetime(cleaned_df['date'], errors='coerce')
        
        logger.info(f"赛程数据清洗完成，形状: {cleaned_df.shape}")
        return cleaned_df
    
    def clean_standings(self, df):
        """
        清洗排名数据
        
        Args:
            df: 排名数据DataFrame
            
        Returns:
            清洗后的排名数据
        """
        logger.info("开始清洗排名数据")
        
        # 复制数据以避免修改原始数据
        cleaned_df = df.copy()
        
        # 处理缺失值
        cleaned_df = cleaned_df.fillna(0)
        
        # 处理列名
        cleaned_df.columns = [col.lower().replace(' ', '_') for col in cleaned_df.columns]
        
        # 转换数据类型
        numeric_columns = ['w', 'l', 'w_pct', 'gb', 'ps_g', 'pa_g', 'srs']
        
        for col in numeric_columns:
            if col in cleaned_df.columns:
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
        
        logger.info(f"排名数据清洗完成，形状: {cleaned_df.shape}")
        return cleaned_df

if __name__ == "__main__":
    # 测试数据清洗模块
    cleaner = DataCleaner()
    
    # 创建测试数据
    test_data = pd.DataFrame({
        'Team': ['Lakers', 'Celtics'],
        'W': [50, 45],
        'L': [32, 37],
        'W/L%': [0.610, 0.549],
        'PTS': [110.5, 108.2]
    })
    
    # 测试清洗球队统计数据
    cleaned_data = cleaner.clean_team_stats(test_data)
    print("清洗前:")
    print(test_data)
    print("\n清洗后:")
    print(cleaned_data)