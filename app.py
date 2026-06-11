#!/usr/bin/env python3
"""NBA数据可视化前端展示 - Flask Web应用"""
from flask import Flask, render_template, jsonify, request
import psycopg2
import pandas as pd
import os

app = Flask(__name__)
app.static_folder = 'static'
app.static_url_path = '/static'

DB_CONFIG = {
    'dbname': 'nba',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5433'
}


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


@app.route('/')
def dashboard():
    """仪表盘主页"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 数据统计
    cursor.execute("SELECT COUNT(*) FROM pbp_all;")
    total_events = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT gameid) FROM pbp_all;")
    total_games = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT current_code) FROM team_mapping WHERE is_active = true;")
    total_teams = cursor.fetchone()[0]
    
    cursor.execute("SELECT MIN(season), MAX(season) FROM pbp_all;")
    seasons = cursor.fetchone()
    
    # 赛季分布数据
    cursor.execute("""
        SELECT season, COUNT(DISTINCT gameid) as games
        FROM pbp_all
        GROUP BY season
        ORDER BY season;
    """)
    season_data = cursor.fetchall()
    
    # 事件类型分布
    cursor.execute("""
        SELECT event_type, COUNT(*) as cnt
        FROM pbp_all
        WHERE event_type IS NOT NULL
        GROUP BY event_type
        ORDER BY cnt DESC
        LIMIT 8;
    """)
    event_data = cursor.fetchall()
    
    conn.close()
    
    return render_template('dashboard.html',
                          total_events=total_events,
                          total_games=total_games,
                          total_teams=total_teams,
                          seasons=seasons,
                          season_data=season_data,
                          event_data=event_data)


@app.route('/games')
def games_list():
    """比赛列表页面"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page
    
    cursor.execute("""
        SELECT gameid, season, 
               MAX(h_pts) as home_score, MAX(a_pts) as visitor_score,
               (SELECT team FROM pbp_all WHERE gameid = t.gameid AND team IS NOT NULL LIMIT 1) as home_team,
               (SELECT team FROM pbp_all WHERE gameid = t.gameid AND team IS NOT NULL LIMIT 1 OFFSET 1) as away_team
        FROM pbp_all t
        GROUP BY gameid, season
        ORDER BY season DESC, gameid DESC
        LIMIT %s OFFSET %s;
    """, (per_page, offset))
    
    games = []
    for row in cursor.fetchall():
        games.append({
            'gameid': row[0],
            'season': row[1],
            'home_score': row[2],
            'visitor_score': row[3],
            'home_team': row[4],
            'away_team': row[5]
        })
    
    # 总页数
    cursor.execute("SELECT COUNT(DISTINCT gameid) FROM pbp_all;")
    total_games = cursor.fetchone()[0]
    total_pages = (total_games + per_page - 1) // per_page
    
    conn.close()
    
    return render_template('games.html',
                          games=games,
                          page=page,
                          total_pages=total_pages)


@app.route('/game/<int:game_id>')
def game_detail(game_id):
    """单场比赛详情页面"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 比赛基本信息
    cursor.execute("""
        SELECT DISTINCT team FROM pbp_all 
        WHERE gameid = %s AND team IS NOT NULL;
    """, (game_id,))
    teams = [t[0] for t in cursor.fetchall()]
    
    cursor.execute("""
        SELECT MAX(h_pts), MAX(a_pts), season FROM pbp_all
        WHERE gameid = %s AND h_pts IS NOT NULL;
    """, (game_id,))
    result = cursor.fetchone()
    home_score, visitor_score, season = result
    
    # 得分走势数据
    cursor.execute("""
        SELECT period, clock_seconds, h_pts, a_pts
        FROM pbp_all
        WHERE gameid = %s AND h_pts IS NOT NULL
        ORDER BY period, clock_seconds DESC;
    """, (game_id,))
    score_data = []
    for row in cursor.fetchall():
        period, time, home, away = row
        game_seconds = (period - 1) * 720 + (720 - time)
        score_data.append({
            'time': game_seconds,
            'home': home,
            'away': away
        })
    
    # 事件统计
    cursor.execute("""
        SELECT event_type, COUNT(*) as cnt
        FROM pbp_all
        WHERE gameid = %s AND event_type IS NOT NULL
        GROUP BY event_type
        ORDER BY cnt DESC;
    """, (game_id,))
    event_stats = cursor.fetchall()
    
    # 投篮统计
    cursor.execute("""
        SELECT team, 
               SUM(CASE WHEN event_type = 'Made Shot' THEN 1 ELSE 0 END) as made,
               SUM(CASE WHEN event_type = 'Missed Shot' THEN 1 ELSE 0 END) as missed
        FROM pbp_all
        WHERE gameid = %s AND team IS NOT NULL
        GROUP BY team;
    """, (game_id,))
    shooting_stats = []
    for row in cursor.fetchall():
        team, made, missed = row
        total = made + missed
        rate = (made / total * 100) if total > 0 else 0
        shooting_stats.append({
            'team': team,
            'made': made,
            'missed': missed,
            'total': total,
            'rate': round(rate, 1)
        })
    
    # 各节得分
    cursor.execute("""
        SELECT period, MAX(h_pts) as home, MAX(a_pts) as away
        FROM pbp_all
        WHERE gameid = %s AND period <= 4
        GROUP BY period ORDER BY period;
    """, (game_id,))
    period_scores = []
    for row in cursor.fetchall():
        period, home, away = row
        period_scores.append({
            'period': f'第{period}节',
            'home': home,
            'away': away
        })
    
    conn.close()
    
    return render_template('game_detail.html',
                          game_id=game_id,
                          season=season,
                          teams=teams,
                          home_score=home_score,
                          visitor_score=visitor_score,
                          score_data=score_data,
                          event_stats=event_stats,
                          shooting_stats=shooting_stats,
                          period_scores=period_scores)


@app.route('/api/season_data')
def api_season_data():
    """获取赛季数据API"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT season, COUNT(DISTINCT gameid) as games
        FROM pbp_all
        GROUP BY season
        ORDER BY season;
    """)
    data = []
    for row in cursor.fetchall():
        data.append({'season': row[0], 'games': row[1]})
    
    conn.close()
    return jsonify(data)


@app.route('/api/event_data')
def api_event_data():
    """获取事件类型数据API"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT event_type, COUNT(*) as cnt
        FROM pbp_all
        WHERE event_type IS NOT NULL
        GROUP BY event_type
        ORDER BY cnt DESC
        LIMIT 10;
    """)
    data = []
    for row in cursor.fetchall():
        data.append({'type': row[0], 'count': row[1]})
    
    conn.close()
    return jsonify(data)


@app.route('/game/<int:game_id>/pbp')
def game_pbp(game_id):
    """单场比赛PBP数据展示"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 获取比赛基本信息
        cursor.execute("""
            SELECT DISTINCT team FROM pbp_all 
            WHERE gameid = %s AND team IS NOT NULL;
        """, (game_id,))
        teams = [t[0] for t in cursor.fetchall()]
        
        cursor.execute("""
            SELECT MAX(h_pts), MAX(a_pts), MAX(season) FROM pbp_all
            WHERE gameid = %s AND h_pts IS NOT NULL;
        """, (game_id,))
        result = cursor.fetchone()
        home_score, visitor_score, season = result
        
        # 获取PBP数据
        cursor.execute("""
            SELECT period, eventnum, clock, clock_seconds, team, player, 
                   event_type, subtype, result, dist, x, y, description, h_pts, a_pts
            FROM pbp_all
            WHERE gameid = %s
            ORDER BY period, eventnum;
        """, (game_id,))
        
        pbp_data = []
        for row in cursor.fetchall():
            pbp_data.append({
                'period': int(row[0]) if row[0] else 0,
                'eventnum': int(row[1]) if row[1] else 0,
                'clock': str(row[2]) if row[2] else '',
                'clock_seconds': float(row[3]) if row[3] else 0.0,
                'team': str(row[4]) if row[4] else '',
                'player': str(row[5]) if row[5] else '',
                'event_type': str(row[6]) if row[6] else '',
                'subtype': str(row[7]) if row[7] else '',
                'result': str(row[8]) if row[8] else '',
                'dist': int(row[9]) if row[9] else 0,
                'x': int(row[10]) if row[10] else 0,
                'y': int(row[11]) if row[11] else 0,
                'description': str(row[12]) if row[12] else '',
                'h_pts': int(row[13]) if row[13] else 0,
                'a_pts': int(row[14]) if row[14] else 0
            })
        
        conn.close()
        
        return render_template('game_pbp.html',
                              game_id=game_id,
                              season=season,
                              teams=teams,
                              home_score=home_score,
                              visitor_score=visitor_score,
                              pbp_data=pbp_data)
    
    except Exception as e:
        conn.close()
        return f"Error: {str(e)}", 500


@app.route('/player/<player_name>')
def player_shot_chart(player_name):
    """球员投篮热区展示"""
    import json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取球员投篮数据
    cursor.execute("""
        SELECT x, y, dist, result, season
        FROM pbp_all
        WHERE player ILIKE %s
        AND (event_type LIKE 'Made%%' OR event_type LIKE 'Missed%%')
        AND x IS NOT NULL AND y IS NOT NULL;
    """, (f"%{player_name}%",))
    
    shots = []
    for row in cursor.fetchall():
        x, y, dist, result, season = row
        shots.append({
            'x': float(x),
            'y': float(y),
            'dist': int(dist) if dist else 0,
            'made': result == 'Made',
            'season': season
        })
    
    # 获取区域统计
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN dist <= 5 AND result = 'Made' THEN 1 ELSE 0 END) as close_made,
            SUM(CASE WHEN dist <= 5 THEN 1 ELSE 0 END) as close_att,
            SUM(CASE WHEN dist > 5 AND dist <= 18 AND result = 'Made' THEN 1 ELSE 0 END) as mid_made,
            SUM(CASE WHEN dist > 5 AND dist <= 18 THEN 1 ELSE 0 END) as mid_att,
            SUM(CASE WHEN dist > 22 AND result = 'Made' THEN 1 ELSE 0 END) as three_made,
            SUM(CASE WHEN dist > 22 THEN 1 ELSE 0 END) as three_att
        FROM pbp_all
        WHERE player ILIKE %s
        AND (event_type LIKE 'Made%%' OR event_type LIKE 'Missed%%');
    """, (f"%{player_name}%",))
    
    row = cursor.fetchone()
    zone_stats = [
        {'name': '禁区', 'made': row[0], 'att': row[1], 'pct': round(row[0]/row[1]*100,1) if row[1] else 0},
        {'name': '中距离', 'made': row[2], 'att': row[3], 'pct': round(row[2]/row[3]*100,1) if row[3] else 0},
        {'name': '三分', 'made': row[4], 'att': row[5], 'pct': round(row[4]/row[5]*100,1) if row[5] else 0}
    ]
    
    conn.close()
    
    total_shots = len(shots)
    made_count = sum(1 for s in shots if s['made'])
    fg_pct = round(made_count / total_shots * 100, 1) if total_shots else 0
    
    return render_template('player_shot_chart.html',
                          player_name=player_name,
                          shots=json.dumps(shots),
                          total_shots=total_shots,
                          made_count=made_count,
                          fg_pct=fg_pct,
                          zone_stats=zone_stats)


@app.route('/players')
def players_list():
    """球员列表页面"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取热门球员
    cursor.execute("""
        SELECT player, COUNT(*) as shots
        FROM pbp_all
        WHERE player IS NOT NULL
        AND (event_type LIKE 'Made%%' OR event_type LIKE 'Missed%%')
        GROUP BY player
        ORDER BY shots DESC
        LIMIT 50;
    """)
    
    players = []
    for row in cursor.fetchall():
        players.append({'name': row[0], 'shots': row[1]})
    
    conn.close()
    
    return render_template('players_list.html', players=players)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
