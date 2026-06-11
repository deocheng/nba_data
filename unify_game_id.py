#!/usr/bin/env python3
"""统一Game ID格式 - 将爬取数据的ID映射到pbp_all格式"""
import psycopg2

DB_CONFIG = {
    'dbname': 'nba',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5433'
}


def create_game_id_mapping(conn):
    """创建Game ID映射表"""
    cursor = conn.cursor()
    
    # 创建映射表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_id_mapping (
            id SERIAL PRIMARY KEY,
            crawled_id VARCHAR(50) NOT NULL,
            nba_id BIGINT NOT NULL,
            season INTEGER,
            home_score INTEGER,
            visitor_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE UNIQUE INDEX IF NOT EXISTS idx_game_id_mapping_crawled_id ON game_id_mapping(crawled_id);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_game_id_mapping_nba_id ON game_id_mapping(nba_id);
    """)
    conn.commit()
    print("✅ 创建 game_id_mapping 表")


def build_mapping(conn):
    """构建ID映射关系"""
    cursor = conn.cursor()
    
    # 清空旧映射
    cursor.execute("DELETE FROM game_id_mapping;")
    
    # 获取爬取比赛的信息
    cursor.execute("""
        SELECT gm.game_id, gm.home_score, gm.visitor_score, gm.season_end
        FROM game_metadata gm
        WHERE gm.pbp_imported = true;
    """)
    crawled_games = cursor.fetchall()
    
    print(f"🔄 正在构建 {len(crawled_games)} 个比赛的ID映射...")
    
    # 为每个爬取比赛查找对应的NBA ID
    mappings = []
    for crawled_id, home_score, visitor_score, season_end in crawled_games:
        if home_score is None or visitor_score is None:
            continue
        
        # 在pbp_all中查找相同比分的比赛
        cursor.execute("""
            SELECT gameid, season
            FROM pbp_all
            WHERE h_pts = %s AND a_pts = %s
            AND ABS(season - %s) <= 1
            LIMIT 1;
        """, (home_score, visitor_score, season_end))
        
        result = cursor.fetchone()
        if result:
            nba_id, nba_season = result
            mappings.append((crawled_id, nba_id, nba_season, home_score, visitor_score))
    
    # 批量插入映射
    if mappings:
        cursor.executemany("""
            INSERT INTO game_id_mapping (crawled_id, nba_id, season, home_score, visitor_score)
            VALUES (%s, %s, %s, %s, %s);
        """, mappings)
        conn.commit()
        print(f"✅ 成功构建 {len(mappings)} 个ID映射")
    else:
        print("❌ 未找到任何匹配")
    
    return len(mappings)


def update_play_by_play(conn):
    """更新play_by_play表使用统一的NBA ID"""
    cursor = conn.cursor()
    
    print("\n🔄 更新 play_by_play 表...")
    
    # 添加新字段存储统一ID
    cursor.execute("ALTER TABLE play_by_play ADD COLUMN IF NOT EXISTS nba_gameid BIGINT;")
    
    # 更新nba_gameid字段
    cursor.execute("""
        UPDATE play_by_play p
        SET nba_gameid = m.nba_id
        FROM game_id_mapping m
        WHERE p.game_id = m.crawled_id;
    """)
    conn.commit()
    
    # 检查更新结果
    cursor.execute("SELECT COUNT(*) FROM play_by_play WHERE nba_gameid IS NOT NULL;")
    updated = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM play_by_play;")
    total = cursor.fetchone()[0]
    
    print(f"✅ 更新完成: {updated}/{total} 条记录")
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_play_by_play_nba_gameid ON play_by_play(nba_gameid);")
    conn.commit()
    print("✅ 创建 nba_gameid 索引")


def update_game_metadata(conn):
    """更新game_metadata表使用统一的NBA ID"""
    cursor = conn.cursor()
    
    print("\n🔄 更新 game_metadata 表...")
    
    # 添加新字段
    cursor.execute("ALTER TABLE game_metadata ADD COLUMN IF NOT EXISTS nba_gameid BIGINT;")
    
    # 更新
    cursor.execute("""
        UPDATE game_metadata gm
        SET nba_gameid = m.nba_id
        FROM game_id_mapping m
        WHERE gm.game_id = m.crawled_id;
    """)
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM game_metadata WHERE nba_gameid IS NOT NULL;")
    updated = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM game_metadata;")
    total = cursor.fetchone()[0]
    
    print(f"✅ 更新完成: {updated}/{total} 条记录")


def verify_mapping(conn):
    """验证映射结果"""
    cursor = conn.cursor()
    
    print("\n" + "=" * 80)
    print("🔍 验证映射结果")
    print("=" * 80)
    
    # 映射表统计
    cursor.execute("SELECT COUNT(*) FROM game_id_mapping;")
    mapping_count = cursor.fetchone()[0]
    
    # play_by_play统计
    cursor.execute("SELECT COUNT(*) FROM play_by_play WHERE nba_gameid IS NOT NULL;")
    pbp_updated = cursor.fetchone()[0]
    
    # game_metadata统计
    cursor.execute("SELECT COUNT(*) FROM game_metadata WHERE nba_gameid IS NOT NULL;")
    meta_updated = cursor.fetchone()[0]
    
    print(f"\n📊 映射表记录: {mapping_count}")
    print(f"📊 play_by_play 更新: {pbp_updated} 条")
    print(f"📊 game_metadata 更新: {meta_updated} 条")
    
    # 显示一些映射示例
    cursor.execute("SELECT crawled_id, nba_id, season FROM game_id_mapping LIMIT 10;")
    mappings = cursor.fetchall()
    
    print("\n📋 映射示例:")
    print(f"{'爬取ID':<15} {'NBA ID':<12} {'赛季'}")
    print("-" * 40)
    for crawled_id, nba_id, season in mappings:
        print(f"{crawled_id:<15} {nba_id:<12} {season}")


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    
    print("=" * 80)
    print("🔧 统一Game ID格式")
    print("=" * 80)
    
    # 步骤1: 创建映射表
    create_game_id_mapping(conn)
    
    # 步骤2: 构建映射关系
    build_mapping(conn)
    
    # 步骤3: 更新play_by_play表
    update_play_by_play(conn)
    
    # 步骤4: 更新game_metadata表
    update_game_metadata(conn)
    
    # 步骤5: 验证结果
    verify_mapping(conn)
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ 统一ID完成！")
    print("=" * 80)
    print("\n📌 现在可以使用 nba_gameid 字段在两个数据源间进行关联查询")


if __name__ == '__main__':
    main()
