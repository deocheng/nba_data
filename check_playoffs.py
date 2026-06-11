#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查季后赛数据"""
import pandas as pd
from data_importer.pbp_storage import get_pbp_storage

storage = get_pbp_storage(season_end=2026)
summary = storage.get_import_summary()
print('当前数据库状态:', summary)

# 检查游戏列表
games_df = pd.read_csv('CSV/2026_season/all_games_2026.csv', encoding='utf-8-sig')
print(f'\n总游戏数: {len(games_df)}')

# 从boxscore_url提取日期
games_df['game_date'] = games_df['boxscore_url'].str.extract(r'/(\d{8})')[0]
games_df['game_date'] = pd.to_datetime(games_df['game_date'], format='%Y%m%d')

min_date = games_df['game_date'].min()
max_date = games_df['game_date'].max()
print(f'日期范围: {min_date} 到 {max_date}')

# 检查各月份的比赛数
games_df['game_month'] = games_df['game_date'].dt.month
month_counts = games_df['game_month'].value_counts().sort_index()
print('\n各月份比赛数:')
for month, count in month_counts.items():
    print(f'  {month}月: {count}场')

# 检查季后赛（4月及之后）
playoff_games = games_df[games_df['game_date'] >= '2026-04-01']
print(f'\n季后赛比赛数（4月及之后）: {len(playoff_games)}')

if len(playoff_games) > 0:
    print('\n季后赛比赛示例:')
    print(playoff_games[['game_date', 'visitor_team', 'home_team', 'boxscore_url']].head(20))
    
    # 检查已处理的季后赛比赛
    processed_playoff = 0
    for _, row in playoff_games.iterrows():
        game_id = row['boxscore_url'].split('/')[-1].replace('.html', '')
        if storage.is_game_processed(game_id):
            processed_playoff += 1
    
    print(f'\n已处理季后赛比赛: {processed_playoff}/{len(playoff_games)}')

storage.close()