import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()
with db.get_cursor() as cur:
    # 检查所有六月份的比赛
    cur.execute("""
        SELECT gm.game_id, gm.game_date, gm.visitor_team, gm.home_team, COUNT(pbp.id) as pbp_count
        FROM game_metadata gm
        LEFT JOIN play_by_play pbp ON gm.game_id = pbp.game_id
        WHERE gm.game_date >= '2026-06-01'
        GROUP BY gm.game_id, gm.game_date, gm.visitor_team, gm.home_team
        ORDER BY gm.game_date
    """)
    june_games = cur.fetchall()

print("=" * 60)
print("总决赛G3数据状态")
print("=" * 60)
for g in june_games:
    print(f"  {g[1]}: {g[2]} @ {g[3]}")
    print(f"    Game ID: {g[0]}")
    print(f"    PBP记录: {g[4]}条")
    print()
