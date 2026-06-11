#!/usr/bin/env python3
"""NBA数据可视化工具 - 美观的图表展示"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import psycopg2
import os
from datetime import datetime

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

DB_CONFIG = {
    'dbname': 'nba',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5433'
}


class NBAVisualizer:
    def __init__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()
        
    def get_team_color(self, team):
        """获取球队主色调"""
        team_colors = {
            'LAL': ('#552583', '#FDB927'),
            'GSW': ('#1D428A', '#FFC72C'),
            'SAS': ('#C4CED4', '#000000'),
            'OKC': ('#007AC1', '#EF3B24'),
            'HOU': ('#CE1141', '#000000'),
            'DAL': ('#00538C', '#B8C4CA'),
            'BOS': ('#007A33', '#C8102E'),
            'MIA': ('#98002E', '#F9A01B'),
            'CHI': ('#CE1141', '#000000'),
            'NYK': ('#006BB6', '#F58426'),
            'PHI': ('#006BB6', '#ED174C'),
            'TOR': ('#CE1141', '#000000'),
            'MIL': ('#00471B', '#EEE1C6'),
            'DEN': ('#0E2240', '#FEC524'),
            'PHO': ('#1D1160', '#E56020'),
            'default': ('#636E72', '#2D3436')
        }
        return team_colors.get(team.upper(), team_colors['default'])
    
    def plot_season_distribution(self, output_path='season_dist.png'):
        """绘制赛季分布饼图"""
        self.cursor.execute("""
            SELECT season, COUNT(DISTINCT gameid) as game_count
            FROM pbp_all
            GROUP BY season
            ORDER BY season;
        """)
        data = pd.DataFrame(self.cursor.fetchall(), columns=['season', 'games'])
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 创建漂亮的颜色映射
        colors = plt.cm.tab20c(range(len(data)))
        
        wedges, texts, autotexts = ax.pie(
            data['games'], 
            labels=data['season'],
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            wedgeprops={'edgecolor': 'white', 'linewidth': 2},
            textprops={'fontsize': 10}
        )
        
        ax.set_title('🏀 NBA比赛赛季分布 (1997-2026)', fontsize=18, fontweight='bold', pad=20)
        
        # 添加图例
        plt.legend(wedges, data['season'], loc='center left', bbox_to_anchor=(1, 0.5), title='赛季')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✅ 赛季分布图已保存: {output_path}")
    
    def plot_event_type_distribution(self, output_path='event_type.png'):
        """绘制事件类型分布图"""
        self.cursor.execute("""
            SELECT event_type, COUNT(*) as cnt
            FROM pbp_all
            WHERE event_type IS NOT NULL
            GROUP BY event_type
            ORDER BY cnt DESC
            LIMIT 10;
        """)
        data = pd.DataFrame(self.cursor.fetchall(), columns=['event_type', 'count'])
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        colors = sns.color_palette('coolwarm', len(data))
        bars = ax.barh(data['event_type'], data['count'], color=colors)
        
        ax.set_title('🔥 事件类型分布统计', fontsize=18, fontweight='bold', pad=20)
        ax.set_xlabel('事件数量', fontsize=12)
        ax.set_ylabel('事件类型', fontsize=12)
        
        # 添加数值标签
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 5000, bar.get_y() + bar.get_height()/2,
                    f'{width:,}', va='center', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        print(f"✅ 事件类型分布图已保存: {output_path}")
    
    def plot_shooting_distance(self, output_path='shooting_dist.png'):
        """绘制投篮距离分布图"""
        self.cursor.execute("""
            SELECT dist, COUNT(*) as cnt
            FROM pbp_all
            WHERE dist IS NOT NULL AND dist > 0 AND event_type LIKE '%Shot%'
            GROUP BY dist
            ORDER BY dist;
        """)
        data = pd.DataFrame(self.cursor.fetchall(), columns=['distance', 'count'])
        
        fig, ax = plt.subplots(figsize=(14, 7))
        
        # 创建颜色渐变
        norm = plt.Normalize(data['distance'].min(), data['distance'].max())
        colors = plt.cm.plasma(norm(data['distance']))
        
        bars = ax.bar(data['distance'], data['count'], color=colors, edgecolor='white')
        
        ax.set_title('🎯 投篮距离分布', fontsize=18, fontweight='bold', pad=20)
        ax.set_xlabel('距离 (英尺)', fontsize=12)
        ax.set_ylabel('投篮次数', fontsize=12)
        
        # 添加三分线标记
        ax.axvline(x=23.75, color='#E74C3C', linestyle='--', label='三分线 (23.75英尺)')
        ax.legend()
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        print(f"✅ 投篮距离分布图已保存: {output_path}")
    
    def plot_score_distribution(self, output_path='score_dist.png'):
        """绘制比分分布热力图"""
        self.cursor.execute("""
            SELECT home_score, visitor_score, COUNT(*) as cnt
            FROM (
                SELECT gameid, MAX(h_pts) as home_score, MAX(a_pts) as visitor_score
                FROM pbp_all
                WHERE h_pts IS NOT NULL AND a_pts IS NOT NULL
                GROUP BY gameid
            ) t
            WHERE home_score BETWEEN 80 AND 150 AND visitor_score BETWEEN 80 AND 150
            GROUP BY home_score, visitor_score
            ORDER BY cnt DESC
            LIMIT 200;
        """)
        data = pd.DataFrame(self.cursor.fetchall(), columns=['home', 'away', 'count'])
        
        pivot = data.pivot(index='home', columns='away', values='count').fillna(0)
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        sns.heatmap(pivot, cmap='viridis', annot=False, 
                    cbar_kws={'label': '比赛次数'},
                    ax=ax)
        
        ax.set_title('📊 比赛比分分布热力图', fontsize=18, fontweight='bold', pad=20)
        ax.set_xlabel('客队得分', fontsize=12)
        ax.set_ylabel('主队得分', fontsize=12)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        print(f"✅ 比分热力图已保存: {output_path}")
    
    def plot_team_comparison(self, teams=['SAS', 'LAL', 'GSW'], output_path='team_compare.png'):
        """绘制球队数据对比图"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        colors = ['#E74C3C', '#3498DB', '#2ECC71', '#F39C12']
        
        # 1. 投篮次数对比
        for i, team in enumerate(teams):
            self.cursor.execute("""
                SELECT season, COUNT(*) as shots
                FROM pbp_all
                WHERE team = %s AND event_type LIKE '%Shot%'
                GROUP BY season
                ORDER BY season;
            """, (team,))
            data = pd.DataFrame(self.cursor.fetchall(), columns=['season', 'shots'])
            if len(data) > 0:
                axes[0, 0].plot(data['season'], data['shots'], marker='o', label=team, 
                               linewidth=2, color=colors[i])
        
        axes[0, 0].set_title('🏀 球队投篮次数对比', fontsize=14, fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. 命中次数对比
        for i, team in enumerate(teams):
            self.cursor.execute("""
                SELECT season, COUNT(*) as made
                FROM pbp_all
                WHERE team = %s AND event_type = 'Made Shot'
                GROUP BY season
                ORDER BY season;
            """, (team,))
            data = pd.DataFrame(self.cursor.fetchall(), columns=['season', 'made'])
            if len(data) > 0:
                axes[0, 1].plot(data['season'], data['made'], marker='s', label=team, 
                               linewidth=2, color=colors[i])
        
        axes[0, 1].set_title('🎯 球队命中次数对比', fontsize=14, fontweight='bold')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. 犯规次数对比
        for i, team in enumerate(teams):
            self.cursor.execute("""
                SELECT season, COUNT(*) as fouls
                FROM pbp_all
                WHERE team = %s AND event_type = 'Foul'
                GROUP BY season
                ORDER BY season;
            """, (team,))
            data = pd.DataFrame(self.cursor.fetchall(), columns=['season', 'fouls'])
            if len(data) > 0:
                axes[1, 0].plot(data['season'], data['fouls'], marker='^', label=team, 
                               linewidth=2, color=colors[i])
        
        axes[1, 0].set_title('💪 球队犯规次数对比', fontsize=14, fontweight='bold')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. 失误次数对比
        for i, team in enumerate(teams):
            self.cursor.execute("""
                SELECT season, COUNT(*) as tos
                FROM pbp_all
                WHERE team = %s AND event_type = 'Turnover'
                GROUP BY season
                ORDER BY season;
            """, (team,))
            data = pd.DataFrame(self.cursor.fetchall(), columns=['season', 'tos'])
            if len(data) > 0:
                axes[1, 1].plot(data['season'], data['tos'], marker='D', label=team, 
                               linewidth=2, color=colors[i])
        
        axes[1, 1].set_title('❌ 球队失误次数对比', fontsize=14, fontweight='bold')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        print(f"✅ 球队对比图已保存: {output_path}")
    
    def plot_game_flow(self, game_id, output_path='game_flow.png'):
        """绘制单场比赛得分走势图"""
        self.cursor.execute("""
            SELECT period, clock_seconds, h_pts, a_pts, description
            FROM pbp_all
            WHERE gameid = %s AND h_pts IS NOT NULL
            ORDER BY period, clock_seconds DESC;
        """, (game_id,))
        data = pd.DataFrame(self.cursor.fetchall(), columns=['period', 'time', 'home', 'away', 'desc'])
        
        # 转换时间为比赛秒数（从开始算起）
        data['game_seconds'] = data.apply(
            lambda row: (row['period'] - 1) * 720 + (720 - row['time']), axis=1
        )
        
        fig, ax = plt.subplots(figsize=(14, 7))
        
        ax.plot(data['game_seconds'], data['home'], label='主队', color='#E74C3C', linewidth=3)
        ax.plot(data['game_seconds'], data['away'], label='客队', color='#3498DB', linewidth=3)
        
        # 添加节次分隔线
        for period in range(1, 5):
            ax.axvline(x=period * 720, color='gray', linestyle='--', alpha=0.5)
            ax.text(period * 720 - 360, ax.get_ylim()[1] * 0.95, 
                    f'第{period}节', ha='center', fontsize=10)
        
        ax.set_title(f'📈 比赛 {game_id} 得分走势', fontsize=18, fontweight='bold', pad=20)
        ax.set_xlabel('比赛时间 (秒)', fontsize=12)
        ax.set_ylabel('得分', fontsize=12)
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        print(f"✅ 比赛走势图已保存: {output_path}")
    
    def create_dashboard(self):
        """创建完整的数据仪表盘"""
        print("🎨 正在创建数据可视化仪表盘...")
        
        # 创建输出目录
        os.makedirs('visualizations', exist_ok=True)
        
        # 生成各种图表
        self.plot_season_distribution('visualizations/season_dist.png')
        self.plot_event_type_distribution('visualizations/event_type.png')
        self.plot_shooting_distance('visualizations/shooting_dist.png')
        self.plot_score_distribution('visualizations/score_dist.png')
        self.plot_team_comparison(['SAS', 'LAL', 'GSW'], 'visualizations/team_compare.png')
        
        # 示例比赛走势
        self.cursor.execute("SELECT DISTINCT gameid FROM pbp_all WHERE season = 2026 LIMIT 1;")
        sample_game = self.cursor.fetchone()
        if sample_game:
            self.plot_game_flow(sample_game[0], 'visualizations/game_flow.png')
        
        self.conn.close()
        print("\n🎉 仪表盘创建完成！所有图表已保存到 visualizations/ 目录")


if __name__ == '__main__':
    visualizer = NBAVisualizer()
    visualizer.create_dashboard()
