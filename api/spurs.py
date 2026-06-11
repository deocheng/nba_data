from fastapi import APIRouter, HTTPException
import psycopg2
import os
import csv
import io
import re

router = APIRouter(prefix="/api", tags=["马刺队"])

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

def convert_height_to_cm(height_str):
    """将英制身高转换为厘米"""
    if not height_str:
        return ""

    # 格式: "6-11" 或 "6'11"" 等
    match = re.match(r"(\d+)-(\d+)", height_str)
    if match:
        feet = int(match.group(1))
        inches = int(match.group(2))
        total_inches = feet * 12 + inches
        cm = total_inches * 2.54
        return f"{cm:.0f} cm"

    return height_str

def convert_weight_to_kg(weight_str):
    """将英制体重转换为公斤"""
    if not weight_str:
        return ""

    try:
        pounds = float(weight_str)
        kg = pounds * 0.453592
        return f"{kg:.0f} kg"
    except:
        return weight_str

def name_to_player_id(name):
    """将球员名字转换为ID"""
    if not name:
        return ""

    # 特殊球员映射
    special_names = {
        "Victor Wembanyama": "wembanyama",
        "Jeremy Sochan": "jeremy_sochan",
        "Devin Vassell": "devin_vassell",
        "Keldon Johnson": "keldon_johnson",
        "Zach Collins": "zach_collins",
        "Malaki Branham": "malaki_branham",
        "Blake Wesley": "blake_wesley",
        "Julian Champagnie": "julian_champagnie",
        "Dominick Barlow": "dominick_barlow",
        "Sidy Cissoko": "sidy_cissoko",
        "Dylan Harper": "sas_dylan_harper",
        "Stephon Castle": "sas_stephon_castle"
    }

    if name in special_names:
        return special_names[name]

    # 通用转换
    return name.lower().replace(" ", "_").replace("'", "")

def parse_csv_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    header_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith('Rk,Gtm,Date'):
            header_idx = i
            break

    if header_idx is None:
        return []

    content = ''.join(lines[header_idx:])
    reader = csv.reader(io.StringIO(content))
    headers = next(reader)

    games = []
    for row in reader:
        if len(row) < 8:
            continue

        game_date = row[2].strip() if len(row) > 2 else ''
        if not game_date:
            continue

        team_score = row[6].strip() if len(row) > 6 else ''
        opp_score = row[7].strip() if len(row) > 7 else ''

        if not team_score.isdigit() or not opp_score.isdigit():
            continue

        game = {
            'Rk': row[0].strip() if len(row) > 0 else '',
            'Date': game_date,
            'Opp': row[4].strip() if len(row) > 4 else '',
            'Rslt': row[5].strip() if len(row) > 5 else '',
            'Tm': team_score,
            'Opp_1': opp_score,
            'OT': row[8].strip() if len(row) > 8 else '',
            'FG': row[9].strip() if len(row) > 9 else '',
            'FGA': row[10].strip() if len(row) > 10 else '',
            'FG%': row[11].strip() if len(row) > 11 else '',
            '3P': row[12].strip() if len(row) > 12 else '',
            '3PA': row[13].strip() if len(row) > 13 else '',
            '3P%': row[14].strip() if len(row) > 14 else '',
            'FT': row[19].strip() if len(row) > 19 else '',
            'FTA': row[20].strip() if len(row) > 20 else '',
            'FT%': row[21].strip() if len(row) > 21 else '',
            'ORB': row[22].strip() if len(row) > 22 else '',
            'DRB': row[23].strip() if len(row) > 23 else '',
            'TRB': row[24].strip() if len(row) > 24 else '',
            'AST': row[25].strip() if len(row) > 25 else '',
            'STL': row[26].strip() if len(row) > 26 else '',
            'BLK': row[27].strip() if len(row) > 27 else '',
            'TOV': row[28].strip() if len(row) > 28 else '',
            'PF': row[29].strip() if len(row) > 29 else ''
        }
        games.append(game)

    return games

@router.get("/spurs/roster")
def get_spurs_roster():
    roster_file = os.path.join(CSV_DIR, "2025-2026SAS_roster.csv")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        roster = []
        with open(roster_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

            header_line = None
            for i, line in enumerate(lines):
                if line.strip().startswith('No.,Player,Pos'):
                    header_line = i
                    break

            if header_line is None:
                conn.close()
                return {"success": True, "data": roster}

            content = ''.join(lines[header_line:])
            reader = csv.DictReader(io.StringIO(content))
            for row in reader:
                name = row.get("Player", "").replace("  (TW)", "")
                player_id = name_to_player_id(name)

                # 从数据库获取球员详细信息 - 改进匹配逻辑
                nickname = None
                body_info = None
                avatar_url = None

                try:
                    # 尝试多种匹配方式
                    match_queries = [
                        "SELECT nickname, body_info, avatar_url FROM players WHERE name = %s",
                        "SELECT nickname, body_info, avatar_url FROM players WHERE name ILIKE %s",
                    ]
                    
                    search_terms = [name, f"%{name.split()[-1]}%"]
                    
                    player_row = None
                    for query, term in zip(match_queries, search_terms):
                        cursor.execute(query, (term,))
                        player_row = cursor.fetchone()
                        if player_row and player_row[2]:  # 优先找到有头像的
                            break
                    
                    if player_row:
                        nickname = player_row[0]
                        body_info = player_row[1]
                        avatar_url = player_row[2]
                except Exception as e:
                    print(f"查询球员信息失败: {e}")
                    pass

                roster.append({
                    "number": row.get("No.", ""),
                    "name": name,
                    "player_id": player_id,
                    "position": row.get("Pos", ""),
                    "height": convert_height_to_cm(row.get("Ht", "")),
                    "weight": convert_weight_to_kg(row.get("Wt", "")),
                    "birth_date": row.get("Birth Date", ""),
                    "birth_place": row.get("Birth", ""),
                    "experience": row.get("Exp", "").replace("R", "新秀"),
                    "college": row.get("College", ""),
                    "nickname": nickname,
                    "body_info": body_info,
                    "avatar_url": avatar_url
                })

        conn.close()
        return {"success": True, "data": roster}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/spurs/season/{season}")
def get_spurs_season(season: str = "2023-2024"):
    # 将短格式转换为数据库格式
    if len(season) == 7:  # 2025-26
        season_db = season[:4] + "-" + str(int(season[5:7]) + 2000)
    else:  # 2025-2026
        season_db = season

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 直接从team_games表获取数据（包含完整的比赛类型信息）
        query = """
            SELECT game_date, team_score, opp_score, opp_team_abbr, game_type, is_playoff
            FROM team_games
            WHERE team_id = 'SAS'
              AND season_id = %s
            ORDER BY game_date
        """
        cursor.execute(query, (season_db,))
        rows = cursor.fetchall()

        if rows:
            games = []
            game_number = 1
            for row in rows:
                game_type = row[4] if row[4] else 'regular'
                is_playoff = row[5] if row[5] else False
                is_special = game_type in ['playin', 'playoff']

                games.append({
                    "game_number": str(game_number),
                    "game_date": row[0].strftime('%Y-%m-%d') if row[0] else "",
                    "opponent": row[3] or "",
                    "team_score": str(row[1]) if row[1] else "",
                    "opp_score": str(row[2]) if row[2] else "",
                    "game_type": game_type,
                    "is_playoff": is_playoff,
                    "is_special": is_special
                })
                game_number += 1

            return {"success": True, "data": {"season": season, "games": games}}

        # 如果team_games没有数据，尝试从historical_games表获取
        query = """
            SELECT game_date, team_score, opp_score
            FROM historical_games
            WHERE team_abbr = 'SAS'
              AND season = %s
            ORDER BY game_date
        """
        cursor.execute(query, (season_db,))
        rows = cursor.fetchall()

        if rows:
            games = []
            game_number = 1
            for row in rows:
                games.append({
                    "game_number": str(game_number),
                    "game_date": row[0].strftime('%Y-%m-%d') if row[0] else "",
                    "opponent": "",
                    "team_score": str(row[1]) if row[1] else "",
                    "opp_score": str(row[2]) if row[2] else "",
                    "game_type": "regular",
                    "is_playoff": False,
                    "is_special": False
                })
                game_number += 1

            return {"success": True, "data": {"season": season, "games": games}}

        # 如果都没有数据，尝试从CSV文件读取（兼容旧数据）
        season_files = {
            "2023-2024": "2023-2024spurs.csv",
            "2024-2025": "2024-2025spurs.csv",
            "2025-2026": "2025-2026spurs.csv"
        }

        if season in season_files:
            file_path = os.path.join(CSV_DIR, season_files[season])
            games_data = parse_csv_file(file_path)

            games = []
            for game_data in games_data:
                games.append({
                    "game_number": game_data.get("Rk", ""),
                    "game_date": game_data.get("Date", ""),
                    "opponent": game_data.get("Opp", ""),
                    "result": game_data.get("Rslt", ""),
                    "team_score": game_data.get("Tm", ""),
                    "opp_score": game_data.get("Opp_1", ""),
                    "game_type": "regular",
                    "is_playoff": False,
                    "is_special": False
                })

            return {"success": True, "data": {"season": season, "games": games}}

        raise HTTPException(status_code=404, detail="未找到该赛季数据")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting season data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@router.get("/spurs/season_summary/{season}")
def get_spurs_season_summary(season: str = "2023-2024"):
    season_files = {
        "2023-2024": "2023-2024spurs.csv",
        "2024-2025": "2024-2025spurs.csv",
        "2025-2026": "2025-2026spurs.csv"
    }

    if season not in season_files:
        raise HTTPException(status_code=400, detail="无效的赛季")

    file_path = os.path.join(CSV_DIR, season_files[season])

    try:
        games_data = parse_csv_file(file_path)

        wins = 0
        losses = 0
        total_points = 0
        total_opp_points = 0
        total_fg_made = 0
        total_fg_att = 0
        total_three_made = 0
        total_three_att = 0
        total_ft_made = 0
        total_ft_att = 0
        total_rebounds = 0
        total_assists = 0
        total_steals = 0
        total_blocks = 0

        for game in games_data:
            if game.get("Rslt", "").startswith("W"):
                wins += 1
            elif game.get("Rslt", "").startswith("L"):
                losses += 1

            try:
                total_points += int(game.get("Tm", "0") or "0")
                total_opp_points += int(game.get("Opp_1", "0") or "0")
                total_fg_made += int(game.get("FG", "0") or "0")
                total_fg_att += int(game.get("FGA", "0") or "0")
                total_three_made += int(game.get("3P", "0") or "0")
                total_three_att += int(game.get("3PA", "0") or "0")
                total_ft_made += int(game.get("FT", "0") or "0")
                total_ft_att += int(game.get("FTA", "0") or "0")
                total_rebounds += int(game.get("TRB", "0") or "0")
                total_assists += int(game.get("AST", "0") or "0")
                total_steals += int(game.get("STL", "0") or "0")
                total_blocks += int(game.get("BLK", "0") or "0")
            except:
                pass

        total_games = wins + losses

        return {
            "success": True,
            "data": {
                "season": season,
                "total_games": total_games,
                "wins": wins,
                "losses": losses,
                "win_rate": round(wins / total_games * 100, 1) if total_games > 0 else 0,
                "avg_points": round(total_points / total_games, 1) if total_games > 0 else 0,
                "avg_opp_points": round(total_opp_points / total_games, 1) if total_games > 0 else 0,
                "fg_pct": round(total_fg_made / total_fg_att * 100, 1) if total_fg_att > 0 else 0,
                "three_pct": round(total_three_made / total_three_att * 100, 1) if total_three_att > 0 else 0,
                "ft_pct": round(total_ft_made / total_ft_att * 100, 1) if total_ft_att > 0 else 0,
                "avg_rebounds": round(total_rebounds / total_games, 1) if total_games > 0 else 0,
                "avg_assists": round(total_assists / total_games, 1) if total_games > 0 else 0,
                "avg_steals": round(total_steals / total_games, 1) if total_games > 0 else 0,
                "avg_blocks": round(total_blocks / total_games, 1) if total_games > 0 else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/spurs/wembanyama")
def get_wembanyama_data():
    regular_season = {
        "avg_points": 0,
        "avg_rebounds": 0,
        "avg_assists": 0,
        "avg_blocks": 0,
        "avg_steals": 0,
        "games_played": 0
    }
    playoffs = {
        "avg_points": 0,
        "avg_rebounds": 0,
        "avg_assists": 0,
        "avg_blocks": 0,
        "avg_steals": 0,
        "games_played": 0
    }

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT *
            FROM "2025-26_sas_per_game"
            WHERE "Player" LIKE '%Wembanyama%'
        """
        cursor.execute(query)
        row = cursor.fetchone()

        if row:
            regular_season = {
                "avg_points": round(float(row[29]), 1) if row[29] else 0,
                "avg_rebounds": round(float(row[23]), 1) if row[23] else 0,
                "avg_assists": round(float(row[24]), 1) if row[24] else 0,
                "avg_blocks": round(float(row[26]), 1) if row[26] else 0,
                "avg_steals": round(float(row[25]), 1) if row[25] else 0,
                "games_played": int(row[5]) if row[5] else 0
            }

        query = """
            SELECT *
            FROM "2025-26_sas_per_game_playoffs"
            WHERE "Player" LIKE '%Wembanyama%'
        """
        cursor.execute(query)
        row = cursor.fetchone()

        if row:
            playoffs = {
                "avg_points": round(float(row[29]), 1) if row[29] else 0,
                "avg_rebounds": round(float(row[23]), 1) if row[23] else 0,
                "avg_assists": round(float(row[24]), 1) if row[24] else 0,
                "avg_blocks": round(float(row[26]), 1) if row[26] else 0,
                "avg_steals": round(float(row[25]), 1) if row[25] else 0,
                "games_played": int(row[5]) if row[5] else 0
            }
    except Exception as e:
        print(f"查询文班亚马数据失败: {e}")
    finally:
        if conn:
            conn.close()

    return {
        "success": True,
        "data": {
            "player_info": {
                "name": "维克托·文班亚马",
                "english_name": "Victor Wembanyama",
                "position": "C",
                "position_cn": "中锋",
                "height": "224 cm",
                "weight": "107 kg",
                "jersey_number": "1",
                "birth_date": "2004-01-04",
                "draft_year": "2023",
                "draft_pick": "第一轮第1顺位"
            },
            "regular_season": regular_season,
            "playoffs": playoffs,
            "career_highlights": [
                "2023年NBA选秀状元",
                "2023-24赛季年度最佳新秀",
                "2024-25赛季最佳防守球员",
                "连续2次入选全明星"
            ]
        }
    }

@router.get("/spurs/seasons")
def get_spurs_seasons():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT DISTINCT season
            FROM historical_games
            WHERE team_abbr = 'SAS'
            ORDER BY season DESC
        """
        cursor.execute(query)
        seasons = cursor.fetchall()

        if seasons:
            return {
                "success": True,
                "data": [
                    {"season": season[0], "label": f"{season[0][:4]}-{season[0][5:7]}赛季"}
                    for season in seasons
                ]
            }
        else:
            # 如果数据库没有数据，返回默认赛季
            return {
                "success": True,
                "data": [
                    {"season": "2023-2024", "label": "2023-24赛季"},
                    {"season": "2024-2025", "label": "2024-25赛季"},
                    {"season": "2025-2026", "label": "2025-26赛季"}
                ]
            }
    except Exception as e:
        print(f"Error getting seasons: {e}")
        return {
            "success": True,
            "data": [
                {"season": "2023-2024", "label": "2023-24赛季"},
                {"season": "2024-2025", "label": "2024-25赛季"},
                {"season": "2025-2026", "label": "2025-26赛季"}
            ]
        }
    finally:
        if conn:
            conn.close()
