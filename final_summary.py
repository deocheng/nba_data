#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终总结
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
    print('🏆 Excel 数据导入总结')
    print('=' * 80)
    
    # 统计
    count_sql = "SELECT COUNT(*) FROM game_metadata WHERE game_id LIKE '2026%'"
    game_count = db_manager.fetch_one(count_sql)[0]
    
    player_count_sql = "SELECT COUNT(DISTINCT player_id) FROM player_game_stats"
    player_count = db_manager.fetch_one(player_count_sql)[0]
    
    stats_count_sql = "SELECT COUNT(*) FROM player_game_stats"
    stats_count = db_manager.fetch_one(stats_count_sql)[0]
    
    print(f'\n✅ 成功导入:')
    print(f'   - 比赛: {game_count} 场')
    print(f'   - 球员统计: {stats_count} 条')
    print(f'   - 涉及球员: {player_count} 人')
    
    # 展示数据导入完成！')
    db_manager.close()

if __name__ == '__main__':
    main()
