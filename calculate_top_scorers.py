import pandas as pd
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
CSV_FILE = BASE_DIR / "CSV_Clean" / "league_leaders_parsed.csv"
OUTPUT_FILE = BASE_DIR / "static" / "charts" / "top_scorers_analysis.json"

def calculate_scores():
    df = pd.read_csv(CSV_FILE)
    df_2025 = df[df['season'] == '2025-26'].copy()
    
    all_players = {}
    categories = df_2025['category'].unique()
    
    for category in categories:
        category_data = df_2025[df_2025['category'] == category].sort_values('rank').head(10)
        
        if len(category_data) < 2:
            continue
        
        values = category_data['value'].tolist()
        players = category_data['player'].tolist()
        teams = category_data['team'].tolist()
        
        max_value = values[0]
        
        for i, (player, team, value) in enumerate(zip(players, teams, values)):
            if player not in all_players:
                all_players[player] = {
                    'player': player,
                    'team': team,
                    'total_score': 0.0,
                    'categories': [],
                    'details': []
                }
            
            base_score = max(10 - i, 0)
            
            bonus = 0.0
            if i == 0 and len(values) > 1:
                gap = (values[0] - values[1]) / values[0] if values[0] != 0 else 0
                if gap >= 0.15:
                    bonus = 1.5
                elif gap > 0:
                    bonus = 1.0
            
            total_score = base_score + bonus
            
            all_players[player]['total_score'] += total_score
            all_players[player]['categories'].append({
                'category': category,
                'rank': i + 1,
                'value': value,
                'base_score': base_score,
                'bonus': bonus,
                'total': total_score
            })
    
    player_list = sorted(all_players.values(), key=lambda x: x['total_score'], reverse=True)
    
    top_5 = player_list[:5]
    
    for player in top_5:
        player['categories'] = sorted(player['categories'], key=lambda x: x['total'], reverse=True)
    
    result = {
        'top_5_players': top_5,
        'all_players_count': len(player_list),
        'categories_analyzed': len(categories)
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"分析完成！已保存到 {OUTPUT_FILE}")
    print(f"\n=== 2025-26赛季综合得分前五名 ===")
    for i, player in enumerate(top_5):
        print(f"\n{i+1}. {player['player']} ({player['team']}) - 总分: {player['total_score']:.1f}")
        print(f"   参与榜单数: {len(player['categories'])}")
        print(f"   主要榜单:")
        for cat in player['categories'][:5]:
            print(f"     - {cat['category']} 第{cat['rank']}名: +{cat['total']:.1f}分 (基础{cat['base_score']}+奖金{cat['bonus']})")
    
    return result

if __name__ == "__main__":
    calculate_scores()