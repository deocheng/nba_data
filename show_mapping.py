import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()

with db.get_cursor() as cur:
    # 查看映射表结构
    cur.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'game_id_mapping'
        ORDER BY ordinal_position
    """)
    cols = [r[0] for r in cur.fetchall()]
    print(f"game_id_mapping 字段: {cols}")
    
    # 查看样例数据
    cur.execute("SELECT * FROM game_id_mapping LIMIT 5")
    samples = cur.fetchall()
    print(f"\n样例数据:")
    for s in samples:
        print(f"  {s}")
    
    # 统计
    cur.execute("SELECT COUNT(*) FROM game_id_mapping")
    count = cur.fetchone()[0]
    print(f"\n总记录数: {count}")
