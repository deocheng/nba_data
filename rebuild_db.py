#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速重建数据库表
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_importer.database import DatabaseManager
from data_importer.config import DatabaseConfig

print("=" * 60)
print("重建数据库表")
print("=" * 60)

db_manager = DatabaseManager(DatabaseConfig())

# 删除旧表
tables = ['play_by_play', 'game_metadata']

for table in tables:
    try:
        db_manager.execute(f'DROP TABLE IF EXISTS {table} CASCADE')
        print(f"✓ 删除表: {table}")
    except Exception as e:
        print(f"✗ 删除表失败 {table}: {e}")

db_manager.close()
print("\n表已删除，现在重新初始化存储系统...")

from data_importer.pbp_storage import PBPDataStorage
storage = PBPDataStorage()
print("\n✓ 表重建完成!")

summary = storage.get_import_summary()
print(f"\n摘要: {summary}")

storage.close()
print("\n完成!")
