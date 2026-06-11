#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的 NBA 数据爬取脚本
从 Basketball Reference 爬取整个赛季的比赛数据和 play-by-play
"""
import sys
import os
import json
import pandas as pd

# 添加项目路径
sys.path.insert(0, r'c:\autopick\AutoPick')

from nba_data.crawler.play_by_play_scraper import PlayByPlayScraper

def main():
    print("=" * 80)
    print("NBA 赛季数据爬取脚本")
    print("=" * 80)
    
    # 创建爬虫
    scraper = PlayByPlayScraper(headless=True)
    
    # 要爬取的赛季
    season_end_year = 2026
    
    # 要爬取的月份（NBA赛季：10月到次年6月）
    months = ['october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june']
    
    # 输出目录
    output_dir = f"nba_data/CSV/{season_end_year}_season"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 爬取所有月份的比赛列表（只获取有boxscore的比赛）
    print(f"\n1. 爬取 {season_end_year} 赛季所有月份的比赛...")
    all_games = scraper.scrape_season_all_months(season_end_year, months)
    
    if not all_games:
        print("❌ 未获取到任何比赛数据")
        return
    
    print(f"✅ 共获取 {len(all_games)} 场有boxscore的比赛")
    
    # 保存比赛列表
    games_df = pd.DataFrame(all_games)
    games_file = os.path.join(output_dir, f"all_games_{season_end_year}.csv")
    games_df.to_csv(games_file, index=False, encoding='utf-8-sig')
    print(f"\n✓ 比赛列表已保存到: {games_file}")
    
    # 2. 爬取每场比赛的详细数据
    print("\n" + "=" * 80)
    print("2. 爬取比赛详细数据...")
    print("=" * 80)
    
    # 只处理前N场比赛用于测试（去掉注释以处理全部）
    games_to_process = all_games[:10]  # 测试：只处理前10场
    # games_to_process = all_games  # 生产：处理全部
    
    boxscores_dir = os.path.join(output_dir, 'boxscores')
    pbp_dir = os.path.join(output_dir, 'pbp')
    os.makedirs(boxscores_dir, exist_ok=True)
    os.makedirs(pbp_dir, exist_ok=True)
    
    success_count = 0
    fail_count = 0
    
    for i, game in enumerate(games_to_process, 1):
        print(f"\n处理第 {i}/{len(games_to_process)} 场")
        print(f"  日期: {game['date']}")
        print(f"  对阵: {game['visitor_team']} @ {game['home_team']}")
        print(f"  Boxscore URL: {game['boxscore_url']}")
        
        # 生成文件名
        date_str = game['date'].replace('/', '-')
        filename_base = f"{date_str}_{game['visitor_team']}_{game['home_team']}"
        
        # 获取 boxscore 数据
        boxscore = scraper.scrape_single_boxscore(game['boxscore_url'])
        
        if boxscore:
            # 保存 boxscore
            boxscore_df = pd.DataFrame(boxscore['player_stats'])
            boxscore_file = os.path.join(boxscores_dir, f"{filename_base}_boxscore.csv")
            boxscore_df.to_csv(boxscore_file, index=False, encoding='utf-8-sig')
            
            # 获取 play-by-play 数据
            pbp_data = scraper.scrape_play_by_play_data(game['boxscore_url'])
            
            if pbp_data:
                pbp_df = pd.DataFrame(pbp_data)
                pbp_file = os.path.join(pbp_dir, f"{filename_base}_pbp.csv")
                pbp_df.to_csv(pbp_file, index=False, encoding='utf-8-sig')
                print(f"  ✅ 成功获取 boxscore 和 pbp 数据")
            else:
                print(f"  ⚠️ 获取 boxscore 成功，但 pbp 数据为空")
            
            success_count += 1
        else:
            print(f"  ❌ 获取失败")
            fail_count += 1
        
        # 检查是否需要休息
        scraper._check_and_rest()
        
        # 防封锁延迟（不是最后一场）
        if i < len(games_to_process):
            scraper._safe_random_delay()
    
    print("\n" + "=" * 80)
    print("爬取完成！")
    print(f"成功: {success_count} 场")
    print(f"失败: {fail_count} 场")
    print(f"输出目录: {output_dir}")
    print("=" * 80)

if __name__ == "__main__":
    main()
