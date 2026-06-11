#!/usr/bin/env python3
"""批量导入1997-2026年PBP数据 - 改进版
使用 COPY WITH CSV 格式正确处理含有逗号的字段
"""
import pandas as pd
import psycopg2
import psycopg2.extras
import re
import time
import tempfile
import os
from pathlib import Path

DB_CONFIG = {
    'dbname': 'nba',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5433'
}

CSV_DIR = Path('CSV')
TARGET_TABLE = 'pbp_all'


def parse_clock_to_seconds(clock_str):
    """将 PT12M00.00S 格式转换为秒数"""
    if pd.isna(clock_str) or not isinstance(clock_str, str):
        return None
    match = re.match(r'PT(\d+)M(\d+(?:\.\d+)?)S', clock_str)
    if match:
        return float(match.group(1)) * 60 + float(match.group(2))
    match2 = re.match(r'(\d+):(\d+(?:\.\d+)?)', str(clock_str))
    if match2:
        return float(match2.group(1)) * 60 + float(match2.group(2))
    return None


def create_table(conn):
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {TARGET_TABLE};")
    cursor.execute(f"""
        CREATE TABLE {TARGET_TABLE} (
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
    print(f"✅ 表 {TARGET_TABLE} 已创建")


def create_indexes(conn):
    cursor = conn.cursor()
    print("\n🔨 创建索引中...")
    indexes = [
        (f"idx_{TARGET_TABLE}_season_game_event", f"(season, gameid, eventnum)"),
        (f"idx_{TARGET_TABLE}_season", f"(season)"),
        (f"idx_{TARGET_TABLE}_gameid", f"(gameid)"),
        (f"idx_{TARGET_TABLE}_playerid", f"(playerid)"),
        (f"idx_{TARGET_TABLE}_team", f"(team)"),
        (f"idx_{TARGET_TABLE}_event_type", f"(event_type)"),
    ]
    for name, definition in indexes:
        cursor.execute(f"CREATE INDEX {name} ON {TARGET_TABLE} {definition};")
        conn.commit()
        print(f"   ✅ {name}")


def process_and_copy_file(conn, csv_path, season):
    """处理单个CSV文件并使用 COPY 导入"""
    print(f"📄 处理 {csv_path.name} (赛季 {season})", flush=True)
    start_time = time.time()
    
    # 读取CSV
    df = pd.read_csv(csv_path)
    
    # 1. 补全 season 字段
    if 'season' not in df.columns:
        df['season'] = season
    df['season'] = season
    
    # 2. 重命名 desc -> description
    if 'desc' in df.columns:
        df.rename(columns={'desc': 'description'}, inplace=True)
    
    # 3. type -> event_type
    if 'type' in df.columns:
        df.rename(columns={'type': 'event_type'}, inplace=True)
    
    # 4. 转换时间
    df['clock_seconds'] = df['clock'].apply(parse_clock_to_seconds)
    
    # 5. 计算 eventnum (每个 gameid 内的事件编号)
    df = df.sort_values(['gameid', 'period', 'clock_seconds'],
                       ascending=[True, True, False]).reset_index(drop=True)
    df['eventnum'] = df.groupby('gameid').cumcount()
    
    # 6. 字段类型处理
    import numpy as np
    df['gameid'] = pd.to_numeric(df['gameid'], errors='coerce').fillna(0).astype(np.int64)
    df['playerid'] = pd.to_numeric(df['playerid'], errors='coerce').fillna(0).astype(np.int64)
    df['h_pts'] = pd.to_numeric(df['h_pts'], errors='coerce')
    df['a_pts'] = pd.to_numeric(df['a_pts'], errors='coerce')
    df['x'] = pd.to_numeric(df['x'], errors='coerce').fillna(0).astype(np.int64)
    df['y'] = pd.to_numeric(df['y'], errors='coerce').fillna(0).astype(np.int64)
    df['dist'] = pd.to_numeric(df['dist'], errors='coerce').fillna(0).astype(np.int64)
    df['period'] = pd.to_numeric(df['period'], errors='coerce').fillna(0).astype(np.int64)
    df['eventnum'] = pd.to_numeric(df['eventnum'], errors='coerce').astype(np.int64)
    
    # 7. 输出列
    cols = ['season', 'gameid', 'eventnum', 'period', 'clock', 'clock_seconds',
            'h_pts', 'a_pts', 'team', 'playerid', 'player', 'event_type',
            'subtype', 'result', 'x', 'y', 'dist', 'description']
    
    for c in cols:
        if c not in df.columns:
            df[c] = None
    
    df_out = df[cols]
    
    # 8. 使用 COPY WITH CSV - 通过 StringIO 直接传给数据库
    import io
    
    cursor = conn.cursor()
    
    # 方法: 使用 copy_expert + StringIO, CSV格式带引号
    buffer = io.StringIO()
    df_out.to_csv(buffer, index=False, header=False, 
                  quoting=1,  # QUOTE_ALL - 所有字段加引号，确保逗号等特殊字符处理
                  quotechar='"', escapechar='\\', lineterminator='\n',
                  na_rep='')
    buffer.seek(0)
    
    # 使用 COPY FROM STDIN WITH CSV
    copy_sql = f"""
        COPY {TARGET_TABLE} (season, gameid, eventnum, period, clock, clock_seconds,
            h_pts, a_pts, team, playerid, player, event_type, subtype, result,
            x, y, dist, description)
        FROM STDIN WITH (FORMAT CSV, QUOTE '"', ESCAPE '\\')
    """
    
    cursor.copy_expert(copy_sql, buffer)
    conn.commit()
    
    elapsed = time.time() - start_time
    print(f"   ✅ 导入 {len(df):,} 行，用时 {elapsed:.1f} 秒 ({len(df)/elapsed:,.0f} 行/秒)", flush=True)
    
    return len(df)


def import_all_seasons():
    total_start = time.time()
    
    pbp_files = sorted(CSV_DIR.glob('pbp*.csv'))
    print(f"找到 {len(pbp_files)} 个PBP文件")
    
    file_season_map = []
    for f in pbp_files:
        season = int(f.name.replace('pbp', '').replace('.csv', ''))
        file_season_map.append((f, season))
    
    file_season_map.sort(key=lambda x: x[1])
    print(f"赛季范围: {file_season_map[0][1]} - {file_season_map[-1][1]}")
    
    conn = psycopg2.connect(**DB_CONFIG)
    
    try:
        create_table(conn)
        
        total_rows = 0
        for csv_path, season in file_season_map:
            rows = process_and_copy_file(conn, csv_path, season)
            total_rows += rows
        
        elapsed_total = time.time() - total_start
        
        print(f"\n{'='*80}")
        print(f"📊 数据导入完成，共 {total_rows:,} 行，用时 {elapsed_total/60:.1f} 分钟")
        print(f"{'='*80}")
        
        print(f"\n🔨 创建索引...")
        idx_start = time.time()
        create_indexes(conn)
        idx_elapsed = time.time() - idx_start
        print(f"✅ 索引创建完成 ({idx_elapsed/60:.1f} 分钟)")
        
        # 统计
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {TARGET_TABLE};")
        final_count = cursor.fetchone()[0]
        
        cursor.execute(f"""
            SELECT season, COUNT(*) as cnt
            FROM {TARGET_TABLE}
            GROUP BY season ORDER BY season;
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
