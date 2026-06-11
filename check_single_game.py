#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查并测试单场比赛
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from data_importer.pbp_storage import get_pbp_storage
import pandas as pd

# 检查数据库
storage = get_pbp_storage(season_end=2026)

game_id = '202510220ATL'
print(f"检查游戏: {game_id}")
is_processed = storage.is_game_processed(game_id)
print(f"已处理: {is_processed}")

if is_processed:
    print("\n✅ 这场比赛已经被处理过了！")
else:
    print("\n❌ 这场比赛还没有处理")

storage.close()

print("\n\n=== 现在让我在浏览器中打开这个页面...")
print("请在浏览器中查看页面结构")
print("URL: https://www.basketball-reference.com/boxscores/pbp/202510220ATL.html")
