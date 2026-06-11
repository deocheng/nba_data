import pandas as pd
import os

csv_dir = 'CSV/1947'

# 检查主要文件的列名和第一行数据
files_to_check = ['Player Totals.csv', 'Team Totals.csv']

for f in files_to_check:
    path = os.path.join(csv_dir, f)
    if os.path.exists(path):
        df = pd.read_csv(path, encoding='utf-8-sig')
        print(f"\n{f}:")
        print(f"  行数: {len(df)}")
        print(f"  列名: {list(df.columns)[:10]}")
        if len(df) > 0:
            print(f"  第一行: {dict(df.iloc[0])}")
