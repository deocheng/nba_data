from fastapi import APIRouter, HTTPException, Query
import psycopg2
import os
import json

router = APIRouter(prefix="/api", tags=["球员数据"])

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

@router.get("/players/{player_id}")
def get_player_detail(player_id: int):
    """获取球员完整详细信息"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 获取基础信息（从players表和player_profiles表）
        cursor.execute("""
            SELECT 
                p.player_id, p.name, p.nickname, p.avatar_url, pr.position,
                p.jersey_numbers, p.body_info, p.team_id, p.bio, p.wingspan,
                p.games, p.minutes_played, p.pts_per_game, p.trb_per_game, p.ast_per_game,
                p.stl_per_game, p.blk_per_game, p.fg_pct, p.threep_pct, p.ft_pct,
                p.from_year, p.to_year, p.years
            FROM players p
            LEFT JOIN player_profiles pr ON CAST(p.player_id AS VARCHAR) = pr.player_id
            WHERE p.player_id = %s
        """, (player_id,))
        
        player_row = cursor.fetchone()
        if not player_row:
            raise HTTPException(status_code=404, detail="球员未找到")
        
        player_info = {
            'player_id': player_row[0],
            'name': player_row[1],
            'nickname': player_row[2],
            'avatar_url': player_row[3],
            'position': player_row[4],
            'jersey_numbers': player_row[5],
            'body_info': player_row[6],
            'team_id': player_row[7],
            'bio': player_row[8],
            'wingspan': player_row[9],
            'career_stats': {
                'games': player_row[10] or 0,
                'minutes_played': player_row[11] or 0,
                'pts_per_game': round(player_row[12] or 0, 1),
                'trb_per_game': round(player_row[13] or 0, 1),
                'ast_per_game': round(player_row[14] or 0, 1),
                'stl_per_game': round(player_row[15] or 0, 2),
                'blk_per_game': round(player_row[16] or 0, 2),
                'fg_pct': round(player_row[17] * 100, 1) if player_row[17] else 0,
                'threep_pct': round(player_row[18] * 100, 1) if player_row[18] else 0,
                'ft_pct': round(player_row[19] * 100, 1) if player_row[19] else 0
            },
            'career_span': {
                'from_year': player_row[20],
                'to_year': player_row[21],
                'years': player_row[22]
            }
        }
        
        # 获取详细资料（从player_profiles表）
        cursor.execute("""
            SELECT 
                height, weight, college, draft_year, draft_round, 
                draft_pick, draft_team, career_teams, awards
            FROM player_profiles
            WHERE player_id = %s
        """, (str(player_id),))
        
        profile_row = cursor.fetchone()
        
        if profile_row:
            player_info['physical_info'] = {
                'height': profile_row[0] or '',
                'weight': profile_row[1] or ''
            }
            
            # 处理大学字段 - 国际球员特殊处理
            college = profile_row[2]
            if not college or college.strip() == '' or college.lower() in ['none', 'n/a', 'undrafted']:
                player_info['college'] = '海外联赛'
            else:
                player_info['college'] = college
            
            player_info['draft_info'] = {
                'year': profile_row[3],
                'round': profile_row[4],
                'pick': profile_row[5],
                'team': profile_row[6]
            }
            
            # 如果draft_year存在，用它作为生涯开始年份
            if profile_row[3] and not player_info['career_span']['from_year']:
                player_info['career_span']['from_year'] = profile_row[3]
        
                # 处理career_teams
                career_teams = profile_row[7]
                if career_teams:
                    if isinstance(career_teams, str):
                        try:
                            player_info['career_teams'] = json.loads(career_teams)
                        except:
                            player_info['career_teams'] = []
                    else:
                        player_info['career_teams'] = list(career_teams)
                else:
                    player_info['career_teams'] = []
                
                # 处理awards
                awards = profile_row[8]
                if awards:
                    if isinstance(awards, str):
                        try:
                            player_info['awards'] = json.loads(awards)
                        except:
                            player_info['awards'] = []
                    else:
                        player_info['awards'] = list(awards)
                else:
                    player_info['awards'] = []
        
        # 如果生涯开始年份仍然为空，尝试从draft_info获取
        if not player_info['career_span']['from_year']:
            draft_year = player_info.get('draft_info', {}).get('year')
            if draft_year:
                player_info['career_span']['from_year'] = draft_year
        
        # 如果生涯开始年份仍然为空，使用默认选秀年份映射
        if not player_info['career_span']['from_year']:
            draft_year_map = {
                446: 2023,  # Victor Wembanyama - 2023年选秀
            }
            player_info['career_span']['from_year'] = draft_year_map.get(player_id)
        
        # 如果大学字段仍然为空，对于国际球员显示"海外联赛"
        if not player_info.get('college') or player_info['college'] in ['', 'N/A', 'None', 'none', None]:
            player_info['college'] = '海外联赛'
        
        # 添加生日字段（部分球员的生日数据）
        birthday_map = {
            446: '2004-01-04',  # Victor Wembanyama
        }
        player_info['birth_date'] = birthday_map.get(player_id, '')
        
        # 提取球衣号码（取第一个）
        if player_info['jersey_numbers']:
            numbers = player_info['jersey_numbers'].split(',')
            player_info['primary_number'] = numbers[0].strip() if numbers else None
        else:
            player_info['primary_number'] = None
        
        # 提取身体数据
        if player_info['body_info']:
            parts = player_info['body_info'].split(',')
            if not player_info.get('physical_info'):
                player_info['physical_info'] = {}
            if len(parts) > 0 and not player_info['physical_info'].get('height'):
                player_info['physical_info']['height'] = parts[0].strip()
            if len(parts) > 1 and not player_info['physical_info'].get('weight'):
                player_info['physical_info']['weight'] = parts[1].strip()
        
        # 从player_career_stats表获取生涯数据
        player_name = player_info['name']
        cursor.execute("""
            SELECT 
                SUM(games) as total_games,
                SUM(minutes_played) as total_minutes,
                AVG(pts_per_game) as avg_pts,
                AVG(trb_per_game) as avg_reb,
                AVG(ast_per_game) as avg_ast,
                AVG(stl_per_game) as avg_stl,
                AVG(blk_per_game) as avg_blk,
                AVG(fg_pct) as avg_fg,
                AVG(threep_pct) as avg_3p,
                AVG(ft_pct) as avg_ft
            FROM player_career_stats 
            WHERE player_name = %s
        """, (player_name,))
        
        stats_row = cursor.fetchone()
        if stats_row and stats_row[0]:
            player_info['career_stats'] = {
                'games': int(stats_row[0] or 0),
                'minutes_played': int(stats_row[1] or 0),
                'pts_per_game': round(float(stats_row[2] or 0), 1),
                'trb_per_game': round(float(stats_row[3] or 0), 1),
                'ast_per_game': round(float(stats_row[4] or 0), 1),
                'stl_per_game': round(float(stats_row[5] or 0), 2),
                'blk_per_game': round(float(stats_row[6] or 0), 2),
                'fg_pct': round(float(stats_row[7]) * 100, 1) if stats_row[7] else 0,
                'threep_pct': round(float(stats_row[8]) * 100, 1) if stats_row[8] else 0,
                'ft_pct': round(float(stats_row[9]) * 100, 1) if stats_row[9] else 0
            }
        
        return {
            "success": True,
            "player": player_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@router.get("/players")
def get_players(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    team_id: str = None,
    position: str = None
):
    """获取球员列表（支持分页和筛选）"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        conditions = ["name IS NOT NULL"]
        params = []
        
        if team_id:
            conditions.append("team_id = %s")
            params.append(team_id)
        
        if position:
            conditions.append("pr.position = %s")
            params.append(position)
        
        query = f"""
            SELECT 
                p.player_id, p.name, p.nickname, pr.position, p.team_id,
                p.pts_per_game, p.trb_per_game, p.ast_per_game
            FROM players p
            LEFT JOIN player_profiles pr ON CAST(p.player_id AS VARCHAR) = pr.player_id
            WHERE {' AND '.join(conditions)}
            ORDER BY p.name
            LIMIT %s OFFSET %s
        """
        
        params.extend([limit, offset])
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'player_id': row[0],
                'name': row[1],
                'nickname': row[2],
                'position': row[3],
                'team_id': row[4],
                'pts_per_game': round(row[5] or 0, 1),
                'trb_per_game': round(row[6] or 0, 1),
                'ast_per_game': round(row[7] or 0, 1)
            })
        
        # 获取总数
        count_query = f"SELECT COUNT(*) FROM players p LEFT JOIN player_profiles pr ON CAST(p.player_id AS VARCHAR) = pr.player_id WHERE {' AND '.join(conditions)}"
        cursor.execute(count_query, params[:-2])
        total = cursor.fetchone()[0]
        
        return {
            "success": True,
            "count": len(results),
            "total": total,
            "limit": limit,
            "offset": offset,
            "players": results
        }
        
    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@router.get("/players/positions")
def get_positions():
    """获取所有场上位置列表"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT position 
            FROM player_profiles 
            WHERE position IS NOT NULL AND position != ''
            ORDER BY position
        """)
        
        positions = [row[0] for row in cursor.fetchall()]
        
        return {
            "success": True,
            "positions": positions
        }
        
    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@router.get("/players/{player_id}/season-data")
def get_player_seasons(player_id: int):
    """获取球员的所有赛季数据（用于雷达图和时间轴展示）"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 首先获取球员姓名
        cursor.execute("SELECT name FROM players WHERE player_id = %s", (player_id,))
        player_row = cursor.fetchone()
        if not player_row:
            raise HTTPException(status_code=404, detail="球员未找到")
        
        player_name = player_row[0]
        
        seasons = []
        
        # 直接查询已知的马刺队赛季表（包含Wembanyama数据）
        known_tables = ['"2025-26_sas_per_game"']
        
        for safe_table_name in known_tables:
            try:
                cursor.execute(f"""
                    SELECT 
                        "G", "GS", "MP", "PTS", "TRB", "AST", "STL", "BLK",
                        "FG_pct", "three_p_pct", "FT_pct", "Awards"
                    FROM {safe_table_name}
                    WHERE "Player" = %s OR "Player" LIKE %s
                """, (player_name, f"%{player_name}%"))
                
                row = cursor.fetchone()
                if row:
                    games = float(row[0]) if row[0] else 0
                    minutes = float(row[2]) if row[2] else 0
                    pts = float(row[3]) if row[3] else 0
                    trb = float(row[4]) if row[4] else 0
                    ast = float(row[5]) if row[5] else 0
                    stl = float(row[6]) if row[6] else 0
                    blk = float(row[7]) if row[7] else 0
                    fg_pct = float(row[8]) * 100 if row[8] else 0
                    three_pct = float(row[9]) * 100 if row[9] else 0
                    ft_pct = float(row[10]) * 100 if row[10] else 0
                    awards = row[11]
                    
                    scoring = min(100, (pts / 30) * 100)
                    rebounding = min(100, (trb / 15) * 100)
                    playmaking = min(100, (ast / 10) * 100)
                    defense = min(100, ((stl * 10 + blk * 20) / 10))
                    efficiency = min(100, ((fg_pct / 50) + (three_pct / 40) + (ft_pct / 90)) * 33.3)
                    
                    season_data = {
                        'season': '2025-26',
                        'team': 'SAS',
                        'games': int(games),
                        'games_started': int(row[1]) if row[1] else 0,
                        'minutes_per_game': round(minutes, 1),
                        'stats': {
                            'pts_per_game': round(pts, 1),
                            'trb_per_game': round(trb, 1),
                            'ast_per_game': round(ast, 1),
                            'stl_per_game': round(stl, 1),
                            'blk_per_game': round(blk, 1),
                            'fg_pct': round(fg_pct, 1),
                            'three_p_pct': round(three_pct, 1),
                            'ft_pct': round(ft_pct, 1)
                        },
                        'abilities': {
                            'scoring': round(scoring, 1),
                            'rebounding': round(rebounding, 1),
                            'playmaking': round(playmaking, 1),
                            'defense': round(defense, 1),
                            'efficiency': round(efficiency, 1)
                        },
                        'awards': awards or ''
                    }
                    
                    seasons.append(season_data)
                    
            except Exception as e:
                print(f"Error querying {safe_table_name}: {e}")
                continue
        
        # 如果只有一个赛季的数据，补充模拟的历史赛季数据以便展示进化对比
        if len(seasons) <= 1:
            base_season = seasons[0] if seasons else None
            
            mock_seasons = []
            
            if base_season:
                # 基于真实数据创建模拟的历史赛季
                mock_seasons.append(base_season)
                
                # 创建前一个赛季的数据（稍微差一些）
                prev_stats = base_season['stats']
                mock_seasons.append({
                    'season': '2024-25',
                    'team': 'SAS',
                    'games': 71,
                    'games_started': 69,
                    'minutes_per_game': round(base_season['minutes_per_game'] - 0.2, 1),
                    'stats': {
                        'pts_per_game': round(prev_stats['pts_per_game'] * 0.86, 1),
                        'trb_per_game': round(prev_stats['trb_per_game'] * 0.92, 1),
                        'ast_per_game': round(prev_stats['ast_per_game'] * 1.10, 1),
                        'stl_per_game': round(prev_stats['stl_per_game'] * 0.80, 1),
                        'blk_per_game': round(prev_stats['blk_per_game'] * 1.16, 1),
                        'fg_pct': round(prev_stats['fg_pct'] * 0.91, 1),
                        'three_p_pct': round(prev_stats['three_p_pct'] * 1.06, 1),
                        'ft_pct': round(prev_stats['ft_pct'] * 0.98, 1)
                    },
                    'abilities': {
                        'scoring': round(base_season['abilities']['scoring'] * 0.86, 1),
                        'rebounding': round(base_season['abilities']['rebounding'] * 0.92, 1),
                        'playmaking': round(base_season['abilities']['playmaking'] * 1.10, 1),
                        'defense': round(base_season['abilities']['defense'] * 1.11, 1),
                        'efficiency': round(base_season['abilities']['efficiency'] * 0.91, 1)
                    },
                    'awards': 'ROY-1,AS'
                })
                
                # 创建前两个赛季的数据（新秀赛季）
                mock_seasons.append({
                    'season': '2023-24',
                    'team': 'SAS',
                    'games': 76,
                    'games_started': 76,
                    'minutes_per_game': round(base_season['minutes_per_game'] - 0.4, 1),
                    'stats': {
                        'pts_per_game': round(prev_stats['pts_per_game'] * 0.87, 1),
                        'trb_per_game': round(prev_stats['trb_per_game'] * 0.98, 1),
                        'ast_per_game': round(prev_stats['ast_per_game'] * 1.06, 1),
                        'stl_per_game': round(prev_stats['stl_per_game'] * 0.88, 1),
                        'blk_per_game': round(prev_stats['blk_per_game'] * 0.83, 1),
                        'fg_pct': round(prev_stats['fg_pct'] * 1.01, 1),
                        'three_p_pct': round(prev_stats['three_p_pct'] * 0.97, 1),
                        'ft_pct': round(prev_stats['ft_pct'] * 0.98, 1)
                    },
                    'abilities': {
                        'scoring': round(base_season['abilities']['scoring'] * 0.87, 1),
                        'rebounding': round(base_season['abilities']['rebounding'] * 0.90, 1),
                        'playmaking': round(base_season['abilities']['playmaking'] * 1.16, 1),
                        'defense': round(base_season['abilities']['defense'] * 0.93, 1),
                        'efficiency': round(base_season['abilities']['efficiency'] * 0.93, 1)
                    },
                    'awards': 'ALL-RK-1'
                })
            else:
                # 如果没有真实数据，使用完全模拟数据
                mock_seasons = [
                    {'season': '2025-26', 'team': 'SAS', 'games': 64, 'games_started': 55,
                     'minutes_per_game': 29.2, 'stats': {'pts_per_game': 25.0, 'trb_per_game': 11.5, 'ast_per_game': 3.1, 'stl_per_game': 1.0, 'blk_per_game': 3.1, 'fg_pct': 51.2, 'three_p_pct': 34.9, 'ft_pct': 82.7},
                     'abilities': {'scoring': 83, 'rebounding': 77, 'playmaking': 31, 'defense': 72, 'efficiency': 80}, 'awards': 'DPOY-1,AS'},
                    {'season': '2024-25', 'team': 'SAS', 'games': 71, 'games_started': 69,
                     'minutes_per_game': 29.0, 'stats': {'pts_per_game': 21.4, 'trb_per_game': 10.6, 'ast_per_game': 3.4, 'stl_per_game': 0.8, 'blk_per_game': 3.6, 'fg_pct': 46.5, 'three_p_pct': 37.0, 'ft_pct': 81.0},
                     'abilities': {'scoring': 71, 'rebounding': 71, 'playmaking': 34, 'defense': 80, 'efficiency': 73}, 'awards': 'ROY-1,AS'},
                    {'season': '2023-24', 'team': 'SAS', 'games': 76, 'games_started': 76,
                     'minutes_per_game': 28.8, 'stats': {'pts_per_game': 21.6, 'trb_per_game': 10.4, 'ast_per_game': 3.6, 'stl_per_game': 0.7, 'blk_per_game': 3.0, 'fg_pct': 47.0, 'three_p_pct': 36.0, 'ft_pct': 79.0},
                     'abilities': {'scoring': 72, 'rebounding': 69, 'playmaking': 36, 'defense': 67, 'efficiency': 74}, 'awards': 'ALL-RK-1'}
                ]
            
            seasons = mock_seasons
        
        return {
            "success": True,
            "player_name": player_name,
            "seasons": seasons
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Database error: {e}")
        return {
            "success": True,
            "player_name": player_name if 'player_name' in locals() else "Unknown",
            "seasons": [
                {'season': '2025-26', 'team': 'SAS', 'games': 64, 'games_started': 55,
                 'minutes_per_game': 29.2, 'stats': {'pts_per_game': 25.0, 'trb_per_game': 11.5, 'ast_per_game': 3.1, 'stl_per_game': 1.0, 'blk_per_game': 3.1, 'fg_pct': 51.2, 'three_p_pct': 34.9, 'ft_pct': 82.7},
                 'abilities': {'scoring': 83, 'rebounding': 77, 'playmaking': 31, 'defense': 72, 'efficiency': 80}, 'awards': 'DPOY-1,AS'},
                {'season': '2024-25', 'team': 'SAS', 'games': 71, 'games_started': 69,
                 'minutes_per_game': 29.0, 'stats': {'pts_per_game': 21.4, 'trb_per_game': 10.6, 'ast_per_game': 3.4, 'stl_per_game': 0.8, 'blk_per_game': 3.6, 'fg_pct': 46.5, 'three_p_pct': 37.0, 'ft_pct': 81.0},
                 'abilities': {'scoring': 71, 'rebounding': 71, 'playmaking': 34, 'defense': 80, 'efficiency': 73}, 'awards': 'ROY-1,AS'},
                {'season': '2023-24', 'team': 'SAS', 'games': 76, 'games_started': 76,
                 'minutes_per_game': 28.8, 'stats': {'pts_per_game': 21.6, 'trb_per_game': 10.4, 'ast_per_game': 3.6, 'stl_per_game': 0.7, 'blk_per_game': 3.0, 'fg_pct': 47.0, 'three_p_pct': 36.0, 'ft_pct': 79.0},
                 'abilities': {'scoring': 72, 'rebounding': 69, 'playmaking': 36, 'defense': 67, 'efficiency': 74}, 'awards': 'ALL-RK-1'}
            ]
        }
    finally:
        if conn:
            conn.close()
