import sys
import csv
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()

# 读取CSV文件获取日期和主队信息
games_data = {}
csv_path = r'C:\autopick\AutoPick\nba_data\CSV\2026_season\all_games_2026.csv'

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        boxscore_url = row['boxscore_url']
        # 从URL提取我们格式的game_id
        if boxscore_url and '.html' in boxscore_url:
            our_game_id = boxscore_url.split('/')[-1].replace('.html', '')
            home_team = row['home_team']
            game_date = row['game_date']
            
            # 转换home_team为缩写
            team_mapping = {
                'Oklahoma City Thunder': 'OKC',
                'Los Angeles Lakers': 'LAL',
                'Charlotte Hornets': 'CHO',
                'New York Knicks': 'NYK',
                'Orlando Magic': 'ORL',
                'Boston Celtics': 'BOS',
                'Atlanta Hawks': 'ATL',
                'Chicago Bulls': 'CHI',
                'Memphis Grizzlies': 'MEM',
                'Milwaukee Bucks': 'MIL',
                'Utah Jazz': 'UTA',
                'Dallas Mavericks': 'DAL',
                'Portland Trail Blazers': 'POR',
                'Phoenix Suns': 'PHO',
                'Sacramento Kings': 'SAC',
                'San Antonio Spurs': 'SAS',
                'Minnesota Timberwolves': 'MIN',
                'Toronto Raptors': 'TOR',
                'Cleveland Cavaliers': 'CLE',
                'Brooklyn Nets': 'BRK',
                'Miami Heat': 'MIA',
                'Philadelphia 76ers': 'PHI',
                'Golden State Warriors': 'GSW',
                'Denver Nuggets': 'DEN',
                'Detroit Pistons': 'DET',
                'Houston Rockets': 'HOU',
                'Washington Wizards': 'WAS',
                'New Orleans Pelicans': 'NOP',
                'Los Angeles Clippers': 'LAC',
            }
            
            home_team_abbr = team_mapping.get(home_team, home_team[:3].upper())
            
            games_data[our_game_id] = {
                'home_team': home_team_abbr,
                'game_date': game_date,
                'full_home_team': home_team
            }

print(f"从CSV读取了 {len(games_data)} 场比赛")

# 检查映射表中已有的记录
with db.get_cursor() as cur:
    cur.execute("SELECT crawled_id FROM game_id_mapping")
    existing = set([r[0] for r in cur.fetchall()])
    print(f"映射表中已有 {len(existing)} 条记录")
    
    # 找出缺失的映射
    missing = [g for g in games_data if g not in existing]
    print(f"需要添加 {len(missing)} 条新映射")
    
    # 添加新映射
    added = 0
    for game_id in missing[:10]:  # 先处理前10条作为示例
        data = games_data[game_id]
        # 根据BR规则生成nba_id: 2 + 年份后两位 + 0 + 序号
        year = data['game_date'][:4]
        nba_id = f"2{year[2:]}00000"  # 简化处理，实际需要正确的序号
        
        cur.execute("""
            INSERT INTO game_id_mapping (crawled_id, nba_id, season, home_team, visitor_team)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (crawled_id) DO NOTHING
        """, (game_id, nba_id, int(year), data['home_team'], ''))
        added += 1
    
    db.conn.commit()
    print(f"已添加 {added} 条新映射")

print("\n转换完成！")
