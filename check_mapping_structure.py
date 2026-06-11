import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()

with db.get_cursor() as cur:
    # 获取game_id_mapping表的字段
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'game_id_mapping'
        ORDER BY ordinal_position
    """)
    cols = cur.fetchall()
    print("game_id_mapping 表结构:")
    for col, dtype in cols:
        print(f"  {col}: {dtype}")
    
    # 查看样例数据
    cur.execute("SELECT * FROM game_id_mapping LIMIT 2")
    samples = cur.fetchall()
    print(f"\n样例数据:")
    for s in samples:
        print(f"  {s}")
