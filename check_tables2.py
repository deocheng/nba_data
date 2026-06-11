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

    # 查看 teams 表的字段
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'teams'
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    print('teams 表的字段:')
    for col in columns:
        print(f'  {col[0]}')

    # 查看 games 表的字段
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'games'
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    print('\ngames 表的字段:')
    for col in columns:
        print(f'  {col[0]}')

    # 查看 games 表中马刺队的比赛
    cursor.execute("""
        SELECT game_id, game_date, season, home_team_id, away_team_id
        FROM games
        ORDER BY game_date DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()
    print('\ngames 表中最近10场比赛:')
    for row in rows:
        print(f'  {row}')

    conn.close()
except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()
