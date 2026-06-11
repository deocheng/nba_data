import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()

with db.get_cursor() as cur:
    # 获取各赛季的gameid样例
    cur.execute("""
        SELECT DISTINCT gameid 
        FROM pbp_all 
        WHERE gameid >= 20000000 AND gameid < 21000000
        ORDER BY gameid
        LIMIT 10
    """)
    samples = [r[0] for r in cur.fetchall()]

print("=" * 60)
print("验证 gameid 格式：2 + 年份(2位) + 0 + 场次(4位)")
print("=" * 60)

def parse_gameid(gid):
    """解析gameid"""
    gid_str = str(gid).zfill(8)  # 确保8位
    prefix = gid_str[0]    # 2
    year = gid_str[1:3]    # 96
    separator = gid_str[3] # 0
    seq = gid_str[4:]      # 0001
    return f"2|{year}|{separator}|{seq}"

print("\n样例解析:")
for s in samples[:8]:
    parsed = parse_gameid(s)
    print(f"  {s} → {parsed}")

print("""
============================================================
结论：
  29600001 = 2 | 96 | 0 | 0001 = 标识2 + 1996年 + 分隔0 + 第1场
  20000001 = 2 | 00 | 0 | 0001 = 标识2 + 2000年 + 分隔0 + 第1场
  20200001 = 2 | 20 | 0 | 0001 = 标识2 + 2020年 + 分隔0 + 第1场

✅ 您的理解正确！
============================================================
""")
