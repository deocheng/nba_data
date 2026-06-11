#!/usr/bin/env python3
"""
ETL模块 - 数据抽取
功能：从CSV、JSON文件中抽取NBA数据
"""

import os
import json
import csv
import pandas as pd

def extract_from_json(file_path):
    """从JSON文件抽取数据"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_from_csv(file_path, delimiter=','):
    """从CSV文件抽取数据"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    data = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            data.append(dict(row))
    return data

def extract_player_stats_2025_26():
    """抽取2025-26赛季球员统计数据"""
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "player_stats_2025-26.json")
    return extract_from_json(file_path)

def extract_team_stats_2025_26():
    """抽取2025-26赛季球队统计数据"""
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "team_stats_2025-26.json")
    return extract_from_json(file_path)

def extract_teams_detailed():
    """抽取球队详细信息"""
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tencent_teams_detailed.json")
    return extract_from_json(file_path)

def extract_advanced_stats():
    """抽取高阶数据"""
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "advanced_stats_2025-26.json")
    return extract_from_json(file_path)

def extract_legendary_player_career(player_id):
    """抽取传奇球员生涯数据"""
    csv_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "CSV")
    
    player_map = {
        "michael_jordan": "MJ career.csv",
        "kobe_bryant": "KobeBryant Career.csv",
        "tim_duncan": "TimDuncan career.csv",
        "lebron_james": "LBJ career.csv",
        "victor_wembanyama": "Wemby Career.csv"
    }
    
    file_name = player_map.get(player_id)
    if not file_name:
        raise ValueError(f"未知球员ID: {player_id}")
    
    file_path = os.path.join(csv_dir, file_name)
    return extract_from_csv(file_path)

def extract_spurs_season_data(season):
    """抽取马刺队赛季数据"""
    csv_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "CSV")
    file_name = f"{season.replace('-', '_')}spurs.csv"
    file_path = os.path.join(csv_dir, file_name)
    
    if not os.path.exists(file_path):
        # 尝试其他格式
        alt_file_name = f"{season}spurs.csv"
        alt_file_path = os.path.join(csv_dir, alt_file_name)
        if os.path.exists(alt_file_path):
            file_path = alt_file_path
        else:
            raise FileNotFoundError(f"马刺队赛季数据文件不存在: {file_path}")
    
    return extract_from_csv(file_path)

def extract_tencent_regular_season(season):
    """抽取腾讯常规赛数据"""
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), f"tencent_regular_season_{season}.json")
    return extract_from_json(file_path)

if __name__ == "__main__":
    # 测试抽取功能
    print("测试数据抽取...")
    
    # 测试抽取球队数据
    teams = extract_teams_detailed()
    print(f"抽取球队数量: {len(teams)}")
    
    # 测试抽取球员数据
    players = extract_player_stats_2025_26()
    print(f"抽取球员数量: {len(players)}")
    
    # 测试抽取高阶数据
    advanced = extract_advanced_stats()
    print(f"抽取高阶数据数量: {len(advanced)}")
    
    print("数据抽取测试完成!")
