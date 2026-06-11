import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()
with db.get_cursor() as cur:
    cur.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'game_metadata'
        ORDER BY ordinal_position
    """)
    cols = cur.fetchall()
    print("game_metadata 字段:")
    for c in cols:
        print(f"  - {c[0]}")
