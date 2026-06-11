from fastapi import APIRouter
import psycopg2
import os

router = APIRouter(prefix="/api", tags=["马刺季后赛数据"])

DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'nba'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5433')
}

@router.get("/spurs/playoffs/2026")
def get_spurs_playoffs_2026():
    """获取马刺2026季后赛所有比赛数据"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                game_rank, game_number, game_date, is_away, opponent, result,
                team_score, opp_score, overtime,
                FG, FGA, FG_pct, threeP, threePA, threeP_pct,
                twoP, twoPA, twoP_pct, eFG_pct,
                FT, FTA, FT_pct,
                ORB, DRB, TRB, AST, STL, BLK, TOV, PF,
                opp_FG, opp_FGA, opp_FG_pct, opp_threeP, opp_threePA, opp_threeP_pct,
                opp_twoP, opp_twoPA, opp_twoP_pct, opp_eFG_pct,
                opp_FT, opp_FTA, opp_FT_pct,
                opp_ORB, opp_DRB, opp_TRB, opp_AST, opp_STL, opp_BLK, opp_TOV, opp_PF
            FROM spurs_playoffs_games_2026
            ORDER BY game_date
        """)
        
        columns = [
            'game_rank', 'game_number', 'game_date', 'is_away', 'opponent', 'result',
            'team_score', 'opp_score', 'overtime',
            'FG', 'FGA', 'FG_pct', 'threeP', 'threePA', 'threeP_pct',
            'twoP', 'twoPA', 'twoP_pct', 'eFG_pct',
            'FT', 'FTA', 'FT_pct',
            'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF',
            'opp_FG', 'opp_FGA', 'opp_FG_pct', 'opp_threeP', 'opp_threePA', 'opp_threeP_pct',
            'opp_twoP', 'opp_twoPA', 'opp_twoP_pct', 'opp_eFG_pct',
            'opp_FT', 'opp_FTA', 'opp_FT_pct',
            'opp_ORB', 'opp_DRB', 'opp_TRB', 'opp_AST', 'opp_STL', 'opp_BLK', 'opp_TOV', 'opp_PF'
        ]
        
        games = []
        for row in cursor.fetchall():
            game = dict(zip(columns, row))
            game['game_date'] = str(game['game_date'])
            games.append(game)
        
        # 计算赛季统计
        total_wins = sum(1 for g in games if g['result'] == 'W')
        total_losses = sum(1 for g in games if g['result'] == 'L')
        
        total_points = sum(g['team_score'] for g in games)
        total_opp_points = sum(g['opp_score'] for g in games)
        
        avg_points = round(total_points / len(games), 1) if games else 0
        avg_opp_points = round(total_opp_points / len(games), 1) if games else 0
        
        conn.close()
        
        return {
            "success": True,
            "data": {
                "season": "2025-26",
                "playoffs": "2026",
                "team": "SAS",
                "team_name": "圣安东尼奥马刺",
                "total_games": len(games),
                "wins": total_wins,
                "losses": total_losses,
                "avg_points": avg_points,
                "avg_opp_points": avg_opp_points,
                "games": games
            }
        }
    
    except Exception as e:
        print(f"Error fetching Spurs playoffs data: {e}")
        if conn:
            conn.close()
        return {"success": False, "message": str(e)}

@router.get("/spurs/playoffs/2026/advanced")
def get_spurs_playoffs_advanced():
    """获取马刺2026季后赛高级数据"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                game_rank, game_number, game_date, is_away, opponent, result,
                team_score, opp_score, overtime,
                ORtg, DRtg, Pace, FTr, threePAr, TS_pct, TRB_pct, AST_pct,
                STL_pct, BLK_pct, eFG_pct_off, TOV_pct_off, ORB_pct_off, FT_FGA_off,
                eFG_pct_def, TOV_pct_def, ORB_pct_def, FT_FGA_def
            FROM spurs_playoffs_advanced_2026
            ORDER BY game_date
        """)
        
        columns = [
            'game_rank', 'game_number', 'game_date', 'is_away', 'opponent', 'result',
            'team_score', 'opp_score', 'overtime',
            'ORtg', 'DRtg', 'Pace', 'FTr', 'threePAr', 'TS_pct', 'TRB_pct', 'AST_pct',
            'STL_pct', 'BLK_pct', 'eFG_pct_off', 'TOV_pct_off', 'ORB_pct_off', 'FT_FGA_off',
            'eFG_pct_def', 'TOV_pct_def', 'ORB_pct_def', 'FT_FGA_def'
        ]
        
        games = []
        for row in cursor.fetchall():
            game = dict(zip(columns, row))
            game['game_date'] = str(game['game_date'])
            # 转换数值为浮点数
            for key in game:
                if key not in ['game_rank', 'game_number', 'is_away', 'opponent', 'result', 'team_score', 'opp_score', 'overtime', 'game_date']:
                    if game[key] is not None:
                        game[key] = float(game[key])
            games.append(game)
        
        # 计算平均值
        if games:
            avg_stats = {
                'avg_ORtg': round(sum(g['ORtg'] for g in games if g['ORtg']) / len(games), 1),
                'avg_DRtg': round(sum(g['DRtg'] for g in games if g['DRtg']) / len(games), 1),
                'avg_Pace': round(sum(g['Pace'] for g in games if g['Pace']) / len(games), 1),
                'avg_TS_pct': round(sum(g['TS_pct'] for g in games if g['TS_pct']) / len(games) * 100, 1),
                'avg_eFG_pct_off': round(sum(g['eFG_pct_off'] for g in games if g['eFG_pct_off']) / len(games) * 100, 1)
            }
        else:
            avg_stats = {}
        
        conn.close()
        
        return {
            "success": True,
            "data": {
                "season": "2025-26",
                "playoffs": "2026",
                "team": "SAS",
                "team_name": "圣安东尼奥马刺",
                "total_games": len(games),
                "games": games,
                "averages": avg_stats
            }
        }
    
    except Exception as e:
        print(f"Error fetching Spurs advanced data: {e}")
        if conn:
            conn.close()
        return {"success": False, "message": str(e)}

@router.get("/spurs/playoffs/2026/summary")
def get_spurs_playoffs_summary():
    """获取马刺2026季后赛摘要统计"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 获取所有比赛数据
        cursor.execute("""
            SELECT * FROM spurs_playoffs_games_2026 ORDER BY game_date
        """)
        games = cursor.fetchall()
        
        # 获取高级数据
        cursor.execute("""
            SELECT * FROM spurs_playoffs_advanced_2026 ORDER BY game_date
        """)
        advanced_games = cursor.fetchall()
        
        conn.close()
        
        if not games:
            return {
                "success": True,
                "data": {
                    "message": "暂无数据"
                }
            }
        
        # 计算基础统计
        total_games = len(games)
        wins = sum(1 for g in games if g[5] == 'W')
        losses = total_games - wins
        
        total_pts = sum(g[6] or 0 for g in games)
        total_opp_pts = sum(g[7] or 0 for g in games)
        
        # 按对手分组统计
        opponents = {}
        for g in games:
            opp = g[4]
            if opp not in opponents:
                opponents[opp] = {'games': 0, 'wins': 0, 'losses': 0, 'pts': 0, 'opp_pts': 0}
            opponents[opp]['games'] += 1
            opponents[opp]['pts'] += g[6] or 0
            opponents[opp]['opp_pts'] += g[7] or 0
            if g[5] == 'W':
                opponents[opp]['wins'] += 1
            else:
                opponents[opp]['losses'] += 1
        
        return {
            "success": True,
            "data": {
                "season": "2025-26",
                "playoffs": "2026",
                "team": "SAS",
                "team_name": "圣安东尼奥马刺",
                "summary": {
                    "total_games": total_games,
                    "wins": wins,
                    "losses": losses,
                    "win_rate": round(wins / total_games * 100, 1) if total_games > 0 else 0,
                    "total_points": total_pts,
                    "total_opp_points": total_opp_pts,
                    "avg_points": round(total_pts / total_games, 1),
                    "avg_opp_points": round(total_opp_pts / total_games, 1)
                },
                "by_opponent": opponents
            }
        }
    
    except Exception as e:
        print(f"Error fetching Spurs summary: {e}")
        if conn:
            conn.close()
        return {"success": False, "message": str(e)}
