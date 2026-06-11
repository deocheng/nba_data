from fastapi import APIRouter, HTTPException
from api.legendary_players import calculate_career_stats, get_season_data, get_player_info
import json

router = APIRouter(prefix="/api/players", tags=["球员对比"])

@router.get("/list")
def get_player_list():
    players = [
        {"id": "michael_jordan", "name": "迈克尔·乔丹", "name_en": "Michael Jordan"},
        {"id": "kobe_bryant", "name": "科比·布莱恩特", "name_en": "Kobe Bryant"},
        {"id": "tim_duncan", "name": "蒂姆·邓肯", "name_en": "Tim Duncan"},
        {"id": "lebron_james", "name": "勒布朗·詹姆斯", "name_en": "LeBron James"},
        {"id": "victor_wembanyama", "name": "维克托·文班亚马", "name_en": "Victor Wembanyama"}
    ]
    return players

@router.get("/compare")
def compare_players(player1_id: str, player2_id: str, season: str = None):
    try:
        player1_info = get_player_info(player1_id)
        player2_info = get_player_info(player2_id)
        
        if not player1_info or not player2_info:
            raise HTTPException(status_code=404, detail="球员信息未找到")
        
        if season and season != "career":
            player1_stats = get_season_data(player1_id)
            player2_stats = get_season_data(player2_id)
            # 过滤特定赛季
            player1_stats = [s for s in player1_stats if s.get("season") == season]
            player2_stats = [s for s in player2_stats if s.get("season") == season]
            player1_stats = player1_stats[0] if player1_stats else {}
            player2_stats = player2_stats[0] if player2_stats else {}
            comparison_type = "赛季对比"
        else:
            player1_stats = calculate_career_stats(player1_id)
            player2_stats = calculate_career_stats(player2_id)
            comparison_type = "生涯对比"
        
        comparison = {
            "type": comparison_type,
            "season": season if season else "生涯",
            "player1": {
                "info": player1_info,
                "stats": player1_stats
            },
            "player2": {
                "info": player2_info,
                "stats": player2_stats
            },
            "differences": calculate_differences(player1_stats, player2_stats)
        }
        
        return comparison
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def calculate_differences(stats1, stats2):
    diffs = {}
    
    numeric_fields = ['points', 'rebounds', 'assists', 'steals', 'blocks', 'fg_pct', 'ft_pct', 'games_played', 'avg_points', 'avg_rebounds', 'avg_assists', 'avg_steals', 'avg_blocks', 'per', 'ws', 'bpm', 'vorp']
    
    for field in numeric_fields:
        val1 = float(stats1.get(field, 0) or 0)
        val2 = float(stats2.get(field, 0) or 0)
        diffs[field] = round(val1 - val2, 2)
    
    return diffs

@router.get("/{player_id}/seasons")
def get_player_season_list(player_id: str):
    seasons = []
    
    if player_id == "michael_jordan":
        seasons = ["1984-85", "1985-86", "1986-87", "1987-88", "1988-89", "1989-90", "1990-91", "1991-92", "1992-93", "1995-96", "1996-97", "1997-98", "2001-02", "2002-03"]
    elif player_id == "kobe_bryant":
        seasons = ["1996-97", "1997-98", "1998-99", "1999-00", "2000-01", "2001-02", "2002-03", "2003-04", "2004-05", "2005-06", "2006-07", "2007-08", "2008-09", "2009-10", "2010-11", "2011-12", "2012-13", "2013-14", "2014-15", "2015-16"]
    elif player_id == "tim_duncan":
        seasons = ["1997-98", "1998-99", "1999-00", "2000-01", "2001-02", "2002-03", "2003-04", "2004-05", "2005-06", "2006-07", "2007-08", "2008-09", "2009-10", "2010-11", "2011-12", "2012-13", "2013-14", "2014-15", "2015-16", "2016-17"]
    elif player_id == "lebron_james":
        seasons = ["2003-04", "2004-05", "2005-06", "2006-07", "2007-08", "2008-09", "2009-10", "2010-11", "2011-12", "2012-13", "2013-14", "2014-15", "2015-16", "2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "2021-22", "2022-23", "2023-24"]
    elif player_id == "victor_wembanyama":
        seasons = ["2023-24", "2024-25"]
    
    return {"seasons": seasons, "career": True}