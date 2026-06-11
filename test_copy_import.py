#!/usr/bin/env python3
"""测试 COPY 命令导入 - 使用正确的空值处理"""
import pandas as pd
import psycopg2
import re
import time
import io
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
    
    df = pd.read_csv(csv_path, nrows=5000)  # 只用前5000行测试
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
    
    print(f"h_pts 空值数量: {df['h_pts'].isna().sum()}")
    print(f"team 空值数量: {df['team'].isna().sum()}")
    
    # 方法测试: 使用 copy_expert, 明确用 \N 表示NULL
    print("\n方法: COPY WITH CSV + NULL '\\N'")
    buffer = io.StringIO()
    
    # 关键: 使用 \N 作为NULL, 用csv标准引号处理含逗号字段
    # 注意: 在CSV格式中, NULL 必须是 未加引号 的 \N 才能被识别
    df.to_csv(buffer, index=False, header=False,
              sep=',', quotechar='"', quoting=0,  # quoting=0: 最小化引号,只有需要时才加
              na_rep='\\N', escapechar='\\', lineterminator='\n')
    
    # 查看样本
    buffer.seek(0)
    lines = buffer.readlines()
    print(f"\n样本行 (前3行):")
    for l in lines[:3]:
        print(f"  {l[:200]}")
    
    # 实际测试导入
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 测试表
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
    
    buffer.seek(0)
    start = time.time()
    
    copy_sql = """
        COPY pbp_test_copy (season, gameid, eventnum, period, clock, clock_seconds,
            h_pts, a_pts, team, playerid, player, event_type, subtype, result,
            x, y, dist, description)
        FROM STDIN WITH (FORMAT CSV, DELIMITER ',', QUOTE '"', ESCAPE '\\', NULL '\\N')
    """
    cursor.copy_expert(copy_sql, buffer)
    conn.commit()
    
    elapsed = time.time() - start
    cursor.execute("SELECT COUNT(*) FROM pbp_test_copy;")
    count = cursor.fetchone()[0]
    
    print(f"\n✅ 导入成功: {count} 行, {elapsed:.2f} 秒, {count/elapsed:,.0f} 行/秒")
    
    # 验证数据质量
    cursor.execute("SELECT COUNT(*) FROM pbp_test_copy WHERE h_pts IS NULL;")
    null_hpts = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pbp_test_copy WHERE team IS NULL;")
    null_team = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pbp_test_copy WHERE description IS NULL;")
    null_desc = cursor.fetchone()[0]
    
    print(f"\n数据质量检查:")
    print(f"  h_pts 为NULL: {null_hpts}")
    print(f"  team 为NULL: {null_team}")
    print(f"  description 为NULL: {null_desc}")
    
    cursor.execute("DROP TABLE IF EXISTS pbp_test_copy;")
    conn.commit()
    conn.close()
    print("\n测试完成,测试表已删除")


if __name__ == '__main__':
    main()
