from fastapi import APIRouter, HTTPException, Query
import psycopg2
import os
import csv
import io

router = APIRouter(prefix="/api", tags=["球队对阵"])

DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'nba'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5433')
}

CSV_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "CSV")

def get_connection():
    """获取数据库连接"""
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_client_encoding('UTF8')
    return conn

def get_matchup_from_csv(team1_id, team2_id):
    """从CSV获取两队交锋数据"""
    games = []
    
    filepath = os.path.join(CSV_DIR, "1989-2026SAS.csv")
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if len(lines) >= 3:
            for line in lines[2:]:
                if not line.strip():
                    continue
                row = line.strip().split(',')
                if len(row) < 8:
                    continue
                
                game_date = row[2].strip()
                if not game_date:
                    continue
                
                opp = row[4].strip()
                team_score = row[6].strip()
                opp_score = row[7].strip()
                
                if not team_score.isdigit() or not opp_score.isdigit():
                    continue
                
                is_home = not opp.startswith('@')
                opp_team = opp.replace('@', '').strip()
                
                team1_pts = int(team_score)
                team2_pts = int(opp_score)
                
                if team1_id == 'SAS':
                    if opp_team == team2_id or opp_team == team2_id.lower() or opp_team == team2_id.upper():
                        games.append({
                            "game_date": game_date,
                            "team1_score": team1_pts,
                            "team2_score": team2_pts,
                            "team1_is_home": is_home,
                            "team1_win": team1_pts > team2_pts
                        })
                elif team2_id == 'SAS':
                    if opp_team == team1_id or opp_team == team1_id.lower() or opp_team == team1_id.upper():
                        games.append({
                            "game_date": game_date,
                            "team1_score": team2_pts,
                            "team2_score": team1_pts,
                            "team1_is_home": not is_home,
                            "team1_win": team2_pts > team1_pts
                        })
    
    games.sort(key=lambda x: x['game_date'], reverse=True)
    return games[:20]

def get_team_info(team_id):
    """获取球队信息"""
    teams = {
        "SAS": {"team_name": "圣安东尼奥马刺", "team_abbr": "SAS"},
        "LAL": {"team_name": "洛杉矶湖人", "team_abbr": "LAL"},
        "HOU": {"team_name": "休斯顿火箭", "team_abbr": "HOU"},
        "GSW": {"team_name": "金州勇士", "team_abbr": "GSW"},
        "DAL": {"team_name": "达拉斯独行侠", "team_abbr": "DAL"},
        "PHO": {"team_name": "菲尼克斯太阳", "team_abbr": "PHO"},
        "DEN": {"team_name": "丹佛掘金", "team_abbr": "DEN"},
        "MEM": {"team_name": "孟菲斯灰熊", "team_abbr": "MEM"},
        "LAC": {"team_name": "洛杉矶快船", "team_abbr": "LAC"},
        "UTA": {"team_name": "犹他爵士", "team_abbr": "UTA"},
        "POR": {"team_name": "波特兰开拓者", "team_abbr": "POR"},
        "OKC": {"team_name": "俄克拉荷马雷霆", "team_abbr": "OKC"},
        "MIN": {"team_name": "明尼苏达森林狼", "team_abbr": "MIN"},
        "SAC": {"team_name": "萨克拉门托国王", "team_abbr": "SAC"},
        "NOP": {"team_name": "新奥尔良鹈鹕", "team_abbr": "NOP"},
        "MIL": {"team_name": "密尔沃基雄鹿", "team_abbr": "MIL"},
        "BOS": {"team_name": "波士顿凯尔特人", "team_abbr": "BOS"},
        "PHI": {"team_name": "费城76人", "team_abbr": "PHI"},
        "MIA": {"team_name": "迈阿密热火", "team_abbr": "MIA"},
        "NYK": {"team_name": "纽约尼克斯", "team_abbr": "NYK"},
        "CHI": {"team_name": "芝加哥公牛", "team_abbr": "CHI"},
        "CLE": {"team_name": "克利夫兰骑士", "team_abbr": "CLE"},
        "TOR": {"team_name": "多伦多猛龙", "team_abbr": "TOR"},
        "IND": {"team_name": "印第安纳步行者", "team_abbr": "IND"},
        "WAS": {"team_name": "华盛顿奇才", "team_abbr": "WAS"},
        "BKN": {"team_name": "布鲁克林篮网", "team_abbr": "BKN"},
        "ATL": {"team_name": "亚特兰大老鹰", "team_abbr": "ATL"},
        "DET": {"team_name": "底特律活塞", "team_abbr": "DET"},
        "CHA": {"team_name": "夏洛特黄蜂", "team_abbr": "CHA"},
        "ORL": {"team_name": "奥兰多魔术", "team_abbr": "ORL"}
    }
    return teams.get(team_id, {"team_name": team_id, "team_abbr": team_id})

@router.get("/matchup")
def get_team_matchup(
    team1_id: str = Query(..., description="球队1ID"),
    team2_id: str = Query(..., description="球队2ID"),
    season: str = Query("all", description="赛季")
):
    """获取两队交锋数据"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 获取球队信息
        cursor.execute("SELECT team_abbr, team_name FROM teams WHERE team_abbr = %s", (team1_id,))
        team1_db_info = cursor.fetchone()
        
        cursor.execute("SELECT team_abbr, team_name FROM teams WHERE team_abbr = %s", (team2_id,))
        team2_db_info = cursor.fetchone()
        
        if not team1_db_info or not team2_db_info:
            raise Exception("Team not found")
        
        # 使用team_id和opp_team_name(球队缩写)查询 (更准确，避免数字ID后两位冲突)
        if season == "all":
            query = """
                SELECT game_date, team_id, team_score, opp_score, is_home,
                       trb, ast, stl, blk, tov,
                       opp_trb, opp_ast, opp_stl, opp_blk, opp_tov
                FROM team_games
                WHERE team_id = %s AND opp_team_name = %s
                ORDER BY game_date DESC
            """
            cursor.execute(query, (team1_id, team2_id))
        else:
            query = """
                SELECT game_date, team_id, team_score, opp_score, is_home,
                       trb, ast, stl, blk, tov,
                       opp_trb, opp_ast, opp_stl, opp_blk, opp_tov
                FROM team_games
                WHERE team_id = %s AND opp_team_name = %s
                  AND (season_id = %s OR season_id = %s)
                ORDER BY game_date DESC
            """
            parts = season.split('-')
            alt_season = f"{parts[0]}-20{parts[1]}" if len(parts) == 2 and len(parts[0]) == 4 and len(parts[1]) == 2 else season
            cursor.execute(query, (team1_id, team2_id, season, alt_season))
        
        games = cursor.fetchall()
        
        if not games:
            raise Exception("No data from database")
        
        team1_wins = 0
        team2_wins = 0
        
        game_list = []
        for game in games:
            game_date, record_team_id, team_score, opp_score, is_home, trb, ast, stl, blk, tov, opp_trb, opp_ast, opp_stl, opp_blk, opp_tov = game
            
            team1_pts = team_score
            team2_pts = opp_score
            team1_is_home = is_home
            is_team1_win = team_score > opp_score
            
            if is_team1_win:
                team1_wins += 1
            else:
                team2_wins += 1
            
            game_list.append({
                "game_date": game_date.strftime("%Y-%m-%d") if game_date else "",
                "team1_score": team1_pts,
                "team2_score": team2_pts,
                "team1_is_home": team1_is_home,
                "team1_win": is_team1_win,
                "team1_trb": trb,
                "team1_ast": ast,
                "team1_stl": stl,
                "team1_blk": blk,
                "team1_tov": tov,
                "team2_trb": opp_trb,
                "team2_ast": opp_ast,
                "team2_stl": opp_stl,
                "team2_blk": opp_blk,
                "team2_tov": opp_tov
            })
        
        team1_info = get_team_info(team1_id)
        team2_info = get_team_info(team2_id)
        
        return {
            "success": True,
            "data": {
                "team1": {
                    "team_id": team1_id,
                    "team_name": team1_info["team_name"],
                    "team_abbr": team1_info["team_abbr"]
                },
                "team2": {
                    "team_id": team2_id,
                    "team_name": team2_info["team_name"],
                    "team_abbr": team2_info["team_abbr"]
                },
                "total_games": len(game_list),
                "team1_wins": team1_wins,
                "team2_wins": team2_wins,
                "season": season,
                "games": game_list
            }
        }
    
    except Exception as e:
        print(f"Database query failed, using CSV backup: {e}")
        games = get_matchup_from_csv(team1_id, team2_id)
        
        team1_info = get_team_info(team1_id)
        team2_info = get_team_info(team2_id)
        
        team1_wins = sum(1 for g in games if g['team1_win'])
        team2_wins = len(games) - team1_wins
        
        return {
            "success": True,
            "data": {
                "team1": {
                    "team_id": team1_id,
                    "team_name": team1_info["team_name"],
                    "team_abbr": team1_info["team_abbr"]
                },
                "team2": {
                    "team_id": team2_id,
                    "team_name": team2_info["team_name"],
                    "team_abbr": team2_info["team_abbr"]
                },
                "total_games": len(games),
                "team1_wins": team1_wins,
                "team2_wins": team2_wins,
                "games": games
            }
        }
    finally:
        if conn:
            conn.close()
