import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent
CSV_FILE = BASE_DIR / "CSV_Clean" / "league_leaders_parsed.csv"

df = pd.read_csv(CSV_FILE)

categories = df['category'].unique()
print(f"\n=== 数据统计 ===")
print(f"总记录数: {len(df)}")
print(f"赛季数量: {len(df['season'].unique())}")
print(f"球员数量: {len(df['player'].unique())}")
print(f"球队数量: {len(df['team'].unique())}")
print(f"\n统计类别数量: {len(categories)}")

print(f"\n=== 所有统计类别列表 ===")
for i, cat in enumerate(sorted(categories), 1):
    print(f"{i}. {cat}")

categories_2025 = df[df['season'] == '2025-26']['category'].unique()
print(f"\n=== 2025-26赛季统计类别 ===")
print(f"2025-26赛季统计类别数量: {len(categories_2025)}")
for i, cat in enumerate(sorted(categories_2025), 1):
    print(f"{i}. {cat}")
