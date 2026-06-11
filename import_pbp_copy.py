#!/usr/bin/env python3
"""使用PostgreSQL COPY命令优化导入PBP数据
这个方法比逐行INSERT快得多
"""
import pandas as pd
import re
import psycopg2
from pathlib import Path
import tempfile
import csv

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

def create_table_sql():
    """返回建表SQL语句"""
    return """
    CREATE TABLE IF NOT EXISTS pbp_1997_copy (
        id SERIAL PRIMARY KEY,
        gameid VARCHAR,
        eventnum INTEGER,
        period INTEGER,
        clock VARCHAR,
        clock_seconds FLOAT,
        h_pts FLOAT,
        a_pts FLOAT,
        team VARCHAR,
        playerid INTEGER,
        player VARCHAR,
        type VARCHAR,
        subtype VARCHAR,
        result VARCHAR,
        x FLOAT,
        y FLOAT,
        dist FLOAT,
        description VARCHAR,
        season INTEGER
    );
    
    -- 创建联合索引
    CREATE UNIQUE INDEX IF NOT EXISTS idx_pbp_1997_game_event 
    ON pbp_1997_copy (gameid, eventnum);
    """

def import_with_copy(db_config):
    """使用COPY命令快速导入数据"""
    print("\n" + "=" * 80)
    print("使用COPY命令快速导入1997年PBP数据")
    print("=" * 80)
    
    # 读取和处理数据
    print("\n步骤1: 读取和预处理CSV...")
    df = pd.read_csv('CSV/pbp1997.csv')
    print(f"  读取 {len(df)} 行数据")
    
    # 处理数据
    df_processed = df.copy()
    
    # 添加eventnum
    df_processed['eventnum'] = range(len(df_processed))
    
    # 解析时钟
    print("\n步骤2: 转换时间字段...")
    df_processed['clock_seconds'] = df_processed['clock'].apply(parse_clock_to_seconds)
    
    # 重命名desc列
    df_processed.rename(columns={'desc': 'description'}, inplace=True)
    
    # 确保列顺序正确
    column_order = [
        'gameid', 'eventnum', 'period', 'clock', 'clock_seconds',
        'h_pts', 'a_pts', 'team', 'playerid', 'player',
        'type', 'subtype', 'result', 'x', 'y', 'dist',
        'description', 'season'
    ]
    df_processed = df_processed[column_order]
    
    # 连接数据库
    print("\n步骤3: 连接数据库...")
    conn = psycopg2.connect(**db_config)
    conn.autocommit = True
    
    try:
        # 创建表
        print("  创建表结构...")
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS pbp_1997_copy;")
        cursor.execute(create_table_sql())
        conn.commit()
        
        # 使用COPY导入
        print("\n步骤4: 使用COPY命令导入数据...")
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
            temp_path = Path(f.name)
            
            # 写CSV，不带表头（COPY会处理）
            df_processed.to_csv(f, index=False, header=False, na_rep='\\N')
            
        print(f"  临时文件: {temp_path}")
        
        # COPY命令
        copy_sql = """
        COPY pbp_1997_copy (
            gameid, eventnum, period, clock, clock_seconds,
            h_pts, a_pts, team, playerid, player,
            type, subtype, result, x, y, dist,
            description, season
        )
        FROM %s
        WITH (
            FORMAT CSV,
            DELIMITER ',',
            NULL '\\N',
            ENCODING 'UTF8'
        );
        """
        
        print("  执行COPY命令...")
        cursor.execute(copy_sql, (str(temp_path),))
        conn.commit()
        
        # 查询结果
        cursor.execute("SELECT COUNT(*) FROM pbp_1997_copy;")
        count = cursor.fetchone()[0]
        
        print("\n" + "=" * 80)
        print(f"✅ COPY导入成功！共 {count} 行数据")
        print("=" * 80)
        
        # 删除临时文件
        temp_path.unlink()
        
    finally:
        conn.close()
    
    return count

def main():
    db_config = {
        'dbname': 'nba',
        'user': 'postgres',
        'password': 'postgres',
        'host': 'localhost',
        'port': '5433'
    }
    
    import_with_copy(db_config)

if __name__ == "__main__":
    main()
