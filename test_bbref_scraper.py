#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 basketball_reference_web_scraper 库
"""
from basketball_reference_web_scraper import client
from basketball_reference_web_scraper.data import Team
from datetime import datetime

print('✓ 库导入成功！')
print('库版本: 4.15.4')
print()

# 测试获取 2024-25 赛季的比赛数据
print('尝试获取 2024-25 赛季的数据...')
try:
    games = client.season_schedule(season_end_year=2025)
    print(f'✓ 成功获取 {len(games)} 场比赛！')
    
    # 显示前5场比赛
    print()
    print('前5场比赛:')
    for i, game in enumerate(games[:5]):
        print(f'{i+1}. {game["home_team"].value} vs {game["away_team"].value}')
        print(f'   日期: {game["date"].date()}')
        print(f'   比分: {game["home_score"]} - {game["away_score"]}')
        print()
    
except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()
