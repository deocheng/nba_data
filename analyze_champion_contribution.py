import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
CSV_FILE = BASE_DIR / "CSV_Clean" / "league_leaders_parsed.csv"
OUTPUT_DIR = BASE_DIR / "static" / "charts"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PAST_5_YEARS = [
    ('2025-26', '待定'),
    ('2024-25', '波士顿凯尔特人'),
    ('2023-24', '俄克拉荷马城雷霆'),
    ('2022-23', '丹佛掘金'),
    ('2021-22', '金州勇士'),
]

TEAM_ABBR_MAP = {
    '凯尔特人': 'BOS',
    '雷霆': 'OKC',
    '掘金': 'DEN',
    '勇士': 'GSW',
}

def calculate_champion_contribution():
    df = pd.read_csv(CSV_FILE)
    
    results = []
    
    for season, champion in PAST_5_YEARS:
        print(f"\n=== {season}赛季 - 冠军: {champion} ===")
        
        season_data = df[df['season'] == season].copy()
        
        if season_data.empty:
            print(f"  没有找到 {season} 赛季的数据")
            continue
        
        team_abbr = TEAM_ABBR_MAP.get(champion.replace('俄克拉荷马城', '').replace('波士顿', '').replace('丹佛', '').replace('金州', ''), '')
        
        if not team_abbr:
            print(f"  无法识别球队缩写: {champion}")
            continue
        
        team_data = season_data[season_data['team'] == team_abbr].copy()
        
        total_categories = len(season_data['category'].unique())
        team_categories = len(team_data['category'].unique())
        
        print(f"  赛季统计类别总数: {total_categories}")
        print(f"  冠军队上榜类别数: {team_categories}")
        print(f"  上榜率: {team_categories/total_categories*100:.1f}%")
        
        contribution_sum = 0
        player_contributions = {}
        
        for _, row in team_data.iterrows():
            rank = row['rank']
            if rank <= 20:
                contribution = (20 - rank) / 20
                contribution_sum += contribution
                
                player = row['player']
                if player not in player_contributions:
                    player_contributions[player] = 0
                player_contributions[player] += contribution
        
        avg_contribution = contribution_sum / team_categories if team_categories > 0 else 0
        
        print(f"  总贡献值: {contribution_sum:.2f}")
        print(f"  平均贡献值: {avg_contribution:.2f}")
        print(f"  上榜球员贡献分布:")
        for player, contrib in sorted(player_contributions.items(), key=lambda x: -x[1]):
            print(f"    • {player}: {contrib:.2f}")
        
        results.append({
            'season': season,
            'champion': champion,
            'team_abbr': team_abbr,
            'total_categories': total_categories,
            'team_categories': team_categories,
            'coverage_rate': team_categories / total_categories,
            'total_contribution': contribution_sum,
            'avg_contribution': avg_contribution,
            'player_contributions': player_contributions
        })
    
    results_file = OUTPUT_DIR / "champion_contribution_analysis.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 分析结果已保存到: {results_file}")
    
    return results

def plot_results(results):
    plt.figure(figsize=(12, 8))
    
    seasons = [r['season'] for r in results]
    coverage_rates = [r['coverage_rate'] * 100 for r in results]
    avg_contributions = [r['avg_contribution'] * 100 for r in results]
    
    x = range(len(seasons))
    width = 0.35
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    bars1 = ax1.bar(x, coverage_rates, width, color='#e94560', label='上榜率')
    ax1.set_ylabel('上榜率 (%)', fontsize=12)
    ax1.set_title('过去五年冠军队在联盟领袖榜单的表现', fontsize=16, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(seasons, fontsize=10)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    for bar, rate in zip(bars1, coverage_rates):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{rate:.1f}%', 
                 ha='center', va='bottom', fontsize=9)
    
    bars2 = ax2.bar(x, avg_contributions, width, color='#4dbd74', label='平均贡献度')
    ax2.set_xlabel('赛季', fontsize=12)
    ax2.set_ylabel('平均贡献度 (%)', fontsize=12)
    ax2.set_xticks(x)
    ax2.set_xticklabels(seasons, fontsize=10)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    for bar, contrib in zip(bars2, avg_contributions):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{contrib:.1f}%', 
                 ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    plot_file = OUTPUT_DIR / "champion_contribution_chart.png"
    plt.savefig(plot_file, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"\n📊 图表已保存到: {plot_file}")

if __name__ == "__main__":
    results = calculate_champion_contribution()
    plot_results(results)
    
    print("\n=== 汇总结果 ===")
    print(f"{'赛季':<10} {'冠军队':<12} {'上榜率':<8} {'平均贡献度':<10}")
    print("-" * 50)
    for r in results:
        print(f"{r['season']:<10} {r['champion']:<12} {r['coverage_rate']*100:>6.1f}% {r['avg_contribution']*100:>12.1f}%")