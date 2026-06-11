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

    # 查看 player_game_stats 表中不同的 game_id
    cursor.execute("""
        SELECT DISTINCT game_id
        FROM player_game_stats
        ORDER BY game_id DESC
        LIMIT 20
    """)

    rows = cursor.fetchall()
    print('player_game_stats 表中最近20个 game_id:')
    for row in rows:
        print(f'  {row[0]}')

    # 检查 player_game_logs 表
    print('\n\nplayer_game_logs 表的字段:')
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'player_game_logs'
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    for col in columns:
        print(f'  {col[0]}')

    # 查看 player_game_logs 表中不同的 game_id
    cursor.execute("""
        SELECT DISTINCT game_id
        FROM player_game_logs
        ORDER BY game_id DESC
        LIMIT 20
    """)

    rows = cursor.fetchall()
    print('\n\nplayer_game_logs 表中最近20个 game_id:')
    for row in rows:
        print(f'  {row[0]}')

    conn.close()
except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()
