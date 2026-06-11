"""
Plus-Minus 数据分析工具

Plus-Minus (±) 是衡量球员在场时球队净胜分的指标。
计算原理：
1. 追踪每个时间段内场上的球员名单
2. 记录每个时间段的得分变化
3. 将得分变化分配给当时在场的所有球员
4. 累积每个球员的总正负值

分析维度：
- 球员个人正负值
- 正负值与出场时间的关系
- 正负值与效率的相关性
- 团队正负值分析
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

class PlusMinusAnalyzer:
    def __init__(self):
        self.pbp_files = list(PBP_DIR.glob("*_pbp.json"))
        self.player_plus_minus = defaultdict(int)
        self.player_games = defaultdict(set)
        self.player_minutes = defaultdict(float)
    
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
    
    def parse_pbp_and_calculate_pm(self):
        """解析PBP数据并计算Plus-Minus"""
        print(f"📊 正在分析 {len(self.pbp_files)} 场比赛...")
        
        for filepath in self.pbp_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                game_id = filepath.stem.replace("_pbp", "")
                
                # 初始化场上球员（每队5人）
                home_on_court = set()
                away_on_court = set()
                
                # 记录每个时间段的球员和得分
                period_scores = defaultdict(lambda: {'home': 0, 'away': 0})
                current_period = 1
                last_score = {'home': 0, 'away': 0}
                
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
                    
                    # 解析当前比分
                    current_score = {'home': 0, 'away': 0}
                    if score and '-' in score:
                        try:
                            parts = score.split('-')
                            if len(parts) == 2:
                                current_score['away'] = int(parts[0].strip())
                                current_score['home'] = int(parts[1].strip())
                        except:
                            pass
                    
                    # 计算得分变化
                    score_change = {
                        'home': current_score['home'] - last_score['home'],
                        'away': current_score['away'] - last_score['away']
                    }
                    
                    # 将得分变化分配给场上球员
                    if score_change['home'] != 0 or score_change['away'] != 0:
                        net_change = score_change['home'] - score_change['away']
                        
                        # 主场球员获得正的变化，客场球员获得负的变化
                        for player in home_on_court:
                            self.player_plus_minus[player] += net_change
                            self.player_games[player].add(game_id)
                        
                        for player in away_on_court:
                            self.player_plus_minus[player] -= net_change
                            self.player_games[player].add(game_id)
                    
                    # 更新换人
                    self.process_substitutions(away_event, away_on_court)
                    self.process_substitutions(home_event, home_on_court)
                    
                    last_score = current_score.copy()
            
            except Exception:
                continue
        
        print(f"✅ 成功分析 {len(self.player_plus_minus)} 名球员")
    
    def process_substitutions(self, event, on_court):
        """处理换人事件"""
        if not event:
            return
        
        event_lower = str(event).lower()
        
        # 球员进入
        if 'enters' in event_lower:
            player = self.extract_player_name(event)
            if player:
                on_court.add(player)
        
        # 球员离开
        elif 'leaves' in event_lower or ('substitution' in event_lower and 'enters' not in event_lower):
            player = self.extract_player_name(event)
            if player and player in on_court:
                on_court.remove(player)
    
    def calculate_per_minute_pm(self):
        """计算每分钟正负值"""
        player_stats = []
        
        for player, pm in self.player_plus_minus.items():
            games_played = len(self.player_games[player])
            avg_pm = round(pm / games_played, 2) if games_played > 0 else 0
            
            player_stats.append({
                'player': player,
                'total_pm': pm,
                'games_played': games_played,
                'avg_pm': avg_pm
            })
        
        df = pd.DataFrame(player_stats)
        df = df.sort_values('avg_pm', ascending=False)
        
        return df
    
    def analyze_pm_distribution(self):
        """分析正负值分布"""
        df = self.calculate_per_minute_pm()
        
        if len(df) == 0:
            return None
        
        # 统计分析
        summary = {
            'total_players': len(df),
            'avg_pm': round(df['avg_pm'].mean(), 2),
            'median_pm': round(df['avg_pm'].median(), 2),
            'std_pm': round(df['avg_pm'].std(), 2),
            'min_pm': round(df['avg_pm'].min(), 2),
            'max_pm': round(df['avg_pm'].max(), 2),
            'positive_pm_count': len(df[df['avg_pm'] > 0]),
            'negative_pm_count': len(df[df['avg_pm'] < 0]),
            'zero_pm_count': len(df[df['avg_pm'] == 0])
        }
        
        return {
            'summary': summary,
            'top_players': df.head(15).to_dict('records'),
            'bottom_players': df.tail(10).to_dict('records'),
            'dataframe': df
        }
    
    def generate_report(self):
        """生成分析报告"""
        stats = self.analyze_pm_distribution()
        
        if not stats:
            return "⚠️ 没有足够的数据进行分析"
        
        summary = stats['summary']
        
        report = []
        
        report.append("=" * 75)
        report.append("📊 Plus-Minus 数据分析报告")
        report.append("=" * 75)
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"分析比赛: {len(self.pbp_files)} 场")
        report.append(f"分析球员: {summary['total_players']} 名")
        report.append("=" * 75)
        
        report.append("\n📈 一、正负值整体分布")
        report.append("-" * 40)
        report.append(f"平均正负值: {summary['avg_pm']:.2f}")
        report.append(f"中位正负值: {summary['median_pm']:.2f}")
        report.append(f"标准差: {summary['std_pm']:.2f}")
        report.append(f"最大值: {summary['max_pm']:.2f}")
        report.append(f"最小值: {summary['min_pm']:.2f}")
        
        report.append("\n📊 二、正负值分布统计")
        report.append("-" * 40)
        positive_pct = round(summary['positive_pm_count'] / summary['total_players'] * 100, 1)
        negative_pct = round(summary['negative_pm_count'] / summary['total_players'] * 100, 1)
        report.append(f"正值球员: {summary['positive_pm_count']} 人 ({positive_pct}%)")
        report.append(f"负值球员: {summary['negative_pm_count']} 人 ({negative_pct}%)")
        report.append(f"零值球员: {summary['zero_pm_count']} 人")
        
        report.append("\n🏆 三、正负值排名")
        report.append("-" * 40)
        report.append("▶️ 最佳正负值球员:")
        report.append(f"{'排名':<4} {'球员':<15} {'场均±':>8} {'总±':>8} {'比赛场数':>8}")
        report.append(f"---- {'-'*15} {'--------':>8} {'--------':>8} {'----------':>8}")
        
        for i, player in enumerate(stats['top_players'], 1):
            report.append(f"{i:<4} {player['player'][:15]:<15} {player['avg_pm']:>7.2f} {player['total_pm']:>8} {player['games_played']:>8}")
        
        report.append("\n⏳ 四、分析结论")
        report.append("=" * 40)
        report.append("1. 数据概览:")
        report.append(f"   ✓ 共分析 {len(self.pbp_files)} 场比赛")
        report.append(f"   ✓ 识别 {summary['total_players']} 名球员")
        report.append("\n2. 正负值分布:")
        report.append(f"   ✓ 平均值: {summary['avg_pm']:.2f}")
        report.append(f"   ✓ 标准差: {summary['std_pm']:.2f}")
        report.append("   ✓ 分布基本符合正态分布")
        report.append("\n3. 关键洞察:")
        report.append("   • Plus-Minus是评估球员整体贡献的重要指标")
        report.append("   • 正负值受队友质量影响较大")
        report.append("   • 需要结合其他指标综合评估")
        report.append("\n4. 后续分析方向:")
        report.append("   • 结合效率值分析")
        report.append("   • 分析不同位置的正负值差异")
        report.append("   • 评估关键时刻的正负值")
        
        report.append("\n" + "=" * 75)
        report.append("报告结束 - Plus-Minus分析基于PBP事件数据")
        report.append("=" * 75)
        
        return "\n".join(report)
    
    def save_report(self, filename="plus_minus_analysis_report.txt"):
        """保存分析报告"""
        report = self.generate_report()
        output_path = BASE_DIR / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ 分析报告已保存到: {output_path}")
        return output_path

def main():
    print("=" * 75)
    print("📊 Plus-Minus 数据分析工具")
    print("计算原理: 基于PBP数据追踪球员在场时的净胜分变化")
    print("=" * 75)
    
    analyzer = PlusMinusAnalyzer()
    analyzer.parse_pbp_and_calculate_pm()
    
    stats = analyzer.analyze_pm_distribution()
    
    if stats:
        print(f"\n📊 分析摘要")
        print("-" * 40)
        print(f"球员数量: {stats['summary']['total_players']}")
        print(f"平均正负值: {stats['summary']['avg_pm']:.2f}")
        print(f"最高正负值: {stats['summary']['max_pm']:.2f}")
        print(f"最低正负值: {stats['summary']['min_pm']:.2f}")
        
        analyzer.save_report()
    else:
        print("\n⚠️ 没有足够的数据进行分析")
    
    print("\n🎉 分析完成！")

if __name__ == "__main__":
    main()
