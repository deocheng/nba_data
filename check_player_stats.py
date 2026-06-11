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

    # 查看 player_game_stats 表的字段
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'player_game_stats'
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    print('player_game_stats 表的字段:')
    for col in columns:
        print(f'  {col[0]}')

    # 查看前5条数据
    cursor.execute("SELECT * FROM player_game_stats LIMIT 5")
    rows = cursor.fetchall()
    print('\nplayer_game_stats 表数据样例:')
    for row in rows:
        print(row)

    conn.close()
except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()
