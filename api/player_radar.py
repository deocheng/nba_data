from fastapi import APIRouter, HTTPException, Query
import psycopg2
import os

router = APIRouter(prefix="/api", tags=["球员雷达图"])

DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'nba'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5433')
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def get_radar_data_from_db(player_id):
    """从数据库获取球员雷达图数据"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT SUM(games_played), SUM(minutes_played), SUM(points), 
                   SUM(rebounds), SUM(assists), SUM(steals), SUM(blocks),
                   SUM(fg_made), SUM(fg_att), SUM(three_made), SUM(three_att),
                   SUM(ft_made), SUM(ft_att), AVG(per), AVG(ts_pct)
            FROM player_team_seasons 
            WHERE player_id = %s
        """
        cursor.execute(query, (player_id,))
        row = cursor.fetchone()
        
        if not row or row[0] is None:
            return None
        
        games_played, minutes_played, points, rebounds, assists, steals, blocks, \
        fg_made, fg_att, three_made, three_att, ft_made, ft_att, per, ts_pct = row
        
        return {
            "avg_points": points / games_played if games_played > 0 else 0,
            "avg_rebounds": rebounds / games_played if games_played > 0 else 0,
            "avg_assists": assists / games_played if games_played > 0 else 0,
            "avg_steals": steals / games_played if games_played > 0 else 0,
            "avg_blocks": blocks / games_played if games_played > 0 else 0,
            "fg_pct": fg_made / fg_att if fg_att > 0 else 0,
            "three_pct": three_made / three_att if three_att > 0 else 0,
            "ft_pct": ft_made / ft_att if ft_att > 0 else 0,
            "per": per or 0,
            "ts_pct": ts_pct or 0
        }
    except Exception as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()

LEGENDARY_PLAYERS_DATA = {
    "michael_jordan": {
        "avg_points": 30.1, "avg_rebounds": 6.2, "avg_assists": 5.3,
        "avg_steals": 2.35, "avg_blocks": 0.83, "fg_pct": 0.497,
        "three_pct": 0.327, "ft_pct": 0.835, "per": 27.9, "ts_pct": 0.569
    },
    "kobe_bryant": {
        "avg_points": 25.0, "avg_rebounds": 5.2, "avg_assists": 4.7,
        "avg_steals": 1.44, "avg_blocks": 0.47, "fg_pct": 0.447,
        "three_pct": 0.329, "ft_pct": 0.837, "per": 22.9, "ts_pct": 0.550
    },
    "tim_duncan": {
        "avg_points": 18.9, "avg_rebounds": 10.8, "avg_assists": 3.0,
        "avg_steals": 0.74, "avg_blocks": 2.17, "fg_pct": 0.531,
        "three_pct": 0.201, "ft_pct": 0.764, "per": 21.9, "ts_pct": 0.573
    },
    "lebron_james": {
        "avg_points": 28.7, "avg_rebounds": 8.2, "avg_assists": 8.3,
        "avg_steals": 1.64, "avg_blocks": 0.83, "fg_pct": 0.527,
        "three_pct": 0.343, "ft_pct": 0.749, "per": 27.1, "ts_pct": 0.583
    },
    "victor_wembanyama": {
        "avg_points": 16.2, "avg_rebounds": 5.8, "avg_assists": 1.3,
        "avg_steals": 0.57, "avg_blocks": 2.01, "fg_pct": 0.488,
        "three_pct": 0.360, "ft_pct": 0.812, "per": 21.5, "ts_pct": 0.598
    }
}

@router.get("/player/{player_id}/radar")
def get_player_radar_data(player_id: str):
    """获取球员雷达图数据"""
    
    if player_id in LEGENDARY_PLAYERS_DATA:
        raw_data = LEGENDARY_PLAYERS_DATA[player_id]
    else:
        raw_data = get_radar_data_from_db(player_id)
        if not raw_data:
            raise HTTPException(status_code=404, detail="球员数据未找到")
    
    radar_data = {
        "labels": ["得分能力", "篮板能力", "助攻能力", "防守能力", "投篮效率", "三分能力", "罚球能力", "综合效率"],
        "datasets": [{
            "label": "球员能力",
            "data": [
                min(raw_data["avg_points"] / 40, 1),
                min(raw_data["avg_rebounds"] / 15, 1),
                min(raw_data["avg_assists"] / 12, 1),
                min((raw_data["avg_steals"] + raw_data["avg_blocks"]) / 4, 1),
                raw_data["fg_pct"],
                raw_data["three_pct"],
                raw_data["ft_pct"],
                min(raw_data["per"] / 40, 1)
            ],
            "maxValues": [40, 15, 12, 4, 1, 1, 1, 40],
            "actualValues": [
                round(raw_data["avg_points"], 1),
                round(raw_data["avg_rebounds"], 1),
                round(raw_data["avg_assists"], 1),
                round(raw_data["avg_steals"] + raw_data["avg_blocks"], 2),
                round(raw_data["fg_pct"] * 100, 1),
                round(raw_data["three_pct"] * 100, 1),
                round(raw_data["ft_pct"] * 100, 1),
                round(raw_data["per"], 1)
            ]
        }]
    }
    
    return {"success": True, "data": radar_data}

@router.get("/players/compare/radar")
def compare_players_radar(
    player1_id: str = Query(..., description="球员1ID"),
    player2_id: str = Query(..., description="球员2ID")
):
    """对比两名球员的雷达图数据"""
    
    def get_data(p_id):
        if p_id in LEGENDARY_PLAYERS_DATA:
            return LEGENDARY_PLAYERS_DATA[p_id]
        else:
            data = get_radar_data_from_db(p_id)
            return data if data else None
    
    data1 = get_data(player1_id)
    data2 = get_data(player2_id)
    
    if not data1:
        raise HTTPException(status_code=404, detail=f"球员 {player1_id} 数据未找到")
    if not data2:
        raise HTTPException(status_code=404, detail=f"球员 {player2_id} 数据未找到")
    
    labels = ["得分能力", "篮板能力", "助攻能力", "防守能力", "投篮效率", "三分能力", "罚球能力", "综合效率"]
    
    return {
        "success": True,
        "data": {
            "labels": labels,
            "players": [
                {
                    "id": player1_id,
                    "data": [
                        min(data1["avg_points"] / 40, 1),
                        min(data1["avg_rebounds"] / 15, 1),
                        min(data1["avg_assists"] / 12, 1),
                        min((data1["avg_steals"] + data1["avg_blocks"]) / 4, 1),
                        data1["fg_pct"],
                        data1["three_pct"],
                        data1["ft_pct"],
                        min(data1["per"] / 40, 1)
                    ],
                    "actualValues": [
                        round(data1["avg_points"], 1),
                        round(data1["avg_rebounds"], 1),
                        round(data1["avg_assists"], 1),
                        round(data1["avg_steals"] + data1["avg_blocks"], 2),
                        round(data1["fg_pct"] * 100, 1),
                        round(data1["three_pct"] * 100, 1),
                        round(data1["ft_pct"] * 100, 1),
                        round(data1["per"], 1)
                    ]
                },
                {
                    "id": player2_id,
                    "data": [
                        min(data2["avg_points"] / 40, 1),
                        min(data2["avg_rebounds"] / 15, 1),
                        min(data2["avg_assists"] / 12, 1),
                        min((data2["avg_steals"] + data2["avg_blocks"]) / 4, 1),
                        data2["fg_pct"],
                        data2["three_pct"],
                        data2["ft_pct"],
                        min(data2["per"] / 40, 1)
                    ],
                    "actualValues": [
                        round(data2["avg_points"], 1),
                        round(data2["avg_rebounds"], 1),
                        round(data2["avg_assists"], 1),
                        round(data2["avg_steals"] + data2["avg_blocks"], 2),
                        round(data2["fg_pct"] * 100, 1),
                        round(data2["three_pct"] * 100, 1),
                        round(data2["ft_pct"] * 100, 1),
                        round(data2["per"], 1)
                    ]
                }
            ]
        }
    }