#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NBA League Leaders 数据分析系统
用于解析、分类和查询2025-26赛季常规赛各项数据排行榜
"""
import pandas as pd
import re
import json
import os

class LeagueLeadersAnalyzer:
    """NBA联盟领袖数据分析器"""

    def __init__(self, excel_path='nba_data/CSV/league leaders 2025-26 .xlsx'):
        """
        初始化分析器

        Args:
            excel_path: Excel文件路径
        """
        self.excel_path = excel_path
        self.data = {}  # 存储分类后的数据
        self.players = {}  # 球员索引
        self.teams = {}  # 球队索引
        self.load_and_parse()

    def load_and_parse(self):
        """加载并解析Excel文件"""
        df = pd.read_excel(self.excel_path)
        data = df['League Leaders'].tolist()

        current_category = None
        category_data = []

        for idx, row in enumerate(data):
            row = str(row).strip()
            
            # 跳过空行和查看全部链接
            if not row or row.startswith('View all'):
                if current_category and category_data:
                    self.data[current_category] = category_data
                    category_data = []
                current_category = None
                continue

            # 检查是否是统计类别（不以数字开头）
            if not row[0].isdigit():
                if current_category and category_data:
                    self.data[current_category] = category_data
                
                current_category = row
                category_data = []
                continue

            # 解析排名数据
            # 格式: 排名.球员名 • 球队数据值
            match = re.match(r'^(\d+)\.(.+?)•(.+?)([\d.]+)$', row)
            if match:
                rank = int(match.group(1))
                player = match.group(2).strip()
                team = match.group(3).strip()
                value = float(match.group(4)) if '.' in match.group(4) else int(match.group(4))

                category_data.append({
                    'rank': rank,
                    'player': player,
                    'team': team,
                    'value': value
                })

                # 更新球员索引
                if player not in self.players:
                    self.players[player] = []
                self.players[player].append({
                    'category': current_category,
                    'rank': rank,
                    'team': team,
                    'value': value
                })

                # 更新球队索引
                if team not in self.teams:
                    self.teams[team] = []
                self.teams[team].append({
                    'category': current_category,
                    'rank': rank,
                    'player': player,
                    'value': value
                })

        # 处理最后一个类别
        if current_category and category_data:
            self.data[current_category] = category_data

        print(f'✅ 成功解析 {len(self.data)} 个统计类别，共 {len(self.players)} 名球员')

    def get_all_categories(self):
        """获取所有统计类别"""
        return list(self.data.keys())

    def get_category_data(self, category):
        """获取指定类别的数据"""
        return self.data.get(category, [])

    def get_team_leaders(self, team_abbr):
        """获取指定球队的上榜球员"""
        return sorted(self.teams.get(team_abbr, []), key=lambda x: x['rank'])

    def get_player_rankings(self, player_name):
        """获取指定球员的所有排名"""
        return sorted(self.players.get(player_name, []), key=lambda x: x['rank'])

    def search_player(self, keyword):
        """搜索球员（支持模糊匹配）"""
        results = []
        for player in self.players:
            if keyword.lower() in player.lower():
                results.append(player)
        return sorted(results)

    def search_team(self, keyword):
        """搜索球队（支持模糊匹配）"""
        results = []
        for team in self.teams:
            if keyword.lower() in team.lower():
                results.append(team)
        return sorted(results)

    def compare_players(self, player1, player2):
        """比较两名球员的排名"""
        p1_data = self.get_player_rankings(player1)
        p2_data = self.get_player_rankings(player2)
        
        comparison = []
        all_categories = set([x['category'] for x in p1_data] + [x['category'] for x in p2_data])
        
        for cat in all_categories:
            p1_rank = next((x for x in p1_data if x['category'] == cat), None)
            p2_rank = next((x for x in p2_data if x['category'] == cat), None)
            
            comparison.append({
                'category': cat,
                player1: p1_rank,
                player2: p2_rank
            })
        
        return sorted(comparison, key=lambda x: (x[player1]['rank'] if x[player1] else 999, 
                                                x[player2]['rank'] if x[player2] else 999))

    def save_to_json(self, output_path='league_leaders_data.json'):
        """将数据保存到JSON文件"""
        data = {
            'categories': self.data,
            'players': self.players,
            'teams': self.teams
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f'✅ 数据已保存到 {output_path}')

    def print_team_leaders(self, team_abbr):
        """打印球队上榜球员"""
        leaders = self.get_team_leaders(team_abbr)
        
        if not leaders:
            print(f'❌ 球队 {team_abbr} 没有球员上榜')
            return
        
        print(f'\n🏀 {team_abbr} 球队上榜球员（共 {len(leaders)} 人）')
        print('-' * 70)
        
        for item in leaders:
            rank = item['rank'] if item['rank'] else 0
            category = item['category'] if item['category'] else 'Unknown'
            player = item['player'] if item['player'] else 'Unknown'
            value = item['value'] if item['value'] is not None else 0
            print(f"  #{rank:2d} {category:<25} {player:<25} {value}")

    def print_player_rankings(self, player_name):
        """打印球员排名"""
        rankings = self.get_player_rankings(player_name)
        
        if not rankings:
            print(f'❌ 未找到球员 "{player_name}" 的数据')
            return
        
        print(f'\n🎯 {player_name} 的排名情况（共 {len(rankings)} 项）')
        print('-' * 70)
        
        for item in rankings:
            rank = item['rank'] if item['rank'] else 0
            category = item['category'] if item['category'] else 'Unknown'
            team = item['team'] if item['team'] else 'XXX'
            value = item['value'] if item['value'] is not None else 0
            print(f"  #{rank:2d} {category:<25} {team:5} {value}")

    def print_category(self, category):
        """打印指定类别的排名"""
        data = self.get_category_data(category)
        
        if not data:
            print(f'❌ 未找到类别 "{category}"')
            return
        
        print(f'\n📊 {category} 排行榜（前20名）')
        print('-' * 70)
        
        for item in data:
            print(f"  #{item['rank']:2d} {item['player']:<25} {item['team']:5} {item['value']}")

    def print_all_categories(self):
        """打印所有统计类别"""
        print('\n📋 所有统计类别:')
        print('-' * 50)
        for i, cat in enumerate(self.get_all_categories(), 1):
            count = len(self.data[cat])
            print(f'  {i:2d}. {cat} ({count}人)')

# 创建全局实例
analyzer = None

def init_analyzer():
    """初始化分析器"""
    global analyzer
    analyzer = LeagueLeadersAnalyzer()
    return analyzer

def main():
    """命令行交互界面"""
    print('=' * 70)
    print('    NBA 2025-26赛季联盟领袖数据查询系统')
    print('=' * 70)
    print('支持的查询功能:')
    print('  1. 查询球队上榜球员（如：马刺、LAL）')
    print('  2. 查询球员排名（如：勒布朗、东契奇）')
    print('  3. 比较两名球员（如：詹姆斯 vs 东契奇）')
    print('  4. 查看所有统计类别')
    print('  5. 查看指定类别排名（如：Points）')
    print('  6. 搜索球员')
    print('  7. 退出')
    print('=' * 70)

    # 初始化
    global analyzer
    if not analyzer:
        print('正在加载数据...')
        analyzer = LeagueLeadersAnalyzer()
    
    while True:
        print('\n请输入查询（输入 "help" 显示帮助，"quit" 退出）:')
        query = input('>>> ').strip()
        
        if not query:
            continue
        
        if query.lower() in ['quit', 'exit', 'q']:
            print('👋 再见！')
            break
        
        if query.lower() in ['help', 'h']:
            print('\n帮助信息:')
            print('  - 输入球队缩写（如 SAS、LAL、OKC）查看该队上榜球员')
            print('  - 输入球员名字（如 LeBron James、Luka Dončić）查看排名')
            print('  - 输入 "vs" 比较两名球员（如 LeBron vs Luka）')
            print('  - 输入 "categories" 查看所有统计类别')
            print('  - 输入类别名称（如 Points）查看该类别排名')
            print('  - 输入 "search 关键词" 搜索球员')
            continue
        
        if query.lower() == 'categories':
            analyzer.print_all_categories()
            continue
        
        if query.lower().startswith('search '):
            keyword = query[7:].strip()
            results = analyzer.search_player(keyword)
            if results:
                print(f'\n找到 {len(results)} 名球员:')
                for player in results[:10]:
                    print(f'  - {player}')
                if len(results) > 10:
                    print(f'  ...还有 {len(results) - 10} 名球员')
            else:
                print(f'\n❌ 未找到包含 "{keyword}" 的球员')
            continue
        
        if ' vs ' in query:
            parts = query.split(' vs ')
            if len(parts) == 2:
                p1, p2 = parts[0].strip(), parts[1].strip()
                comparison = analyzer.compare_players(p1, p2)
                
                print(f'\n⚔️ {p1} vs {p2} 对比')
                print('-' * 80)
                print(f"{'类别':<25} | {p1:<20} | {p2:<20}")
                print('-' * 80)
                
                for item in comparison:
                    p1_info = f"#{item[p1]['rank']} ({item[p1]['value']})" if item[p1] else '-'
                    p2_info = f"#{item[p2]['rank']} ({item[p2]['value']})" if item[p2] else '-'
                    print(f"{item['category']:<25} | {p1_info:<20} | {p2_info:<20}")
            continue
        
        # 尝试作为球队查询
        team_result = analyzer.get_team_leaders(query.upper())
        if team_result:
            analyzer.print_team_leaders(query.upper())
            continue
        
        # 尝试作为球员查询
        player_results = analyzer.search_player(query)
        if len(player_results) == 1:
            analyzer.print_player_rankings(player_results[0])
            continue
        elif len(player_results) > 1:
            print(f'\n找到多个匹配的球员:')
            for p in player_results[:5]:
                print(f'  - {p}')
            print('请输入更精确的名字')
            continue
        
        # 尝试作为类别查询
        category_result = analyzer.get_category_data(query)
        if category_result:
            analyzer.print_category(query)
            continue
        
        print(f'\n❌ 未找到 "{query}" 的数据，请尝试其他查询')

if __name__ == '__main__':
    main()
