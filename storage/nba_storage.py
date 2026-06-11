import os
import json
import pandas as pd
import logging
from config.config import Config

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NBAStorage:
    def __init__(self, data_dir=None):
        """
        初始化 NBA 数据存储
        :param data_dir: 数据存储目录
        """
        # 获取配置
        nba_config = Config.get_nba_config()
        
        self.data_dir = data_dir or nba_config['data_dir']
        
        # 确保数据目录存在
        os.makedirs(self.data_dir, exist_ok=True)
    
    def save_json(self, data, filename):
        """
        保存数据为 JSON 文件
        :param data: 数据
        :param filename: 文件名
        """
        file_path = os.path.join(self.data_dir, filename)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"成功保存数据到 {file_path}")
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
    
    def save_csv(self, data, filename):
        """
        保存数据为 CSV 文件
        :param data: 数据
        :param filename: 文件名
        """
        file_path = os.path.join(self.data_dir, filename)
        try:
            if isinstance(data, pd.DataFrame):
                df = data
            else:
                df = pd.DataFrame(data)
            df.to_csv(file_path, index=False, encoding='utf-8')
            logger.info(f"成功保存数据到 {file_path}")
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
    
    def load_json(self, filename):
        """
        加载 JSON 文件
        :param filename: 文件名
        :return: 数据
        """
        file_path = os.path.join(self.data_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"成功加载数据从 {file_path}")
            return data
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            return {}
    
    def load_csv(self, filename):
        """
        加载 CSV 文件
        :param filename: 文件名
        :return: 数据
        """
        file_path = os.path.join(self.data_dir, filename)
        try:
            df = pd.read_csv(file_path)
            logger.info(f"成功加载数据从 {file_path}")
            return df
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            return pd.DataFrame()
    
    def save_player_stats(self, player_id, stats_data):
        """
        保存球员统计数据
        :param player_id: 球员ID
        :param stats_data: 统计数据
        """
        filename = f"player_{player_id}_stats.json"
        self.save_json(stats_data, filename)
    
    def save_team_info(self, team_id, team_info):
        """
        保存球队信息
        :param team_id: 球队ID
        :param team_info: 球队信息
        """
        filename = f"team_{team_id}_info.json"
        self.save_json(team_info, filename)
    
    def save_games_data(self, team_id, season, games_data):
        """
        保存球队赛季比赛数据
        :param team_id: 球队ID
        :param season: 赛季
        :param games_data: 比赛数据
        """
        filename = f"team_{team_id}_games_{season}.json"
        self.save_json(games_data, filename)
    
    def save_all_players(self, players_data):
        """
        保存所有球员信息
        :param players_data: 球员信息列表
        """
        filename = "players_all.json"
        self.save_json(players_data, filename)
    
    def save_all_teams(self, teams_data):
        """
        保存所有球队信息
        :param teams_data: 球队信息列表
        """
        filename = "teams.json"
        self.save_json(teams_data, filename)
    
    def load_player_stats(self, player_id):
        """
        加载球员统计数据
        :param player_id: 球员ID
        :return: 统计数据
        """
        filename = f"player_{player_id}_stats.json"
        return self.load_json(filename)
    
    def load_team_info(self, team_id):
        """
        加载球队信息
        :param team_id: 球队ID
        :return: 球队信息
        """
        filename = f"team_{team_id}_info.json"
        return self.load_json(filename)
    
    def load_games_data(self, team_id, season):
        """
        加载球队赛季比赛数据
        :param team_id: 球队ID
        :param season: 赛季
        :return: 比赛数据
        """
        filename = f"team_{team_id}_games_{season}.json"
        return self.load_json(filename)
    
    def load_all_players(self):
        """
        加载所有球员信息
        :return: 球员信息列表
        """
        filename = "players_all.json"
        return self.load_json(filename)
    
    def load_all_teams(self):
        """
        加载所有球队信息
        :return: 球队信息列表
        """
        filename = "teams.json"
        return self.load_json(filename)
    
    def save_stats_summary(self, summary_data):
        """
        保存统计摘要数据
        :param summary_data: 摘要数据
        """
        filename = "stats_summary.json"
        self.save_json(summary_data, filename)
    
    def load_stats_summary(self):
        """
        加载统计摘要数据
        :return: 摘要数据
        """
        filename = "stats_summary.json"
        return self.load_json(filename)
