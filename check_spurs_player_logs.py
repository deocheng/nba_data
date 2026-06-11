import psycopg2
import os

db_config = {
    'dbname': os.getenv('POSTGRES_DB', 'nba'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5433')
}

try:
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    # 查看 player_game_logs 表中马刺队最近的5场比赛
    cursor.execute("""
        SELECT
            pgl.game_id,
            pgl.game_date,
            pgl.opp_team_abbr,
            pgl.result,
            pgl.minutes_played,
            pgl.points,
            pgl.rebounds,
            pgl.assists,
            pgl.steals,
            pgl.blocks,
            pgl.fg_made,
            pgl.fg_att,
            pgl.three_made,
            pgl.three_att,
            pgl.ft_made,
            pgl.ft_att,
            pgl.plus_minus,
            p.name as player_name
        FROM player_game_logs pgl
        JOIN players p ON pgl.player_id = p.player_id
        WHERE pgl.team_id = 27
        ORDER BY pgl.game_date DESC, pgl.points DESC
        LIMIT 20
    """)

    rows = cursor.fetchall()
    print('马刺队最近的球员比赛数据:')
    for row in rows:
        print(f'  日期: {row[1]}')
        print(f'  球员: {row[17]}')
        print(f'  对手: {row[2]}')
        print(f'  结果: {row[3]}')
        print(f'  得分: {row[5]}')
        print(f'  时间: {row[4]}')
        print()

    conn.close()
except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()
