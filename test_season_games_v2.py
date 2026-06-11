#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试从赛季赛程页面获取数据 - 使用requests方式
"""
import sys
import os
import requests
from bs4 import BeautifulSoup

# 添加项目路径
sys.path.insert(0, r'c:\autopick\AutoPick')

def main():
    print("=" * 80)
    print("测试从 NBA_2025_games.html 获取数据")
    print("=" * 80)
    
    # 测试2025赛季（已完成的赛季）
    url = "https://www.basketball-reference.com/leagues/NBA_2025_games.html"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.basketball-reference.com/',
    }
    
    print(f"\n请求URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有比赛
        games_data = []
        
        # 查找月份部分
        month_divs = soup.find_all('div', class_='filter')
        
        for div in month_divs:
            month_header = div.find('h3')
            month_name = month_header.get_text().strip() if month_header else "Unknown"
            
            table = div.find('table')
            if not table:
                continue
            
            rows = table.find_all('tr')
            for row in rows:
                try:
                    # 获取日期
                    date_cell = row.find('td', {'data-stat': 'date_game'})
                    if not date_cell:
                        continue
                    
                    date_str = date_cell.get_text().strip()
                    
                    # 获取球队
                    visitor_cell = row.find('td', {'data-stat': 'visitor_team_name'})
                    home_cell = row.find('td', {'data-stat': 'home_team_name'})
                    
                    visitor_team = visitor_cell.get_text().strip() if visitor_cell else ""
                    home_team = home_cell.get_text().strip() if home_cell else ""
                    
                    # 获取比分
                    visitor_score_cell = row.find('td', {'data-stat': 'visitor_pts'})
                    home_score_cell = row.find('td', {'data-stat': 'home_pts'})
                    
                    visitor_score = visitor_score_cell.get_text().strip() if visitor_score_cell else ""
                    home_score = home_score_cell.get_text().strip() if home_score_cell else ""
                    
                    # 获取boxscore链接
                    boxscore_cell = row.find('td', {'data-stat': 'box_score_text'}).find('a') if row.find('td', {'data-stat': 'box_score_text'}) else None
                    boxscore_url = ""
                    if boxscore_cell:
                        href = boxscore_cell.get('href')
                        if href:
                            boxscore_url = "https://www.basketball-reference.com" + href
                    
                    games_data.append({
                        'month': month_name,
                        'date': date_str,
                        'visitor_team': visitor_team,
                        'home_team': home_team,
                        'visitor_score': visitor_score,
                        'home_score': home_score,
                        'boxscore_url': boxscore_url
                    })
                    
                except Exception as e:
                    continue
        
        print(f"✅ 成功获取 {len(games_data)} 场比赛")
        
        # 统计月份分布
        month_counts = {}
        for game in games_data:
            month = game['month']
            month_counts[month] = month_counts.get(month, 0) + 1
        
        print("\n月份分布:")
        for month, count in sorted(month_counts.items()):
            print(f"  {month}: {count} 场")
        
        # 显示前10场比赛
        print("\n前10场比赛:")
        for i, game in enumerate(games_data[:10], 1):
            score_info = f" {game['visitor_score']} - {game['home_score']}" if game['visitor_score'] else ""
            boxscore_available = "✅" if game['boxscore_url'] else "❌"
            print(f"  {i}. {game['date']}: {game['visitor_team']} @ {game['home_team']}{score_info} {boxscore_available}")
        
        # 测试获取单场比赛的详细数据
        games_with_boxscore = [g for g in games_data if g['boxscore_url']]
        if games_with_boxscore:
            print("\n" + "=" * 80)
            print("测试获取单场比赛详细数据...")
            print("=" * 80)
            
            game = games_with_boxscore[0]
            print(f"\n获取比赛数据: {game['boxscore_url']}")
            
            try:
                response = requests.get(game['boxscore_url'], headers=headers, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 获取球队名称
                team_names = soup.find_all('div', class_='scorebox')
                if team_names:
                    scorebox = team_names[0]
                    team_links = scorebox.find_all('a')
                    if len(team_links) >= 2:
                        away_team = team_links[0].get_text().strip()
                        home_team = team_links[1].get_text().strip()
                        print(f"  客队: {away_team}")
                        print(f"  主队: {home_team}")
                
                # 获取比分
                scores = soup.find_all('div', class_='score')
                if len(scores) >= 2:
                    away_score = scores[0].get_text().strip()
                    home_score = scores[1].get_text().strip()
                    print(f"  比分: {away_score} - {home_score}")
                
                # 获取球员统计
                tables = soup.find_all('table', {'id': lambda x: x and '_basic' in x})
                player_stats = []
                
                for table in tables:
                    team_abbr = table.get('id').split('_')[0] if table.get('id') else 'unknown'
                    
                    headers = []
                    th_elements = table.find('thead').find_all('th')
                    for th in th_elements:
                        headers.append(th.get_text().strip())
                    
                    rows = table.find('tbody').find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        player_data = {'team': team_abbr}
                        for i, cell in enumerate(cells):
                            if i < len(headers):
                                player_data[headers[i]] = cell.get_text().strip()
                        if player_data.get('Player') and player_data['Player'] != 'Team Totals':
                            player_stats.append(player_data)
                
                print(f"  球员数: {len(player_stats)}")
                
                print("\n  球员数据示例:")
                for player in player_stats[:5]:
                    print(f"    {player.get('Player')}: {player.get('PTS')}分 {player.get('TRB')}篮板 {player.get('AST')}助攻")
                
            except Exception as e:
                print(f"❌ 获取比赛数据失败: {e}")
        
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("✅ 测试完成")
    print("=" * 80)

if __name__ == "__main__":
    main()
