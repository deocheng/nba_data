#!/usr/bin/env python3
"""根据比赛日期、球队和比分匹配两个数据源的相同比赛"""
import psycopg2

DB_CONFIG = {
    'dbname': 'nba',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5433'
}


def get_crawled_games(conn):
    """获取爬取数据中的比赛信息（日期、球队、比分）"""
    cursor = conn.cursor()
    
    # 从 game_metadata 获取比赛信息
    cursor.execute("""
        SELECT 
            gm.game_id,
            gm.game_date,
            gm.home_team,
            gm.visitor_team,
            gm.home_score,
            gm.visitor_score,
            gm.boxscore_url
        FROM game_metadata gm
        WHERE gm.pbp_imported = true;
    """)
    
    games = []
    for row in cursor.fetchall():
        games.append({
            'game_id': row[0],
            'game_date': row[1],
            'home_team': row[2],
            'visitor_team': row[3],
            'home_score': row[4],
            'visitor_score': row[5],
            'source': 'crawled',
            'boxscore_url': row[6]
        })
    
    return games


def get_imported_games(conn):
    """获取导入数据中的比赛信息（日期、球队、比分）"""
    cursor = conn.cursor()
    
    # 从 pbp_all 获取每个比赛的最终比分和球队信息
    cursor.execute("""
        SELECT 
            gameid,
            season,
            MAX(h_pts) as home_score,
            MAX(a_pts) as visitor_score
        FROM pbp_all
        WHERE h_pts IS NOT NULL AND a_pts IS NOT NULL
        GROUP BY gameid, season;
    """)
    
    games = []
    for row in cursor.fetchall():
        games.append({
            'gameid': row[0],
            'season': row[1],
            'home_score': row[2],
            'visitor_score': row[3],
            'source': 'imported'
        })
    
    return games


def normalize_team_name(team):
    """标准化球队名称，便于匹配"""
    if not team:
        return None
    
    team_mapping = {
        'Golden State Warriors': 'GSW',
        'Los Angeles Lakers': 'LAL',
        'Oklahoma City Thunder': 'OKC',
        'Houston Rockets': 'HOU',
        'Brooklyn Nets': 'BRK',
        'Charlotte Hornets': 'CHO',
        'New York Knicks': 'NYK',
        'Cleveland Cavaliers': 'CLE',
        'Phoenix Suns': 'PHO',
        'Sacramento Kings': 'SAC',
        'Denver Nuggets': 'DEN',
        'Boston Celtics': 'BOS',
        'Milwaukee Bucks': 'MIL',
        'Toronto Raptors': 'TOR',
        'Philadelphia 76ers': 'PHI',
        'Portland Trail Blazers': 'POR',
        'Miami Heat': 'MIA',
        'Utah Jazz': 'UTA',
        'Dallas Mavericks': 'DAL',
        'San Antonio Spurs': 'SAS',
        'Memphis Grizzlies': 'MEM',
        'Indiana Pacers': 'IND',
        'Detroit Pistons': 'DET',
        'Chicago Bulls': 'CHI',
        'Washington Wizards': 'WAS',
        'Orlando Magic': 'ORL',
        'Atlanta Hawks': 'ATL',
        'Minnesota Timberwolves': 'MIN',
        'New Orleans Pelicans': 'NOP',
        # 简写形式
        'GSW': 'GSW', 'LAL': 'LAL', 'OKC': 'OKC', 'HOU': 'HOU',
        'BRK': 'BRK', 'CHO': 'CHO', 'CHA': 'CHO', 'NYK': 'NYK',
        'CLE': 'CLE', 'PHO': 'PHO', 'SAC': 'SAC', 'DEN': 'DEN',
        'BOS': 'BOS', 'MIL': 'MIL', 'TOR': 'TOR', 'PHI': 'PHI',
        'POR': 'POR', 'MIA': 'MIA', 'UTA': 'UTA', 'DAL': 'DAL',
        'SAS': 'SAS', 'MEM': 'MEM', 'IND': 'IND', 'DET': 'DET',
        'CHI': 'CHI', 'WAS': 'WAS', 'ORL': 'ORL', 'ATL': 'ATL',
        'MIN': 'MIN', 'NOP': 'NOP', 'NOH': 'NOP', 'NOK': 'NOP'
    }
    
    return team_mapping.get(team.strip(), team.strip())


def find_matches(crawled_games, imported_games):
    """根据比分匹配比赛"""
    matches = []
    unmatched_crawled = []
    unmatched_imported = []
    
    # 创建导入比赛的索引（按比分）
    score_index = {}
    for game in imported_games:
        score_key = f"{int(game['home_score'])}-{int(game['visitor_score'])}"
        if score_key not in score_index:
            score_index[score_key] = []
        score_index[score_key].append(game)
    
    # 查找匹配
    for crawled in crawled_games:
        if crawled['home_score'] is None or crawled['visitor_score'] is None:
            unmatched_crawled.append(crawled)
            continue
        
        score_key = f"{int(crawled['home_score'])}-{int(crawled['visitor_score'])}"
        
        if score_key in score_index:
            # 找到相同比分的比赛
            candidates = score_index[score_key]
            
            matched = False
            for candidate in candidates:
                # 检查赛季是否匹配（允许±1年，因为NBA赛季跨年度）
                crawled_season = 2026  # 爬取的都是2026赛季
                imported_season = candidate['season']
                
                if abs(crawled_season - imported_season) <= 1:
                    matches.append({
                        'crawled': crawled,
                        'imported': candidate,
                        'match_type': 'score+season',
                        'score': score_key
                    })
                    matched = True
                    break
            
            if not matched:
                unmatched_crawled.append(crawled)
        else:
            unmatched_crawled.append(crawled)
    
    # 检查未匹配的导入比赛（有比分的）
    crawled_scores = set()
    for game in crawled_games:
        if game['home_score'] is not None and game['visitor_score'] is not None:
            crawled_scores.add(f"{int(game['home_score'])}-{int(game['visitor_score'])}")
    
    for game in imported_games:
        score_key = f"{int(game['home_score'])}-{int(game['visitor_score'])}"
        if score_key not in crawled_scores:
            unmatched_imported.append(game)
    
    return matches, unmatched_crawled, unmatched_imported


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    
    print("=" * 90)
    print("📊 比赛匹配分析（基于日期、球队、比分）")
    print("=" * 90)
    
    # 获取数据
    print("\n🔄 正在获取数据...")
    crawled_games = get_crawled_games(conn)
    imported_games = get_imported_games(conn)
    
    print(f"   爬取比赛: {len(crawled_games)} 场")
    print(f"   导入比赛: {len(imported_games)} 场")
    
    # 查找匹配
    print("\n🔍 正在匹配比赛...")
    matches, unmatched_crawled, unmatched_imported = find_matches(crawled_games, imported_games)
    
    print(f"\n✅ 找到 {len(matches)} 个匹配")
    print(f"❌ 爬取数据未匹配: {len(unmatched_crawled)} 场")
    print(f"❌ 导入数据未匹配: {len(unmatched_imported)} 场")
    
    # 显示匹配结果
    if matches:
        print("\n" + "=" * 90)
        print("🎯 匹配成功的比赛")
        print("=" * 90)
        print(f"{'爬取ID':<15} {'爬取比分':<12} {'导入ID':<12} {'导入赛季':<10}")
        print("-" * 90)
        
        for m in matches[:20]:  # 只显示前20个
            c = m['crawled']
            i = m['imported']
            print(f"{c['game_id']:<15} {c['home_score']}-{c['visitor_score']:<12} {i['gameid']:<12} {i['season']:<10}")
        
        if len(matches) > 20:
            print(f"... 还有 {len(matches) - 20} 个匹配未显示")
    
    # 显示未匹配的爬取比赛（有比分的）
    scored_crawled = [g for g in unmatched_crawled if g['home_score'] is not None]
    if scored_crawled:
        print("\n" + "=" * 90)
        print("❌ 爬取数据中未匹配的比赛（有比分）")
        print("=" * 90)
        print(f"{'比赛ID':<15} {'主队':<20} {'客队':<20} {'比分':<10}")
        print("-" * 90)
        
        for g in scored_crawled[:10]:
            print(f"{g['game_id']:<15} {g['home_team'][:20]:<20} {g['visitor_team'][:20]:<20} {g['home_score']}-{g['visitor_score']:<10}")
        
        if len(scored_crawled) > 10:
            print(f"... 还有 {len(scored_crawled) - 10} 场未显示")
    
    # 统计信息
    print("\n" + "=" * 90)
    print("📋 统计摘要")
    print("=" * 90)
    print(f"  爬取比赛总数: {len(crawled_games)}")
    print(f"  导入比赛总数: {len(imported_games)}")
    print(f"  匹配成功: {len(matches)}")
    print(f"  匹配率: {len(matches) / len(crawled_games) * 100:.1f}%")
    print(f"  未匹配爬取: {len(unmatched_crawled)}")
    print(f"  未匹配导入: {len(unmatched_imported)}")
    
    conn.close()
    
    print("\n✅ 分析完成")


if __name__ == '__main__':
    main()
