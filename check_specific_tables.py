#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查特定的表
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_importer.database import DatabaseManager
from data_importer.config import DatabaseConfig

def main():
    db_config = DatabaseConfig()
    db_manager = DatabaseManager(db_config)
    
    for table_name in ['game_metadata', 'play_by_play', 'player_game_stats']:
        print('=' * 80)
        print(f'检查表: {table_name}')
        print('=' * 80)
        
        # 检查表是否存在
        check_sql = "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)"
        exists = db_manager.fetch_one(check_sql, (table_name,))
        
        if not exists or not exists[0]:
            print(f'表 {table_name} 不存在')
            print()
            continue
            
        # 获取列名
        print(f'表 {table_name} 存在')
        
        columns_sql = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
        """
        columns = db_manager.fetch_all(columns_sql, (table_name,))
        
        for col in columns:
            print(f'  {col[0]} ({col[1]})')
        
        print()
            
    db_manager.close()

if __name__ == '__main__':
    main()
