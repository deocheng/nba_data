import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()
with db.get_cursor() as cur:
    # 检查G3数据
    cur.execute("""
        SELECT gm.game_id, gm.game_date, gm.visitor_team, gm.home_team, COUNT(pbp.id)
        FROM game_metadata gm
        LEFT JOIN play_by_play pbp ON gm.game_id = pbp.game_id
        WHERE gm.game_id LIKE '202606%'
        GROUP BY gm.game_id, gm.game_date, gm.visitor_team, gm.home_team
        ORDER BY gm.game_date
    """)
    june_games = cur.fetchall()

print("六月份总决赛数据:")
for g in june_games:
    print(f"  {g[1]}: {g[2]} @ {g[3]} - {g[4]}条PBP记录 ({g[0]})")
