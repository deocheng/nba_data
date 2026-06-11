import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()

# 检查数据库中的表
with db.get_cursor() as cur:
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = cur.fetchall()
    print("数据库中的表:")
    for t in tables:
        print(f"  - {t[0]}")

# 检查是否有player_seasons等统计表
with db.get_cursor() as cur:
    cur.execute("""
        SELECT COUNT(*) FROM player_stats LIMIT 1
    """)
    try:
        count = cur.fetchone()[0]
        print(f"\nplayer_stats表: {count}条记录")
    except:
        print("\nplayer_stats表不存在")
        
    cur.execute("""
        SELECT COUNT(*) FROM team_stats LIMIT 1
    """)
    try:
        count = cur.fetchone()[0]
        print(f"team_stats表: {count}条记录")
    except:
        print("team_stats表不存在")
