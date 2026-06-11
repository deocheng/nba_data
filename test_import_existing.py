#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试导入已有的 PBP 数据
"""

import sys
import os
import json
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_importer.pbp_storage import PBPDataStorage

print("=" * 60)
print("导入已有的 PBP 数据")
print("=" * 60)

# 加载游戏列表
season_end = 2026
games_df = pd.read_csv(os.path.join('CSV', f'{season_end}_season', f'all_games_{season_end}.csv'), encoding='utf-8-sig')
print(f"✓ 加载了 {len(games_df)} 场游戏")

# 初始化存储
storage = PBPDataStorage(season_end=season_end)

# 查找 PBP 目录
pbp_dir = os.path.join('CSV', f'{season_end}_season', 'pbp')
if os.path.exists(pbp_dir):
    pbp_files = [f for f in os.listdir(pbp_dir) if f.endswith('_pbp.json')]
    print(f"\n找到 {len(pbp_files)} 个 PBP 文件")
    
    success = 0
    failed = 0
    
    for pbp_file in pbp_files[:5]:  # 先导入 5 个测试
        try:
            game_id = pbp_file.replace('_pbp.json', '')
            
            # 找到对应的游戏信息
            game_row = games_df[games_df['boxscore_url'].str.contains(game_id)]
            if len(game_row) == 0:
                print(f"⚠ 找不到游戏信息: {game_id}")
                continue
            
            game_info = game_row.iloc[0].to_dict()
            
            # 加载 PBP 数据
            with open(os.path.join(pbp_dir, pbp_file), 'r', encoding='utf-8') as f:
                pbp_data = json.load(f)
            
            print(f"\n处理: {game_info['visitor_team']} @ {game_info['home_team']} ({game_id})")
            
            # 处理
            result = storage.process_single_game(game_info, pbp_data)
            
            if result['success']:
                print(f"✓ 成功! 文件: {result['file_saved']}, DB: {result['db_imported']} ({result['records_imported']} 条)")
                success += 1
            else:
                print(f"✗ 失败: {result.get('errors')}")
                failed += 1
        
        except Exception as e:
            print(f"✗ 处理失败 {pbp_file}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"完成: 成功 {success}, 失败 {failed}")

summary = storage.get_import_summary()
print(f"\n摘要: {summary}")
storage.close()
print("\n完成!")
