#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试导入
"""
import sys
import os
import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_importer.database import DatabaseManager
from data_importer.config import DatabaseConfig

def main():
    db_config = DatabaseConfig()
    db_manager = DatabaseManager(db_config)
    
    excel_file = 'CSV/2026 final NYK vs SAS.xlsx'
    wb = openpyxl.load_workbook(excel_file)
    ws = wb['G1']
    
    print('=' * 80)
    print('测试解析')
    print('=' * 80)
    
    # 查看行 70-100 的数据
    for row_num in range(70, 110):
        row = list(ws.iter_rows(min_row=row_num, max_row=row_num, min_col=1, max_col=25, values_only=True))[0]
        print(f'Row {row_num}: {[str(x)[:30] if x else "" for x in row[:22]]}')
    
    db_manager.close()

if __name__ == '__main__':
    main()
