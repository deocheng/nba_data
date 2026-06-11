import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

import numpy as np
from pathlib import Path
from matplotlib.backends.backend_pdf import PdfPages

BASE_DIR = Path(__file__).parent
CSV_FILE = BASE_DIR / "CSV_Clean" / "league_leaders_parsed.csv"
OUTPUT_DIR = BASE_DIR / "static" / "charts"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CHART_TYPES = [
    'bar',       # 柱状图
    'barh',      # 水平柱状图
    'line',      # 折线图
    'scatter',   # 散点图
    'pie',       # 饼图
    'hist',      # 直方图
    'box',       # 箱线图
]

def generate_chart(chart_type, data, category, output_path):
    plt.figure(figsize=(12, 8))
    
    players = data['player'].tolist()[:10]
    values = data['value'].tolist()[:10]
    teams = data['team'].tolist()[:10]
    
    colors = plt.cm.viridis(np.linspace(0, 0.9, len(players)))
    
    if chart_type == 'bar':
        plt.bar(players, values, color=colors)
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.title(f'{category} - Bar Chart', fontsize=14, fontweight='bold')
    
    elif chart_type == 'barh':
        y_pos = np.arange(len(players))
        plt.barh(y_pos, values, color=colors)
        plt.yticks(y_pos, [f'{p} ({t})' for p, t in zip(players, teams)])
        plt.gca().invert_yaxis()
        plt.title(f'{category} - Horizontal Bar Chart', fontsize=14, fontweight='bold')
    
    elif chart_type == 'line':
        plt.plot(players, values, marker='o', linestyle='-', linewidth=2, markersize=8, color='#e94560')
        plt.xticks(rotation=45, ha='right', fontsize=10)
        for i, (p, v) in enumerate(zip(players, values)):
            plt.text(i, v + max(values) * 0.02, f'{v:.1f}', ha='center', fontsize=9)
        plt.title(f'{category} - Line Chart', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
    
    elif chart_type == 'scatter':
        x = np.arange(len(players))
        sizes = [v / max(values) * 300 for v in values]
        plt.scatter(x, values, s=sizes, c=colors, alpha=0.7, edgecolors='white', linewidth=2)
        plt.xticks(x, [f'{p} ({t})' for p, t in zip(players, teams)], rotation=45, ha='right', fontsize=9)
        plt.title(f'{category} - Scatter Chart', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
    
    elif chart_type == 'pie':
        plt.pie(values, labels=[f'{p}\n({v})' for p, v in zip(players, values)], 
                colors=colors, autopct='%1.1f%%', startangle=90)
        plt.title(f'{category} - Pie Chart', fontsize=14, fontweight='bold')
        plt.axis('equal')
    
    elif chart_type == 'hist':
        plt.hist(values, bins=10, color='#e94560', edgecolor='white', alpha=0.7)
        plt.title(f'{category} - Histogram', fontsize=14, fontweight='bold')
        plt.xlabel('Value')
        plt.ylabel('Frequency')
        plt.grid(True, alpha=0.3)
    
    elif chart_type == 'box':
        plt.boxplot(values, vert=False, patch_artist=True, 
                    boxprops={'facecolor': '#e94560', 'alpha': 0.7})
        plt.title(f'{category} - Box Plot', fontsize=14, fontweight='bold')
        plt.yticks([1], [category])
        plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

def generate_all_chart_types():
    df = pd.read_csv(CSV_FILE)
    df_2025 = df[df['season'] == '2025-26'].copy()
    
    top_categories = ['Points', 'Points Per Game', 'Assists', 'Assists Per Game', 
                      'Total Rebounds', 'Rebounds Per Game', 'Blocks', 'Blocks Per Game']
    
    print(f"生成 {len(CHART_TYPES)} 种图表类型，每种类型包含 {len(top_categories)} 个统计类别...")
    
    pdf_output = OUTPUT_DIR / "all_chart_types_demo.pdf"
    with PdfPages(pdf_output) as pdf:
        for chart_type in CHART_TYPES:
            for category in top_categories[:5]:
                cat_data = df_2025[df_2025['category'] == category].sort_values('rank').head(10)
                
                if cat_data.empty:
                    continue
                
                plt.figure(figsize=(10, 6))
                
                players = cat_data['player'].tolist()[:10]
                values = cat_data['value'].tolist()[:10]
                teams = cat_data['team'].tolist()[:10]
                
                colors = plt.cm.viridis(np.linspace(0, 0.9, len(players)))
                
                if chart_type == 'bar':
                    plt.bar(players, values, color=colors)
                    plt.xticks(rotation=45, ha='right', fontsize=8)
                
                elif chart_type == 'barh':
                    y_pos = np.arange(len(players))
                    plt.barh(y_pos, values, color=colors)
                    plt.yticks(y_pos, [f'{p} ({t})' for p, t in zip(players, teams)], fontsize=8)
                    plt.gca().invert_yaxis()
                
                elif chart_type == 'line':
                    plt.plot(players, values, marker='o', linestyle='-', linewidth=2, markersize=6, color='#e94560')
                    plt.xticks(rotation=45, ha='right', fontsize=8)
                
                elif chart_type == 'scatter':
                    x = np.arange(len(players))
                    sizes = [v / max(values) * 200 for v in values]
                    plt.scatter(x, values, s=sizes, c=colors, alpha=0.7)
                    plt.xticks(x, [p.split()[0] for p in players], fontsize=8)
                
                elif chart_type == 'pie':
                    plt.pie(values, labels=[p.split()[0] for p in players], 
                            colors=colors, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 8})
                    plt.axis('equal')
                
                elif chart_type == 'hist':
                    plt.hist(values, bins=8, color='#e94560', edgecolor='white', alpha=0.7)
                
                elif chart_type == 'box':
                    plt.boxplot(values, vert=False, patch_artist=True, 
                                boxprops={'facecolor': '#e94560', 'alpha': 0.7})
                    plt.yticks([1], [category.split()[0]])
                
                plt.title(f'{chart_type.capitalize()} Chart - {category}', fontsize=12, fontweight='bold')
                plt.tight_layout()
                
                pdf.savefig(bbox_inches='tight', dpi=100)
                plt.close()
    
    print(f"\n✅ 图表类型演示PDF已保存到: {pdf_output}")
    
    chart_info = []
    for chart_type in CHART_TYPES:
        chart_info.append({
            'type': chart_type,
            'description': {
                'bar': '柱状图 - 展示各类别数据的对比',
                'barh': '水平柱状图 - 适合标签较长的场景',
                'line': '折线图 - 展示数据趋势变化',
                'scatter': '散点图 - 展示数据分布和相关性',
                'pie': '饼图 - 展示各部分占比关系',
                'hist': '直方图 - 展示数据分布频率',
                'box': '箱线图 - 展示数据分布统计特征'
            }[chart_type],
            'use_case': {
                'bar': '比较不同球员的数据',
                'barh': '球员姓名较长时使用',
                'line': '展示排名变化趋势',
                'scatter': '展示数据分布和异常值',
                'pie': '展示球员贡献占比',
                'hist': '分析数据分布特征',
                'box': '比较多组数据的分布'
            }[chart_type]
        })
    
    info_file = OUTPUT_DIR / "chart_types_info.json"
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(chart_info, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 图表类型说明已保存到: {info_file}")
    
    return CHART_TYPES

if __name__ == "__main__":
    import json
    chart_types = generate_all_chart_types()
    
    print("\n=== 可用图表类型 ===")
    for i, chart_type in enumerate(chart_types, 1):
        print(f"{i}. {chart_type}")
    
    print("\n=== 图表类型说明 ===")
    descriptions = {
        'bar': '柱状图 - 最常用的图表类型，适合比较不同类别的数据',
        'barh': '水平柱状图 - 当标签较长时更合适',
        'line': '折线图 - 展示数据的变化趋势',
        'scatter': '散点图 - 展示数据点的分布和相关性',
        'pie': '饼图 - 展示各部分占总体的比例',
        'hist': '直方图 - 展示数据的频率分布',
        'box': '箱线图 - 展示数据的统计分布特征'
    }
    
    for chart_type in chart_types:
        print(f"• {descriptions[chart_type]}")