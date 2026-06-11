#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查数据库中的gamelog数据"""
import psycopg2

def main():
    conn = psycopg2.connect(
        dbname='nba',
        user='postgres',
        password='postgres',
        host='localhost',
        port='5433'
    )
    cursor = conn.cursor()

    # 检查 player_game_logs 表
    print('=== player_game_logs 表 ===')
    try:
        cursor.execute('SELECT COUNT(*) FROM player_game_logs')
        count = cursor.fetchone()[0]
        print(f'  记录数: {count}')
        
        if count > 0:
            cursor.execute('SELECT * FROM player_game_logs LIMIT 3')
            columns = [desc[0] for desc in cursor.description]
            print(f'  列: {columns}')
            print(f'  前3条记录:')
            for row in cursor.fetchall():
                print(f'    {row}')
    except Exception as e:
        print(f'  错误: {e}')
    
    # 检查 okc_gamelog 表（看起来是球队的gamelog表
    print('\n=== okc_gamelog 表 ===')
    try:
        cursor.execute('SELECT COUNT(*) FROM okc_gamelog')
        count = cursor.fetchone()[0]
        print(f'  记录数: {count}')
        
        if count > 0:
            cursor.execute('SELECT * FROM okc_gamelog LIMIT 3')
            columns = [desc[0] for desc in cursor.description]
            print(f'  列: {columns}')
            print(f'  前3条记录:')
            for row in cursor.fetchall():
                print(f'    {row}')
    except Exception as e:
        print(f'  错误: {e}')
    
    # 检查其他球队的 gamelog 表
    print('\n=== 其他球队gamelog表 ===')
    team_abbrs = ['SAS', 'LAL', 'GSW', 'BOS', 'MIA']
    for abbr in team_abbrs:
        table_name = f'{abbr.lower()}_gamelog'
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            count = cursor.fetchone()[0]
            print(f'  {table_name}: {count}条')
        except Exception:
            pass  # 表不存在就跳过

    conn.close()

if __name__ == '__main__':
    main()
