import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager
import time

db = DatabaseManager()

# 2026年总决赛的BR格式ID（需要从BR网站获取或推断）
# 格式：2 + 26 + 0 + 序号
finals_games = [
    ('202606020NYK', 22600001, 2026, 109, 118),  # SAS @ NYK G1
    ('202606030SAS', 22600002, 2026, 109, 118),  # NYK @ SAS G2
    ('202606050SAS', 22600003, 2026, 109, 118),  # NYK @ SAS G4?
    ('202606070SAS', 22600004, 2026, 109, 118),  # SAS @ NYK G6?
    ('202606080NYK', 22600005, 2026, 109, 118),  # SAS @ NYK G3
]

print("添加2026年总决赛到映射表...")
print("=" * 60)

with db.get_cursor() as cur:
    added = 0
    for crawled_id, nba_id, season, home_score, visitor_score in finals_games:
        # 检查是否已存在
        cur.execute(
            "SELECT id FROM game_id_mapping WHERE crawled_id = %s",
            (crawled_id,)
        )
        if cur.fetchone():
            print(f"  ⏭ 已存在: {crawled_id}")
            continue
        
        # 插入新记录
        cur.execute("""
            INSERT INTO game_id_mapping (crawled_id, nba_id, season, home_score, visitor_score)
            VALUES (%s, %s, %s, %s, %s)
        """, (crawled_id, nba_id, season, home_score, visitor_score))
        added += 1
        print(f"  ✅ 添加: {crawled_id} ↔ {nba_id}")
        time.sleep(0.1)

print(f"\n添加完成: {added}条记录")

# 验证
with db.get_cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM game_id_mapping WHERE crawled_id LIKE '202606%'")
    count = cur.fetchone()[0]
    print(f"2026年6月映射总数: {count}条")
