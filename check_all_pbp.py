import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()

with db.get_cursor() as cur:
    # 检查pbp_all的gameid分布
    cur.execute("""
        SELECT 
            MIN(gameid) as min_id,
            MAX(gameid) as max_id,
            COUNT(DISTINCT gameid) as unique_games
        FROM pbp_all
    """)
    stats = cur.fetchone()
    print(f"pbp_all: {stats[2]:,}场 ({stats[0]} - {stats[1]})")

    # 检查pbp_1997
    cur.execute("""
        SELECT 
            MIN(gameid) as min_id,
            MAX(gameid) as max_id,
            COUNT(DISTINCT gameid) as unique_games
        FROM pbp_1997
    """)
    stats = cur.fetchone()
    print(f"pbp_1997: {stats[2]:,}场 ({stats[0]} - {stats[1]})")
