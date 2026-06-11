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

    # 查看马刺队2025-26赛季的比赛
    cursor.execute("""
        SELECT
            g.game_id,
            g.game_date,
            g.season,
            ht.abbreviation as home_team,
            at.abbreviation as away_team,
            g.home_score,
            g.away_score
        FROM games g
        JOIN teams ht ON g.home_team_id = ht.team_id
        JOIN teams at ON g.away_team_id = at.team_id
        WHERE (ht.abbreviation = 'SAS' OR at.abbreviation = 'SAS')
          AND g.season = '2025-26'
        ORDER BY g.game_date
        LIMIT 10
    """)

    rows = cursor.fetchall()
    print('马刺队 2025-26 赛季比赛:')
    for row in rows:
        print(f'  game_id: {row[0]}')
        print(f'  日期: {row[1]}')
        print(f'  {row[4]} @ {row[3]}')
        print(f'  比分: {row[5]}-{row[6]}')
        print()

    # 检查 play_by_play 表中是否有这些比赛的 play-by-play 数据
    print('\n检查 play_by_play 数据:')
    for row in rows:
        game_id = row[0]
        cursor.execute("""
            SELECT COUNT(*)
            FROM play_by_play
            WHERE game_id = %s
        """, (game_id,))

        count = cursor.fetchone()[0]
        print(f'  game_id {game_id}: {count} 条 play-by-play 数据')

    conn.close()
except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()