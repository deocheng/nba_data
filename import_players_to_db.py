import sqlite3
import pandas as pd
from pathlib import Path

def import_players_to_db(csv_file, db_file='nba_data.db'):
    """将球员数据导入SQLite数据库"""
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT UNIQUE,
            player_name TEXT,
            from_year INTEGER,
            to_year INTEGER,
            position TEXT,
            height TEXT,
            weight INTEGER,
            birth_date TEXT,
            colleges TEXT,
            player_url TEXT,
            is_active INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_players_player_id ON players(player_id)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_players_player_name ON players(player_name)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_players_is_active ON players(is_active)
    ''')
    
    inserted = 0
    updated = 0
    skipped = 0
    
    for _, row in df.iterrows():
        player_id = row['player_id'] if pd.notna(row['player_id']) else None
        player_name = row['player_name'] if pd.notna(row['player_name']) else None
        
        if not player_id or not player_name:
            skipped += 1
            continue
        
        from_year = int(row['from_year']) if pd.notna(row['from_year']) else None
        to_year = int(row['to_year']) if pd.notna(row['to_year']) else None
        
        is_active = 1 if (pd.isna(row['to_year']) or (pd.notna(row['to_year']) and int(row['to_year']) >= 2025)) else 0
        
        cursor.execute('''
            SELECT id FROM players WHERE player_id = ?
        ''', (player_id,))
        
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE players SET 
                    player_name = ?,
                    from_year = ?,
                    to_year = ?,
                    position = ?,
                    height = ?,
                    weight = ?,
                    birth_date = ?,
                    colleges = ?,
                    player_url = ?,
                    is_active = ?
                WHERE player_id = ?
            ''', (
                player_name,
                from_year,
                to_year,
                row['position'] if pd.notna(row['position']) else None,
                row['height'] if pd.notna(row['height']) else None,
                int(row['weight']) if pd.notna(row['weight']) else None,
                row['birth_date'] if pd.notna(row['birth_date']) else None,
                row['colleges'] if pd.notna(row['colleges']) else None,
                row['player_url'] if pd.notna(row['player_url']) else None,
                is_active,
                player_id
            ))
            updated += 1
        else:
            cursor.execute('''
                INSERT INTO players (
                    player_id, player_name, from_year, to_year, position,
                    height, weight, birth_date, colleges, player_url, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                player_id,
                player_name,
                from_year,
                to_year,
                row['position'] if pd.notna(row['position']) else None,
                row['height'] if pd.notna(row['height']) else None,
                int(row['weight']) if pd.notna(row['weight']) else None,
                row['birth_date'] if pd.notna(row['birth_date']) else None,
                row['colleges'] if pd.notna(row['colleges']) else None,
                row['player_url'] if pd.notna(row['player_url']) else None,
                is_active
            ))
            inserted += 1
    
    conn.commit()
    
    cursor.execute('SELECT COUNT(*) FROM players')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM players WHERE is_active = 1')
    active_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f'导入完成!')
    print(f'  新增: {inserted} 条')
    print(f'  更新: {updated} 条')
    print(f'  跳过: {skipped} 条')
    print(f'  总数: {total} 条')
    print(f'  现役: {active_count} 条')

if __name__ == '__main__':
    csv_file = 'player_data/bbref_all_players.csv'
    
    if not Path(csv_file).exists():
        print(f'错误: 文件 {csv_file} 不存在!')
        exit(1)
    
    print(f'正在导入球员数据...')
    import_players_to_db(csv_file)
    print('✅ 导入成功!')