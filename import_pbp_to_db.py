"""
批量导入PBP数据到数据库
检查已导入和未导入的文件，然后导入所有未导入的文件
"""

import os
import json
from pathlib import Path
import sys
import importlib.util

# 添加data_importer到路径
sys.path.insert(0, str(Path(__file__).parent / 'data_importer'))

# 使用importlib导入模块
spec = importlib.util.spec_from_file_location("database", 
    str(Path(__file__).parent / 'data_importer' / 'database.py'))
database = importlib.util.module_from_spec(spec)
spec.loader.exec_module(database)

spec2 = importlib.util.spec_from_file_location("pbp_storage", 
    str(Path(__file__).parent / 'data_importer' / 'pbp_storage.py'))
pbp_storage = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(pbp_storage)

BASE_DIR = Path(__file__).parent
PBP_DIR = BASE_DIR / "CSV" / "2026_season" / "pbp"

def main():
    print("=" * 70)
    print("📥 批量导入PBP数据到数据库")
    print("=" * 70)
    
    pbp_files = list(PBP_DIR.glob("*_pbp.json"))
    print(f"📁 发现 {len(pbp_files)} 个PBP文件")
    
    db = database.DatabaseManager()
    db.connect()
    
    cursor = db.conn.cursor()
    cursor.execute("SELECT DISTINCT game_id FROM play_by_play")
    imported_games = {row[0] for row in cursor.fetchall()}
    print(f"🗄️ 数据库中已导入 {len(imported_games)} 场比赛")
    
    unimported_files = []
    for filepath in pbp_files:
        game_id = filepath.stem.replace("_pbp", "")
        if game_id not in imported_games:
            unimported_files.append(filepath)
    
    print(f"🔄 需要导入 {len(unimported_files)} 个文件")
    
    storage = pbp_storage.PBPStorage()
    success_count = 0
    error_count = 0
    
    for filepath in unimported_files:
        try:
            game_id = filepath.stem.replace("_pbp", "")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            inserted = storage.import_to_database(game_id, data)
            print(f"✅ {game_id}: 成功导入 {inserted} 条记录")
            success_count += 1
        
        except Exception as e:
            print(f"❌ {filepath.name}: 导入失败 - {str(e)}")
            error_count += 1
    
    db.close()
    
    print("\n" + "=" * 70)
    print("📊 导入完成")
    print("=" * 70)
    print(f"✅ 成功: {success_count} 个文件")
    print(f"❌ 失败: {error_count} 个文件")
    print("=" * 70)

if __name__ == "__main__":
    main()
