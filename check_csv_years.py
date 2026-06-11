import pandas as pd
import os

csv_dir = 'CSV/1947'

# 检查几个主要文件的年份范围
files_to_check = ['Player Totals.csv', 'Player Per Game.csv', 'Team Totals.csv']

for f in files_to_check:
    path = os.path.join(csv_dir, f)
    if os.path.exists(path):
        df = pd.read_csv(path, encoding='utf-8-sig')
        if 'Season' in df.columns:
            seasons = df['Season'].dropna().unique()
            if len(seasons) > 0:
                # 提取开始年份
                start_years = [int(str(s)[:4]) for s in seasons if str(s).startswith('1') or str(s).startswith('2')]
                if start_years:
                    print(f"{f}: {min(start_years)}-{max(start_years)} ({len(seasons)}个赛季)")
                else:
                    print(f"{f}: 无法确定年份范围")
            else:
                print(f"{f}: 无Season数据")
        else:
            print(f"{f}: 无Season列")
