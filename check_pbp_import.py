import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()

with db.get_cursor() as cur:
    # 检查pbp_1997表的记录数
    cur.execute("SELECT COUNT(*) FROM pbp_1997")
    pbp_1997_count = cur.fetchone()[0]
    
    # 检查play_by_play表的记录数
    cur.execute("SELECT COUNT(*) FROM play_by_play")
    play_by_play_count = cur.fetchone()[0]
    
    # 检查2026年的数据
    cur.execute("""
        SELECT COUNT(DISTINCT game_id) FROM play_by_play 
        WHERE game_id LIKE '202606%'
    """)
    finals_count = cur.fetchone()[0]

print("=" * 60)
print("PBP数据导入状态")
print("=" * 60)
print(f"pbp_1997表: {pbp_1997_count:,}条 (CSV: 595,362条)")
print(f"play_by_play表: {play_by_play_count:,}条")
print(f"  - 其中2026年总决赛: {finals_count}场")
print()
print("如果pbp_1997记录数=595362，说明CSV已完全导入")
print("play_by_play包含2025-2026年最新爬取的季后赛数据")
print("=" * 60)
