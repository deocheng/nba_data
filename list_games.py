#!/usr/bin/env python3
"""查询可用的比赛ID"""
import psycopg2

DB_CONFIG = {
    'dbname': 'nba',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5433'
}

conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()

# 查询最近的比赛
cursor.execute("""
    SELECT DISTINCT gameid, season, 
           MAX(h_pts) as home_score, MAX(a_pts) as visitor_score
    FROM pbp_all
    WHERE season >= 2025
    GROUP BY gameid, season
    ORDER BY season DESC, gameid DESC
    LIMIT 10;
""")

print("📋 可用的比赛ID (2025-2026赛季):")
print("-" * 60)
print(f"{'比赛ID':<12} {'赛季':<6} {'比分'}")
print("-" * 60)

for row in cursor.fetchall():
    gameid, season, home, away = row
    print(f"{gameid:<12} {season:<6} {home}-{away}")

conn.close()
