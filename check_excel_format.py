import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent
EXCEL_FILE = BASE_DIR / "CSV" / "league leaders 1955-2026 .xlsx"

xls = pd.ExcelFile(EXCEL_FILE)

print(f"工作表数量: {len(xls.sheet_names)}")
print(f"第一个工作表: {xls.sheet_names[0]}")

df = pd.read_excel(xls, sheet_name=xls.sheet_names[0], header=None)

print(f"\n前30行数据:")
print(df.head(30).to_string())

print(f"\n列数: {len(df.columns)}")
print(f"行数: {len(df)}")