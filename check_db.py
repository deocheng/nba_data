#!/usr/bin/env python3
import psycopg2

conn = psycopg2.connect('dbname=nba user=postgres password=postgres')
cur = conn.cursor()

cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
tables = cur.fetchall()

print('现有数据库表:')
for table in tables:
    print(f'  - {table[0]}')

conn.close()