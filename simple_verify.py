#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单验证导入数据
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_importer.database import DatabaseManager
from data_importer.config import DatabaseConfig

def main():
    db_config = DatabaseConfig()
    db_manager = DatabaseManager(db_config)
    
    print('=' * 80)
    print('简单验证导入数据')
    print('=' * 80)
    
    # 查看 games 表
    print('\n1. 查看 games 表中的新比赛:')
    check_games_sql = "SELECT game_id, game_date, home_team_id, away_team_id, home_score, away_score FROM games WHERE game_date >= '2026-06-01'"
    games = db_manager.fetch_all(check_games_sql)
    if games:
        for game in games:
            print(f'   Game ID: {game[0]} - Date: {game[1]} - Score: {game[4]} - {game[5]}')
    else:
        print('   No new games found')
        
    # 查看 player_game_stats 表的结构和数据量
    print('\n2. 查看 player_game_stats 表的数据:')
    count_sql = "SELECT COUNT(*) FROM player_game_stats"
    count = db_manager.fetch_one(count_sql)[0]
    print(f'   Total rows: {count}')
    
    # 查看一些 sample 数据
    sample_sql = """
    SELECT p.name, pgs.pts, pgs.trb, pgs.ast, pgs.minutes
    FROM player_game_stats pgs
    JOIN players p ON pgs.player_id = p.player_id
    LIMIT 10
    """
    samples = db_manager.fetch_all(sample_sql)
    for sample in samples:
        print(f'   {sample[0]}: {sample[1]} pts, {sample[2]} reb, {sample[3]} ast, {sample[4]} m')
        
    # 查看 game_metadata 表
    print('\n3. 查看 game_metadata 表:')
    meta_sql = "SELECT game_id, visitor_team, home_team, visitor_score, home_score FROM game_metadata WHERE game_id LIKE '2026%'"
    metas = db_manager.fetch_all(meta_sql)
    for meta in metas:
        print(f'   {meta[0]}: {meta[1]} {meta[3]} - {meta[4]} {meta[2]}')
    
    print('\n✅ 验证完成！')
    db_manager.close()

if __name__ == '__main__':
    main()
