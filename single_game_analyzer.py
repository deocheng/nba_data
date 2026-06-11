"""
单场比赛球员分析工具

针对单场比赛进行深度分析：
1. 球员出场时间和休息时间
2. 每节表现追踪
3. 关键时刻表现
4. 对位分析
5. 实时正负值变化
"""

import json
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BASE_DIR = Path(__file__).parent
PBP_DIR = BASE_DIR / "CSV" / "2026_season" / "pbp"

class SingleGameAnalyzer:
    def __init__(self):
        self.pbp_files = list(PBP_DIR.glob("*_pbp.json"))
    
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
    
    def analyze_game(self, game_data, game_id):
        """分析单场比赛"""
        # 追踪场上球员
        home_on_court = set()
        away_on_court = set()
        
        # 记录球员数据
        player_stats = defaultdict(lambda: {
            'periods': {1: {'minutes': 0, 'plus_minus': 0, 'actions': []},
                        2: {'minutes': 0, 'plus_minus': 0, 'actions': []},
                        3: {'minutes': 0, 'plus_minus': 0, 'actions': []},
                        4: {'minutes': 0, 'plus_minus': 0, 'actions': []}},
            'total_minutes': 0,
            'total_plus_minus': 0,
            'actions': [],
            'on_court_changes': []
        })
        
        current_period = 1
        last_score = {'home': 0, 'away': 0}
        last_time = 720  # 12分钟 = 720秒
        
        for row in game_data:
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
            
            game_time = self.parse_time(time_str)
            if game_time is None:
                game_time = 720 - (current_period - 1) * 720
            
            # 计算时间段长度
            time_diff = last_time - game_time
            if time_diff > 0 and time_diff < 300:  # 合理时间差
                for player in home_on_court:
                    player_stats[player]['periods'][current_period]['minutes'] += time_diff / 60
                    player_stats[player]['total_minutes'] += time_diff / 60
                for player in away_on_court:
                    player_stats[player]['periods'][current_period]['minutes'] += time_diff / 60
                    player_stats[player]['total_minutes'] += time_diff / 60
            
            # 解析比分
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
            
            # 更新正负值
            if score_change['home'] != 0 or score_change['away'] != 0:
                net_change = score_change['home'] - score_change['away']
                for player in home_on_court:
                    player_stats[player]['periods'][current_period]['plus_minus'] += net_change
                    player_stats[player]['total_plus_minus'] += net_change
                for player in away_on_court:
                    player_stats[player]['periods'][current_period]['plus_minus'] -= net_change
                    player_stats[player]['total_plus_minus'] -= net_change
            
            # 记录事件
            if 'makes' in str(away_event).lower() or 'makes' in str(home_event).lower():
                player = self.extract_player_name(away_event) or self.extract_player_name(home_event)
                if player:
                    action_type = '3PT' if '3-pt' in str(away_event + home_event) else '2PT'
                    player_stats[player]['periods'][current_period]['actions'].append({
                        'type': action_type,
                        'time': time_str,
                        'period': current_period
                    })
                    player_stats[player]['actions'].append({
                        'type': action_type,
                        'time': time_str,
                        'period': current_period
                    })
            
            # 处理换人
            if 'enters' in str(away_event).lower():
                player = self.extract_player_name(away_event)
                if player:
                    home_on_court.add(player)
                    player_stats[player]['on_court_changes'].append({
                        'type': 'enter',
                        'time': time_str,
                        'period': current_period
                    })
            
            if 'leaves' in str(away_event).lower():
                player = self.extract_player_name(away_event)
                if player and player in home_on_court:
                    home_on_court.remove(player)
                    player_stats[player]['on_court_changes'].append({
                        'type': 'leave',
                        'time': time_str,
                        'period': current_period
                    })
            
            if 'enters' in str(home_event).lower():
                player = self.extract_player_name(home_event)
                if player:
                    away_on_court.add(player)
                    player_stats[player]['on_court_changes'].append({
                        'type': 'enter',
                        'time': time_str,
                        'period': current_period
                    })
            
            if 'leaves' in str(home_event).lower():
                player = self.extract_player_name(home_event)
                if player and player in away_on_court:
                    away_on_court.remove(player)
                    player_stats[player]['on_court_changes'].append({
                        'type': 'leave',
                        'time': time_str,
                        'period': current_period
                    })
            
            last_score = current_score.copy()
            last_time = game_time
        
        return player_stats
    
    def generate_game_report(self, game_id, player_stats):
        """生成单场比赛报告"""
        report = []
        
        report.append("=" * 75)
        report.append(f"🏀 单场比赛球员分析报告 - {game_id}")
        report.append("=" * 75)
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("-" * 75)
        
        # 按出场时间排序
        sorted_players = sorted(player_stats.items(), 
                                key=lambda x: x[1]['total_minutes'], 
                                reverse=True)
        
        report.append("\n📊 球员出场时间排名")
        report.append("-" * 40)
        report.append(f"{'排名':<4} {'球员':<15} {'出场时间':>10} {'正负值':>8}")
        report.append(f"---- {'-'*15} {'----------':>10} {'--------':>8}")
        
        for i, (player, stats) in enumerate(sorted_players[:10], 1):
            report.append(f"{i:<4} {player[:15]:<15} {stats['total_minutes']:>9.1f}分钟 {stats['total_plus_minus']:>8}")
        
        report.append("\n📈 每节表现详情")
        report.append("-" * 40)
        
        for player, stats in sorted_players[:5]:
            report.append(f"\n▶️ {player}:")
            report.append(f"   总出场: {stats['total_minutes']:.1f}分钟 | 总正负值: {stats['total_plus_minus']}")
            
            for period in [1, 2, 3, 4]:
                period_stats = stats['periods'][period]
                if period_stats['minutes'] > 0:
                    report.append(f"   第{period}节: {period_stats['minutes']:.1f}分钟 | ±{period_stats['plus_minus']}")
                    
                    if period_stats['actions']:
                        actions_str = ', '.join([f"{a['type']}@{a['time']}" for a in period_stats['actions']])
                        report.append(f"      进攻动作: {actions_str}")
        
        report.append("\n🔄 换人记录")
        report.append("-" * 40)
        
        for player, stats in sorted_players[:5]:
            if stats['on_court_changes']:
                report.append(f"\n▶️ {player}:")
                for change in stats['on_court_changes']:
                    action = '入场' if change['type'] == 'enter' else '离场'
                    report.append(f"   第{change['period']}节 {change['time']} - {action}")
        
        report.append("\n" + "=" * 75)
        report.append("报告结束")
        report.append("=" * 75)
        
        return "\n".join(report)
    
    def analyze_and_report(self):
        """运行分析并生成报告"""
        if not self.pbp_files:
            print("❌ 没有找到PBP数据文件")
            return
        
        # 选择最近的比赛
        latest_file = max(self.pbp_files, key=lambda x: x.stat().st_mtime)
        game_id = latest_file.stem.replace("_pbp", "")
        
        print(f"📊 正在分析比赛: {game_id}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        player_stats = self.analyze_game(data, game_id)
        
        if not player_stats:
            print("❌ 没有找到有效数据")
            return
        
        report = self.generate_game_report(game_id, player_stats)
        
        output_path = BASE_DIR / f"single_game_analysis_{game_id}.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 分析报告已保存到: {output_path}")
        print("\n📋 报告预览:")
        print("-" * 50)
        lines = report.split('\n')
        for line in lines[:30]:
            print(line)
        
        return report

def main():
    print("=" * 75)
    print("🏀 单场比赛球员分析工具")
    print("专注于分析特定比赛中球员的详细表现")
    print("=" * 75)
    
    analyzer = SingleGameAnalyzer()
    analyzer.analyze_and_report()
    
    print("\n🎉 分析完成！")

if __name__ == "__main__":
    main()
