#!/usr/bin/env python3
"""检视PBP赛季覆盖情况"""
import psycopg2

def check_seasons():
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
        print("📊 PBP数据时间跨度总览")
        print("=" * 80)
        
        # play_by_play表
        print("\n🔵 play_by_play 主表")
        print("-" * 80)
        cursor.execute("""
            SELECT season_end, COUNT(*) as game_count, SUM(record_count) as total_records
            FROM (
                SELECT season_end, COUNT(*) as record_count, game_id
                FROM play_by_play
                GROUP BY season_end, game_id
            ) t
            GROUP BY season_end
            ORDER BY season_end;
        """)
        pbp_seasons = cursor.fetchall()
        
        for season, game_count, total_records in pbp_seasons:
            print(f"  {season}赛季: {game_count}场比赛, {total_records:,}条记录")
        
        cursor.execute("SELECT COUNT(DISTINCT game_id) FROM play_by_play;")
        total_games = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM play_by_play;")
        total_records = cursor.fetchone()[0]
        
        pbp_season_list = [s for s, _, _ in pbp_seasons]
        if pbp_season_list:
            print(f"\n  ⏱️  时间跨度: {min(pbp_season_list)} - {max(pbp_season_list)}")
        print(f"  📈 总计: {total_games}场比赛, {total_records:,}条记录")
        
        # pbp_1997表
        print("\n" + "=" * 80)
        print("🟢 pbp_1997 历史表")
        print("-" * 80)
        
        cursor.execute("""
            SELECT season, COUNT(*) as cnt, COUNT(DISTINCT gameid) as game_count
            FROM pbp_1997
            GROUP BY season
            ORDER BY season;
        """)
        pbp1997 = cursor.fetchall()
        
        for season, cnt, game_count in pbp1997:
            print(f"  {season}赛季: {game_count}场比赛, {cnt:,}条记录")
        
        # 总结
        print("\n" + "=" * 80)
        print("📅 PBP数据时间跨度总结")
        print("=" * 80)
        
        all_seasons = set()
        for s, _, _ in pbp_seasons:
            all_seasons.add(s)
        for s, _, _ in pbp1997:
            all_seasons.add(s)
        
        print(f"\n所有赛季: {sorted(all_seasons)}")
        print(f"时间跨度: {min(all_seasons)} - {max(all_seasons)}")
        
        total_all_records = total_records + 595362
        print(f"PBP总记录数: {total_all_records:,}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    check_seasons()
