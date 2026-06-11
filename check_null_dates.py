import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()
with db.get_cursor() as cur:
    # 检查有PBP但game_date为NULL的比赛
    cur.execute("""
        SELECT COUNT(DISTINCT gm.game_id), COUNT(pbp.id)
        FROM game_metadata gm
        INNER JOIN play_by_play pbp ON gm.game_id = pbp.game_id
        WHERE gm.game_date IS NULL
    """)
    result = cur.fetchone()
    print(f"game_date为NULL的比赛: {result[0]}场, PBP记录: {result[1]}条")
    
    # 查看这些比赛的game_id样例
    cur.execute("""
        SELECT DISTINCT gm.game_id
        FROM game_metadata gm
        INNER JOIN play_by_play pbp ON gm.game_id = pbp.game_id
        WHERE gm.game_date IS NULL
        LIMIT 10
    """)
    samples = cur.fetchall()
    print(f"\ngame_id样例:")
    for s in samples:
        print(f"  {s[0]}")
    
    # 尝试从game_id提取年份
    print(f"\n从game_id推断的年份分布:")
    cur.execute("""
        SELECT 
            CASE 
                WHEN gm.game_id ~ '^[0-9]{4}' THEN SUBSTRING(gm.game_id FROM 1 FOR 4)
                ELSE 'unknown'
            END as year_prefix,
            COUNT(DISTINCT gm.game_id) as cnt
        FROM game_metadata gm
        INNER JOIN play_by_play pbp ON gm.game_id = pbp.game_id
        WHERE gm.game_date IS NULL
        GROUP BY year_prefix
        ORDER BY year_prefix
    """)
    results = cur.fetchall()
    for r in results:
        print(f"  {r[0]}: {r[1]}场比赛")
