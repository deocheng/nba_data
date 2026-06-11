#!/usr/bin/env python3
"""分析爬取数据和导入数据中的季后赛情况"""
import psycopg2

conn = psycopg2.connect(dbname='nba', user='postgres', password='postgres', host='localhost', port='5433')
cursor = conn.cursor()

print("=" * 60)
print("🏀 爬取数据 (play_by_play表) 分析")
print("=" * 60)

# 爬取数据统计
cursor.execute("SELECT COUNT(DISTINCT game_id) FROM play_by_play;")
pbp_games = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM play_by_play;")
pbp_events = cursor.fetchone()[0]

print("爬取比赛场数:", pbp_games)
print("爬取事件总数:", pbp_events)

# 爬取数据的game_id格式分析（Basketball Reference格式）
cursor.execute("SELECT game_id FROM play_by_play LIMIT 5;")
sample_ids = [row[0] for row in cursor.fetchall()]
print("\n爬取数据Game ID示例:", sample_ids)

print("\n" + "=" * 60)
print("📥 导入数据 (pbp_all表) 分析")
print("=" * 60)

# 导入数据统计
cursor.execute("""
    SELECT season, COUNT(DISTINCT gameid) as games
    FROM pbp_all
    GROUP BY season
    ORDER BY season DESC;
""")
print("各赛季比赛场数:")
for row in cursor.fetchall():
    print("  赛季{}: {}场".format(row[0], row[1]))

# 分析2025赛季额外的90场
print("\n🔍 2025赛季详细分析:")
cursor.execute("""
    SELECT gameid, COUNT(*) as events
    FROM pbp_all
    WHERE season = 2025
    GROUP BY gameid
    ORDER BY events DESC
    LIMIT 10;
""")
print("比赛事件数TOP10（可能是加时赛多的比赛）:")
for row in cursor.fetchall():
    print("  {}: {}事件".format(row[0], row[1]))

# 通过game_id判断是否包含季后赛
# 爬取数据的game_id格式是: 202510210LAL (2025年10月21日湖人主场)
# 日期分析：常规赛通常10月-4月，季后赛4月-6月
cursor.execute("""
    SELECT 
        CASE 
            WHEN SUBSTR(game_id, 5, 2) IN ('04', '05', '06') THEN '季后赛(4-6月)'
            WHEN SUBSTR(game_id, 5, 2) IN ('10', '11', '12', '01', '02', '03') THEN '常规赛(10-3月)'
            ELSE '其他'
        END as game_type,
        COUNT(DISTINCT game_id) as games
    FROM play_by_play
    GROUP BY game_type;
""")
print("\n📅 爬取数据按月份分类:")
for row in cursor.fetchall():
    print("  {}: {}场".format(row[0], row[1]))

conn.close()
