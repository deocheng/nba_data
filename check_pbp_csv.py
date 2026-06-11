import pandas as pd
import os

# 检查CSV文件
csv_path = 'CSV/pbp1997.csv'
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    print(f"CSV/pbp1997.csv:")
    print(f"  行数: {len(df):,}条")
    print(f"  列名: {list(df.columns)}")
    print(f"\n前3行:")
    print(df.head(3))
else:
    print(f"文件不存在: {csv_path}")
