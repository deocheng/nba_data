#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('nba_data.db')
cursor = conn.cursor()

# 检查2025-26赛季数据
cursor.execute('SELECT COUNT(*) FROM team_games WHERE season LIKE "2025%"')
count = cursor.fetchone()[0]
print(f'2025-26赛季比赛数: {count}')

cursor.execute('SELECT MIN(date), MAX(date) FROM team_games WHERE season LIKE "2025%"')
dates = cursor.fetchone()
print(f'日期范围: {dates[0]} 到 {dates[1]}')

cursor.execute('SELECT COUNT(DISTINCT team_abbr) FROM team_games WHERE season LIKE "2025%"')
teams = cursor.fetchone()[0]
print(f'涉及球队数: {teams}')

# 获取一些样例数据
cursor.execute('SELECT * FROM team_games WHERE season LIKE "2025%" LIMIT 5')
print('\n样例数据:')
for row in cursor.fetchall():
    print(f'{row[3]} - {row[4]}: {row[1]} {row[7]} - {row[8]} {row[5]}')

conn.close()
