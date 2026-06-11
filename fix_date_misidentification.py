import pandas as pd
import re
from pathlib import Path

def find_and_fix_date_misidentified_scores(search_path='.'):
    """
    查找目录中所有Excel和CSV文件，找出可能被误识别为日期的比分数据，并进行修复
    """
    problematic_files = []
    
    for file in Path(search_path).rglob('*.xlsx'):
        try:
            df = pd.read_excel(file, engine='openpyxl')
            fix_date_misidentification(file, df, problematic_files)
        except Exception as e:
            pass
    
    for file in Path(search_path).rglob('*.csv'):
        try:
            df = pd.read_csv(file)
            fix_date_misidentification(file, df, problematic_files)
        except Exception as e:
            pass
    
    return problematic_files

def fix_date_misidentification(file_path, df, problematic_files):
    """
    检查DataFrame中是否有被误识别为日期的比分数据，并尝试修复
    """
    file_name = str(file_path)
    
    for col in df.columns:
        if df[col].dtype == 'datetime64[ns]':
            sample_values = df[col].dropna().head(20).tolist()
            if sample_values:
                for val in sample_values:
                    # 检查年份是否异常（比分可能被识别为日期，年份会是不合理的值）
                    if val.year < 1900 or val.year > 2100:
                        problematic_files.append({
                            'file': file_name,
                            'column': col,
                            'sample_value': str(val),
                            'issue': 'Date misidentified - year out of reasonable range'
                        })
                        break
    
    for col in df.columns:
        if df[col].dtype == 'object':
            sample_values = df[col].dropna().head(20).tolist()
            for val in sample_values:
                val_str = str(val)
                # 检查是否是比分格式（如"102-115"）
                if '-' in val_str and len(val_str) <= 10:
                    parts = val_str.split('-')
                    if len(parts) == 2:
                        try:
                            num1 = int(parts[0].strip())
                            num2 = int(parts[1].strip())
                            if 50 <= num1 <= 200 and 50 <= num2 <= 200:
                                problematic_files.append({
                                    'file': file_name,
                                    'column': col,
                                    'sample_value': val_str,
                                    'issue': 'Score format detected (XX-YY where X,Y between 50-200)'
                                })
                                break
                        except:
                            pass

def export_fixed_data(file_path, output_dir='fixed_data'):
    """
    将修复后的数据导出到新文件
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        if file_path.suffix == '.xlsx':
            df = pd.read_excel(file_path, engine='openpyxl', dtype=str)
        else:
            df = pd.read_csv(file_path, dtype=str)
        
        for col in df.columns:
            for i, val in enumerate(df[col]):
                if pd.notna(val):
                    val_str = str(val)
                    # 检查是否是比分格式
                    if '-' in val_str and len(val_str) <= 10:
                        parts = val_str.split('-')
                        if len(parts) == 2:
                            try:
                                num1 = int(parts[0].strip())
                                num2 = int(parts[1].strip())
                                if 50 <= num1 <= 200 and 50 <= num2 <= 200:
                                    df.at[i, col] = f"{num1}-{num2}"
                            except:
                                pass
        
        output_file = output_path / file_path.name
        if file_path.suffix == '.xlsx':
            df.to_excel(output_file, index=False, engine='openpyxl')
        else:
            df.to_csv(output_file, index=False)
        
        print(f"Fixed data exported to: {output_file}")
        return output_file
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

if __name__ == "__main__":
    print("=== 查找被误识别为日期的比分数据 ===")
    print()
    
    problematic_files = find_and_fix_date_misidentified_scores()
    
    if problematic_files:
        print("找到以下可能存在问题的文件:")
        print("-" * 80)
        for i, issue in enumerate(problematic_files, 1):
            print(f"{i}. 文件: {issue['file']}")
            print(f"   列: {issue['column']}")
            print(f"   示例值: {issue['sample_value']}")
            print(f"   问题: {issue['issue']}")
            print()
        
        print("是否需要修复这些文件?")
        user_input = input("输入 'yes' 进行修复: ").strip().lower()
        if user_input == 'yes':
            for issue in problematic_files:
                export_fixed_data(Path(issue['file']))
    else:
        print("未找到被误识别为日期的比分数据。")
        print("\n如果您知道文件位置，请提供文件路径。")