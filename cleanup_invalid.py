#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理无效的球员记录
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_importer.database import DatabaseManager
from data_importer.config import DatabaseConfig

def main():
    db_config = DatabaseConfig()
    db_manager = DatabaseManager(db_config)
    
    # 删除无效的球员
    invalid_names = [
        "Share & Export",
        "Modify, Export & Share Table",
        "Get as Excel Workbook",
        "Get table as CSV (for Excel)",
        "Get Link to Table",
        "About Sharing Tools",
        "Video: SR Sharing Tools & How-to",
        "Video: Stats Table Tips & Tricks",
        "Data Usage Terms",
    ]
    
    print('=' * 80)
    print('清理无效的球员记录')
    print('=' * 80)
    
    for name in invalid_names:
        delete_sql = "DELETE FROM player_game_stats WHERE player_id IN (SELECT player_id FROM players WHERE name = %s)"
        db_manager.execute(delete_sql, (name,))
        
        delete_player_sql = "DELETE FROM players WHERE name = %s"
        db_manager.execute(delete_player_sql, (name,))
        
        print(f'✅ 删除了无效球员: {name}')
    
    print('\n✅ 清理完成！')
    
    # 验证
    print('\n' + '=' * 80)
    print('验证剩余数据')
    print('=' * 80)
    
    # 查看有效球员
    players_sql = """
    SELECT p.player_id, p.name, count(pgs.id) as game_count
    FROM players p
    LEFT JOIN player_game_stats pgs ON p.player_id = pgs.player_id
    GROUP BY p.player_id, p.name
    ORDER BY p.name
    """
    
    players = db_manager.fetch_all(players_sql)
    print(f'\n有效球员: {len(players)} 个')
    for p in players:
        print(f'  {p[0]}: {p[1]} ({p[2]} 场)')
    
    db_manager.close()

if __name__ == '__main__':
    main()
