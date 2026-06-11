import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
matplotlib.use('pdf')
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

import re
from pathlib import Path
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

BASE_DIR = Path(__file__).parent
CSV_FILE = BASE_DIR / "CSV_Clean" / "league_leaders_parsed.csv"
OUTPUT_DIR = BASE_DIR / "static" / "charts"
PDF_OUTPUT = OUTPUT_DIR / "nba_league_leaders_2025-26_all_charts.pdf"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

def get_real_categories(df):
    real_categories = []
    for cat in df['category'].unique():
        is_real = any(stat.lower() in cat.lower() for stat in KNOWN_STATS)
        has_player_name = bool(re.search(r'[A-Z][a-z]+\s+[A-Z][a-z]+.*[A-Z]{2,3}\d', cat))
        if is_real and not has_player_name:
            real_categories.append(cat)
    return sorted(real_categories)

def generate_all_charts_pdf():
    print("读取数据...")
    df = pd.read_csv(CSV_FILE)
    df_2025 = df[df['season'] == '2025-26'].copy()
    
    categories = get_real_categories(df_2025)
    print(f"找到 {len(categories)} 个统计类别")
    
    print(f"\n开始生成 PDF，保存到: {PDF_OUTPUT}")
    
    with PdfPages(PDF_OUTPUT) as pdf:
        for i, category in enumerate(categories):
            print(f"生成图表 {i+1}/{len(categories)}: {category}")
            
            cat_data = df_2025[df_2025['category'] == category].sort_values('rank').head(10)
            
            if cat_data.empty or len(cat_data) < 3:
                continue
            
            fig, ax = plt.subplots(figsize=(11.69, 8.27))
            
            players = cat_data['player'].tolist()
            values = cat_data['value'].tolist()
            teams = cat_data['team'].tolist()
            
            colors = plt.cm.plasma(np.linspace(0, 0.9, len(players)))
            
            bars = ax.barh(range(len(players)), values, color=colors)
            
            ax.set_yticks(range(len(players)))
            ax.set_yticklabels([f'{p} ({t})' for p, t in zip(players, teams)], fontsize=9)
            ax.invert_yaxis()
            
            ax.set_xlabel('Value', fontsize=11)
            ax.set_title(f'NBA League Leaders 2025-26\n{category}', fontsize=14, fontweight='bold')
            
            for j, (bar, val) in enumerate(zip(bars, values)):
                ax.text(val + max(values) * 0.02, j, f'{val:.1f}', va='center', fontsize=10)
            
            ax.grid(axis='x', alpha=0.3, linestyle='--')
            
            plt.tight_layout()
            
            pdf.savefig(fig, bbox_inches='tight', dpi=100)
            plt.close(fig)
    
    print(f"\n✅ PDF已成功保存到: {PDF_OUTPUT}")
    print(f"📊 总共生成了 {len(categories)} 个图表")
    
    return len(categories)

if __name__ == "__main__":
    total = generate_all_charts_pdf()
    print(f"\n统计：")
    print(f"  - 可生成的图表种类: {total} 种")
    print(f"  - PDF文件: {PDF_OUTPUT.name}")