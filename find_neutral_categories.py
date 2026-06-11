import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent
CSV_FILE = BASE_DIR / "CSV_Clean" / "league_leaders_parsed.csv"

OFFENSIVE_CATEGORIES = [
    'Points', 'Points Per Game', 'Points Per 36 Minutes', 'Points Per 100 Possessions',
    'Assists', 'Assists Per Game', 'Assists Per 36 Minutes', 'Assists Per 100 Possessions',
    'Field Goals', 'Field Goals Per Game', 'Field Goals Per 36 Minutes', 'Field Goals Per 100 Possessions',
    'Field Goal Attempts', 'Field Goal Attempts Per Game', 'Field Goal Attempts Per 36 Minutes', 'Field Goal Attempts Per 100 Possessions',
    'Three Pointers', 'Three Pointers Per Game', 'Three Point Attempts', 'Three Point Attempts Per Game',
    'Free Throws', 'Free Throws Per Game', 'Free Throws Per 36 Minutes', 'Free Throws Per 100 Possessions',
    'Free Throw Attempts', 'Free Throw Attempts Per Game', 'Free Throw Attempts Per 36 Minutes', 'Free Throw Attempts Per 100 Possessions',
    'Offensive Rebounds', 'Offensive Rebounds Per Game', 'Offensive Rebounds Per 36 Minutes', 'Offensive Rebounds Per 100 Possessions',
    'Field Goal Pct', 'Three Point Pct', 'Free Throw Pct', 'True Shooting Pct', 'Effective Field Goal Pct',
    'Offensive Rating', 'Offensive Win Shares', 'Offensive Box Plus/Minus',
    'Usage Pct', 'Player Efficiency Rating', 'Win Shares', 'Win Shares Per 48 Minutes',
    'Value Over Replacement Player', 'Box Plus/Minus', 'Minutes Played', 'Minutes Per Game',
    'Turnovers', 'Turnovers Per Game', 'Turnovers Per 36 Minutes', 'Turnovers Per 100 Possessions', 'Turnover Pct'
]

DEFENSIVE_CATEGORIES = [
    'Steals', 'Steals Per Game', 'Steals Per 36 Minutes', 'Steals Per 100 Possessions', 'Steal Pct',
    'Blocks', 'Blocks Per Game', 'Blocks Per 36 Minutes', 'Blocks Per 100 Possessions', 'Block Pct',
    'Defensive Rebounds', 'Defensive Rebounds Per Game', 'Defensive Rebounds Per 36 Minutes', 'Defensive Rebounds Per 100 Possessions',
    'Total Rebounds', 'Total Rebounds Per Game', 'Total Rebounds Per 36 Minutes', 'Total Rebounds Per 100 Possessions',
    'Defensive Rebound Pct', 'Offensive Rebound Pct', 'Total Rebound Pct',
    'Defensive Rating', 'Defensive Win Shares', 'Defensive Box Plus/Minus',
    'Personal Fouls', 'Personal Fouls Per 36 Minutes', 'Personal Fouls Per 100 Possessions',
    'Assist Pct'
]

def find_missing_categories(team_abbr, season='2025-26'):
    df = pd.read_csv(CSV_FILE)
    season_data = df[df['season'] == season].copy()
    
    team_data = season_data[season_data['team'] == team_abbr].copy()
    
    all_categories = set()
    offensive_categories = set()
    defensive_categories = set()
    neutral_categories = set()
    
    for _, row in team_data.iterrows():
        category = row['category']
        all_categories.add(category)
        
        is_offensive = any(off_cat.lower() in category.lower() for off_cat in OFFENSIVE_CATEGORIES)
        is_defensive = any(def_cat.lower() in category.lower() for def_cat in DEFENSIVE_CATEGORIES)
        
        if is_offensive:
            offensive_categories.add(category)
        if is_defensive:
            defensive_categories.add(category)
        if not is_offensive and not is_defensive:
            neutral_categories.add(category)
    
    print(f"\n=== {team_abbr} 类别分析 ===")
    print(f"总上榜类别数: {len(all_categories)}")
    print(f"进攻类别数: {len(offensive_categories)}")
    print(f"防守类别数: {len(defensive_categories)}")
    print(f"中性类别数: {len(neutral_categories)}")
    print(f"重叠类别(攻防都算): {len(offensive_categories & defensive_categories)}")
    
    print("\n📋 中性类别列表(既不算进攻也不算防守):")
    for i, cat in enumerate(sorted(neutral_categories), 1):
        print(f"{i}. {cat}")
    
    print("\n📋 重叠类别(攻防都算):")
    for i, cat in enumerate(sorted(offensive_categories & defensive_categories), 1):
        print(f"{i}. {cat}")
    
    return {
        'all': all_categories,
        'offensive': offensive_categories,
        'defensive': defensive_categories,
        'neutral': neutral_categories,
        'overlap': offensive_categories & defensive_categories
    }

if __name__ == "__main__":
    print("=== 尼克斯 (NYK) ===")
    nyk_result = find_missing_categories('NYK')
    
    print("\n\n=== 马刺 (SAS) ===")
    sas_result = find_missing_categories('SAS')