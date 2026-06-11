#!/usr/bin/env python3
"""批量导入1998-2025年PBP数据到数据库
优化点：
1. 使用统一表结构 pbp_all 存储所有年份
2. 添加 eventnum（每个比赛内的事件编号）
3. 添加 clock_seconds（时间字段转换为秒数）
4. desc 字段重命名为 description（避免SQL关键字冲突）
5. 使用 COPY 命令批量导入，比INSERT快很多
6. 建立 (season, gameid, eventnum) 联合索引
"""
import pandas as pd
import psycopg2
import re
import time
import tempfile
import os
from pathlib import Path

# 数据库配置
DB_CONFIG = {
    'dbname': 'nba',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5433'
}

CSV_DIR = Path('CSV')
TARGET_TABLE = 'pbp_all'
CHUNKSIZE = 100000  # 每批处理行数

def parse_clock_to_seconds(clock_str):
    """将 PT12M00.00S 格式转换为秒数"""
    if pd.isna(clock_str) or not isinstance(clock_str, str):
        return None
    match = re.match(r'PT(\d+)M(\d+(?:\.\d+)?)S', clock_str)
    if match:
        minutes = float(match.group(1))
        seconds = float(match.group(2))
        return minutes * 60 + seconds
    # 备用: 尝试 12:00.0 格式
    match2 = re.match(r'(\d+):(\d+(?:\.\d+)?)', str(clock_str))
    if match2:
        minutes = float(match2.group(1))
        seconds = float(match2.group(2))
        return minutes * 60 + seconds
    return None


def create_table(conn):
    """创建统一PBP数据表（如果不存在）"""
    cursor = conn.cursor()
    
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TARGET_TABLE} (
            id SERIAL PRIMARY KEY,
            season INTEGER,
            gameid BIGINT,
            eventnum INTEGER,
            period INTEGER,
            clock VARCHAR(20),
            clock_seconds FLOAT,
            h_pts FLOAT,
            a_pts FLOAT,
            team VARCHAR(10),
            playerid BIGINT,
            player VARCHAR(100),
            event_type VARCHAR(50),
            subtype VARCHAR(100),
            result VARCHAR(20),
            x INTEGER,
            y INTEGER,
            dist INTEGER,
            description TEXT
        );
    """)
    conn.commit()
    print(f"✅ 表 {TARGET_TABLE} 已创建/存在")


def drop_table(conn):
    """清空并重建表（用于重新导入）"""
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {TARGET_TABLE};")
    conn.commit()
    print(f"✅ 旧表 {TARGET_TABLE} 已删除")


def create_indexes(conn):
    """创建查询索引"""
    cursor = conn.cursor()
    
    print("🔨 创建索引中...")
    
    index_defs = [
        (f"idx_{TARGET_TABLE}_season_game_event", f"(season, gameid, eventnum)"),
        (f"idx_{TARGET_TABLE}_season", f"(season)"),
        (f"idx_{TARGET_TABLE}_gameid", f"(gameid)"),
        (f"idx_{TARGET_TABLE}_playerid", f"(playerid)"),
        (f"idx_{TARGET_TABLE}_team", f"(team)"),
        (f"idx_{TARGET_TABLE}_event_type", f"(event_type)"),
    ]
    
    for idx_name, idx_def in index_defs:
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {TARGET_TABLE} {idx_def};")
            conn.commit()
            print(f"   ✅ 索引 {idx_name}")
        except Exception as e:
            print(f"   ⚠️  索引 {idx_name} 跳过: {e}")


def process_and_copy_file(conn, csv_path, season):
    """处理单个CSV文件并使用COPY导入"""
    print(f"\n📄 处理 {csv_path.name} (赛季 {season})")
    
    start_time = time.time()
    
    # 读取整个文件（单个文件65MB，pandas可以处理）
    df = pd.read_csv(csv_path)
    
    # 1. 补全 season 字段
    if 'season' not in df.columns:
        df['season'] = season
    
    # 2. 重命名 desc -> description（SQL关键字）
    if 'desc' in df.columns:
        df.rename(columns={'desc': 'description'}, inplace=True)
    
    # 3. type 字段重命名为 event_type（避免冲突）
    if 'type' in df.columns:
        df.rename(columns={'type': 'event_type'}, inplace=True)
    
    # 4. 计算 clock_seconds
    df['clock_seconds'] = df['clock'].apply(parse_clock_to_seconds)
    
    # 5. 计算 eventnum（每个gameid内的事件编号）
    df = df.sort_values(['gameid', 'period', 'clock_seconds'], 
                        ascending=[True, True, False]).reset_index(drop=True)
    df['eventnum'] = df.groupby('gameid').cumcount()
    
    # 6. 处理字段类型
    df['gameid'] = pd.to_numeric(df['gameid'], errors='coerce').fillna(0).astype('int64')
    df['playerid'] = pd.to_numeric(df['playerid'], errors='coerce').fillna(0).astype('int64')
    df['h_pts'] = pd.to_numeric(df['h_pts'], errors='coerce')
    df['a_pts'] = pd.to_numeric(df['a_pts'], errors='coerce')
    df['x'] = pd.to_numeric(df['x'], errors='coerce').fillna(0).astype('Int64')
    df['y'] = pd.to_numeric(df['y'], errors='coerce').fillna(0).astype('Int64')
    df['dist'] = pd.to_numeric(df['dist'], errors='coerce').fillna(0).astype('Int64')
    df['period'] = pd.to_numeric(df['period'], errors='coerce').fillna(0).astype('Int64')
    df['eventnum'] = pd.to_numeric(df['eventnum'], errors='coerce').astype('Int64')
    df['season'] = season
    
    # 7. 输出到临时CSV，使用COPY命令导入
    # 列顺序：season, gameid, eventnum, period, clock, clock_seconds, h_pts, a_pts, 
    #         team, playerid, player, event_type, subtype, result, x, y, dist, description
    cols = ['season', 'gameid', 'eventnum', 'period', 'clock', 'clock_seconds',
            'h_pts', 'a_pts', 'team', 'playerid', 'player', 'event_type',
            'subtype', 'result', 'x', 'y', 'dist', 'description']
    
    # 确保所有需要的列存在
    for c in cols:
        if c not in df.columns:
            df[c] = None
    
    df_out = df[cols]
    
    # 写入临时CSV并使用COPY
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
    try:
        df_out.to_csv(temp_file, index=False, header=False, na_rep='\\N', lineterminator='\n')
        temp_file.close()
        
        cursor = conn.cursor()
        
        # 使用 COPY FROM
        with open(temp_file.name, 'r', encoding='utf-8') as f:
            cursor.copy_from(f, TARGET_TABLE, columns=cols, sep=',', null='\\N')
        
        conn.commit()
        
        elapsed = time.time() - start_time
        print(f"   ✅ 导入 {len(df):,} 行，用时 {elapsed:.1f} 秒, 速度 {len(df)/elapsed:,.0f} 行/秒")
        
    finally:
        os.unlink(temp_file.name)
    
    return len(df)


def import_all_seasons():
    """导入所有赛季的PBP数据"""
    total_start = time.time()
    
    # 确定要导入的赛季（1998到2025，1997已经在pbp_1997表中，但也可以一起导入）
    pbp_files = sorted(CSV_DIR.glob('pbp*.csv'))
    print(f"找到 {len(pbp_files)} 个PBP文件")
    
    # 从文件名提取赛季
    file_season_map = []
    for f in pbp_files:
        season = int(f.name.replace('pbp', '').replace('.csv', ''))
        file_season_map.append((f, season))
    
    file_season_map.sort(key=lambda x: x[1])
    print(f"赛季范围: {file_season_map[0][1]} - {file_season_map[-1][1]}")
    
    # 连接数据库
    conn = psycopg2.connect(**DB_CONFIG)
    
    try:
        # 1. 创建表
        drop_table(conn)
        create_table(conn)
        
        # 2. 逐个导入
        total_rows = 0
        for csv_path, season in file_season_map:
            rows = process_and_copy_file(conn, csv_path, season)
            total_rows += rows
        
        elapsed_total = time.time() - total_start
        
        # 3. 创建索引
        print(f"\n\n{'='*80}")
        print(f"📊 数据导入完成，共 {total_rows:,} 行，用时 {elapsed_total/60:.1f} 分钟")
        print(f"{'='*80}")
        
        print(f"\n🔨 开始创建索引（可能需要几分钟）...")
        idx_start = time.time()
        create_indexes(conn)
        idx_elapsed = time.time() - idx_start
        print(f"\n✅ 索引创建完成，用时 {idx_elapsed/60:.1f} 分钟")
        
        # 4. 统计信息
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {TARGET_TABLE};")
        final_count = cursor.fetchone()[0]
        
        cursor.execute(f"""
            SELECT season, COUNT(*) as cnt
            FROM {TARGET_TABLE}
            GROUP BY season
            ORDER BY season;
        """)
        season_stats = cursor.fetchall()
        
        print(f"\n📋 各赛季数据量:")
        for season, cnt in season_stats:
            print(f"   {season}: {cnt:,} 行")
        
        print(f"\n✅ 总记录数: {final_count:,}")
        
    finally:
        conn.close()


if __name__ == '__main__':
    import_all_seasons()
