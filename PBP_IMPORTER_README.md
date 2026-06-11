# Play-by-Play 数据即时保存和导入系统

## 概述

这个系统提供了一个完整的解决方案，用于爬取 Basketball Reference 的 Play-by-Play 数据，并即时保存到 JSON 文件和 PostgreSQL 数据库中。

## 主要功能

1. **即时文件保存** - 爬取的 PBP 数据立即保存到 JSON 文件
2. **即时数据库导入** - 同时将数据导入到 PostgreSQL 数据库
3. **断点续爬** - 保存进度，支持从上次停止处继续
4. **定时休息** - 支持运行一段时间后自动休息，避免反爬虫

## 文件结构

```
nba_data/
├── data_importer/
│   ├── pbp_storage.py          # 核心存储管理模块
│   ├── database.py             # 数据库操作
│   ├── config.py               # 配置管理
│   └── ...
├── crawler_with_storage.py     # 带存储的爬虫
├── CSV/
│   └── 2026_season/
│       ├── all_games_2026.csv  # 比赛列表
│       └── pbp/                # PBP JSON 文件存储
└── ...
```

## 数据库表结构

### `game_metadata` - 比赛元数据
| 字段 | 类型 | 说明 |
|------|------|------|
| id | SERIAL | 主键 |
| game_id | VARCHAR(50) | 比赛唯一 ID |
| season_end | INTEGER | 赛季结束年份 |
| visitor_team | VARCHAR(50) | 客队 |
| home_team | VARCHAR(50) | 主队 |
| visitor_score | INTEGER | 客队得分 |
| home_score | INTEGER | 主队得分 |
| game_date | DATE | 比赛日期 |
| boxscore_url | TEXT | Boxscore URL |
| pbp_saved | BOOLEAN | PBP 是否已保存到文件 |
| pbp_imported | BOOLEAN | PBP 是否已导入数据库 |
| saved_at | TIMESTAMP | 保存时间 |
| imported_at | TIMESTAMP | 导入时间 |
| created_at | TIMESTAMP | 创建时间 |

### `play_by_play` - Play-by-Play 数据
| 字段 | 类型 | 说明 |
|------|------|------|
| id | SERIAL | 主键 |
| game_id | VARCHAR(50) | 比赛 ID (外键) |
| season_end | INTEGER | 赛季结束年份 |
| period | INTEGER | 节次 |
| game_clock | VARCHAR(20) | 比赛时间 |
| visitor_action | TEXT | 客队动作 |
| home_action | TEXT | 主队动作 |
| visitor_score | INTEGER | 客队得分 |
| home_score | INTEGER | 主队得分 |
| score_change | INTEGER | 得分变化 |
| row_num | INTEGER | 行号 |
| created_at | TIMESTAMP | 创建时间 |

## 快速开始

### 1. 导入已有的 PBP 数据
```python
from data_importer.pbp_storage import PBPDataStorage
import pandas as pd
import json

# 初始化存储
storage = PBPDataStorage(season_end=2026)

# 加载比赛列表
games_df = pd.read_csv('CSV/2026_season/all_games_2026.csv')

# 处理单场比赛
game_id = '202510210OKC'
game_row = games_df[games_df['boxscore_url'].str.contains(game_id)].iloc[0]
game_info = game_row.to_dict()

with open(f'CSV/2026_season/pbp/{game_id}_pbp.json') as f:
    pbp_data = json.load(f)

result = storage.process_single_game(game_info, pbp_data)
print(result)

storage.close()
```

### 2. 运行完整爬虫
```bash
cd nba_data
python crawler_with_storage.py
```

或者用参数：
```bash
python crawler_with_storage.py --max-games 10 --delay 30
```

## 命令行参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| --season | 2026 | 赛季结束年份 |
| --max-games | 5 | 最大爬取数量（测试用） |
| --delay | 40 | 请求间隔秒数 |
| --no-headless | False | 显示浏览器窗口 |
| --run-minutes | 30 | 单次运行分钟数 |
| --rest-minutes | 5 | 休息分钟数 |

## 检查进度

查看导入摘要：
```python
from data_importer.pbp_storage import PBPDataStorage

storage = PBPDataStorage()
summary = storage.get_import_summary()
print(summary)
# {'total_games': 3, 'pbp_saved': 3, 'pbp_imported': 3, 'pbp_records': 1566}
```

## 查询数据库

```python
from data_importer.database import DatabaseManager
from data_importer.config import DatabaseConfig

db = DatabaseManager(DatabaseConfig())

# 查询单场比赛的 PBP 数据
pbp_data = db.fetch_dict(
    "SELECT * FROM play_by_play WHERE game_id = %s ORDER BY row_num",
    ('202510210OKC',)
)

# 查询所有比赛
games = db.fetch_dict("SELECT * FROM game_metadata ORDER BY game_date")

db.close()
```

## 注意事项

1. **数据库配置** - 确保 PostgreSQL 服务运行，并配置好连接参数
2. **反爬策略** - 建议使用合理的请求间隔，避免触发反爬虫
3. **进度文件** - 不要删除 `full_progress.json` 和 `import_status.json`，否则会丢失进度
