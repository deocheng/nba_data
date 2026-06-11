from fastapi import APIRouter, HTTPException, Query
import psycopg2
import os
import csv
import io
from datetime import datetime

router = APIRouter(prefix="/api", tags=["球队历史"])

DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'nba'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5433')
}

CSV_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "CSV")

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def parse_team_history_csv(filepath):
    """解析球队历史CSV数据"""
    games = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if len(lines) < 3:
            return games
        
        headers = lines[1].strip().split(',')
        
        for line in lines[2:]:
            if not line.strip():
                continue
            row = line.strip().split(',')
            if len(row) < 8:
                continue
            
            game_date = row[2].strip()
            if not game_date:
                continue
            
            team_score = row[6].strip()
            opp_score = row[7].strip()
            
            if not team_score.isdigit() or not opp_score.isdigit():
                continue
            
            fg_pct = float(row[11].strip()) if row[11].strip() else 0
            ft_pct = float(row[21].strip()) if row[21].strip() else 0
            
            year = int(game_date.split('-')[0])
            month = int(game_date.split('-')[1])
            season = f"{year}-{year+1}" if month >= 10 else f"{year-1}-{year}"
            
            games.append({
                'season': season,
                'game_date': game_date,
                'team_score': int(team_score),
                'opp_score': int(opp_score),
                'opp': row[4].strip(),
                'rslt': row[5].strip(),
                'fg_pct': fg_pct,
                'ft_pct': ft_pct
            })
    except Exception as e:
        print(f"Error parsing CSV: {e}")
    
    return games

def get_spurs_history_from_csv():
    """从CSV获取马刺历史数据"""
    filepath = os.path.join(CSV_DIR, "1989-2026SAS.csv")
    if os.path.exists(filepath):
        return parse_team_history_csv(filepath)
    return []

@router.get("/teams/{team_id}/history")
def get_team_history(team_id: str):
    """获取球队历史战绩数据"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT season, COUNT(*) as total_games,
                   SUM(CASE WHEN team_score > opp_score THEN 1 ELSE 0 END) as wins,
                   SUM(CASE WHEN team_score < opp_score THEN 1 ELSE 0 END) as losses,
                   AVG(team_score) as avg_points,
                   AVG(opp_score) as avg_opp_points,
                   AVG(fg_pct) as avg_fg_pct,
                   AVG(ft_pct) as avg_ft_pct
            FROM historical_games 
            WHERE team_abbr = %s
            GROUP BY season
            ORDER BY season
        """
        cursor.execute(query, (team_id,))
        seasons = cursor.fetchall()
        
        if seasons:
            result = []
            for season, total_games, wins, losses, avg_points, avg_opp_points, avg_fg_pct, avg_ft_pct in seasons:
                win_rate = wins / total_games if total_games > 0 else 0
                result.append({
                    "season": season,
                    "total_games": total_games,
                    "wins": wins,
                    "losses": losses,
                    "win_rate": round(win_rate * 100, 1),
                    "avg_points": round(avg_points, 1),
                    "avg_opp_points": round(avg_opp_points, 1),
                    "avg_fg_pct": round(avg_fg_pct * 100, 1),
                    "avg_ft_pct": round(avg_ft_pct * 100, 1)
                })
        else:
            result = []
        
        query = """
            SELECT team_name, team_abbr, conference, conference_cn, division, division_cn
            FROM teams WHERE team_abbr = %s OR team_id = %s
        """
        cursor.execute(query, (team_id, team_id))
        team_info = cursor.fetchone()
        
        team_name = team_info[0] if team_info else team_id
        team_abbr = team_info[1] if team_info else team_id
        
        if not result:
            raise Exception("No data from database")
        
        return {
            "success": True,
            "data": {
                "team_info": {
                    "team_name": team_name,
                    "team_abbr": team_abbr,
                    "conference": team_info[2] if team_info else "",
                    "conference_cn": team_info[3] if team_info else "",
                    "division": team_info[4] if team_info else "",
                    "division_cn": team_info[5] if team_info else ""
                },
                "seasons": result,
                "total_seasons": len(result),
                "all_time_wins": sum(s["wins"] for s in result),
                "all_time_losses": sum(s["losses"] for s in result),
                "all_time_win_rate": round(sum(s["wins"] for s in result) / sum(s["total_games"] for s in result) * 100, 1) if sum(s["total_games"] for s in result) > 0 else 0
            }
        }
    
    except Exception as e:
        print(f"Database query failed, using CSV backup: {e}")
        games = get_spurs_history_from_csv()
        
        if not games:
            return {
                "success": False,
                "message": "No data available"
            }
        
        season_stats = {}
        for game in games:
            season = game['season']
            if season not in season_stats:
                season_stats[season] = {
                    'total_games': 0,
                    'wins': 0,
                    'losses': 0,
                    'total_points': 0,
                    'total_opp_points': 0,
                    'total_fg_pct': 0,
                    'total_ft_pct': 0
                }
            
            season_stats[season]['total_games'] += 1
            season_stats[season]['total_points'] += game['team_score']
            season_stats[season]['total_opp_points'] += game['opp_score']
            season_stats[season]['total_fg_pct'] += game['fg_pct']
            season_stats[season]['total_ft_pct'] += game['ft_pct']
            
            if game['team_score'] > game['opp_score']:
                season_stats[season]['wins'] += 1
            else:
                season_stats[season]['losses'] += 1
        
        result = []
        for season in sorted(season_stats.keys()):
            stats = season_stats[season]
            win_rate = stats['wins'] / stats['total_games'] if stats['total_games'] > 0 else 0
            result.append({
                "season": season,
                "total_games": stats['total_games'],
                "wins": stats['wins'],
                "losses": stats['losses'],
                "win_rate": round(win_rate * 100, 1),
                "avg_points": round(stats['total_points'] / stats['total_games'], 1) if stats['total_games'] > 0 else 0,
                "avg_opp_points": round(stats['total_opp_points'] / stats['total_games'], 1) if stats['total_games'] > 0 else 0,
                "avg_fg_pct": round(stats['total_fg_pct'] / stats['total_games'] * 100, 1) if stats['total_games'] > 0 else 0,
                "avg_ft_pct": round(stats['total_ft_pct'] / stats['total_games'] * 100, 1) if stats['total_games'] > 0 else 0
            })
        
        return {
            "success": True,
            "data": {
                "team_info": {
                    "team_name": "圣安东尼奥马刺",
                    "team_abbr": "SAS",
                    "conference": "Western",
                    "conference_cn": "西部",
                    "division": "Southwest",
                    "division_cn": "西南赛区"
                },
                "seasons": result,
                "total_seasons": len(result),
                "all_time_wins": sum(s["wins"] for s in result),
                "all_time_losses": sum(s["losses"] for s in result),
                "all_time_win_rate": round(sum(s["wins"] for s in result) / sum(s["total_games"] for s in result) * 100, 1) if sum(s["total_games"] for s in result) > 0 else 0
            }
        }
    finally:
        if conn:
            conn.close()

@router.get("/teams/{team_id}/season/{season_id}")
def get_team_season_detail(team_id: str, season_id: str):
    """获取球队特定赛季详情"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT game_date, team_score, opp_score, fg_pct, ft_pct
            FROM historical_games 
            WHERE team_abbr = %s AND season = %s
            ORDER BY game_date
        """
        cursor.execute(query, (team_id, season_id))
        games = cursor.fetchall()
        
        if games:
            result = []
            for game_date, team_score, opp_score, fg_pct, ft_pct in games:
                result.append({
                    "game_date": game_date.strftime("%Y-%m-%d") if game_date else "",
                    "team_score": team_score,
                    "opp_score": opp_score,
                    "result": "W" if team_score > opp_score else "L",
                    "fg_pct": round(fg_pct * 100, 1),
                    "ft_pct": round(ft_pct * 100, 1),
                    "margin": team_score - opp_score
                })
        else:
            result = []
        
        if result:
            return {
                "success": True,
                "data": {
                    "team_id": team_id,
                    "season": season_id,
                    "games": result,
                    "total_games": len(result),
                    "wins": sum(1 for g in result if g["result"] == "W"),
                    "losses": sum(1 for g in result if g["result"] == "L"),
                    "win_rate": round(sum(1 for g in result if g["result"] == "W") / len(result) * 100, 1) if len(result) > 0 else 0,
                    "avg_points": round(sum(g["team_score"] for g in result) / len(result), 1) if len(result) > 0 else 0,
                    "avg_opp_points": round(sum(g["opp_score"] for g in result) / len(result), 1) if len(result) > 0 else 0
                }
            }
        else:
            raise Exception("No data from database")
    
    except Exception as e:
        print(f"Database query failed, using CSV backup: {e}")
        all_games = get_spurs_history_from_csv()
        season_games = [g for g in all_games if g['season'] == season_id]
        
        if not season_games:
            season_format = season_id
            if '-' in season_id and len(season_id) == 7:
                parts = season_id.split('-')
                season_format = f"{parts[0]}-{parts[1][-2:]}"
            
            season_games = [g for g in all_games if g['season'] == season_format]
        
        result = []
        for game in season_games:
            result.append({
                "game_date": game['game_date'],
                "team_score": game['team_score'],
                "opp_score": game['opp_score'],
                "result": "W" if game['team_score'] > game['opp_score'] else "L",
                "fg_pct": round(game['fg_pct'] * 100, 1),
                "ft_pct": round(game['ft_pct'] * 100, 1),
                "margin": game['team_score'] - game['opp_score']
            })
        
        return {
            "success": True,
            "data": {
                "team_id": team_id,
                "season": season_id,
                "games": result,
                "total_games": len(result),
                "wins": sum(1 for g in result if g["result"] == "W"),
                "losses": sum(1 for g in result if g["result"] == "L"),
                "win_rate": round(sum(1 for g in result if g["result"] == "W") / len(result) * 100, 1) if len(result) > 0 else 0,
                "avg_points": round(sum(g["team_score"] for g in result) / len(result), 1) if len(result) > 0 else 0,
                "avg_opp_points": round(sum(g["opp_score"] for g in result) / len(result), 1) if len(result) > 0 else 0
            }
        }
    finally:
        if conn:
            conn.close()

@router.get("/teams/{team_id}/best_games")
def get_team_best_games(team_id: str, limit: int = 10):
    """获取球队最佳比赛记录"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT game_date, season, team_score, opp_score, fg_pct, ft_pct
            FROM historical_games 
            WHERE team_abbr = %s AND team_score > opp_score
            ORDER BY (team_score - opp_score) DESC
            LIMIT %s
        """
        cursor.execute(query, (team_id, limit))
        games = cursor.fetchall()
        
        if games:
            result = []
            for game_date, season, team_score, opp_score, fg_pct, ft_pct in games:
                result.append({
                    "game_date": game_date.strftime("%Y-%m-%d") if game_date else "",
                    "season": season,
                    "team_score": team_score,
                    "opp_score": opp_score,
                    "margin": team_score - opp_score,
                    "fg_pct": round(fg_pct * 100, 1),
                    "ft_pct": round(ft_pct * 100, 1)
                })
            
            return {
                "success": True,
                "data": result
            }
        else:
            raise Exception("No data from database")
    
    except Exception as e:
        print(f"Database query failed, using CSV backup: {e}")
        all_games = get_spurs_history_from_csv()
        wins = [g for g in all_games if g['team_score'] > g['opp_score']]
        wins.sort(key=lambda x: (x['team_score'] - x['opp_score']), reverse=True)
        top_wins = wins[:limit]
        
        result = []
        for game in top_wins:
            result.append({
                "game_date": game['game_date'],
                "season": game['season'],
                "team_score": game['team_score'],
                "opp_score": game['opp_score'],
                "margin": game['team_score'] - game['opp_score'],
                "fg_pct": round(game['fg_pct'] * 100, 1),
                "ft_pct": round(game['ft_pct'] * 100, 1)
            })
        
        return {
            "success": True,
            "data": result
        }
    finally:
        if conn:
            conn.close()

@router.get("/teams/{team_id}/worst_games")
def get_team_worst_games(team_id: str, limit: int = 10):
    """获取球队最差比赛记录"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT game_date, season, team_score, opp_score, fg_pct, ft_pct
            FROM historical_games 
            WHERE team_abbr = %s AND team_score < opp_score
            ORDER BY (opp_score - team_score) DESC
            LIMIT %s
        """
        cursor.execute(query, (team_id, limit))
        games = cursor.fetchall()
        
        if games:
            result = []
            for game_date, season, team_score, opp_score, fg_pct, ft_pct in games:
                result.append({
                    "game_date": game_date.strftime("%Y-%m-%d") if game_date else "",
                    "season": season,
                    "team_score": team_score,
                    "opp_score": opp_score,
                    "margin": team_score - opp_score,
                    "fg_pct": round(fg_pct * 100, 1),
                    "ft_pct": round(ft_pct * 100, 1)
                })
            
            return {
                "success": True,
                "data": result
            }
        else:
            raise Exception("No data from database")
    
    except Exception as e:
        print(f"Database query failed, using CSV backup: {e}")
        all_games = get_spurs_history_from_csv()
        losses = [g for g in all_games if g['team_score'] < g['opp_score']]
        losses.sort(key=lambda x: (x['opp_score'] - x['team_score']), reverse=True)
        top_losses = losses[:limit]
        
        result = []
        for game in top_losses:
            result.append({
                "game_date": game['game_date'],
                "season": game['season'],
                "team_score": game['team_score'],
                "opp_score": game['opp_score'],
                "margin": game['team_score'] - game['opp_score'],
                "fg_pct": round(game['fg_pct'] * 100, 1),
                "ft_pct": round(game['ft_pct'] * 100, 1)
            })
        
        return {
            "success": True,
            "data": result
        }
    finally:
        if conn:
            conn.close()

@router.get("/teams/{team_id}/home_away_stats")
def get_home_away_stats(team_id: str):
    """获取球队主客场战绩统计"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                SUM(CASE WHEN team_score > opp_score THEN 1 ELSE 0 END) as home_wins,
                SUM(CASE WHEN team_score < opp_score THEN 1 ELSE 0 END) as home_losses,
                AVG(team_score) as home_avg_points,
                AVG(opp_score) as home_avg_opp_points
            FROM historical_games 
            WHERE team_abbr = %s
            UNION ALL
            SELECT 
                SUM(CASE WHEN team_score > opp_score THEN 1 ELSE 0 END) as away_wins,
                SUM(CASE WHEN team_score < opp_score THEN 1 ELSE 0 END) as away_losses,
                AVG(team_score) as away_avg_points,
                AVG(opp_score) as away_avg_opp_points
            FROM historical_games 
            WHERE team_abbr = %s
        """
        cursor.execute(query, (team_id, team_id))
        results = cursor.fetchall()
        
        if len(results) >= 2:
            home_wins, home_losses, home_avg_points, home_avg_opp_points = results[0]
            away_wins, away_losses, away_avg_points, away_avg_opp_points = results[1]
            
            return {
                "success": True,
                "data": {
                    "home": {
                        "wins": home_wins,
                        "losses": home_losses,
                        "total": home_wins + home_losses,
                        "win_rate": round(home_wins / (home_wins + home_losses) * 100, 1) if (home_wins + home_losses) > 0 else 0,
                        "avg_points": round(home_avg_points, 1),
                        "avg_opp_points": round(home_avg_opp_points, 1)
                    },
                    "away": {
                        "wins": away_wins,
                        "losses": away_losses,
                        "total": away_wins + away_losses,
                        "win_rate": round(away_wins / (away_wins + away_losses) * 100, 1) if (away_wins + away_losses) > 0 else 0,
                        "avg_points": round(away_avg_points, 1),
                        "avg_opp_points": round(away_avg_opp_points, 1)
                    }
                }
            }
        else:
            raise Exception("No data from database")
    
    except Exception as e:
        print(f"Database query failed, using CSV backup: {e}")
        all_games = get_spurs_history_from_csv()
        
        home_games = []
        away_games = []
        
        for game in all_games:
            if game['opp'].startswith('@'):
                away_games.append(game)
            else:
                home_games.append(game)
        
        home_wins = sum(1 for g in home_games if g['team_score'] > g['opp_score'])
        home_losses = len(home_games) - home_wins
        home_avg_points = round(sum(g['team_score'] for g in home_games) / len(home_games), 1) if home_games else 0
        home_avg_opp_points = round(sum(g['opp_score'] for g in home_games) / len(home_games), 1) if home_games else 0
        
        away_wins = sum(1 for g in away_games if g['team_score'] > g['opp_score'])
        away_losses = len(away_games) - away_wins
        away_avg_points = round(sum(g['team_score'] for g in away_games) / len(away_games), 1) if away_games else 0
        away_avg_opp_points = round(sum(g['opp_score'] for g in away_games) / len(away_games), 1) if away_games else 0
        
        return {
            "success": True,
            "data": {
                "home": {
                    "wins": home_wins,
                    "losses": home_losses,
                    "total": home_wins + home_losses,
                    "win_rate": round(home_wins / (home_wins + home_losses) * 100, 1) if (home_wins + home_losses) > 0 else 0,
                    "avg_points": home_avg_points,
                    "avg_opp_points": home_avg_opp_points
                },
                "away": {
                    "wins": away_wins,
                    "losses": away_losses,
                    "total": away_wins + away_losses,
                    "win_rate": round(away_wins / (away_wins + away_losses) * 100, 1) if (away_wins + away_losses) > 0 else 0,
                    "avg_points": away_avg_points,
                    "avg_opp_points": away_avg_opp_points
                }
            }
        }
    finally:
        if conn:
            conn.close()

@router.get("/teams/{team_id}/season_chart/{season_id}")
def get_team_season_chart(team_id: str, season_id: str):
    """获取球队特定赛季的图表数据，包括比赛和交易信息"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 转换赛季格式（"2025-26" -> "2025-2026"）
        db_season_id = season_id
        if '-' in season_id and len(season_id) == 7:
            parts = season_id.split('-')
            db_season_id = f"{parts[0]}-{int(parts[1]) + 2000}"
        
        # 获取赛季比赛数据 - 使用team_id而不是team_abbr
        query = """
            SELECT game_date, team_score, opp_score, opp_team_name, game_type
            FROM team_games 
            WHERE team_id = %s AND season_id = %s
            ORDER BY game_date
        """
        cursor.execute(query, (team_id, db_season_id))
        games = cursor.fetchall()
        
        # 获取赛季交易数据（从transactions表或使用模拟数据）
        transactions = []
        try:
            cursor.execute("""
                SELECT date, description, type 
                FROM transactions 
                WHERE team_id = %s 
                AND date BETWEEN %s AND %s
                ORDER BY date
            """, (team_id, f"{season_id[:4]}-10-01", f"{season_id[5:9]}-06-30"))
            transactions = cursor.fetchall()
        except:
            # 如果没有交易表，使用模拟交易数据
            transactions = []
        
        # 处理比赛数据
        game_data = []
        for game_date, team_score, opp_score, opp_team, game_type in games:
            is_win = team_score > opp_score
            # 判断是否是特殊比赛（附加赛或季后赛）
            is_special = game_type in ['playin', 'playoff']
            game_data.append({
                "game_date": game_date.strftime("%Y-%m-%d") if game_date else "",
                "team_score": team_score,
                "opp_score": opp_score,
                "opp_team": opp_team,
                "is_win": is_win,
                "game_type": game_type if game_type else "regular",
                "is_special": is_special,
                "display_score": team_score if is_win else -team_score,
                "month": game_date.month if game_date else 1
            })
        
        # 处理交易数据
        transaction_data = []
        for date, description, tx_type in transactions:
            transaction_data.append({
                "date": date.strftime("%Y-%m-%d") if date else "",
                "description": description,
                "type": tx_type or "交易"
            })
        
        # 如果数据库没有数据，使用CSV后备
        if not game_data:
            all_games = get_spurs_history_from_csv()
            # 尝试匹配赛季格式
            target_season = season_id
            if '-' in season_id and len(season_id) == 7:
                parts = season_id.split('-')
                target_season = f"{parts[0]}-{parts[1][-2:]}"
            
            season_games = [g for g in all_games if g['season'] == target_season or g['season'] == season_id]
            
            for game in season_games:
                is_win = game['team_score'] > game['opp_score']
                game_date = game['game_date']
                month = int(game_date.split('-')[1])
                game_data.append({
                    "game_date": game_date,
                    "team_score": game['team_score'],
                    "opp_score": game['opp_score'],
                    "opp_team": game['opp'],
                    "is_win": is_win,
                    "display_score": game['team_score'] if is_win else -game['team_score'],
                    "month": month
                })
            
            # 添加模拟交易数据
            if team_id == 'SAS' and (season_id == '2023-24' or season_id == '2023-2024'):
                transaction_data = [
                    {"date": "2023-10-15", "description": "签下Victor Wembanyama", "type": "选秀/签约"},
                    {"date": "2023-12-20", "description": "与其他球队的交易", "type": "交易"}
                ]
        
        return {
            "success": True,
            "data": {
                "team_id": team_id,
                "season": season_id,
                "games": game_data,
                "transactions": transaction_data
            }
        }
    except Exception as e:
        print(f"Error getting season chart data: {e}")
        return {
            "success": True,
            "data": {
                "team_id": team_id,
                "season": season_id,
                "games": [],
                "transactions": []
            }
        }
    finally:
        if conn:
            conn.close()

@router.get("/teams/all")
def get_all_teams():
    """获取所有球队列表"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT team_id, team_name, team_abbr, conference, conference_cn
            FROM teams 
            ORDER BY conference, team_name
        """
        cursor.execute(query)
        teams = cursor.fetchall()
        
        if teams:
            result = []
            for team_id, team_name, team_abbr, conference, conference_cn in teams:
                result.append({
                    "team_id": team_id,
                    "team_name": team_name,
                    "team_abbr": team_abbr,
                    "conference": conference,
                    "conference_cn": conference_cn
                })
            
            return {
                "success": True,
                "data": result
            }
        else:
            raise Exception("No data from database")
    
    except Exception as e:
        print(f"Database query failed, using default teams: {e}")
        default_teams = [
            {"team_id": "SAS", "team_name": "圣安东尼奥马刺", "team_abbr": "SAS", "conference": "Western", "conference_cn": "西部"},
            {"team_id": "LAL", "team_name": "洛杉矶湖人", "team_abbr": "LAL", "conference": "Western", "conference_cn": "西部"},
            {"team_id": "HOU", "team_name": "休斯顿火箭", "team_abbr": "HOU", "conference": "Western", "conference_cn": "西部"},
            {"team_id": "GSW", "team_name": "金州勇士", "team_abbr": "GSW", "conference": "Western", "conference_cn": "西部"},
            {"team_id": "DAL", "team_name": "达拉斯独行侠", "team_abbr": "DAL", "conference": "Western", "conference_cn": "西部"},
            {"team_id": "PHO", "team_name": "菲尼克斯太阳", "team_abbr": "PHO", "conference": "Western", "conference_cn": "西部"},
            {"team_id": "DEN", "team_name": "丹佛掘金", "team_abbr": "DEN", "conference": "Western", "conference_cn": "西部"},
            {"team_id": "MEM", "team_name": "孟菲斯灰熊", "team_abbr": "MEM", "conference": "Western", "conference_cn": "西部"},
            {"team_id": "LAC", "team_name": "洛杉矶快船", "team_abbr": "LAC", "conference": "Western", "conference_cn": "西部"},
            {"team_id": "UTA", "team_name": "犹他爵士", "team_abbr": "UTA", "conference": "Western", "conference_cn": "西部"},
            {"team_id": "POR", "team_name": "波特兰开拓者", "team_abbr": "POR", "conference": "Western", "conference_cn": "西部"},
            {"team_id": "OKC", "team_name": "俄克拉荷马雷霆", "team_abbr": "OKC", "conference": "Western", "conference_cn": "西部"},
            {"team_id": "MIN", "team_name": "明尼苏达森林狼", "team_abbr": "MIN", "conference": "Western", "conference_cn": "西部"},
            {"team_id": "SAC", "team_name": "萨克拉门托国王", "team_abbr": "SAC", "conference": "Western", "conference_cn": "西部"},
            {"team_id": "NOP", "team_name": "新奥尔良鹈鹕", "team_abbr": "NOP", "conference": "Western", "conference_cn": "西部"},
            {"team_id": "MIL", "team_name": "密尔沃基雄鹿", "team_abbr": "MIL", "conference": "Eastern", "conference_cn": "东部"},
            {"team_id": "BOS", "team_name": "波士顿凯尔特人", "team_abbr": "BOS", "conference": "Eastern", "conference_cn": "东部"},
            {"team_id": "PHI", "team_name": "费城76人", "team_abbr": "PHI", "conference": "Eastern", "conference_cn": "东部"},
            {"team_id": "MIA", "team_name": "迈阿密热火", "team_abbr": "MIA", "conference": "Eastern", "conference_cn": "东部"},
            {"team_id": "NYK", "team_name": "纽约尼克斯", "team_abbr": "NYK", "conference": "Eastern", "conference_cn": "东部"},
            {"team_id": "CHI", "team_name": "芝加哥公牛", "team_abbr": "CHI", "conference": "Eastern", "conference_cn": "东部"},
            {"team_id": "CLE", "team_name": "克利夫兰骑士", "team_abbr": "CLE", "conference": "Eastern", "conference_cn": "东部"},
            {"team_id": "TOR", "team_name": "多伦多猛龙", "team_abbr": "TOR", "conference": "Eastern", "conference_cn": "东部"},
            {"team_id": "IND", "team_name": "印第安纳步行者", "team_abbr": "IND", "conference": "Eastern", "conference_cn": "东部"},
            {"team_id": "WAS", "team_name": "华盛顿奇才", "team_abbr": "WAS", "conference": "Eastern", "conference_cn": "东部"},
            {"team_id": "BKN", "team_name": "布鲁克林篮网", "team_abbr": "BKN", "conference": "Eastern", "conference_cn": "东部"},
            {"team_id": "ATL", "team_name": "亚特兰大老鹰", "team_abbr": "ATL", "conference": "Eastern", "conference_cn": "东部"},
            {"team_id": "DET", "team_name": "底特律活塞", "team_abbr": "DET", "conference": "Eastern", "conference_cn": "东部"},
            {"team_id": "CHA", "team_name": "夏洛特黄蜂", "team_abbr": "CHA", "conference": "Eastern", "conference_cn": "东部"},
            {"team_id": "ORL", "team_name": "奥兰多魔术", "team_abbr": "ORL", "conference": "Eastern", "conference_cn": "东部"}
        ]
        
        return {
            "success": True,
            "data": default_teams
        }
    finally:
        if conn:
            conn.close()