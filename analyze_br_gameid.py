import pandas as pd

# 分析CSV/pbp1997.csv的gameid格式
df = pd.read_csv('CSV/pbp1997.csv', encoding='utf-8-sig')

print("=" * 60)
print("Basketball-Reference gameid 格式分析")
print("=" * 60)

# 检查gameid的结构
print(f"\ngameid样例:")
sample_ids = df['gameid'].unique()[:20]
for gid in sample_ids:
    print(f"  {gid}")

# 分析gameid的数字特征
print(f"\ngameid特征:")
print(f"  最小值: {df['gameid'].min()}")
print(f"  最大值: {df['gameid'].max()}")
print(f"  唯一种类: {df['gameid'].nunique()}")

# 按赛季分析
print(f"\n按赛季统计:")
season_stats = df.groupby('season').agg({
    'gameid': ['min', 'max', 'nunique']
}).reset_index()
season_stats.columns = ['season', 'min_gameid', 'max_gameid', 'game_count']
print(season_stats)

# 分析gameid的数字构成
print(f"\n数字分析:")
print(f"  前4位 → 可能是赛季标识")
print(f"  后4位 → 可能是比赛序号")
for _, row in season_stats.iterrows():
    min_id = row['min_gameid']
    max_id = row['max_gameid']
    prefix = str(min_id)[:4]
    suffix_range = f"{str(min_id)[4:]} - {str(max_id)[4:]}"
    print(f"\n  Season {row['season']}:")
    print(f"    前缀: {prefix}")
    print(f"    序号范围: {suffix_range}")
