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

    # 查看 play_by_play 表中有数据的比赛
    cursor.execute("""
        SELECT
            g.game_id,
            g.game_date,
            g.season,
            ht.abbreviation as home_team,
            at.abbreviation as away_team,
            COUNT(*) as pbp_count
        FROM games g
        JOIN teams ht ON g.home_team_id = ht.team_id
        JOIN teams at ON g.away_team_id = at.team_id
        JOIN play_by_play pbp ON g.game_id = pbp.game_id
        GROUP BY g.game_id, g.game_date, g.season, ht.abbreviation, at.abbreviation
        ORDER BY g.game_date DESC
        LIMIT 20
    """)

    rows = cursor.fetchall()
    print('有 play-by-play 数据的比赛:')
    for row in rows:
        print(f'  game_id: {row[0]}')
        print(f'  日期: {row[1]}')
        print(f'  {row[4]} @ {row[3]}')
        print(f'  play-by-play 数据: {row[5]} 条')
        print()

    conn.close()
except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()