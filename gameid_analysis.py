import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()

with db.get_cursor() as cur:
    # 检查每个赛季的gameid范围
    cur.execute("""
        SELECT 
            season,
            MIN(gameid) as min_id,
            MAX(gameid) as max_id,
            COUNT(DISTINCT gameid) as unique_games
        FROM pbp_1997 
        GROUP BY season
        ORDER BY season
    """)
    stats = cur.fetchall()

print("pbp_1997 gameid按赛季统计:")
print("=" * 70)
for s in stats:
    print(f"Season {s[0]}: {s[1]} - {s[2]} ({s[3]}场)")

print("\n规律分析:")
print("gameid格式: XXYYZZZZ")
print("  XXYY = 赛季标识 (2960 = 1996-97赛季)")
print("  ZZZZ = 赛季内比赛序号")
