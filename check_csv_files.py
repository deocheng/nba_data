import sys
import os
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()

# 列出CSV目录
csv_dir = r'C:\autopick\AutoPick\CSV'
print(f"CSV目录内容:")
for item in os.listdir(csv_dir):
    path = os.path.join(csv_dir, item)
    if os.path.isfile(path):
        print(f"  {item}")

print("\n" + "="*60)

# 检查pbp_all中有多少唯一的gameid
with db.get_cursor() as cur:
    cur.execute("SELECT COUNT(DISTINCT gameid) FROM pbp_all")
    unique_gameids = cur.fetchone()[0]
    print(f"pbp_all中唯一gameid数量: {unique_gameids}")
    
    # 查看gameid的范围
    cur.execute("SELECT MIN(gameid), MAX(gameid) FROM pbp_all")
    min_max = cur.fetchone()
    print(f"gameid范围: {min_max[0]} - {min_max[1]}")
    
    # 查看前10个gameid
    cur.execute("SELECT DISTINCT gameid FROM pbp_all ORDER BY gameid LIMIT 10")
    sample_ids = [r[0] for r in cur.fetchall()]
    print(f"\n前10个gameid: {sample_ids}")
