#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入2026 NBA总决赛G3数据（手动复制粘贴的数据）
"""
import os
import sys
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

def parse_g3_pbp(file_path):
    """解析G3的PBP数据"""
    df = pd.read_excel(file_path, sheet_name='G3')
    
    print(f"读取到 {len(df)} 行数据")
    
    # 找到PBP数据的起始行（包含时间格式的行）
    start_row = None
    for i in range(len(df)):
        first_col = str(df.iloc[i, 0])
        if len(first_col) == 8 and first_col.count(':') == 2:
            start_row = i
            break
    
    if start_row is None:
        print("❌ 未找到PBP数据起始行")
        return None
    
    print(f"PBP数据从第 {start_row} 行开始")
    
    # 提取PBP数据
    pbp_data = []
    for i in range(start_row, len(df)):
        time_str = str(df.iloc[i, 0])
        
        # 检查是否为有效时间格式
        if len(time_str) != 8 or time_str.count(':') != 2:
            continue
        
        # 跳过干扰行
        if 'Share & Export' in time_str or 'nan' == time_str:
            continue
        
        row_data = {
            'time': time_str,
            'visitor_action': str(df.iloc[i, 1]) if pd.notna(df.iloc[i, 1]) else '',
            'visitor_score': str(df.iloc[i, 2]) if pd.notna(df.iloc[i, 2]) else '',
            'score': str(df.iloc[i, 3]) if pd.notna(df.iloc[i, 3]) else '',
            'home_score': str(df.iloc[i, 4]) if pd.notna(df.iloc[i, 4]) else '',
            'home_action': str(df.iloc[i, 5]) if pd.notna(df.iloc[i, 5]) else '',
            'row_number': i
        }
        
        # 过滤空行
        if row_data['visitor_action'] == 'nan':
            row_data['visitor_action'] = ''
        if row_data['home_action'] == 'nan':
            row_data['home_action'] = ''
        
        if row_data['visitor_action'] or row_data['home_action'] or 'End of' in row_data['home_action'] or 'End of' in row_data['visitor_action']:
            pbp_data.append(row_data)
    
    print(f"解析到 {len(pbp_data)} 条PBP记录")
    return pbp_data

def import_to_database(pbp_data):
    """将PBP数据导入数据库"""
    from data_importer.pbp_storage import get_pbp_storage
    
    storage = get_pbp_storage(season_end=2026)
    
    # 构造比赛信息
    game_info = {
        'game_id': '202606070SAS',
        'game_date': '2026-06-07',
        'visitor_team': 'New York Knicks',
        'visitor_abbrev': 'NYK',
        'home_team': 'San Antonio Spurs',
        'home_abbrev': 'SAS',
        'boxscore_url': '/boxscores/202606070SAS.html'
    }
    
    # 将PBP数据转换为存储格式
    formatted_pbp = []
    for idx, record in enumerate(pbp_data):
        cells = [
            record['time'],
            record['visitor_action'],
            record['visitor_score'],
            record['score'],
            record['home_score'],
            record['home_action']
        ]
        formatted_pbp.append({
            'row': idx,
            'cells': cells
        })
    
    result = storage.process_single_game(game_info, formatted_pbp)
    
    if result.get('success'):
        print("✅ G3数据导入成功！")
        print(f"记录数: {len(formatted_pbp)}")
    else:
        print(f"❌ 导入失败: {result.get('error')}")
    
    storage.close()
    return result

def main():
    file_path = 'CSV/2026 final NYK vs SAS.xlsx'
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return
    
    print("=== 开始导入G3数据 ===")
    
    # 解析PBP数据
    pbp_data = parse_g3_pbp(file_path)
    
    if pbp_data is None or len(pbp_data) == 0:
        print("❌ 未解析到有效数据")
        return
    
    # 显示前10条数据预览
    print("\n前10条PBP数据预览:")
    for i, record in enumerate(pbp_data[:10]):
        print(f"{i+1}. {record['time']} | {record['visitor_action'][:30]} | {record['home_action'][:30]}")
    
    # 导入数据库
    import_to_database(pbp_data)
    
    print("\n=== G3数据导入完成 ===")

if __name__ == "__main__":
    main()