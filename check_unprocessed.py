#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查未处理的游戏
"""

import pandas as pd
from data_importer.pbp_storage import get_pbp_storage

def main():
    storage = get_pbp_storage(season_end=2026)
    games_df = pd.read_csv('CSV/2026_season/all_games_2026.csv', encoding='utf-8-sig')
    
    summary = storage.get_import_summary()
    print(f"已处理状态: {summary}")
    
    unprocessed = []
    for _, row in games_df.iterrows():
        game_id = row['boxscore_url'].split('/')[-1].replace('.html', '')
        if not storage.is_game_processed(game_id):
            unprocessed.append((game_id, row['visitor_team'], row['home_team']))
    
    print(f"\n未处理游戏数: {len(unprocessed)}")
    
    if unprocessed:
        print("\n前20个未处理游戏:")
        for i, (game_id, v, h) in enumerate(unprocessed[:20]):
            print(f"{i+1}. {v} @ {h} ({game_id})")
        
        # 检查20251022日期的游戏
        print("\n\n20251022日期的游戏:")
        games_on_20251022 = []
        for _, row in games_df.iterrows():
            game_id = row['boxscore_url'].split('/')[-1].replace('.html', '')
            if game_id.startswith('20251022'):
                games_on_20251022.append((game_id, row['visitor_team'], row['home_team'], storage.is_game_processed(game_id)))
        
        print(f"找到 {len(games_on_20251022)} 场游戏:")
        for game_id, v, h, processed in games_on_20251022:
            status = "✓ 已处理" if processed else "✗ 未处理"
            print(f"{status} - {v} @ {h} ({game_id})")
    
    storage.close()

if __name__ == '__main__':
    main()
