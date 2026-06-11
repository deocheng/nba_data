import pandas as pd
import numpy as np

# 读取原始文件（跳过空行，处理多余逗号）
df = pd.read_csv('/path/to/MJ career.csv', 
                 header=0, 
                 skip_blank_lines=True,
                 on_bad_lines='skip')

# 删除完全空的列
df = df.dropna(axis=1, how='all')

# 保留主要列（推荐）
columns_to_keep = [
    'Rk', 'Gcar', 'Gtm', 'Date', 'Team', 'Opp', 'Result', 'GS', 'MP',
    'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%',
    'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'GmSc'
]

df = df[columns_to_keep].copy()

# 数据类型转换
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['MP'] = df['MP'].astype(str).str.replace(':00:00', '').str.strip()  # 处理时间格式

# 提取胜负和比分
df['Win'] = df['Result'].str.contains('W', na=False).astype(int)
df['PTS_Allowed'] = df['Result'].str.extract(r'([0-9]+)-([0-9]+)')[1].astype(float)

print(df.shape)
print(df.head())
df.to_csv('MJ_career_clean.csv', index=False)