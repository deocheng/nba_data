#!/usr/bin/env python3
"""检视PBP数据时间跨度"""
import psycopg2

def check_pbp_time_span():
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
        
        # 查看有哪些PBP表
        print("=" * 80)
        print("现有PBP数据表")
        print("=" * 80)
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename LIKE 'pbp%'
            ORDER BY tablename;
        """)
        tables = cursor.fetchall()
        
        for (table_name,) in tables:
            print(f"\n📊 {table_name}")
            print("-" * 80)
            
            # 查询行数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"  总记录数: {count:,}")
            
            # 检查season列
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                AND column_name = 'season';
            """)
            has_season = cursor.fetchone() is not None
            
            if has_season:
                # 查询season分布
                cursor.execute(f"""
                    SELECT season, COUNT(*) as cnt
                    FROM {table_name}
                    WHERE season IS NOT NULL
                    GROUP BY season
                    ORDER BY season;
                """)
                seasons = cursor.fetchall()
                
                print(f"\n  赛季分布:")
                for season, cnt in seasons:
                    print(f"    {season}: {cnt:,} 条")
                
                if seasons:
                    season_list = [s for s, _ in seasons if s is not None]
                    if season_list:
                        print(f"\n  ⏱️  时间跨度: {min(season_list)} - {max(season_list)}")
            else:
                print(f"  无season列")
    
    finally:
        conn.close()

if __name__ == "__main__":
    check_pbp_time_span()
