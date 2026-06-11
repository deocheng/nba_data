import pandas as pd

# 读取现有CSV
df = pd.read_csv('CSV/2026_season/all_games_2026.csv', encoding='utf-8-sig')

# 添加总决赛G1和G2
new_games = [
    {'month': 'june', 'date': 1, 'visitor_team': 'San Antonio Spurs', 'home_team': 'New York Knicks',
     'visitor_score': '', 'home_score': '', 'boxscore_url': 'https://www.basketball-reference.com/boxscores/202606010NYK.html'},
    {'month': 'june', 'date': 2, 'visitor_team': 'San Antonio Spurs', 'home_team': 'New York Knicks',
     'visitor_score': '', 'home_score': '', 'boxscore_url': 'https://www.basketball-reference.com/boxscores/202606020NYK.html'},
    {'month': 'june', 'date': 8, 'visitor_team': 'San Antonio Spurs', 'home_team': 'New York Knicks',
     'visitor_score': '', 'home_score': '', 'boxscore_url': 'https://www.basketball-reference.com/boxscores/202606080NYK.html'},
]

# 检查是否已存在
g1_exists = any('202606010' in str(url) for url in df['boxscore_url'])
g2_exists = any('202606020' in str(url) for url in df['boxscore_url'])
g6_exists = any('202606080' in str(url) for url in df['boxscore_url'])

if not g1_exists or not g2_exists or not g6_exists:
    new_df = pd.DataFrame(new_games)
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv('CSV/2026_season/all_games_2026.csv', index=False, encoding='utf-8-sig')
    print('已添加G1、G2和G6到CSV')
else:
    print('G1、G2和G6已存在')

# 显示六月份的比赛
df['game_date'] = df['boxscore_url'].str.extract(r'/(\d{8})')[0]
df['game_date'] = pd.to_datetime(df['game_date'], format='%Y%m%d')
june = df[df['game_date'] >= '2026-06-01'].sort_values('game_date')
print(f'\n六月份总决赛比赛:')
for _, row in june.iterrows():
    print(f"  {row['game_date'].strftime('%Y-%m-%d')}: {row['visitor_team']} @ {row['home_team']} ({row['boxscore_url'].split('/')[-1].replace('.html','')})")
