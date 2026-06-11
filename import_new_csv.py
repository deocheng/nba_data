#!/usr/bin/env python3
"""
分析和导入 CSV 文件到数据库
支持 advanced_stats.csv, Advanced.csv, pbp1997.csv
"""
import sys
import importlib.util

# 使用 importlib 导入模块
spec_db = importlib.util.spec_from_file_location("database", "data_importer/database.py")
database = importlib.util.module_from_spec(spec_db)
spec_db.loader.exec_module(database)

import pandas as pd
import numpy as np
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
CSV_DIR = BASE_DIR / "CSV"

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
    
    print(f"\n前5行数据预览:")
    print(df.head())
    
    print(f"\n数据类型统计:")
    print(df.dtypes)
    
    print(f"\n缺失值统计:")
    print(df.isnull().sum())
    
    return df

def create_table_from_df(db, df, table_name):
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
    for col in df.columns:
        col_type = type_mapping.get(str(df[col].dtype), 'TEXT')
        # 处理列名中的特殊字符
        col_name = col.replace('%', 'percent').replace(' ', '_').replace('/', '_').replace('-', '_').replace('3PAr', 'threep_ar').replace('.', '_').lower()
        columns.append(f'"{col_name}" {col_type}')
    
    create_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n    ' + ',\n    '.join(columns) + '\n)'
    print(create_sql)
    
    db.execute(create_sql)
    db.commit()
    
    return [col.replace('%', 'percent').replace(' ', '_').replace('/', '_').replace('-', '_').replace('3PAr', 'threep_ar').replace('.', '_').lower() for col in df.columns]

def import_csv_to_db(db, file_path, table_name):
    """导入 CSV 到数据库"""
    print(f"\n{'='*80}")
    print(f"导入文件: {file_path.name} -> {table_name}")
    print(f"{'='*80}")
    
    # 读取 CSV
    df = pd.read_csv(file_path)
    
    # 先删除可能存在的表
    try:
        db.execute(f'DROP TABLE IF EXISTS "{table_name}"')
        db.commit()
    except:
        pass
    
    # 创建表
    col_mapping = create_table_from_df(db, df.head(100), table_name)
    
    # 准备插入数据
    total_rows = len(df)
    batch_size = 1000
    inserted = 0
    
    for i in range(0, total_rows, batch_size):
        batch = df.iloc[i:i+batch_size]
        
        placeholders = ', '.join(['%s'] * len(col_mapping))
        insert_sql = f'INSERT INTO "{table_name}" ({", ".join([f"{col}" for col in col_mapping])}) VALUES ({placeholders})'
        
        values = []
        for _, row in batch.iterrows():
            row_values = []
            for col in df.columns:
                val = row[col]
                if pd.isna(val):
                    row_values.append(None)
                else:
                    if isinstance(val, float) and val.is_integer():
                        row_values.append(int(val))
                    else:
                        row_values.append(val)
            values.append(tuple(row_values))
        
        db.executemany(insert_sql, values)
        db.commit()
        
        inserted += len(batch)
        print(f"已导入: {inserted}/{total_rows} 行")
    
    print(f"\n✅ 成功导入 {inserted} 行数据到 {table_name}")
    return inserted

def main():
    db = database.DatabaseManager()
    db.connect()
    
    files = [
        (CSV_DIR / "advanced_stats.csv", "advanced_stats"),
        (CSV_DIR / "Advanced.csv", "advanced_2026"),
        (CSV_DIR / "pbp1997.csv", "pbp_1997")
    ]
    
    for file_path, table_name in files:
        if file_path.exists():
            analyze_csv(file_path)
            import_csv_to_db(db, file_path, table_name)
        else:
            print(f"⚠️ 文件不存在: {file_path}")
    
    db.close()
    
    print("\n" + "="*80)
    print("✅ 所有文件处理完成")
    print("="*80)

if __name__ == "__main__":
    main()
