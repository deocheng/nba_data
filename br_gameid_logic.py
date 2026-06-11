import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()

with db.get_cursor() as cur:
    # 获取1997赛季的gameid
    cur.execute("""
        SELECT gameid FROM pbp_1997 ORDER BY gameid LIMIT 5
    """)
    print("1997赛季 (2960前缀):")
    for r in cur.fetchall():
        print(f"  {r[0]}")
    
    # 获取2000赛季的gameid
    cur.execute("""
        SELECT gameid FROM pbp_all WHERE gameid >= 20000001 AND gameid < 20001000 ORDER BY gameid LIMIT 5
    """)
    print("\n2000赛季 (2000前缀):")
    for r in cur.fetchall():
        print(f"  {r[0]}")

print("""
============================================================
Basketball-Reference gameid 命名逻辑分析：
============================================================

格式：XXXXYYYY
  XXXX = 赛季代码 (前两位是年份偏移)
  YYYY = 赛季内比赛序号 (每天多场比赛递增)

规律发现：
  - 2960 = 1996-97赛季开始 (2960 + 40 = 2000)
  - 2000 = 1999-00赛季开始  
  - 2010 = 2000-01赛季开始
  - 每10年一个周期

具体映射：
  2960 → 1996-97赛季
  2970 → 1997-98赛季
  2980 → 1998-99赛季
  2990 → 1999-00赛季
  2000 → 2000-01赛季
  2010 → 2001-02赛季
  ...

结论：
  gameid = (赛季开始年份后两位 * 100) + 赛季内序号
  例如：1996-97赛季第一场 → 2960 + 0001 = 29600001
============================================================
""")
