#!/usr/bin/env python3
"""查询2025和2026赛季数据对比"""
import psycopg2

conn = psycopg2.connect(dbname='nba', user='postgres', password='postgres', host='localhost', port='5433')
cursor = conn.cursor()

# 查询各赛季数据量
cursor.execute("""
    SELECT season, COUNT(DISTINCT gameid) as games, COUNT(*) as events
    FROM pbp_all
    WHERE season IN (2025, 2026)
    GROUP BY season
    ORDER BY season;
""")

print("📊 各赛季数据统计:")
print("-" * 50)
print("{:<8} {:<12} {:<12}".format("赛季", "比赛场数", "事件总数"))
print("-" * 50)
for row in cursor.fetchall():
    season, games, events = row
    print("{:<8} {:<12} {:,}".format(season, games, events))

# 检查2026赛季数据
cursor.execute("""
    SELECT COUNT(DISTINCT gameid) as games
    FROM pbp_all
    WHERE season = 2026 AND team IS NOT NULL;
""")
result = cursor.fetchone()
print("\n🔍 2026赛季有球队信息的比赛:", result[0], "场")

# 检查每个赛季的时间范围
cursor.execute("""
    SELECT season, MIN(clock_seconds), MAX(clock_seconds)
    FROM pbp_all
    WHERE season IN (2025, 2026)
    GROUP BY season;
""")
print("\n⏱️ 比赛时间范围统计:")
for row in cursor.fetchall():
    season, min_sec, max_sec = row
    print("赛季{}: 最短{}秒, 最长{}秒".format(season, min_sec, max_sec))

conn.close()
