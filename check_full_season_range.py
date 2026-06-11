#!/usr/bin/env python3
"""检查数据库中的完整赛季范围"""
import psycopg2

conn = psycopg2.connect(dbname='nba', user='postgres', password='postgres', host='localhost', port='5433')
cursor = conn.cursor()

print("=" * 70)
print("🏀 数据库完整赛季统计")
print("=" * 70)

# 检查pbp_all表的赛季范围
cursor.execute("""
    SELECT
        MIN(season) as min_season,
        MAX(season) as max_season,
        COUNT(DISTINCT season) as num_seasons,
        COUNT(DISTINCT gameid) as total_games,
        COUNT(*) as total_events
    FROM pbp_all;
""")
result = cursor.fetchone()
print(f"\n📊 pbp_all表:")
print(f"  赛季范围: {result[0]} - {result[1]} ({result[2]}个赛季)")
print(f"  总比赛数: {result[3]:,}场")
print(f"  总事件数: {result[4]:,}")

# 检查player_per_game表的赛季范围
cursor.execute("""
    SELECT
        MIN(season) as min_season,
        MAX(season) as max_season,
        COUNT(*) as total_records
    FROM player_per_game
    WHERE season IS NOT NULL;
""")
result = cursor.fetchone()
print(f"\n📊 player_per_game表:")
print(f"  赛季范围: {result[0]} - {result[1]}")
print(f"  记录数: {result[2]:,}")

# 检查team_stats_per_game表的赛季范围
cursor.execute("""
    SELECT
        MIN(season) as min_season,
        MAX(season) as max_season,
        COUNT(*) as total_records
    FROM team_stats_per_game
    WHERE season IS NOT NULL;
""")
result = cursor.fetchone()
print(f"\n📊 team_stats_per_game表:")
print(f"  赛季范围: {result[0]} - {result[1]}")
print(f"  记录数: {result[2]:,}")

# 检查player_totals表的赛季范围
cursor.execute("""
    SELECT
        MIN(season_id) as min_season,
        MAX(season_id) as max_season,
        COUNT(*) as total_records
    FROM player_totals
    WHERE season_id IS NOT NULL;
""")
result = cursor.fetchone()
print(f"\n📊 player_totals表:")
print(f"  赛季范围: {result[0]} - {result[1]}")
print(f"  记录数: {result[2]:,}")

# 列出所有包含赛季数据的表
print("\n" + "=" * 70)
print("📁 所有包含赛季数据的表")
print("=" * 70)

tables = ['player_per_game', 'team_stats_per_game', 'player_totals',
          'player_advanced', 'player_shooting', 'opponent_stats_per_game']

for table in tables:
    try:
        cursor.execute(f"""
            SELECT MIN(season), MAX(season), COUNT(*)
            FROM {table}
            WHERE season IS NOT NULL;
        """)
        result = cursor.fetchone()
        if result:
            print(f"  {table:<30} {result[0]} - {result[1]} ({result[2]:,}条)")
    except:
        try:
            cursor.execute(f"""
                SELECT MIN(season_id), MAX(season_id), COUNT(*)
                FROM {table}
                WHERE season_id IS NOT NULL;
            """)
            result = cursor.fetchone()
            if result:
                print(f"  {table:<30} {result[0]} - {result[1]} ({result[2]:,}条)")
        except:
            print(f"  {table:<30} 无法查询")

conn.close()
