import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()
with db.get_cursor() as cur:
    # 总比赛数
    cur.execute("SELECT COUNT(*) FROM game_metadata")
    total = cur.fetchone()[0]
    
    # PBP记录数
    cur.execute("SELECT COUNT(*) FROM play_by_play")
    pbp_records = cur.fetchone()[0]
    
    # 六月份比赛
    cur.execute("""
        SELECT game_id, game_date::text, visitor_team, home_team
        FROM game_metadata
        WHERE game_date >= '2026-06-01'
        ORDER BY game_date
    """)
    june_games = cur.fetchall()
    
    # 最近的比赛
    cur.execute("""
        SELECT game_id, game_date::text, visitor_team, home_team
        FROM game_metadata
        ORDER BY game_date DESC
        LIMIT 10
    """)
    recent = cur.fetchall()

print('='*60)
print('爬取情况报告')
print('='*60)
print(f'数据库总比赛数: {total}')
print(f'PBP记录总数: {pbp_records}')
print(f'\n六月份总决赛: {len(june_games)}场')
for g in june_games:
    print(f'  {g[1]}: {g[2]} @ {g[3]} ({g[0]})')

print(f'\n最近爬取的比赛:')
for g in recent:
    print(f'  {g[1]}: {g[2]} @ {g[3]} ({g[0]})')
print('='*60)
