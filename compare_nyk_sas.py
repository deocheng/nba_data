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

def compare_teams(team1_abbr, team2_abbr, season='2025-26'):
    df = pd.read_csv(CSV_FILE)
    season_data = df[df['season'] == season].copy()
    
    team1_data = season_data[season_data['team'] == team1_abbr].copy()
    team2_data = season_data[season_data['team'] == team2_abbr].copy()
    
    def calculate_team_stats(team_data, team_abbr):
        player_contributions = {}
        total_contribution = 0
        categories = set()
        
        for _, row in team_data.iterrows():
            rank = row['rank']
            player = row['player']
            category = row['category']
            
            if rank <= 20:
                contribution = (20 - rank) / 20
                total_contribution += contribution
                categories.add(category)
                
                if player not in player_contributions:
                    player_contributions[player] = 0
                player_contributions[player] += contribution
        
        return {
            'team_abbr': team_abbr,
            'player_count': len(player_contributions),
            'total_contribution': total_contribution,
            'category_count': len(categories),
            'avg_contribution': total_contribution / len(categories) if len(categories) > 0 else 0,
            'player_contributions': player_contributions
        }
    
    team1_stats = calculate_team_stats(team1_data, team1_abbr)
    team2_stats = calculate_team_stats(team2_data, team2_abbr)
    
    return team1_stats, team2_stats

def main():
    team1_stats, team2_stats = compare_teams('NYK', 'SAS')
    
    print("=== 2025-26赛季 尼克斯 vs 马刺 对比分析 ===")
    print(f"\n{'指标':<15} {'尼克斯 (NYK)':<20} {'马刺 (SAS)':<20}")
    print("-" * 60)
    print(f"上榜人数: {team1_stats['player_count']:<20} {team2_stats['player_count']:<20}")
    print(f"上榜类别数: {team1_stats['category_count']:<20} {team2_stats['category_count']:<20}")
    print(f"总贡献值: {team1_stats['total_contribution']:<20.2f} {team2_stats['total_contribution']:<20.2f}")
    print(f"平均贡献度: {(team1_stats['avg_contribution']*100):<18.1f}% {(team2_stats['avg_contribution']*100):<20.1f}%")
    
    print("\n📋 尼克斯上榜球员及贡献:")
    for player, contrib in sorted(team1_stats['player_contributions'].items(), key=lambda x: -x[1]):
        print(f"  • {player}: {contrib:.2f}")
    
    print("\n📋 马刺上榜球员及贡献:")
    for player, contrib in sorted(team2_stats['player_contributions'].items(), key=lambda x: -x[1]):
        print(f"  • {player}: {contrib:.2f}")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    team_names = ['尼克斯 (NYK)', '马刺 (SAS)']
    player_counts = [team1_stats['player_count'], team2_stats['player_count']]
    total_contribs = [team1_stats['total_contribution'], team2_stats['total_contribution']]
    
    bars1 = ax1.bar(team_names, player_counts, color=['#006BB6', '#C4CED4'])
    ax1.set_title('上榜人数对比', fontsize=14, fontweight='bold')
    ax1.set_ylabel('人数', fontsize=12)
    for bar, count in zip(bars1, player_counts):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{count}', 
                 ha='center', va='bottom', fontsize=12)
    
    bars2 = ax2.bar(team_names, total_contribs, color=['#006BB6', '#C4CED4'])
    ax2.set_title('总贡献值对比', fontsize=14, fontweight='bold')
    ax2.set_ylabel('贡献值', fontsize=12)
    for bar, contrib in zip(bars2, total_contribs):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{contrib:.2f}', 
                 ha='center', va='bottom', fontsize=12)
    
    plt.tight_layout()
    chart_file = OUTPUT_DIR / "nyk_vs_sas_comparison.png"
    plt.savefig(chart_file, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"\n📊 对比图表已保存到: {chart_file}")
    
    return team1_stats, team2_stats

if __name__ == "__main__":
    main()