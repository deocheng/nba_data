#!/usr/bin/env python3
"""
ETL模块 - 数据转换
功能：清洗和转换抽取的数据，适配目标表结构
"""

import re
from datetime import datetime

def transform_teams(teams_data):
    """转换球队数据"""
    transformed = []
    
    for team in teams_data:
        transformed.append({
            "team_id": str(team.get("team_id", team.get("id", ""))),
            "team_name": team.get("team_name", team.get("name", "")),
            "team_name_en": team.get("team_name_en", team.get("name_en", "")),
            "team_abbr": team.get("team_abbr", team.get("abbr", "")),
            "conference": team.get("conference", team.get("conf", "")),
            "conference_cn": team.get("conference_cn", ""),
            "division": team.get("division", ""),
            "division_cn": team.get("division_cn", ""),
            "city": team.get("city", ""),
            "arena": team.get("arena", ""),
            "founded_year": team.get("founded_year", team.get("founded", ""))
        })
    
    return transformed

def transform_players(players_data):
    """转换球员数据"""
    transformed = []
    
    for player in players_data:
        transformed.append({
            "player_id": str(player.get("player_id", player.get("id", ""))),
            "player_name": player.get("player_name", player.get("name", "")),
            "player_name_en": player.get("player_name_en", player.get("name_en", "")),
            "position": player.get("position", player.get("pos", "")),
            "position_cn": player.get("position_cn", ""),
            "height": player.get("height", ""),
            "weight": player.get("weight", ""),
            "jersey_number": player.get("number", player.get("jersey", "")),
            "birth_date": parse_date(player.get("birth_date", "")),
            "birth_place": player.get("birth_place", ""),
            "draft_year": player.get("draft_year", ""),
            "draft_pick": player.get("draft_pick", ""),
            "retire_year": player.get("retire_year", "")
        })
    
    return transformed

def transform_player_team_seasons(player_stats, advanced_stats=None):
    """转换球员-球队-赛季数据"""
    transformed = []
    
    for player in player_stats:
        # 获取高阶数据
        adv_data = None
        if advanced_stats:
            adv_data = next((a for a in advanced_stats if a.get("player_id") == str(player.get("player_id"))), None)
        
        # 计算命中率
        fg_att = safe_int(player.get("FGA", player.get("fg_att", 0)))
        fg_made = safe_int(player.get("FGM", player.get("fg_made", 0)))
        ft_att = safe_int(player.get("FTA", player.get("ft_att", 0)))
        ft_made = safe_int(player.get("FTM", player.get("ft_made", 0)))
        three_att = safe_int(player.get("3PA", player.get("three_att", 0)))
        three_made = safe_int(player.get("3PM", player.get("three_made", 0)))
        
        transformed.append({
            "player_id": str(player.get("player_id", player.get("id", ""))),
            "team_id": str(player.get("team_id", "")),
            "season_id": player.get("season", "2025-26"),
            "games_played": safe_int(player.get("GP", player.get("games_played", 0))),
            "minutes_played": safe_float(player.get("MP", player.get("minutes_played", 0))),
            "points": safe_int(player.get("PTS", player.get("points", 0))),
            "rebounds": safe_int(player.get("REB", player.get("rebounds", 0))),
            "assists": safe_int(player.get("AST", player.get("assists", 0))),
            "steals": safe_int(player.get("STL", player.get("steals", 0))),
            "blocks": safe_int(player.get("BLK", player.get("blocks", 0))),
            "fg_made": fg_made,
            "fg_att": fg_att,
            "three_made": three_made,
            "three_att": three_att,
            "ft_made": ft_made,
            "ft_att": ft_att,
            # 高阶指标
            "per": safe_float(adv_data.get("per") if adv_data else player.get("PER", 0)),
            "ts_pct": safe_float(adv_data.get("ts_pct") if adv_data else 0),
            "usg_pct": safe_float(adv_data.get("usg_pct") if adv_data else 0),
            "ws": safe_float(adv_data.get("ws") if adv_data else 0),
            "ws_per_48": safe_float(adv_data.get("ws_per_48") if adv_data else 0),
            "bpm": safe_float(adv_data.get("bpm") if adv_data else 0),
            "vorp": safe_float(adv_data.get("vorp") if adv_data else 0),
            "offensive_rating": safe_float(adv_data.get("offensive_rating") if adv_data else 0),
            "defensive_rating": safe_float(adv_data.get("defensive_rating") if adv_data else 0),
            "assist_ratio": safe_float(adv_data.get("assist_ratio") if adv_data else 0),
            "turnover_ratio": safe_float(adv_data.get("turnover_ratio") if adv_data else 0),
            "rebound_rate": safe_float(adv_data.get("rebound_rate") if adv_data else 0),
            # 场均数据
            "avg_points": safe_float(player.get("PTS", 0)) / safe_int(player.get("GP", 1)),
            "avg_rebounds": safe_float(player.get("REB", 0)) / safe_int(player.get("GP", 1)),
            "avg_assists": safe_float(player.get("AST", 0)) / safe_int(player.get("GP", 1)),
            "avg_steals": safe_float(player.get("STL", 0)) / safe_int(player.get("GP", 1)),
            "avg_blocks": safe_float(player.get("BLK", 0)) / safe_int(player.get("GP", 1)),
            "fg_pct": fg_made / fg_att if fg_att > 0 else 0,
            "three_pct": three_made / three_att if three_att > 0 else 0,
            "ft_pct": ft_made / ft_att if ft_att > 0 else 0
        })
    
    return transformed

def transform_team_games(games_data):
    """转换球队比赛数据"""
    transformed = []
    
    for game in games_data:
        is_home = game.get("home_team") == game.get("team_name") or not game.get("is_away")
        team_score = game.get("home_score") if is_home else game.get("away_score")
        opp_score = game.get("away_score") if is_home else game.get("home_score")
        result = "W" if team_score > opp_score else "L"
        
        transformed.append({
            "game_id": game.get("game_id", ""),
            "team_id": str(game.get("team_id", "")),
            "season_id": game.get("season", "2025-26"),
            "game_date": parse_date(game.get("game_date", "")),
            "game_number": game.get("game_number", ""),
            "is_home": is_home,
            "opp_team_id": str(game.get("opp_team_id", "")),
            "opp_team_abbr": game.get("opp_team_abbr", game.get("opp_team", "")),
            "opp_team_name": game.get("opp_team", ""),
            "result": result,
            "team_score": team_score,
            "opp_score": opp_score,
            "ot_flag": game.get("ot_flag", "")
        })
    
    return transformed

def parse_date(date_str):
    """解析日期字符串"""
    if not date_str:
        return None
    
    date_formats = ['%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y']
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None

def safe_int(value):
    """安全转换为整数"""
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0

def safe_float(value):
    """安全转换为浮点数"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def clean_text(text):
    """清理文本数据"""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', str(text)).strip()

if __name__ == "__main__":
    # 测试转换功能
    from extract import extract_teams_detailed, extract_player_stats_2025_26, extract_advanced_stats
    
    print("测试数据转换...")
    
    teams = extract_teams_detailed()
    transformed_teams = transform_teams(teams)
    print(f"转换球队数量: {len(transformed_teams)}")
    print(f"球队示例: {transformed_teams[0]}")
    
    players = extract_player_stats_2025_26()
    advanced = extract_advanced_stats()
    transformed_seasons = transform_player_team_seasons(players, advanced)
    print(f"转换球员赛季数据数量: {len(transformed_seasons)}")
    print(f"球员赛季示例: {transformed_seasons[0]}")
    
    print("数据转换测试完成!")
