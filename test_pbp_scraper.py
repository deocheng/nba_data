#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Play by Play 爬虫
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, r'c:\autopick\AutoPick')

from nba_data.crawler.play_by_play_scraper import PlayByPlayScraper

def main():
    print("=" * 80)
    print("测试 Play by Play 爬虫")
    print("=" * 80)
    
    # 创建爬虫
    scraper = PlayByPlayScraper(headless=True)
    
    # 测试获取赛程
    print("\n1. 测试获取 2024-2025 赛季赛程...")
    schedule = scraper.scrape_season_schedule(2025)
    
    if not schedule:
        print("❌ 未能获取赛程")
        return
    
    print(f"✅ 成功获取 {len(schedule)} 场比赛")
    print("\n前5场比赛:")
    for i, game in enumerate(schedule[:5], 1):
        print(f"  {i}. {game['date'].strftime('%Y-%m-%d')}: {game['away_team'].value} @ {game['home_team'].value}")
    
    # 测试获取单场比赛数据（只测试1-2场，避免长时间运行）
    print("\n" + "=" * 80)
    print("2. 测试获取单场比赛数据...")
    print("=" * 80)
    
    # 临时缩短延迟时间用于测试
    original_min = scraper.min_delay
    original_max = scraper.max_delay
    scraper.min_delay = 5
    scraper.max_delay = 8
    
    try:
        # 测试获取第一场比赛的数据
        if len(schedule) > 0:
            game_info = schedule[0]
            
            print(f"\n获取第一场比赛的数据...")
            print(f"  时间: {game_info['date'].strftime('%Y-%m-%d')}")
            print(f"  对阵: {game_info['away_team'].value} @ {game_info['home_team'].value}")
            
            pbp_data, game_id = scraper.scrape_play_by_play(game_info)
            if pbp_data:
                print(f"✅ Play by Play 数据: {len(pbp_data)} 条")
                print("  前3条记录:")
                for i, pbp in enumerate(pbp_data[:3], 1):
                    print(f"    {i}. {pbp}")
            
            player_box, team_box = scraper.scrape_box_scores(game_info)
            if player_box:
                print(f"✅ 球员 Box Score 数据: {len(player_box)} 条")
            if team_box:
                print(f"✅ 球队 Box Score 数据: {len(team_box)} 条")
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
