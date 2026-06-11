import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

from pathlib import Path

BASE_DIR = Path(__file__).parent
CSV_FILE = BASE_DIR / "CSV_Clean" / "league_leaders_parsed.csv"
OUTPUT_DIR = BASE_DIR / "static" / "charts"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

NEUTRAL_CATEGORIES = [
    'Rebounds Per Game', 'Rebounds'
]

import re
def is_player_name(category):
    return bool(re.search(r'[A-Z][a-z]+\s+[A-Z][a-z]+.*[A-Z]{2,3}\d', category))

def analyze_offense_defense_corrected(team_abbr, season='2025-26'):
    df = pd.read_csv(CSV_FILE)
    season_data = df[df['season'] == season].copy()
    
    team_data = season_data[season_data['team'] == team_abbr].copy()
    
    offensive_contrib = 0
    defensive_contrib = 0
    neutral_contrib = 0
    offensive_categories = set()
    defensive_categories = set()
    neutral_categories = set()
    
    for _, row in team_data.iterrows():
        rank = row['rank']
        category = row['category']
        
        if is_player_name(category):
            continue
        
        if rank <= 20:
            contribution = (20 - rank) / 20
            
            is_offensive = any(off_cat.lower() in category.lower() for off_cat in OFFENSIVE_CATEGORIES)
            is_defensive = any(def_cat.lower() in category.lower() for def_cat in DEFENSIVE_CATEGORIES)
            is_neutral = any(neu_cat.lower() in category.lower() for neu_cat in NEUTRAL_CATEGORIES)
            
            if is_neutral:
                neutral_contrib += contribution
                neutral_categories.add(category)
                offensive_contrib += contribution / 2
                defensive_contrib += contribution / 2
            elif is_offensive and not is_defensive:
                offensive_contrib += contribution
                offensive_categories.add(category)
            elif is_defensive and not is_offensive:
                defensive_contrib += contribution
                defensive_categories.add(category)
            elif is_offensive and is_defensive:
                offensive_contrib += contribution
                defensive_contrib += contribution
                offensive_categories.add(category)
                defensive_categories.add(category)
    
    total_contrib = offensive_contrib + defensive_contrib
    offensive_pct = (offensive_contrib / total_contrib) * 100 if total_contrib > 0 else 0
    defensive_pct = (defensive_contrib / total_contrib) * 100 if total_contrib > 0 else 0
    
    return {
        'team_abbr': team_abbr,
        'offensive_contrib': offensive_contrib,
        'defensive_contrib': defensive_contrib,
        'neutral_contrib': neutral_contrib,
        'total_contrib': total_contrib,
        'offensive_pct': offensive_pct,
        'defensive_pct': defensive_pct,
        'offensive_categories': len(offensive_categories),
        'defensive_categories': len(defensive_categories),
        'neutral_categories': len(neutral_categories)
    }

def main():
    nyk_stats = analyze_offense_defense_corrected('NYK')
    sas_stats = analyze_offense_defense_corrected('SAS')
    
    print("=== 2025-26赛季 尼克斯 vs 马刺 攻防占比分析（修正版）===")
    print("修正规则：中性类别（如篮板）贡献值平均分配给攻防两端")
    print(f"\n{'指标':<22} {'尼克斯 (NYK)':<20} {'马刺 (SAS)':<20}")
    print("-" * 68)
    print(f"进攻贡献值: {nyk_stats['offensive_contrib']:<20.2f} {sas_stats['offensive_contrib']:<20.2f}")
    print(f"防守贡献值: {nyk_stats['defensive_contrib']:<20.2f} {sas_stats['defensive_contrib']:<20.2f}")
    print(f"中性贡献值: {nyk_stats['neutral_contrib']:<20.2f} {sas_stats['neutral_contrib']:<20.2f}")
    print(f"进攻占比: {(nyk_stats['offensive_pct']):<18.1f}% {(sas_stats['offensive_pct']):<20.1f}%")
    print(f"防守占比: {(nyk_stats['defensive_pct']):<18.1f}% {(sas_stats['defensive_pct']):<20.1f}%")
    print(f"进攻类别数: {nyk_stats['offensive_categories']:<20} {sas_stats['offensive_categories']:<20}")
    print(f"防守类别数: {nyk_stats['defensive_categories']:<20} {sas_stats['defensive_categories']:<20}")
    print(f"中性类别数: {nyk_stats['neutral_categories']:<20} {sas_stats['neutral_categories']:<20}")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    labels = ['进攻', '防守']
    nyk_sizes = [nyk_stats['offensive_pct'], nyk_stats['defensive_pct']]
    sas_sizes = [sas_stats['offensive_pct'], sas_stats['defensive_pct']]
    
    colors = ['#10b981', '#e94560']
    
    ax1.pie(nyk_sizes, labels=labels, colors=colors, autopct='%1.1f%%',
            startangle=90, textprops={'fontsize': 12})
    ax1.set_title('尼克斯 攻防占比（修正版）', fontsize=14, fontweight='bold')
    ax1.axis('equal')
    
    ax2.pie(sas_sizes, labels=labels, colors=colors, autopct='%1.1f%%',
            startangle=90, textprops={'fontsize': 12})
    ax2.set_title('马刺 攻防占比（修正版）', fontsize=14, fontweight='bold')
    ax2.axis('equal')
    
    plt.tight_layout()
    chart_file = OUTPUT_DIR / "nyk_sas_offense_defense_corrected.png"
    plt.savefig(chart_file, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"\n📊 修正后的攻防占比饼图已保存到: {chart_file}")
    
    return nyk_stats, sas_stats

if __name__ == "__main__":
    main()