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

    # 查找所有包含 play_by_play 的表
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name LIKE '%play_by_play%'
        ORDER BY table_name
    """)

    tables = cursor.fetchall()
    print('包含 play_by_play 的表:')
    for table in tables:
        print(f'  {table[0]}')

        # 查看表结构
        cursor.execute(f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{table[0]}'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        print(f'    字段:')
        for col in columns:
            print(f'      {col[0]} ({col[1]})')

    # 查看 play_by_play 表的数据样例
    if tables:
        table_name = tables[0][0]
        print(f'\n\n{table_name} 表的数据样例:')
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 10")
        rows = cursor.fetchall()
        for row in rows:
            print(row)

    conn.close()
except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()