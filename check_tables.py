#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库表结构
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_importer.database import DatabaseManager
from data_importer.config import DatabaseConfig

def main():
    db_config = DatabaseConfig()
    db_manager = DatabaseManager(db_config)
    
    # 获取所有表
    tables_sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    tables = db_manager.fetch_all(tables_sql)
    
    print('=' * 80)
    print('数据库中的表')
    print('=' * 80)
    
    for table in tables:
        print(f'\n表: {table[0]}')
        print('-' * 60)
        
        # 获取表结构
        columns_sql = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
        """
        
        columns = db_manager.fetch_all(columns_sql, (table[0],))
        
        for col in columns:
            col_name, data_type, is_nullable, col_default = col
            print(f'  {col_name} ({data_type})')
            
    db_manager.close()

if __name__ == '__main__':
    main()
