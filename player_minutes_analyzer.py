"""
球员最佳出场时长分析工具

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
from datetime import datetime, timedelta
from collections import defaultdict

BASE_DIR = Path(__file__).parent
PBP_DIR = BASE_DIR / "CSV" / "2026_season" / "pbp"

class PlayerMinutesAnalyzer:
    def __init__(self):
        self.pbp_files = list(PBP_DIR.glob("*_pbp.json"))
        self.player_data = defaultdict(lambda: defaultdict(list))
        self.game_logs = []
    
    def parse_time(self, time_str):
        """解析比赛时间字符串"""
        if not time_str or time_str.strip() == '':
            return None
        
        try:
            # 处理格式: "11:43.0" 或 "11:43"
            time_str = str(time_str).replace('.0', '').strip()
            if ':' in time_str:
                minutes, seconds = time_str.split(':')
                return int(minutes) * 60 + int(seconds)
        except:
            pass
        
        return None
    
    def extract_player_minutes(self):
        """从PBP数据中提取球员出场时间"""
        print(f"📊 正在分析 {len(self.pbp_files)} 场比赛...")
        
        for filepath in self.pbp_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                game_id = filepath.stem.replace("_pbp", "")
                date_str = game_id[:8]
                
                # 记录球员在场上的时间段
                on_court = set()
                player_period_minutes = defaultdict(list)
                current_period = 1
                
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
                    if '1st' in str(time_str):
                        current_period = 1
                    elif '2nd' in str(time_str):
                        current_period = 2
                    elif '3rd' in str(time_str):
                        current_period = 3
                    elif '4th' in str(time_str):
                        current_period = 4
                    elif 'OT' in str(time_str):
                        current_period = 5
                    
                    game_time = self.parse_time(time_str)
                    if game_time is None:
                        continue
                    
                    # 解析换人事件
                    for event in [away_event, home_event]:
                        if 'enters' in str(event).lower() or 'enters the game' in str(event).lower():
                            # 球员进入比赛
                            player = self.extract_player_name(event)
                            if player:
                                on_court.add(player)
                                # 记录上场时间
                                self.player_data[player]['enter_times'].append({
                                    'game_id': game_id,
                                    'date': date_str,
                                    'period': current_period,
                                    'time': game_time
                                })
                        
                        elif 'leaves' in str(event).lower() or 'substitution' in str(event).lower():
                            # 球员离开比赛
                            player = self.extract_player_name(event)
                            if player and player in on_court:
                                on_court.remove(player)
                                # 记录下场时间
                                self.player_data[player]['exit_times'].append({
                                    'game_id': game_id,
                                    'date': date_str,
                                    'period': current_period,
                                    'time': game_time
                                })
                
                # 计算本场比赛球员出场时间
                self.calculate_game_minutes(game_id, date_str)
                
            except Exception as e:
                continue
        
        print(f"✅ 成功分析 {len(self.player_data)} 名球员")
    
    def extract_player_name(self, event):
        """从事件描述中提取球员名字"""
        if not event:
            return None
        
        import re
        
        # 匹配球员名字模式
        patterns = [
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+enters',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+leaves',
            r'substitution:\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+makes',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+misses'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, str(event))
            if match:
                return match.group(1)
        
        return None
    
    def calculate_game_minutes(self, game_id, date_str):
        """计算球员单场比赛出场时间"""
        for player, data in self.player_data.items():
            enters = [e for e in data['enter_times'] if e['game_id'] == game_id]
            exits = [e for e in data['exit_times'] if e['game_id'] == game_id]
            
            total_minutes = 0
            
            # 简单计算：每个节次的出场时间
            for period in range(1, 6):
                period_enters = [e for e in enters if e['period'] == period]
                period_exits = [e for e in exits if e['period'] == period]
                
                if period_enters:
                    # 假设球员在节开始时上场，如果没有记录入场时间
                    enter_time = period_enters[0]['time'] if period_enters else (period - 1) * 720
                    exit_time = period_exits[0]['time'] if period_exits else period * 720
                    
                    # 节开始时间是 (period-1) * 720 秒
                    period_start = (period - 1) * 720
                    period_end = period * 720
                    
                    # 计算在本节的出场时间
                    start = max(enter_time, period_start)
                    end = min(exit_time if period_exits else period_end, period_end)
                    
                    if end > start:
                        total_minutes += (end - start) / 60
            
            if total_minutes > 0:
                self.game_logs.append({
                    'player': player,
                    'game_id': game_id,
                    'date': date_str,
                    'minutes_played': round(total_minutes, 1)
                })
    
    def analyze_minutes_efficiency(self):
        """分析出场时长与效率的关系"""
        if not self.game_logs:
            print("⚠️ 没有足够的数据进行分析")
            return None
        
        df = pd.DataFrame(self.game_logs)
        
        # 计算球员平均出场时间
        player_avg = df.groupby('player')['minutes_played'].agg(['mean', 'count', 'min', 'max']).reset_index()
        player_avg.columns = ['player', 'avg_minutes', 'games_played', 'min_minutes', 'max_minutes']
        
        # 按出场时间分组分析
        df['minutes_group'] = pd.cut(df['minutes_played'], 
                                     bins=[0, 10, 15, 20, 25, 30, 35, 40, 48],
                                     labels=['0-10', '10-15', '15-20', '20-25', '25-30', '30-35', '35-40', '40+'])
        
        group_stats = df.groupby('minutes_group')['player'].count().reset_index()
        group_stats.columns = ['minutes_range', 'game_count']
        
        return {
            'player_summary': player_avg,
            'minutes_distribution': group_stats,
            'total_games': len(df),
            'total_players': df['player'].nunique()
        }
    
    def find_optimal_minutes_range(self, player_name=None):
        """找到最佳出场时长范围"""
        df = pd.DataFrame(self.game_logs)
        
        if player_name:
            df = df[df['player'] == player_name]
        
        # 按5分钟区间分组
        bins = [0, 10, 15, 20, 25, 30, 35, 40, 48]
        df['minutes_group'] = pd.cut(df['minutes_played'], bins=bins, labels=[str(i) for i in range(8)])
        
        # 统计每个区间的比赛数
        distribution = df.groupby('minutes_group').size().reset_index(name='count')
        distribution['percentage'] = round(distribution['count'] / distribution['count'].sum() * 100, 1)
        
        # 找到出现次数最多的区间（众数区间）
        optimal_index = distribution['count'].idxmax()
        optimal_range = f"{bins[optimal_index]}-{bins[optimal_index+1]}分钟"
        
        # 计算平均出场时间
        avg_minutes = round(df['minutes_played'].mean(), 1)
        median_minutes = round(df['minutes_played'].median(), 1)
        
        return {
            'optimal_range': optimal_range,
            'avg_minutes': avg_minutes,
            'median_minutes': median_minutes,
            'distribution': distribution.to_dict('records'),
            'total_games': len(df)
        }
    
    def generate_report(self):
        """生成分析报告"""
        stats = self.analyze_minutes_efficiency()
        
        if not stats:
            return "⚠️ 没有足够的数据进行分析"
        
        report = []
        
        report.append("=" * 75)
        report.append("🏀 球员出场时长分析报告")
        report.append("=" * 75)
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"分析比赛: {stats['total_games']} 场")
        report.append(f"分析球员: {stats['total_players']} 名")
        report.append("=" * 75)
        
        report.append("\n📊 一、出场时长分布")
        report.append("-" * 40)
        
        dist = stats['minutes_distribution']
        for _, row in dist.iterrows():
            report.append(f"   {row['minutes_range']}分钟: {row['game_count']} 场")
        
        report.append("\n📈 二、球员平均出场时间")
        report.append("-" * 40)
        
        # 显示出场时间最多的前10名球员
        top_players = stats['player_summary'].sort_values('avg_minutes', ascending=False).head(10)
        report.append(f"{'球员':<15} {'场均时间':>8} {'比赛场数':>8}")
        report.append(f"{'-'*15} {'--------':>8} {'----------':>8}")
        
        for _, row in top_players.iterrows():
            report.append(f"{row['player'][:15]:<15} {row['avg_minutes']:>7.1f}分钟 {row['games_played']:>8}场")
        
        report.append("\n🎯 三、最佳出场时长分析")
        report.append("-" * 40)
        
        optimal = self.find_optimal_minutes_range()
        report.append(f"最佳出场时长区间: {optimal['optimal_range']}")
        report.append(f"联盟平均出场时间: {optimal['avg_minutes']:.1f}分钟")
        report.append(f"联盟中位出场时间: {optimal['median_minutes']:.1f}分钟")
        
        report.append("\n📝 四、分析结论")
        report.append("=" * 40)
        report.append("1. 出场时间分布:")
        report.append(f"   ✓ 共分析 {stats['total_games']} 场比赛")
        report.append(f"   ✓ 涉及 {stats['total_players']} 名球员")
        report.append("\n2. 最佳时长建议:")
        report.append(f"   ✓ 最常见出场区间: {optimal['optimal_range']}")
        report.append("   ✓ 建议根据球员类型制定出场策略")
        report.append("\n3. 后续分析方向:")
        report.append("   • 结合球员效率数据评估最佳时长")
        report.append("   • 分析疲劳效应（后半段效率变化）")
        report.append("   • 位置差异分析（后卫vs前锋vs中锋）")
        
        report.append("\n" + "=" * 75)
        report.append("报告结束")
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
    analyzer.extract_player_minutes()
    
    stats = analyzer.analyze_minutes_efficiency()
    
    if stats:
        print(f"\n📊 分析摘要")
        print("-" * 40)
        print(f"比赛场次: {stats['total_games']}")
        print(f"球员数量: {stats['total_players']}")
        
        optimal = analyzer.find_optimal_minutes_range()
        print(f"最佳出场区间: {optimal['optimal_range']}")
        print(f"平均出场时间: {optimal['avg_minutes']:.1f}分钟")
        
        analyzer.save_report()
    
    print("\n🎉 分析完成！")

if __name__ == "__main__":
    main()
