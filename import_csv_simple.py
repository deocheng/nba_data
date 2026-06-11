#!/usr/bin/env python3
"""
分析和导入 CSV 文件到数据库
直接使用 psycopg2 和 pandas，避免相对导入问题
"""
import sys
import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path

BASE_DIR = Path(__file__).parent
CSV_DIR = BASE_DIR / "CSV"

def get_db_connection():
    """获取数据库连接"""
    conn = psycopg2.connect(
        host="localhost",
        port="5433",
        database="nba",
        user="postgres",
        password="postgres"
    )
    return conn

def analyze_csv(file_path):
    """分析 CSV 文件结构"""
    print(f"\n{'='*80}")
    print(f"分析文件: {file_path.name}")
    print(f"{'='*80}")
    
    df = pd.read_csv(file_path, nrows=100)
    print(f"\n总行数: {len(df)}")
    print(f"\n列名:")
    for i, col in enumerate(df.columns):
        print(f"  {i+1:2d}. {col} (类型: {df[col].dtype})")
    
    print(f"\n前3行数据预览:")
    print(df.head(3).to_string())
    
    print(f"\n数据类型统计:")
    print(df.dtypes)
    
    print(f"\n缺失值统计:")
    print(df.isnull().sum())
    
    return df

def create_table_from_df(conn, df, table_name):
    """根据 DataFrame 创建表"""
    print(f"\n创建表: {table_name}")
    
    # 生成 SQL 建表语句
    type_mapping = {
        'int64': 'INTEGER',
        'float64': 'DOUBLE PRECISION',
        'object': 'TEXT',
        'bool': 'BOOLEAN'
    }
    
    columns = []
    col_mapping = []
    for col in df.columns:
        col_type = type_mapping.get(str(df[col].dtype), 'TEXT')
        # 处理列名中的特殊字符
        col_name = col.replace('%', 'percent').replace(' ', '_').replace('/', '_').replace('-', '_').replace('.', '_').lower()
        # 特殊处理 3PAr
        if '3par' in col_name:
            col_name = 'threep_ar'
        # 特殊处理保留字
        if col_name == 'desc':
            col_name = 'description'
        columns.append(f'"{col_name}" {col_type}')
        col_mapping.append((col, col_name))
    
    create_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n    ' + ',\n    '.join(columns) + '\n)'
    print(create_sql)
    
    cursor = conn.cursor()
    cursor.execute(create_sql)
    conn.commit()
    
    return col_mapping

def import_csv_to_db(conn, file_path, table_name):
    """导入 CSV 到数据库"""
    print(f"\n{'='*80}")
    print(f"导入文件: {file_path.name} -> {table_name}")
    print(f"{'='*80}")
    
    # 读取 CSV
    df = pd.read_csv(file_path)
    
    # 先删除可能存在的表
    cursor = conn.cursor()
    try:
        cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')
        conn.commit()
    except:
        pass
    
    # 创建表
    col_mapping = create_table_from_df(conn, df.head(100), table_name)
    col_names = [x[1] for x in col_mapping]
    
    # 准备插入数据
    total_rows = len(df)
    inserted = 0
    
    for _, row in df.iterrows():
        # 为每一行构建 insert 语句
        placeholders = ', '.join(['%s'] * len(col_mapping))
        insert_sql = f'INSERT INTO "{table_name}" ({", ".join([f"{col}" for col in col_names])}) VALUES ({placeholders})'
        
        row_values = []
        for orig_col, _ in col_mapping:
            val = row[orig_col]
            if pd.isna(val):
                row_values.append(None)
            else:
                if isinstance(val, float) and val.is_integer():
                    row_values.append(int(val))
                else:
                    row_values.append(val)
        
        cursor.execute(insert_sql, row_values)
        inserted += 1
        
        if inserted % 100 == 0:
            conn.commit()
            print(f"已导入: {inserted}/{total_rows} 行")
    
    conn.commit()
    print(f"已导入: {inserted}/{total_rows} 行")
    print(f"\n✅ 成功导入 {inserted} 行数据到 {table_name}")
    return inserted

def main():
    conn = get_db_connection()
    
    files = [
        # (CSV_DIR / "advanced_stats.csv", "advanced_stats"),
        # (CSV_DIR / "Advanced.csv", "advanced_2026"),
        (CSV_DIR / "pbp1997.csv", "pbp_1997")
    ]
    
    for file_path, table_name in files:
        if file_path.exists():
            analyze_csv(file_path)
            import_csv_to_db(conn, file_path, table_name)
        else:
            print(f"⚠️ 文件不存在: {file_path}")
    
    # 验证导入
    print(f"\n{'='*80}")
    print("验证导入结果")
    print(f"{'='*80}")
    cursor = conn.cursor()
    all_files = [
        (CSV_DIR / "advanced_stats.csv", "advanced_stats"),
        (CSV_DIR / "Advanced.csv", "advanced_2026"),
        (CSV_DIR / "pbp1997.csv", "pbp_1997")
    ]
    for _, table_name in all_files:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
            count = cursor.fetchone()[0]
            print(f"{table_name}: {count} 行")
        except Exception as e:
            print(f"{table_name}: 查询失败 - {e}")
    
    conn.close()
    
    print("\n" + "="*80)
    print("✅ 所有文件处理完成")
    print("="*80)

if __name__ == "__main__":
    main()
