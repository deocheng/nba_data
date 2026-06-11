#!/usr/bin/env python3
"""统一Game ID格式 - 优化版（批量查询）"""
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
    print("🔧 统一Game ID格式")
    print("=" * 80)
    
    # 步骤1: 创建/清空映射表
    cursor.execute("DROP TABLE IF EXISTS game_id_mapping;")
    cursor.execute("""
        CREATE TABLE game_id_mapping (
            id SERIAL PRIMARY KEY,
            crawled_id VARCHAR(50) NOT NULL,
            nba_id BIGINT NOT NULL,
            season INTEGER,
            home_score INTEGER,
            visitor_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE UNIQUE INDEX idx_game_id_mapping_crawled_id ON game_id_mapping(crawled_id);
        CREATE INDEX idx_game_id_mapping_nba_id ON game_id_mapping(nba_id);  -- 非唯一索引，允许一对多
    """)
    conn.commit()
    print("✅ 创建 game_id_mapping 表")
    
    # 步骤2: 构建比分->gameid索引（从pbp_all）
    print("\n🔄 构建比分索引...")
    cursor.execute("""
        SELECT DISTINCT gameid, season, 
               MAX(h_pts) OVER (PARTITION BY gameid) as home_score,
               MAX(a_pts) OVER (PARTITION BY gameid) as visitor_score
        FROM pbp_all
        WHERE h_pts IS NOT NULL AND a_pts IS NOT NULL;
    """)
    
    score_index = {}
    for row in cursor.fetchall():
        gameid, season, h_pts, a_pts = row
        score_key = f"{int(h_pts)}-{int(a_pts)}"
        if score_key not in score_index:
            score_index[score_key] = []
        score_index[score_key].append((gameid, season))
    
    print(f"   索引构建完成: {len(score_index)} 个不同比分")
    
    # 步骤3: 获取爬取比赛并匹配
    print("\n🔄 匹配比赛ID...")
    cursor.execute("""
        SELECT gm.game_id, gm.home_score, gm.visitor_score, gm.season_end
        FROM game_metadata gm
        WHERE gm.pbp_imported = true AND gm.home_score IS NOT NULL;
    """)
    
    mappings = []
    matched = 0
    unmatched = 0
    
    for crawled_id, home_score, visitor_score, season_end in cursor.fetchall():
        score_key = f"{int(home_score)}-{int(visitor_score)}"
        
        if score_key in score_index:
            candidates = score_index[score_key]
            
            # 优先匹配赛季接近的
            found = False
            for nba_id, nba_season in candidates:
                if abs(nba_season - season_end) <= 1:
                    mappings.append((crawled_id, nba_id, nba_season, home_score, visitor_score))
                    matched += 1
                    found = True
                    break
            
            if not found:
                # 如果没有赛季匹配，取第一个
                nba_id, nba_season = candidates[0]
                mappings.append((crawled_id, nba_id, nba_season, home_score, visitor_score))
                matched += 1
        else:
            unmatched += 1
    
    print(f"   匹配成功: {matched}, 未匹配: {unmatched}")
    
    # 步骤4: 批量插入映射
    cursor.executemany("""
        INSERT INTO game_id_mapping (crawled_id, nba_id, season, home_score, visitor_score)
        VALUES (%s, %s, %s, %s, %s);
    """, mappings)
    conn.commit()
    print("✅ 映射表更新完成")
    
    # 步骤5: 更新play_by_play表
    print("\n🔄 更新 play_by_play 表...")
    cursor.execute("ALTER TABLE play_by_play ADD COLUMN IF NOT EXISTS nba_gameid BIGINT;")
    cursor.execute("""
        UPDATE play_by_play p
        SET nba_gameid = m.nba_id
        FROM game_id_mapping m
        WHERE p.game_id = m.crawled_id;
    """)
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM play_by_play WHERE nba_gameid IS NOT NULL;")
    pbp_updated = cursor.fetchone()[0]
    print(f"   ✅ 更新 {pbp_updated} 条记录")
    
    # 步骤6: 更新game_metadata表
    print("\n🔄 更新 game_metadata 表...")
    cursor.execute("ALTER TABLE game_metadata ADD COLUMN IF NOT EXISTS nba_gameid BIGINT;")
    cursor.execute("""
        UPDATE game_metadata gm
        SET nba_gameid = m.nba_id
        FROM game_id_mapping m
        WHERE gm.game_id = m.crawled_id;
    """)
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM game_metadata WHERE nba_gameid IS NOT NULL;")
    meta_updated = cursor.fetchone()[0]
    print(f"   ✅ 更新 {meta_updated} 条记录")
    
    # 步骤7: 创建索引
    print("\n🔄 创建索引...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_play_by_play_nba_gameid ON play_by_play(nba_gameid);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_game_metadata_nba_gameid ON game_metadata(nba_gameid);")
    conn.commit()
    print("   ✅ 索引创建完成")
    
    # 验证
    print("\n" + "=" * 80)
    print("🔍 验证结果")
    print("=" * 80)
    
    cursor.execute("SELECT COUNT(*) FROM game_id_mapping;")
    mapping_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT crawled_id, nba_id, season FROM game_id_mapping LIMIT 5;")
    sample_mappings = cursor.fetchall()
    
    print(f"\n📊 映射表记录: {mapping_count}")
    print("\n📋 映射示例:")
    for crawled_id, nba_id, season in sample_mappings:
        print(f"   {crawled_id} → {nba_id} (赛季 {season})")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ 统一ID完成！")
    print("=" * 80)


if __name__ == '__main__':
    main()
