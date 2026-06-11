#!/usr/bin/env python3
"""批量导入1997-2026年PBP数据 - 最终版
使用 TAB 分隔 + COPY 命令，速度快且可靠
"""
import pandas as pd
import psycopg2
import re
import time
import io
import numpy as np
from pathlib import Path
import sys

DB_CONFIG = {
    'dbname': 'nba',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5433'
}

CSV_DIR = Path('CSV')
TARGET_TABLE = 'pbp_all'

COLS = ['season', 'gameid', 'eventnum', 'period', 'clock', 'clock_seconds',
        'h_pts', 'a_pts', 'team', 'playerid', 'player', 'event_type',
        'subtype', 'result', 'x', 'y', 'dist', 'description']

TEXT_COLS = {'clock', 'team', 'player', 'event_type', 'subtype', 'result', 'description'}


def parse_clock_to_seconds(clock_str):
    if pd.isna(clock_str) or not isinstance(clock_str, str):
        return None
    match = re.match(r'PT(\d+)M(\d+(?:\.\d+)?)S', clock_str)
    if match:
        return float(match.group(1)) * 60 + float(match.group(2))
    match2 = re.match(r'(\d+):(\d+(?:\.\d+)?)', str(clock_str))
    if match2:
        return float(match2.group(1)) * 60 + float(match2.group(2))
    return None


def fmt(val, col_name):
    """格式化值为 COPY 格式"""
    if pd.isna(val):
        return r'\N'
    # 文本字段: 替换 TAB、换行符
    if col_name in TEXT_COLS:
        s = str(val)
        s = s.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
        return s
    return str(val)


def process_file(csv_path, season):
    """读取并处理单个CSV文件, 返回 TAB 分隔的字符串"""
    df = pd.read_csv(csv_path)
    
    # 字段处理
    if 'season' not in df.columns:
        df['season'] = season
    df['season'] = season
    
    if 'desc' in df.columns:
        df.rename(columns={'desc': 'description'}, inplace=True)
    if 'type' in df.columns:
        df.rename(columns={'type': 'event_type'}, inplace=True)
    
    df['clock_seconds'] = df['clock'].apply(parse_clock_to_seconds)
    df = df.sort_values(['gameid', 'period', 'clock_seconds'],
                       ascending=[True, True, False]).reset_index(drop=True)
    df['eventnum'] = df.groupby('gameid').cumcount()
    
    df['gameid'] = pd.to_numeric(df['gameid'], errors='coerce').fillna(0).astype(np.int64)
    df['playerid'] = pd.to_numeric(df['playerid'], errors='coerce').fillna(0).astype(np.int64)
    df['h_pts'] = pd.to_numeric(df['h_pts'], errors='coerce')
    df['a_pts'] = pd.to_numeric(df['a_pts'], errors='coerce')
    df['x'] = pd.to_numeric(df['x'], errors='coerce').fillna(0).astype(np.int64)
    df['y'] = pd.to_numeric(df['y'], errors='coerce').fillna(0).astype(np.int64)
    df['dist'] = pd.to_numeric(df['dist'], errors='coerce').fillna(0).astype(np.int64)
    df['period'] = pd.to_numeric(df['period'], errors='coerce').fillna(0).astype(np.int64)
    
    for c in COLS:
        if c not in df.columns:
            df[c] = None
    df = df[COLS]
    
    # 生成 TAB 分隔的文本 (用列表推导加速)
    lines = []
    for row in df.itertuples(index=False, name=None):
        line_fields = [fmt(row[i], COLS[i]) for i in range(len(COLS))]
        lines.append('\t'.join(line_fields))
    
    return '\n'.join(lines) + '\n', len(df)


def main():
    total_start = time.time()
    
    pbp_files = sorted(CSV_DIR.glob('pbp*.csv'))
    file_season_map = []
    for f in pbp_files:
        season = int(f.name.replace('pbp', '').replace('.csv', ''))
        file_season_map.append((f, season))
    file_season_map.sort(key=lambda x: x[1])
    
    print(f"找到 {len(file_season_map)} 个PBP文件: {file_season_map[0][1]}-{file_season_map[-1][1]}")
    
    # 创建表
    conn = psycopg2.connect(**DB_CONFIG)
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
    
    total_rows = 0
    for i, (csv_path, season) in enumerate(file_season_map):
        file_start = time.time()
        print(f"[{i+1}/{len(file_season_map)}] 📄 {csv_path.name} (赛季 {season})", flush=True)
        
        data_str, rows = process_file(csv_path, season)
        process_time = time.time() - file_start
        
        buffer = io.StringIO(data_str)
        copy_start = time.time()
        cursor.copy_from(buffer, TARGET_TABLE, sep='\t', null='\\N', columns=COLS)
        conn.commit()
        copy_time = time.time() - copy_start
        
        total_rows += rows
        elapsed = time.time() - file_start
        print(f"   ✅ {rows:>8,} 行 | 处理 {process_time:>5.1f}s | COPY {copy_time:>5.1f}s | 总计 {elapsed:>6.1f}s", flush=True)
    
    elapsed_total = time.time() - total_start
    print(f"\n{'='*80}")
    print(f"📊 数据导入完成: {total_rows:,} 行, 用时 {elapsed_total/60:.1f} 分钟")
    print(f"{'='*80}")
    
    # 创建索引
    print("\n🔨 创建索引...", flush=True)
    idx_start = time.time()
    index_defs = [
        (f"idx_{TARGET_TABLE}_season_game_event", "(season, gameid, eventnum)"),
        (f"idx_{TARGET_TABLE}_season", "(season)"),
        (f"idx_{TARGET_TABLE}_gameid", "(gameid)"),
        (f"idx_{TARGET_TABLE}_playerid", "(playerid)"),
        (f"idx_{TARGET_TABLE}_team", "(team)"),
        (f"idx_{TARGET_TABLE}_event_type", "(event_type)"),
    ]
    for name, definition in index_defs:
        try:
            t0 = time.time()
            cursor.execute(f"CREATE INDEX {name} ON {TARGET_TABLE} {definition};")
            conn.commit()
            print(f"   ✅ {name} ({time.time()-t0:.1f}s)")
        except Exception as e:
            print(f"   ⚠️  {name}: {e}")
    
    idx_elapsed = time.time() - idx_start
    print(f"✅ 索引创建完成 ({idx_elapsed/60:.1f} 分钟)")
    
    # 统计
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
    
    total_elapsed = time.time() - total_start
    print(f"\n⏱️  总计用时: {total_elapsed/60:.1f} 分钟")
    
    conn.close()


if __name__ == '__main__':
    main()
