#!/usr/bin/env python3
"""创建球队映射表 - 处理球队更名和合并"""
import psycopg2

DB_CONFIG = {
    'dbname': 'nba',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5433'
}

# NBA球队更名历史映射
TEAM_MAPPING = {
    # 夏洛特黄蜂/山猫
    'CHH': {'current': 'CHA', 'name': '夏洛特黄蜂', 'history': ['CHH']},
    'CHA': {'current': 'CHA', 'name': '夏洛特黄蜂', 'history': ['CHA']},
    
    # 布鲁克林篮网
    'NJN': {'current': 'BKN', 'name': '布鲁克林篮网', 'history': ['NJN']},
    'BKN': {'current': 'BKN', 'name': '布鲁克林篮网', 'history': ['BKN']},
    
    # 新奥尔良鹈鹕
    'NOH': {'current': 'NOP', 'name': '新奥尔良鹈鹕', 'history': ['NOH', 'NOK']},
    'NOK': {'current': 'NOP', 'name': '新奥尔良鹈鹕', 'history': ['NOH', 'NOK']},
    'NOP': {'current': 'NOP', 'name': '新奥尔良鹈鹕', 'history': ['NOP']},
    
    # 俄克拉荷马城雷霆
    'SEA': {'current': 'OKC', 'name': '俄克拉荷马城雷霆', 'history': ['SEA']},
    'OKC': {'current': 'OKC', 'name': '俄克拉荷马城雷霆', 'history': ['OKC']},
    
    # 孟菲斯灰熊
    'VAN': {'current': 'MEM', 'name': '孟菲斯灰熊', 'history': ['VAN']},
    'MEM': {'current': 'MEM', 'name': '孟菲斯灰熊', 'history': ['MEM']},
    
    # 其他保持不变的球队
    'ATL': {'current': 'ATL', 'name': '亚特兰大老鹰', 'history': ['ATL']},
    'BOS': {'current': 'BOS', 'name': '波士顿凯尔特人', 'history': ['BOS']},
    'CHI': {'current': 'CHI', 'name': '芝加哥公牛', 'history': ['CHI']},
    'CLE': {'current': 'CLE', 'name': '克利夫兰骑士', 'history': ['CLE']},
    'DAL': {'current': 'DAL', 'name': '达拉斯独行侠', 'history': ['DAL']},
    'DEN': {'current': 'DEN', 'name': '丹佛掘金', 'history': ['DEN']},
    'DET': {'current': 'DET', 'name': '底特律活塞', 'history': ['DET']},
    'GSW': {'current': 'GSW', 'name': '金州勇士', 'history': ['GSW']},
    'HOU': {'current': 'HOU', 'name': '休斯顿火箭', 'history': ['HOU']},
    'IND': {'current': 'IND', 'name': '印第安纳步行者', 'history': ['IND']},
    'LAC': {'current': 'LAC', 'name': '洛杉矶快船', 'history': ['LAC']},
    'LAL': {'current': 'LAL', 'name': '洛杉矶湖人', 'history': ['LAL']},
    'MIA': {'current': 'MIA', 'name': '迈阿密热火', 'history': ['MIA']},
    'MIL': {'current': 'MIL', 'name': '密尔沃基雄鹿', 'history': ['MIL']},
    'MIN': {'current': 'MIN', 'name': '明尼苏达森林狼', 'history': ['MIN']},
    'NYK': {'current': 'NYK', 'name': '纽约尼克斯', 'history': ['NYK']},
    'ORL': {'current': 'ORL', 'name': '奥兰多魔术', 'history': ['ORL']},
    'PHI': {'current': 'PHI', 'name': '费城76人', 'history': ['PHI']},
    'PHX': {'current': 'PHX', 'name': '菲尼克斯太阳', 'history': ['PHX']},
    'POR': {'current': 'POR', 'name': '波特兰开拓者', 'history': ['POR']},
    'SAC': {'current': 'SAC', 'name': '萨克拉门托国王', 'history': ['SAC']},
    'SAS': {'current': 'SAS', 'name': '圣安东尼奥马刺', 'history': ['SAS']},
    'TOR': {'current': 'TOR', 'name': '多伦多猛龙', 'history': ['TOR']},
    'UTA': {'current': 'UTA', 'name': '犹他爵士', 'history': ['UTA']},
    'WAS': {'current': 'WAS', 'name': '华盛顿奇才', 'history': ['WAS']}
}


def create_team_mapping_table():
    """创建球队映射表"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 创建球队映射表
    cursor.execute("""
        DROP TABLE IF EXISTS team_mapping;
        CREATE TABLE team_mapping (
            id SERIAL PRIMARY KEY,
            team_code VARCHAR(10) NOT NULL,
            current_code VARCHAR(10) NOT NULL,
            team_name VARCHAR(50) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE UNIQUE INDEX idx_team_mapping_code ON team_mapping(team_code);
    """)
    
    # 插入球队映射数据
    for code, info in TEAM_MAPPING.items():
        is_active = (code == info['current'])
        cursor.execute("""
            INSERT INTO team_mapping (team_code, current_code, team_name, is_active)
            VALUES (%s, %s, %s, %s);
        """, (code, info['current'], info['name'], is_active))
    
    conn.commit()
    print("✅ 球队映射表创建完成")
    
    # 统计当前活跃球队
    cursor.execute("SELECT COUNT(DISTINCT current_code) FROM team_mapping WHERE is_active = true;")
    active_teams = cursor.fetchone()[0]
    print(f"📊 当前活跃球队数量: {active_teams}")
    
    # 显示合并后的球队列表
    cursor.execute("SELECT DISTINCT current_code, team_name FROM team_mapping WHERE is_active = true ORDER BY current_code;")
    print("\n🏀 当前活跃球队:")
    for row in cursor.fetchall():
        print(f"   {row[0]} - {row[1]}")
    
    conn.close()


def update_pbp_all_with_current_team():
    """更新pbp_all表添加当前球队代码"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 添加新字段
    cursor.execute("ALTER TABLE pbp_all ADD COLUMN IF NOT EXISTS current_team VARCHAR(10);")
    
    # 更新current_team字段
    cursor.execute("""
        UPDATE pbp_all p
        SET current_team = m.current_code
        FROM team_mapping m
        WHERE p.team = m.team_code;
    """)
    
    conn.commit()
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pbp_all_current_team ON pbp_all(current_team);")
    
    print("\n✅ pbp_all表已更新，添加current_team字段")
    
    conn.close()


if __name__ == '__main__':
    print("=" * 80)
    print("🔧 创建NBA球队映射表")
    print("=" * 80)
    
    create_team_mapping_table()
    update_pbp_all_with_current_team()
    
    print("\n🎉 球队映射表创建完成！")
    print("提示: 现在可以使用current_team字段查询合并后的球队数据")
