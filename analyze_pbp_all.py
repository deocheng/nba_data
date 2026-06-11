import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()

with db.get_cursor() as cur:
    # 检查pbp_all的gameid分布
    cur.execute("""
        SELECT 
            MIN(gameid) as min_id,
            MAX(gameid) as max_id,
            COUNT(DISTINCT gameid) as game_count
        FROM pbp_all
    """)
    stats = cur.fetchone()
    print(f"pbp_all: {stats[2]:,}场")
    print(f"  范围: {stats[0]} - {stats[1]}")

    # 获取一些gameid样本
    cur.execute("""
        SELECT DISTINCT gameid 
        FROM pbp_all 
        ORDER BY gameid
        LIMIT 30
    """)
    samples = [r[0] for r in cur.fetchall()]
    
    print(f"\ngameid样本:")
    for s in samples[:15]:
        print(f"  {s}")
    
    print(f"\n分析:")
    print(f"  前4位: {str(samples[0])[:4]} - {str(samples[-1])[:4]}")
    print(f"  后4位: {str(samples[0])[4:]} - {str(samples[-1])[4:]}")
    
    # 检查年份分布
    cur.execute("""
        SELECT 
            LEFT(gameid::text, 4) as year_prefix,
            COUNT(DISTINCT gameid) as games,
            MIN(gameid) as min_id,
            MAX(gameid) as max_id
        FROM pbp_all
        GROUP BY LEFT(gameid::text, 4)
        ORDER BY year_prefix
        LIMIT 30
    """)
    year_stats = cur.fetchall()
    
    print(f"\n按前4位年份统计:")
    for y in year_stats:
        print(f"  {y[0]}: {y[1]:,}场 ({y[2]} - {y[3]})")
