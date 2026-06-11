import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()

with db.get_cursor() as cur:
    # 检查pbp_1997表
    cur.execute("SELECT COUNT(*) FROM pbp_1997")
    pbp_1997 = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM pbp_all")
    pbp_all = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM play_by_play")
    play_by_play = cur.fetchone()[0]
    
    # 检查player_totals
    cur.execute("SELECT COUNT(*) FROM player_totals")
    player_totals = cur.fetchone()[0]
    
    # 检查team_totals
    cur.execute("SELECT COUNT(*) FROM team_totals")
    team_totals = cur.fetchone()[0]
    
    # 检查年份范围
    cur.execute("""
        SELECT MIN(season), MAX(season) FROM player_totals
    """)
    season_range = cur.fetchone()
    
    cur.execute("""
        SELECT MIN(season), MAX(season) FROM team_totals
    """)
    team_season_range = cur.fetchone()

print("=" * 60)
print("数据库数据概览")
print("=" * 60)
print(f"\nPBP数据:")
print(f"  - pbp_1997: {pbp_1997:,}条")
print(f"  - pbp_all: {pbp_all:,}条")
print(f"  - play_by_play: {play_by_play:,}条")
print(f"\n球员统计:")
print(f"  - player_totals: {player_totals:,}条 ({season_range[0]}-{season_range[1]})")
print(f"\n球队统计:")
print(f"  - team_totals: {team_totals:,}条 ({team_season_range[0]}-{team_season_range[1]})")
print("=" * 60)
