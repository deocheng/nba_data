import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()

with db.get_cursor() as cur:
    # 检查不同年份的gameid样例
    cur.execute("""
        SELECT DISTINCT gameid, season 
        FROM pbp_1997 
        WHERE season IN (1997, 2000, 2010, 2020, 2024)
        ORDER BY season
        LIMIT 20
    """)
    samples = cur.fetchall()

print("pbp_1997 gameid样例:")
for g in samples:
    print(f"  {g[0]} (season: {g[1]})")

print("\ngameid格式分析:")
print("29600001 → 可能是: 年份=29, 月=60, 日=01 (不合理)")
print("29600001 → 更可能是: 比赛编号/序列号")
print("\n请告诉我正确的解析方式，我来修正理解")
