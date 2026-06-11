#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的比赛详细数据爬取脚本
从 Basketball Reference 爬取 boxscore 和 play-by-play 数据
"""
import os
import sys
import pandas as pd
import logging
from datetime import datetime

# 添加项目路径
sys.path.insert(0, r'c:\autopick\AutoPick')

from nba_data.crawler.play_by_play_scraper import PlayByPlayScraper

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    print("=" * 80)
    print("NBA 比赛详细数据爬取脚本")
    print("=" * 80)
    
    # 创建爬虫（40秒延迟）
    scraper = PlayByPlayScraper(headless=True, min_delay=40, max_delay=40)
    
    # 加载已保存的比赛列表
    season_end_year = 2026
    games_file = f'CSV/{season_end_year}_season/all_games_{season_end_year}.csv'
    
    if not os.path.exists(games_file):
        print(f"❌ 文件不存在: {games_file}")
        return
    
    games_df = pd.read_csv(games_file, encoding='utf-8-sig')
    print(f"✅ 加载到 {len(games_df)} 场比赛")
    
    # 输出目录
    output_dir = f'CSV/{season_end_year}_season'
    boxscores_dir = os.path.join(output_dir, 'boxscores')
    pbp_dir = os.path.join(output_dir, 'pbp')
    
    os.makedirs(boxscores_dir, exist_ok=True)
    os.makedirs(pbp_dir, exist_ok=True)
    
    # 检查进度文件
    progress_file = os.path.join(output_dir, 'scrape_progress.json')
    processed = set()
    
    if os.path.exists(progress_file):
        import json
        with open(progress_file, 'r', encoding='utf-8') as f:
            processed = set(json.load(f))
        print(f"✅ 已处理 {len(processed)} 场比赛")
    
    # 过滤未处理的比赛
    games_to_process = games_df[~games_df['boxscore_url'].isin(processed)]
    
    print(f"\n待处理比赛数: {len(games_to_process)}")
    print(f"总进度: {len(processed)}/{len(games_df)} ({len(processed)/len(games_df)*100:.1f}%)")
    
    # 先测试爬取5场比赛
    test_count = min(10, len(games_to_process))
    print(f"\n先测试爬取 {test_count} 场比赛...")
    print("=" * 80)
    
    success_count = 0
    fail_count = 0
    
    for i, game in games_to_process.head(test_count).iterrows():
        game_index = i + 1
        print(f"\n处理第 {game_index}/{test_count} 场")
        print(f"  对阵: {game['visitor_team']} @ {game['home_team']}")
        print(f"  比分: {game['visitor_score']} - {game['home_score']}")
        print(f"  Boxscore URL: {game['boxscore_url']}")
        
        try:
            # 提取日期从URL
            # URL 格式: https://www.basketball-reference.com/boxscores/202510210OKC.html
            url_parts = game['boxscore_url'].split('/')
            game_key = url_parts[-1].replace('.html', '')
            
            # 生成文件名（从URL中提取日期和球队）
            filename_base = game_key
            
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
                    print(f"  ✅ 成功获取 boxscore ({len(boxscore_df)} 球员) 和 pbp ({len(pbp_df)} 条)")
                else:
                    print(f"  ⚠️ 获取 boxscore 成功，但 pbp 数据为空")
                
                success_count += 1
                processed.add(game['boxscore_url'])
                
                # 保存进度
                import json
                with open(progress_file, 'w', encoding='utf-8') as f:
                    json.dump(list(processed), f)
                
            else:
                print(f"  ❌ 获取失败")
                fail_count += 1
                
        except Exception as e:
            print(f"  ❌ 处理异常: {e}")
            fail_count += 1
            import traceback
            traceback.print_exc()
        
        # 防封锁延迟（不是最后一场）
        if i < len(games_to_process.head(test_count)) - 1:
            scraper._safe_random_delay()
    
    print("\n" + "=" * 80)
    print("测试爬取完成！")
    print(f"成功: {success_count} 场")
    print(f"失败: {fail_count} 场")
    print(f"输出目录: {output_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()
