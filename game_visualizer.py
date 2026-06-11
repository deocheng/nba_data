#!/usr/bin/env python3
"""单场比赛可视化工具 - 生成完整的比赛分析图表集"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import psycopg2
import os
import argparse

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

DB_CONFIG = {
    'dbname': 'nba',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5433'
}


class GameVisualizer:
    def __init__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()
    
    def get_game_info(self, game_id):
        """获取比赛基本信息"""
        self.cursor.execute("""
            SELECT DISTINCT team, season 
            FROM pbp_all 
            WHERE gameid = %s AND team IS NOT NULL
            LIMIT 2;
        """, (game_id,))
        teams = self.cursor.fetchall()
        
        # 获取最终比分
        self.cursor.execute("""
            SELECT MAX(h_pts) as home_score, MAX(a_pts) as visitor_score
            FROM pbp_all
            WHERE gameid = %s AND h_pts IS NOT NULL;
        """, (game_id,))
        scores = self.cursor.fetchone()
        
        return {
            'teams': teams,
            'home_score': scores[0],
            'visitor_score': scores[1],
            'game_id': game_id
        }
    
    def plot_score_flow(self, game_id, ax):
        """绘制得分走势图"""
        self.cursor.execute("""
            SELECT period, clock_seconds, h_pts, a_pts
            FROM pbp_all
            WHERE gameid = %s AND h_pts IS NOT NULL
            ORDER BY period, clock_seconds DESC;
        """, (game_id,))
        data = pd.DataFrame(self.cursor.fetchall(), columns=['period', 'time', 'home', 'away'])
        
        data['game_seconds'] = data.apply(
            lambda row: (row['period'] - 1) * 720 + (720 - row['time']), axis=1
        )
        
        ax.plot(data['game_seconds'], data['home'], label='主队', color='#E74C3C', linewidth=3)
        ax.plot(data['game_seconds'], data['away'], label='客队', color='#3498DB', linewidth=3)
        
        for period in range(1, 5):
            ax.axvline(x=period * 720, color='gray', linestyle='--', alpha=0.5)
            ax.text(period * 720 - 360, ax.get_ylim()[1] * 0.95, f'第{period}节', ha='center', fontsize=9)
        
        ax.set_title('📈 得分走势', fontsize=14, fontweight='bold')
        ax.set_xlabel('比赛时间(秒)')
        ax.set_ylabel('得分')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def plot_event_distribution(self, game_id, ax):
        """绘制事件类型分布"""
        self.cursor.execute("""
            SELECT event_type, COUNT(*) as cnt
            FROM pbp_all
            WHERE gameid = %s AND event_type IS NOT NULL
            GROUP BY event_type
            ORDER BY cnt DESC;
        """, (game_id,))
        data = pd.DataFrame(self.cursor.fetchall(), columns=['event_type', 'count'])
        
        sns.barplot(x='count', y='event_type', data=data, palette='coolwarm', ax=ax)
        ax.set_title('📊 事件类型分布', fontsize=14, fontweight='bold')
        ax.set_xlabel('次数')
        ax.set_ylabel('事件类型')
    
    def plot_shooting_by_team(self, game_id, ax):
        """绘制两队投篮对比"""
        self.cursor.execute("""
            SELECT team, 
                   SUM(CASE WHEN event_type = 'Made Shot' THEN 1 ELSE 0 END) as made,
                   SUM(CASE WHEN event_type = 'Missed Shot' THEN 1 ELSE 0 END) as missed
            FROM pbp_all
            WHERE gameid = %s AND team IS NOT NULL
            GROUP BY team;
        """, (game_id,))
        data = pd.DataFrame(self.cursor.fetchall(), columns=['team', 'made', 'missed'])
        
        data['total'] = data['made'] + data['missed']
        data['rate'] = (data['made'] / data['total'] * 100).round(1)
        
        ax.bar(data['team'], data['made'], label='命中', color='#2ECC71')
        ax.bar(data['team'], data['missed'], bottom=data['made'], label='未命中', color='#E74C3C')
        
        ax.set_title('🎯 投篮命中情况', fontsize=14, fontweight='bold')
        ax.set_ylabel('投篮次数')
        ax.legend()
        
        # 添加命中率标签
        for i, row in data.iterrows():
            ax.text(i, row['total'] + 2, f"{row['rate']}%", ha='center', fontweight='bold')
    
    def plot_period_scores(self, game_id, ax):
        """绘制各节得分"""
        self.cursor.execute("""
            SELECT period, MAX(h_pts) as home, MAX(a_pts) as away
            FROM pbp_all
            WHERE gameid = %s AND period <= 4
            GROUP BY period
            ORDER BY period;
        """, (game_id,))
        data = pd.DataFrame(self.cursor.fetchall(), columns=['period', 'home', 'away'])
        
        periods = ['第1节', '第2节', '第3节', '第4节']
        x = range(len(periods))
        
        ax.bar([i - 0.2 for i in x], data['home'], width=0.4, label='主队', color='#E74C3C')
        ax.bar([i + 0.2 for i in x], data['away'], width=0.4, label='客队', color='#3498DB')
        
        ax.set_title('⏱️ 各节得分', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(periods)
        ax.set_ylabel('得分')
        ax.legend()
    
    def plot_distance_distribution(self, game_id, ax):
        """绘制投篮距离分布"""
        self.cursor.execute("""
            SELECT dist, COUNT(*) as cnt, team
            FROM pbp_all
            WHERE gameid = %s AND dist IS NOT NULL AND dist > 0 AND event_type LIKE '%Shot%'
            GROUP BY dist, team;
        """, (game_id,))
        data = pd.DataFrame(self.cursor.fetchall(), columns=['distance', 'count', 'team'])
        
        teams = data['team'].unique()
        for team in teams:
            team_data = data[data['team'] == team]
            ax.hist(team_data['distance'], bins=10, alpha=0.6, label=team)
        
        ax.axvline(x=23.75, color='red', linestyle='--', label='三分线')
        ax.set_title('📍 投篮距离分布', fontsize=14, fontweight='bold')
        ax.set_xlabel('距离(英尺)')
        ax.set_ylabel('次数')
        ax.legend()
    
    def plot_fouls(self, game_id, ax):
        """绘制犯规次数"""
        self.cursor.execute("""
            SELECT team, COUNT(*) as cnt
            FROM pbp_all
            WHERE gameid = %s AND event_type = 'Foul' AND team IS NOT NULL
            GROUP BY team;
        """, (game_id,))
        data = pd.DataFrame(self.cursor.fetchall(), columns=['team', 'count'])
        
        sns.barplot(x='team', y='count', data=data, palette='Set2', ax=ax)
        ax.set_title('💪 犯规次数', fontsize=14, fontweight='bold')
        ax.set_ylabel('犯规次数')
    
    def visualize_game(self, game_id, output_dir=None):
        """生成完整的比赛可视化图表集"""
        if output_dir is None:
            output_dir = f'game_{game_id}'
        os.makedirs(output_dir, exist_ok=True)
        
        game_info = self.get_game_info(game_id)
        teams = [t[0] for t in game_info['teams']]
        
        print(f"🎨 正在生成比赛 {game_id} 的可视化图表...")
        print(f"   球队: {teams[0]} vs {teams[1]}")
        print(f"   比分: {game_info['home_score']} - {game_info['visitor_score']}")
        
        # 创建子图布局
        fig = plt.figure(figsize=(20, 15))
        
        # 主标题
        fig.suptitle(f'🏀 比赛分析报告 - {game_id}', fontsize=20, fontweight='bold', y=0.98)
        
        # 布局: 3行2列
        ax1 = fig.add_subplot(3, 2, 1)
        ax2 = fig.add_subplot(3, 2, 2)
        ax3 = fig.add_subplot(3, 2, 3)
        ax4 = fig.add_subplot(3, 2, 4)
        ax5 = fig.add_subplot(3, 2, 5)
        ax6 = fig.add_subplot(3, 2, 6)
        
        # 绘制各图表
        self.plot_score_flow(game_id, ax1)
        self.plot_event_distribution(game_id, ax2)
        self.plot_shooting_by_team(game_id, ax3)
        self.plot_period_scores(game_id, ax4)
        self.plot_distance_distribution(game_id, ax5)
        self.plot_fouls(game_id, ax6)
        
        plt.tight_layout()
        
        # 保存完整报告
        report_path = os.path.join(output_dir, f'game_{game_id}_report.png')
        plt.savefig(report_path, dpi=150)
        print(f"✅ 比赛报告已保存: {report_path}")
        
        # 单独保存各图表
        self.save_individual_charts(game_id, output_dir)
        
        self.conn.close()
        print(f"\n🎉 比赛 {game_id} 可视化完成！")
    
    def save_individual_charts(self, game_id, output_dir):
        """单独保存各图表"""
        # 得分走势
        plt.figure(figsize=(12, 6))
        self.cursor.execute("""
            SELECT period, clock_seconds, h_pts, a_pts
            FROM pbp_all
            WHERE gameid = %s AND h_pts IS NOT NULL
            ORDER BY period, clock_seconds DESC;
        """, (game_id,))
        data = pd.DataFrame(self.cursor.fetchall(), columns=['period', 'time', 'home', 'away'])
        data['game_seconds'] = data.apply(
            lambda row: (row['period'] - 1) * 720 + (720 - row['time']), axis=1
        )
        
        plt.plot(data['game_seconds'], data['home'], label='主队', color='#E74C3C', linewidth=3)
        plt.plot(data['game_seconds'], data['away'], label='客队', color='#3498DB', linewidth=3)
        plt.title('得分走势', fontsize=16, fontweight='bold')
        plt.xlabel('比赛时间(秒)')
        plt.ylabel('得分')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(output_dir, f'{game_id}_score_flow.png'), dpi=150)
        
        # 事件分布
        plt.figure(figsize=(10, 6))
        self.cursor.execute("""
            SELECT event_type, COUNT(*) as cnt
            FROM pbp_all
            WHERE gameid = %s AND event_type IS NOT NULL
            GROUP BY event_type
            ORDER BY cnt DESC;
        """, (game_id,))
        data = pd.DataFrame(self.cursor.fetchall(), columns=['event_type', 'count'])
        sns.barplot(x='count', y='event_type', data=data, palette='coolwarm')
        plt.title('事件类型分布', fontsize=16, fontweight='bold')
        plt.savefig(os.path.join(output_dir, f'{game_id}_events.png'), dpi=150)
        
        # 投篮对比
        plt.figure(figsize=(8, 6))
        self.cursor.execute("""
            SELECT team, 
                   SUM(CASE WHEN event_type = 'Made Shot' THEN 1 ELSE 0 END) as made,
                   SUM(CASE WHEN event_type = 'Missed Shot' THEN 1 ELSE 0 END) as missed
            FROM pbp_all
            WHERE gameid = %s AND team IS NOT NULL
            GROUP BY team;
        """, (game_id,))
        data = pd.DataFrame(self.cursor.fetchall(), columns=['team', 'made', 'missed'])
        plt.bar(data['team'], data['made'], label='命中', color='#2ECC71')
        plt.bar(data['team'], data['missed'], bottom=data['made'], label='未命中', color='#E74C3C')
        plt.title('投篮命中情况', fontsize=16, fontweight='bold')
        plt.legend()
        plt.savefig(os.path.join(output_dir, f'{game_id}_shooting.png'), dpi=150)


def main():
    parser = argparse.ArgumentParser(description='单场比赛可视化工具')
    parser.add_argument('game_id', type=int, help='比赛ID')
    parser.add_argument('-o', '--output', help='输出目录')
    args = parser.parse_args()
    
    visualizer = GameVisualizer()
    visualizer.visualize_game(args.game_id, args.output)


if __name__ == '__main__':
    main()
