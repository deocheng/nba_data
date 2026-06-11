#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理刚才错误添加的比赛统计，重新导入
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_importer.database import DatabaseManager
from data_importer.config import DatabaseConfig

def main():
    db_config = DatabaseConfig()
    db_manager = DatabaseManager(db_config)
    
    # 查找刚才导入的比赛
    find_games_sql = "SELECT game_id, visitor_team, home_team, visitor_score, home_score FROM game_metadata WHERE game_id LIKE '202606%'"
    games = db_manager.fetch_all(find_games_sql)
    
    print('=' * 80)
    print('清理并重新导入')
    print('=' * 80)
    
    for game in games:
        game_id, visitor, home, vs, hs = game
        print(f'\n处理比赛: {visitor} {vs} - {hs} {home} ({game_id})')
        
        # 删除球员统计
        delete_sql = """
        DELETE FROM player_game_stats 
        WHERE game_id IN (
            SELECT g.game_id FROM games g 
            JOIN game_metadata gm ON gm.game_date = g.game_date
            WHERE gm.game_id = %s
        )
        """
        db_manager.execute(delete_sql, (game_id,))
        print(f'  ✅ 已删除球员统计')
    
    print('\n✅ 清理完成！现在可以重新运行 import_excel_to_db.py')
    db_manager.close()

if __name__ == '__main__':
    main()
