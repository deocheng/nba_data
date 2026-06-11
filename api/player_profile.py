from fastapi import APIRouter, HTTPException
import psycopg2
import os
import json

router = APIRouter(prefix="/api", tags=["球员个人页面"])

DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'nba'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5433')
}

def get_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_client_encoding('UTF8')
    return conn

@router.get("/player/{player_id}/profile")
def get_player_profile(player_id: str):
    """获取球员完整个人资料，包括生涯数据和履历"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 获取球员基本信息
        cursor.execute("""
            SELECT player_id, player_name, draft_year, draft_round, draft_pick, draft_team,
                   height, weight, position, college, career_teams, awards, bio
            FROM player_profiles
            WHERE player_id = %s
        """, (player_id,))
        
        profile_row = cursor.fetchone()
        
        if not profile_row:
            raise HTTPException(status_code=404, detail="球员资料未找到")
        
        profile = {
            "player_id": profile_row[0],
            "player_name": profile_row[1],
            "draft_info": {
                "year": profile_row[2],
                "round": profile_row[3],
                "pick": profile_row[4],
                "team": profile_row[5]
            },
            "physical_info": {
                "height": profile_row[6],
                "weight": profile_row[7],
                "position": profile_row[8],
                "college": profile_row[9]
            },
            "career_teams": profile_row[10] if profile_row[10] else [],
            "awards": profile_row[11] if profile_row[11] else [],
            "bio": profile_row[12]
        }
        
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
        
        total_games, played_games, inactive_games, total_minutes, total_points, \
        total_rebounds, total_assists, total_steals, total_blocks, total_fg_made, \
        total_fg_att, total_three_made, total_three_att, total_ft_made, total_ft_att = career_total
        
        # 计算场均数据
        career_summary = {
            "total_games": total_games or 0,
            "played_games": played_games or 0,
            "inactive_games": inactive_games or 0,
            "total_minutes": round(total_minutes or 0, 1),
            "total_points": total_points or 0,
            "total_rebounds": total_rebounds or 0,
            "total_assists": total_assists or 0,
            "total_steals": total_steals or 0,
            "total_blocks": total_blocks or 0,
            "total_fg_made": total_fg_made or 0,
            "total_fg_att": total_fg_att or 0,
            "total_three_made": total_three_made or 0,
            "total_three_att": total_three_att or 0,
            "total_ft_made": total_ft_made or 0,
            "total_ft_att": total_ft_att or 0
        }
        
        career_averages = {
            "avg_minutes": round((total_minutes or 0) / played_games, 1) if played_games and played_games > 0 else 0,
            "avg_points": round((total_points or 0) / played_games, 1) if played_games and played_games > 0 else 0,
            "avg_rebounds": round((total_rebounds or 0) / played_games, 1) if played_games and played_games > 0 else 0,
            "avg_assists": round((total_assists or 0) / played_games, 1) if played_games and played_games > 0 else 0,
            "avg_steals": round((total_steals or 0) / played_games, 2) if played_games and played_games > 0 else 0,
            "avg_blocks": round((total_blocks or 0) / played_games, 2) if played_games and played_games > 0 else 0,
            "fg_pct": round((total_fg_made or 0) / (total_fg_att or 1) * 100, 1) if total_fg_att and total_fg_att > 0 else 0,
            "three_pct": round((total_three_made or 0) / (total_three_att or 1) * 100, 1) if total_three_att and total_three_att > 0 else 0,
            "ft_pct": round((total_ft_made or 0) / (total_ft_att or 1) * 100, 1) if total_ft_att and total_ft_att > 0 else 0
        }
        
        # 获取按赛季和比赛类型统计
        cursor.execute("""
            SELECT 
                season_id,
                game_type,
                SUM(CASE WHEN minutes_played > 0 THEN 1 ELSE 0 END) as games,
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
            ORDER BY season_id DESC, game_type
        """, (player_id,))
        
        seasons_data = []
        for row in cursor.fetchall():
            season_id, game_type, games, minutes, points, rebounds, assists, steals, \
            blocks, fg_made, fg_att, three_made, three_att, ft_made, ft_att = row
            
            seasons_data.append({
                "season_id": season_id,
                "game_type": game_type,
                "games": games,
                "minutes": round(minutes or 0, 1),
                "points": points or 0,
                "rebounds": rebounds or 0,
                "assists": assists or 0,
                "steals": steals or 0,
                "blocks": blocks or 0,
                "fg_made": fg_made or 0,
                "fg_att": fg_att or 0,
                "fg_pct": round((fg_made or 0) / (fg_att or 1) * 100, 1) if fg_att and fg_att > 0 else 0,
                "three_made": three_made or 0,
                "three_att": three_att or 0,
                "three_pct": round((three_made or 0) / (three_att or 1) * 100, 1) if three_att and three_att > 0 else 0,
                "ft_made": ft_made or 0,
                "ft_att": ft_att or 0,
                "ft_pct": round((ft_made or 0) / (ft_att or 1) * 100, 1) if ft_att and ft_att > 0 else 0,
                "avg_minutes": round((minutes or 0) / games, 1) if games and games > 0 else 0,
                "avg_points": round((points or 0) / games, 1) if games and games > 0 else 0
            })
        
        # 获取特殊场次
        cursor.execute("""
            SELECT game_date, game_type, minutes_played, points, result, notes
            FROM player_game_logs
            WHERE player_id = %s AND notes IS NOT NULL
            ORDER BY game_date DESC
        """, (player_id,))
        
        special_games = []
        for row in cursor.fetchall():
            special_games.append({
                "game_date": str(row[0]),
                "game_type": row[1],
                "minutes_played": round(row[2] or 0, 1),
                "points": row[3],
                "result": row[4],
                "notes": row[5]
            })
        
        # 获取缺席场次
        cursor.execute("""
            SELECT game_date, season_id, game_type, opp_team_abbr, result
            FROM player_game_logs
            WHERE player_id = %s AND minutes_played = 0
            ORDER BY game_date DESC
        """, (player_id,))
        
        inactive_games_list = []
        for row in cursor.fetchall():
            inactive_games_list.append({
                "game_date": str(row[0]),
                "season_id": row[1],
                "game_type": row[2],
                "opponent": row[3] or "",
                "result": row[4] or ""
            })
        
        # 获取球队效力期间详细数据
        team_stats = {}
        cursor.execute("""
            SELECT team_id, season_id, game_type,
                   COUNT(*) as games,
                   SUM(points) as points,
                   SUM(rebounds) as rebounds,
                   SUM(assists) as assists,
                   SUM(minutes_played) as minutes
            FROM player_game_logs
            WHERE player_id = %s AND minutes_played > 0
            GROUP BY team_id, season_id, game_type
            ORDER BY team_id, season_id
        """, (player_id,))
        
        for row in cursor.fetchall():
            team_id, season_id, game_type, games, points, rebounds, assists, minutes = row
            key = f"{team_id}_{season_id}_{game_type}"
            if key not in team_stats:
                team_stats[key] = {
                    "team_id": team_id,
                    "season_id": season_id,
                    "game_type": game_type,
                    "games": 0,
                    "points": 0,
                    "rebounds": 0,
                    "assists": 0,
                    "minutes": 0
                }
            team_stats[key]["games"] += games
            team_stats[key]["points"] += points or 0
            team_stats[key]["rebounds"] += rebounds or 0
            team_stats[key]["assists"] += assists or 0
            team_stats[key]["minutes"] += minutes or 0
        
        team_detailed_stats = list(team_stats.values())
        
        # 计算雷达图数据
        radar_labels = ["得分能力", "篮板能力", "助攻能力", "防守能力", "投篮效率", "三分能力", "罚球能力"]
        
        radar_data = {
            "labels": radar_labels,
            "datasets": [{
                "label": "球员能力",
                "data": [
                    min(career_averages["avg_points"] / 40, 1),
                    min(career_averages["avg_rebounds"] / 15, 1),
                    min(career_averages["avg_assists"] / 12, 1),
                    min((career_averages["avg_steals"] + career_averages["avg_blocks"]) / 4, 1),
                    career_averages["fg_pct"] / 100,
                    career_averages["three_pct"] / 100,
                    career_averages["ft_pct"] / 100
                ],
                "actualValues": [
                    round(career_averages["avg_points"], 1),
                    round(career_averages["avg_rebounds"], 1),
                    round(career_averages["avg_assists"], 1),
                    round(career_averages["avg_steals"] + career_averages["avg_blocks"], 2),
                    round(career_averages["fg_pct"], 1),
                    round(career_averages["three_pct"], 1),
                    round(career_averages["ft_pct"], 1)
                ]
            }]
        }
        
        return {
            "success": True,
            "data": {
                "profile": profile,
                "career_summary": career_summary,
                "career_averages": career_averages,
                "seasons": seasons_data,
                "special_games": special_games,
                "inactive_games": inactive_games_list,
                "team_stats": team_detailed_stats,
                "radar_data": radar_data
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@router.get("/players/list")
def get_players_list():
    """获取所有球员列表"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT player_id, player_name, position, college
            FROM player_profiles
            ORDER BY player_name
        """)
        
        players = []
        for row in cursor.fetchall():
            players.append({
                "player_id": row[0],
                "player_name": row[1],
                "position": row[2],
                "college": row[3]
            })
        
        return {
            "success": True,
            "data": players
        }
    
    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@router.get("/player/{player_id}/recent_games")
def get_player_recent_games(player_id: str, limit: int = 10):
    """获取球员最近N场比赛数据"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT game_date, game_type, minutes_played, points, rebounds, assists, 
                   steals, blocks, fg_made, fg_att, three_made, three_att, ft_made, ft_att, result
            FROM player_game_logs
            WHERE player_id = %s AND minutes_played > 0
            ORDER BY game_date DESC
            LIMIT %s
        """, (player_id, limit))
        
        games = []
        for row in cursor.fetchall():
            games.append({
                "game_date": str(row[0]),
                "game_type": row[1],
                "minutes_played": round(row[2] or 0, 1),
                "points": row[3] or 0,
                "rebounds": row[4] or 0,
                "assists": row[5] or 0,
                "steals": row[6] or 0,
                "blocks": row[7] or 0,
                "fg_made": row[8] or 0,
                "fg_att": row[9] or 0,
                "three_made": row[10] or 0,
                "three_att": row[11] or 0,
                "ft_made": row[12] or 0,
                "ft_att": row[13] or 0,
                "result": row[14] or ""
            })
        
        # 反转列表，让最早的比赛在前面
        games.reverse()
        
        return {
            "success": True,
            "data": games
        }
    
    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()
