import pandas as pd
import sys
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

# 清理CSV中的重复数据
df = pd.read_csv('CSV/2026_season/all_games_2026.csv', encoding='utf-8-sig')
df['game_date'] = df['boxscore_url'].str.extract(r'/(\d{8})')[0]

# 去重
df_unique = df.drop_duplicates(subset=['game_date', 'visitor_team', 'home_team'], keep='first')
df_unique.to_csv('CSV/2026_season/all_games_2026.csv', index=False, encoding='utf-8-sig')
print(f'已去重: {len(df)} -> {len(df_unique)}')

# 检查数据库中的六月份比赛
db = DatabaseManager()
with db.get_cursor() as cur:
    cur.execute("""
        SELECT game_id, game_date, visitor_team, home_team
        FROM game_metadata
        WHERE game_date >= '2026-06-01'
        ORDER BY game_date
    """)
    db_games = cur.fetchall()

print(f'\n数据库中六月份比赛: {len(db_games)}场')
for g in db_games:
    print(f"  {g[1]}: {g[2]} @ {g[3]} ({g[0]})")
