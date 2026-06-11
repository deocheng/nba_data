import psycopg2
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NBADatabase:
    def __init__(self):
        self.conn = None
    
    def connect(self):
        try:
            self.conn = psycopg2.connect(
                dbname=os.getenv('POSTGRES_DB', 'nba'),
                user=os.getenv('POSTGRES_USER', 'postgres'),
                password=os.getenv('POSTGRES_PASSWORD', 'postgres'),
                host=os.getenv('POSTGRES_HOST', 'localhost'),
                port=os.getenv('POSTGRES_PORT', '5433')
            )
            logger.info("成功连接PostgreSQL数据库")
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False
    
    def disconnect(self):
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")
    
    def create_tables(self):
        if not self.conn:
            logger.error("数据库未连接")
            return False
        
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS teams (
                    team_id VARCHAR(20) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    abbreviation VARCHAR(10),
                    conference VARCHAR(20),
                    division VARCHAR(50)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    player_id VARCHAR(20) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    position VARCHAR(10),
                    number VARCHAR(10),
                    height VARCHAR(20),
                    weight VARCHAR(20),
                    age INT,
                    experience VARCHAR(10),
                    college VARCHAR(100),
                    salary VARCHAR(50),
                    draft_year INT,
                    draft_pick VARCHAR(20),
                    team_id VARCHAR(20) REFERENCES teams(team_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS games (
                    game_id VARCHAR(20) PRIMARY KEY,
                    home_team VARCHAR(100) NOT NULL,
                    away_team VARCHAR(100) NOT NULL,
                    home_score INT,
                    away_score INT,
                    status VARCHAR(20) NOT NULL,
                    time VARCHAR(20),
                    date DATE NOT NULL
                )
            ''')
            
            self.conn.commit()
            logger.info("数据表创建成功")
            return True
        
        except Exception as e:
            logger.error(f"创建数据表失败: {e}")
            return False
    
    def create_tables_with_source(self):
        if not self.conn:
            logger.error("数据库未连接")
            return False
        
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS teams (
                    team_id VARCHAR(20) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    abbreviation VARCHAR(10),
                    conference VARCHAR(20),
                    division VARCHAR(50),
                    source VARCHAR(50) DEFAULT 'UNKNOWN'
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    player_id VARCHAR(20) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    position VARCHAR(10),
                    number VARCHAR(10),
                    height VARCHAR(20),
                    weight VARCHAR(20),
                    age INT,
                    experience VARCHAR(10),
                    college VARCHAR(100),
                    salary VARCHAR(50),
                    draft_year INT,
                    draft_pick VARCHAR(20),
                    team_id VARCHAR(20) REFERENCES teams(team_id),
                    source VARCHAR(50) DEFAULT 'UNKNOWN'
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS games (
                    game_id VARCHAR(20) PRIMARY KEY,
                    home_team VARCHAR(100) NOT NULL,
                    away_team VARCHAR(100) NOT NULL,
                    home_score INT,
                    away_score INT,
                    status VARCHAR(20) NOT NULL,
                    time VARCHAR(20),
                    date DATE NOT NULL,
                    source VARCHAR(50) DEFAULT 'UNKNOWN'
                )
            ''')
            
            self.conn.commit()
            logger.info("带来源字段的数据表创建成功")
            return True
        
        except Exception as e:
            logger.error(f"创建数据表失败: {e}")
            return False
    
    def clear_table(self, table_name):
        if not self.conn:
            logger.error("数据库未连接")
            return False
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(f'DELETE FROM {table_name}')
            self.conn.commit()
            logger.info(f"成功清空表: {table_name}")
            return True
        except Exception as e:
            logger.error(f"清空表失败: {e}")
            return False
    
    def clear_all_tables(self):
        tables = ['players', 'games', 'teams']
        for table in tables:
            self.clear_table(table)
        return True
    
    def insert_team(self, team_id, name, abbreviation=None, conference=None, division=None, source=None):
        if not self.conn:
            logger.error("数据库未连接")
            return False
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO teams (team_id, name, abbreviation, conference, division, source)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (team_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    abbreviation = EXCLUDED.abbreviation,
                    conference = EXCLUDED.conference,
                    division = EXCLUDED.division,
                    source = EXCLUDED.source
            ''', (team_id, name, abbreviation, conference, division, source or 'UNKNOWN'))
            self.conn.commit()
            logger.info(f"成功插入球队: {name}")
            return True
        except Exception as e:
            logger.error(f"插入球队失败: {e}")
            return False
    
    def insert_player(self, player_id, name, position=None, number=None, height=None, 
                     weight=None, age=None, experience=None, college=None, 
                     salary=None, draft_year=None, draft_pick=None, team_id=None, source=None):
        if not self.conn:
            logger.error("数据库未连接")
            return False
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO players 
                (player_id, name, position, number, height, weight, age, experience, 
                 college, salary, draft_year, draft_pick, team_id, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (player_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    position = EXCLUDED.position,
                    number = EXCLUDED.number,
                    height = EXCLUDED.height,
                    weight = EXCLUDED.weight,
                    age = EXCLUDED.age,
                    experience = EXCLUDED.experience,
                    college = EXCLUDED.college,
                    salary = EXCLUDED.salary,
                    draft_year = EXCLUDED.draft_year,
                    draft_pick = EXCLUDED.draft_pick,
                    team_id = EXCLUDED.team_id,
                    source = EXCLUDED.source
            ''', (player_id, name, position, number, height, weight, age, 
                  experience, college, salary, draft_year, draft_pick, team_id, source or 'UNKNOWN'))
            self.conn.commit()
            logger.info(f"成功插入球员: {name}")
            return True
        except Exception as e:
            logger.error(f"插入球员失败: {e}")
            return False
    
    def insert_game(self, game_id, home_team, away_team, home_score=None, 
                   away_score=None, status=None, time=None, date=None, source=None):
        if not self.conn:
            logger.error("数据库未连接")
            return False
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO games 
                (game_id, home_team, away_team, home_score, away_score, status, time, date, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (game_id) DO UPDATE SET
                    home_team = EXCLUDED.home_team,
                    away_team = EXCLUDED.away_team,
                    home_score = EXCLUDED.home_score,
                    away_score = EXCLUDED.away_score,
                    status = EXCLUDED.status,
                    time = EXCLUDED.time,
                    date = EXCLUDED.date,
                    source = EXCLUDED.source
            ''', (game_id, home_team, away_team, home_score, away_score, status, time, date, source or 'UNKNOWN'))
            self.conn.commit()
            logger.info(f"成功插入比赛: {home_team} vs {away_team}")
            return True
        except Exception as e:
            logger.error(f"插入比赛失败: {e}")
            return False
    
    def insert_teams_batch(self, teams_data):
        if not self.conn:
            logger.error("数据库未连接")
            return False
        
        try:
            cursor = self.conn.cursor()
            for team in teams_data:
                team_id = team.get('team_id')
                name = team.get('name') or team.get('team_name')
                abbreviation = team.get('abbreviation') or team.get('team_abbr')
                conference = team.get('conference')
                division = team.get('division')
                source = team.get('source') or 'UNKNOWN'
                
                cursor.execute('''
                    INSERT INTO teams (team_id, name, abbreviation, conference, division, source)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (team_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        abbreviation = EXCLUDED.abbreviation,
                        conference = EXCLUDED.conference,
                        division = EXCLUDED.division,
                        source = EXCLUDED.source
                ''', (team_id, name, abbreviation, conference, division, source))
            self.conn.commit()
            logger.info(f"成功批量插入 {len(teams_data)} 支球队")
            return True
        except Exception as e:
            logger.error(f"批量插入球队失败: {e}")
            return False
    
    def insert_players_batch(self, players_data):
        if not self.conn:
            logger.error("数据库未连接")
            return False
        
        try:
            cursor = self.conn.cursor()
            for player in players_data:
                cursor.execute('''
                    INSERT INTO players 
                    (player_id, name, position, number, height, weight, age, experience, 
                     college, salary, draft_year, draft_pick, team_id, source)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (player_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        position = EXCLUDED.position,
                        number = EXCLUDED.number,
                        height = EXCLUDED.height,
                        weight = EXCLUDED.weight,
                        age = EXCLUDED.age,
                        experience = EXCLUDED.experience,
                        college = EXCLUDED.college,
                        salary = EXCLUDED.salary,
                        draft_year = EXCLUDED.draft_year,
                        draft_pick = EXCLUDED.draft_pick,
                        team_id = EXCLUDED.team_id,
                        source = EXCLUDED.source
                ''', (player.get('player_id'), player.get('name'), player.get('position'),
                      player.get('number'), player.get('height'), player.get('weight'),
                      player.get('age'), player.get('experience'), player.get('college'),
                      player.get('salary'), player.get('draft_year'), player.get('draft_pick'),
                      player.get('team_id'), player.get('source') or 'UNKNOWN'))
            self.conn.commit()
            logger.info(f"成功批量插入 {len(players_data)} 名球员")
            return True
        except Exception as e:
            logger.error(f"批量插入球员失败: {e}")
            return False
    
    def insert_games_batch(self, games_data):
        if not self.conn:
            logger.error("数据库未连接")
            return False
        
        try:
            cursor = self.conn.cursor()
            for game in games_data:
                home_score_raw = game.get('home_score')
                away_score_raw = game.get('away_score')
                
                home_score = None
                if home_score_raw is not None:
                    if isinstance(home_score_raw, int):
                        home_score = home_score_raw
                    elif isinstance(home_score_raw, str) and home_score_raw.isdigit():
                        home_score = int(home_score_raw)
                
                away_score = None
                if away_score_raw is not None:
                    if isinstance(away_score_raw, int):
                        away_score = away_score_raw
                    elif isinstance(away_score_raw, str) and away_score_raw.isdigit():
                        away_score = int(away_score_raw)
                
                cursor.execute('''
                    INSERT INTO games 
                    (game_id, home_team, away_team, home_score, away_score, status, time, date, source)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (game_id) DO UPDATE SET
                        home_team = EXCLUDED.home_team,
                        away_team = EXCLUDED.away_team,
                        home_score = EXCLUDED.home_score,
                        away_score = EXCLUDED.away_score,
                        status = EXCLUDED.status,
                        time = EXCLUDED.time,
                        date = EXCLUDED.date,
                        source = EXCLUDED.source
                ''', (game.get('game_id'), game.get('home_team'), game.get('away_team'),
                      home_score, away_score, game.get('status'), game.get('time'), 
                      game.get('date'), game.get('source') or 'UNKNOWN'))
            self.conn.commit()
            logger.info(f"成功批量插入 {len(games_data)} 场比赛")
            return True
        except Exception as e:
            logger.error(f"批量插入比赛失败: {e}")
            return False
    
    def get_team_count(self):
        if not self.conn:
            logger.error("数据库未连接")
            return 0
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM teams')
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"获取球队数量失败: {e}")
            return 0
    
    def get_player_count(self):
        if not self.conn:
            logger.error("数据库未连接")
            return 0
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM players')
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"获取球员数量失败: {e}")
            return 0
    
    def get_game_count(self):
        if not self.conn:
            logger.error("数据库未连接")
            return 0
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM games')
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"获取比赛数量失败: {e}")
            return 0
    
    def get_todays_games(self, date):
        if not self.conn:
            logger.error("数据库未连接")
            return []
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM games WHERE date = %s', (date,))
            games = cursor.fetchall()
            return games
        except Exception as e:
            logger.error(f"获取比赛数据失败: {e}")
            return []
    
    def get_data_by_source(self, source):
        if not self.conn:
            logger.error("数据库未连接")
            return []
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM teams WHERE source = %s', (source,))
            teams = cursor.fetchall()
            
            cursor.execute('SELECT * FROM players WHERE source = %s', (source,))
            players = cursor.fetchall()
            
            cursor.execute('SELECT * FROM games WHERE source = %s', (source,))
            games = cursor.fetchall()
            
            return {'teams': teams, 'players': players, 'games': games}
        except Exception as e:
            logger.error(f"获取数据失败: {e}")
            return []