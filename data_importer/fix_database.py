#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复或重建数据库表
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_importer.database import DatabaseManager
from data_importer.config import DatabaseConfig
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def rebuild_tables():
    """重建表（删除并重新创建）"""
    db_manager = DatabaseManager(DatabaseConfig())
    
    # 检查表是否存在
    tables_to_check = ['play_by_play', 'game_metadata']
    
    for table_name in tables_to_check:
        exists = db_manager.table_exists(table_name)
        logger.info(f"表 {table_name} 存在: {exists}")
        if exists:
            # 备份数据（可选）
            try:
                db_manager.backup_table(table_name)
            except Exception as e:
                logger.warning(f"备份表失败: {e}")
            
            # 删除表
            try:
                db_manager.execute(f'DROP TABLE IF EXISTS {table_name} CASCADE')
                logger.info(f"已删除表: {table_name}")
            except Exception as e:
                logger.error(f"删除表失败: {e}")
    
    db_manager.close()
    
    logger.info("表已清理，现在重新初始化...")


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("数据库表重建工具")
    logger.info("=" * 60)
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--rebuild', action='store_true', help='重建表（删除并重新创建）')
    args = parser.parse_args()
    
    if args.rebuild:
        confirm = input("警告: 这将删除 play_by_play 和 game_metadata 表! 确定吗? (y/n): ")
        if confirm.lower() == 'y':
            rebuild_tables()
        else:
            logger.info("取消操作")
    else:
        logger.info("使用 --rebuild 参数来重建表")
    
    logger.info("完成")
