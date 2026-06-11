from fastapi import APIRouter, HTTPException, Query
import psycopg2
import os

from .legendary_players import LEGENDARY_PLAYERS, LEGENDARY_STATS, TEAM_MAP

router = APIRouter(prefix="/api", tags=["排行榜"])

DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'nba'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5433')
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

@router.get("/rankings/all")
def get_all_rankings():
    """获取所有指标的排行榜摘要"""
    metrics = ["per", "ws", "bpm", "vorp"]
    
    result = {}
    for metric in metrics:
        response = get_rankings(metric, limit=5)
        result[metric] = response
    
    return {
        "success": True,
        "data": result
    }

@router.get("/rankings/career")
def get_career_rankings():
    """获取生涯高阶数据排行榜"""
    conn = None
    rankings = []
    
    legendary_career = []
    for player_id, stats in LEGENDARY_STATS.items():
        teams = LEGENDARY_PLAYERS[player_id]["teams"]
        team_name = ", ".join([TEAM_MAP.get(t, {"name": t})["name"] for t in teams])
        legendary_career.append({
            "player_id": player_id,
            "player_name": LEGENDARY_PLAYERS[player_id]["name"],
            "avg_per": stats.get("per", 0),
            "total_ws": stats.get("ws", 0) * 15,
            "avg_bpm": stats.get("bpm", 0),
            "total_vorp": stats.get("vorp", 0) * 15,
            "avg_points": stats.get("pts", 0),
            "avg_rebounds": stats.get("reb", 0),
            "avg_assists": stats.get("ast", 0),
            "team": team_name,
            "is_legendary": True
        })
    
    legendary_career.sort(key=lambda x: x["avg_per"], reverse=True)
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT pts.player_id, p.player_name, 
                   AVG(pts.per) as avg_per, 
                   SUM(pts.ws) as total_ws,
                   AVG(pts.bpm) as avg_bpm,
                   SUM(pts.vorp) as total_vorp,
                   AVG(pts.avg_points) as avg_points,
                   AVG(pts.avg_rebounds) as avg_rebounds,
                   AVG(pts.avg_assists) as avg_assists
            FROM player_team_seasons pts
            LEFT JOIN players p ON pts.player_id = p.player_id
            GROUP BY pts.player_id, p.player_name
            HAVING COUNT(*) >= 2
            ORDER BY avg_per DESC
            LIMIT 20
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        for row in rows:
            player_id, player_name, avg_per, total_ws, avg_bpm, total_vorp, avg_pts, avg_reb, avg_ast = row
            rankings.append({
                "player_id": player_id,
                "player_name": player_name if player_name else "未知球员",
                "avg_per": round(avg_per, 1) if avg_per else 0,
                "total_ws": round(total_ws, 1) if total_ws else 0,
                "avg_bpm": round(avg_bpm, 1) if avg_bpm else 0,
                "total_vorp": round(total_vorp, 1) if total_vorp else 0,
                "avg_points": round(avg_pts, 1) if avg_pts else 0,
                "avg_rebounds": round(avg_reb, 1) if avg_reb else 0,
                "avg_assists": round(avg_ast, 1) if avg_ast else 0
            })
        
        all_rankings = legendary_career + rankings
        all_rankings.sort(key=lambda x: x["avg_per"], reverse=True)
        
        return {"success": True, "data": all_rankings[:20]}
    
    except Exception as e:
        return {"success": True, "data": legendary_career[:10]}
    finally:
        if conn:
            conn.close()

@router.get("/rankings/metrics")
def get_metrics_info():
    """获取所有可用指标信息"""
    metrics = {
        "per": {"name": "PER效率值", "description": "球员效率评分，综合衡量球员每48分钟的贡献", "unit": ""},
        "ws": {"name": "WS胜利贡献值", "description": "球员为球队胜利做出的贡献", "unit": ""},
        "bpm": {"name": "BPM正负值", "description": "球员在场时球队每100回合净胜分", "unit": ""},
        "vorp": {"name": "VORP球员价值", "description": "替代球员价值，衡量球员优于联盟平均水平的程度", "unit": ""},
        "pts": {"name": "场均得分", "description": "球员场均得分", "unit": "分"},
        "reb": {"name": "场均篮板", "description": "球员场均篮板", "unit": "个"},
        "ast": {"name": "场均助攻", "description": "球员场均助攻", "unit": "次"}
    }
    return {"success": True, "data": metrics}

@router.get("/rankings/{metric}")
def get_rankings(metric: str, limit: int = Query(10, ge=1, le=50)):
    """获取高阶数据排行榜"""
    metrics = {
        "per": {"name": "PER效率值", "description": "球员效率评分，综合衡量球员每48分钟的贡献"},
        "ws": {"name": "WS胜利贡献值", "description": "球员为球队胜利做出的贡献"},
        "bpm": {"name": "BPM正负值", "description": "球员在场时球队每100回合净胜分"},
        "vorp": {"name": "VORP球员价值", "description": "替代球员价值，衡量球员优于联盟平均水平的程度"},
        "pts": {"name": "场均得分", "description": "球员场均得分"},
        "reb": {"name": "场均篮板", "description": "球员场均篮板"},
        "ast": {"name": "场均助攻", "description": "球员场均助攻"}
    }
    
    if metric not in metrics:
        raise HTTPException(status_code=400, detail=f"无效的指标类型。可选: {', '.join(metrics.keys())}")
    
    legendary_rankings = []
    for player_id, stats in LEGENDARY_STATS.items():
        if metric in stats:
            teams = LEGENDARY_PLAYERS[player_id]["teams"]
            team_name = ", ".join([TEAM_MAP.get(t, {"name": t})["name"] for t in teams])
            legendary_rankings.append({
                "player_id": player_id,
                "player_name": LEGENDARY_PLAYERS[player_id]["name"],
                "value": stats[metric],
                "season": "生涯平均",
                "team": team_name,
                "is_legendary": True
            })
    
    legendary_rankings.sort(key=lambda x: x["value"], reverse=True)
    
    db_rankings = []
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if metric == "per":
            query = """
                SELECT pts.player_id, p.player_name, pts.per, pts.season_id, pts.team_abbr
                FROM player_team_seasons pts
                LEFT JOIN players p ON pts.player_id = p.player_id
                WHERE pts.per IS NOT NULL
                ORDER BY pts.per DESC
                LIMIT %s
            """
        elif metric == "ws":
            query = """
                SELECT pts.player_id, p.player_name, pts.ws, pts.season_id, pts.team_abbr
                FROM player_team_seasons pts
                LEFT JOIN players p ON pts.player_id = p.player_id
                WHERE pts.ws IS NOT NULL
                ORDER BY pts.ws DESC
                LIMIT %s
            """
        elif metric == "bpm":
            query = """
                SELECT pts.player_id, p.player_name, pts.bpm, pts.season_id, pts.team_abbr
                FROM player_team_seasons pts
                LEFT JOIN players p ON pts.player_id = p.player_id
                WHERE pts.bpm IS NOT NULL
                ORDER BY pts.bpm DESC
                LIMIT %s
            """
        elif metric == "vorp":
            query = """
                SELECT pts.player_id, p.player_name, pts.vorp, pts.season_id, pts.team_abbr
                FROM player_team_seasons pts
                LEFT JOIN players p ON pts.player_id = p.player_id
                WHERE pts.vorp IS NOT NULL
                ORDER BY pts.vorp DESC
                LIMIT %s
            """
        elif metric == "pts":
            query = """
                SELECT pts.player_id, p.player_name, pts.avg_points, pts.season_id, pts.team_abbr
                FROM player_team_seasons pts
                LEFT JOIN players p ON pts.player_id = p.player_id
                WHERE pts.avg_points IS NOT NULL
                ORDER BY pts.avg_points DESC
                LIMIT %s
            """
        elif metric == "reb":
            query = """
                SELECT pts.player_id, p.player_name, pts.avg_rebounds, pts.season_id, pts.team_abbr
                FROM player_team_seasons pts
                LEFT JOIN players p ON pts.player_id = p.player_id
                WHERE pts.avg_rebounds IS NOT NULL
                ORDER BY pts.avg_rebounds DESC
                LIMIT %s
            """
        else:  # ast
            query = """
                SELECT pts.player_id, p.player_name, pts.avg_assists, pts.season_id, pts.team_abbr
                FROM player_team_seasons pts
                LEFT JOIN players p ON pts.player_id = p.player_id
                WHERE pts.avg_assists IS NOT NULL
                ORDER BY pts.avg_assists DESC
                LIMIT %s
            """
        
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        
        for row in rows:
            player_id, player_name, value, season_id, team_abbr = row
            db_rankings.append({
                "player_id": player_id,
                "player_name": player_name if player_name else "未知球员",
                "value": round(value, 1) if value else 0,
                "season": season_id,
                "team": team_abbr
            })
    
    except Exception as e:
        print(f"Database error: {e}")
        db_rankings = []
    
    finally:
        if conn:
            conn.close()
    
    all_rankings = legendary_rankings + db_rankings
    all_rankings.sort(key=lambda x: x["value"], reverse=True)
    
    return {
        "success": True,
        "data": {
            "metric": metric,
            "metric_name": metrics[metric]["name"],
            "description": metrics[metric]["description"],
            "rankings": all_rankings[:limit]
        }
    }