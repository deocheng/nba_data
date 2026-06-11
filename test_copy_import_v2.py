#!/usr/bin/env python3
"""快速测试: 使用 TAB 分隔的 TEXT 格式 COPY"""
import pandas as pd
import psycopg2
import re
import time
import io
import csv
import numpy as np
from pathlib import Path

DB_CONFIG = {
    'dbname': 'nba',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5433'
}

CSV_DIR = Path('CSV')


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


def main():
    csv_path = CSV_DIR / 'pbp1997.csv'
    print(f"测试 {csv_path.name}")
    
    df = pd.read_csv(csv_path, nrows=5000)
    print(f"读取 {len(df)} 行")
    
    # 数据处理
    if 'season' not in df.columns:
        df['season'] = 1997
    df['season'] = 1997
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
    
    cols = ['season', 'gameid', 'eventnum', 'period', 'clock', 'clock_seconds',
            'h_pts', 'a_pts', 'team', 'playerid', 'player', 'event_type',
            'subtype', 'result', 'x', 'y', 'dist', 'description']
    for c in cols:
        if c not in df.columns:
            df[c] = None
    df = df[cols]
    
    # 关键: 使用 TAB 分隔, \N 作为 NULL, 手动替换 description 中的 tab 和换行
    print("\n使用 TAB 分隔 + \\N 作为 NULL")
    
    # 将数据转换为适合 COPY 的格式
    def format_value(val, col_name):
        if pd.isna(val):
            return '\\N'
        s = str(val)
        # 替换 description 等文本字段中的 TAB 和换行符
        if col_name in ['description', 'player', 'subtype', 'event_type', 'result', 'team', 'clock']:
            s = s.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
        return s
    
    lines = []
    for _, row in df.iterrows():
        line_fields = [format_value(row[col], col) for col in cols]
        lines.append('\t'.join(line_fields))
    
    buffer_content = '\n'.join(lines) + '\n'
    
    # 查看样本
    sample_lines = buffer_content.split('\n')[:3]
    print(f"样本行 (前3行, 截断到300字符):")
    for l in sample_lines:
        print(f"  {l[:300]}")
    
    # 实际导入测试
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS pbp_test_copy;")
    cursor.execute("""
        CREATE TABLE pbp_test_copy (
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
    
    buffer = io.StringIO(buffer_content)
    start = time.time()
    
    # 使用 copy_from (TEXT 格式, TAB 分隔)
    cursor.copy_from(buffer, 'pbp_test_copy', sep='\t', null='\\N', columns=cols)
    conn.commit()
    
    elapsed = time.time() - start
    cursor.execute("SELECT COUNT(*) FROM pbp_test_copy;")
    count = cursor.fetchone()[0]
    
    print(f"\n✅ 导入成功: {count} 行, {elapsed:.2f} 秒, {count/elapsed:,.0f} 行/秒")
    
    cursor.execute("SELECT COUNT(*) FROM pbp_test_copy WHERE h_pts IS NULL;")
    print(f"  h_pts NULL: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM pbp_test_copy WHERE team IS NULL;")
    print(f"  team NULL: {cursor.fetchone()[0]}")
    
    cursor.execute("DROP TABLE IF EXISTS pbp_test_copy;")
    conn.commit()
    conn.close()
    print("\n测试完成")


if __name__ == '__main__':
    main()
