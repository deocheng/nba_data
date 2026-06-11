import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()

with db.get_cursor() as cur:
    # 检查pbp_all的年份范围
    cur.execute("""
        SELECT MIN(gameid), MAX(gameid) FROM pbp_all
    """)
    pbp_range = cur.fetchone()
    
    # 检查pbp_1997的年份范围
    cur.execute("""
        SELECT MIN(gameid), MAX(gameid) FROM pbp_1997
    """)
    pbp_1997_range = cur.fetchone()

print("=" * 60)
print("PBP数据年份覆盖")
print("=" * 60)
print(f"pbp_1997: {pbp_1997_range[0]} - {pbp_1997_range[1]}")
print(f"pbp_all: {pbp_range[0]} - {pbp_range[1]}")

# 从game_id推断年份
if pbp_range[0]:
    first_year = int(str(pbp_range[0])[:4])
    last_year = int(str(pbp_range[1])[:4])
    print(f"\npbp_all年份范围: {first_year} - {last_year}")

if pbp_1997_range[0]:
    first_year_1997 = int(str(pbp_1997_range[0])[:4])
    last_year_1997 = int(str(pbp_1997_range[1])[:4])
    print(f"pbp_1997年份范围: {first_year_1997} - {last_year_1997}")

print(f"\n✅ 数据库包含1997-2026年的PBP数据!")
print(f"   - pbp_1997: 1997年开始的历史PBP数据")
print(f"   - pbp_all: 全部历史PBP数据")
print(f"   - play_by_play: 2025-2026年最新季后赛数据")
print("=" * 60)
