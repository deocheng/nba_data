import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()

with db.get_cursor() as cur:
    # 检查是否已有映射表
    cur.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_name = 'game_id_mapping'
    """)
    exists = cur.fetchone()
    
    if exists:
        cur.execute("SELECT COUNT(*) FROM game_id_mapping")
        count = cur.fetchone()[0]
        print(f"✅ game_id_mapping 表已存在: {count}条记录")
    else:
        print("❌ game_id_mapping 表不存在，需要创建")
        
    # 检查pbp_all是否已有日期字段
    cur.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'pbp_all'
        LIMIT 10
    """)
    cols = [r[0] for r in cur.fetchall()]
    print(f"\npbp_all表字段: {cols}")
    
    # 检查play_by_play是否已有br_gameid字段
    cur.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'play_by_play'
    """)
    cols2 = [r[0] for r in cur.fetchall()]
    print(f"\nplay_by_play表字段: {cols2}")

print("""
============================================================
建议的补全方案：
============================================================

1. 在 pbp_all 表添加字段：
   - game_date (日期)
   - home_team (主场球队)
   - br_gameid (保持原gameid)

2. 在 play_by_play 表添加字段：
   - br_gameid (BR格式)
   
3. 创建 game_id_mapping 映射表

这样两种格式就能互相对应了！
============================================================
""")
