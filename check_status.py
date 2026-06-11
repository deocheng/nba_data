#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()
with db.get_cursor() as cur:
    # 统计2026年4月后的比赛数
    cur.execute("SELECT COUNT(*) FROM game_metadata WHERE game_date >= '2026-04-01'")
    playoff_count = cur.fetchone()[0]

    # 总比赛数
    cur.execute('SELECT COUNT(*) FROM game_metadata')
    total_count = cur.fetchone()[0]

    # PBP记录数
    cur.execute('SELECT COUNT(*) FROM play_by_play')
    pbp_count = cur.fetchone()[0]

    # 显示最近10场比赛
    cur.execute("""
        SELECT game_id, game_date, visitor_team, home_team
        FROM game_metadata
        WHERE game_date >= '2026-04-01'
        ORDER BY game_date DESC
        LIMIT 10
    """)
    recent = cur.fetchall()

print(f'季后赛比赛数: {playoff_count}')
print(f'总比赛数: {total_count}')
print(f'PBP记录数: {pbp_count}')
print(f'\n最近10场季后赛:')
for g in recent:
    print(f'  {g[1]} - {g[2]} @ {g[3]} ({g[0]})')
