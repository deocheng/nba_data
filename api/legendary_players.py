import csv
import os
import json
from datetime import datetime
from typing import List, Dict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_DIR = os.path.join(BASE_DIR, "CSV")

LEGENDARY_PLAYERS = {
    "michael_jordan": {
        "name": "迈克尔·乔丹",
        "english_name": "Michael Jordan",
        "position": "SG",
        "position_cn": "得分后卫",
        "height": "198",
        "weight": "98",
        "jersey_number": "23",
        "birth_date": "1963-02-17",
        "birth_place": "美国纽约布鲁克林",
        "draft_year": "1984",
        "draft_pick": "第一轮第3顺位",
        "retire_year": "2003",
        "teams": ["CHI", "WAS"],
        "honors": {
            "championships": 6,
            "mvp": 5,
            "fmvp": 6,
            "scoring_champ": 10,
            "all_star": 14,
            "defensive_player": 1,
            "rookie_of_year": 1
        },
        "career_stats": {
            "games_played": 1072,
            "minutes_played": 39088,
            "field_goals_made": 12192,
            "field_goals_attempted": 24537,
            "three_pointers_made": 581,
            "three_pointers_attempted": 1778,
            "free_throws_made": 7327,
            "free_throws_attempted": 8772,
            "rebounds": 6672,
            "assists": 5633,
            "steals": 2514,
            "blocks": 893,
            "points": 32292,
            "avg_points": 30.1,
            "avg_rebounds": 6.2,
            "avg_assists": 5.3,
            "avg_steals": 2.35,
            "avg_blocks": 0.83,
            "fg_percentage": 0.497,
            "three_p_percentage": 0.327,
            "ft_percentage": 0.835,
            "fg_pct": 0.497,
            "three_pct": 0.327,
            "ft_pct": 0.835,
            "per": 27.9,
            "ws": 207.8,
            "bpm": 8.0,
            "vorp": 122.5
        },
        "seasons": [
            {"season": "1984-85", "team": "CHI", "games": 82, "points": 2153, "rebounds": 482, "assists": 481, "avg_points": 26.3, "avg_rebounds": 5.9, "avg_assists": 5.9},
            {"season": "1985-86", "team": "CHI", "games": 18, "points": 408, "rebounds": 98, "assists": 109, "avg_points": 22.7, "avg_rebounds": 5.4, "avg_assists": 6.1},
            {"season": "1986-87", "team": "CHI", "games": 82, "points": 3041, "rebounds": 526, "assists": 463, "avg_points": 37.1, "avg_rebounds": 6.4, "avg_assists": 5.6},
            {"season": "1987-88", "team": "CHI", "games": 82, "points": 2868, "rebounds": 588, "assists": 491, "avg_points": 35.0, "avg_rebounds": 7.2, "avg_assists": 6.0},
            {"season": "1988-89", "team": "CHI", "games": 81, "points": 2633, "rebounds": 652, "assists": 614, "avg_points": 32.5, "avg_rebounds": 8.0, "avg_assists": 7.6},
            {"season": "1989-90", "team": "CHI", "games": 82, "points": 2753, "rebounds": 690, "assists": 593, "avg_points": 33.6, "avg_rebounds": 8.4, "avg_assists": 7.2},
            {"season": "1990-91", "team": "CHI", "games": 82, "points": 2580, "rebounds": 605, "assists": 549, "avg_points": 31.5, "avg_rebounds": 7.4, "avg_assists": 6.7},
            {"season": "1991-92", "team": "CHI", "games": 80, "points": 2404, "rebounds": 583, "assists": 519, "avg_points": 30.1, "avg_rebounds": 7.3, "avg_assists": 6.5},
            {"season": "1992-93", "team": "CHI", "games": 78, "points": 2541, "rebounds": 548, "assists": 465, "avg_points": 32.6, "avg_rebounds": 7.0, "avg_assists": 6.0},
            {"season": "1995-96", "team": "CHI", "games": 82, "points": 2491, "rebounds": 503, "assists": 432, "avg_points": 30.4, "avg_rebounds": 6.1, "avg_assists": 5.3},
            {"season": "1996-97", "team": "CHI", "games": 82, "points": 2431, "rebounds": 442, "assists": 423, "avg_points": 29.6, "avg_rebounds": 5.4, "avg_assists": 5.2},
            {"season": "1997-98", "team": "CHI", "games": 82, "points": 2357, "rebounds": 453, "assists": 352, "avg_points": 28.7, "avg_rebounds": 5.5, "avg_assists": 4.3},
            {"season": "2001-02", "team": "WAS", "games": 60, "points": 1152, "rebounds": 339, "assists": 263, "avg_points": 19.2, "avg_rebounds": 5.7, "avg_assists": 4.4},
            {"season": "2002-03", "team": "WAS", "games": 82, "points": 1640, "rebounds": 422, "assists": 299, "avg_points": 20.0, "avg_rebounds": 5.1, "avg_assists": 3.6}
        ]
    },
    "kobe_bryant": {
        "name": "科比·布莱恩特",
        "english_name": "Kobe Bryant",
        "position": "SG",
        "position_cn": "得分后卫",
        "height": "198",
        "weight": "96",
        "jersey_number": "24",
        "birth_date": "1978-08-23",
        "birth_place": "美国宾夕法尼亚州费城",
        "draft_year": "1996",
        "draft_pick": "第一轮第13顺位",
        "retire_year": "2016",
        "teams": ["LAL"],
        "honors": {
            "championships": 5,
            "mvp": 1,
            "fmvp": 2,
            "scoring_champ": 2,
            "all_star": 18,
            "defensive_player": 0,
            "rookie_of_year": 0
        },
        "career_stats": {
            "games_played": 1346,
            "minutes_played": 48637,
            "field_goals_made": 11719,
            "field_goals_attempted": 26200,
            "three_pointers_made": 1827,
            "three_pointers_attempted": 5546,
            "free_throws_made": 8378,
            "free_throws_attempted": 10011,
            "rebounds": 7047,
            "assists": 6306,
            "steals": 1944,
            "blocks": 640,
            "points": 33643,
            "avg_points": 25.0,
            "avg_rebounds": 5.2,
            "avg_assists": 4.7,
            "avg_steals": 1.44,
            "avg_blocks": 0.47,
            "fg_percentage": 0.447,
            "three_p_percentage": 0.329,
            "ft_percentage": 0.837,
            "fg_pct": 0.447,
            "three_pct": 0.329,
            "ft_pct": 0.837,
            "per": 22.9,
            "ws": 172.0,
            "bpm": 4.2,
            "vorp": 87.9
        },
        "seasons": [
            {"season": "1996-97", "team": "LAL", "games": 71, "points": 539, "rebounds": 143, "assists": 199, "avg_points": 7.6, "avg_rebounds": 2.0, "avg_assists": 2.8},
            {"season": "1997-98", "team": "LAL", "games": 79, "points": 1086, "rebounds": 233, "assists": 261, "avg_points": 13.6, "avg_rebounds": 2.9, "avg_assists": 3.3},
            {"season": "1998-99", "team": "LAL", "games": 50, "points": 1178, "rebounds": 205, "assists": 199, "avg_points": 23.6, "avg_rebounds": 4.1, "avg_assists": 4.0},
            {"season": "1999-00", "team": "LAL", "games": 66, "points": 1616, "rebounds": 336, "assists": 330, "avg_points": 24.5, "avg_rebounds": 5.1, "avg_assists": 5.0},
            {"season": "2005-06", "team": "LAL", "games": 80, "points": 2832, "rebounds": 474, "assists": 463, "avg_points": 35.4, "avg_rebounds": 5.9, "avg_assists": 5.8},
            {"season": "2006-07", "team": "LAL", "games": 77, "points": 2430, "rebounds": 468, "assists": 413, "avg_points": 31.6, "avg_rebounds": 6.1, "avg_assists": 5.4},
            {"season": "2008-09", "team": "LAL", "games": 82, "points": 2225, "rebounds": 492, "assists": 481, "avg_points": 27.1, "avg_rebounds": 6.0, "avg_assists": 5.9},
            {"season": "2009-10", "team": "LAL", "games": 73, "points": 1970, "rebounds": 412, "assists": 364, "avg_points": 27.0, "avg_rebounds": 5.6, "avg_assists": 5.0},
            {"season": "2015-16", "team": "LAL", "games": 66, "points": 1161, "rebounds": 261, "assists": 191, "avg_points": 17.6, "avg_rebounds": 4.0, "avg_assists": 2.9}
        ]
    },
    "tim_duncan": {
        "name": "蒂姆·邓肯",
        "english_name": "Tim Duncan",
        "position": "PF/C",
        "position_cn": "大前锋/中锋",
        "height": "211",
        "weight": "113",
        "jersey_number": "21",
        "birth_date": "1976-04-25",
        "birth_place": "美属维尔京群岛圣克罗伊岛",
        "draft_year": "1997",
        "draft_pick": "第一轮第1顺位",
        "retire_year": "2016",
        "teams": ["SAS"],
        "honors": {
            "championships": 5,
            "mvp": 2,
            "fmvp": 3,
            "scoring_champ": 0,
            "all_star": 15,
            "defensive_player": 0,
            "rookie_of_year": 1
        },
        "career_stats": {
            "games_played": 1392,
            "minutes_played": 47368,
            "field_goals_made": 10285,
            "field_goals_attempted": 19358,
            "three_pointers_made": 30,
            "three_pointers_attempted": 149,
            "free_throws_made": 6468,
            "free_throws_attempted": 8468,
            "rebounds": 15091,
            "assists": 4225,
            "steals": 1025,
            "blocks": 3020,
            "points": 26496,
            "avg_points": 18.9,
            "avg_rebounds": 10.8,
            "avg_assists": 3.0,
            "avg_steals": 0.74,
            "avg_blocks": 2.17,
            "fg_percentage": 0.531,
            "three_p_percentage": 0.201,
            "ft_percentage": 0.764,
            "fg_pct": 0.531,
            "three_pct": 0.201,
            "ft_pct": 0.764,
            "per": 20.8,
            "ws": 206.4,
            "bpm": 6.3,
            "vorp": 96.9
        },
        "seasons": [
            {"season": "1997-98", "team": "SAS", "games": 82, "points": 1969, "rebounds": 1189, "assists": 277, "avg_points": 24.0, "avg_rebounds": 14.5, "avg_assists": 3.4},
            {"season": "1998-99", "team": "SAS", "games": 50, "points": 1020, "rebounds": 663, "assists": 135, "avg_points": 20.4, "avg_rebounds": 13.3, "avg_assists": 2.7},
            {"season": "2002-03", "team": "SAS", "games": 81, "points": 1840, "rebounds": 1139, "assists": 322, "avg_points": 22.7, "avg_rebounds": 14.1, "avg_assists": 4.0},
            {"season": "2006-07", "team": "SAS", "games": 80, "points": 1431, "rebounds": 929, "assists": 284, "avg_points": 17.9, "avg_rebounds": 11.6, "avg_assists": 3.6},
            {"season": "2013-14", "team": "SAS", "games": 74, "points": 858, "rebounds": 666, "assists": 219, "avg_points": 11.6, "avg_rebounds": 9.0, "avg_assists": 3.0}
        ]
    },
    "lebron_james": {
        "name": "勒布朗·詹姆斯",
        "english_name": "LeBron James",
        "position": "SF",
        "position_cn": "小前锋",
        "height": "206",
        "weight": "113",
        "jersey_number": "23",
        "birth_date": "1984-12-30",
        "birth_place": "美国俄亥俄州阿克伦",
        "draft_year": "2003",
        "draft_pick": "第一轮第1顺位",
        "retire_year": "",
        "teams": ["CLE", "MIA", "LAL"],
        "honors": {
            "championships": 4,
            "mvp": 4,
            "fmvp": 4,
            "scoring_champ": 1,
            "all_star": 21,
            "defensive_player": 0,
            "rookie_of_year": 1
        },
        "career_stats": {
            "games_played": 1410,
            "minutes_played": 52086,
            "field_goals_made": 14664,
            "field_goals_attempted": 27819,
            "three_pointers_made": 2438,
            "three_pointers_attempted": 7102,
            "free_throws_made": 8700,
            "free_throws_attempted": 11612,
            "rebounds": 11608,
            "assists": 11684,
            "steals": 2316,
            "blocks": 1176,
            "points": 40479,
            "avg_points": 28.7,
            "avg_rebounds": 8.2,
            "avg_assists": 8.3,
            "avg_steals": 1.64,
            "avg_blocks": 0.83,
            "fg_percentage": 0.527,
            "three_p_percentage": 0.343,
            "ft_percentage": 0.749,
            "fg_pct": 0.527,
            "three_pct": 0.343,
            "ft_pct": 0.749,
            "per": 27.1,
            "ws": 214.7,
            "bpm": 7.9,
            "vorp": 123.4
        },
        "seasons": [
            {"season": "2003-04", "team": "CLE", "games": 79, "points": 1654, "rebounds": 432, "assists": 465, "avg_points": 20.9, "avg_rebounds": 5.5, "avg_assists": 5.9},
            {"season": "2005-06", "team": "CLE", "games": 79, "points": 2478, "rebounds": 613, "assists": 586, "avg_points": 31.4, "avg_rebounds": 7.9, "avg_assists": 7.4},
            {"season": "2011-12", "team": "MIA", "games": 62, "points": 1683, "rebounds": 556, "assists": 502, "avg_points": 27.1, "avg_rebounds": 9.0, "avg_assists": 8.1},
            {"season": "2015-16", "team": "CLE", "games": 76, "points": 2063, "rebounds": 671, "assists": 684, "avg_points": 27.1, "avg_rebounds": 8.8, "avg_assists": 9.0},
            {"season": "2020-21", "team": "LAL", "games": 45, "points": 1126, "rebounds": 388, "assists": 340, "avg_points": 25.0, "avg_rebounds": 8.6, "avg_assists": 7.6}
        ]
    },
    "victor_wembanyama": {
        "name": "维克托·文班亚马",
        "english_name": "Victor Wembanyama",
        "position": "C",
        "position_cn": "中锋",
        "height": "224",
        "weight": "107",
        "jersey_number": "1",
        "birth_date": "2004-01-04",
        "birth_place": "法国勒谢奈",
        "draft_year": "2023",
        "draft_pick": "第一轮第1顺位",
        "retire_year": "",
        "teams": ["SAS"],
        "honors": {
            "championships": 0,
            "mvp": 0,
            "fmvp": 0,
            "scoring_champ": 0,
            "all_star": 2,
            "defensive_player": 1,
            "rookie_of_year": 1
        },
        "career_stats": {
            "games_played": 144,
            "minutes_played": 4980,
            "field_goals_made": 864,
            "field_goals_attempted": 1770,
            "three_pointers_made": 175,
            "three_pointers_attempted": 486,
            "free_throws_made": 433,
            "free_throws_attempted": 533,
            "rebounds": 832,
            "assists": 190,
            "steals": 82,
            "blocks": 289,
            "points": 2336,
            "avg_points": 16.2,
            "avg_rebounds": 5.8,
            "avg_assists": 1.3,
            "avg_steals": 0.57,
            "avg_blocks": 2.01,
            "fg_percentage": 0.488,
            "three_p_percentage": 0.360,
            "ft_percentage": 0.812,
            "fg_pct": 0.488,
            "three_pct": 0.360,
            "ft_pct": 0.812,
            "per": 21.5,
            "ws": 9.8,
            "bpm": 3.2,
            "vorp": 3.1
        },
        "seasons": [
            {"season": "2023-24", "team": "SAS", "games": 71, "points": 1196, "rebounds": 403, "assists": 90, "avg_points": 16.8, "avg_rebounds": 5.7, "avg_assists": 1.3},
            {"season": "2024-25", "team": "SAS", "games": 73, "points": 1140, "rebounds": 429, "assists": 100, "avg_points": 15.6, "avg_rebounds": 5.9, "avg_assists": 1.4}
        ]
    }
}

LEGENDARY_STATS = {
    "michael_jordan": {
        "per": 27.9,
        "ws": 207.8,
        "bpm": 8.0,
        "vorp": 122.5,
        "pts": 30.1,
        "reb": 6.2,
        "ast": 5.3
    },
    "kobe_bryant": {
        "per": 22.9,
        "ws": 172.0,
        "bpm": 4.2,
        "vorp": 87.9,
        "pts": 25.0,
        "reb": 5.2,
        "ast": 4.7
    },
    "tim_duncan": {
        "per": 20.8,
        "ws": 206.4,
        "bpm": 6.3,
        "vorp": 96.9,
        "pts": 18.9,
        "reb": 10.8,
        "ast": 3.0
    },
    "lebron_james": {
        "per": 27.1,
        "ws": 214.7,
        "bpm": 7.9,
        "vorp": 123.4,
        "pts": 28.7,
        "reb": 8.2,
        "ast": 8.3
    },
    "victor_wembanyama": {
        "per": 21.5,
        "ws": 9.8,
        "bpm": 3.2,
        "vorp": 3.1,
        "pts": 16.2,
        "reb": 5.8,
        "ast": 1.3
    }
}

TEAM_MAP = {
    "CHI": {"name": "芝加哥公牛", "abbr": "CHI"},
    "WAS": {"name": "华盛顿奇才", "abbr": "WAS"},
    "LAL": {"name": "洛杉矶湖人", "abbr": "LAL"},
    "SAS": {"name": "圣安东尼奥马刺", "abbr": "SAS"},
    "CLE": {"name": "克里夫兰骑士", "abbr": "CLE"},
    "MIA": {"name": "迈阿密热火", "abbr": "MIA"}
}

def get_player_list():
    players = []
    for key, data in LEGENDARY_PLAYERS.items():
        players.append({
            "id": key,
            "name": data["name"],
            "english_name": data["english_name"],
            "position": data["position_cn"],
            "teams": [TEAM_MAP.get(t, {"name": t, "abbr": t})["name"] for t in data["teams"]]
        })
    return players

def get_player_info(player_id):
    if player_id not in LEGENDARY_PLAYERS:
        return None
    
    player = LEGENDARY_PLAYERS[player_id]
    return {
        "id": player_id,
        "name": player["name"],
        "english_name": player["english_name"],
        "position": player["position"],
        "position_cn": player["position_cn"],
        "height": player["height"],
        "weight": player["weight"],
        "jersey_number": player["jersey_number"],
        "birth_date": player["birth_date"],
        "birth_place": player["birth_place"],
        "draft_year": player["draft_year"],
        "draft_pick": player["draft_pick"],
        "retire_year": player["retire_year"],
        "teams": [TEAM_MAP.get(t, {"name": t, "abbr": t}) for t in player["teams"]],
        "honors": player["honors"]
    }

def calculate_career_stats(player_id):
    player = LEGENDARY_PLAYERS.get(player_id)
    if not player:
        return None
    
    return player.get("career_stats", {
        "games_played": 0,
        "minutes_played": 0,
        "field_goals_made": 0,
        "field_goals_attempted": 0,
        "three_pointers_made": 0,
        "three_pointers_attempted": 0,
        "free_throws_made": 0,
        "free_throws_attempted": 0,
        "rebounds": 0,
        "assists": 0,
        "steals": 0,
        "blocks": 0,
        "points": 0,
        "avg_points": 0,
        "avg_rebounds": 0,
        "avg_assists": 0,
        "avg_steals": 0,
        "avg_blocks": 0,
        "fg_percentage": 0,
        "three_p_percentage": 0,
        "ft_percentage": 0,
        "fg_pct": 0.0,
        "three_pct": 0.0,
        "ft_pct": 0.0
    })

def get_season_data(player_id):
    player = LEGENDARY_PLAYERS.get(player_id)
    if not player:
        return []
    
    return player.get("seasons", [])

def get_timeline(player_id):
    player = LEGENDARY_PLAYERS.get(player_id)
    if not player:
        return []
    
    timeline = []
    
    if player_id == "michael_jordan":
        timeline = [
            {"start_year": 1984, "end_year": 1993, "team": "CHI", "team_name": "芝加哥公牛", "description": "第一个公牛时期"},
            {"start_year": 1995, "end_year": 1998, "team": "CHI", "team_name": "芝加哥公牛", "description": "第二个公牛时期"},
            {"start_year": 2001, "end_year": 2003, "team": "WAS", "team_name": "华盛顿奇才", "description": "奇才时期"}
        ]
    elif player_id == "kobe_bryant":
        timeline = [
            {"start_year": 1996, "end_year": 2016, "team": "LAL", "team_name": "洛杉矶湖人", "description": "整个职业生涯"}
        ]
    elif player_id == "tim_duncan":
        timeline = [
            {"start_year": 1997, "end_year": 2016, "team": "SAS", "team_name": "圣安东尼奥马刺", "description": "整个职业生涯"}
        ]
    elif player_id == "lebron_james":
        timeline = [
            {"start_year": 2003, "end_year": 2010, "team": "CLE", "team_name": "克里夫兰骑士", "description": "第一个骑士时期"},
            {"start_year": 2010, "end_year": 2014, "team": "MIA", "team_name": "迈阿密热火", "description": "热火时期"},
            {"start_year": 2014, "end_year": 2018, "team": "CLE", "team_name": "克里夫兰骑士", "description": "第二个骑士时期"},
            {"start_year": 2018, "end_year": 2026, "team": "LAL", "team_name": "洛杉矶湖人", "description": "湖人时期"}
        ]
    elif player_id == "victor_wembanyama":
        timeline = [
            {"start_year": 2023, "end_year": 2026, "team": "SAS", "team_name": "圣安东尼奥马刺", "description": "现役"}
        ]
    
    return timeline
