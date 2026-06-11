import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager
import json

db = DatabaseManager()
with db.get_cursor() as cur:
    # 获取一条PBP记录看看结构
    cur.execute("""
        SELECT game_id, game_clock, visitor_score, home_score, visitor_action, home_action, score_change
        FROM play_by_play
        WHERE game_clock IS NOT NULL
        LIMIT 5
    """)
    records = cur.fetchall()

print("play_by_play 数据样例:")
for r in records:
    print(f"  game_id: {r[0]}")
    print(f"  game_clock: {r[1]}")
    print(f"  visitor_score: {r[2]}")
    print(f"  home_score: {r[3]}")
    print(f"  visitor_action: {r[4]}")
    print(f"  home_action: {r[5]}")
    print(f"  score_change: {r[6]}")
    print()
