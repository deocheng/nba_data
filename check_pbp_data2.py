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

    # 查看 play_by_play 表的数据样例
    print('play_by_play 表的数据样例:')
    cursor.execute("""
        SELECT
            id,
            game_id,
            period,
            clock,
            description,
            home_score,
            away_score,
            player_name,
            team_abbr,
            event_type
        FROM play_by_play
        ORDER BY game_id, period, clock DESC
        LIMIT 20
    """)
    rows = cursor.fetchall()
    for row in rows:
        print(f'  Game: {row[1]}, Period: {row[2]}, Clock: {row[3]}')
        print(f'  Player: {row[7]}, Team: {row[8]}')
        print(f'  Event: {row[9]}, Description: {row[4]}')
        print(f'  Score: {row[5]}-{row[6]}')
        print()

    # 检查有哪些不同的 game_id
    cursor.execute("""
        SELECT DISTINCT game_id
        FROM play_by_play
        ORDER BY game_id DESC
        LIMIT 10
    """)
    game_ids = cursor.fetchall()
    print('\nplay_by_play 表中最近10个 game_id:')
    for gid in game_ids:
        print(f'  {gid[0]}')

    # 检查马刺队的 play_by_play 数据
    print('\n\n马刺队的 play_by_play 数据样例:')
    cursor.execute("""
        SELECT
            game_id,
            player_name,
            team_abbr,
            event_type,
            description,
            home_score,
            away_score
        FROM play_by_play
        WHERE team_abbr = 'SAS'
        ORDER BY game_id, period, clock DESC
        LIMIT 20
    """)
    rows = cursor.fetchall()
    for row in rows:
        print(f'  Game: {row[0]}, Player: {row[1]}')
        print(f'  Event: {row[3]}, Score: {row[5]}-{row[6]}')
        print()

    conn.close()
except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()