"""
配置管理模块
管理数据库连接和导入配置
"""

import os
from typing import Dict, Optional

class DatabaseConfig:
    """数据库配置"""
    
    def __init__(self, dbname: str = None, user: str = None, password: str = None, 
                 host: str = None, port: int = None, skip_errors: bool = True):
        self.dbname = dbname or os.getenv('POSTGRES_DB', 'nba')
        self.user = user or os.getenv('POSTGRES_USER', 'postgres')
        self.password = password or os.getenv('POSTGRES_PASSWORD', 'postgres')
        self.host = host or os.getenv('POSTGRES_HOST', 'localhost')
        self.port = port or int(os.getenv('POSTGRES_PORT', '5433'))
        self.skip_errors = skip_errors
    
    def to_dict(self) -> Dict:
        return {
            'dbname': self.dbname,
            'user': self.user,
            'password': self.password,
            'host': self.host,
            'port': self.port
        }

class ImportConfig:
    """导入配置"""
    
    def __init__(self, 
                 input_dir: str = 'CSV',
                 output_dir: str = 'CSV_Clean',
                 backup_dir: str = 'backups',
                 create_backup: bool = True,
                 overwrite_existing: bool = True,
                 skip_errors: bool = True,
                 verbose: bool = True,
                 dry_run: bool = False):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.backup_dir = backup_dir
        self.create_backup = create_backup
        self.overwrite_existing = overwrite_existing
        self.skip_errors = skip_errors
        self.verbose = verbose
        self.dry_run = dry_run

class TeamConfig:
    """球队配置"""
    
    TEAM_ABBR_MAP = {
        'SAS': 'San Antonio Spurs',
        'OKC': 'Oklahoma City Thunder',
        'LAL': 'Los Angeles Lakers',
        'HOU': 'Houston Rockets',
        'DAL': 'Dallas Mavericks',
        'NOP': 'New Orleans Pelicans',
        'GSW': 'Golden State Warriors',
        'PHX': 'Phoenix Suns',
        'DEN': 'Denver Nuggets',
        'MIN': 'Minnesota Timberwolves',
        'POR': 'Portland Trail Blazers',
        'UTA': 'Utah Jazz',
        'LAC': 'Los Angeles Clippers',
        'SAC': 'Sacramento Kings',
        'MEM': 'Memphis Grizzlies',
        'BOS': 'Boston Celtics',
        'MIA': 'Miami Heat',
        'MIL': 'Milwaukee Bucks',
        'PHI': 'Philadelphia 76ers',
        'TOR': 'Toronto Raptors',
        'BKN': 'Brooklyn Nets',
        'NYK': 'New York Knicks',
        'CHI': 'Chicago Bulls',
        'CLE': 'Cleveland Cavaliers',
        'IND': 'Indiana Pacers',
        'DET': 'Detroit Pistons',
        'ATL': 'Atlanta Hawks',
        'CHA': 'Charlotte Hornets',
        'ORL': 'Orlando Magic',
        'WAS': 'Washington Wizards'
    }
    
    @classmethod
    def get_team_name(cls, abbr: str) -> str:
        return cls.TEAM_ABBR_MAP.get(abbr, abbr)
    
    @classmethod
    def get_team_abbr(cls, name: str) -> Optional[str]:
        for abbr, team_name in cls.TEAM_ABBR_MAP.items():
            if team_name.lower() == name.lower() or abbr.lower() == name.lower():
                return abbr
        return None

# 默认配置
DEFAULT_DB_CONFIG = DatabaseConfig()
DEFAULT_IMPORT_CONFIG = ImportConfig()
