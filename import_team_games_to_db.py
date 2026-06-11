import sqlite3
import pandas as pd
from pathlib import Path

def import_team_data_to_db(csv_file, team_abbr, db_file='nba_data.db'):
    """将球队数据导入SQLite数据库"""
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_abbr TEXT,
            season TEXT,
            game_num INTEGER,
            date TEXT,
            opponent TEXT,
            result TEXT,
            team_score INTEGER,
            opponent_score INTEGER,
            ot TEXT,
            fg INTEGER,
            fga INTEGER,
            fg_pct REAL,
            three_p INTEGER,
            three_pa INTEGER,
            three_p_pct REAL,
            two_p INTEGER,
            two_pa INTEGER,
            two_p_pct REAL,
            efg_pct REAL,
            ft INTEGER,
            fta INTEGER,
            ft_pct REAL,
            orb INTEGER,
            drb INTEGER,
            trb INTEGER,
            ast INTEGER,
            stl INTEGER,
            blk INTEGER,
            tov INTEGER,
            pf INTEGER,
            opp_fg INTEGER,
            opp_fga INTEGER,
            opp_fg_pct REAL,
            opp_three_p INTEGER,
            opp_three_pa INTEGER,
            opp_three_p_pct REAL,
            opp_two_p INTEGER,
            opp_two_pa INTEGER,
            opp_two_p_pct REAL,
            opp_efg_pct REAL,
            opp_ft INTEGER,
            opp_fta INTEGER,
            opp_ft_pct REAL,
            opp_orb INTEGER,
            opp_drb INTEGER,
            opp_trb INTEGER,
            opp_ast INTEGER,
            opp_stl INTEGER,
            opp_blk INTEGER,
            opp_tov INTEGER,
            opp_pf INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_team_games_team_abbr ON team_games(team_abbr)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_team_games_season ON team_games(season)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_team_games_date ON team_games(date)')
    
    inserted = 0
    skipped = 0
    
    for _, row in df.iterrows():
        try:
            season = '1989-90'
            for col in row.index:
                if '1989' in str(col) or '1990' in str(col) or '1991' in str(col) or '1992' in str(col):
                    season_parts = str(col).split('-')
                    if len(season_parts) >= 2:
                        season = col[:7]
                        break
            
            game_num = row.get('Rk') or row.get('Unnamed: 0')
            
            if pd.isna(game_num) or (isinstance(game_num, str) and not game_num.isdigit()):
                skipped += 1
                continue
            
            date = row.get('Date')
            opponent = row.get('Opp')
            result = row.get('Rslt')
            team_score = row.get('Tm')
            opponent_score = row.get('Opp')
            
            cursor.execute('''
                INSERT INTO team_games (
                    team_abbr, season, game_num, date, opponent, result,
                    team_score, opponent_score, ot, fg, fga, fg_pct,
                    three_p, three_pa, three_p_pct, two_p, two_pa, two_p_pct,
                    efg_pct, ft, fta, ft_pct, orb, drb, trb, ast, stl, blk, tov, pf,
                    opp_fg, opp_fga, opp_fg_pct, opp_three_p, opp_three_pa, opp_three_p_pct,
                    opp_two_p, opp_two_pa, opp_two_p_pct, opp_efg_pct, opp_ft, opp_fta, opp_ft_pct,
                    opp_orb, opp_drb, opp_trb, opp_ast, opp_stl, opp_blk, opp_tov, opp_pf
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                team_abbr,
                season,
                int(game_num) if pd.notna(game_num) else None,
                date if pd.notna(date) else None,
                opponent if pd.notna(opponent) else None,
                result if pd.notna(result) else None,
                int(team_score) if pd.notna(team_score) and str(team_score).isdigit() else None,
                int(opponent_score) if pd.notna(opponent_score) and str(opponent_score).isdigit() else None,
                row.get('OT') if pd.notna(row.get('OT')) else None,
                int(row['FG']) if pd.notna(row.get('FG')) else None,
                int(row['FGA']) if pd.notna(row.get('FGA')) else None,
                float(row['FG%']) if pd.notna(row.get('FG%')) else None,
                int(row['3P']) if pd.notna(row.get('3P')) else None,
                int(row['3PA']) if pd.notna(row.get('3PA')) else None,
                float(row['3P%']) if pd.notna(row.get('3P%')) else None,
                int(row['2P']) if pd.notna(row.get('2P')) else None,
                int(row['2PA']) if pd.notna(row.get('2PA')) else None,
                float(row['2P%']) if pd.notna(row.get('2P%')) else None,
                float(row['eFG%']) if pd.notna(row.get('eFG%')) else None,
                int(row['FT']) if pd.notna(row.get('FT')) else None,
                int(row['FTA']) if pd.notna(row.get('FTA')) else None,
                float(row['FT%']) if pd.notna(row.get('FT%')) else None,
                int(row['ORB']) if pd.notna(row.get('ORB')) else None,
                int(row['DRB']) if pd.notna(row.get('DRB')) else None,
                int(row['TRB']) if pd.notna(row.get('TRB')) else None,
                int(row['AST']) if pd.notna(row.get('AST')) else None,
                int(row['STL']) if pd.notna(row.get('STL')) else None,
                int(row['BLK']) if pd.notna(row.get('BLK')) else None,
                int(row['TOV']) if pd.notna(row.get('TOV')) else None,
                int(row['PF']) if pd.notna(row.get('PF')) else None,
                int(row.get('FG.1')) if pd.notna(row.get('FG.1')) else None,
                int(row.get('FGA.1')) if pd.notna(row.get('FGA.1')) else None,
                float(row.get('FG%.1')) if pd.notna(row.get('FG%.1')) else None,
                int(row.get('3P.1')) if pd.notna(row.get('3P.1')) else None,
                int(row.get('3PA.1')) if pd.notna(row.get('3PA.1')) else None,
                float(row.get('3P%.1')) if pd.notna(row.get('3P%.1')) else None,
                int(row.get('2P.1')) if pd.notna(row.get('2P.1')) else None,
                int(row.get('2PA.1')) if pd.notna(row.get('2PA.1')) else None,
                float(row.get('2P%.1')) if pd.notna(row.get('2P%.1')) else None,
                float(row.get('eFG%.1')) if pd.notna(row.get('eFG%.1')) else None,
                int(row.get('FT.1')) if pd.notna(row.get('FT.1')) else None,
                int(row.get('FTA.1')) if pd.notna(row.get('FTA.1')) else None,
                float(row.get('FT%.1')) if pd.notna(row.get('FT%.1')) else None,
                int(row.get('ORB.1')) if pd.notna(row.get('ORB.1')) else None,
                int(row.get('DRB.1')) if pd.notna(row.get('DRB.1')) else None,
                int(row.get('TRB.1')) if pd.notna(row.get('TRB.1')) else None,
                int(row.get('AST.1')) if pd.notna(row.get('AST.1')) else None,
                int(row.get('STL.1')) if pd.notna(row.get('STL.1')) else None,
                int(row.get('BLK.1')) if pd.notna(row.get('BLK.1')) else None,
                int(row.get('TOV.1')) if pd.notna(row.get('TOV.1')) else None,
                int(row.get('PF.1')) if pd.notna(row.get('PF.1')) else None
            ))
            inserted += 1
        except Exception as e:
            skipped += 1
    
    conn.commit()
    
    cursor.execute('SELECT COUNT(*) FROM team_games WHERE team_abbr = ?', (team_abbr,))
    total = cursor.fetchone()[0]
    
    conn.close()
    
    print(f'{team_abbr} 数据导入完成!')
    print(f'  新增: {inserted} 条')
    print(f'  跳过: {skipped} 条')
    print(f'  总数: {total} 条')

def import_all_team_data(db_file='nba_data.db'):
    """导入所有球队数据"""
    csv_dir = Path('CSV')
    team_files = csv_dir.glob('1989-2026*.csv')
    
    for csv_file in team_files:
        team_abbr = csv_file.stem.replace('1989-2026', '')
        print(f'\n正在导入 {team_abbr}...')
        import_team_data_to_db(str(csv_file), team_abbr, db_file)

if __name__ == '__main__':
    print("开始导入球队数据到数据库...")
    import_all_team_data()
    print("\n✅ 所有球队数据导入完成!")