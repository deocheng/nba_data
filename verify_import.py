#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证 Excel 导入数据
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
    print('验证导入数据')
    print('=' * 80)
    
    # 查看比赛信息
    print('\n📋 比赛信息:')
    games_sql = """
    SELECT game_id, game_date, visitor_team, home_team, visitor_score, home_score 
    FROM game_metadata 
    WHERE game_id LIKE '202606%'
    """
    games = db_manager.fetch_all(games_sql)
    for game in games:
        game_id, date, visitor, home, vs, hs = game
        print(f'  {game_id}: {visitor} {vs} - {hs} {home} ({date})')
        
        # 查看对应的球员统计
        stats_sql = """
        SELECT p.name, t.name as team, pgs.pts, pgs.reb, pgs.ast, pgs.minutes
        FROM player_game_stats pgs
        JOIN players p ON pgs.player_id = p.player_id
        JOIN teams t ON pgs.team_id = t.team_id
        JOIN games g ON pgs.game_id = g.game_id
        JOIN game_metadata gm ON g.game_date = gm.game_date
        WHERE gm.game_id = %s
        ORDER BY pgs.pts DESC NULLS LAST
        """
        stats = db_manager.fetch_all(stats_sql, (game_id,))
        print(f'  📊 球员统计 ({len(stats)} 人):')
        for stat in stats:
            name, team, pts, reb, ast, mins = stat
            pts_str = f'{pts} pts' if pts else ''
            reb_str = f'{reb} reb' if reb else ''
            ast_str = f'{ast} ast' if ast else ''
            mins_str = f'{mins:.1f} m' if mins else ''
            print(f'    - {name}: {team} | {pts_str} {reb_str} {ast_str} {mins_str}')
    
    print('\n✅ 验证完成！')
    db_manager.close()

if __name__ == '__main__':
    main()
