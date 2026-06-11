#!/usr/bin/env python3
"""
高阶数据API路由
提供球员高阶数据查询接口
"""

from fastapi import APIRouter, HTTPException, Query
import psycopg2
import os

router = APIRouter(prefix="/api/advanced-stats", tags=["高阶数据"])

DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'nba'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5433')
}

def get_connection():
    """获取数据库连接"""
    return psycopg2.connect(**DB_CONFIG)

@router.get("/")
def get_advanced_stats(
    player_id: str = Query(None, description="球员ID"),
    team_id: str = Query(None, description="球队ID"),
    season_id: str = Query(None, description="赛季ID"),
    sort_by: str = Query("per", description="排序字段"),
    limit: int = Query(50, description="返回数量限制")
):
    """获取高阶数据列表"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            pts.player_id, pts.team_id, pts.season_id,
            p.player_name, t.team_name, t.team_abbr,
            pts.games_played, pts.minutes_played,
            pts.per, pts.ts_pct, pts.usg_pct,
            pts.ws, pts.ws_per_48, pts.bpm, pts.vorp,
            pts.offensive_rating, pts.defensive_rating,
            pts.assist_ratio, pts.turnover_ratio, pts.rebound_rate,
            pts.avg_points, pts.avg_rebounds, pts.avg_assists,
            pts.fg_pct, pts.three_pct, pts.ft_pct
        FROM player_team_seasons pts
        LEFT JOIN players p ON pts.player_id = p.player_id
        LEFT JOIN teams t ON pts.team_id = t.team_id
        WHERE 1=1
        """
        
        params = []
        
        if player_id:
            query += " AND pts.player_id = %s"
            params.append(player_id)
        
        if team_id:
            query += " AND pts.team_id = %s"
            params.append(team_id)
        
        if season_id:
            query += " AND pts.season_id = %s"
            params.append(season_id)
        
        # 验证排序字段
        valid_sort_fields = ['per', 'ts_pct', 'usg_pct', 'ws', 'bpm', 'vorp', 'offensive_rating', 'defensive_rating']
        if sort_by not in valid_sort_fields:
            sort_by = 'per'
        
        query += f" ORDER BY pts.{sort_by} DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, tuple(params))
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return {"success": True, "data": results}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@router.get("/{player_id}")
def get_player_advanced_stats(player_id: str):
    """获取单个球员的高阶数据"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            pts.player_id, pts.team_id, pts.season_id,
            p.player_name, t.team_name, t.team_abbr,
            pts.games_played, pts.minutes_played,
            pts.per, pts.ts_pct, pts.usg_pct,
            pts.ws, pts.ws_per_48, pts.bpm, pts.vorp,
            pts.offensive_rating, pts.defensive_rating,
            pts.assist_ratio, pts.turnover_ratio, pts.rebound_rate,
            pts.avg_points, pts.avg_rebounds, pts.avg_assists,
            pts.fg_pct, pts.three_pct, pts.ft_pct
        FROM player_team_seasons pts
        LEFT JOIN players p ON pts.player_id = p.player_id
        LEFT JOIN teams t ON pts.team_id = t.team_id
        WHERE pts.player_id = %s
        ORDER BY pts.season_id
        """
        
        cursor.execute(query, (player_id,))
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        if not results:
            raise HTTPException(status_code=404, detail="球员高阶数据未找到")
        
        return {"success": True, "data": results}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@router.get("/leaders/{stat}")
def get_leaders(stat: str, limit: int = 10):
    """获取特定高阶指标的领先者"""
    valid_stats = ['per', 'ts_pct', 'usg_pct', 'ws', 'bpm', 'vorp', 'offensive_rating', 'defensive_rating']
    
    if stat not in valid_stats:
        raise HTTPException(status_code=400, detail=f"无效的统计指标: {stat}")
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = f"""
        SELECT 
            pts.player_id, p.player_name, pts.team_id, t.team_abbr,
            pts.season_id, pts.{stat}
        FROM player_team_seasons pts
        LEFT JOIN players p ON pts.player_id = p.player_id
        LEFT JOIN teams t ON pts.team_id = t.team_id
        ORDER BY pts.{stat} DESC LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return {"success": True, "data": results}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()
