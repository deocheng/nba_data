"""
系列赛对位分析工具

针对季后赛系列赛中两队球员的对位表现进行深度分析：
1. 球员对位记录追踪
2. 对位时的正负值
3. 进攻效率对比
4. 防守效果评估
5. 关键比赛对位表现
"""

import json
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BASE_DIR = Path(__file__).parent
PBP_DIR = BASE_DIR / "CSV" / "2026_season" / "pbp"

class PlayoffSeriesAnalyzer:
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
    
    def analyze_series(self, team_a_players, team_b_players):
        """分析系列赛中两队球员的对位情况"""
        # 存储对位数据
        matchup_data = defaultdict(lambda: {
            'games': 0,
            'minutes_together': 0,
            'plus_minus': 0,
            'offensive_actions': [],
            'defensive_actions': []
        })
        
        for filepath in self.pbp_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                game_id = filepath.stem.replace("_pbp", "")
                
                home_on_court = set()
                away_on_court = set()
                current_period = 1
                last_score = {'home': 0, 'away': 0}
                last_time = 720
                
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
                    if '1st' in time_lower or 'q1' in time_str:
                        current_period = 1
                    elif '2nd' in time_lower or 'q2' in time_str:
                        current_period = 2
                    elif '3rd' in time_lower or 'q3' in time_str:
                        current_period = 3
                    elif '4th' in time_lower or 'q4' in time_str:
                        current_period = 4
                    
                    game_time = self.parse_time(time_str)
                    if game_time is None:
                        game_time = 720 - (current_period - 1) * 720
                    
                    time_diff = last_time - game_time
                    if time_diff > 0 and time_diff < 300:
                        # 检查对位组合
                        team_a_on_court = [p for p in home_on_court if p in team_a_players]
                        team_b_on_court = [p for p in away_on_court if p in team_b_players]
                        
                        for a_player in team_a_on_court:
                            for b_player in team_b_on_court:
                                matchup_key = (a_player, b_player)
                                matchup_data[matchup_key]['minutes_together'] += time_diff / 60
                                matchup_data[matchup_key]['games'] += 1
                    
                    # 处理得分事件
                    if 'makes' in str(away_event).lower():
                        player = self.extract_player_name(away_event)
                        if player and player in team_b_players:
                            for a_player in home_on_court:
                                if a_player in team_a_players:
                                    matchup_data[(a_player, player)]['offensive_actions'].append({
                                        'game': game_id,
                                        'period': current_period,
                                        'time': time_str,
                                        'type': '3PT' if '3-pt' in away_event else '2PT'
                                    })
                    
                    if 'makes' in str(home_event).lower():
                        player = self.extract_player_name(home_event)
                        if player and player in team_a_players:
                            for b_player in away_on_court:
                                if b_player in team_b_players:
                                    matchup_data[(player, b_player)]['offensive_actions'].append({
                                        'game': game_id,
                                        'period': current_period,
                                        'time': time_str,
                                        'type': '3PT' if '3-pt' in home_event else '2PT'
                                    })
                    
                    # 处理换人
                    if 'enters' in str(away_event).lower():
                        player = self.extract_player_name(away_event)
                        if player:
                            away_on_court.add(player)
                    if 'leaves' in str(away_event).lower():
                        player = self.extract_player_name(away_event)
                        if player and player in away_on_court:
                            away_on_court.remove(player)
                    
                    if 'enters' in str(home_event).lower():
                        player = self.extract_player_name(home_event)
                        if player:
                            home_on_court.add(player)
                    if 'leaves' in str(home_event).lower():
                        player = self.extract_player_name(home_event)
                        if player and player in home_on_court:
                            home_on_court.remove(player)
                    
                    last_time = game_time
            
            except Exception:
                continue
        
        return matchup_data
    
    def generate_series_report(self, team_a_name, team_a_players, team_b_name, team_b_players):
        """生成系列赛对位报告"""
        matchup_data = self.analyze_series(team_a_players, team_b_players)
        
        report = []
        
        report.append("=" * 80)
        report.append(f"🏆 {team_a_name} vs {team_b_name} 系列赛对位分析")
        report.append("=" * 80)
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"分析比赛: {len(self.pbp_files)} 场")
        report.append("-" * 80)
        
        if not matchup_data:
            report.append("⚠️ 没有找到有效的对位数据")
            return "\n".join(report)
        
        report.append(f"\n📊 {team_a_name} 球员名单: {', '.join(team_a_players)}")
        report.append(f"📊 {team_b_name} 球员名单: {', '.join(team_b_players)}")
        
        report.append("\n🔥 对位统计详情")
        report.append("-" * 40)
        report.append(f"{'A队球员':<15} {'B队球员':<15} {'对位时间':>10} {'进攻次数':>10}")
        report.append(f"{'---------':<15} {'---------':<15} {'----------':>10} {'----------':>10}")
        
        for (a_player, b_player), data in sorted(matchup_data.items(), 
                                                 key=lambda x: x[1]['minutes_together'],
                                                 reverse=True):
            report.append(f"{a_player[:15]:<15} {b_player[:15]:<15} {data['minutes_together']:>9.1f}分钟 {len(data['offensive_actions']):>10}")
        
        report.append("\n🎯 重点对位分析")
        report.append("-" * 40)
        
        # 找出对位时间最长的组合
        top_matchups = sorted(matchup_data.items(), 
                              key=lambda x: x[1]['minutes_together'],
                              reverse=True)[:5]
        
        for (a_player, b_player), data in top_matchups:
            report.append(f"\n▶️ {a_player} vs {b_player}")
            report.append(f"   对位时间: {data['minutes_together']:.1f}分钟")
            report.append(f"   进攻回合: {len(data['offensive_actions'])}次")
            
            if data['offensive_actions']:
                report.append("   关键进攻事件:")
                for action in data['offensive_actions'][-5:]:
                    report.append(f"      - 第{action['period']}节 {action['time']}: {action['type']}命中")
        
        report.append("\n📈 对位效率分析")
        report.append("-" * 40)
        
        for (a_player, b_player), data in top_matchups:
            if data['minutes_together'] > 0:
                freq = len(data['offensive_actions']) / data['minutes_together']
                report.append(f"{a_player} vs {b_player}: 每分钟进攻 {freq:.2f} 次")
        
        report.append("\n" + "=" * 80)
        report.append("报告结束")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_report(self, team_a_name, team_b_name, report):
        """保存报告"""
        filename = f"series_matchup_{team_a_name.lower()}_{team_b_name.lower()}.txt"
        output_path = BASE_DIR / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ 分析报告已保存到: {output_path}")
        return output_path

def main():
    print("=" * 80)
    print("🏆 季后赛系列赛对位分析工具")
    print("分析两队球员在系列赛中的对位表现")
    print("=" * 80)
    
    analyzer = PlayoffSeriesAnalyzer()
    
    # 示例：马刺 vs 尼克斯系列赛
    team_a_name = "Spurs"
    team_a_players = {'V.Wembanyama', 'D.Fox', 'D.Vassell', 'K.Johnson', 'S.Castle'}
    
    team_b_name = "Knicks"  
    team_b_players = {'J.Brunson', 'K.Towns', 'M.Bridges', 'OG.Anunoby', 'J.Hart'}
    
    report = analyzer.generate_series_report(team_a_name, team_a_players, 
                                            team_b_name, team_b_players)
    
    print("\n📋 报告预览:")
    print("-" * 50)
    lines = report.split('\n')
    for line in lines[:40]:
        print(line)
    
    analyzer.save_report(team_a_name, team_b_name, report)
    
    print("\n🎉 分析完成！")

if __name__ == "__main__":
    main()
