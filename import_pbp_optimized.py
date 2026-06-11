#!/usr/bin/env python3
"""优化PBP数据导入
1. 使用chunksize分批导入
2. 添加EVENTNUM作为索引
3. 时间字段转成秒数
4. 添加联合主键
"""
import pandas as pd
import re
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, Index, MetaData

def parse_clock_to_seconds(clock_str):
    """将时钟格式转成秒数
    PT12M00.00S -> 720.0
    11:39.0 -> 699.0
    """
    if pd.isna(clock_str):
        return None
    
    clock_str = str(clock_str)
    
    # 格式1: PT12M00.00S
    if 'PT' in clock_str:
        match = re.match(r'PT(\d+)M(\d+\.?\d*)S', clock_str)
        if match:
            minutes = float(match.group(1))
            seconds = float(match.group(2))
            return minutes * 60 + seconds
    
    # 格式2: 11:39.0
    if ':' in clock_str:
        parts = clock_str.split(':')
        if len(parts) == 2:
            try:
                minutes = float(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
            except:
                pass
    
    return None

def import_1997_data(db_conn, chunksize=10000):
    """导入1997年数据"""
    print("\n" + "=" * 80)
    print("导入1997年PBP数据")
    print("=" * 80)
    
    table_name = 'pbp_1997_optimized'
    
    # 创建表结构
    metadata = MetaData()
    pbp_table = Table(
        table_name,
        metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('gameid', String),
        Column('eventnum', Integer),
        Column('period', Integer),
        Column('clock', String),
        Column('clock_seconds', Float),
        Column('h_pts', Float),
        Column('a_pts', Float),
        Column('team', String),
        Column('playerid', Integer),
        Column('player', String),
        Column('type', String),
        Column('subtype', String),
        Column('result', String),
        Column('x', Float),
        Column('y', Float),
        Column('dist', Float),
        Column('description', String),
        Column('season', Integer),
        Index('idx_game_event', 'gameid', 'eventnum', unique=True)
    )
    
    print("创建数据库表结构...")
    metadata.create_all(db_conn)
    
    total_rows = 0
    for chunk_idx, df in enumerate(pd.read_csv('CSV/pbp1997.csv', chunksize=chunksize)):
        # 处理数据
        df_processed = df.copy()
        
        # 添加eventnum（从行号生成）
        df_processed['eventnum'] = chunk_idx * chunksize + df_processed.index
        
        # 解析时钟
        df_processed['clock_seconds'] = df_processed['clock'].apply(parse_clock_to_seconds)
        
        # 重命名desc列（保留字）
        df_processed.rename(columns={'desc': 'description'}, inplace=True)
        
        # 插入数据
        try:
            df_processed.to_sql(
                table_name,
                db_conn,
                if_exists='append',
                index=False,
                method='multi',
                chunksize=chunksize
            )
            
            inserted = len(df_processed)
            total_rows += inserted
            print(f"批次 {chunk_idx+1}: 成功导入 {inserted} 行（累计 {total_rows} 行）")
        except Exception as e:
            print(f"批次 {chunk_idx+1} 导入失败: {e}")
    
    print(f"\n✅ 1997数据导入完成: 共 {total_rows} 行")
    
    return total_rows

def main():
    print("=" * 80)
    print("PBP数据优化导入工具")
    print("=" * 80)
    
    # 连接数据库
    db_config = {
        'dbname': 'nba',
        'user': 'postgres',
        'password': 'postgres',
        'host': 'localhost',
        'port': '5433'
    }
    
    # 使用SQLAlchemy引擎
    conn_str = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
    engine = create_engine(conn_str)
    print(f"成功连接到数据库")
    
    with engine.connect() as conn:
        with conn.begin():
            # 导入1997数据
            total_1997 = import_1997_data(conn)
    
    print("\n" + "=" * 80)
    print("✅ 全部导入完成！")
    print(f"  1997数据: {total_1997} 行")
    print("=" * 80)

if __name__ == "__main__":
    main()
