import pandas as pd

df = pd.read_csv('player_data/bbref_all_players.csv', encoding='utf-8-sig')

curry_df = df[df['player_name'].str.contains('Curry', case=False)]

if not curry_df.empty:
    print("🏀 库里家族球员信息:")
    print("=" * 60)
    
    for _, row in curry_df.iterrows():
        print(f"\n姓名: {row['player_name']}")
        print(f"位置: {row['position']}")
        print(f"身高: {row['height']}")
        print(f"体重: {row['weight']} 磅")
        print(f"进入联盟: {row['from_year']}")
        print(f"离开联盟: {row['to_year'] if pd.notna(row['to_year']) else '现役'}")
        print(f"大学: {row['colleges']}")
        print(f"是否现役: {'✅ 是' if pd.isna(row['to_year']) or int(row['to_year']) >= 2025 else '❌ 否'}")
else:
    print("未找到库里相关球员")