import pandas as pd
import numpy as np
import psycopg2
from datetime import datetime
import glob
import os

# ==================== 配置区 ====================
DB_CONFIG = {
    'dbname': 'nba',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5433'
}

CSV_DIR = r'C:\autopick\AutoPick\nba_data\CSV'

# ==================== 工具函数 ====================
def mp_to_minutes(mp_str):
    """将比赛时间转换为分钟数"""
    if pd.isna(mp_str) or str(mp_str) == 'nan' or str(mp_str).strip() == '':
        return 0.0
    mp_str = str(mp_str).strip()
    if ':' in mp_str:
        try:
            parts = mp_str.split(':')
            if len(parts) == 2:
                m, s = map(int, parts)
                return m + s/60
            elif len(parts) == 3:
                h, m, s = map(int, parts)
                return h * 60 + m + s/60
        except:
            return 0.0
    try:
        return float(mp_str)
    except:
        return 0.0

def calculate_advanced_stats(df):
    """计算进阶数据"""
    df = df.copy()
    df['minutes'] = df['MP'].apply(mp_to_minutes)
    
    # True Shooting %
    df['ts_pct'] = np.where(
        (df['FGA'] + df['FTA']) > 0,
        df['PTS'] / (2 * (df['FGA'] + 0.44 * df['FTA'])),
        np.nan
    )
    
    # Effective FG %
    df['efg_pct'] = np.where(df['FGA'] > 0,
                             (df['FG'] + 0.5 * df.get('FG3', 0)) / df['FGA'], np.nan)
    
    # Usage Rate (简化版)
    df['usg_pct'] = np.where(df['minutes'] > 0,
        (df['FGA'] + 0.44*df['FTA'] + df['TOV']) / df['minutes'] * 100, np.nan)
    
    # PER 计算
    def calc_per(row):
        if row['minutes'] <= 0:
            return np.nan
        pts = row['PTS']
        fga = row['FGA']
        fta = row['FTA']
        fg3a = row.get('FG3A', 0)
        orb = row.get('ORB', 0)
        drb = row.get('DRB', 0)
        ast = row['AST']
        stl = row['STL']
        blk = row['BLK']
        tov = row['TOV']
        pf = row.get('PF', 0)
        fg = row['FG']
        ft = row.get('FT', 0)
        
        per = (pts + 0.7 * ast + 0.3 * orb + stl + 0.7 * blk -
               0.7 * tov - 0.3 * pf - 0.4 * (fga - fg) -
               0.3 * (fta - ft)) / row['minutes'] * 40
        
        return round(per, 2)
    
    df['per'] = df.apply(calc_per, axis=1)
    df['ws_per_48'] = round(df['per'] * 0.03, 2)
    
    df['data_version'] = 'v1.0'
    df['imported_at'] = datetime.now()
    df['updated_at'] = datetime.now()
    
    return df

# ==================== 球队数据初始化 ====================
def init_teams():
    teams_data = [
        ('LAL', 'Los Angeles Lakers', 'Los Angeles', 'LAL', 'Western', 'Pacific'),
        ('SAS', 'San Antonio Spurs', 'San Antonio', 'SAS', 'Western', 'Southwest'),
        ('HOU', 'Houston Rockets', 'Houston', 'HOU', 'Western', 'Southwest'),
        ('CHI', 'Chicago Bulls', 'Chicago', 'CHI', 'Eastern', 'Central'),
        ('MIA', 'Miami Heat', 'Miami', 'MIA', 'Eastern', 'Southeast'),
        ('GSW', 'Golden State Warriors', 'Golden State', 'GSW', 'Western', 'Pacific'),
        ('CLE', 'Cleveland Cavaliers', 'Cleveland', 'CLE', 'Eastern', 'Central'),
        ('BOS', 'Boston Celtics', 'Boston', 'BOS', 'Eastern', 'Atlantic'),
        ('DEN', 'Denver Nuggets', 'Denver', 'DEN', 'Western', 'Northwest'),
        ('PHX', 'Phoenix Suns', 'Phoenix', 'PHX', 'Western', 'Pacific'),
    ]
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    for team_id, full_name, city, abbreviation, conference, division in teams_data:
        cur.execute('''
            INSERT INTO teams (team_id, full_name, city, abbreviation, conference, division)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (team_id) DO NOTHING
        ''', (team_id, full_name, city, abbreviation, conference, division))
    
    conn.commit()
    conn.close()
    print("✅ 球队数据初始化完成")

# ==================== 赛季数据初始化 ====================
def init_seasons():
    seasons_data = []
    for year in range(1989, 2027):
        season_id = f"{year}-{str(year+1)[-2:]}"
        seasons_data.append((season_id, year, year+1, False))
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    for season_id, start_year, end_year, is_playoff in seasons_data:
        cur.execute('''
            INSERT INTO seasons (season_id, start_year, end_year, is_playoff)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (season_id) DO NOTHING
        ''', (season_id, start_year, end_year, is_playoff))
    
    conn.commit()
    conn.close()
    print("✅ 赛季数据初始化完成")

# ==================== 导入1989-2026开头的CSV文件 ====================
def import_historical_games():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    csv_pattern = os.path.join(CSV_DIR, '1989-2026*.csv')
    csv_files = glob.glob(csv_pattern)
    
    print(f"\n找到 {len(csv_files)} 个历史比赛数据文件")
    
    for filepath in csv_files:
        filename = os.path.basename(filepath)
        team_abbr = filename.replace('1989-2026', '').replace('.csv', '')
        print(f"\n正在处理: {filename} (球队: {team_abbr})")
        
        try:
            # 使用csv模块逐行读取
            import csv
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            # 跳过第一行（空行）
            if len(rows) > 0 and all(cell.strip() == '' for cell in rows[0]):
                rows = rows[1:]
            
            if len(rows) < 2:
                print(f"⚠️ 文件内容太少，跳过")
                continue
            
            # 第二行是列名
            headers = rows[0]
            # 数据行从第三行开始
            data_rows = rows[1:]
            
            inserted = 0
            skipped = 0
            
            for row in data_rows:
                if len(row) < 6:  # 需要至少有日期、对手、比分等基本信息
                    skipped += 1
                    continue
                
                # 提取数据
                date_str = row[2].strip() if len(row) > 2 else ''
                opp_team = row[4].strip() if len(row) > 4 else ''
                team_score_str = row[6].strip() if len(row) > 6 else ''
                opp_score_str = row[7].strip() if len(row) > 7 else ''
                
                if not date_str:
                    skipped += 1
                    continue
                
                # 解析日期
                try:
                    game_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    season_year = game_date.year
                    season = f"{season_year}-{str(season_year+1)[-2:]}"
                except:
                    skipped += 1
                    continue
                
                # 提取得分
                try:
                    team_score = int(team_score_str) if team_score_str.isdigit() else None
                    opp_score = int(opp_score_str) if opp_score_str.isdigit() else None
                except:
                    team_score = None
                    opp_score = None
                
                if team_score is None:
                    skipped += 1
                    continue
                
                # 提取命中率（第11列和第13列）
                fg_pct = None
                ft_pct = None
                if len(row) > 10:
                    try:
                        fg_pct = float(row[10].strip())
                    except:
                        pass
                if len(row) > 12:
                    try:
                        ft_pct = float(row[12].strip())
                    except:
                        pass
                
                cur.execute('''
                    INSERT INTO historical_games (team_abbr, game_date, season, 
                        team_score, opp_score, fg_pct, ft_pct)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                ''', (team_abbr, game_date, season, team_score, opp_score, fg_pct, ft_pct))
                inserted += 1
            
            conn.commit()
            print(f"✅ 成功导入 {inserted} 条记录，跳过 {skipped} 条无效记录")
            
        except Exception as e:
            print(f"❌ 处理文件 {filename} 时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    conn.close()

# ==================== 导入球员生涯数据 ====================
def import_player_career_data():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    csv_pattern = os.path.join(CSV_DIR, '*Career*.csv')
    csv_files = glob.glob(csv_pattern)
    
    print(f"\n找到 {len(csv_files)} 个球员生涯数据文件")
    
    for filepath in csv_files:
        filename = os.path.basename(filepath)
        player_name = filename.replace('Career.csv', '').replace('.csv', '').strip()
        player_id = player_name.lower().replace(' ', '_')
        
        print(f"\n正在处理: {filename} (球员: {player_name})")
        
        try:
            df = pd.read_csv(filepath, encoding='utf-8', header=None)
            
            all_data = []
            current_season = None
            columns = None
            
            for idx, row in df.iterrows():
                first_val = str(row.iloc[0]).strip()
                
                # 检测赛季标题行（如 "1996-97 Regular Season"）
                if '-' in first_val and len(first_val) >= 7 and len(first_val) <= 20:
                    current_season = first_val[:7]  # 提取 "1996-97"
                    continue
                
                # 检测列名行
                if 'Rk' in str(row.iloc[0]) and 'Gcar' in str(row.iloc[1]):
                    columns = row.tolist()
                    continue
                
                # 跳过空行和分隔行
                if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '':
                    continue
                
                # 处理数据行
                if columns is not None and current_season is not None:
                    data_dict = dict(zip(columns, row.tolist()))
                    data_dict['Season'] = current_season
                    all_data.append(data_dict)
            
            if not all_data:
                print(f"⚠️ 没有找到有效数据，跳过文件")
                continue
            
            df = pd.DataFrame(all_data)
            
            # 选择需要的列
            needed_columns = ['Rk', 'Gcar', 'Date', 'Team', 'Opp', 'Result', 'GS', 'MP', 
                             'FG', 'FGA', 'FG3', 'FG3A', 'FT', 'FTA', 'ORB', 'DRB', 
                             'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'Season']
            
            # 确保所有需要的列都存在
            for col in needed_columns:
                if col not in df.columns:
                    df[col] = None
            
            df = df[needed_columns]
            
            # 转换数据类型
            numeric_cols = ['GS', 'FG', 'FGA', 'FG3', 'FG3A', 'FT', 'FTA', 'ORB', 'DRB', 
                           'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']
            
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            
            df = calculate_advanced_stats(df)
            
            # 插入球员信息
            cur.execute('''
                INSERT INTO players (player_id, full_name)
                VALUES (%s, %s)
                ON CONFLICT (player_id) DO NOTHING
            ''', (player_id, player_name))
            
            # 按赛季汇总
            season_summary = df.groupby(['Team', 'Season']).agg({
                'GS': 'sum',
                'minutes': 'sum',
                'PTS': 'sum',
                'TRB': 'sum',
                'AST': 'sum',
                'STL': 'sum',
                'BLK': 'sum',
                'TOV': 'sum',
                'FG': 'sum',
                'FGA': 'sum',
                'FG3': 'sum',
                'FG3A': 'sum',
                'FT': 'sum',
                'FTA': 'sum',
                'per': 'mean',
                'ts_pct': 'mean',
                'usg_pct': 'mean',
                'ws_per_48': 'mean'
            }).reset_index()
            
            inserted_seasons = 0
            for _, row in season_summary.iterrows():
                team_id = str(row['Team'])[:3] if len(str(row['Team'])) >= 3 else 'LAL'
                season_id = str(row['Season'])
                
                games_played = len(df[(df['Team'] == row['Team']) & (df['Season'] == row['Season'])])
                
                cur.execute('''
                    INSERT INTO player_team_seasons (
                        player_id, team_id, season_id, games_played, games_started,
                        minutes_total, minutes_per_game,
                        pts_total, reb_total, ast_total, stl_total, blk_total, tov_total,
                        fg_total, fga_total, fg3_total, fg3a_total, ft_total, fta_total,
                        per, ts_pct, usg_pct, ws_per_48
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                              %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (player_id, team_id, season_id) DO UPDATE SET
                        games_played = EXCLUDED.games_played,
                        minutes_total = EXCLUDED.minutes_total, minutes_per_game = EXCLUDED.minutes_per_game,
                        pts_total = EXCLUDED.pts_total, reb_total = EXCLUDED.reb_total,
                        ast_total = EXCLUDED.ast_total, stl_total = EXCLUDED.stl_total,
                        blk_total = EXCLUDED.blk_total, tov_total = EXCLUDED.tov_total,
                        per = EXCLUDED.per, ts_pct = EXCLUDED.ts_pct,
                        usg_pct = EXCLUDED.usg_pct, ws_per_48 = EXCLUDED.ws_per_48,
                        updated_at = NOW()
                ''', (
                    player_id, team_id, season_id,
                    games_played, int(row['GS']),
                    int(row['minutes']), round(row['minutes'] / games_played, 2) if games_played > 0 else 0,
                    int(row['PTS']), int(row['TRB']), int(row['AST']),
                    int(row['STL']), int(row['BLK']), int(row['TOV']),
                    int(row['FG']), int(row['FGA']), int(row['FG3']),
                    int(row['FG3A']), int(row['FT']), int(row['FTA']),
                    round(float(row['per']), 2) if pd.notna(row['per']) else None,
                    round(float(row['ts_pct']), 4) if pd.notna(row['ts_pct']) else None,
                    round(float(row['usg_pct']), 4) if pd.notna(row['usg_pct']) else None,
                    round(float(row['ws_per_48']), 2) if pd.notna(row['ws_per_48']) else None
                ))
                inserted_seasons += 1
            
            conn.commit()
            print(f"✅ 成功导入 {len(df)} 场比赛，{inserted_seasons} 个赛季记录")
            
        except Exception as e:
            print(f"❌ 处理文件 {filename} 时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    conn.close()

# ==================== 主函数 ====================
def main():
    print("=" * 60)
    print("          NBA ETL 数据导入工具")
    print("=" * 60)
    
    print("\n1️⃣ 初始化球队数据...")
    init_teams()
    
    print("\n2️⃣ 初始化赛季数据...")
    init_seasons()
    
    print("\n3️⃣ 导入历史比赛数据 (1989-2026开头的CSV)...")
    import_historical_games()
    
    print("\n4️⃣ 导入球员生涯数据 (Career文件)...")
    import_player_career_data()
    
    print("\n" + "=" * 60)
    print("🎉 数据导入完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()