#!/usr/bin/env python3
"""
投篮热区可视化工具
结合SVG球场图片展示球员投篮数据
"""
import psycopg2
import json

class ShotChartVisualizer:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname='nba', user='postgres', password='postgres',
            host='localhost', port='5433'
        )
    
    def close(self):
        self.conn.close()
    
    def get_player_shots(self, player_name):
        """获取球员所有投篮数据"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT 
                x, y, dist, result, season
            FROM pbp_all
            WHERE player ILIKE %s
            AND (event_type LIKE 'Made%%' OR event_type LIKE 'Missed%%')
            AND x IS NOT NULL AND y IS NOT NULL;
        """, (f"%{player_name}%",))
        
        shots = []
        for row in cursor.fetchall():
            x, y, dist, result, season = row
            shots.append({
                'x': float(x),
                'y': float(y),
                'dist': int(dist) if dist else 0,
                'made': result == 'Made',
                'season': season
            })
        
        cursor.close()
        return shots
    
    def get_zone_stats(self, player_name):
        """获取各区域统计"""
        cursor = self.conn.cursor()
        
        zones = [
            {'name': '禁区', 'sql': 'dist <= 5'},
            {'name': '近距离中距离', 'sql': 'dist > 5 AND dist <= 10'},
            {'name': '中距离', 'sql': 'dist > 10 AND dist <= 18'},
            {'name': '长两分', 'sql': 'dist > 18 AND dist <= 22'},
            {'name': '三分', 'sql': 'dist > 22'},
        ]
        
        results = []
        for zone in zones:
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as attempts,
                    SUM(CASE WHEN result = 'Made' THEN 1 ELSE 0 END) as made
                FROM pbp_all
                WHERE player ILIKE %s
                AND (event_type LIKE 'Made%%' OR event_type LIKE 'Missed%%')
                AND {zone['sql']};
            """, (f"%{player_name}%",))
            
            row = cursor.fetchone()
            attempts, made = row
            if attempts > 0:
                results.append({
                    'zone': zone['name'],
                    'attempts': attempts,
                    'made': made,
                    'pct': round(made / attempts * 100, 1)
                })
        
        cursor.close()
        return results
    
    def save_shot_chart(self, player_name, output_file=None):
        """保存投篮热区HTML文件"""
        shots = self.get_player_shots(player_name)
        zone_stats = self.get_zone_stats(player_name)
        
        if not shots:
            print(f"未找到球员 {player_name} 的数据")
            return None
        
        total_shots = len(shots)
        made_count = sum(1 for s in shots if s['made'])
        fg_pct = round(made_count / total_shots * 100, 1)
        
        # 生成区域统计卡片
        zone_cards = ""
        for z in zone_stats:
            zone_cards += f"""
            <div class="zone-card">
                <div class="zone-name">{z['zone']}</div>
                <div class="zone-pct">{z['pct']}%</div>
                <div style="color: #aaa; font-size: 0.8rem;">{z['made']}/{z['attempts']}次</div>
            </div>
            """
        
        # 生成HTML文件
        html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{player_name} 投篮热区</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #fff; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ text-align: center; margin-bottom: 20px; }}
        header h1 {{ color: #feca57; }}
        .stats-bar {{ display: flex; justify-content: center; gap: 40px; margin-bottom: 20px; }}
        .stat-item {{ text-align: center; }}
        .stat-value {{ font-size: 2rem; color: #feca57; font-weight: bold; }}
        .stat-label {{ color: #aaa; }}
        .court-container {{ position: relative; width: 910px; height: 855px; margin: 0 auto; }}
        .court-bg {{ width: 100%; height: 100%; position: absolute; top: 0; left: 0; z-index: 1; }}
        .shot-point {{ position: absolute; border-radius: 50%; z-index: 2; transform: translate(-50%, -50%); cursor: pointer; }}
        .shot-made {{ background: rgba(46, 213, 115, 0.7); border: 2px solid #2ed573; }}
        .shot-missed {{ background: rgba(255, 107, 107, 0.5); border: 2px solid #ff6b6b; }}
        .zone-stats {{ display: flex; justify-content: center; gap: 20px; margin-top: 30px; flex-wrap: wrap; }}
        .zone-card {{ background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; text-align: center; }}
        .zone-name {{ color: #feca57; font-weight: bold; }}
        .zone-pct {{ font-size: 1.5rem; font-weight: bold; }}
        .legend {{ display: flex; justify-content: center; gap: 30px; margin-top: 20px; }}
        .legend-item {{ display: flex; align-items: center; gap: 10px; }}
        .legend-dot {{ width: 20px; height: 20px; border-radius: 50%; }}
        .legend-dot.made {{ background: #2ed573; }}
        .legend-dot.missed {{ background: #ff6b6b; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏀 {player_name} 投篮热区</h1>
        </header>
        
        <div class="stats-bar">
            <div class="stat-item"><div class="stat-value">{total_shots}</div><div class="stat-label">总出手</div></div>
            <div class="stat-item"><div class="stat-value">{made_count}</div><div class="stat-label">命中</div></div>
            <div class="stat-item"><div class="stat-value">{fg_pct}%</div><div class="stat-label">命中率</div></div>
        </div>
        
        <div class="court-container">
            <img class="court-bg" src="NBAlogo/court-nba-bbr.svg" />
            <div id="shot-points"></div>
        </div>
        
        <div class="legend">
            <div class="legend-item"><div class="legend-dot made"></div><span>命中</span></div>
            <div class="legend-item"><div class="legend-dot missed"></div><span>未命中</span></div>
        </div>
        
        <div class="zone-stats">
            {zone_cards}
        </div>
    </div>
    
    <script>
        const shots = {json.dumps(shots)};
        const container = document.getElementById('shot-points');
        
        shots.forEach(shot => {{
            const point = document.createElement('div');
            point.className = 'shot-point ' + (shot.made ? 'shot-made' : 'shot-missed');
            const size = Math.max(6, Math.min(15, 20 - shot.dist/4));
            point.style.width = size + 'px';
            point.style.height = size + 'px';
            point.style.left = shot.x + 'px';
            point.style.top = shot.y + 'px';
            point.title = '距离: ' + shot.dist + '英尺\\n结果: ' + (shot.made ? '命中' : '未命中') + '\\n赛季: ' + shot.season;
            container.appendChild(point);
        }});
    </script>
</body>
</html>'''
        
        if not output_file:
            output_file = f"shot_chart_{player_name.replace(' ', '_')}.html"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ 投篮热区图表已保存到: {output_file}")
        return output_file


def main():
    visualizer = ShotChartVisualizer()
    
    print("=" * 70)
    print("🎯 投篮热区可视化工具")
    print("=" * 70)
    
    test_players = ['S. Curry', 'K. Durant', 'L. James']
    
    for player in test_players:
        print(f"\n📊 正在生成 {player} 的投篮热区...")
        visualizer.save_shot_chart(player)
    
    print("\n" + "=" * 70)
    print("🔍 查询其他球员（输入'quit'退出）")
    print("=" * 70)
    
    while True:
        try:
            player = input("\n球员名字: ").strip()
            if player.lower() == 'quit':
                break
            if player:
                visualizer.save_shot_chart(player)
        except KeyboardInterrupt:
            break
    
    visualizer.close()
    print("\n👋 再见！")


if __name__ == "__main__":
    main()
