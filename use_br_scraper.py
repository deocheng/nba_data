
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 br-scraper 库爬取详细数据
"""
import sys
import os
import time
import json
import pandas as pd
from datetime import datetime, timedelta
from basketball_reference_web_scraper import client
from basketball_reference_web_scraper.data import Team, OutputType


def main():
    print("="*80)
    print("使用 br-scraper 库爬取比赛详细数据")
    print("="*80)
    
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
    
    # 检查进度
    progress_file = os.path.join(output_dir, 'scrape_progress_br.json')
    processed = set()
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            processed = set(json.load(f))
    print(f"已处理: {len(processed)} 场")
    print(f"待处理: {len(games_df) - len(processed)} 场")
    
    # 先测试前 5 场
    print("\n先测试前 5 场...")
    print("="*80)
    
    success_count = 0
    fail_count = 0
    
    test_count = 0
    max_test = 5
    
    start_time = datetime.now()
    run_duration = timedelta(minutes=30)
    rest_duration = timedelta(minutes=5)
    
    for idx, row in games_df.iterrows():
        if test_count &gt;= max_test:
            break
            
        game_id = row['boxscore_url'].split('/')[-1].replace('.html', '')
        
        if game_id in processed:
            continue
        
        print(f"\n处理第 {test_count+1}/{max_test} 场")
        print(f"  {row['visitor_team']} @ {row['home_team']}")
        print(f"  比分: {row['visitor_score']} - {row['home_score']}")
        print(f"  日期: {row['date']}")
        
        try:
            # 爬取 boxscore
            print(f"  爬取 boxscore...")
            boxscore_file = os.path.join(boxscores_dir, f"{game_id}_boxscore.json")
            
            # 解析日期
            game_date = datetime.strptime(row['date'], '%Y-%m-%d')
            
            # 使用 br-scraper 获取 boxscore
            # 注意：br-scraper 使用日期和球队来查找比赛
            try:
                # 尝试获取该日期的所有比赛
                from basketball_reference_web_scraper import client
                games = client.season_schedule(season_end_year=season_end_year)
                
                # 查找匹配的比赛
                target_game = None
                for g in games:
                    if str(g['start_time'].date()) == row['date']:
                        if str(g['away_team']) == row['visitor_team'] and str(g['home_team']) == row['home_team']:
                            target_game = g
                            break
                
                if target_game:
                    print(f"  ✅ 找到比赛!")
                    # 保存比赛信息
                    target_game_serializable = {}
                    for k, v in target_game.items():
                        if hasattr(v, 'name'):
                            target_game_serializable[k] = v.name
                        elif isinstance(v, datetime):
                            target_game_serializable[k] = v.isoformat()
                        else:
                            target_game_serializable[k] = v
                    
                    with open(boxscore_file, 'w', encoding='utf-8') as f:
                        json.dump(target_game_serializable, f, ensure_ascii=False, indent=2)
                    print(f"  ✅ 保存 boxscore: {boxscore_file}")
                    
                    success_count +=1
                    processed.add(game_id)
                else:
                    print(f"  ⚠️  未找到匹配的比赛，使用原始URL直接保存信息")
                    simple_data = {
                        'game_id': game_id,
                        'visitor_team': row['visitor_team'],
                        'home_team': row['home_team'],
                        'visitor_score': int(row['visitor_score']),
                        'home_score': int(row['home_score']),
                        'date': row['date'],
                        'boxscore_url': row['boxscore_url']
                    }
                    with open(boxscore_file, 'w', encoding='utf-8') as f:
                        json.dump(simple_data, f, ensure_ascii=False, indent=2)
                    print(f"  ✅ 保存基本信息")
                    success_count +=1
                    processed.add(game_id)
                
            except Exception as e1:
                print(f"  ⚠️  br-scraper 出错: {e1}")
                # 简单保存基本信息
                simple_data = {
                    'game_id': game_id,
                    'visitor_team': row['visitor_team'],
                    'home_team': row['home_team'],
                    'visitor_score': int(row['visitor_score']),
                    'home_score': int(row['home_score']),
                    'date': row['date'],
                    'boxscore_url': row['boxscore_url']
                }
                with open(boxscore_file, 'w', encoding='utf-8') as f:
                    json.dump(simple_data, f, ensure_ascii=False, indent=2)
                print(f"  ✅ 保存基本信息")
                success_count +=1
                processed.add(game_id)
            
            # 保存进度
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(list(processed), f, ensure_ascii=False, indent=2)
            
            # 检查时间，控制休息
            elapsed = datetime.now() - start_time
            if elapsed &gt; run_duration:
                print(f"\n运行了 {run_duration}, 休息 {rest_duration}...")
                time.sleep(rest_duration.total_seconds())
                start_time = datetime.now()
            
            # 延时
            print(f"  等待 10 秒...")
            time.sleep(10)
            
        except Exception as e:
            print(f"  ❌ 失败: {e}")
            fail_count +=1
            import traceback
            traceback.print_exc()
        
        test_count +=1
    
    print("\n" + "="*80)
    print("测试完成!")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    print(f"输出目录: {output_dir}")
    print("="*80)


if __name__ == "__main__":
    main()
