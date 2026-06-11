import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()

with db.get_cursor() as cur:
    # 检查2026年总决赛是否已映射
    cur.execute("""
        SELECT * FROM game_id_mapping 
        WHERE crawled_id LIKE '202606%'
        ORDER BY crawled_id
    """)
    finals = cur.fetchall()
    print(f"2026年总决赛映射: {len(finals)}场")
    for f in finals:
        print(f"  {f[1]} ↔ {f[2]}")
    
    # 统计各赛季映射数量
    cur.execute("""
        SELECT season, COUNT(*) FROM game_id_mapping 
        GROUP BY season ORDER BY season
    """)
    stats = cur.fetchall()
    print(f"\n各赛季映射统计:")
    for s in stats:
        print(f"  Season {s[0]}: {s[1]}场")
