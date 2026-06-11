"""
增强版单场比赛分析工具

支持更详细的进攻数据统计：
1. 出手距离分类（禁区/中距离/三分线外）
2. 终结方式（扣篮/上篮/跳投/抛投等）
3. 投篮位置分布
4. 命中率统计
"""

import json
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BASE_DIR = Path(__file__).parent
PBP_DIR = BASE_DIR / "CSV" / "2026_season" / "pbp"

class EnhancedGameAnalyzer:
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
    
    def parse_shooting_info(self, event):
        """解析投篮信息：距离和终结方式"""
        event_lower = str(event).lower()
        
        # 判断出手距离
        distance = None
        if 'at rim' in event_lower or 'dunk' in event_lower or 'layup' in event_lower:
            distance = '禁区内'
        elif 'short mid' in event_lower or 'mid-range' in event_lower:
            distance = '中距离'
        elif 'long mid' in event_lower:
            distance = '远距离中距离'
        elif '3-pt' in event_lower or 'three' in event_lower:
            distance = '三分线外'
        else:
            distance = '未知'
        
        # 判断终结方式
        finish_type = None
        if 'dunk' in event_lower:
            finish_type = '扣篮'
        elif 'layup' in event_lower:
            finish_type = '上篮'
        elif 'floater' in event_lower:
            finish_type = '抛投'
        elif 'tip shot' in event_lower:
            finish_type = '补篮'
        elif 'bank' in event_lower:
            finish_type = '擦板'
        elif 'fadeaway' in event_lower:
            finish_type = '后仰'
        elif 'step back' in event_lower:
            finish_type = '后撤步'
        elif 'turnaround' in event_lower:
            finish_type = '转身'
        elif 'jumper' in event_lower or 'jump shot' in event_lower:
            finish_type = '跳投'
        else:
            finish_type = '其他'
        
        return distance, finish_type
    
    def analyze_game(self, game_data, game_id):
        """分析单场比赛，包含出手距离和终结方式"""
        player_stats = defaultdict(lambda: {
            'total_shots': 0,
            'made_shots': 0,
            'distance_stats': defaultdict(lambda: {'made': 0, 'attempted': 0}),
            'finish_stats': defaultdict(lambda: {'made': 0, 'attempted': 0}),
            'periods': {1: {'shots': 0, 'made': 0},
                        2: {'shots': 0, 'made': 0},
                        3: {'shots': 0, 'made': 0},
                        4: {'shots': 0, 'made': 0}},
            'shot_details': []
        })
        
        current_period = 1
        
        for row in game_data:
            if 'cells' not in row:
                continue
            
            cells = row['cells']
            if len(cells) < 6:
                continue
            
            time_str = cells[0]
            away_event = cells[1] if cells[1] else ''
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
            
            # 分析投篮事件
            for event in [away_event, home_event]:
                if 'makes' in str(event).lower() or 'misses' in str(event).lower():
                    player = self.extract_player_name(event)
                    if not player:
                        continue
                    
                    distance, finish_type = self.parse_shooting_info(event)
                    is_made = 'makes' in str(event).lower()
                    is_three = '3-pt' in str(event).lower()
                    
                    player_stats[player]['total_shots'] += 1
                    if is_made:
                        player_stats[player]['made_shots'] += 1
                    
                    player_stats[player]['distance_stats'][distance]['attempted'] += 1
                    if is_made:
                        player_stats[player]['distance_stats'][distance]['made'] += 1
                    
                    player_stats[player]['finish_stats'][finish_type]['attempted'] += 1
                    if is_made:
                        player_stats[player]['finish_stats'][finish_type]['made'] += 1
                    
                    player_stats[player]['periods'][current_period]['shots'] += 1
                    if is_made:
                        player_stats[player]['periods'][current_period]['made'] += 1
                    
                    player_stats[player]['shot_details'].append({
                        'time': time_str,
                        'period': current_period,
                        'distance': distance,
                        'finish_type': finish_type,
                        'made': is_made,
                        'three': is_three
                    })
        
        return player_stats
    
    def generate_detailed_report(self, game_id, player_stats):
        """生成详细的投篮分析报告"""
        report = []
        
        report.append("=" * 80)
        report.append(f"🏀 单场比赛投篮分析报告 - {game_id}")
        report.append("=" * 80)
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("-" * 80)
        
        # 按投篮数排序
        sorted_players = sorted(player_stats.items(), 
                                key=lambda x: x[1]['total_shots'], 
                                reverse=True)
        
        report.append("\n📊 球员投篮统计")
        report.append("-" * 40)
        report.append(f"{'排名':<4} {'球员':<15} {'出手':>6} {'命中':>6} {'命中率':>8}")
        report.append(f"---- {'-'*15} {'-----':>6} {'-----':>6} {'--------':>8}")
        
        for i, (player, stats) in enumerate(sorted_players[:10], 1):
            fg_pct = (stats['made_shots'] / stats['total_shots']) * 100 if stats['total_shots'] > 0 else 0
            report.append(f"{i:<4} {player[:15]:<15} {stats['total_shots']:>5} {stats['made_shots']:>6} {fg_pct:>7.1f}%")
        
        report.append("\n🎯 出手距离分布")
        report.append("-" * 40)
        
        for player, stats in sorted_players[:5]:
            report.append(f"\n▶️ {player}:")
            total_shots = stats['total_shots']
            
            for distance, dist_stats in stats['distance_stats'].items():
                if dist_stats['attempted'] > 0:
                    pct = (dist_stats['attempted'] / total_shots) * 100
                    fg_pct = (dist_stats['made'] / dist_stats['attempted']) * 100
                    report.append(f"   {distance}: {dist_stats['attempted']}次 ({pct:.1f}%) | 命中率: {fg_pct:.1f}%")
        
        report.append("\n🏀 终结方式统计")
        report.append("-" * 40)
        
        for player, stats in sorted_players[:5]:
            report.append(f"\n▶️ {player}:")
            
            for finish_type, finish_stats in stats['finish_stats'].items():
                if finish_stats['attempted'] > 0:
                    fg_pct = (finish_stats['made'] / finish_stats['attempted']) * 100
                    report.append(f"   {finish_type}: {finish_stats['made']}/{finish_stats['attempted']} ({fg_pct:.1f}%)")
        
        report.append("\n📈 每节投篮效率")
        report.append("-" * 40)
        
        for player, stats in sorted_players[:3]:
            report.append(f"\n▶️ {player}:")
            for period in [1, 2, 3, 4]:
                period_stats = stats['periods'][period]
                if period_stats['shots'] > 0:
                    fg_pct = (period_stats['made'] / period_stats['shots']) * 100
                    report.append(f"   第{period}节: {period_stats['made']}/{period_stats['shots']} ({fg_pct:.1f}%)")
        
        report.append("\n" + "=" * 80)
        report.append("报告结束")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def analyze_and_report(self):
        """运行分析并生成报告"""
        if not self.pbp_files:
            print("❌ 没有找到PBP数据文件")
            return
        
        latest_file = max(self.pbp_files, key=lambda x: x.stat().st_mtime)
        game_id = latest_file.stem.replace("_pbp", "")
        
        print(f"📊 正在分析比赛: {game_id}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        player_stats = self.analyze_game(data, game_id)
        
        if not player_stats:
            print("❌ 没有找到有效数据")
            return
        
        report = self.generate_detailed_report(game_id, player_stats)
        
        output_path = BASE_DIR / f"shooting_analysis_{game_id}.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 分析报告已保存到: {output_path}")
        print("\n📋 报告预览:")
        print("-" * 50)
        lines = report.split('\n')
        for line in lines[:40]:
            print(line)
        
        return report

def main():
    print("=" * 80)
    print("🏀 增强版单场比赛投篮分析工具")
    print("支持出手距离和终结方式统计")
    print("=" * 80)
    
    analyzer = EnhancedGameAnalyzer()
    analyzer.analyze_and_report()
    
    print("\n🎉 分析完成！")

if __name__ == "__main__":
    main()
