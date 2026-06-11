import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()

with db.get_cursor() as cur:
    # 检查game_metadata表
    cur.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_name LIKE 'game%'
    """)
    tables = [r[0] for r in cur.fetchall()]
    print(f"游戏相关表: {tables}")
    
    if 'game_metadata' in tables:
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'game_metadata'
            ORDER BY ordinal_position
        """)
        cols = [r[0] for r in cur.fetchall()]
        print(f"\ngame_metadata字段: {cols}")
        
        # 查看样例数据
        cur.execute("SELECT * FROM game_metadata LIMIT 3")
        samples = cur.fetchall()
        print(f"\n样例数据:")
        for s in samples:
            print(f"  {s}")
