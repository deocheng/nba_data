"""
命令行接口模块
提供命令行交互功能
"""

import argparse
import logging
import sys
import os

from .config import ImportConfig, TeamConfig
from .importers import DataImporter, NBATeamImporter

logger = logging.getLogger(__name__)

def setup_logging(verbose: bool = False):
    """设置日志"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def print_stats(stats: dict):
    """打印统计信息"""
    print("\n" + "="*50)
    print("导入统计报告")
    print("="*50)
    print(f"处理文件数: {stats['files_processed']}")
    print(f"解析记录数: {stats['records_parsed']}")
    print(f"验证通过数: {stats['records_validated']}")
    print(f"成功插入数: {stats['records_inserted']}")
    print(f"错误数: {stats['errors']}")
    print(f"警告数: {stats['warnings']}")
    print("="*50 + "\n")

def import_file(args):
    """导入单个文件"""
    config = ImportConfig(
        create_backup=args.backup,
        overwrite_existing=not args.no_overwrite,
        skip_errors=args.skip_errors,
        verbose=args.verbose
    )
    
    importer = DataImporter(config)
    inserted, errors_count, errors = importer.import_file(args.file, args.table)
    
    print(f"导入完成:")
    print(f"  成功插入: {inserted} 条记录")
    print(f"  错误数: {errors_count}")
    
    if errors:
        print("\n错误详情:")
        for error in errors[:10]:
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... 还有 {len(errors) - 10} 条错误")

def import_directory(args):
    """导入目录"""
    config = ImportConfig(
        input_dir=args.directory,
        create_backup=args.backup,
        overwrite_existing=not args.no_overwrite,
        skip_errors=args.skip_errors,
        verbose=args.verbose
    )
    
    importer = DataImporter(config)
    results = importer.import_directory()
    
    print("导入结果:")
    for filename, (inserted, errors_count, errors) in results.items():
        status = "✅" if errors_count == 0 else "⚠️" if inserted > 0 else "❌"
        print(f"{status} {filename}: {inserted} 条记录, {errors_count} 个错误")
    
    print_stats(importer.get_stats())

def import_nba_team(args):
    """导入NBA球队数据"""
    config = ImportConfig(
        create_backup=args.backup,
        overwrite_existing=not args.no_overwrite,
        skip_errors=args.skip_errors,
        verbose=args.verbose
    )
    
    team_abbr = args.team
    if team_abbr not in TeamConfig.TEAM_ABBR_MAP:
        print(f"错误: 不支持的球队缩写: {team_abbr}")
        print(f"支持的球队: {', '.join(TeamConfig.TEAM_ABBR_MAP.keys())}")
        sys.exit(1)
    
    importer = NBATeamImporter(team_abbr, config)
    results = importer.import_excel_file(args.file)
    
    print("\n导入结果:")
    for sheet_name, (inserted, errors_count, errors) in results.items():
        status = "✅" if errors_count == 0 else "⚠️" if inserted > 0 else "❌"
        print(f"{status} {sheet_name}: {inserted} 条记录, {errors_count} 个错误")
    
    print_stats(importer.get_stats())

def list_tables(args):
    """列出数据库中的表"""
    from .database import DatabaseManager
    
    db_manager = DatabaseManager()
    tables = db_manager.fetch_all("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    
    print("数据库中的表:")
    for table in tables:
        print(f"  - {table[0]}")

def show_team_abbrs(args):
    """显示所有支持的球队缩写"""
    print("支持的NBA球队缩写:")
    for abbr, name in TeamConfig.TEAM_ABBR_MAP.items():
        print(f"  {abbr}: {name}")

def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        prog='data_importer',
        description='通用数据导入应用 - 支持多种格式的数据导入',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细日志')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 导入单个文件
    file_parser = subparsers.add_parser('import-file', help='导入单个文件')
    file_parser.add_argument('file', help='要导入的文件路径')
    file_parser.add_argument('-t', '--table', help='目标表名（可选）')
    file_parser.add_argument('-b', '--backup', action='store_true', help='导入前备份数据')
    file_parser.add_argument('--no-overwrite', action='store_true', help='不覆盖现有数据')
    file_parser.add_argument('--skip-errors', action='store_true', default=True, help='跳过错误记录')
    
    # 导入目录
    dir_parser = subparsers.add_parser('import-dir', help='导入目录中的所有文件')
    dir_parser.add_argument('directory', nargs='?', default='CSV', help='要导入的目录')
    dir_parser.add_argument('-b', '--backup', action='store_true', help='导入前备份数据')
    dir_parser.add_argument('--no-overwrite', action='store_true', help='不覆盖现有数据')
    dir_parser.add_argument('--skip-errors', action='store_true', default=True, help='跳过错误记录')
    
    # 导入NBA球队数据
    nba_parser = subparsers.add_parser('import-nba', help='导入NBA球队数据')
    nba_parser.add_argument('team', help='球队缩写（如 SAS, OKC）')
    nba_parser.add_argument('file', help='NBA球队Excel文件路径')
    nba_parser.add_argument('-b', '--backup', action='store_true', help='导入前备份数据')
    nba_parser.add_argument('--no-overwrite', action='store_true', help='不覆盖现有数据')
    nba_parser.add_argument('--skip-errors', action='store_true', default=True, help='跳过错误记录')
    
    # 列出表
    list_parser = subparsers.add_parser('list-tables', help='列出数据库中的表')
    
    # 显示球队缩写
    team_parser = subparsers.add_parser('list-teams', help='显示所有支持的球队缩写')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    setup_logging(args.verbose)
    
    try:
        if args.command == 'import-file':
            import_file(args)
        elif args.command == 'import-dir':
            import_directory(args)
        elif args.command == 'import-nba':
            import_nba_team(args)
        elif args.command == 'list-tables':
            list_tables(args)
        elif args.command == 'list-teams':
            show_team_abbrs(args)
    except Exception as e:
        logger.error(f"执行命令时发生错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
