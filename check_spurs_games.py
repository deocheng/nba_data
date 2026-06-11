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

    # 查看 teams 表中马刺队的信息
    cursor.execute("""
        SELECT team_id, name, abbreviation
        FROM teams
        WHERE abbreviation = 'SAS'
    """)

    row = cursor.fetchone()
    if row:
        print(f'马刺队信息:')
        print(f'  team_id: {row[0]}')
        print(f'  name: {row[1]}')
        print(f'  abbreviation: {row[2]}')
    else:
        print('未找到马刺队')

    # 查看 games 表中马刺队的比赛（2025-26赛季）
    cursor.execute("""
        SELECT
            g.game_id,
            g.game_date,
            g.season,
            g.home_team_id,
            g.away_team_id,
            g.home_score,
            g.away_score,
            ht.abbreviation as home_team_abbr,
            at.abbreviation as away_team_abbr
        FROM games g
        JOIN teams ht ON g.home_team_id = ht.team_id
        JOIN teams at ON g.away_team_id = at.team_id
        WHERE (ht.abbreviation = 'SAS' OR at.abbreviation = 'SAS')
          AND g.season = '2025-26'
        ORDER BY g.game_date DESC
        LIMIT 5
    """)

    rows = cursor.fetchall()
    print('\n马刺队最近5场 2025-26 赛季比赛:')
    for row in rows:
        print(f'  Game ID: {row[0]}')
        print(f'  日期: {row[1]}')
        print(f'  {row[7]} {row[5]} vs {row[8]} {row[6]}')
        print()

    conn.close()
except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()
