#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 teams 和 players 数据
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
    print('Teams 数据')
    print('=' * 80)
    teams = db_manager.fetch_all("SELECT team_id, name, abbreviation FROM teams")
    for team in teams:
        print(f'{team[0]}: {team[1]} ({team[2]})')
    
    print('\n' + '=' * 80)
    print('Players 数据')
    print('=' * 80)
    players = db_manager.fetch_all("SELECT player_id, name FROM players LIMIT 20")
    for player in players:
        print(f'{player[0]}: {player[1]}')
    
    db_manager.close()

if __name__ == '__main__':
    main()
