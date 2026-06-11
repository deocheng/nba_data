import pandas as pd

# 读取CSV
df = pd.read_csv('CSV/2026_season/all_games_2026.csv', encoding='utf-8-sig')

# 显示当前六月份的比赛
df['game_date'] = df['boxscore_url'].str.extract(r'/(\d{8})')[0]
df['game_date'] = pd.to_datetime(df['game_date'], format='%Y%m%d')
june = df[df['game_date'] >= '2026-06-01'].sort_values('game_date')

print('当前CSV中六月份的比赛:')
for _, row in june.iterrows():
    print(f"  {row['game_date'].strftime('%Y-%m-%d')}: {row['visitor_team']} @ {row['home_team']}")
    print(f"    URL: {row['boxscore_url']}")
    print()
