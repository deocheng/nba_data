import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()
with db.get_cursor() as cur:
    # 删除旧记录
    cur.execute("DELETE FROM play_by_play WHERE game_id = '202606080NYK'")
    print(f"已删除PBP记录: {cur.rowcount}条")
    
    cur.execute("DELETE FROM game_metadata WHERE game_id = '202606080NYK'")
    print(f"已删除元数据: {cur.rowcount}条")

print("可以重新爬取G3了")
