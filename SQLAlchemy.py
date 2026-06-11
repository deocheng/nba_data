import time
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session, declarative_base, relationship
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, Text, JSON
from basketball_reference_scraper.seasons import get_schedule
from basketball_reference_scraper.box_scores import get_box_scores

# ==================== 配置 ====================
DATABASE_URL = "postgresql+psycopg2://your_user:your_password@localhost:5432/basketball_timeline"

Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False)   # echo=True 可用于调试

# ==================== ORM 模型 ====================
class Team(Base):
    __tablename__ = 'teams'
    team_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    abbreviation = Column(String(3), unique=True)

class Player(Base):
    __tablename__ = 'players'
    player_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    # 其他字段...

class Game(Base):
    __tablename__ = 'games'
    game_id = Column(Integer, primary_key=True)
    game_date = Column(Date, nullable=False)
    season = Column(String(20), nullable=False)
    home_team_id = Column(Integer, ForeignKey('teams.team_id'))
    away_team_id = Column(Integer, ForeignKey('teams.team_id'))
    home_score = Column(Integer)
    away_score = Column(Integer)
    winner_team_id = Column(Integer)

class PlayerGameStat(Base):
    __tablename__ = 'player_game_stats'
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.game_id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.player_id'))
    team_id = Column(Integer, ForeignKey('teams.team_id'), nullable=False)
    
    is_home = Column(Boolean, nullable=False)
    minutes_played = Column(Float)
    started = Column(Boolean, default=False)
    
    points = Column(Integer, default=0)
    rebounds = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    steals = Column(Integer, default=0)
    blocks = Column(Integer, default=0)
    turnovers = Column(Integer, default=0)
    fouls = Column(Integer, default=0)
    
    fgm = Column(Integer)
    fga = Column(Integer)
    three_made = Column(Integer)
    three_attempted = Column(Integer)
    ftm = Column(Integer)
    fta = Column(Integer)
    
    plus_minus = Column(Integer)
    advanced_stats = Column(JSON)
    notes = Column(Text)

# ==================== 主导入函数 ====================
def import_season(season: int):
    print(f"开始导入 {season-1}-{season} 赛季...")
    
    schedule = get_schedule(season, playoffs=False)
    print(f"共找到 {len(schedule)} 场比赛")
    
    with Session(engine) as session:
        for idx, row in schedule.iterrows():
            game_date = row['DATE'].date()
            visitor_abbr = row['VISITOR']
            home_abbr = row['HOME']
            visitor_pts = int(row.get('VISITOR_PTS') or 0)
            home_pts = int(row.get('HOME_PTS') or 0)
            
            # 1. 插入或获取 Game
            game = session.query(Game).filter(
                Game.game_date == game_date,
                Game.home_team_id == session.query(Team.team_id).filter(Team.abbreviation == home_abbr).scalar(),
                Game.away_team_id == session.query(Team.team_id).filter(Team.abbreviation == visitor_abbr).scalar()
            ).first()
            
            if game:
                print(f"跳过已存在: {game_date} {visitor_abbr} @ {home_abbr}")
                continue
                
            game = Game(
                game_date=game_date,
                season=f"{season-1}-{season}",
                home_team_id=session.query(Team.team_id).filter(Team.abbreviation == home_abbr).scalar(),
                away_team_id=session.query(Team.team_id).filter(Team.abbreviation == visitor_abbr).scalar(),
                home_score=home_pts,
                away_score=visitor_pts,
                winner_team_id= home_abbr if home_pts > visitor_pts else visitor_abbr if visitor_pts > home_pts else None
            )
            session.add(game)
            session.flush()   # 获取 game_id
            
            # 2. 获取 Box Score
            try:
                box = get_box_scores(game_date.strftime('%Y-%m-%d'), home_abbr, visitor_abbr)
                
                for team_abbr, df in box.items():
                    if df is None or df.empty:
                        continue
                        
                    team_id = session.query(Team.team_id).filter(Team.abbreviation == team_abbr).scalar()
                    is_home = (team_abbr == home_abbr)
                    
                    for _, p in df.iterrows():
                        # 这里需要处理 player_id 映射（后续可优化）
                        player_name = p['PLAYER']
                        player = session.query(Player).filter(Player.name == player_name).first()
                        
                        if not player:
                            # 可在此自动创建新球员（推荐）
                            player = Player(name=player_name)
                            session.add(player)
                            session.flush()
                        
                        stat = PlayerGameStat(
                            game_id=game.game_id,
                            player_id=player.player_id,
                            team_id=team_id,
                            is_home=is_home,
                            minutes_played=p.get('MP'),
                            started=p.get('GS', False),
                            points=int(p.get('PTS') or 0),
                            rebounds=int(p.get('TRB') or 0),
                            assists=int(p.get('AST') or 0),
                            # ... 其他字段类似映射
                            plus_minus=int(p.get('+/-') or 0)
                        )
                        session.add(stat)
                
                session.commit()
                print(f"✓ {game_date} {visitor_abbr} @ {home_abbr} 导入成功")
                
            except Exception as e:
                session.rollback()
                print(f"✗ {game_date} 失败: {e}")
            
            time.sleep(25)   # 防限流

# ==================== 执行 ====================
if __name__ == "__main__":
    import_season(2025)   # 示例：导入 2024-25 赛季