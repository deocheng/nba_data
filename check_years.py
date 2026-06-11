import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()
with db.get_cursor() as cur:
    # 按年份统计有PBP记录的比赛
    cur.execute("""
        SELECT 
            EXTRACT(YEAR FROM gm.game_date) as year,
            COUNT(DISTINCT gm.game_id) as game_count,
            COUNT(pbp.id) as pbp_count
        FROM game_metadata gm
        INNER JOIN play_by_play pbp ON gm.game_id = pbp.game_id
        WHERE gm.game_date IS NOT NULL
        GROUP BY EXTRACT(YEAR FROM gm.game_date)
        ORDER BY year
    """)
    yearly_stats = cur.fetchall()

    # 统计总数据
    cur.execute("SELECT COUNT(DISTINCT gm.game_id) FROM game_metadata gm INNER JOIN play_by_play pbp ON gm.game_id = pbp.game_id")
    total_games = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM play_by_play")
    total_pbp = cur.fetchone()[0]

print("=" * 60)
print("数据库年份统计 (有PBP记录的比赛)")
print("=" * 60)
for stat in yearly_stats:
    print(f"  {int(stat[0])}年: {stat[1]}场比赛, {stat[2]}条PBP记录")

print()
print(f"总计: {total_games}场比赛, {total_pbp}条PBP记录")
print("=" * 60)

# 检查是否有缺失年份
years = [int(s[0]) for s in yearly_stats]
if years:
    first_year = min(years)
    last_year = max(years)
    all_years = set(range(first_year, last_year + 1))
    missing = all_years - set(years)
    if missing:
        print(f"缺失年份: {sorted(missing)}")
    else:
        print(f"年份覆盖: {first_year} - {last_year} (完整)")
