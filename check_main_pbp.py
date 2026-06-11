#!/usr/bin/env python3
"""检视play_by_play主表的时间跨度"""
import psycopg2

def check_play_by_play():
    db_config = {
        'dbname': 'nba',
        'user': 'postgres',
        'password': 'postgres',
        'host': 'localhost',
        'port': '5433'
    }
    
    conn = psycopg2.connect(**db_config)
    
    try:
        cursor = conn.cursor()
        
        print("=" * 80)
        print("play_by_play 主表分析")
        print("=" * 80)
        
        # 总记录数
        cursor.execute("SELECT COUNT(*) FROM play_by_play;")
        count = cursor.fetchone()[0]
        print(f"\n📊 总记录数: {count:,}")
        
        # 查看表结构
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'play_by_play'
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        
        print(f"\n📋 表结构 ({len(columns)} 列):")
        for col_name, data_type in columns:
            print(f"  {col_name:<30} {data_type}")
        
        # 检查game_metadata中的日期
        print("\n" + "=" * 80)
        print("game_metadata 时间分析")
        print("=" * 80)
        
        cursor.execute("SELECT COUNT(*) FROM game_metadata;")
        meta_count = cursor.fetchone()[0]
        print(f"\n📋 总比赛数: {meta_count}")
        
        # 查看game_metadata结构
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'game_metadata'
            ORDER BY ordinal_position;
        """)
        meta_cols = cursor.fetchall()
        print(f"\n表结构 ({len(meta_cols)} 列):")
        for col_name, data_type in meta_cols:
            print(f"  {col_name:<30} {data_type}")
        
        # 尝试查找日期列
        cursor.execute("SELECT * FROM game_metadata LIMIT 5;")
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]
        
        print(f"\n📝 样本数据:")
        for i, row in enumerate(rows):
            print(f"\n比赛 {i+1}:")
            for col_name, val in zip(col_names, row):
                print(f"  {col_name}: {val}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    check_play_by_play()
