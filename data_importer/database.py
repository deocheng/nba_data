"""
数据库连接模块
提供健壮的数据库连接和操作功能
"""

import psycopg2
import psycopg2.errors
from psycopg2 import sql
from contextlib import contextmanager
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from .config import DatabaseConfig

logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self.connection = None
        self._connect()
    
    def _connect(self):
        """建立数据库连接"""
        try:
            self.connection = psycopg2.connect(**self.config.to_dict())
            self.connection.set_client_encoding('UTF8')
            logger.info(f"成功连接数据库: {self.config.dbname}")
        except psycopg2.Error as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def reconnect(self):
        """重新连接数据库"""
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
        self._connect()
    
    @contextmanager
    def get_cursor(self):
        """获取游标上下文管理器"""
        if not self.connection:
            self._connect()
        
        cursor = self.connection.cursor()
        try:
            yield cursor
        except Exception as e:
            self.connection.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        else:
            self.connection.commit()
        finally:
            cursor.close()
    
    def execute(self, query: str, params: tuple = None):
        """执行SQL查询"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor
    
    def execute_many(self, query: str, params_list: List[tuple]):
        """批量执行SQL查询"""
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)
    
    def fetch_one(self, query: str, params: tuple = None):
        """获取单行结果"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()
    
    def fetch_all(self, query: str, params: tuple = None):
        """获取所有结果"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    
    def fetch_dict(self, query: str, params: tuple = None) -> List[Dict]:
        """获取结果并转换为字典列表"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            )
        """
        result = self.fetch_one(query, (table_name,))
        return result[0] if result else False
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """获取表的列名"""
        query = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = %s
            ORDER BY ordinal_position
        """
        result = self.fetch_all(query, (table_name,))
        return [row[0] for row in result]
    
    def create_table(self, table_name: str, columns: Dict[str, str], 
                     primary_key: str = 'id', if_not_exists: bool = True):
        """
        创建表
        :param table_name: 表名
        :param columns: 列定义字典 {column_name: data_type}
        :param primary_key: 主键列名
        :param if_not_exists: 是否添加IF NOT EXISTS
        """
        if if_not_exists and self.table_exists(table_name):
            logger.info(f"表 {table_name} 已存在，跳过创建")
            return
        
        columns_def = []
        for col_name, col_type in columns.items():
            if col_name == primary_key:
                columns_def.append(f"{col_name} SERIAL PRIMARY KEY")
            else:
                columns_def.append(f"{col_name} {col_type}")
        
        columns_str = ",\n    ".join(columns_def)
        query = f"""
            CREATE TABLE {'IF NOT EXISTS ' if if_not_exists else ''}{table_name} (
                {columns_str}
            )
        """
        
        self.execute(query)
        logger.info(f"表 {table_name} 创建成功")
    
    def truncate_table(self, table_name: str):
        """清空表数据"""
        if not self.table_exists(table_name):
            logger.warning(f"表 {table_name} 不存在，跳过清空")
            return
        
        query = f"TRUNCATE TABLE {table_name}"
        self.execute(query)
        logger.info(f"表 {table_name} 已清空")
    
    def insert_data(self, table_name: str, data: List[Dict[str, Any]], 
                    batch_size: int = 100):
        """
        插入数据
        :param table_name: 表名
        :param data: 数据列表
        :param batch_size: 批量插入大小
        """
        if not data:
            logger.warning("没有数据需要插入")
            return 0
        
        columns = list(data[0].keys())
        placeholders = ", ".join([f"%({col})s" for col in columns])
        columns_str = ", ".join(columns)
        
        query = f"""
            INSERT INTO {table_name} ({columns_str})
            VALUES ({placeholders})
        """
        
        inserted = 0
        errors = 0
        
        with self.get_cursor() as cursor:
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                try:
                    cursor.executemany(query, batch)
                    inserted += len(batch)
                except Exception as e:
                    errors += len(batch)
                    logger.error(f"批量插入失败 (行 {i}-{i+len(batch)-1}): {e}")
                    if not self.config.skip_errors:
                        raise
        
        logger.info(f"成功插入 {inserted} 条记录，跳过 {errors} 条错误记录")
        return inserted
    
    def backup_table(self, table_name: str, backup_dir: str = 'backups') -> str:
        """备份表数据"""
        import os
        
        if not self.table_exists(table_name):
            logger.warning(f"表 {table_name} 不存在，跳过备份")
            return ""
        
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"{table_name}_{timestamp}.sql")
        
        query = f"COPY {table_name} TO STDOUT WITH CSV HEADER"
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            with self.get_cursor() as cursor:
                cursor.copy_expert(query, f)
        
        logger.info(f"表 {table_name} 已备份到 {backup_file}")
        return backup_file
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            try:
                self.connection.close()
                logger.info("数据库连接已关闭")
            except Exception as e:
                logger.error(f"关闭连接失败: {e}")
    
    def __del__(self):
        self.close()

# 全局数据库管理器实例
db_manager = DatabaseManager()
