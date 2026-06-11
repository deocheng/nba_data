#!/usr/bin/env python3
"""检查数据库中的球员名字格式"""
import psycopg2

conn = psycopg2.connect(dbname='nba', user='postgres', password='postgres', host='localhost', port='5433')
cursor = conn.cursor()

# 查询前20个球员名字
cursor.execute('SELECT DISTINCT player FROM pbp_all WHERE player IS NOT NULL ORDER BY player LIMIT 20;')
players = [row[0] for row in cursor.fetchall()]
print('球员名字示例:')
for p in players:
    print(f'  {p}')

# 查询包含LeBron的球员
cursor.execute("SELECT DISTINCT player FROM pbp_all WHERE player ILIKE '%LeBron%';")
result = cursor.fetchall()
print(f'\n包含LeBron的球员: {result}')

# 查询包含Curry的球员
cursor.execute("SELECT DISTINCT player FROM pbp_all WHERE player ILIKE '%Curry%';")
result = cursor.fetchall()
print(f'包含Curry的球员: {result}')

# 查询包含Durant的球员
cursor.execute("SELECT DISTINCT player FROM pbp_all WHERE player ILIKE '%Durant%';")
result = cursor.fetchall()
print(f'包含Durant的球员: {result}')

conn.close()
