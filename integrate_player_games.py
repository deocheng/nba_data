import pandas as pd
import os
import json
from pathlib import Path

# 定义路径
BASE_DIR = Path(__file__).parent
PLAYER_GAMES_DIR = BASE_DIR / "CSV_Clean" / "player_games"
OUTPUT_DIR = BASE_DIR / "CSV_Clean"


def calculate_ts_percent(row):
    """计算真实命中率"""
    try:
        pts = row.get('pts', 0)
        fga = row.get('fga', 0)
        fta = row.get('fta', 0)
        
        if pd.isna(fga) or pd.isna(fta) or fga == 0 and fta == 0:
            return 0
        
        denominator = 2 * (fga + 0.44 * fta)
        if denominator == 0:
            return 0
        
        return (pts / denominator) * 100
    except:
        return 0


def calculate_gbpm(row):
    """简化的 gBPM 计算"""
    try:
        pts = row.get('pts', 0)
        trb = row.get('trb', row.get('reb', 0))
        ast = row.get('ast', 0)
        stl = row.get('stl', 0)
        blk = row.get('blk', 0)
        tov = row.get('tov', 0)
        fg_pct = row.get('fg_pct', 0)
        
        if pd.isna(fg_pct):
            fg_pct = 0
        
        # 简化的 gBPM 计算
        value = pts + trb * 1.5 + ast * 2 + stl * 3 + blk * 3 - tov * 2 + fg_pct * 100
        return round(value, 1)
    except:
        return 0


def convert_mp_to_float(mp_str):
    """将 mm:ss 格式转换为小数"""
    try:
        if pd.isna(mp_str) or mp_str == 'Inactive' or mp_str == '':
            return 0
        if ':' in str(mp_str):
            parts = str(mp_str).split(':')
            minutes = float(parts[0])
            seconds = float(parts[1]) if len(parts) > 1 else 0
            return minutes + seconds / 60
        return float(mp_str)
    except:
        return 0


def integrate_player_games():
    """整合所有球员的单场比赛数据"""
    print("开始整合球员单场比赛数据...")
    
    all_files = list(PLAYER_GAMES_DIR.glob("*.csv"))
    print(f"找到 {len(all_files)} 个球员数据文件")
    
    all_data = []
    
    for file_path in all_files:
        print(f"处理文件: {file_path.name}")
        
        try:
            df = pd.read_csv(file_path)
            
            if df.empty:
                continue
            
            # 标准化列名
            df = df.rename(columns={
                'player_name': 'player',
                'game_date': 'date',
                'mp': 'minutes_played',
                'reb': 'trb'
            })
            
            # 转换时间格式
            if 'minutes_played' in df.columns:
                df['minutes_played'] = df['minutes_played'].apply(convert_mp_to_float)
                df = df[df['minutes_played'] > 0].copy()
            
            # 转换数据类型
            numeric_cols = ['fg', 'fga', 'fg_pct', 'three_p', 'three_pa', 
                           'three_p_pct', 'ft', 'fta', 'ft_pct', 'orb', 'drb', 'trb', 
                           'ast', 'stl', 'blk', 'tov', 'pf', 'pts', 'minutes_played']
            
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # 计算真实命中率
            df['ts_percent'] = df.apply(calculate_ts_percent, axis=1)
            df['ts_percent'] = df['ts_percent'].round(1)
            
            # 计算 gBPM
            df['gBPM'] = df.apply(calculate_gbpm, axis=1)
            
            # 提取球员名称
            if 'player' not in df.columns or df['player'].isna().all():
                # 从文件名推测球员名
                filename = file_path.stem
                player_name = filename.replace('_career', '').replace('_', ' ').title()
                df['player'] = player_name
            
            all_data.append(df)
            print(f"  - 添加 {len(df)} 条记录")
            
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    if all_data:
        merged_df = pd.concat(all_data, ignore_index=True)
        
        # 保存完整数据
        output_file = OUTPUT_DIR / "all_player_games.csv"
        merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"数据已保存到 {output_file}")
        print(f"共 {len(merged_df)} 条比赛记录")
        
        # 按日期排序，获取最近的比赛
        if 'date' in merged_df.columns:
            try:
                merged_df['date'] = pd.to_datetime(merged_df['date'], errors='coerce')
                merged_df = merged_df.sort_values('date', ascending=False)
                
                # 保存最新比赛的JSON
                latest_games = merged_df.head(200).to_dict('records')
                json_output = OUTPUT_DIR / "latest_player_games.json"
                
                # 转换日期格式为字符串
                for game in latest_games:
                    if 'date' in game and pd.notna(game['date']):
                        game['date'] = str(game['date']).split(' ')[0]
                
                with open(json_output, 'w', encoding='utf-8') as f:
                    json.dump(latest_games, f, ensure_ascii=False, indent=2, default=str)
                print(f"最新比赛数据已保存到 {json_output}")
                
            except Exception as e:
                print(f"日期处理出错: {e}")
                import traceback
                traceback.print_exc()
        
        return merged_df
    else:
        print("没有找到可用的数据")
        return None


if __name__ == "__main__":
    integrate_player_games()
