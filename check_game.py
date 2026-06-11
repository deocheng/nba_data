#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查特定比赛是否已爬取
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_importer.pbp_storage import PBPDataStorage

def check_game(url):
    # 从 URL 提取 game_id
    game_id = url.split('/')[-1].replace('.html', '')
    print(f"检查比赛: {game_id}")
    
    # 检查文件是否存在
    pbp_file = os.path.join('CSV', '2026_season', 'pbp', f'{game_id}_pbp.json')
    file_exists = os.path.exists(pbp_file)
    
    print(f"\n文件存在: {'✅' if file_exists else '❌'}")
    if file_exists:
        import json
        with open(pbp_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"记录数: {len(data)} 条")
        
    # 检查数据库
    storage = PBPDataStorage()
    is_imported = storage.is_game_imported(game_id)
    print(f"数据库已导入: {'✅' if is_imported else '❌'}")
    storage.close()
    
    return file_exists and is_imported

if __name__ == "__main__":
    url = "https://www.basketball-reference.com/boxscores/pbp/202606030SAS.html"
    print("=" * 60)
    print(f"检查 URL: {url}")
    print("=" * 60)
    
    check_game(url)
