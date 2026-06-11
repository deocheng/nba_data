"""
数据解析模块
支持多种格式的数据解析
"""

import pandas as pd
import os
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, time, timedelta
import logging

logger = logging.getLogger(__name__)

class DataParser:
    """数据解析器基类"""
    
    def __init__(self):
        self.errors = []
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """解析文件"""
        raise NotImplementedError
    
    def add_error(self, message: str, row: int = None):
        """添加错误信息"""
        if row is not None:
            self.errors.append(f"第{row}行: {message}")
        else:
            self.errors.append(message)
    
    def get_errors(self) -> List[str]:
        """获取所有错误"""
        return self.errors
    
    def clear_errors(self):
        """清空错误"""
        self.errors = []

class ExcelParser(DataParser):
    """Excel文件解析器"""
    
    def __init__(self):
        super().__init__()
    
    def parse(self, file_path: str, sheet_name: str = None) -> List[Dict[str, Any]]:
        """
        解析Excel文件
        :param file_path: 文件路径
        :param sheet_name: 指定sheet名称，None表示解析所有sheet
        :return: 数据列表
        """
        try:
            xlsx = pd.ExcelFile(file_path)
            
            if sheet_name:
                if sheet_name not in xlsx.sheet_names:
                    self.add_error(f"Sheet '{sheet_name}' 不存在")
                    return []
                return self._parse_sheet(xlsx, sheet_name)
            else:
                all_data = []
                for name in xlsx.sheet_names:
                    sheet_data = self._parse_sheet(xlsx, name)
                    all_data.extend(sheet_data)
                return all_data
        
        except Exception as e:
            self.add_error(f"读取Excel文件失败: {e}")
            return []
    
    def _parse_sheet(self, xlsx: pd.ExcelFile, sheet_name: str) -> List[Dict[str, Any]]:
        """解析单个sheet"""
        try:
            df = pd.read_excel(xlsx, sheet_name=sheet_name)
            df = self._clean_dataframe(df)
            return df.to_dict('records')
        except Exception as e:
            self.add_error(f"解析Sheet '{sheet_name}' 失败: {e}")
            return []
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """清理DataFrame数据"""
        # 移除完全空的行和列
        df = df.dropna(how='all').dropna(how='all', axis=1)
        
        # 重置索引
        df = df.reset_index(drop=True)
        
        # 处理列名中的特殊字符
        df.columns = [self._clean_column_name(col) for col in df.columns]
        
        # 转换时间格式
        df = self._convert_time_columns(df)
        
        return df
    
    def _clean_column_name(self, name: str) -> str:
        """清理列名"""
        if isinstance(name, str):
            # 移除特殊字符，转换为小写，替换空格为下划线
            name = str(name).strip()
            name = name.replace(' ', '_').replace('-', '_').replace('/', '_')
            name = ''.join(c for c in name if c.isalnum() or c == '_')
            return name.lower()
        return str(name).lower()
    
    def _convert_time_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """转换时间列"""
        for col in df.columns:
            if 'time' in col.lower() or 'minute' in col.lower() or 'mp' in col.lower():
                df[col] = df[col].apply(self._parse_time_value)
        return df
    
    def _parse_time_value(self, value: Any) -> Optional[float]:
        """解析时间值（处理Excel时间格式问题）"""
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
                elif len(parts) == 3:
                    return float(parts[0]) + float(parts[1]) / 60 + float(parts[2]) / 3600
        
        try:
            return float(value)
        except:
            return None

class CSVParser(DataParser):
    """CSV文件解析器"""
    
    def __init__(self):
        super().__init__()
    
    def parse(self, file_path: str, delimiter: str = ',') -> List[Dict[str, Any]]:
        """
        解析CSV文件
        :param file_path: 文件路径
        :param delimiter: 分隔符
        :return: 数据列表
        """
        try:
            df = pd.read_csv(file_path, delimiter=delimiter)
            df = self._clean_dataframe(df)
            return df.to_dict('records')
        except Exception as e:
            self.add_error(f"读取CSV文件失败: {e}")
            return []
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """清理DataFrame数据"""
        df = df.dropna(how='all').dropna(how='all', axis=1)
        df = df.reset_index(drop=True)
        
        df.columns = [self._clean_column_name(col) for col in df.columns]
        
        return df
    
    def _clean_column_name(self, name: str) -> str:
        """清理列名"""
        if isinstance(name, str):
            name = str(name).strip()
            name = name.replace(' ', '_').replace('-', '_').replace('/', '_')
            name = ''.join(c for c in name if c.isalnum() or c == '_')
            return name.lower()
        return str(name).lower()

class JSONParser(DataParser):
    """JSON文件解析器"""
    
    def __init__(self):
        super().__init__()
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """
        解析JSON文件
        :param file_path: 文件路径
        :return: 数据列表
        """
        try:
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
            else:
                self.add_error("JSON格式不正确")
                return []
        
        except Exception as e:
            self.add_error(f"读取JSON文件失败: {e}")
            return []

class ParserFactory:
    """解析器工厂"""
    
    @staticmethod
    def get_parser(file_path: str) -> DataParser:
        """
        根据文件扩展名获取解析器
        :param file_path: 文件路径
        :return: 对应的解析器实例
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in ['.xlsx', '.xls']:
            return ExcelParser()
        elif ext == '.csv':
            return CSVParser()
        elif ext == '.json':
            return JSONParser()
        else:
            raise ValueError(f"不支持的文件格式: {ext}")
    
    @staticmethod
    def parse_file(file_path: str, **kwargs) -> List[Dict[str, Any]]:
        """
        解析文件（便捷方法）
        :param file_path: 文件路径
        :param kwargs: 额外参数
        :return: 数据列表
        """
        parser = ParserFactory.get_parser(file_path)
        return parser.parse(file_path, **kwargs)
