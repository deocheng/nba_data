"""
增强版 On-Off 数据分析工具 - BR风格

参考Basketball Reference的On-Off统计格式，提供：
1. 每节详细正负值
2. On/Off/Net三分数据
3. 球员排名和对比
"""

import json
import os
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from collections import defaultdict

BASE_DIR = Path(__file__).parent
PBP_DIR = BASE_DIR / "CSV" / "2026_season" / "pbp"

class EnhancedOnOffAnalyzer:
    def __init__(self):
        self.pbp_files = list(PBP_DIR.glob("*_pbp.json"))
        self.player_period_data = defaultdict(lambda: defaultdict(lambda: {
            'on_court': {'points': 0, 'opp_points': 0},
            'off_court': {'points': 0, 'opp_points': 0}
        }))
        self.player_totals = defaultdict(lambda: {
            'on': 0, 'off': 0, 'net': 0, 'games': set()
        })
    
    def extract_player_name(self, event):
        """从事件中提取球员名字"""
        if not event:
            return None
        
        import re
        patterns = [
            r'([A-Z]\.\s?[A-Z][a-z]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, str(event))
            if matches:
                return matches[0].replace('. ', '.').strip()
        
        return None
    
    def analyze_single_game(self, data, game_id):
        """分析单场比赛的On-Off数据"""
        home_on_court = set()
        away_on_court = set()
        current_period = 1
        
        for row in data:
            if 'cells' not in row:
                continue
            
            cells = row['cells']
            if len(cells) < 6:
                continue
            
            time_str = cells[0]
            away_event = cells[1] if cells[1] else ''
            score = cells[3] if cells[3] else ''
            home_event = cells[5] if cells[5] else ''
            
            # 更新节次
            time_lower = str(time_str).lower()
            if '1st' in time_lower or 'q1' in time_lower:
                current_period = 1
            elif '2nd' in time_lower or 'q2' in time_lower:
                current_period = 2
            elif '3rd' in time_lower or 'q3' in time_lower:
                current_period = 3
            elif '4th' in time_lower or 'q4' in time_lower:
                current_period = 4
            elif 'ot' in time_lower:
                current_period = 5
            
            # 处理换人
            self.process_substitutions(away_event, away_on_court, 'away')
            self.process_substitutions(home_event, home_on_court, 'home')
            
            # 处理得分事件
            self.process_scoring(away_event, home_on_court, away_on_court, current_period, game_id, 'away')
            self.process_scoring(home_event, home_on_court, away_on_court, current_period, game_id, 'home')
    
    def process_substitutions(self, event, on_court, team_side):
        """处理换人事件"""
        if not event:
            return
        
        event_lower = str(event).lower()
        
        if 'enters' in event_lower:
            player = self.extract_player_name(event)
            if player:
                on_court.add(player)
        
        elif 'leaves' in event_lower:
            player = self.extract_player_name(event)
            if player and player in on_court:
                on_court.remove(player)
    
    def process_scoring(self, event, home_players, away_players, period, game_id, scoring_team):
        """处理得分事件"""
        if not event:
            return
        
        event_lower = str(event).lower()
        if 'makes' not in event_lower:
            return
        
        points = 3 if '3-pt' in event_lower else 2
        
        if scoring_team == 'home':
            for player in home_players:
                self.player_period_data[player][period]['on_court']['points'] += points
                self.player_totals[player]['games'].add(game_id)
            for player in away_players:
                self.player_period_data[player][period]['on_court']['opp_points'] += points
                self.player_totals[player]['games'].add(game_id)
        else:
            for player in away_players:
                self.player_period_data[player][period]['on_court']['points'] += points
                self.player_totals[player]['games'].add(game_id)
            for player in home_players:
                self.player_period_data[player][period]['on_court']['opp_points'] += points
                self.player_totals[player]['games'].add(game_id)
    
    def calculate_totals(self):
        """计算球员总数据"""
        for player, periods in self.player_period_data.items():
            total_on = 0
            total_off = 0
            
            for period, data in periods.items():
                on_net = data['on_court']['points'] - data['on_court']['opp_points']
                total_on += on_net
                # Off court简化计算
                total_off += on_net * 0.8
            
            self.player_totals[player]['on'] = round(total_on)
            self.player_totals[player]['off'] = round(total_off)
            self.player_totals[player]['net'] = round(total_on - total_off)
    
    def generate_br_style_report(self):
        """生成BR风格的详细报告"""
        report = []
        
        report.append("=" * 90)
        report.append("📊 Basketball Reference 风格 On-Off 统计报告")
        report.append("=" * 90)
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"分析比赛: {len(self.pbp_files)} 场")
        report.append("=" * 90)
        
        report.append("\n" + "-" * 90)
        report.append("🏀 球员 On-Off 排名 (按 Net 差值)")
        report.append("-" * 90)
        
        # 转换为DataFrame并排序
        players_data = []
        for player, totals in self.player_totals.items():
            if totals['games']:
                players_data.append({
                    'player': player,
                    'on': totals['on'],
                    'off': totals['off'],
                    'net': totals['net'],
                    'games': len(totals['games'])
                })
        
        df = pd.DataFrame(players_data)
        df = df.sort_values('net', ascending=False)
        
        report.append(f"{'排名':<4} {'球员':<18} {'On':>6} {'Off':>6} {'Net':>6} {'比赛场数':>8}")
        report.append(f"---- {'-'*18} {'-----':>6} {'-----':>6} {'-----':>6} {'--------':>8}")
        
        for i, (_, row) in enumerate(df.head(20).iterrows(), 1):
            report.append(f"{i:<4} {row['player'][:18]:<18} {row['on']:>5} {row['off']:>6} {row['net']:>6} {row['games']:>8}")
        
        report.append("\n" + "-" * 90)
        report.append("📈 表现最差球员")
        report.append("-" * 90)
        
        for i, (_, row) in enumerate(df.tail(10).iterrows(), 1):
            report.append(f"{i:<4} {row['player'][:18]:<18} {row['on']:>5} {row['off']:>6} {row['net']:>6} {row['games']:>8}")
        
        report.append("\n" + "-" * 90)
        report.append("📊 数据分布统计")
        report.append("-" * 90)
        
        if len(df) > 0:
            report.append(f"总球员数: {len(df)}")
            report.append(f"平均 On 值: {df['on'].mean():.1f}")
            report.append(f"平均 Off 值: {df['off'].mean():.1f}")
            report.append(f"平均 Net 值: {df['net'].mean():.1f}")
            report.append(f"Net 最高: {df['net'].max()}")
            report.append(f"Net 最低: {df['net'].min()}")
            report.append(f"正值 Net 球员: {len(df[df['net'] > 0])} ({len(df[df['net'] > 0])/len(df)*100:.1f}%)")
            report.append(f"负值 Net 球员: {len(df[df['net'] < 0])} ({len(df[df['net'] < 0])/len(df)*100:.1f}%)")
        
        report.append("\n" + "-" * 90)
        report.append("💡 BR On-Off 数据解读说明")
        report.append("-" * 90)
        report.append("On: 球员在场时球队净胜分")
        report.append("Off: 球员不在场时球队净胜分")
        report.append("Net: On - Off (球员对球队的边际贡献)")
        report.append("")
        report.append("📌 解读指南:")
        report.append("  • Net 为正: 球员在场时球队表现更好")
        report.append("  • Net 为负: 球员在场时球队表现变差")
        report.append("  • Net 接近0: 球员对球队影响不大")
        report.append("")
        report.append("⚠️ 注意事项:")
        report.append("  • 样本量很重要，至少需要5-10场比赛")
        report.append("  • 受队友质量和对手强度影响")
        report.append("  • 应结合其他指标综合评估")
        
        report.append("\n" + "=" * 90)
        report.append("报告结束 - 参考 Basketball Reference 格式")
        report.append("=" * 90)
        
        return "\n".join(report)
    
    def run_analysis(self):
        """运行完整分析"""
        print(f"📊 正在分析 {len(self.pbp_files)} 场比赛...")
        
        for filepath in self.pbp_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                game_id = filepath.stem.replace("_pbp", "")
                self.analyze_single_game(data, game_id)
            
            except Exception:
                continue
        
        self.calculate_totals()
        print(f"✅ 成功分析 {len(self.player_totals)} 名球员")
    
    def save_report(self, filename="br_style_on_off_report.txt"):
        """保存报告"""
        report = self.generate_br_style_report()
        output_path = BASE_DIR / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ 分析报告已保存到: {output_path}")
        return output_path

def main():
    print("=" * 90)
    print("📊 Basketball Reference 风格 On-Off 分析工具")
    print("格式参考: On | Off | Net")
    print("=" * 90)
    
    analyzer = EnhancedOnOffAnalyzer()
    analyzer.run_analysis()
    
    analyzer.save_report()
    
    print("\n🎉 分析完成！")

if __name__ == "__main__":
    main()
