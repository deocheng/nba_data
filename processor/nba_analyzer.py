import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NBAAnalyzer:
    def __init__(self):
        """
        初始化 NBA 数据分析器
        """
        pass
    
    def analyze_player_career(self, career_stats):
        """
        分析球员职业生涯
        :param career_stats: 球员职业生涯统计数据
        :return: 分析结果
        """
        logger.info("分析球员职业生涯")
        try:
            if not career_stats:
                return {}
            
            # 提取赛季统计数据
            season_stats = career_stats.get('season_stats', [])
            if not season_stats:
                return {}
            
            # 转换为 DataFrame
            df = pd.DataFrame(season_stats)
            
            # 分析得分趋势
            scoring_trend = df[['SEASON_ID', 'PTS_PER_GAME']].sort_values('SEASON_ID')
            
            # 分析篮板趋势
            rebounding_trend = df[['SEASON_ID', 'REB_PER_GAME']].sort_values('SEASON_ID')
            
            # 分析助攻趋势
            assist_trend = df[['SEASON_ID', 'AST_PER_GAME']].sort_values('SEASON_ID')
            
            # 分析最佳赛季
            best_season = df.loc[df['PTS'].idxmax()]
            
            # 分析职业生涯高峰期
            peak_years = df[(df['PTS_PER_GAME'] > df['PTS_PER_GAME'].mean())]['SEASON_ID'].tolist()
            
            return {
                'scoring_trend': scoring_trend.to_dict('records'),
                'rebounding_trend': rebounding_trend.to_dict('records'),
                'assist_trend': assist_trend.to_dict('records'),
                'best_season': best_season.to_dict(),
                'peak_years': peak_years,
                'career_totals': career_stats.get('career_totals', {})
            }
        except Exception as e:
            logger.error(f"分析球员职业生涯失败: {e}")
            return {}
    
    def analyze_team_performance(self, team_performance):
        """
        分析球队表现
        :param team_performance: 球队表现数据
        :return: 分析结果
        """
        logger.info("分析球队表现")
        try:
            if not team_performance:
                return {}
            
            # 转换为 DataFrame
            df = pd.DataFrame(team_performance.get('team_performance', []))
            
            # 分析胜率最高的球队
            best_team = df.loc[df['WIN_PERCENTAGE'].idxmax()]
            
            # 分析得分最高的球队
            highest_scoring_team = df.loc[df['AVG_PTS'].idxmax()]
            
            # 分析失分最少的球队
            best_defense_team = df.loc[df['AVG_PTS_ALLOWED'].idxmin()]
            
            # 分析整体表现
            overall_stats = {
                'average_win_percentage': df['WIN_PERCENTAGE'].mean(),
                'average_points': df['AVG_PTS'].mean(),
                'average_points_allowed': df['AVG_PTS_ALLOWED'].mean(),
                'total_teams': len(df)
            }
            
            return {
                'best_team': best_team.to_dict(),
                'highest_scoring_team': highest_scoring_team.to_dict(),
                'best_defense_team': best_defense_team.to_dict(),
                'overall_stats': overall_stats,
                'total_games': team_performance.get('total_games', 0)
            }
        except Exception as e:
            logger.error(f"分析球队表现失败: {e}")
            return {}
    
    def analyze_player_comparison(self, players_stats):
        """
        分析球员对比
        :param players_stats: 球员统计数据列表
        :return: 分析结果
        """
        logger.info("分析球员对比")
        try:
            if not players_stats:
                return {}
            
            # 提取关键统计数据
            players_data = []
            for player_stats in players_stats:
                career_totals = player_stats.get('career_totals', {})
                players_data.append({
                    'player_id': player_stats.get('player_id', ''),
                    'player_name': player_stats.get('player_name', ''),
                    'points': career_totals.get('points', 0),
                    'rebounds': career_totals.get('rebounds', 0),
                    'assists': career_totals.get('assists', 0),
                    'points_per_game': career_totals.get('points_per_game', 0),
                    'rebounds_per_game': career_totals.get('rebounds_per_game', 0),
                    'assists_per_game': career_totals.get('assists_per_game', 0),
                    'field_goal_percentage': career_totals.get('field_goal_percentage', 0)
                })
            
            # 转换为 DataFrame
            df = pd.DataFrame(players_data)
            
            # 分析得分最高的球员
            highest_scorer = df.loc[df['points'].idxmax()]
            
            # 分析篮板最多的球员
            best_rebounder = df.loc[df['rebounds'].idxmax()]
            
            # 分析助攻最多的球员
            best_assister = df.loc[df['assists'].idxmax()]
            
            # 分析场均得分最高的球员
            highest_ppg = df.loc[df['points_per_game'].idxmax()]
            
            return {
                'highest_scorer': highest_scorer.to_dict(),
                'best_rebounder': best_rebounder.to_dict(),
                'best_assister': best_assister.to_dict(),
                'highest_ppg': highest_ppg.to_dict(),
                'comparison_data': players_data
            }
        except Exception as e:
            logger.error(f"分析球员对比失败: {e}")
            return {}
    
    def generate_statistics_summary(self, all_players, all_teams):
        """
        生成统计摘要
        :param all_players: 所有球员信息
        :param all_teams: 所有球队信息
        :return: 统计摘要
        """
        logger.info("生成统计摘要")
        try:
            summary = {
                'total_players': len(all_players),
                'total_teams': len(all_teams),
                'active_players': len([p for p in all_players if p.get('is_active', False)]),
                'inactive_players': len([p for p in all_players if not p.get('is_active', False)]),
                'teams': [t.get('full_name') for t in all_teams]
            }
            
            return summary
        except Exception as e:
            logger.error(f"生成统计摘要失败: {e}")
            return {}
