#!/usr/bin/env python3
"""检查PBP文件结构和大小"""
import pandas as pd
from pathlib import Path
import os

csv_dir = Path('CSV')

pbp_files = sorted(csv_dir.glob('pbp*.csv'))
print(f"找到 {len(pbp_files)} 个PBP文件")
print("=" * 100)
print(f"{'文件名':<20} {'大小(MB)':>12} {'行数':>12} {'列数':>6}")
print("=" * 100)

for pbp_file in pbp_files:
    size_mb = os.path.getsize(pbp_file) / (1024 * 1024)
    try:
        df = pd.read_csv(pbp_file, nrows=1)
        cols = len(df.columns)
        # 估算行数
        with open(pbp_file, 'r') as f:
            line_count = sum(1 for _ in f) - 1
        print(f"{pbp_file.name:<20} {size_mb:>10.2f} MB {line_count:>12,} {cols:>6}")
    except Exception as e:
        print(f"{pbp_file.name:<20} {size_mb:>10.2f} MB 读取失败: {e}")

print("=" * 100)

# 检查几个代表性文件的结构
print("\n\n🔍 字段结构分析 (样本文件)")
print("=" * 100)

sample_files = [
    'pbp1998.csv',
    'pbp2005.csv',
    'pbp2015.csv',
    'pbp2025.csv',
]

for fname in sample_files:
    fpath = csv_dir / fname
    if fpath.exists():
        try:
            df = pd.read_csv(fpath, nrows=5)
            print(f"\n📄 {fname}")
            print(f"  列: {list(df.columns)}")
            print(f"  前3行:")
            print(df.head(3).to_string())
        except Exception as e:
            print(f"  读取失败: {e}")
