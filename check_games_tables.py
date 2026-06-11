import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()

with db.get_cursor() as cur:
    # 检查games表结构
    cur.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'games'
        ORDER BY ordinal_position
    """)
    cols = [r[0] for r in cur.fetchall()]
    print(f"games表字段: {cols}")
    
    # 查看样例数据
    cur.execute("SELECT * FROM games LIMIT 3")
    samples = cur.fetchall()
    print(f"\n样例数据:")
    for s in samples:
        print(f"  {s}")
    
    # 检查games_partitioned表结构
    cur.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'games_partitioned'
        ORDER BY ordinal_position
    """)
    cols2 = [r[0] for r in cur.fetchall()]
    print(f"\ngames_partitioned表字段: {cols2}")
