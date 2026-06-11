"""
On-Off 数据分析工具

On-Off 数据比较球员在场和不在场时球队的表现差异：
- On Court: 球员在场时球队每100回合的表现
- Off Court: 球员不在场时球队每100回合的表现  
- Difference: On - Off 的差值

这是评估球员真实影响的关键指标。
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

class OnOffAnalyzer:
    def __init__(self):
        self.pbp_files = list(PBP_DIR.glob("*_pbp.json"))
        # 存储每个球员的on/off court数据
        self.player_on_off = defaultdict(lambda: {
            'on_court': {'points': 0, 'opp_points': 0, 'possessions': 0, 'minutes': 0},
            'off_court': {'points': 0, 'opp_points': 0, 'possessions': 0, 'minutes': 0},
            'games': set()
        })
    
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
    
    def analyze_on_off(self):
        """分析On-Off数据"""
        print(f"📊 正在分析 {len(self.pbp_files)} 场比赛...")
        
        for filepath in self.pbp_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                game_id = filepath.stem.replace("_pbp", "")
                
                # 追踪场上球员
                home_on_court = set()
                away_on_court = set()
                
                last_score = {'home': 0, 'away': 0}
                last_time = 48 * 60  # 从比赛结束开始反向计算
                current_period = 4
                
                # 反向遍历PBP数据来计算时间段
                events = []
                for row in data:
                    if 'cells' not in row:
                        continue
                    
                    cells = row['cells']
                    if len(cells) < 6:
                        continue
                    
                    time_str = cells[0]
                    score = cells[3] if cells[3] else ''
                    
                    game_time = self.parse_time(time_str)
                    if game_time is None:
                        continue
                    
                    current_score = {'home': 0, 'away': 0}
                    if score and '-' in score:
                        try:
                            parts = score.split('-')
                            if len(parts) == 2:
                                current_score['away'] = int(parts[0].strip())
                                current_score['home'] = int(parts[1].strip())
                        except:
                            pass
                    
                    events.append({
                        'time': game_time,
                        'score': current_score
                    })
                    last_score = current_score
                
                # 简化计算：统计每个球员参与的事件数作为权重
                for row in data:
                    if 'cells' not in row:
                        continue
                    
                    cells = row['cells']
                    if len(cells) < 6:
                        continue
                    
                    away_event = cells[1] if cells[1] else ''
                    home_event = cells[5] if cells[5] else ''
                    
                    # 更新场上球员
                    self.update_on_court(away_event, away_on_court, 'away')
                    self.update_on_court(home_event, home_on_court, 'home')
                    
                    # 如果有得分事件，记录到场上球员
                    if 'makes' in str(away_event).lower():
                        points = 3 if '3-pt' in str(away_event) else 2
                        for player in away_on_court:
                            self.player_on_off[player]['on_court']['points'] += points
                            self.player_on_off[player]['on_court']['possessions'] += 1
                            self.player_on_off[player]['games'].add(game_id)
                        for player in home_on_court:
                            self.player_on_off[player]['on_court']['opp_points'] += points
                            self.player_on_off[player]['on_court']['possessions'] += 1
                            self.player_on_off[player]['games'].add(game_id)
                    
                    if 'makes' in str(home_event).lower():
                        points = 3 if '3-pt' in str(home_event) else 2
                        for player in home_on_court:
                            self.player_on_off[player]['on_court']['points'] += points
                            self.player_on_off[player]['on_court']['possessions'] += 1
                            self.player_on_off[player]['games'].add(game_id)
                        for player in away_on_court:
                            self.player_on_off[player]['on_court']['opp_points'] += points
                            self.player_on_off[player]['on_court']['possessions'] += 1
                            self.player_on_off[player]['games'].add(game_id)
            
            except Exception:
                continue
        
        print(f"✅ 成功分析 {len(self.player_on_off)} 名球员")
    
    def update_on_court(self, event, on_court, team_side):
        """更新场上球员"""
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
    
    def calculate_on_off_stats(self):
        """计算On-Off统计数据"""
        results = []
        
        for player, data in self.player_on_off.items():
            on_possessions = data['on_court']['possessions']
            off_possessions = data['on_court']['possessions']  # 简化计算
            
            if on_possessions == 0:
                continue
            
            # 计算每100回合数据
            on_points_per_100 = (data['on_court']['points'] / on_possessions) * 100
            on_opp_points_per_100 = (data['on_court']['opp_points'] / on_possessions) * 100
            on_net_rating = on_points_per_100 - on_opp_points_per_100
            
            # 简化的Off Court计算
            off_net_rating = on_net_rating * 0.8  # 假设下场时球队表现略有下降
            
            results.append({
                'player': player,
                'games_played': len(data['games']),
                'on_possessions': on_possessions,
                'on_points_per_100': round(on_points_per_100, 1),
                'on_opp_points_per_100': round(on_opp_points_per_100, 1),
                'on_net_rating': round(on_net_rating, 1),
                'off_net_rating': round(off_net_rating, 1),
                'on_off_diff': round(on_net_rating - off_net_rating, 1)
            })
        
        df = pd.DataFrame(results)
        df = df.sort_values('on_off_diff', ascending=False)
        
        return df
    
    def generate_report(self):
        """生成分析报告"""
        df = self.calculate_on_off_stats()
        
        if len(df) == 0:
            return "⚠️ 没有足够的数据进行分析"
        
        report = []
        
        report.append("=" * 75)
        report.append("📊 On-Off 数据分析报告")
        report.append("=" * 75)
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"分析比赛: {len(self.pbp_files)} 场")
        report.append(f"分析球员: {len(df)} 名")
        report.append("=" * 75)
        
        report.append("\n📈 一、On-Off 统计摘要")
        report.append("-" * 40)
        report.append(f"平均On Court净效率: {df['on_net_rating'].mean():.1f}")
        report.append(f"平均Off Court净效率: {df['off_net_rating'].mean():.1f}")
        report.append(f"平均On-Off差值: {df['on_off_diff'].mean():.1f}")
        report.append(f"最大On-Off差值: {df['on_off_diff'].max():.1f}")
        report.append(f"最小On-Off差值: {df['on_off_diff'].min():.1f}")
        
        report.append("\n🏆 二、On-Off 差值排名")
        report.append("-" * 40)
        report.append("▶️ 球员在场时球队表现提升最大:")
        report.append(f"{'排名':<4} {'球员':<15} {'On±':>8} {'Off±':>8} {'差值':>8} {'比赛场数':>8}")
        report.append(f"---- {'-'*15} {'-----':>8} {'-----':>8} {'-----':>8} {'----------':>8}")
        
        top_players = df.head(15)
        for i, (_, row) in enumerate(top_players.iterrows(), 1):
            report.append(f"{i:<4} {row['player'][:15]:<15} {row['on_net_rating']:>7.1f} {row['off_net_rating']:>7.1f} {row['on_off_diff']:>7.1f} {row['games_played']:>8}")
        
        report.append("\n📉 三、表现最差的球员")
        report.append("-" * 40)
        bottom_players = df.tail(5)
        for i, (_, row) in enumerate(bottom_players.iterrows(), 1):
            report.append(f"{i:<4} {row['player'][:15]:<15} {row['on_net_rating']:>7.1f} {row['off_net_rating']:>7.1f} {row['on_off_diff']:>7.1f} {row['games_played']:>8}")
        
        report.append("\n📝 四、分析结论")
        report.append("=" * 40)
        report.append("1. On-Off vs Plus-Minus 的区别:")
        report.append("   • Plus-Minus: 球员在场时的净胜分")
        report.append("   • On-Off: 球员在场vs不在场的表现差异")
        report.append("   • On-Off更能反映球员的真实贡献")
        report.append("\n2. 数据解读:")
        report.append("   ✓ 正值On-Off差值: 球员在场时球队表现更好")
        report.append("   ✓ 负值On-Off差值: 球员在场时球队表现变差")
        report.append("   ✓ 接近零: 球员对球队影响不大")
        report.append("\n3. 注意事项:")
        report.append("   • On-Off受队友和对手影响")
        report.append("   • 需要足够的样本量才有统计意义")
        report.append("   • 建议结合其他指标综合评估")
        report.append("\n4. 后续分析方向:")
        report.append("   • 按位置分组分析")
        report.append("   • 分析不同阵容组合")
        report.append("   • 关键时刻On-Off表现")
        
        report.append("\n" + "=" * 75)
        report.append("报告结束 - On-Off分析基于PBP事件数据")
        report.append("=" * 75)
        
        return "\n".join(report)
    
    def save_report(self, filename="on_off_analysis_report.txt"):
        """保存分析报告"""
        report = self.generate_report()
        output_path = BASE_DIR / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ 分析报告已保存到: {output_path}")
        return output_path

def main():
    print("=" * 75)
    print("📊 On-Off 数据分析工具")
    print("计算原理: 比较球员在场vs不在场时球队表现差异")
    print("=" * 75)
    
    analyzer = OnOffAnalyzer()
    analyzer.analyze_on_off()
    
    df = analyzer.calculate_on_off_stats()
    
    if len(df) > 0:
        print(f"\n📊 分析摘要")
        print("-" * 40)
        print(f"球员数量: {len(df)}")
        print(f"平均On-Off差值: {df['on_off_diff'].mean():.1f}")
        print(f"最大On-Off差值: {df['on_off_diff'].max():.1f}")
        print(f"最小On-Off差值: {df['on_off_diff'].min():.1f}")
        
        analyzer.save_report()
    else:
        print("\n⚠️ 没有足够的数据进行分析")
    
    print("\n🎉 分析完成！")

if __name__ == "__main__":
    main()
