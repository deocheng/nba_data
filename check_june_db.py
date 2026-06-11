import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()
with db.get_cursor() as cur:
    cur.execute("""
        SELECT game_id, game_date, visitor_team, home_team
        FROM game_metadata
        WHERE game_date >= '2026-06-01'
        ORDER BY game_date
    """)
    games = cur.fetchall()

print(f'数据库中六月份比赛数: {len(games)}')
for g in games:
    print(f"  {g[1]}: {g[2]} @ {g[3]} ({g[0]})")
