#!/usr/bin/env python3
"""批量导入1997-2026年PBP数据 - 可靠版
使用 pandas + SQLAlchemy to_sql，自动处理引号/空值等问题
"""
import pandas as pd
import re
import time
import sys
from pathlib import Path
from sqlalchemy import create_engine

DB_URL = 'postgresql://postgres:postgres@localhost:5433/nba'
CSV_DIR = Path('CSV')
TARGET_TABLE = 'pbp_all'
CHUNKSIZE = 50000  # 每批插入行数


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
    total_start = time.time()
    engine = create_engine(DB_URL)
    
    pbp_files = sorted(CSV_DIR.glob('pbp*.csv'))
    print(f"找到 {len(pbp_files)} 个PBP文件")
    
    file_season_map = []
    for f in pbp_files:
        season = int(f.name.replace('pbp', '').replace('.csv', ''))
        file_season_map.append((f, season))
    file_season_map.sort(key=lambda x: x[1])
    print(f"赛季范围: {file_season_map[0][1]} - {file_season_map[-1][1]}")
    
    # 删除旧表
    with engine.connect() as conn:
        conn.exec_driver_sql(f"DROP TABLE IF EXISTS {TARGET_TABLE};")
        conn.commit()
    print(f"✅ 旧表已删除")
    
    total_rows = 0
    
    for i, (csv_path, season) in enumerate(file_season_map):
        file_start = time.time()
        print(f"\n[{i+1}/{len(file_season_map)}] 📄 {csv_path.name} (赛季 {season})", flush=True)
        
        df = pd.read_csv(csv_path)
        file_rows = len(df)
        
        # 数据处理
        if 'season' not in df.columns:
            df['season'] = season
        df['season'] = season
        
        if 'desc' in df.columns:
            df.rename(columns={'desc': 'description'}, inplace=True)
        
        if 'type' in df.columns:
            df.rename(columns={'type': 'event_type'}, inplace=True)
        
        df['clock_seconds'] = df['clock'].apply(parse_clock_to_seconds)
        
        # eventnum 计算
        df = df.sort_values(['gameid', 'period', 'clock_seconds'],
                           ascending=[True, True, False]).reset_index(drop=True)
        df['eventnum'] = df.groupby('gameid').cumcount()
        
        # 字段类型
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
        
        # 列顺序
        cols = ['season', 'gameid', 'eventnum', 'period', 'clock', 'clock_seconds',
                'h_pts', 'a_pts', 'team', 'playerid', 'player', 'event_type',
                'subtype', 'result', 'x', 'y', 'dist', 'description']
        for c in cols:
            if c not in df.columns:
                df[c] = None
        df = df[cols]
        
        # 写入数据库
        if_exists = 'append' if total_rows > 0 else 'replace'
        df.to_sql(TARGET_TABLE, engine, if_exists='append', index=False, 
                  chunksize=CHUNKSIZE, method='multi')
        
        elapsed = time.time() - file_start
        total_rows += file_rows
        print(f"   ✅ {file_rows:,} 行, {elapsed:.1f} 秒, {file_rows/elapsed:,.0f} 行/秒", flush=True)
    
    elapsed_total = time.time() - total_start
    print(f"\n{'='*80}")
    print(f"📊 数据导入完成: {total_rows:,} 行, {elapsed_total/60:.1f} 分钟")
    print(f"{'='*80}")
    
    # 创建索引
    print("\n🔨 创建索引...", flush=True)
    idx_start = time.time()
    with engine.connect() as conn:
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
                conn.exec_driver_sql(f"CREATE INDEX {name} ON {TARGET_TABLE} {definition};")
                conn.commit()
                print(f"   ✅ {name}")
            except Exception as e:
                print(f"   ⚠️  {name}: {e}")
    
    idx_elapsed = time.time() - idx_start
    print(f"✅ 索引完成 ({idx_elapsed/60:.1f} 分钟)")
    
    # 统计
    with engine.connect() as conn:
        result = conn.execute(f"SELECT COUNT(*) FROM {TARGET_TABLE}")
        final_count = result.scalar()
        print(f"\n✅ 总记录数: {final_count:,}")
        
        result2 = conn.execute(f"""
            SELECT season, COUNT(*) as cnt
            FROM {TARGET_TABLE}
            GROUP BY season ORDER BY season
        """)
        print(f"\n📋 各赛季数据量:")
        for season, cnt in result2.fetchall():
            print(f"   {season}: {cnt:,} 行")
    
    total_elapsed = time.time() - total_start
    print(f"\n⏱️  总计用时: {total_elapsed/60:.1f} 分钟")


if __name__ == '__main__':
    main()
