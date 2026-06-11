"""
数据导入模块
提供通用的数据导入功能
"""

import os
import logging
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from .config import ImportConfig, TeamConfig
from .database import DatabaseManager
from .parsers import ParserFactory
from .validators import DataValidator, NBADataValidator

logger = logging.getLogger(__name__)

class DataImporter:
    """通用数据导入器"""
    
    def __init__(self, config: ImportConfig = None):
        self.config = config or ImportConfig()
        self.db_manager = DatabaseManager()
        self.validator = DataValidator()
        self.stats = {
            'files_processed': 0,
            'records_parsed': 0,
            'records_validated': 0,
            'records_inserted': 0,
            'errors': 0,
            'warnings': 0
        }
    
    def import_file(self, file_path: str, table_name: str = None, 
                    validator: DataValidator = None) -> Tuple[int, int, List[str]]:
        """
        导入单个文件
        :param file_path: 文件路径
        :param table_name: 目标表名，默认为文件名
        :param validator: 自定义验证器
        :return: (插入记录数, 错误数, 错误列表)
        """
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return 0, 1, [f"文件不存在: {file_path}"]
        
        # 生成表名
        if table_name is None:
            table_name = os.path.splitext(os.path.basename(file_path))[0].lower()
            table_name = table_name.replace(' ', '_').replace('-', '_')
        
        # 备份现有数据
        if self.config.create_backup and self.db_manager.table_exists(table_name):
            self.db_manager.backup_table(table_name, self.config.backup_dir)
        
        # 解析文件
        parser = ParserFactory.get_parser(file_path)
        data = parser.parse(file_path)
        
        if not data:
            logger.warning(f"文件 {file_path} 没有数据")
            return 0, 0, []
        
        self.stats['files_processed'] += 1
        self.stats['records_parsed'] += len(data)
        
        # 验证数据
        data_validator = validator or self.validator
        valid_data, errors = data_validator.validate_data(data)
        
        self.stats['records_validated'] += len(valid_data)
        self.stats['errors'] += len(errors)
        
        if errors:
            logger.warning(f"验证失败 {len(errors)} 条记录")
            for error in errors[:5]:
                logger.warning(f"  - {error}")
        
        if not valid_data:
            logger.warning("没有通过验证的数据")
            return 0, len(errors), errors
        
        # 创建表（如果不存在）
        columns = self._infer_columns(valid_data[0])
        self.db_manager.create_table(table_name, columns)
        
        # 清空现有数据（如果需要）
        if self.config.overwrite_existing:
            self.db_manager.truncate_table(table_name)
        
        # 插入数据
        inserted = self.db_manager.insert_data(table_name, valid_data)
        self.stats['records_inserted'] += inserted
        
        logger.info(f"成功导入 {inserted} 条记录到表 {table_name}")
        return inserted, len(errors), errors
    
    def import_directory(self, directory: str = None, 
                         validator: DataValidator = None) -> Dict[str, Tuple[int, int, List[str]]]:
        """
        导入目录中的所有文件
        :param directory: 目录路径，默认为配置中的输入目录
        :param validator: 自定义验证器
        :return: {文件名: (插入数, 错误数, 错误列表)}
        """
        directory = directory or self.config.input_dir
        
        if not os.path.isdir(directory):
            logger.error(f"目录不存在: {directory}")
            return {}
        
        results = {}
        
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            if os.path.isfile(file_path):
                try:
                    inserted, errors_count, errors = self.import_file(
                        file_path, 
                        validator=validator
                    )
                    results[filename] = (inserted, errors_count, errors)
                except Exception as e:
                    logger.error(f"处理文件 {filename} 时发生错误: {e}")
                    results[filename] = (0, 1, [str(e)])
        
        return results
    
    def _infer_columns(self, sample_data: Dict[str, Any]) -> Dict[str, str]:
        """
        从示例数据推断列类型
        :param sample_data: 示例数据行
        :return: 列定义字典
        """
        columns = {'id': 'SERIAL PRIMARY KEY'}
        
        for key, value in sample_data.items():
            if key == 'id':
                continue
            
            if isinstance(value, int):
                columns[key] = 'INTEGER'
            elif isinstance(value, float):
                columns[key] = 'FLOAT'
            elif isinstance(value, datetime):
                columns[key] = 'TIMESTAMP'
            elif isinstance(value, bool):
                columns[key] = 'BOOLEAN'
            else:
                columns[key] = 'TEXT'
        
        return columns
    
    def get_stats(self) -> Dict[str, int]:
        """获取导入统计"""
        return self.stats
    
    def reset_stats(self):
        """重置统计"""
        self.stats = {
            'files_processed': 0,
            'records_parsed': 0,
            'records_validated': 0,
            'records_inserted': 0,
            'errors': 0,
            'warnings': 0
        }

class NBATeamImporter(DataImporter):
    """NBA球队数据导入器"""
    
    def __init__(self, team_abbr: str, config: ImportConfig = None, strict_validation: bool = False):
        super().__init__(config)
        self.team_abbr = team_abbr.upper()
        self.team_name = TeamConfig.get_team_name(team_abbr)
        self.validator = NBADataValidator(strict=strict_validation)
        self._init_table_mappings()
    
    def _init_table_mappings(self):
        """初始化表名映射"""
        self.table_mappings = {
            'roster': f'{self.team_abbr.lower()}_roster',
            'per game': f'{self.team_abbr.lower()}_per_game',
            'per game playoffs': f'{self.team_abbr.lower()}_per_game_playoffs',
            'total': f'{self.team_abbr.lower()}_total',
            'total playoffs': f'{self.team_abbr.lower()}_total_playoffs',
            'advanced': f'{self.team_abbr.lower()}_advanced',
            'advanced playoffs': f'{self.team_abbr.lower()}_advanced_playoffs',
            'gamelog': f'{self.team_abbr.lower()}_gamelog',
            'gamelog playoffs': f'{self.team_abbr.lower()}_gamelog_playoffs',
            'team and opponent stats': f'{self.team_abbr.lower()}_team_stats',
            '59 season': 'team_history_records'
        }
    
    def import_excel_file(self, file_path: str) -> Dict[str, Tuple[int, int, List[str]]]:
        """
        导入NBA球队Excel文件
        :param file_path: Excel文件路径
        :return: {sheet名: (插入数, 错误数, 错误列表)}
        """
        import pandas as pd
        
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return {}
        
        results = {}
        xlsx = pd.ExcelFile(file_path)
        
        for sheet_name in xlsx.sheet_names:
            try:
                # 获取目标表名
                table_name = self.table_mappings.get(sheet_name.lower(), None)
                
                if not table_name:
                    # 自动生成表名
                    table_name = f"{self.team_abbr.lower()}_{sheet_name.lower().replace(' ', '_')}"
                
                # 备份
                if self.config.create_backup and self.db_manager.table_exists(table_name):
                    self.db_manager.backup_table(table_name, self.config.backup_dir)
                
                # 解析数据
                df = pd.read_excel(xlsx, sheet_name=sheet_name)
                df = self._clean_nba_data(df)
                data = df.to_dict('records')
                
                if not data:
                    logger.warning(f"Sheet '{sheet_name}' 没有数据")
                    results[sheet_name] = (0, 0, [])
                    continue
                
                self.stats['records_parsed'] += len(data)
                
                # 验证数据
                valid_data, errors = self.validator.validate_data(data)
                self.stats['records_validated'] += len(valid_data)
                self.stats['errors'] += len(errors)
                
                if not valid_data:
                    logger.warning(f"Sheet '{sheet_name}' 没有通过验证的数据")
                    results[sheet_name] = (0, len(errors), errors)
                    continue
                
                # 创建表
                columns = self._infer_columns(valid_data[0])
                self.db_manager.create_table(table_name, columns)
                
                # 清空数据
                if self.config.overwrite_existing:
                    self.db_manager.truncate_table(table_name)
                
                # 插入数据
                inserted = self.db_manager.insert_data(table_name, valid_data)
                self.stats['records_inserted'] += inserted
                
                logger.info(f"成功导入 Sheet '{sheet_name}' 到表 {table_name}: {inserted} 条记录")
                results[sheet_name] = (inserted, len(errors), errors)
                
            except Exception as e:
                logger.error(f"处理 Sheet '{sheet_name}' 时发生错误: {e}")
                results[sheet_name] = (0, 1, [str(e)])
        
        self.stats['files_processed'] += 1
        return results
    
    def _clean_nba_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        清理NBA数据
        :param df: 原始DataFrame
        :return: 清理后的DataFrame
        """
        # 移除空行和空列
        df = df.dropna(how='all').dropna(how='all', axis=1)
        df = df.reset_index(drop=True)
        
        # 清理列名
        df.columns = [self._clean_column_name(col) for col in df.columns]
        
        # 处理球员姓名
        if 'player' in df.columns:
            df['player'] = df['player'].apply(self._clean_player_name)
        
        # 处理时间格式问题
        if 'mp' in df.columns:
            df['mp'] = df['mp'].apply(self._parse_minutes)
        
        return df
    
    def _clean_column_name(self, name: str) -> str:
        """清理列名"""
        if isinstance(name, str):
            name = str(name).strip()
            name = name.replace(' ', '_').replace('-', '_').replace('/', '_')
            name = name.replace('%', '_pct').replace('$', '_usd')
            
            # 移除非法字符
            name = ''.join(c for c in name if c.isalnum() or c == '_')
            
            # 如果以数字开头，添加前缀
            if name and name[0].isdigit():
                name = 'col_' + name
            
            return name.lower()
        return str(name).lower()
    
    def _clean_player_name(self, name: str) -> str:
        """清理球员姓名"""
        if pd.isna(name):
            return ""
        name = str(name).strip()
        name = name.replace('  (TW)', '').replace('*', '').strip()
        return name
    
    def _parse_minutes(self, value: Any) -> Optional[float]:
        """解析上场时间"""
        from datetime import time, timedelta
        
        if pd.isna(value):
            return None
        
        if isinstance(value, time):
            return float(value.hour) + float(value.minute) / 60
        
        if isinstance(value, timedelta):
            seconds = value.seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return float(hours) + float(minutes) / 60
        
        if isinstance(value, str):
            value = value.strip()
            if ':' in value:
                parts = value.split(':')
                if len(parts) == 2:
                    return float(parts[0]) + float(parts[1]) / 60
        
        try:
            return float(value)
        except:
            return None
