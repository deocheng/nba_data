import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()

with db.get_cursor() as cur:
    # 检查play_by_play中的2026年6月比赛
    cur.execute("""
        SELECT DISTINCT game_id FROM play_by_play 
        WHERE game_id LIKE '202606%'
        ORDER BY game_id
    """)
    june_games = [r[0] for r in cur.fetchall()]
    print(f"play_by_play中6月份比赛: {len(june_games)}场")
    for g in june_games:
        print(f"  {g}")
    
    # 检查这些是否已在映射表中
    cur.execute("""
        SELECT crawled_id FROM game_id_mapping 
        WHERE crawled_id LIKE '202606%'
    """)
    mapped = [r[0] for r in cur.fetchall()]
    print(f"\n已在映射表中的6月份比赛: {len(mapped)}场")
    
    # 找出缺失的
    missing = [g for g in june_games if g not in mapped]
    print(f"需要添加的: {len(missing)}场")
    for m in missing:
        print(f"  {m}")
