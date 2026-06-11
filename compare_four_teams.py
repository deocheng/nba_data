import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

from pathlib import Path
import re

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
    'Offensive Rebound Pct',
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
    'Defensive Rebound Pct',
    'Defensive Rating', 'Defensive Win Shares', 'Defensive Box Plus/Minus',
    'Personal Fouls', 'Personal Fouls Per 36 Minutes', 'Personal Fouls Per 100 Possessions',
    'Assist Pct'
]

EXCLUDE_CATEGORIES = [
    'Total Rebounds', 'Total Rebounds Per Game', 'Total Rebounds Per 36 Minutes', 'Total Rebounds Per 100 Possessions',
    'Total Rebound Pct'
]

TEAM_INFO = {
    'OKC': {'name': '俄克拉荷马城雷霆', 'color': '#007AC1'},
    'SAS': {'name': '圣安东尼奥马刺', 'color': '#C4CED4'},
    'NYK': {'name': '纽约尼克斯', 'color': '#006BB6'},
    'CLE': {'name': '克利夫兰骑士', 'color': '#860038'}
}

def is_player_name(category):
    return bool(re.search(r'[A-Z][a-z]+\s+[A-Z][a-z]+.*[A-Z]{2,3}\d', category))

def is_excluded(category):
    return any(excl.lower() in category.lower() for excl in EXCLUDE_CATEGORIES)

def analyze_team(team_abbr, season='2025-26'):
    df = pd.read_csv(CSV_FILE)
    season_data = df[df['season'] == season].copy()
    
    team_data = season_data[season_data['team'] == team_abbr].copy()
    
    offensive_contrib = 0
    defensive_contrib = 0
    offensive_categories = set()
    defensive_categories = set()
    player_contributions = {}
    
    for _, row in team_data.iterrows():
        rank = row['rank']
        category = row['category']
        player = row['player']
        
        if is_player_name(category) or is_excluded(category):
            continue
        
        if rank <= 20:
            contribution = (20 - rank) / 20
            
            is_offensive = any(off_cat.lower() in category.lower() for off_cat in OFFENSIVE_CATEGORIES)
            is_defensive = any(def_cat.lower() in category.lower() for def_cat in DEFENSIVE_CATEGORIES)
            
            if is_offensive:
                offensive_contrib += contribution
                offensive_categories.add(category)
            
            if is_defensive:
                defensive_contrib += contribution
                defensive_categories.add(category)
            
            if player not in player_contributions:
                player_contributions[player] = 0
            player_contributions[player] += contribution
    
    total_contrib = offensive_contrib + defensive_contrib
    offensive_pct = (offensive_contrib / total_contrib) * 100 if total_contrib > 0 else 0
    defensive_pct = (defensive_contrib / total_contrib) * 100 if total_contrib > 0 else 0
    
    top_players = sorted(player_contributions.items(), key=lambda x: -x[1])[:5]
    
    return {
        'team_abbr': team_abbr,
        'team_name': TEAM_INFO[team_abbr]['name'],
        'color': TEAM_INFO[team_abbr]['color'],
        'offensive_contrib': offensive_contrib,
        'defensive_contrib': defensive_contrib,
        'total_contrib': total_contrib,
        'offensive_pct': offensive_pct,
        'defensive_pct': defensive_pct,
        'offensive_categories': len(offensive_categories),
        'defensive_categories': len(defensive_categories),
        'top_players': top_players
    }

def main():
    teams = ['OKC', 'SAS', 'NYK', 'CLE']
    results = {}
    
    for team in teams:
        results[team] = analyze_team(team)
        print(f"分析完成: {results[team]['team_name']}")
    
    print("\n=== 2025-26赛季 四队攻防占比对比 ===")
    print(f"{'球队':<15} {'进攻贡献':<12} {'防守贡献':<12} {'进攻占比':<8} {'防守占比':<8}")
    print("-" * 65)
    for team in teams:
        r = results[team]
        print(f"{r['team_name']:<15} {r['offensive_contrib']:<12.2f} {r['defensive_contrib']:<12.2f} {r['offensive_pct']:<6.1f}% {r['defensive_pct']:<6.1f}%")
    
    print("\n📋 各队核心球员贡献:")
    for team in teams:
        r = results[team]
        print(f"\n{r['team_name']}:")
        for player, contrib in r['top_players']:
            print(f"  • {player}: {contrib:.2f}")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    team_names = [results[t]['team_name'] for t in teams]
    offensive_values = [results[t]['offensive_pct'] for t in teams]
    defensive_values = [results[t]['defensive_pct'] for t in teams]
    colors = [results[t]['color'] for t in teams]
    
    x = range(len(teams))
    width = 0.35
    
    bars1 = ax1.bar([i - width/2 for i in x], offensive_values, width, label='进攻', color='#10b981')
    bars2 = ax1.bar([i + width/2 for i in x], defensive_values, width, label='防守', color='#e94560')
    ax1.set_xticks(x)
    ax1.set_xticklabels(team_names, fontsize=11)
    ax1.set_title('四队攻防占比对比', fontsize=14, fontweight='bold')
    ax1.set_ylabel('占比 (%)', fontsize=12)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, height, f'{height:.1f}%', 
                 ha='center', va='bottom', fontsize=9)
    
    for bar in bars2:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, height, f'{height:.1f}%', 
                 ha='center', va='bottom', fontsize=9)
    
    total_contribs = [results[t]['total_contrib'] for t in teams]
    bars3 = ax2.bar(team_names, total_contribs, color=colors)
    ax2.set_title('四队总贡献值对比', fontsize=14, fontweight='bold')
    ax2.set_ylabel('总贡献值', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    for bar, contrib in zip(bars3, total_contribs):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{contrib:.1f}', 
                 ha='center', va='bottom', fontsize=11)
    
    plt.tight_layout()
    chart_file = OUTPUT_DIR / "four_teams_comparison.png"
    plt.savefig(chart_file, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"\n📊 四队对比图表已保存到: {chart_file}")
    
    return results

if __name__ == "__main__":
    main()