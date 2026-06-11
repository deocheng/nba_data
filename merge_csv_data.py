#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并CSV\1947目录下的数据到数据库
"""
import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

sys.path.insert(0, os.path.dirname(__file__))

# 数据库连接
engine = create_engine('postgresql://postgres:postgres@localhost:5433/nba')

def load_and_merge_csv(file_path, table_name):
    """加载CSV文件并合并到数据库"""
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        
        print(f"\n处理文件: {os.path.basename(file_path)}")
        print(f"数据行数: {len(df)}")
        print(f"列名: {list(df.columns)}")
        
        # 清理列名（去除空格和特殊字符）
        df.columns = [col.strip().replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_').lower() for col in df.columns]
        
        # 使用upsert方式合并数据
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists='append',
            index=False,
            chunksize=1000
        )
        
        print(f"✅ 成功合并 {len(df)} 条记录到 {table_name} 表")
        return True
    except Exception as e:
        print(f"❌ 处理文件 {file_path} 时出错: {e}")
        return False

def main():
    csv_dir = os.path.join(os.path.dirname(__file__), 'CSV', '1947')
    
    if not os.path.exists(csv_dir):
        print(f"错误: 目录不存在 {csv_dir}")
        return
    
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
    
    print(f"找到 {len(csv_files)} 个CSV文件")
    
    # 定义文件到表名的映射
    file_table_map = {
        'Player Per Game.csv': 'player_per_game',
        'Player Totals.csv': 'player_totals',
        'Player Shooting.csv': 'player_shooting',
        'Advanced.csv': 'player_advanced',
        'Per 36 Minutes.csv': 'player_per_36_minutes',
        'Per 100 Poss.csv': 'player_per_100_poss',
        'Player Play By Play.csv': 'player_play_by_play',
        'Player Season Info.csv': 'player_season_info',
        'Player Career Info.csv': 'player_career_info',
        'Player Award Shares.csv': 'player_award_shares',
        'Team Stats Per Game.csv': 'team_stats_per_game',
        'Team Totals.csv': 'team_totals',
        'Team Stats Per 100 Poss.csv': 'team_stats_per_100_poss',
        'Team Summaries.csv': 'team_summaries',
        'Opponent Stats Per Game.csv': 'opponent_stats_per_game',
        'Opponent Totals.csv': 'opponent_totals',
        'Opponent Stats Per 100 Poss.csv': 'opponent_stats_per_100_poss',
        'All-Star Selections.csv': 'all_star_selections',
        'Draft Pick History.csv': 'draft_pick_history',
        'End of Season Teams.csv': 'end_of_season_teams',
        'End of Season Teams (Voting).csv': 'end_of_season_teams_voting',
        'Team Abbrev.csv': 'team_abbrev'
    }
    
    success_count = 0
    fail_count = 0
    
    for csv_file in csv_files:
        file_path = os.path.join(csv_dir, csv_file)
        table_name = file_table_map.get(csv_file, csv_file.replace('.csv', '').replace(' ', '_').lower())
        
        if load_and_merge_csv(file_path, table_name):
            success_count += 1
        else:
            fail_count += 1
    
    print(f"\n\n合并完成！")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    
    # 显示数据库表统计
    print("\n数据库表统计:")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        tables = result.fetchall()
        
        for table in tables:
            table_name = table[0]
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).fetchone()[0]
            print(f"  {table_name}: {count} 条记录")

if __name__ == "__main__":
    main()