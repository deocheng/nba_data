#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Play-by-Play 数据即时保存和数据库导入系统
"""

import sys
import os
import json
import logging
import time
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_importer.database import DatabaseManager
from data_importer.config import DatabaseConfig

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class PBPDataStorage:
    """Play-by-Play 数据存储管理器 - 即时保存到文件和数据库"""
    
    def __init__(self, 
                 season_end: int = 2026,
                 data_dir: str = None,
                 db_config: DatabaseConfig = None):
        """
        初始化存储管理器
        
        :param season_end: 赛季结束年份
        :param data_dir: 数据存储目录
        :param db_config: 数据库配置
        """
        self.season_end = season_end
        
        # 目录设置
        self.base_dir = data_dir or os.path.join(os.path.dirname(__file__), '..', 'CSV')
        self.season_dir = os.path.join(self.base_dir, f'{season_end}_season')
        self.pbp_dir = os.path.join(self.season_dir, 'pbp')
        self.imported_dir = os.path.join(self.base_dir, '.imported')
        
        # 创建目录
        os.makedirs(self.pbp_dir, exist_ok=True)
        os.makedirs(self.imported_dir, exist_ok=True)
        
        # 进度文件
        self.progress_file = os.path.join(self.season_dir, 'full_progress.json')
        self.import_progress_file = os.path.join(self.imported_dir, 'import_status.json')
        
        # 数据库
        self.db_config = db_config or DatabaseConfig()
        self.db_manager = DatabaseManager(self.db_config)
        
        # 初始化数据库表
        self._init_database_tables()
        
        # 加载进度
        self.processed_games = self._load_progress(self.progress_file)
        self.imported_games = self._load_progress(self.import_progress_file)
        
        logger.info(f"PBP存储管理器初始化完成: 已处理 {len(self.processed_games)} 场, 已导入 {len(self.imported_games)} 场")
    
    def _init_database_tables(self):
        """初始化必要的数据库表"""
        
        # 1. Play-by-Play 主表
        pbp_table_columns = {
            'id': 'SERIAL PRIMARY KEY',
            'game_id': 'VARCHAR(50) NOT NULL',
            'season_end': 'INTEGER',
            'period': 'INTEGER',
            'game_clock': 'VARCHAR(20)',
            'visitor_action': 'TEXT',
            'home_action': 'TEXT',
            'visitor_score': 'INTEGER',
            'home_score': 'INTEGER',
            'score_change': 'INTEGER',
            'row_num': 'INTEGER',
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        }
        self.db_manager.create_table('play_by_play', pbp_table_columns, primary_key='id')
        
        # 2. 游戏元数据表
        game_table_columns = {
            'id': 'SERIAL PRIMARY KEY',
            'game_id': 'VARCHAR(50) UNIQUE NOT NULL',
            'season_end': 'INTEGER',
            'visitor_team': 'VARCHAR(50)',
            'home_team': 'VARCHAR(50)',
            'visitor_score': 'INTEGER',
            'home_score': 'INTEGER',
            'game_date': 'DATE',
            'boxscore_url': 'TEXT',
            'pbp_saved': 'BOOLEAN DEFAULT FALSE',
            'pbp_imported': 'BOOLEAN DEFAULT FALSE',
            'saved_at': 'TIMESTAMP',
            'imported_at': 'TIMESTAMP',
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        }
        self.db_manager.create_table('game_metadata', game_table_columns, primary_key='id')
        
        # 创建索引
        try:
            if not self._index_exists('idx_pbp_game_id'):
                self.db_manager.execute('CREATE INDEX idx_pbp_game_id ON play_by_play(game_id)')
                logger.info("创建索引 idx_pbp_game_id")
            
            if not self._index_exists('idx_game_metadata_game_id'):
                self.db_manager.execute('CREATE UNIQUE INDEX idx_game_metadata_game_id ON game_metadata(game_id)')
                logger.info("创建索引 idx_game_metadata_game_id")
        except Exception as e:
            logger.warning(f"创建索引时出错: {e}")
    
    def _index_exists(self, index_name: str) -> bool:
        """检查索引是否存在"""
        query = """
            SELECT EXISTS (
                SELECT FROM pg_indexes 
                WHERE indexname = %s
            )
        """
        result = self.db_manager.fetch_one(query, (index_name,))
        return result[0] if result else False
    
    def _load_progress(self, file_path: str) -> set:
        """加载进度文件"""
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return set(data)
                    elif isinstance(data, dict):
                        return set(data.get('games', []))
            except Exception as e:
                logger.warning(f"加载进度失败 {file_path}: {e}")
        return set()
    
    def _save_progress(self, file_path: str, game_set: set):
        """保存进度"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(sorted(list(game_set)), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存进度失败 {file_path}: {e}")
    
    def is_game_processed(self, game_id: str) -> bool:
        """检查游戏是否已处理"""
        return game_id in self.processed_games
    
    def is_game_imported(self, game_id: str) -> bool:
        """检查游戏是否已导入数据库"""
        return game_id in self.imported_games
    
    def save_game_metadata(self, game_info: Dict[str, Any]) -> bool:
        """
        保存游戏元数据
        
        :param game_info: 游戏信息字典
        :return: 是否成功
        """
        try:
            game_id = game_info.get('game_id')
            if not game_id:
                logger.warning("缺少 game_id，无法保存元数据")
                return False
            
            # 处理日期
            game_date = game_info.get('date')
            if pd.isna(game_date) or game_date == 'NaN':
                game_date = None
            
            metadata = {
                'game_id': game_id,
                'season_end': self.season_end,
                'visitor_team': str(game_info.get('visitor_team', '')),
                'home_team': str(game_info.get('home_team', '')),
                'visitor_score': int(game_info.get('visitor_score')) if game_info.get('visitor_score') is not None and not pd.isna(game_info.get('visitor_score')) else None,
                'home_score': int(game_info.get('home_score')) if game_info.get('home_score') is not None and not pd.isna(game_info.get('home_score')) else None,
                'game_date': game_date,
                'boxscore_url': str(game_info.get('boxscore_url', ''))
            }
            
            # 检查是否已存在
            existing = self.db_manager.fetch_one(
                "SELECT id FROM game_metadata WHERE game_id = %s",
                (game_id,)
            )
            
            if existing:
                # 更新
                update_query = """
                    UPDATE game_metadata 
                    SET visitor_team = %s, home_team = %s, 
                        visitor_score = %s, home_score = %s,
                        game_date = %s, boxscore_url = %s,
                        saved_at = CURRENT_TIMESTAMP
                    WHERE game_id = %s
                """
                self.db_manager.execute(update_query, (
                    metadata['visitor_team'], metadata['home_team'],
                    metadata['visitor_score'], metadata['home_score'],
                    metadata['game_date'], metadata['boxscore_url'],
                    game_id
                ))
            else:
                # 插入
                insert_query = """
                    INSERT INTO game_metadata 
                    (game_id, season_end, visitor_team, home_team, 
                     visitor_score, home_score, game_date, boxscore_url, saved_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """
                self.db_manager.execute(insert_query, (
                    game_id, metadata['season_end'],
                    metadata['visitor_team'], metadata['home_team'],
                    metadata['visitor_score'], metadata['home_score'],
                    metadata['game_date'], metadata['boxscore_url']
                ))
            
            logger.info(f"游戏元数据保存成功: {game_id}")
            return True
            
        except Exception as e:
            logger.error(f"保存游戏元数据失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_pbp_data(self, game_id: str, pbp_data: List[Dict]) -> str:
        """
        即时保存 Play-by-Play 数据到 JSON 文件
        
        :param game_id: 游戏 ID
        :param pbp_data: PBP 数据列表
        :return: 保存的文件路径
        """
        try:
            # 保存到 JSON
            json_file = os.path.join(self.pbp_dir, f"{game_id}_pbp.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(pbp_data, f, ensure_ascii=False, indent=2)
            
            # 更新进度
            self.processed_games.add(game_id)
            self._save_progress(self.progress_file, self.processed_games)
            
            # 更新数据库状态 - 先检查是否存在记录
            existing = self.db_manager.fetch_one(
                "SELECT id FROM game_metadata WHERE game_id = %s",
                (game_id,)
            )
            
            if existing:
                self.db_manager.execute(
                    "UPDATE game_metadata SET pbp_saved = TRUE, saved_at = CURRENT_TIMESTAMP WHERE game_id = %s",
                    (game_id,)
                )
            
            logger.info(f"PBP 数据保存成功: {game_id} ({len(pbp_data)} 条记录) -> {json_file}")
            return json_file
            
        except Exception as e:
            logger.error(f"保存 PBP 数据失败 {game_id}: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def import_pbp_to_database(self, game_id: str, pbp_data: List[Dict]) -> int:
        """
        即时导入 Play-by-Play 数据到数据库
        
        :param game_id: 游戏 ID
        :param pbp_data: PBP 数据列表
        :return: 导入的记录数
        """
        try:
            if not pbp_data:
                logger.warning(f"没有 PBP 数据可导入: {game_id}")
                return 0
            
            # 转换数据
            records = []
            for idx, row_data in enumerate(pbp_data):
                # 从 cells 中解析数据
                cells = row_data.get('cells', []) if isinstance(row_data, dict) else row_data
                
                if len(cells) >= 6:
                    period_str = cells[0] if idx > 0 else ''
                    visitor_action = cells[1] if len(cells) > 1 else ''
                    score_str = cells[3] if len(cells) > 3 else ''
                    home_action = cells[5] if len(cells) > 5 else ''
                    
                    # 解析比分
                    visitor_score = None
                    home_score = None
                    if '-' in str(score_str):
                        parts = str(score_str).split('-')
                        if len(parts) == 2:
                            try:
                                visitor_score = int(parts[0].strip())
                                home_score = int(parts[1].strip())
                            except:
                                pass
                    
                    records.append({
                        'game_id': game_id,
                        'season_end': self.season_end,
                        'period': self._parse_period(period_str),
                        'game_clock': cells[0] if len(cells) > 0 and idx > 0 else '',
                        'visitor_action': visitor_action,
                        'home_action': home_action,
                        'visitor_score': visitor_score,
                        'home_score': home_score,
                        'score_change': None,
                        'row_num': row_data.get('row', idx) if isinstance(row_data, dict) else idx
                    })
            
            if not records:
                logger.warning(f"没有有效的 PBP 记录可导入: {game_id}")
                return 0
            
            # 删除已存在的记录（避免重复）
            self.db_manager.execute(
                "DELETE FROM play_by_play WHERE game_id = %s",
                (game_id,)
            )
            
            # 插入新记录
            inserted = self.db_manager.insert_data('play_by_play', records, batch_size=100)
            
            # 更新导入进度
            self.imported_games.add(game_id)
            self._save_progress(self.import_progress_file, self.imported_games)
            
            # 更新数据库状态
            existing = self.db_manager.fetch_one(
                "SELECT id FROM game_metadata WHERE game_id = %s",
                (game_id,)
            )
            if existing:
                self.db_manager.execute(
                    "UPDATE game_metadata SET pbp_imported = TRUE, imported_at = CURRENT_TIMESTAMP WHERE game_id = %s",
                    (game_id,)
                )
            
            logger.info(f"PBP 数据导入数据库成功: {game_id} ({inserted} 条记录)")
            return inserted
            
        except Exception as e:
            logger.error(f"导入 PBP 数据到数据库失败 {game_id}: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def _parse_period(self, period_str: str) -> Optional[int]:
        """解析节次"""
        if not period_str:
            return None
        
        period_str = str(period_str).strip()
        
        period_map = {
            '1': 1, '2': 2, '3': 3, '4': 4,
            'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4,
            'OT1': 5, 'OT2': 6, 'OT3': 7, 'OT4': 8,
            'OT': 5
        }
        
        if period_str in period_map:
            return period_map[period_str]
        
        # 尝试提取数字
        import re
        match = re.search(r'\d+', period_str)
        if match:
            num = int(match.group())
            if 1 <= num <= 4:
                return num
            elif num > 0:
                return 4 + num
        
        return None
    
    def process_single_game(self, game_info: Dict[str, Any], pbp_data: List[Dict]) -> Dict[str, Any]:
        """
        完整处理单个游戏：保存文件 + 导入数据库
        
        :param game_info: 游戏信息
        :param pbp_data: PBP 数据
        :return: 处理结果
        """
        game_id = game_info.get('game_id')
        if not game_id:
            game_id = game_info.get('boxscore_url', '').split('/')[-1].replace('.html', '')
        
        if not game_id:
            return {'success': False, 'error': '缺少 game_id'}
        
        result = {
            'game_id': game_id,
            'success': False,
            'metadata_saved': False,
            'file_saved': False,
            'db_imported': False,
            'errors': [],
            'records_saved': 0,
            'records_imported': 0
        }
        
        # 1. 保存元数据
        try:
            game_info['game_id'] = game_id
            result['metadata_saved'] = self.save_game_metadata(game_info)
        except Exception as e:
            result['errors'].append(f"元数据保存失败: {e}")
        
        # 2. 保存到文件
        try:
            saved_file = self.save_pbp_data(game_id, pbp_data)
            result['file_saved'] = bool(saved_file)
            result['records_saved'] = len(pbp_data) if saved_file else 0
        except Exception as e:
            result['errors'].append(f"文件保存失败: {e}")
        
        # 3. 导入到数据库
        try:
            imported_count = self.import_pbp_to_database(game_id, pbp_data)
            result['db_imported'] = imported_count > 0
            result['records_imported'] = imported_count
        except Exception as e:
            result['errors'].append(f"数据库导入失败: {e}")
        
        result['success'] = result['file_saved'] or result['db_imported']
        
        return result
    
    def get_import_summary(self) -> Dict[str, Any]:
        """获取导入摘要"""
        try:
            total_games_result = self.db_manager.fetch_one(
                "SELECT COUNT(*) FROM game_metadata"
            )
            total_games = total_games_result[0] if total_games_result else 0
            
            pbp_saved_result = self.db_manager.fetch_one(
                "SELECT COUNT(*) FROM game_metadata WHERE pbp_saved = TRUE"
            )
            pbp_saved = pbp_saved_result[0] if pbp_saved_result else 0
            
            pbp_imported_result = self.db_manager.fetch_one(
                "SELECT COUNT(*) FROM game_metadata WHERE pbp_imported = TRUE"
            )
            pbp_imported = pbp_imported_result[0] if pbp_imported_result else 0
            
            pbp_records_result = self.db_manager.fetch_one(
                "SELECT COUNT(*) FROM play_by_play"
            )
            pbp_records = pbp_records_result[0] if pbp_records_result else 0
            
            return {
                'total_games': total_games,
                'pbp_saved': pbp_saved,
                'pbp_imported': pbp_imported,
                'pbp_records': pbp_records
            }
        except Exception as e:
            logger.error(f"获取导入摘要失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                'total_games': 0,
                'pbp_saved': 0,
                'pbp_imported': 0,
                'pbp_records': 0
            }
    
    def close(self):
        """关闭资源"""
        self.db_manager.close()


# 全局实例
_pbp_storage = None

def get_pbp_storage(season_end: int = 2026, **kwargs) -> PBPDataStorage:
    """获取 PBP 存储管理器单例"""
    global _pbp_storage
    if _pbp_storage is None:
        _pbp_storage = PBPDataStorage(season_end=season_end, **kwargs)
    return _pbp_storage


if __name__ == "__main__":
    # 测试
    storage = PBPDataStorage()
    summary = storage.get_import_summary()
    print("导入摘要:", summary)
    storage.close()
