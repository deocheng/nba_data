#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查爬取进度
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_importer.pbp_storage import PBPDataStorage

def main():
    print("=" * 60)
    print("爬取进度摘要")
    print("=" * 60)
    
    storage = PBPDataStorage()
    summary = storage.get_import_summary()
    
    print(f"总比赛: {summary['total_games']}")
    print(f"PBP已保存: {summary['pbp_saved']}")
    print(f"PBP已导入: {summary['pbp_imported']}")
    print(f"PBP记录总数: {summary['pbp_records']}")
    
    storage.close()
    
    # 检查文件数
    pbp_dir = 'CSV/2026_season/pbp'
    if os.path.exists(pbp_dir):
        pbp_files = [f for f in os.listdir(pbp_dir) if f.endswith('_pbp.json')]
        print(f"\nPBP文件数: {len(pbp_files)}")

if __name__ == "__main__":
    main()
