#!/usr/bin/env python3
"""单场比赛可视化工具 - 简化版"""
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
            SELECT DISTINCT team FROM pbp_all 
            WHERE gameid = %s AND team IS NOT NULL LIMIT 2;
        """, (game_id,))
        teams = [t[0] for t in self.cursor.fetchall()]
        
        self.cursor.execute("""
            SELECT MAX(h_pts), MAX(a_pts) FROM pbp_all
            WHERE gameid = %s AND h_pts IS NOT NULL;
        """, (game_id,))
        scores = self.cursor.fetchone()
        
        return {
            'teams': teams,
            'home_score': scores[0],
            'visitor_score': scores[1],
            'game_id': game_id
        }
    
    def visualize_game(self, game_id, output_dir=None):
        """生成比赛可视化图表"""
        if output_dir is None:
            output_dir = f'game_{game_id}'
        os.makedirs(output_dir, exist_ok=True)
        
        game_info = self.get_game_info(game_id)
        print(f"🎨 生成比赛 {game_id} 的可视化图表...")
        print(f"   球队: {' vs '.join(game_info['teams'])}")
        print(f"   比分: {game_info['home_score']} - {game_info['visitor_score']}")
        
        # 创建布局
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'🏀 比赛分析 - {game_id}', fontsize=20, fontweight='bold', y=0.98)
        
        # 1. 得分走势
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
        
        axes[0, 0].plot(data['game_seconds'], data['home'], label='主队', color='#E74C3C', linewidth=3)
        axes[0, 0].plot(data['game_seconds'], data['away'], label='客队', color='#3498DB', linewidth=3)
        for period in range(1, 5):
            axes[0, 0].axvline(x=period * 720, color='gray', linestyle='--', alpha=0.5)
        axes[0, 0].set_title('📈 得分走势', fontsize=14, fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. 事件分布
        self.cursor.execute("""
            SELECT event_type, COUNT(*) as cnt
            FROM pbp_all
            WHERE gameid = %s AND event_type IS NOT NULL
            GROUP BY event_type ORDER BY cnt DESC;
        """, (game_id,))
        data = pd.DataFrame(self.cursor.fetchall(), columns=['event_type', 'count'])
        sns.barplot(data=data, x='count', y='event_type', palette='coolwarm', ax=axes[0, 1])
        axes[0, 1].set_title('📊 事件类型分布', fontsize=14, fontweight='bold')
        
        # 3. 投篮对比
        self.cursor.execute("""
            SELECT team, 
                   SUM(CASE WHEN event_type = 'Made Shot' THEN 1 ELSE 0 END) as made,
                   SUM(CASE WHEN event_type = 'Missed Shot' THEN 1 ELSE 0 END) as missed
            FROM pbp_all
            WHERE gameid = %s AND team IS NOT NULL GROUP BY team;
        """, (game_id,))
        data = pd.DataFrame(self.cursor.fetchall(), columns=['team', 'made', 'missed'])
        axes[1, 0].bar(data['team'], data['made'], label='命中', color='#2ECC71')
        axes[1, 0].bar(data['team'], data['missed'], bottom=data['made'], label='未命中', color='#E74C3C')
        axes[1, 0].set_title('🎯 投篮命中情况', fontsize=14, fontweight='bold')
        axes[1, 0].legend()
        
        # 4. 各节得分
        self.cursor.execute("""
            SELECT period, MAX(h_pts) as home, MAX(a_pts) as away
            FROM pbp_all
            WHERE gameid = %s AND period <= 4 GROUP BY period ORDER BY period;
        """, (game_id,))
        data = pd.DataFrame(self.cursor.fetchall(), columns=['period', 'home', 'away'])
        if len(data) == 4:
            axes[1, 1].bar([0.8, 1.8, 2.8, 3.8], data['home'], width=0.4, label='主队', color='#E74C3C')
            axes[1, 1].bar([1.2, 2.2, 3.2, 4.2], data['away'], width=0.4, label='客队', color='#3498DB')
            axes[1, 1].set_xticks([1, 2, 3, 4])
            axes[1, 1].set_xticklabels(['第1节', '第2节', '第3节', '第4节'])
        axes[1, 1].set_title('⏱️ 各节得分', fontsize=14, fontweight='bold')
        axes[1, 1].legend()
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'game_{game_id}_report.png'), dpi=150)
        print(f"✅ 比赛报告已保存")
        
        # 单独保存得分走势图
        self.cursor.execute("""
            SELECT period, clock_seconds, h_pts, a_pts
            FROM pbp_all
            WHERE gameid = %s AND h_pts IS NOT NULL
            ORDER BY period, clock_seconds DESC;
        """, (game_id,))
        score_data = pd.DataFrame(self.cursor.fetchall(), columns=['period', 'time', 'home', 'away'])
        score_data['game_seconds'] = score_data.apply(
            lambda row: (row['period'] - 1) * 720 + (720 - row['time']), axis=1
        )
        
        plt.figure(figsize=(14, 7))
        plt.plot(score_data['game_seconds'], score_data['home'], label='主队', color='#E74C3C', linewidth=3)
        plt.plot(score_data['game_seconds'], score_data['away'], label='客队', color='#3498DB', linewidth=3)
        plt.title(f'比赛 {game_id} 得分走势', fontsize=18, fontweight='bold')
        plt.xlabel('比赛时间(秒)')
        plt.ylabel('得分')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(output_dir, f'{game_id}_score_flow.png'), dpi=150)
        print(f"✅ 得分走势图已保存")
        
        self.conn.close()
        print(f"\n🎉 比赛 {game_id} 可视化完成！")


def main():
    parser = argparse.ArgumentParser(description='单场比赛可视化工具')
    parser.add_argument('game_id', type=int, help='比赛ID')
    parser.add_argument('-o', '--output', help='输出目录')
    args = parser.parse_args()
    
    visualizer = GameVisualizer()
    visualizer.visualize_game(args.game_id, args.output)


if __name__ == '__main__':
    main()
