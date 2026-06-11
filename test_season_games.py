#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试从赛季赛程页面获取数据
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, r'c:\autopick\AutoPick')

from nba_data.crawler.play_by_play_scraper import PlayByPlayScraper

def main():
    print("=" * 80)
    print("测试从 NBA_2026_games.html 获取数据")
    print("=" * 80)
    
    # 创建爬虫
    scraper = PlayByPlayScraper(headless=True)
    
    # 测试获取赛季赛程页面
    print("\n1. 测试获取赛季赛程页面...")
    print("-" * 80)
    
    # 测试2026赛季
    games = scraper.scrape_season_games_page(2026)
    
    if not games:
        print("❌ 未能获取数据")
        return
    
    print(f"✅ 成功获取 {len(games)} 场比赛")
    
    # 统计月份分布
    month_counts = {}
    for game in games:
        month = game['month']
        month_counts[month] = month_counts.get(month, 0) + 1
    
    print("\n月份分布:")
    for month, count in sorted(month_counts.items()):
        print(f"  {month}: {count} 场")
    
    # 显示前10场比赛
    print("\n前10场比赛:")
    for i, game in enumerate(games[:10], 1):
        score_info = f" {game['visitor_score']} - {game['home_score']}" if game['visitor_score'] else ""
        boxscore_available = "✅" if game['boxscore_url'] else "❌"
        print(f"  {i}. {game['date']}: {game['visitor_team']} @ {game['home_team']}{score_info} {boxscore_available}")
    
    # 测试获取单场比赛的详细数据
    games_with_boxscore = [g for g in games if g['boxscore_url']]
    if games_with_boxscore:
        print("\n" + "=" * 80)
        print("2. 测试获取单场比赛详细数据...")
        print("=" * 80)
        
        # 临时缩短延迟
        original_min = scraper.min_delay
        original_max = scraper.max_delay
        scraper.min_delay = 5
        scraper.max_delay = 8
        
        try:
            game = games_with_boxscore[0]
            print(f"\n获取比赛数据:")
            print(f"  日期: {game['date']}")
            print(f"  对阵: {game['visitor_team']} @ {game['home_team']}")
            print(f"  Boxscore URL: {game['boxscore_url']}")
            
            boxscore = scraper.scrape_single_boxscore(game['boxscore_url'])
            
            if boxscore:
                print(f"\n✅ 比赛信息:")
                print(f"  客队: {boxscore.get('away_team')}")
                print(f"  主队: {boxscore.get('home_team')}")
                print(f"  比分: {boxscore.get('away_score')} - {boxscore.get('home_score')}")
                print(f"  球员数: {len(boxscore.get('player_stats', []))}")
                
                print("\n  球员数据示例:")
                for player in boxscore['player_stats'][:5]:
                    print(f"    {player.get('Player')}: {player.get('PTS')}分 {player.get('TRB')}篮板 {player.get('AST')}助攻")
            else:
                print("❌ 未能获取比赛数据")
        except Exception as e:
            print(f"❌ 测试出错: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # 恢复原延迟
            scraper.min_delay = original_min
            scraper.max_delay = original_max
    
    print("\n" + "=" * 80)
    print("✅ 测试完成")
    print("=" * 80)

if __name__ == "__main__":
    main()
