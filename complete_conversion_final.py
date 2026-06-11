import sys
import csv
sys.path.insert(0, '.')
from data_importer.database import DatabaseManager

db = DatabaseManager()

# 球队名称到缩写的映射
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

# 读取CSV文件
games_data = []
csv_path = r'C:\autopick\AutoPick\nba_data\CSV\2026_season\all_games_2026.csv'

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        boxscore_url = row['boxscore_url']
        if boxscore_url and '.html' in boxscore_url:
            # 提取我们格式的game_id
            our_game_id = boxscore_url.split('/')[-1].replace('.html', '')
            home_team = row['home_team']
            visitor_team = row['visitor_team']
            
            # 处理分数字段（可能是带小数点的字符串）
            home_score = row['home_score']
            if home_score and home_score != 'nan':
                home_score = int(float(home_score))
            else:
                home_score = None
                
            visitor_score = row['visitor_score']
            if visitor_score and visitor_score != 'nan':
                visitor_score = int(float(visitor_score))
            else:
                visitor_score = None
                
            game_date = row['game_date']
            
            # 转换为缩写
            home_team_abbr = team_mapping.get(home_team, home_team[:3].upper())
            
            # 根据BR规则生成nba_id: 2 + 年份后两位 + 0 + 序号
            year = game_date[:4]
            # 计算序号（基于日期排序）
            seq = len(games_data) + 1
            nba_id = int(f"2{year[2:]}0{seq:04d}")
            
            games_data.append({
                'our_id': our_game_id,
                'nba_id': nba_id,
                'season': int(year),
                'home_score': home_score,
                'visitor_score': visitor_score,
                'home_team_abbr': home_team_abbr,
                'game_date': game_date
            })

print(f"从CSV读取了 {len(games_data)} 场比赛")

# 检查并添加到映射表
with db.get_cursor() as cur:
    # 获取已有的crawled_id
    cur.execute("SELECT crawled_id FROM game_id_mapping")
    existing = set([r[0] for r in cur.fetchall()])
    print(f"映射表中已有 {len(existing)} 条记录")
    
    # 找出缺失的映射
    missing = [g for g in games_data if g['our_id'] not in existing]
    print(f"需要添加 {len(missing)} 条新映射")
    
    # 添加新映射
    added = 0
    for game in missing:
        try:
            cur.execute("""
                INSERT INTO game_id_mapping (crawled_id, nba_id, season, home_score, visitor_score)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (crawled_id) DO NOTHING
            """, (game['our_id'], game['nba_id'], game['season'], game['home_score'], game['visitor_score']))
            added += 1
            if added % 100 == 0:
                print(f"  已添加 {added} 条...")
        except Exception as e:
            print(f"  ⚠️ 添加 {game['our_id']} 失败: {e}")
    
    # 提交（使用cursor的connection属性）
    cur.connection.commit()
    print(f"\n✅ 已添加 {added} 条新映射")
    
    # 最终统计
    cur.execute("SELECT COUNT(*) FROM game_id_mapping")
    total = cur.fetchone()[0]
    print(f"映射表总计: {total} 条记录")

print("\n" + "="*60)
print("BR格式 → 我们格式 转换完成！")
print("="*60)
