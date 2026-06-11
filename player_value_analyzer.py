#!/usr/bin/env python3
"""
NBA球员价值综合分析系统
分析球员的投篮效率、终结方式、关键时刻表现和对位数据
"""
import psycopg2
import json
from collections import defaultdict
from datetime import datetime

class PlayerValueAnalyzer:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname='nba', user='postgres', password='postgres',
            host='localhost', port='5433'
        )
    
    def close(self):
        self.conn.close()
    
    def get_player_stats(self, player_name=None, season=None, min_shots=50):
        """获取球员基础统计"""
        cursor = self.conn.cursor()
        
        query = """
            SELECT 
                player,
                team,
                season,
                COUNT(*) as total_events,
                SUM(CASE WHEN event_type LIKE 'Made%%' THEN 1 ELSE 0 END) as made_shots,
                SUM(CASE WHEN event_type LIKE 'Missed%%' THEN 1 ELSE 0 END) as missed_shots,
                AVG(dist) as avg_distance,
                SUM(CASE WHEN event_type LIKE 'Made%%' AND dist <= 5 THEN 1 ELSE 0 END) as close_made,
                SUM(CASE WHEN (event_type LIKE 'Made%%' OR event_type LIKE 'Missed%%') AND dist <= 5 THEN 1 ELSE 0 END) as close_attempts,
                SUM(CASE WHEN event_type LIKE 'Made%%' AND dist > 5 AND dist <= 15 THEN 1 ELSE 0 END) as mid_made,
                SUM(CASE WHEN (event_type LIKE 'Made%%' OR event_type LIKE 'Missed%%') AND dist > 5 AND dist <= 15 THEN 1 ELSE 0 END) as mid_attempts,
                SUM(CASE WHEN event_type LIKE 'Made%%' AND dist > 22 THEN 1 ELSE 0 END) as three_made,
                SUM(CASE WHEN (event_type LIKE 'Made%%' OR event_type LIKE 'Missed%%') AND dist > 22 THEN 1 ELSE 0 END) as three_attempts
            FROM pbp_all
            WHERE event_type LIKE 'Made%%' OR event_type LIKE 'Missed%%'
        """
        
        params = []
        if player_name:
            query += " AND player ILIKE %s"
            params.append(f"%{player_name}%")
        if season:
            query += " AND season = %s"
            params.append(season)
        
        query += """
            GROUP BY player, team, season
            HAVING COUNT(*) >= %s
            ORDER BY total_events DESC
        """
        params.append(min_shots)
        
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            player, team, season, total, made, missed, avg_dist, close_m, close_a, mid_m, mid_a, three_m, three_a = row
            
            total_shots = made + missed if made and missed else 1
            close_shots = close_m + close_a if close_m and close_a else 1
            mid_shots = mid_m + mid_a if mid_m and mid_a else 1
            three_shots = three_m + three_a if three_m and three_a else 1
            
            results.append({
                'player': player,
                'team': team,
                'season': season,
                'total_shots': total,
                'made_shots': made,
                'missed_shots': missed,
                'fg_pct': round(made / total_shots * 100, 1) if made else 0,
                'avg_distance': round(avg_dist, 1) if avg_dist else 0,
                'close': {'made': close_m, 'attempts': close_a, 'pct': round(close_m/close_shots*100, 1) if close_a else 0},
                'mid': {'made': mid_m, 'attempts': mid_a, 'pct': round(mid_m/mid_shots*100, 1) if mid_a else 0},
                'three': {'made': three_m, 'attempts': three_a, 'pct': round(three_m/three_shots*100, 1) if three_a else 0}
            })
        
        cursor.close()
        return results
    
    def get_finishing_moves(self, player_name):
        """分析球员终结方式"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT 
                subtype,
                COUNT(*) as attempts,
                SUM(CASE WHEN result = 'Made' THEN 1 ELSE 0 END) as made,
                AVG(dist) as avg_dist
            FROM pbp_all
            WHERE player ILIKE %s
            AND (event_type LIKE 'Made%%' OR event_type LIKE 'Missed%%')
            AND subtype IS NOT NULL
            GROUP BY subtype
            ORDER BY attempts DESC
            LIMIT 15;
        """, (f"%{player_name}%",))
        
        results = []
        for row in cursor.fetchall():
            subtype, attempts, made, avg_dist = row
            results.append({
                'move': subtype,
                'attempts': attempts,
                'made': made,
                'pct': round(made/attempts*100, 1) if attempts else 0,
                'avg_distance': round(avg_dist, 1) if avg_dist else 0
            })
        
        cursor.close()
        return results
    
    def get_clutch_stats(self, player_name, minutes_remaining=5):
        """关键时刻统计（最后N分钟）"""
        cursor = self.conn.cursor()
        
        # 关键时刻定义：最后5分钟，分差10分以内
        cursor.execute("""
            SELECT 
                COUNT(*) as shots,
                SUM(CASE WHEN result = 'Made' THEN 1 ELSE 0 END) as made,
                AVG(dist) as avg_dist
            FROM pbp_all
            WHERE player ILIKE %s
            AND clock_seconds <= %s * 60
            AND clock_seconds > 0
            AND (event_type LIKE 'Made%%' OR event_type LIKE 'Missed%%')
            AND (
                ABS(h_pts - a_pts) <= 10 
                OR period > 4
            );
        """, (f"%{player_name}%", minutes_remaining))
        
        row = cursor.fetchone()
        shots, made, avg_dist = row
        
        cursor.close()
        
        return {
            'minutes_remaining': minutes_remaining,
            'shots': shots,
            'made': made,
            'pct': round(made/shots*100, 1) if shots else 0,
            'avg_distance': round(avg_dist, 1) if avg_dist else 0
        }
    
    def get_shooting_zones(self, player_name):
        """投篮热区分析"""
        cursor = self.conn.cursor()
        
        # 将球场分成多个区域
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN x < -220 AND y > 75 THEN 'Left Corner 3'
                    WHEN x > 220 AND y > 75 THEN 'Right Corner 3'
                    WHEN y > 235 AND x > -75 AND x < 75 THEN 'Top of Key'
                    WHEN y > 180 AND x <= -75 THEN 'Left Wing'
                    WHEN y > 180 AND x >= 75 THEN 'Right Wing'
                    WHEN y <= 180 AND y > 100 AND x < 0 THEN 'Left Baseline'
                    WHEN y <= 180 AND y > 100 AND x > 0 THEN 'Right Baseline'
                    WHEN dist <= 5 THEN 'Paint'
                    WHEN dist <= 10 THEN 'Mid-Range Close'
                    ELSE 'Mid-Range'
                END as zone,
                COUNT(*) as attempts,
                SUM(CASE WHEN result = 'Made' THEN 1 ELSE 0 END) as made
            FROM pbp_all
            WHERE player ILIKE %s
            AND (event_type LIKE 'Made%%' OR event_type LIKE 'Missed%%')
            AND x IS NOT NULL AND y IS NOT NULL
            GROUP BY zone
            ORDER BY attempts DESC;
        """, (f"%{player_name}%",))
        
        results = []
        for row in cursor.fetchall():
            zone, attempts, made = row
            results.append({
                'zone': zone,
                'attempts': attempts,
                'made': made,
                'pct': round(made/attempts*100, 1) if attempts else 0
            })
        
        cursor.close()
        return results
    
    def get_matchup_stats(self, player_name):
        """球员对位数据"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT 
                opponent,
                COUNT(*) as possessions,
                SUM(CASE WHEN result = 'Made' THEN 1 ELSE 0 END) as points
            FROM (
                SELECT 
                    p.player as scorer,
                    p.team as scorer_team,
                    CASE WHEN h.team = p.team THEN a.team ELSE h.team END as opponent,
                    p.result,
                    p.dist
                FROM pbp_all p
                LEFT JOIN pbp_all h ON p.gameid = h.gameid AND p.eventnum = h.eventnum AND h.team = p.team
                LEFT JOIN pbp_all a ON p.gameid = a.gameid AND p.eventnum = a.eventnum AND a.team != p.team
                WHERE p.player ILIKE %s
                AND p.result = 'Made'
            ) sub
            GROUP BY opponent
            ORDER BY possessions DESC
            LIMIT 10;
        """, (f"%{player_name}%",))
        
        results = []
        for row in cursor.fetchall():
            opponent, possessions, points = row
            results.append({
                'opponent': opponent,
                'possessions': possessions,
                'points': points,
                'ppa': round(points/possessions*2, 2) if possessions else 0  # points per attempt
            })
        
        cursor.close()
        return results
    
    def get_career_timeline(self, player_name):
        """球员职业生涯时间线"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT 
                season,
                team,
                COUNT(*) as shots,
                SUM(CASE WHEN result = 'Made' THEN 1 ELSE 0 END) as made,
                AVG(dist) as avg_dist
            FROM pbp_all
            WHERE player ILIKE %s
            AND (event_type LIKE 'Made%%' OR event_type LIKE 'Missed%%')
            GROUP BY season, team
            ORDER BY season;
        """, (f"%{player_name}%",))
        
        results = []
        for row in cursor.fetchall():
            season, team, shots, made, avg_dist = row
            results.append({
                'season': season,
                'team': team,
                'shots': shots,
                'made': made,
                'pct': round(made/shots*100, 1) if shots else 0,
                'avg_distance': round(avg_dist, 1) if avg_dist else 0
            })
        
        cursor.close()
        return results
    
    def get_on_off_impact(self, player_name):
        """On-Off正负值分析"""
        cursor = self.conn.cursor()
        
        # 获取球员在场和不在场时的球队得失分
        cursor.execute("""
            WITH player_games AS (
                SELECT DISTINCT gameid, team
                FROM pbp_all
                WHERE player ILIKE %s
            ),
            scoring AS (
                SELECT 
                    pg.gameid,
                    pg.team,
                    CASE WHEN p.team = pg.team THEN 'with' ELSE 'against' END as context,
                    p.h_pts - p.a_pts as point_diff
                FROM player_games pg
                JOIN pbp_all p ON pg.gameid = p.gameid AND p.period = 1
            )
            SELECT 
                context,
                COUNT(DISTINCT gameid) as games,
                AVG(point_diff) as avg_point_diff
            FROM scoring
            GROUP BY context;
        """, (f"%{player_name}%",))
        
        row = cursor.fetchone()
        cursor.close()
        
        return {
            'with_player': {'games': row[1] if row and row[0] == 'with' else 0, 'avg_diff': round(row[2], 1) if row and row[0] == 'with' and row[2] else 0},
            'against_player': {'games': 0, 'avg_diff': 0}
        }
    
    def analyze_player(self, player_name):
        """综合分析球员价值"""
        print(f"\n{'='*70}")
        print(f"🏀 球员价值分析: {player_name}")
        print(f"{'='*70}")
        
        # 基础统计
        stats = self.get_player_stats(player_name=player_name, min_shots=100)
        if not stats:
            print(f"未找到球员: {player_name}")
            return None
        
        # 取最近赛季的数据
        latest = stats[0]
        print(f"\n📊 当前数据 ({latest['season']}赛季 @ {latest['team']})")
        print("-" * 50)
        print(f"  总投篮: {latest['total_shots']}次 ({latest['made_shots']}命中 {latest['fg_pct']}%)")
        print(f"  平均距离: {latest['avg_distance']}英尺")
        
        print(f"\n📍 投篮区域分布:")
        print(f"  禁区(0-5ft): {latest['close']['attempts']}次, {latest['close']['pct']}%命中")
        print(f"  中距离(5-15ft): {latest['mid']['attempts']}次, {latest['mid']['pct']}%命中")
        print(f"  三分(22+ft): {latest['three']['attempts']}次, {latest['three']['pct']}%命中")
        
        # 终结方式
        finishing = self.get_finishing_moves(player_name)
        if finishing:
            print(f"\n🎯 终结方式 (TOP 5):")
            for i, move in enumerate(finishing[:5], 1):
                print(f"  {i}. {move['move']}: {move['attempts']}次, {move['pct']}%命中")
        
        # 关键时刻
        clutch = self.get_clutch_stats(player_name)
        print(f"\n⏱️ 关键时刻表现 (最后5分钟):")
        print(f"  投篮: {clutch['shots']}次, {clutch['pct']}%命中")
        print(f"  平均距离: {clutch['avg_distance']}英尺")
        
        # 投篮热区
        zones = self.get_shooting_zones(player_name)
        if zones:
            print(f"\n🗺️ 投篮热区:")
            for zone in zones[:5]:
                print(f"  {zone['zone']}: {zone['attempts']}次, {zone['pct']}%命中率")
        
        # 对位数据
        matchups = self.get_matchup_stats(player_name)
        if matchups:
            print(f"\n⚔️ 对位表现 (对阵TOP球队):")
            for mu in matchups[:3]:
                print(f"  vs {mu['opponent']}: {mu['possessions']}次出手, {mu['points']}分 ({mu['ppa']}分/次)")
        
        # 职业生涯时间线
        timeline = self.get_career_timeline(player_name)
        if len(timeline) > 1:
            print(f"\n📈 职业生涯轨迹 ({len(timeline)}个赛季):")
            for t in timeline[-5:]:
                print(f"  {t['season']} @ {t['team']}: {t['shots']}次投篮, {t['pct']}%命中")
        
        return {
            'basic': latest,
            'finishing': finishing[:5],
            'clutch': clutch,
            'zones': zones[:5],
            'matchups': matchups[:5],
            'timeline': timeline
        }


def main():
    analyzer = PlayerValueAnalyzer()
    
    print("\n" + "="*70)
    print("🏀 NBA球员价值综合分析系统")
    print("="*70)
    
    # 演示分析几个球员
    test_players = ['LeBron James', 'Stephen Curry', 'Kevin Durant', 'Giannis Antetokounmpo']
    
    for player in test_players:
        result = analyzer.analyze_player(player)
        if result:
            print()
    
    # 交互式查询
    print("\n" + "="*70)
    print("🔍 查询其他球员")
    print("="*70)
    print("输入球员名字进行分析（或输入'quit'退出）")
    
    while True:
        try:
            player = input("\n球员名字: ").strip()
            if player.lower() == 'quit':
                break
            if player:
                analyzer.analyze_player(player)
        except KeyboardInterrupt:
            break
    
    analyzer.close()
    print("\n👋 再见！")


if __name__ == "__main__":
    main()
