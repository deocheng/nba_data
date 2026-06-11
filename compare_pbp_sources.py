#!/usr/bin/env python3
"""对比导入数据(pbp_all)和爬取数据(play_by_play)的场次重叠情况"""
import psycopg2

DB_CONFIG = {
    'dbname': 'nba',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5433'
}


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("📊 PBP数据场次对比分析")
    print("=" * 80)
    
    # 1. play_by_play 表（爬取的数据）
    print("\n🔵 爬取数据 (play_by_play 表)")
    print("-" * 80)
    
    cursor.execute("SELECT COUNT(DISTINCT game_id) FROM play_by_play;")
    pb_games = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM play_by_play;")
    pb_rows = cursor.fetchone()[0]
    
    cursor.execute("SELECT MIN(season_end), MAX(season_end) FROM play_by_play;")
    pb_seasons = cursor.fetchone()
    
    print(f"  比赛场次: {pb_games:,}")
    print(f"  记录总数: {pb_rows:,}")
    print(f"  赛季范围: {pb_seasons[0]} - {pb_seasons[1]}")
    
    cursor.execute("""
        SELECT season_end, COUNT(DISTINCT game_id) as cnt
        FROM play_by_play
        GROUP BY season_end
        ORDER BY season_end;
    """)
    pb_season_counts = cursor.fetchall()
    print(f"  各赛季场次:")
    for season, cnt in pb_season_counts:
        print(f"    {season}: {cnt} 场")
    
    # 2. pbp_all 表（CSV导入的数据）
    print("\n🟢 导入数据 (pbp_all 表)")
    print("-" * 80)
    
    cursor.execute("SELECT COUNT(DISTINCT gameid) FROM pbp_all;")
    all_games = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM pbp_all;")
    all_rows = cursor.fetchone()[0]
    
    cursor.execute("SELECT MIN(season), MAX(season) FROM pbp_all;")
    all_seasons = cursor.fetchone()
    
    print(f"  比赛场次: {all_games:,}")
    print(f"  记录总数: {all_rows:,}")
    print(f"  赛季范围: {all_seasons[0]} - {all_seasons[1]}")
    
    # 3. 对比分析
    print("\n🔍 场次对比分析")
    print("-" * 80)
    
    # 获取两个表的game_id列表
    cursor.execute("SELECT DISTINCT game_id FROM play_by_play;")
    pb_game_ids = set([str(row[0]) for row in cursor.fetchall()])
    
    cursor.execute("SELECT DISTINCT gameid FROM pbp_all;")
    all_game_ids = set([str(row[0]) for row in cursor.fetchall()])
    
    print(f"\n  play_by_play 独有的场次: {len(pb_game_ids - all_game_ids)}")
    print(f"  pbp_all 独有的场次: {len(all_game_ids - pb_game_ids)}")
    print(f"  两个表都有的场次: {len(pb_game_ids & all_game_ids)}")
    
    # 查看重叠的场次详情（如果有的话）
    overlap = pb_game_ids & all_game_ids
    if overlap:
        print(f"\n  重叠场次示例 (前10个):")
        for gid in sorted(list(overlap))[:10]:
            print(f"    {gid}")
    
    # 4. 检查2026赛季的重叠情况（因为爬取的数据主要是2026赛季）
    print("\n📅 2026赛季专项对比")
    print("-" * 80)
    
    cursor.execute("SELECT COUNT(DISTINCT game_id) FROM play_by_play WHERE season_end = 2026;")
    pb_2026 = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT gameid) FROM pbp_all WHERE season = 2026;")
    all_2026 = cursor.fetchone()[0]
    
    cursor.execute("SELECT DISTINCT game_id FROM play_by_play WHERE season_end = 2026;")
    pb_2026_ids = set([str(row[0]) for row in cursor.fetchall()])
    
    cursor.execute("SELECT DISTINCT gameid FROM pbp_all WHERE season = 2026;")
    all_2026_ids = set([str(row[0]) for row in cursor.fetchall()])
    
    print(f"\n  play_by_play 2026赛季场次: {pb_2026}")
    print(f"  pbp_all 2026赛季场次: {all_2026}")
    print(f"  2026赛季重叠场次: {len(pb_2026_ids & all_2026_ids)}")
    print(f"  play_by_play 2026独有场次: {len(pb_2026_ids - all_2026_ids)}")
    print(f"  pbp_all 2026独有场次: {len(all_2026_ids - pb_2026_ids)}")
    
    # 如果有2026赛季的独有场次，列出一些示例
    pb_2026_unique = pb_2026_ids - all_2026_ids
    all_2026_unique = all_2026_ids - pb_2026_ids
    
    if pb_2026_unique:
        print(f"\n  play_by_play 2026独有场次示例:")
        for gid in sorted(list(pb_2026_unique))[:5]:
            print(f"    {gid}")
    
    if all_2026_unique:
        print(f"\n  pbp_all 2026独有场次示例:")
        for gid in sorted(list(all_2026_unique))[:5]:
            print(f"    {gid}")
    
    # 5. 查看game_metadata表中的爬取状态
    print("\n📋 game_metadata 爬取状态")
    print("-" * 80)
    
    cursor.execute("SELECT COUNT(*) FROM game_metadata;")
    meta_total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM game_metadata WHERE pbp_saved = true;")
    meta_saved = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM game_metadata WHERE pbp_imported = true;")
    meta_imported = cursor.fetchone()[0]
    
    print(f"\n  game_metadata 总记录: {meta_total}")
    print(f"  PBP已保存: {meta_saved}")
    print(f"  PBP已导入: {meta_imported}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ 对比分析完成")
    print("=" * 80)


if __name__ == '__main__':
    main()
