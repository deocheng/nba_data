import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()
with db.get_cursor() as cur:
    # 找出没有PBP数据的比赛（失败的比赛）
    cur.execute("""
        SELECT gm.game_id, gm.game_date, gm.visitor_team, gm.home_team
        FROM game_metadata gm
        LEFT JOIN play_by_play pbp ON gm.game_id = pbp.game_id
        WHERE pbp.id IS NULL
          AND gm.game_date >= '2026-04-01'
        ORDER BY gm.game_date
    """)
    failed_games = cur.fetchall()

print(f"失败的比赛数: {len(failed_games)}")
print("=" * 70)
for i, g in enumerate(failed_games):
    print(f"{i+1}. {g[1]}: {g[2]} @ {g[3]} ({g[0]})")
