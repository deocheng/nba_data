#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 br-scraper 库爬取单场比赛
"""

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from basketball_reference_web_scraper import client
from basketball_reference_web_scraper.data import Team, OutputType
from data_importer.pbp_storage import PBPDataStorage


def scrape_with_br_scraper(game_id):
    """使用 br-scraper 爬取"""
    print(f"使用 br-scraper 爬取: {game_id}")
    
    # 从 game_id 解析日期
    # game_id 格式: YYYYMMDD0TEAM
    date_str = game_id[:8]
    year = int(date_str[:4])
    month = int(date_str[4:6])
    day = int(date_str[6:8])
    
    print(f"日期: {year}-{month}-{day}")
    
    try:
        # 获取当日所有比赛
        games = client.season_schedule(season_end_year=year if month >= 10 else year-1)
        
        for game in games:
            game_date = str(game['start_time'].date())
            if game_date == f"{year}-{month:02d}-{day:02d}":
                print(f"找到比赛: {game}")
                
                # 获取 PBP 数据
                try:
                    pbp_data = client.play_by_play(
                        date=game['start_time'].date(),
                        away_team=game['away_team'],
                        home_team=game['home_team']
                    )
                    
                    print(f"获取到 {len(pbp_data)} 条 PBP 记录")
                    print(f"第一条: {pbp_data[0] if pbp_data else '空'}")
                    
                    return True
                except Exception as e:
                    print(f"获取 PBP 失败: {e}")
                    return False
        
        print("未找到匹配的比赛")
        return False
        
    except Exception as e:
        print(f"获取赛程失败: {e}")
        return False


if __name__ == "__main__":
    game_id = "202606030SAS"
    print("=" * 60)
    print(f"使用 br-scraper 爬取")
    print(f"Game ID: {game_id}")
    print("=" * 60)
    
    success = scrape_with_br_scraper(game_id)
    
    if success:
        print("\n✅ 爬取完成!")
    else:
        print("\n❌ 爬取失败!")
