"""
球员最佳出场时长分析工具 - 改进版

分析逻辑：
1. 从PBP数据中提取球员出场时间和休息时间
2. 分析每节出场时长模式
3. 计算球员效率与出场时长的关系
4. 确定球员的最佳出场时长范围

科学方法：
- 分段分析（每5分钟为一个区间）
- 效率趋势分析
- 疲劳效应评估
- 最佳区间确定
"""

import json
import os
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from collections import defaultdict
import re

BASE_DIR = Path(__file__).parent
PBP_DIR = BASE_DIR / "CSV" / "2026_season" / "pbp"

class PlayerMinutesAnalyzer:
    def __init__(self):
        self.pbp_files = list(PBP_DIR.glob("*_pbp.json"))
        self.player_game_data = defaultdict(lambda: defaultdict(list))
        self.all_players = set()
    
    def parse_time(self, time_str):
        """解析比赛时间字符串"""
        if not time_str or str(time_str).strip() == '':
            return None
        
        try:
            time_str = str(time_str).replace('.0', '').strip()
            if ':' in time_str:
                parts = time_str.split(':')
                if len(parts) == 2:
                    return int(parts[0]) * 60 + int(parts[1])
        except:
            pass
        
        return None
    
    def extract_player_name(self, event):
        """从事件描述中提取球员名字（支持缩写形式）"""
        if not event:
            return None
        
        # 匹配缩写形式: "C. Coward" 或 "J. Jackson"
        patterns = [
            r'([A-Z]\.\s?[A-Z][a-z]+)',  # C. Coward
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)',  # First Last
            r'([A-Z]\.\s?[A-Z]\.\s?[A-Z][a-z]+)'  # 双缩写
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, str(event))
            if matches:
                # 返回第一个匹配到的球员名字
                return matches[0].replace('. ', '.').strip()
        
        return None
    
    def parse_pbp_for_player_events(self):
        """解析PBP数据提取球员事件"""
        print(f"📊 正在分析 {len(self.pbp_files)} 场比赛...")
        
        for filepath in self.pbp_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                game_id = filepath.stem.replace("_pbp", "")
                date_str = game_id[:8]
                
                current_period = 1
                player_actions = []
                
                for row in data:
                    if 'cells' not in row:
                        continue
                    
                    cells = row['cells']
                    if len(cells) < 6:
                        continue
                    
                    time_str = cells[0]
                    away_event = cells[1] if cells[1] else ''
                    home_event = cells[5] if cells[5] else ''
                    
                    # 更新节次
                    time_str_lower = str(time_str).lower()
                    if '1st' in time_str_lower or 'q1' in time_str_lower:
                        current_period = 1
                    elif '2nd' in time_str_lower or 'q2' in time_str_lower:
                        current_period = 2
                    elif '3rd' in time_str_lower or 'q3' in time_str_lower:
                        current_period = 3
                    elif '4th' in time_str_lower or 'q4' in time_str_lower:
                        current_period = 4
                    elif 'ot' in time_str_lower:
                        current_period = 5
                    
                    game_time = self.parse_time(time_str)
                    if game_time is None:
                        continue
                    
                    # 提取两个队的事件
                    for event, team_side in [(away_event, 'away'), (home_event, 'home')]:
                        if not event:
                            continue
                        
                        player = self.extract_player_name(event)
                        if player:
                            self.all_players.add(player)
                            
                            action_type = self.classify_action(event)
                            
                            player_actions.append({
                                'player': player,
                                'period': current_period,
                                'time': game_time,
                                'action': action_type,
                                'team_side': team_side,
                                'raw_event': str(event)
                            })
                
                # 计算球员出场时间
                self.calculate_minutes_from_actions(game_id, date_str, player_actions)
                
            except Exception as e:
                continue
        
        print(f"✅ 成功识别 {len(self.all_players)} 名球员")
    
    def classify_action(self, event):
        """分类事件类型"""
        event_lower = str(event).lower()
        
        if 'makes' in event_lower:
            return 'shot_made'
        elif 'misses' in event_lower:
            return 'shot_miss'
        elif 'rebound' in event_lower:
            return 'rebound'
        elif 'assist' in event_lower:
            return 'assist'
        elif 'steal' in event_lower:
            return 'steal'
        elif 'block' in event_lower:
            return 'block'
        elif 'turnover' in event_lower:
            return 'turnover'
        elif 'foul' in event_lower:
            return 'foul'
        elif 'free throw' in event_lower:
            return 'free_throw'
        elif 'enters' in event_lower:
            return 'enter'
        elif 'leaves' in event_lower:
            return 'leave'
        else:
            return 'other'
    
    def calculate_minutes_from_actions(self, game_id, date_str, actions):
        """从事件计算球员出场时间"""
        # 按球员分组
        player_actions = defaultdict(list)
        for action in actions:
            player_actions[action['player']].append(action)
        
        for player, player_actions_list in player_actions.items():
            # 按时间排序
            player_actions_list.sort(key=lambda x: x['time'])
            
            # 计算出场时间（简化：统计该球员有动作的时间段）
            if not player_actions_list:
                continue
            
            # 获取该球员参与的所有时间段
            periods = set(a['period'] for a in player_actions_list)
            
            total_minutes = 0
            for period in periods:
                period_actions = [a for a in player_actions_list if a['period'] == period]
                if period_actions:
                    # 假设在本节有动作的球员至少出场了一段时间
                    # 简化计算：每个有动作的节次按6分钟计算（约一节的1/4）
                    total_minutes += 6
            
            # 记录到游戏日志
            self.player_game_data[player]['games'].append({
                'game_id': game_id,
                'date': date_str,
                'estimated_minutes': round(total_minutes, 1),
                'actions_count': len(player_actions_list)
            })
    
    def analyze_minutes_distribution(self):
        """分析出场时长分布"""
        game_logs = []
        
        for player, data in self.player_game_data.items():
            for game in data['games']:
                game_logs.append({
                    'player': player,
                    'game_id': game['game_id'],
                    'date': game['date'],
                    'minutes': game['estimated_minutes'],
                    'actions': game['actions_count']
                })
        
        if not game_logs:
            return None
        
        df = pd.DataFrame(game_logs)
        
        # 统计球员平均出场时间
        player_stats = df.groupby('player').agg({
            'minutes': ['mean', 'count', 'min', 'max', 'std'],
            'actions': ['mean', 'sum']
        }).reset_index()
        
        player_stats.columns = ['player', 'avg_minutes', 'games_played', 'min_minutes', 
                               'max_minutes', 'minutes_std', 'avg_actions', 'total_actions']
        
        # 按出场时间分组
        bins = [0, 10, 15, 20, 25, 30, 35, 40, 48]
        df['minutes_group'] = pd.cut(df['minutes'], bins=bins, right=False,
                                     labels=['0-10', '10-15', '15-20', '20-25', 
                                             '25-30', '30-35', '35-40', '40+'])
        
        group_dist = df.groupby('minutes_group', observed=True)['player'].count().reset_index()
        group_dist.columns = ['minutes_range', 'game_count']
        group_dist['percentage'] = round(group_dist['game_count'] / len(df) * 100, 1)
        
        return {
            'player_stats': player_stats,
            'minutes_distribution': group_dist,
            'total_games': len(df),
            'total_players': df['player'].nunique(),
            'raw_data': df
        }
    
    def find_optimal_minutes(self):
        """找到最佳出场时长"""
        stats = self.analyze_minutes_distribution()
        if not stats:
            return None
        
        df = stats['raw_data']
        
        # 计算每个出场时间区间的平均动作数（作为效率指标）
        bins = [0, 10, 15, 20, 25, 30, 35, 40, 48]
        df['minutes_group'] = pd.cut(df['minutes'], bins=bins, right=False,
                                     labels=[str(i) for i in range(8)])
        
        group_stats = df.groupby('minutes_group', observed=True).agg({
            'actions': ['mean', 'sum'],
            'player': 'count'
        }).reset_index()
        
        group_stats.columns = ['group_index', 'avg_actions', 'total_actions', 'game_count']
        
        # 添加区间标签（根据实际索引映射）
        range_map = {'0': '0-10', '1': '10-15', '2': '15-20', '3': '20-25',
                     '4': '25-30', '5': '30-35', '6': '35-40', '7': '40+'}
        midpoint_map = {'0': 10, '1': 15, '2': 20, '3': 25,
                        '4': 30, '5': 35, '6': 40, '7': 45}
        
        group_stats['minutes_range'] = group_stats['group_index'].map(range_map)
        group_stats['midpoint'] = group_stats['group_index'].map(midpoint_map).astype(float)
        
        # 找到效率最高的区间（每分钟动作数）
        group_stats['actions_per_minute'] = group_stats['avg_actions'] / group_stats['midpoint']
        
        max_efficiency_index = group_stats['actions_per_minute'].idxmax()
        optimal_range = group_stats.loc[max_efficiency_index, 'minutes_range']
        
        return {
            'optimal_range': optimal_range,
            'avg_minutes_overall': round(df['minutes'].mean(), 1),
            'median_minutes': round(df['minutes'].median(), 1),
            'distribution': group_stats.to_dict('records'),
            'total_games': len(df)
        }
    
    def generate_report(self):
        """生成分析报告"""
        stats = self.analyze_minutes_distribution()
        
        if not stats:
            return "⚠️ 没有足够的数据进行分析"
        
        optimal = self.find_optimal_minutes()
        
        report = []
        
        report.append("=" * 75)
        report.append("⏱️  球员出场时长分析报告")
        report.append("=" * 75)
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"分析比赛: {stats['total_games']} 场")
        report.append(f"分析球员: {stats['total_players']} 名")
        report.append("=" * 75)
        
        report.append("\n📊 一、出场时长分布")
        report.append("-" * 40)
        
        for _, row in stats['minutes_distribution'].iterrows():
            report.append(f"   {row['minutes_range']}分钟: {row['game_count']} 场 ({row['percentage']}%)")
        
        report.append("\n📈 二、球员出场时间排名")
        report.append("-" * 40)
        
        top_players = stats['player_stats'].sort_values('avg_minutes', ascending=False).head(15)
        report.append(f"{'排名':<4} {'球员':<15} {'场均时间':>8} {'比赛场数':>8}")
        report.append(f"---- {'-'*15} {'--------':>8} {'----------':>8}")
        
        for i, (_, row) in enumerate(top_players.iterrows(), 1):
            report.append(f"{i:<4} {row['player'][:15]:<15} {row['avg_minutes']:>7.1f}分钟 {row['games_played']:>8}场")
        
        report.append("\n🎯 三、最佳出场时长分析")
        report.append("-" * 40)
        
        if optimal:
            report.append(f"效率最高区间: {optimal['optimal_range']}分钟")
            report.append(f"联盟平均出场时间: {optimal['avg_minutes_overall']:.1f}分钟")
            report.append(f"联盟中位出场时间: {optimal['median_minutes']:.1f}分钟")
            
            report.append("\n   各区间效率对比:")
            for dist in optimal['distribution']:
                report.append(f"     {dist['minutes_range']}分钟: 场均动作 {dist['avg_actions']:.1f}次")
        
        report.append("\n📝 四、分析结论")
        report.append("=" * 40)
        report.append("1. 数据概览:")
        report.append(f"   ✓ 共分析 {stats['total_games']} 场比赛")
        report.append(f"   ✓ 识别 {stats['total_players']} 名球员")
        report.append("\n2. 最佳时长建议:")
        if optimal:
            report.append(f"   ✓ 效率最高区间: {optimal['optimal_range']}分钟")
            report.append("   ✓ 建议根据球员类型和表现调整出场时间")
        report.append("\n3. 疲劳效应分析:")
        report.append("   • 需要更多数据来评估长时间出场的效率变化")
        report.append("   • 建议关注30分钟以上区间的效率变化")
        report.append("\n4. 后续分析方向:")
        report.append("   • 结合真实效率数据（得分/篮板/助攻）")
        report.append("   • 分析不同位置的最佳出场时间差异")
        report.append("   • 评估第四节和加时赛的疲劳效应")
        
        report.append("\n" + "=" * 75)
        report.append("报告结束 - 所有分析基于PBP事件数据")
        report.append("=" * 75)
        
        return "\n".join(report)
    
    def save_report(self, filename="player_minutes_analysis_report.txt"):
        """保存分析报告"""
        report = self.generate_report()
        output_path = BASE_DIR / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ 分析报告已保存到: {output_path}")
        return output_path

def main():
    print("=" * 75)
    print("⏱️  球员最佳出场时长分析工具")
    print("分析方法: 数据驱动、科学统计")
    print("=" * 75)
    
    analyzer = PlayerMinutesAnalyzer()
    analyzer.parse_pbp_for_player_events()
    
    stats = analyzer.analyze_minutes_distribution()
    
    if stats:
        print(f"\n📊 分析摘要")
        print("-" * 40)
        print(f"比赛场次: {stats['total_games']}")
        print(f"球员数量: {stats['total_players']}")
        
        optimal = analyzer.find_optimal_minutes()
        if optimal:
            print(f"效率最高区间: {optimal['optimal_range']}分钟")
            print(f"平均出场时间: {optimal['avg_minutes_overall']:.1f}分钟")
        
        analyzer.save_report()
    else:
        print("\n⚠️ 没有足够的数据进行分析")
    
    print("\n🎉 分析完成！")

if __name__ == "__main__":
    main()
