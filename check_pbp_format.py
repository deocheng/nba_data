#!/usr/bin/env python3
"""检查PBP数据格式"""
import pandas as pd

# 检查1997数据格式
print("=" * 80)
print("1997数据格式")
print("=" * 80)
df1 = pd.read_csv('CSV/pbp1997.csv', nrows=10)
print(df1.head())
print("\n列:", df1.columns.tolist())

# 检查新数据格式
print("\n" + "=" * 80)
print("2026数据格式")
print("=" * 80)
df2 = pd.read_csv('CSV/2026_season/pbp/202510210LAL_pbp.csv', nrows=20)
print(df2.head(20))
print("\n列:", df2.columns.tolist())
