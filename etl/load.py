#!/usr/bin/env python3
"""
ETL模块 - 数据加载
功能：将转换后的数据加载到PostgreSQL数据库
"""

import psycopg2
import os
from psycopg2 import extras

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

def load_teams(teams_data):
    """加载球队数据"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        insert_sql = """
        INSERT INTO teams (
            team_id, team_name, team_name_en, team_abbr,
            conference, conference_cn, division, division_cn,
            city, arena, founded_year
        ) VALUES (
            %(team_id)s, %(team_name)s, %(team_name_en)s, %(team_abbr)s,
            %(conference)s, %(conference_cn)s, %(division)s, %(division_cn)s,
            %(city)s, %(arena)s, %(founded_year)s
        ) ON CONFLICT (team_id) DO UPDATE SET
            team_name = EXCLUDED.team_name,
            team_name_en = EXCLUDED.team_name_en,
            team_abbr = EXCLUDED.team_abbr,
            conference = EXCLUDED.conference,
            conference_cn = EXCLUDED.conference_cn,
            division = EXCLUDED.division,
            division_cn = EXCLUDED.division_cn,
            city = EXCLUDED.city,
            arena = EXCLUDED.arena,
            founded_year = EXCLUDED.founded_year,
            updated_at = CURRENT_TIMESTAMP;
        """
        
        cursor.executemany(insert_sql, teams_data)
        conn.commit()
        print(f"成功加载 {cursor.rowcount} 条球队数据")
        return cursor.rowcount
        
    except Exception as e:
        print(f"加载球队数据失败: {e}")
        if conn:
            conn.rollback()
        return 0
    finally:
        if conn:
            conn.close()

def load_players(players_data):
    """加载球员数据"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        insert_sql = """
        INSERT INTO players (
            player_id, player_name, player_name_en, position, position_cn,
            height, weight, jersey_number, birth_date, birth_place,
            draft_year, draft_pick, retire_year
        ) VALUES (
            %(player_id)s, %(player_name)s, %(player_name_en)s, %(position)s, %(position_cn)s,
            %(height)s, %(weight)s, %(jersey_number)s, %(birth_date)s, %(birth_place)s,
            %(draft_year)s, %(draft_pick)s, %(retire_year)s
        ) ON CONFLICT (player_id) DO UPDATE SET
            player_name = EXCLUDED.player_name,
            player_name_en = EXCLUDED.player_name_en,
            position = EXCLUDED.position,
            position_cn = EXCLUDED.position_cn,
            height = EXCLUDED.height,
            weight = EXCLUDED.weight,
            jersey_number = EXCLUDED.jersey_number,
            birth_date = EXCLUDED.birth_date,
            birth_place = EXCLUDED.birth_place,
            draft_year = EXCLUDED.draft_year,
            draft_pick = EXCLUDED.draft_pick,
            retire_year = EXCLUDED.retire_year,
            updated_at = CURRENT_TIMESTAMP;
        """
        
        cursor.executemany(insert_sql, players_data)
        conn.commit()
        print(f"成功加载 {cursor.rowcount} 条球员数据")
        return cursor.rowcount
        
    except Exception as e:
        print(f"加载球员数据失败: {e}")
        if conn:
            conn.rollback()
        return 0
    finally:
        if conn:
            conn.close()

def load_player_team_seasons(data):
    """加载球员-球队-赛季数据"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        insert_sql = """
        INSERT INTO player_team_seasons (
            player_id, team_id, season_id, games_played, minutes_played,
            points, rebounds, assists, steals, blocks,
            fg_made, fg_att, three_made, three_att, ft_made, ft_att,
            per, ts_pct, usg_pct, ws, ws_per_48, bpm, vorp,
            offensive_rating, defensive_rating, assist_ratio, turnover_ratio, rebound_rate,
            avg_points, avg_rebounds, avg_assists, avg_steals, avg_blocks,
            fg_pct, three_pct, ft_pct
        ) VALUES (
            %(player_id)s, %(team_id)s, %(season_id)s, %(games_played)s, %(minutes_played)s,
            %(points)s, %(rebounds)s, %(assists)s, %(steals)s, %(blocks)s,
            %(fg_made)s, %(fg_att)s, %(three_made)s, %(three_att)s, %(ft_made)s, %(ft_att)s,
            %(per)s, %(ts_pct)s, %(usg_pct)s, %(ws)s, %(ws_per_48)s, %(bpm)s, %(vorp)s,
            %(offensive_rating)s, %(defensive_rating)s, %(assist_ratio)s, %(turnover_ratio)s, %(rebound_rate)s,
            %(avg_points)s, %(avg_rebounds)s, %(avg_assists)s, %(avg_steals)s, %(avg_blocks)s,
            %(fg_pct)s, %(three_pct)s, %(ft_pct)s
        ) ON CONFLICT (player_id, team_id, season_id) DO UPDATE SET
            games_played = EXCLUDED.games_played,
            minutes_played = EXCLUDED.minutes_played,
            points = EXCLUDED.points,
            rebounds = EXCLUDED.rebounds,
            assists = EXCLUDED.assists,
            steals = EXCLUDED.steals,
            blocks = EXCLUDED.blocks,
            fg_made = EXCLUDED.fg_made,
            fg_att = EXCLUDED.fg_att,
            three_made = EXCLUDED.three_made,
            three_att = EXCLUDED.three_att,
            ft_made = EXCLUDED.ft_made,
            ft_att = EXCLUDED.ft_att,
            per = EXCLUDED.per,
            ts_pct = EXCLUDED.ts_pct,
            usg_pct = EXCLUDED.usg_pct,
            ws = EXCLUDED.ws,
            ws_per_48 = EXCLUDED.ws_per_48,
            bpm = EXCLUDED.bpm,
            vorp = EXCLUDED.vorp,
            offensive_rating = EXCLUDED.offensive_rating,
            defensive_rating = EXCLUDED.defensive_rating,
            assist_ratio = EXCLUDED.assist_ratio,
            turnover_ratio = EXCLUDED.turnover_ratio,
            rebound_rate = EXCLUDED.rebound_rate,
            avg_points = EXCLUDED.avg_points,
            avg_rebounds = EXCLUDED.avg_rebounds,
            avg_assists = EXCLUDED.avg_assists,
            avg_steals = EXCLUDED.avg_steals,
            avg_blocks = EXCLUDED.avg_blocks,
            fg_pct = EXCLUDED.fg_pct,
            three_pct = EXCLUDED.three_pct,
            ft_pct = EXCLUDED.ft_pct;
        """
        
        cursor.executemany(insert_sql, data)
        conn.commit()
        print(f"成功加载 {cursor.rowcount} 条球员-球队-赛季数据")
        return cursor.rowcount
        
    except Exception as e:
        print(f"加载球员-球队-赛季数据失败: {e}")
        if conn:
            conn.rollback()
        return 0
    finally:
        if conn:
            conn.close()

def load_team_games(data):
    """加载球队比赛数据"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        insert_sql = """
        INSERT INTO team_games (
            game_id, team_id, season_id, game_date, game_number,
            is_home, opp_team_id, opp_team_abbr, opp_team_name,
            result, team_score, opp_score, ot_flag
        ) VALUES (
            %(game_id)s, %(team_id)s, %(season_id)s, %(game_date)s, %(game_number)s,
            %(is_home)s, %(opp_team_id)s, %(opp_team_abbr)s, %(opp_team_name)s,
            %(result)s, %(team_score)s, %(opp_score)s, %(ot_flag)s
        ) ON CONFLICT (game_id, team_id) DO UPDATE SET
            season_id = EXCLUDED.season_id,
            game_date = EXCLUDED.game_date,
            game_number = EXCLUDED.game_number,
            is_home = EXCLUDED.is_home,
            opp_team_id = EXCLUDED.opp_team_id,
            opp_team_abbr = EXCLUDED.opp_team_abbr,
            opp_team_name = EXCLUDED.opp_team_name,
            result = EXCLUDED.result,
            team_score = EXCLUDED.team_score,
            opp_score = EXCLUDED.opp_score,
            ot_flag = EXCLUDED.ot_flag;
        """
        
        cursor.executemany(insert_sql, data)
        conn.commit()
        print(f"成功加载 {cursor.rowcount} 条球队比赛数据")
        return cursor.rowcount
        
    except Exception as e:
        print(f"加载球队比赛数据失败: {e}")
        if conn:
            conn.rollback()
        return 0
    finally:
        if conn:
            conn.close()

def execute_sql_file(file_path):
    """执行SQL文件"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 逐行处理，忽略注释和空行
        current_statement = ""
        for line in lines:
            # 跳过注释行
            if line.strip().startswith('--'):
                continue
            
            current_statement += line
            
            # 检查是否到达语句结束
            if ';' in current_statement:
                # 分割并执行
                parts = current_statement.split(';')
                for part in parts:
                    part = part.strip()
                    if part:
                        try:
                            cursor.execute(part)
                        except Exception as e:
                            print(f"执行SQL语句失败: {part[:50]}...")
                            raise e
                current_statement = ""
        
        conn.commit()
        print(f"成功执行SQL文件: {file_path}")
        
    except Exception as e:
        print(f"执行SQL文件失败: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # 测试加载功能
    from .extract import extract_teams_detailed, extract_player_stats_2025_26, extract_advanced_stats
    from .transform import transform_teams, transform_player_team_seasons
    
    print("测试数据加载...")
    
    # 先创建表结构
    schema_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "database_schema.sql")
    execute_sql_file(schema_file)
    
    # 加载球队数据
    teams = extract_teams_detailed()
    transformed_teams = transform_teams(teams)
    load_teams(transformed_teams)
    
    # 加载球员赛季数据
    players = extract_player_stats_2025_26()
    advanced = extract_advanced_stats()
    transformed_seasons = transform_player_team_seasons(players, advanced)
    load_player_team_seasons(transformed_seasons)
    
    print("数据加载测试完成!")
