
from fastapi import APIRouter, HTTPException
import psycopg2
import os

router = APIRouter(prefix="/api", tags=["球员生涯数据"])

DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'nba'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5433')
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

@router.get("/player/{player_id}/career")
def get_player_career(player_id: str):
    """获取球员完整生涯数据"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 获取生涯总数据
        cursor.execute("""
            SELECT 
                COUNT(*) as total_games,
                SUM(CASE WHEN minutes_played > 0 THEN 1 ELSE 0 END) as played_games,
                SUM(CASE WHEN minutes_played = 0 THEN 1 ELSE 0 END) as inactive_games,
                SUM(minutes_played) as total_minutes,
                SUM(points) as total_points,
                SUM(rebounds) as total_rebounds,
                SUM(assists) as total_assists,
                SUM(steals) as total_steals,
                SUM(blocks) as total_blocks,
                SUM(fg_made) as total_fg_made,
                SUM(fg_att) as total_fg_att,
                SUM(three_made) as total_three_made,
                SUM(three_att) as total_three_att,
                SUM(ft_made) as total_ft_made,
                SUM(ft_att) as total_ft_att
            FROM player_game_logs
            WHERE player_id = %s
        """, (player_id,))
        
        career_total = cursor.fetchone()
        
        if not career_total or career_total[0] == 0:
            raise HTTPException(status_code=404, detail="球员数据未找到")
        
        total_games, played_games, inactive_games, total_minutes, total_points, \
        total_rebounds, total_assists, total_steals, total_blocks, total_fg_made, \
        total_fg_att, total_three_made, total_three_att, total_ft_made, total_ft_att = career_total
        
        # 计算场均数据
        avg_minutes = total_minutes / played_games if played_games > 0 else 0
        avg_points = total_points / played_games if played_games > 0 else 0
        avg_rebounds = total_rebounds / played_games if played_games > 0 else 0
        avg_assists = total_assists / played_games if played_games > 0 else 0
        avg_steals = total_steals / played_games if played_games > 0 else 0
        avg_blocks = total_blocks / played_games if played_games > 0 else 0
        fg_pct = total_fg_made / total_fg_att if total_fg_att > 0 else 0
        three_pct = total_three_made / total_three_att if total_three_att > 0 else 0
        ft_pct = total_ft_made / total_ft_att if total_ft_att > 0 else 0
        
        # 获取按赛季统计
        cursor.execute("""
            SELECT 
                season_id,
                game_type,
                COUNT(*) as games,
                SUM(minutes_played) as minutes,
                SUM(points) as points,
                SUM(rebounds) as rebounds,
                SUM(assists) as assists,
                SUM(steals) as steals,
                SUM(blocks) as blocks,
                SUM(fg_made) as fg_made,
                SUM(fg_att) as fg_att,
                SUM(three_made) as three_made,
                SUM(three_att) as three_att,
                SUM(ft_made) as ft_made,
                SUM(ft_att) as ft_att
            FROM player_game_logs
            WHERE player_id = %s
            GROUP BY season_id, game_type
            ORDER BY season_id, game_type
        """, (player_id,))
        
        seasons_data = []
        for row in cursor.fetchall():
            season_id, game_type, games, minutes, points, rebounds, assists, steals, \
            blocks, fg_made, fg_att, three_made, three_att, ft_made, ft_att = row
            
            season_avg_minutes = minutes / games if games > 0 else 0
            season_avg_points = points / games if games > 0 else 0
            
            seasons_data.append({
                "season_id": season_id,
                "game_type": game_type,
                "games": games,
                "minutes": round(minutes, 1),
                "points": points,
                "rebounds": rebounds,
                "assists": assists,
                "steals": steals,
                "blocks": blocks,
                "fg_made": fg_made,
                "fg_att": fg_att,
                "fg_pct": round(fg_made / fg_att * 100, 1) if fg_att > 0 else 0,
                "three_made": three_made,
                "three_att": three_att,
                "three_pct": round(three_made / three_att * 100, 1) if three_att > 0 else 0,
                "ft_made": ft_made,
                "ft_att": ft_att,
                "ft_pct": round(ft_made / ft_att * 100, 1) if ft_att > 0 else 0,
                "avg_minutes": round(season_avg_minutes, 1),
                "avg_points": round(season_avg_points, 1)
            })
        
        # 获取特殊场次（有注释的）
        cursor.execute("""
            SELECT game_date, game_type, minutes_played, points, result, notes
            FROM player_game_logs
            WHERE player_id = %s AND notes IS NOT NULL
            ORDER BY game_date
        """, (player_id,))
        
        special_games = []
        for row in cursor.fetchall():
            special_games.append({
                "game_date": str(row[0]),
                "game_type": row[1],
                "minutes_played": round(row[2], 1) if row[2] else 0,
                "points": row[3],
                "result": row[4],
                "notes": row[5]
            })
        
        return {
            "success": True,
            "data": {
                "player_id": player_id,
                "career_summary": {
                    "total_games": total_games,
                    "played_games": played_games,
                    "inactive_games": inactive_games,
                    "total_minutes": round(total_minutes, 1),
                    "total_points": total_points,
                    "total_rebounds": total_rebounds,
                    "total_assists": total_assists,
                    "total_steals": total_steals,
                    "total_blocks": total_blocks,
                    "total_fg_made": total_fg_made,
                    "total_fg_att": total_fg_att,
                    "total_three_made": total_three_made,
                    "total_three_att": total_three_att,
                    "total_ft_made": total_ft_made,
                    "total_ft_att": total_ft_att
                },
                "career_averages": {
                    "avg_minutes": round(avg_minutes, 1),
                    "avg_points": round(avg_points, 1),
                    "avg_rebounds": round(avg_rebounds, 1),
                    "avg_assists": round(avg_assists, 1),
                    "avg_steals": round(avg_steals, 2),
                    "avg_blocks": round(avg_blocks, 2),
                    "fg_pct": round(fg_pct * 100, 1),
                    "three_pct": round(three_pct * 100, 1),
                    "ft_pct": round(ft_pct * 100, 1)
                },
                "seasons": seasons_data,
                "special_games": special_games
            }
        }
    
    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()
