import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

import re
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
EXCEL_FILE = BASE_DIR / "CSV" / "league leaders 1955-2026 .xlsx"
OUTPUT_DIR = BASE_DIR / "static" / "charts"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_player_data(text):
    """解析格式: '1.Luka Dončić • LAL2143'"""
    pattern = r'^(\d+)\.(.+?)\s*•\s*([A-Z]{2,3})([\d.]+)$'
    match = re.match(pattern, text.strip())
    
    if match:
        rank = int(match.group(1))
        player = match.group(2).strip()
        team = match.group(3).strip()
        value = float(match.group(4))
        
        return {
            'rank': rank,
            'player': player,
            'team': team,
            'value': value
        }
    return None


def parse_excel():
    print(f"读取 Excel 文件: {EXCEL_FILE}")
    xls = pd.ExcelFile(EXCEL_FILE)
    print(f"找到 {len(xls.sheet_names)} 个工作表")
    
    all_data = []
    
    for sheet_name in xls.sheet_names:
        print(f"处理工作表: {sheet_name}")
        df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
        
        if df.empty or len(df.columns) == 0:
            continue
        
        season = sheet_name
        current_category = None
        
        for idx, row in df.iterrows():
            cell_value = str(row[0]) if pd.notna(row[0]) else ''
            
            if 'View all players' in cell_value or 'League Leaders' in cell_value:
                continue
            
            if not cell_value.strip().startswith(tuple('0123456789')):
                if cell_value.strip() and len(cell_value.strip()) > 2:
                    current_category = cell_value.strip()
                continue
            
            if current_category:
                parsed = parse_player_data(cell_value)
                
                if parsed:
                    all_data.append({
                        'season': season,
                        'category': current_category,
                        'rank': parsed['rank'],
                        'player': parsed['player'],
                        'team': parsed['team'],
                        'value': parsed['value']
                    })
    
    return pd.DataFrame(all_data)


def create_charts(df, season='2025-26'):
    print(f"\n为赛季 {season} 创建图表...")
    
    season_data = df[df['season'] == season]
    
    if season_data.empty:
        print(f"没有找到 {season} 赛季的数据")
        return
    
    categories = season_data['category'].unique()
    print(f"找到 {len(categories)} 个统计类别")
    
    charts_data = []
    
    for category in categories[:15]:
        cat_data = season_data[season_data['category'] == category].head(20)
        
        if cat_data.empty or len(cat_data) < 5:
            continue
        
        fig, ax = plt.subplots(figsize=(14, 10))
        
        players = cat_data['player'].tolist()
        values = cat_data['value'].tolist()
        teams = cat_data['team'].tolist()
        
        colors = plt.cm.viridis([i/len(players) for i in range(len(players))])
        
        bars = ax.barh(range(len(players)), values, color=colors)
        
        ax.set_yticks(range(len(players)))
        ax.set_yticklabels([f'{p} ({t})' for p, t in zip(players, teams)])
        ax.invert_yaxis()
        
        ax.set_xlabel('数值', fontsize=12)
        ax.set_title(f'{season} 赛季 {category} 前20名', fontsize=16, fontweight='bold')
        
        for i, (bar, val) in enumerate(zip(bars, values)):
            ax.text(val + max(values) * 0.02, i, f'{val:.1f}', va='center', fontsize=10)
        
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        chart_file = OUTPUT_DIR / f"{season}_{category.replace(' ', '_').replace('/', '_').replace('%', 'pct')}.png"
        plt.savefig(chart_file, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"  保存图表: {chart_file.name}")
        
        charts_data.append({
            'category': category,
            'chart_url': f'/static/charts/{chart_file.name}',
            'top_players': players[:5],
            'top_values': values[:5],
            'top_teams': teams[:5]
        })
    
    json_output = OUTPUT_DIR / f'{season}_charts_data.json'
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(charts_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n图表数据已保存到 {json_output}")
    
    return charts_data


def main():
    df = parse_excel()
    
    if df.empty:
        print("没有解析到数据")
        return
    
    csv_output = BASE_DIR / "CSV_Clean" / "league_leaders_parsed.csv"
    df.to_csv(csv_output, index=False, encoding='utf-8-sig')
    print(f"\n数据已保存到 {csv_output}")
    print(f"共 {len(df)} 条记录")
    
    print(f"\n统计类别数量: {len(df['category'].unique())}")
    print(f"赛季数量: {len(df['season'].unique())}")
    
    seasons = sorted(df['season'].unique())
    print(f"\n可用赛季: {seasons[-5:]}")
    
    latest_season = seasons[-1]
    charts_data = create_charts(df, latest_season)
    
    return df, charts_data


if __name__ == "__main__":
    main()