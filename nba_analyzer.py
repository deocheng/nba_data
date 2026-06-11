"""
NBA数据分析工具箱 - 统一入口

整合所有分析工具，提供便捷的数据分析体验：
1. 单场比赛分析
2. 系列赛对位分析
3. 投篮分析（出手距离/终结方式）
4. On-Off分析
5. Plus-Minus分析
6. 最佳出场时长分析
"""

import argparse
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent

def analyze_single_game(args):
    """单场比赛分析"""
    print(f"🏀 分析单场比赛: {args.game_id}")
    
    from single_game_analyzer import SingleGameAnalyzer
    analyzer = SingleGameAnalyzer()
    analyzer.pbp_files = list(BASE_DIR / "CSV" / "2026_season" / "pbp" / f"{args.game_id}_pbp.json")
    
    if not analyzer.pbp_files:
        print(f"❌ 未找到比赛文件: {args.game_id}")
        return
    
    analyzer.analyze_and_report()

def analyze_shooting(args):
    """投篮分析"""
    print(f"🎯 分析投篮数据: {args.game_id}")
    
    from enhanced_shooting_analyzer import EnhancedGameAnalyzer
    analyzer = EnhancedGameAnalyzer()
    
    if args.game_id:
        analyzer.pbp_files = list(BASE_DIR / "CSV" / "2026_season" / "pbp" / f"{args.game_id}_pbp.json")
    else:
        analyzer.pbp_files = list(BASE_DIR / "CSV" / "2026_season" / "pbp" / "*_pbp.json")
    
    analyzer.analyze_and_report()

def analyze_on_off(args):
    """On-Off分析"""
    print("📊 运行On-Off分析")
    
    from br_style_on_off_analyzer import EnhancedOnOffAnalyzer
    analyzer = EnhancedOnOffAnalyzer()
    analyzer.run_analysis()
    analyzer.save_report()

def analyze_series(args):
    """系列赛对位分析"""
    print(f"🏆 分析系列赛: {args.team_a} vs {args.team_b}")
    
    from playoff_series_analyzer import PlayoffSeriesAnalyzer
    analyzer = PlayoffSeriesAnalyzer()
    
    team_a_players = args.team_a_players.split(',') if args.team_a_players else []
    team_b_players = args.team_b_players.split(',') if args.team_b_players else []
    
    report = analyzer.generate_series_report(args.team_a, team_a_players, args.team_b, team_b_players)
    print(report)
    analyzer.save_report(args.team_a, args.team_b, report)

def analyze_minutes(args):
    """最佳出场时长分析"""
    print("⏱️ 分析最佳出场时长")
    
    from player_minutes_db_analyzer import PlayerMinutesAnalyzer
    analyzer = PlayerMinutesAnalyzer()
    
    if analyzer.connect_db():
        if analyzer.load_player_game_logs():
            analyzer.calculate_efficiency()
            analyzer.save_report()
        analyzer.close()

def show_stats(args):
    """显示数据统计"""
    pbp_dir = BASE_DIR / "CSV" / "2026_season" / "pbp"
    pbp_files = list(pbp_dir.glob("*_pbp.json"))
    
    print("=" * 60)
    print("📊 数据统计概览")
    print("=" * 60)
    print(f"📁 PBP文件数量: {len(pbp_files)}")
    print("=" * 60)
    
    # 数据库统计
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("database", str(BASE_DIR / 'data_importer' / 'database.py'))
        database = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(database)
        
        db = database.DatabaseManager()
        db.connect()
        
        cursor = db.conn.cursor()
        
        cursor.execute("SELECT COUNT(DISTINCT game_id) FROM play_by_play")
        games_in_db = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM play_by_play")
        records_in_db = cursor.fetchone()[0]
        
        db.close()
        
        print(f"🗄️ 数据库比赛数: {games_in_db}")
        print(f"📝 数据库记录数: {records_in_db}")
    except:
        print("⚠️ 无法连接数据库")
    
    print("=" * 60)

def list_tools(args):
    """列出所有可用工具"""
    tools = [
        {"name": "single-game", "desc": "单场比赛详细分析", "usage": "--game-id <比赛ID>"},
        {"name": "shooting", "desc": "投篮分析（出手距离/终结方式）", "usage": "[--game-id <比赛ID>]"},
        {"name": "on-off", "desc": "On-Off数据分析（BR风格）", "usage": ""},
        {"name": "series", "desc": "系列赛对位分析", "usage": "--team-a A队 --team-b B队"},
        {"name": "minutes", "desc": "最佳出场时长分析", "usage": ""},
        {"name": "stats", "desc": "数据统计概览", "usage": ""},
        {"name": "list-tools", "desc": "列出所有工具", "usage": ""},
    ]
    
    print("=" * 70)
    print("🛠️ NBA数据分析工具箱")
    print("=" * 70)
    print(f"{'命令':<15} {'描述':<30} {'用法':<25}")
    print(f"{'-----':<15} {'-----':<30} {'-----':<25}")
    
    for tool in tools:
        print(f"{tool['name']:<15} {tool['desc']:<30} {tool['usage']:<25}")
    
    print("\n📖 使用示例:")
    print("  python nba_analyzer.py single-game --game-id 202512280LAL")
    print("  python nba_analyzer.py shooting --game-id 202512290HOU")
    print("  python nba_analyzer.py on-off")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(
        prog='nba_analyzer',
        description='NBA数据分析工具箱 - 整合多种分析工具',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 单场比赛分析
    sg_parser = subparsers.add_parser('single-game', help='单场比赛详细分析')
    sg_parser.add_argument('--game-id', required=True, help='比赛ID（如 202512280LAL）')
    
    # 投篮分析
    st_parser = subparsers.add_parser('shooting', help='投篮分析')
    st_parser.add_argument('--game-id', help='比赛ID（可选，默认分析最新比赛）')
    
    # On-Off分析
    oo_parser = subparsers.add_parser('on-off', help='On-Off数据分析')
    
    # 系列赛分析
    se_parser = subparsers.add_parser('series', help='系列赛对位分析')
    se_parser.add_argument('--team-a', required=True, help='A队名称')
    se_parser.add_argument('--team-b', required=True, help='B队名称')
    se_parser.add_argument('--team-a-players', help='A队球员列表（逗号分隔）')
    se_parser.add_argument('--team-b-players', help='B队球员列表（逗号分隔）')
    
    # 出场时长分析
    mi_parser = subparsers.add_parser('minutes', help='最佳出场时长分析')
    
    # 统计概览
    st_parser = subparsers.add_parser('stats', help='数据统计概览')
    
    # 列出工具
    lt_parser = subparsers.add_parser('list-tools', help='列出所有工具')
    
    args = parser.parse_args()
    
    if not args.command:
        list_tools(args)
        return
    
    try:
        if args.command == 'single-game':
            analyze_single_game(args)
        elif args.command == 'shooting':
            analyze_shooting(args)
        elif args.command == 'on-off':
            analyze_on_off(args)
        elif args.command == 'series':
            analyze_series(args)
        elif args.command == 'minutes':
            analyze_minutes(args)
        elif args.command == 'stats':
            show_stats(args)
        elif args.command == 'list-tools':
            list_tools(args)
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
