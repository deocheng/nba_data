import pandas as pd
df = pd.read_csv('CSV/2026_season/all_games_2026.csv', encoding='utf-8-sig')
df['game_date'] = df['boxscore_url'].str.extract(r'/(\d{8})')[0]
df['game_date'] = pd.to_datetime(df['game_date'], format='%Y%m%d')

# 筛选六月份的比赛
june = df[df['game_date'] >= '2026-06-01']
print(f'六月份比赛数: {len(june)}')
for _, row in june.iterrows():
    print(f"  {row['game_date'].strftime('%Y-%m-%d')}: {row['visitor_team']} @ {row['home_team']}")
