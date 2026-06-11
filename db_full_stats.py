#!/usr/bin/env python3
"""查询数据库完整时间跨度"""
import psycopg2

conn = psycopg2.connect(dbname='nba', user='postgres', password='postgres', host='localhost', port='5433')
cursor = conn.cursor()

print("=" * 70)
print("🏀 NBA PBP 数据库完整统计")
print("=" * 70)

# 总览统计
cursor.execute("""
    SELECT
        COUNT(*) as total_events,
        COUNT(DISTINCT gameid) as total_games,
        MIN(season) as start_season,
        MAX(season) as end_season,
        COUNT(DISTINCT team) as total_teams
    FROM pbp_all;
""")
result = cursor.fetchone()
print("\n📊 总览:")
print(f"  总事件数: {result[0]:,}")
print(f"  总比赛数: {result[1]:,}场")
print(f"  赛季跨度: {result[2]} - {result[3]} ({result[3] - result[2] + 1}个赛季)")
print(f"  涉及球队: {result[2]}支")

# 各赛季统计
cursor.execute("""
    SELECT season,
           COUNT(DISTINCT gameid) as games,
           COUNT(*) as events
    FROM pbp_all
    GROUP BY season
    ORDER BY season;
""")

print("\n📅 各赛季数据统计:")
print("-" * 70)
print("{:<8} {:<10} {:<15} {:<10}".format("赛季", "比赛场数", "事件总数", "备注"))
print("-" * 70)

prev_games = 0
for row in cursor.fetchall():
    season, games, events = row
    # 判断是否为完整赛季
    if games >= 1200:
        note = "完整赛季"
    elif games >= 700:
        note = "停摆赛季"
    elif season == result[2]:
        note = "起始赛季"
    elif season == result[3]:
        note = "当前赛季"
    else:
        note = ""
    
    # 标记季后赛数据
    if games > 1230:
        note = "含季后赛"
    
    print("{:<8} {:<10} {:<15,} {:<10}".format(season, games, events, note))

print("-" * 70)
print(f"📈 总计: {result[1]:,}场比赛, {result[0]:,}个事件")

# 检查最新数据
cursor.execute("""
    SELECT MAX(season), COUNT(DISTINCT gameid)
    FROM pbp_all
    WHERE season = (SELECT MAX(season) FROM pbp_all);
""")
latest = cursor.fetchone()
print(f"\n🆕 最新赛季: {latest[0]}, 比赛数: {latest[1]}场")

# 检查最早数据
cursor.execute("""
    SELECT MIN(season), COUNT(DISTINCT gameid)
    FROM pbp_all
    WHERE season = (SELECT MIN(season) FROM pbp_all);
""")
earliest = cursor.fetchone()
print(f"📅 最早赛季: {earliest[0]}, 比赛数: {earliest[1]}场")

conn.close()
