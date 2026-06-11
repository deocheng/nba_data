import psycopg2
import csv
import os
from datetime import datetime

DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'nba'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5433')
}

CSV_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CSV")

def create_tables():
    """创建马刺季后赛数据表"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 创建高级统计数据表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS spurs_playoffs_advanced_2026 (
            id SERIAL PRIMARY KEY,
            game_rank INTEGER,
            game_number INTEGER,
            game_date DATE,
            is_away VARCHAR(1),
            opponent VARCHAR(10),
            result VARCHAR(1),
            team_score INTEGER,
            opp_score INTEGER,
            overtime VARCHAR(10),
            ORtg DECIMAL(6,2),
            DRtg DECIMAL(6,2),
            Pace DECIMAL(6,2),
            FTr DECIMAL(5,4),
            threePAr DECIMAL(5,4),
            TS_pct DECIMAL(6,4),
            TRB_pct DECIMAL(6,4),
            AST_pct DECIMAL(6,4),
            STL_pct DECIMAL(6,4),
            BLK_pct DECIMAL(6,4),
            eFG_pct_off DECIMAL(6,4),
            TOV_pct_off DECIMAL(6,4),
            ORB_pct_off DECIMAL(6,4),
            FT_FGA_off DECIMAL(6,4),
            eFG_pct_def DECIMAL(6,4),
            TOV_pct_def DECIMAL(6,4),
            ORB_pct_def DECIMAL(6,4),
            FT_FGA_def DECIMAL(6,4),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建详细比赛统计表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS spurs_playoffs_games_2026 (
            id SERIAL PRIMARY KEY,
            game_rank INTEGER,
            game_number INTEGER,
            game_date DATE,
            is_away VARCHAR(1),
            opponent VARCHAR(10),
            result VARCHAR(1),
            team_score INTEGER,
            opp_score INTEGER,
            overtime VARCHAR(10),
            FG INTEGER,
            FGA INTEGER,
            FG_pct DECIMAL(6,4),
            threeP INTEGER,
            threePA INTEGER,
            threeP_pct DECIMAL(6,4),
            twoP INTEGER,
            twoPA INTEGER,
            twoP_pct DECIMAL(6,4),
            eFG_pct DECIMAL(6,4),
            FT INTEGER,
            FTA INTEGER,
            FT_pct DECIMAL(6,4),
            ORB INTEGER,
            DRB INTEGER,
            TRB INTEGER,
            AST INTEGER,
            STL INTEGER,
            BLK INTEGER,
            TOV INTEGER,
            PF INTEGER,
            opp_FG INTEGER,
            opp_FGA INTEGER,
            opp_FG_pct DECIMAL(6,4),
            opp_threeP INTEGER,
            opp_threePA INTEGER,
            opp_threeP_pct DECIMAL(6,4),
            opp_twoP INTEGER,
            opp_twoPA INTEGER,
            opp_twoP_pct DECIMAL(6,4),
            opp_eFG_pct DECIMAL(6,4),
            opp_FT INTEGER,
            opp_FTA INTEGER,
            opp_FT_pct DECIMAL(6,4),
            opp_ORB INTEGER,
            opp_DRB INTEGER,
            opp_TRB INTEGER,
            opp_AST INTEGER,
            opp_STL INTEGER,
            opp_BLK INTEGER,
            opp_TOV INTEGER,
            opp_PF INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✓ 数据表创建成功")

def import_advanced_stats():
    """导入高级统计数据"""
    csv_file = os.path.join(CSV_DIR, "sas_playoffs_2026.csv")
    
    if not os.path.exists(csv_file):
        print(f"✗ 文件不存在: {csv_file}")
        return
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 清空现有数据
    cursor.execute("DELETE FROM spurs_playoffs_advanced_2026")
    print("✓ 已清空现有高级统计数据")
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                # 跳过空行
                if not row.get('Rk') or not row.get('Date'):
                    continue
                
                game_rank = int(row['Rk']) if row.get('Rk') else None
                game_number = int(row['Gtm']) if row.get('Gtm') else None
                game_date = datetime.strptime(row['Date'], '%Y-%m-%d').date() if row.get('Date') else None
                is_away = '@' if row.get('Opp', '').startswith('@') else ''
                opponent = row['Opp'].replace('@', '').strip() if row.get('Opp') else ''
                result = row['Rslt'] if row.get('Rslt') else ''
                team_score = int(row['Tm']) if row.get('Tm') else None
                opp_score = int(row['Opp.1']) if row.get('Opp.1') else None
                overtime = row['OT'] if row.get('OT') else ''
                
                cursor.execute("""
                    INSERT INTO spurs_playoffs_advanced_2026 (
                        game_rank, game_number, game_date, is_away, opponent, result,
                        team_score, opp_score, overtime,
                        ORtg, DRtg, Pace, FTr, threePAr, TS_pct, TRB_pct, AST_pct,
                        STL_pct, BLK_pct, eFG_pct_off, TOV_pct_off, ORB_pct_off, FT_FGA_off,
                        eFG_pct_def, TOV_pct_def, ORB_pct_def, FT_FGA_def
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s
                    )
                """, (
                    game_rank, game_number, game_date, is_away, opponent, result,
                    team_score, opp_score, overtime,
                    float(row['ORtg']) if row.get('ORtg') else None,
                    float(row['DRtg']) if row.get('DRtg') else None,
                    float(row['Pace']) if row.get('Pace') else None,
                    float(row['FTr']) if row.get('FTr') else None,
                    float(row['3PAr']) if row.get('3PAr') else None,
                    float(row['TS%']) if row.get('TS%') else None,
                    float(row['TRB%']) if row.get('TRB%') else None,
                    float(row['AST%']) if row.get('AST%') else None,
                    float(row['STL%']) if row.get('STL%') else None,
                    float(row['BLK%']) if row.get('BLK%') else None,
                    float(row['eFG%']) if row.get('eFG%') else None,
                    float(row['TOV%']) if row.get('TOV%') else None,
                    float(row['ORB%']) if row.get('ORB%') else None,
                    float(row['FT/FGA']) if row.get('FT/FGA') else None,
                    float(row['eFG%.1']) if row.get('eFG%.1') else None,
                    float(row['TOV%.1']) if row.get('TOV%.1') else None,
                    float(row['ORB%.1']) if row.get('ORB%.1') else None,
                    float(row['FT/FGA.1']) if row.get('FT/FGA.1') else None
                ))
            except Exception as e:
                print(f"✗ 导入第{game_rank}行数据失败: {e}")
                continue
    
    conn.commit()
    cursor.close()
    conn.close()
    
    # 验证导入结果
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM spurs_playoffs_advanced_2026")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    print(f"✓ 成功导入 {count} 条高级统计数据")

def import_detailed_stats():
    """导入详细比赛统计数据"""
    csv_file = os.path.join(CSV_DIR, "sas_playoffs_2026_detailed.csv")
    
    if not os.path.exists(csv_file):
        print(f"✗ 文件不存在: {csv_file}")
        return
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 清空现有数据
    cursor.execute("DELETE FROM spurs_playoffs_games_2026")
    print("✓ 已清空现有详细比赛数据")
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                if not row.get('Rk') or not row.get('Date'):
                    continue
                
                game_rank = int(row['Rk']) if row.get('Rk') else None
                game_number = int(row['Gtm']) if row.get('Gtm') else None
                game_date = datetime.strptime(row['Date'], '%Y-%m-%d').date() if row.get('Date') else None
                is_away = '@' if row.get('Away') and row['Away'].startswith('@') else ''
                opponent = row['Opp'].strip() if row.get('Opp') else ''
                result = row['Rslt'] if row.get('Rslt') else ''
                team_score = int(row['Tm']) if row.get('Tm') else None
                opp_score = int(row['Opp_Score']) if row.get('Opp_Score') else None
                overtime = row['OT'] if row.get('OT') else ''
                
                cursor.execute("""
                    INSERT INTO spurs_playoffs_games_2026 (
                        game_rank, game_number, game_date, is_away, opponent, result,
                        team_score, opp_score, overtime,
                        FG, FGA, FG_pct, threeP, threePA, threeP_pct,
                        twoP, twoPA, twoP_pct, eFG_pct,
                        FT, FTA, FT_pct,
                        ORB, DRB, TRB, AST, STL, BLK, TOV, PF,
                        opp_FG, opp_FGA, opp_FG_pct, opp_threeP, opp_threePA, opp_threeP_pct,
                        opp_twoP, opp_twoPA, opp_twoP_pct, opp_eFG_pct,
                        opp_FT, opp_FTA, opp_FT_pct,
                        opp_ORB, opp_DRB, opp_TRB, opp_AST, opp_STL, opp_BLK, opp_TOV, opp_PF
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    game_rank, game_number, game_date, is_away, opponent, result,
                    team_score, opp_score, overtime,
                    int(row['FG']) if row.get('FG') else None,
                    int(row['FGA']) if row.get('FGA') else None,
                    float(row['FG_pct'].replace('.', '0.', 1)) if row.get('FG_pct') and row['FG_pct'] != '' else None,
                    int(row['3P']) if row.get('3P') else None,
                    int(row['3PA']) if row.get('3PA') else None,
                    float(row['3P_pct'].replace('.', '0.', 1)) if row.get('3P_pct') and row['3P_pct'] != '' else None,
                    int(row['2P']) if row.get('2P') else None,
                    int(row['2PA']) if row.get('2PA') else None,
                    float(row['2P_pct'].replace('.', '0.', 1)) if row.get('2P_pct') and row['2P_pct'] != '' else None,
                    float(row['eFG_pct'].replace('.', '0.', 1)) if row.get('eFG_pct') and row['eFG_pct'] != '' else None,
                    int(row['FT']) if row.get('FT') else None,
                    int(row['FTA']) if row.get('FTA') else None,
                    float(row['FT_pct'].replace('.', '0.', 1)) if row.get('FT_pct') and row['FT_pct'] != '' else None,
                    int(row['ORB']) if row.get('ORB') else None,
                    int(row['DRB']) if row.get('DRB') else None,
                    int(row['TRB']) if row.get('TRB') else None,
                    int(row['AST']) if row.get('AST') else None,
                    int(row['STL']) if row.get('STL') else None,
                    int(row['BLK']) if row.get('BLK') else None,
                    int(row['TOV']) if row.get('TOV') else None,
                    int(row['PF']) if row.get('PF') else None,
                    int(row['Opp_FG']) if row.get('Opp_FG') else None,
                    int(row['Opp_FGA']) if row.get('Opp_FGA') else None,
                    float(row['Opp_FG_pct'].replace('.', '0.', 1)) if row.get('Opp_FG_pct') and row['Opp_FG_pct'] != '' else None,
                    int(row['Opp_3P']) if row.get('Opp_3P') else None,
                    int(row['Opp_3PA']) if row.get('Opp_3PA') else None,
                    float(row['Opp_3P_pct'].replace('.', '0.', 1)) if row.get('Opp_3P_pct') and row['Opp_3P_pct'] != '' else None,
                    int(row['Opp_2P']) if row.get('Opp_2P') else None,
                    int(row['Opp_2PA']) if row.get('Opp_2PA') else None,
                    float(row['Opp_2P_pct'].replace('.', '0.', 1)) if row.get('Opp_2P_pct') and row['Opp_2P_pct'] != '' else None,
                    float(row['Opp_eFG_pct'].replace('.', '0.', 1)) if row.get('Opp_eFG_pct') and row['Opp_eFG_pct'] != '' else None,
                    int(row['Opp_FT']) if row.get('Opp_FT') else None,
                    int(row['Opp_FTA']) if row.get('Opp_FTA') else None,
                    float(row['Opp_FT_pct'].replace('.', '0.', 1)) if row.get('Opp_FT_pct') and row['Opp_FT_pct'] != '' else None,
                    int(row['Opp_ORB']) if row.get('Opp_ORB') else None,
                    int(row['Opp_DRB']) if row.get('Opp_DRB') else None,
                    int(row['Opp_TRB']) if row.get('Opp_TRB') else None,
                    int(row['Opp_AST']) if row.get('Opp_AST') else None,
                    int(row['Opp_STL']) if row.get('Opp_STL') else None,
                    int(row['Opp_BLK']) if row.get('Opp_BLK') else None,
                    int(row['Opp_TOV']) if row.get('Opp_TOV') else None,
                    int(row['Opp_PF']) if row.get('Opp_PF') else None
                ))
            except Exception as e:
                print(f"✗ 导入第{game_rank}行详细数据失败: {e}")
                continue
    
    conn.commit()
    cursor.close()
    conn.close()
    
    # 验证导入结果
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM spurs_playoffs_games_2026")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    print(f"✓ 成功导入 {count} 条详细比赛数据")

def main():
    print("=" * 60)
    print("马刺2026季后赛数据导入程序")
    print("=" * 60)
    
    try:
        # 创建数据表
        print("\n步骤1: 创建数据表...")
        create_tables()
        
        # 导入高级统计数据
        print("\n步骤2: 导入高级统计数据...")
        import_advanced_stats()
        
        # 导入详细比赛数据
        print("\n步骤3: 导入详细比赛数据...")
        import_detailed_stats()
        
        print("\n" + "=" * 60)
        print("✓ 所有数据导入完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
