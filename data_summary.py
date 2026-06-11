#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数据库中的数据总结"""
import psycopg2
from datetime import datetime

def main():
    conn = psycopg2.connect(
        dbname='nba',
        user='postgres',
        password='postgres',
        host='localhost',
        port='5433'
    )
    cursor = conn.cursor()

    print("=" * 80)
    print("NBA 数据库数据总结")
    print("=" * 80)

    # Play by Play 表
    print("\n1. Play by Play 数据")
    print("-" * 80)
    cursor.execute('SELECT COUNT(*) FROM play_by_play')
    count = cursor.fetchone()[0]
    print(f"  总记录数: {count}")
    
    if count > 0:
        cursor.execute('SELECT COUNT(DISTINCT game_id) FROM play_by_play')
        game_count = cursor.fetchone()[0]
        print(f"  比赛数: {game_count}")
        
        cursor.execute('SELECT MIN(created_at), MAX(created_at) FROM play_by_play')
        min_date, max_date = cursor.fetchone()
        print(f"  时间范围: {min_date} 到 {max_date}")
        
        print("\n  示例数据 (5条):")
        cursor.execute('SELECT * FROM play_by_play WHERE description != \'\' LIMIT 5')
        columns = [desc[0] for desc in cursor.description]
        for row in cursor.fetchall():
            print(f"    {row}")

    # Player Game Logs 表
    print("\n\n2. Player Game Logs 数据")
    print("-" * 80)
    cursor.execute('SELECT COUNT(*) FROM player_game_logs')
    count = cursor.fetchone()[0]
    print(f"  总记录数: {count}")
    
    if count > 0:
        cursor.execute('SELECT COUNT(DISTINCT player_id) FROM player_game_logs')
        player_count = cursor.fetchone()[0]
        print(f"  球员数: {player_count}")
        
        cursor.execute('SELECT COUNT(DISTINCT team_id) FROM player_game_logs')
        team_count = cursor.fetchone()[0]
        print(f"  球队数: {team_count}")
        
        cursor.execute('SELECT MIN(game_date), MAX(game_date) FROM player_game_logs')
        min_date, max_date = cursor.fetchone()
        print(f"  时间范围: {min_date} 到 {max_date}")
        
        print("\n  示例数据 (5条):")
        cursor.execute('SELECT game_date, player_id, team_id, points, rebounds, assists FROM player_game_logs LIMIT 5')
        for row in cursor.fetchall():
            print(f"    {row}")
        
        print("\n  数据项:")
        cursor.execute('SELECT column_name FROM information_schema.columns WHERE table_name = \'player_game_logs\' ORDER BY ordinal_position')
        columns = [col[0] for col in cursor.fetchall()]
        print(f"    {columns}")

    conn.close()
    
    print("\n" + "=" * 80)
    print("总结完毕！")
    print("=" * 80)

if __name__ == '__main__':
    main()
