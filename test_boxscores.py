#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Box Scores 爬虫
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, r'c:\autopick\AutoPick')

from nba_data.crawler.play_by_play_scraper import PlayByPlayScraper

def main():
    print("=" * 80)
    print("测试 Box Scores 爬虫")
    print("=" * 80)
    
    # 创建爬虫
    scraper = PlayByPlayScraper(headless=True)
    
    # 测试获取每日 boxscores
    print("\n1. 测试获取每日 boxscores...")
    print("-" * 80)
    
    # 测试日期（使用过去的日期，确保有数据）
    year, month, day = 2025, 1, 15
    
    games = scraper.scrape_daily_boxscores(year, month, day)
    
    if not games:
        print("❌ 未能获取数据")
        return
    
    print(f"✅ 成功获取 {len(games)} 场比赛")
    print("\n比赛列表:")
    for i, game in enumerate(games[:3], 1):
        print(f"  {i}. {game['teams'][0]} @ {game['teams'][1]}")
        print(f"     URL: {game['url']}")
    
    # 测试获取单场比赛的详细数据
    if len(games) > 0:
        print("\n" + "=" * 80)
        print("2. 测试获取单场比赛详细数据...")
        print("=" * 80)
        
        # 临时缩短延迟
        original_min = scraper.min_delay
        original_max = scraper.max_delay
        scraper.min_delay = 5
        scraper.max_delay = 8
        
        try:
            game_url = games[0]['url']
            print(f"\n获取比赛数据: {game_url}")
            
            boxscore = scraper.scrape_single_boxscore(game_url)
            
            if boxscore:
                print(f"\n✅ 比赛信息:")
                print(f"  客队: {boxscore.get('away_team')}")
                print(f"  主队: {boxscore.get('home_team')}")
                print(f"  比分: {boxscore.get('away_score')} - {boxscore.get('home_score')}")
                print(f"  球员数: {len(boxscore.get('player_stats', []))}")
                
                print("\n  球员数据示例:")
                for player in boxscore['player_stats'][:3]:
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
