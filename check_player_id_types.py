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

    # 检查 players 表的 player_id 类型
    cursor.execute("""
        SELECT player_id, name
        FROM players
        LIMIT 5
    """)

    rows = cursor.fetchall()
    print('players 表中的 player_id:')
    for row in rows:
        print(f'  {row[0]} - {row[1]} (类型: {type(row[0]).__name__})')

    # 检查 player_game_logs 表的 player_id 类型
    cursor.execute("""
        SELECT DISTINCT player_id
        FROM player_game_logs
        LIMIT 5
    """)

    rows = cursor.fetchall()
    print('\nplayer_game_logs 表中的 player_id:')
    for row in rows:
        print(f'  {row[0]} (类型: {type(row[0]).__name__})')

    conn.close()
except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()
