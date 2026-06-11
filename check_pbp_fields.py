import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()
with db.get_cursor() as cur:
    cur.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'play_by_play'
        ORDER BY ordinal_position
    """)
    cols = cur.fetchall()
    print("play_by_play 字段:")
    for c in cols:
        print(f"  - {c[0]}")
