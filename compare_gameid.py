import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()

with db.get_cursor() as cur:
    # 检查pbp_1997的gameid格式
    cur.execute("SELECT DISTINCT gameid FROM pbp_1997 LIMIT 5")
    pbp_1997_ids = cur.fetchall()
    
    # 检查play_by_play的game_id格式
    cur.execute("SELECT DISTINCT game_id FROM play_by_play LIMIT 5")
    play_by_play_ids = cur.fetchall()

print("=" * 60)
print("gameid命名规则对比")
print("=" * 60)
print("\npbp_1997表的gameid:")
for g in pbp_1997_ids:
    print(f"  {g[0]}")
    print(f"    类型: {type(g[0]).__name__}, 长度: {len(str(g[0]))}")

print("\nplay_by_play表的game_id:")
for g in play_by_play_ids:
    print(f"  {g[0]}")
    print(f"    类型: {type(g[0]).__name__}, 长度: {len(str(g[0]))}")

print("\n" + "=" * 60)
print("结论:")
print("pbp_1997: gameid = 纯数字 (如29600001)")
print("play_by_play: game_id = 字母+数字 (如202606080NYK)")
print("=" * 60)
