#!/usr/bin/env python3
"""NBA数据可视化工具 - 简化版"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import psycopg2
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

DB_CONFIG = {
    'dbname': 'nba',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5433'
}


def create_visualizations():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    os.makedirs('visualizations', exist_ok=True)
    
    print("🎨 创建可视化图表...")
    
    # 1. 赛季分布饼图
    cursor.execute("""
        SELECT season, COUNT(DISTINCT gameid) as game_count
        FROM pbp_all
        GROUP BY season
        ORDER BY season;
    """)
    data = pd.DataFrame(cursor.fetchall(), columns=['season', 'games'])
    
    plt.figure(figsize=(12, 8))
    colors = plt.cm.Set3(range(len(data)))
    plt.pie(data['games'], labels=data['season'], colors=colors,
            autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'white'})
    plt.title('NBA比赛赛季分布 (1997-2026)', fontsize=16, fontweight='bold')
    plt.savefig('visualizations/season_dist.png', dpi=150, bbox_inches='tight')
    print("✅ 赛季分布图")
    
    # 2. 事件类型分布
    cursor.execute("""
        SELECT event_type, COUNT(*) as cnt
        FROM pbp_all
        WHERE event_type IS NOT NULL
        GROUP BY event_type
        ORDER BY cnt DESC
        LIMIT 10;
    """)
    data = pd.DataFrame(cursor.fetchall(), columns=['event_type', 'count'])
    
    plt.figure(figsize=(12, 7))
    sns.barplot(x='count', y='event_type', data=data, palette='coolwarm')
    plt.title('事件类型分布统计', fontsize=16, fontweight='bold')
    plt.xlabel('事件数量')
    plt.ylabel('事件类型')
    plt.savefig('visualizations/event_type.png', dpi=150)
    print("✅ 事件类型分布图")
    
    # 3. 投篮距离分布
    cursor.execute("""
        SELECT dist, COUNT(*) as cnt
        FROM pbp_all
        WHERE dist IS NOT NULL AND dist > 0 AND event_type LIKE '%Shot%'
        GROUP BY dist
        ORDER BY dist;
    """)
    data = pd.DataFrame(cursor.fetchall(), columns=['distance', 'count'])
    
    plt.figure(figsize=(14, 7))
    plt.bar(data['distance'], data['count'], color='skyblue', edgecolor='white')
    plt.axvline(x=23.75, color='red', linestyle='--', label='三分线')
    plt.title('投篮距离分布', fontsize=16, fontweight='bold')
    plt.xlabel('距离 (英尺)')
    plt.ylabel('投篮次数')
    plt.legend()
    plt.savefig('visualizations/shooting_dist.png', dpi=150)
    print("✅ 投篮距离分布图")
    
    # 4. 比赛数量趋势
    cursor.execute("""
        SELECT season, COUNT(DISTINCT gameid) as cnt
        FROM pbp_all
        GROUP BY season
        ORDER BY season;
    """)
    data = pd.DataFrame(cursor.fetchall(), columns=['season', 'games'])
    
    plt.figure(figsize=(14, 7))
    plt.plot(data['season'], data['games'], marker='o', linewidth=3, color='#3498DB')
    plt.title('历年比赛数量趋势', fontsize=16, fontweight='bold')
    plt.xlabel('赛季')
    plt.ylabel('比赛场次')
    plt.grid(True, alpha=0.3)
    plt.savefig('visualizations/game_trend.png', dpi=150)
    print("✅ 比赛数量趋势图")
    
    # 5. 球队统计对比
    cursor.execute("""
        SELECT team, COUNT(*) as events
        FROM pbp_all
        WHERE team IS NOT NULL
        GROUP BY team
        ORDER BY events DESC
        LIMIT 15;
    """)
    data = pd.DataFrame(cursor.fetchall(), columns=['team', 'events'])
    
    plt.figure(figsize=(12, 7))
    sns.barplot(x='events', y='team', data=data, palette='viridis')
    plt.title('球队事件数量排名', fontsize=16, fontweight='bold')
    plt.xlabel('事件数量')
    plt.ylabel('球队')
    plt.savefig('visualizations/team_events.png', dpi=150)
    print("✅ 球队事件排名图")
    
    conn.close()
    print("\n🎉 所有图表已保存到 visualizations/ 目录")


if __name__ == '__main__':
    create_visualizations()
