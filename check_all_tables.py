#!/usr/bin/env python3
"""检查所有包含NBA数据的表"""
import psycopg2
from psycopg2 import sql

conn = psycopg2.connect(dbname='nba', user='postgres', password='postgres', host='localhost', port='5433')
cursor = conn.cursor()

print("=" * 70)
print("🔍 检查所有包含赛季数据的表")
print("=" * 70)

# 获取所有表
cursor.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name LIKE '%pbp%' OR table_name LIKE '%play%' OR table_name LIKE '%game%';
""")

tables = [row[0] for row in cursor.fetchall()]

print(f"\n找到 {len(tables)} 个相关表:")
for table in tables:
    print(f"  - {table}")

# 检查每个表的赛季范围
print("\n📊 各表数据统计:")
print("-" * 70)
print("{:<25} {:<12} {:<15} {:<10}".format("表名", "记录数", "赛季范围", "备注"))
print("-" * 70)

for table in tables:
    try:
        cursor.execute(f"""
            SELECT COUNT(*) as cnt, MIN(season) as min_season, MAX(season) as max_season
            FROM {table}
            WHERE season IS NOT NULL;
        """)
        result = cursor.fetchone()
        if result:
            cnt, min_season, max_season = result
            print("{:<25} {:<12,} {:<15} {:<10}".format(
                table, cnt, f"{min_season}-{max_season}" if min_season else "-", ""
            ))
    except Exception as e:
        print("{:<25} {:<12} {:<15} {:<10}".format(table, "错误", "-", str(e)[:10]))

# 检查CSV目录中是否有1947年的数据
import os
csv_dir = "C:/autopick/AutoPick/nba_data/CSV"
if os.path.exists(csv_dir):
    print("\n📁 CSV目录中的文件:")
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
    for csv_file in sorted(csv_files):
        file_path = os.path.join(csv_dir, csv_file)
        size = os.path.getsize(file_path)
        print(f"  - {csv_file} ({size/1024/1024:.1f} MB)")

conn.close()
