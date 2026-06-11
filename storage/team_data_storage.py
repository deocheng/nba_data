#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
球队数据存储模块 - 存储爬取的球队数据到数据库
支持断点续传和数据验证
"""
import sqlite3
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TeamDataStorage:
    """球队数据存储类"""
    
    def __init__(self, db_file='nba_data.db'):
        self.db_file = db_file
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS team_games_crawler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_abbr TEXT NOT NULL,
                season TEXT NOT NULL,
                game_date TEXT,
                game_num INTEGER,
                opponent TEXT,
                result TEXT,
                team_score INTEGER,
                opponent_score INTEGER,
                ot TEXT,
                wl_home TEXT,
                fg INTEGER,
                fga INTEGER,
                fg_pct REAL,
                three_p INTEGER,
                three_pa INTEGER,
                three_p_pct REAL,
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
                pace REAL,
                ftr REAL,
                three_par REAL,
                efg_pct REAL,
                tov_pct REAL,
                orb_pct REAL,
                ft_fga REAL,
                opp_pace REAL,
                opp_ftr REAL,
                opp_efg_pct REAL,
                opp_tov_pct REAL,
                opp_orb_pct REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(team_abbr, season, game_date, opponent)
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_team_games_team_abbr ON team_games_crawler(team_abbr)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_team_games_season ON team_games_crawler(season)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_team_games_date ON team_games_crawler(game_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_team_games_composite ON team_games_crawler(team_abbr, season)')
        
        conn.commit()
        conn.close()
        logger.info("数据库初始化完成")
    
    def validate_data(self, data_dict):
        """验证数据完整性"""
        required_fields = ['team_abbr', 'season', 'game_date']
        
        for field in required_fields:
            if field not in data_dict or pd.isna(data_dict.get(field)):
                return False, f"缺少必填字段: {field}"
        
        return True, None
    
    def insert_game_data(self, game_data):
        """插入单条比赛数据"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO team_games_crawler (
                    team_abbr, season, game_date, game_num, opponent, result,
                    team_score, opponent_score, ot, wl_home,
                    fg, fga, fg_pct, three_p, three_pa, three_p_pct,
                    ft, fta, ft_pct, orb, drb, trb, ast, stl, blk, tov, pf,
                    opp_fg, opp_fga, opp_fg_pct, opp_three_p, opp_three_pa, opp_three_p_pct,
                    opp_ft, opp_fta, opp_ft_pct, opp_orb, opp_drb, opp_trb,
                    opp_ast, opp_stl, opp_blk, opp_tov, opp_pf
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                game_data.get('team_abbr'),
                game_data.get('season'),
                game_data.get('game_date'),
                game_data.get('game_num'),
                game_data.get('opponent'),
                game_data.get('result'),
                game_data.get('team_score'),
                game_data.get('opponent_score'),
                game_data.get('ot'),
                game_data.get('wl_home'),
                game_data.get('fg'),
                game_data.get('fga'),
                game_data.get('fg_pct'),
                game_data.get('three_p'),
                game_data.get('three_pa'),
                game_data.get('three_p_pct'),
                game_data.get('ft'),
                game_data.get('fta'),
                game_data.get('ft_pct'),
                game_data.get('orb'),
                game_data.get('drb'),
                game_data.get('trb'),
                game_data.get('ast'),
                game_data.get('stl'),
                game_data.get('blk'),
                game_data.get('tov'),
                game_data.get('pf'),
                game_data.get('opp_fg'),
                game_data.get('opp_fga'),
                game_data.get('opp_fg_pct'),
                game_data.get('opp_three_p'),
                game_data.get('opp_three_pa'),
                game_data.get('opp_three_p_pct'),
                game_data.get('opp_ft'),
                game_data.get('opp_fta'),
                game_data.get('opp_ft_pct'),
                game_data.get('opp_orb'),
                game_data.get('opp_drb'),
                game_data.get('opp_trb'),
                game_data.get('opp_ast'),
                game_data.get('opp_stl'),
                game_data.get('opp_blk'),
                game_data.get('opp_tov'),
                game_data.get('opp_pf')
            ))
            
            conn.commit()
            return cursor.rowcount > 0
        
        except sqlite3.Error as e:
            logger.error(f"数据库错误: {e}")
            return False
        finally:
            conn.close()
    
    def insert_from_csv(self, csv_file, team_abbr, season):
        """从CSV文件批量导入数据"""
        if not Path(csv_file).exists():
            logger.warning(f"文件不存在: {csv_file}")
            return 0
        
        df = pd.read_csv(csv_file)
        inserted = 0
        
        for _, row in df.iterrows():
            game_data = row.to_dict()
            game_data['team_abbr'] = team_abbr
            game_data['season'] = season
            
            is_valid, error_msg = self.validate_data(game_data)
            if not is_valid:
                logger.debug(f"跳过无效数据: {error_msg}")
                continue
            
            if self.insert_game_data(game_data):
                inserted += 1
        
        logger.info(f"{team_abbr} {season} 赛季: 导入 {inserted} 条数据")
        return inserted
    
    def get_statistics(self, team_abbr=None, season=None):
        """获取统计数据"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        query = "SELECT COUNT(*) FROM team_games_crawler WHERE 1=1"
        params = []
        
        if team_abbr:
            query += " AND team_abbr = ?"
            params.append(team_abbr)
        
        if season:
            query += " AND season = ?"
            params.append(season)
        
        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def get_all_teams(self):
        """获取所有球队列表"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT team_abbr FROM team_games_crawler ORDER BY team_abbr")
        teams = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return teams
    
    def get_all_seasons(self):
        """获取所有赛季列表"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT season FROM team_games_crawler ORDER BY season DESC")
        seasons = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return seasons

def main():
    """测试函数"""
    storage = TeamDataStorage()
    
    logger.info("球队数据存储模块测试")
    
    teams = storage.get_all_teams()
    logger.info(f"已存储的球队数: {len(teams)}")
    
    seasons = storage.get_all_seasons()
    logger.info(f"已存储的赛季数: {len(seasons)}")
    
    if teams:
        for team in teams[:5]:
            count = storage.get_statistics(team_abbr=team)
            logger.info(f"{team}: {count} 条数据")
    
    if seasons:
        for season in seasons[:3]:
            count = storage.get_statistics(season=season)
            logger.info(f"{season}: {count} 条数据")

if __name__ == '__main__':
    main()