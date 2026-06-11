import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()

with db.get_cursor() as cur:
    # 获取pbp_all表的所有字段
    cur.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'pbp_all'
        ORDER BY ordinal_position
    """)
    cols = [r[0] for r in cur.fetchall()]
    print(f"pbp_all表字段:")
    for col in cols:
        print(f"  {col}")
    
    # 检查样例数据
    cur.execute("SELECT * FROM pbp_all LIMIT 1")
    sample = cur.fetchone()
    print(f"\n样例数据:")
    for i, col in enumerate(cols):
        print(f"  {col}: {sample[i]}")

print("\n" + "="*60)
print("分析：需要检查哪些字段包含日期和主队信息")
print("="*60)
