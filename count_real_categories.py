import pandas as pd
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
CSV_FILE = BASE_DIR / "CSV_Clean" / "league_leaders_parsed.csv"

df = pd.read_csv(CSV_FILE)
df_2025 = df[df['season'] == '2025-26'].copy()

KNOWN_STATS = [
    'Points', 'Points Per Game', 'Rebounds', 'Rebounds Per Game',
    'Assists', 'Assists Per Game', 'Steals', 'Steals Per Game',
    'Blocks', 'Blocks Per Game', 'Field Goals', 'Field Goals Per Game',
    'Field Goal Attempts', 'Field Goal Attempts Per Game',
    'Three Pointers', 'Three Pointers Per Game', 'Three Point Attempts',
    'Three Point Attempts Per Game', 'Free Throws', 'Free Throws Per Game',
    'Free Throw Attempts', 'Free Throw Attempts Per Game',
    'Offensive Rebounds', 'Offensive Rebounds Per Game',
    'Defensive Rebounds', 'Defensive Rebounds Per Game',
    'Total Rebounds', 'Total Rebounds Per Game',
    'Minutes Played', 'Minutes Per Game', 'Games',
    'Player Efficiency Rating', 'Win Shares', 'Win Shares Per 48 Minutes',
    'Box Plus/Minus', 'Value Over Replacement Player',
    'Usage Pct', 'True Shooting Pct', 'Effective Field Goal Pct',
    'Turnovers', 'Turnovers Per Game', 'Personal Fouls',
    'Field Goal Pct', 'Free Throw Pct', 'Three Point Pct',
    'Offensive Rating', 'Defensive Rating',
    'Total Rebound Pct', 'Offensive Rebound Pct', 'Defensive Rebound Pct',
    'Steal Pct', 'Block Pct', 'Assist Pct',
    'Points Per 100 Possessions', 'Points Per 36 Minutes',
    'Assists Per 100 Possessions', 'Assists Per 36 Minutes',
    'Rebounds Per 100 Possessions', 'Rebounds Per 36 Minutes',
    'Steals Per 100 Possessions', 'Steals Per 36 Minutes',
    'Blocks Per 100 Possessions', 'Blocks Per 36 Minutes',
    'Field Goals Per 100 Possessions', 'Field Goals Per 36 Minutes',
    'Field Goal Attempts Per 100 Possessions', 'Field Goal Attempts Per 36 Minutes',
    'Free Throws Per 100 Possessions', 'Free Throws Per 36 Minutes',
    'Free Throw Attempts Per 100 Possessions', 'Free Throw Attempts Per 36 Minutes',
    'Offensive Rebounds Per 100 Possessions', 'Offensive Rebounds Per 36 Minutes',
    'Defensive Rebounds Per 100 Possessions', 'Defensive Rebounds Per 36 Minutes',
    'Total Rebounds Per 100 Possessions', 'Total Rebounds Per 36 Minutes',
    'Turnovers Per 100 Possessions', 'Turnovers Per 36 Minutes',
    'Personal Fouls Per 100 Possessions', 'Personal Fouls Per 36 Minutes',
    'Offensive Win Shares', 'Defensive Win Shares',
    'Offensive Box Plus/Minus', 'Defensive Box Plus/Minus',
    'Field Goals Missed'
]

real_categories = []
for cat in df_2025['category'].unique():
    is_real = any(stat.lower() in cat.lower() for stat in KNOWN_STATS)
    has_player_name = bool(re.search(r'[A-Z][a-z]+\s+[A-Z][a-z]+.*[A-Z]{2,3}\d', cat))
    if is_real and not has_player_name:
        real_categories.append(cat)

print(f"\n=== 2025-26赛季真实统计类别 ===")
print(f"统计类别数量: {len(real_categories)}")
print(f"\n所有统计类别列表:")
for i, cat in enumerate(sorted(real_categories), 1):
    print(f"{i}. {cat}")

output_file = BASE_DIR / "statistics_categories.txt"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("=== 2025-26赛季 NBA 统计类别列表 ===\n\n")
    for i, cat in enumerate(sorted(real_categories), 1):
        f.write(f"{i}. {cat}\n")
    f.write(f"\n总计: {len(real_categories)} 个统计类别\n")

print(f"\n列表已保存到 {output_file}")
