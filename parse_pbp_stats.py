import psycopg2
import os
import re
from collections import defaultdict

db_config = {
    'dbname': os.getenv('POSTGRES_DB', 'nba'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5433')
}

def parse_pbp_description(description):
    """解析 play-by-play 描述，提取球员名字和得分事件"""
    # 匹配得分事件: "Player makes X-pt jump shot/layup/etc"
    score_pattern = r'([A-Z]\. [A-Za-z]+) makes (\d)-pt'
    match = re.search(score_pattern, description)

    if match:
        player_name = match.group(1)
        points = int(match.group(2))
        return player_name, points

    # 匹配罚球得分: "Player makes free throw"
    ft_pattern = r'([A-Z]\. [A-Za-z]+) makes free throw'
    match = re.search(ft_pattern, description)

    if match:
        player_name = match.group(1)
        points = 1
        return player_name, points

    return None, None

try:
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    # 获取一个比赛的 play_by_play 数据
    game_id = 8582
    print(f'分析 game_id={game_id} 的 play_by_play 数据:')

    cursor.execute("""
        SELECT
            id,
            game_id,
            period,
            clock,
            description,
            home_score,
            away_score
        FROM play_by_play
        WHERE game_id = %s
        ORDER BY period, clock DESC
    """, (game_id,))

    rows = cursor.fetchall()

    # 统计每个球员的得分
    player_stats = defaultdict(lambda: {
        'points': 0,
        'fg': 0,
        'fga': 0,
        'three_p': 0,
        'three_pa': 0,
        'ft': 0,
        'fta': 0
    })

    for row in rows:
        description = row[4]
        if description:
            player_name, points = parse_pbp_description(description)

            if player_name and points:
                player_stats[player_name]['points'] += points

                if points == 1:
                    player_stats[player_name]['ft'] += 1
                    player_stats[player_name]['fta'] += 1
                elif points == 2:
                    player_stats[player_name]['fg'] += 1
                    player_stats[player_name]['fga'] += 1
                elif points == 3:
                    player_stats[player_name]['fg'] += 1
                    player_stats[player_name]['fga'] += 1
                    player_stats[player_name]['three_p'] += 1
                    player_stats[player_name]['three_pa'] += 1

    # 显示球员统计数据
    print('\n球员得分统计:')
    for player, stats in sorted(player_stats.items(), key=lambda x: x[1]['points'], reverse=True):
        print(f'  {player}: {stats["points"]} 分')
        print(f'    FG: {stats["fg"]}/{stats["fga"]}')
        print(f'    3P: {stats["three_p"]}/{stats["three_pa"]}')
        print(f'    FT: {stats["ft"]}/{stats["fta"]}')
        print()

    conn.close()
except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()