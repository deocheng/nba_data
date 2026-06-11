import pandas as pd
import numpy as np
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NBAProcessor:
    def __init__(self):
        """
        初始化 NBA 数据处理器
        """
        pass
    
    def process_player_career_stats(self, stats_data):
        """
        处理球员职业生涯统计数据
        :param stats_data: 球员职业生涯统计数据
        :return: 处理后的数据
        """
        logger.info("处理球员职业生涯统计数据")
        try:
            if not stats_data:
                return {}
            
            # 转换为 DataFrame
            df = pd.DataFrame(stats_data)
            
            # 计算职业生涯总数据
            career_totals = {
                'games_played': df['GP'].sum(),
                'minutes_played': df['MIN'].sum(),
                'points': df['PTS'].sum(),
                'rebounds': df['REB'].sum(),
                'assists': df['AST'].sum(),
                'steals': df['STL'].sum(),
                'blocks': df['BLK'].sum(),
                'turnovers': df['TOV'].sum(),
                'field_goals_made': df['FGM'].sum(),
                'field_goals_attempted': df['FGA'].sum(),
                'three_pointers_made': df['FG3M'].sum(),
                'three_pointers_attempted': df['FG3A'].sum(),
                'free_throws_made': df['FTM'].sum(),
                'free_throws_attempted': df['FTA'].sum()
            }
            
            # 计算职业生涯平均数据
            career_totals['points_per_game'] = career_totals['points'] / career_totals['games_played'] if career_totals['games_played'] > 0 else 0
            career_totals['rebounds_per_game'] = career_totals['rebounds'] / career_totals['games_played'] if career_totals['games_played'] > 0 else 0
            career_totals['assists_per_game'] = career_totals['assists'] / career_totals['games_played'] if career_totals['games_played'] > 0 else 0
            career_totals['steals_per_game'] = career_totals['steals'] / career_totals['games_played'] if career_totals['games_played'] > 0 else 0
            career_totals['blocks_per_game'] = career_totals['blocks'] / career_totals['games_played'] if career_totals['games_played'] > 0 else 0
            
            # 计算命中率
            career_totals['field_goal_percentage'] = (career_totals['field_goals_made'] / career_totals['field_goals_attempted'] * 100) if career_totals['field_goals_attempted'] > 0 else 0
            career_totals['three_point_percentage'] = (career_totals['three_pointers_made'] / career_totals['three_pointers_attempted'] * 100) if career_totals['three_pointers_attempted'] > 0 else 0
            career_totals['free_throw_percentage'] = (career_totals['free_throws_made'] / career_totals['free_throws_attempted'] * 100) if career_totals['free_throws_attempted'] > 0 else 0
            
            # 按赛季分组数据
            season_stats = df.groupby('SEASON_ID').agg({
                'GP': 'sum',
                'MIN': 'sum',
                'PTS': 'sum',
                'REB': 'sum',
                'AST': 'sum',
                'STL': 'sum',
                'BLK': 'sum',
                'TOV': 'sum',
                'FGM': 'sum',
                'FGA': 'sum',
                'FG3M': 'sum',
                'FG3A': 'sum',
                'FTM': 'sum',
                'FTA': 'sum'
            }).reset_index()
            
            # 计算每个赛季的平均数据
            season_stats['PTS_PER_GAME'] = season_stats['PTS'] / season_stats['GP']
            season_stats['REB_PER_GAME'] = season_stats['REB'] / season_stats['GP']
            season_stats['AST_PER_GAME'] = season_stats['AST'] / season_stats['GP']
            
            # 转换为字典
            season_stats_dict = season_stats.to_dict('records')
            
            return {
                'career_totals': career_totals,
                'season_stats': season_stats_dict
            }
        except Exception as e:
            logger.error(f"处理球员职业生涯统计数据失败: {e}")
            return {}
    
    def process_games_data(self, games_data):
        """
        处理比赛数据
        :param games_data: 比赛数据
        :return: 处理后的数据
        """
        logger.info("处理比赛数据")
        try:
            if not games_data:
                return {}
            
            # 转换为 DataFrame
            df = pd.DataFrame(games_data)
            
            # 计算球队战绩
            df['WINS'] = df.apply(lambda row: 1 if row['WL'] == 'W' else 0, axis=1)
            df['LOSSES'] = df.apply(lambda row: 1 if row['WL'] == 'L' else 0, axis=1)
            
            # 按球队分组计算战绩
            team_record = df.groupby('TEAM_ID').agg({
                'WINS': 'sum',
                'LOSSES': 'sum'
            }).reset_index()
            team_record['WIN_PERCENTAGE'] = team_record['WINS'] / (team_record['WINS'] + team_record['LOSSES']) * 100
            
            # 计算球队平均得分和失分
            team_stats = df.groupby('TEAM_ID').agg({
                'PTS': 'mean',
                'PTS_AST': 'mean'
            }).reset_index()
            team_stats.columns = ['TEAM_ID', 'AVG_PTS', 'AVG_PTS_ALLOWED']
            
            # 合并战绩和统计数据
            team_performance = pd.merge(team_record, team_stats, on='TEAM_ID')
            
            # 转换为字典
            team_performance_dict = team_performance.to_dict('records')
            
            return {
                'team_performance': team_performance_dict,
                'total_games': len(df)
            }
        except Exception as e:
            logger.error(f"处理比赛数据失败: {e}")
            return {}
    
    def process_player_info(self, player_info):
        """
        处理球员信息
        :param player_info: 球员信息
        :return: 处理后的数据
        """
        logger.info("处理球员信息")
        try:
            if not player_info:
                return {}
            
            # 提取关键信息
            processed_info = {
                'id': player_info.get('id'),
                'full_name': player_info.get('full_name'),
                'first_name': player_info.get('first_name'),
                'last_name': player_info.get('last_name'),
                'is_active': player_info.get('is_active'),
                'team_id': player_info.get('team_id')
            }
            
            return processed_info
        except Exception as e:
            logger.error(f"处理球员信息失败: {e}")
            return {}
    
    def process_team_info(self, team_info):
        """
        处理球队信息
        :param team_info: 球队信息
        :return: 处理后的数据
        """
        logger.info("处理球队信息")
        try:
            if not team_info:
                return {}
            
            # 提取关键信息
            processed_info = {
                'id': team_info.get('id'),
                'full_name': team_info.get('full_name'),
                'abbreviation': team_info.get('abbreviation'),
                'nickname': team_info.get('nickname'),
                'city': team_info.get('city'),
                'state': team_info.get('state'),
                'year_founded': team_info.get('year_founded')
            }
            
            return processed_info
        except Exception as e:
            logger.error(f"处理球队信息失败: {e}")
            return {}
    
    def process_multiple_players(self, players_info):
        """
        处理多个球员的信息
        :param players_info: 球员信息列表
        :return: 处理后的数据
        """
        logger.info("处理多个球员的信息")
        try:
            if not players_info:
                return []
            
            processed_players = []
            for player_info in players_info:
                processed_player = self.process_player_info(player_info)
                if processed_player:
                    processed_players.append(processed_player)
            
            return processed_players
        except Exception as e:
            logger.error(f"处理多个球员的信息失败: {e}")
            return []
    
    def process_multiple_teams(self, teams_info):
        """
        处理多个球队的信息
        :param teams_info: 球队信息列表
        :return: 处理后的数据
        """
        logger.info("处理多个球队的信息")
        try:
            if not teams_info:
                return []
            
            processed_teams = []
            for team_info in teams_info:
                processed_team = self.process_team_info(team_info)
                if processed_team:
                    processed_teams.append(processed_team)
            
            return processed_teams
        except Exception as e:
            logger.error(f"处理多个球队的信息失败: {e}")
            return []
