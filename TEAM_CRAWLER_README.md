# NBA球队数据爬虫使用说明

## 概述

这是一个严格遵守反爬规则的NBA球队数据爬虫，用于从Basketball Reference缓慢谨慎地爬取所有球队最近4年的比赛数据。

## 功能特性

### 1. 反爬机制
- **User-Agent轮换**：预定义8个常用浏览器UA，随机选择
- **请求延迟**：每次请求前随机等待3-5秒
- **速率限制处理**：遇到429状态码时自动延长等待10-15秒
- **指数退避重试**：失败后等待时间指数增长（2^attempt秒）
- **详细日志记录**：记录所有请求、响应、错误信息

### 2. 断点续传
- 自动记录爬取进度到 `crawler_progress.json`
- 支持从上次中断位置继续爬取
- 避免重复爬取已完成的数据

### 3. 数据存储
- 自动存储到SQLite数据库
- 支持数据验证
- 避免重复插入

## 目录结构

```
nba_data/
├── crawler/
│   ├── base_scraper.py          # 爬虫基类（反爬机制）
│   └── team_data_crawler.py     # 球队数据爬虫
├── storage/
│   └── team_data_storage.py     # 数据存储模块
├── crawler_data/                 # 爬取的CSV数据
│   └── team_data/
├── crawler_progress.json         # 爬取进度记录
├── crawl_team_data.py            # 主程序
└── nba_data.db                   # 数据库
```

## 使用方法

### 1. 基本使用

```bash
cd c:\autopick\AutoPick\nba_data
python crawl_team_data.py
```

### 2. 功能选项

运行后会显示菜单：

```
1. 爬取所有球队最近4年数据（推荐：缓慢谨慎）
2. 爬取单个球队所有赛季数据
3. 爬取单个赛季所有球队数据
4. 显示数据库统计信息
5. 测试爬虫（爬取1个球队1个赛季）
q. 退出
```

### 3. 推荐流程

**首次使用：**
```bash
python crawl_team_data.py
# 选择选项 1
# 开始爬取所有球队最近4年数据
```

**继续爬取（中断后）：**
```bash
python crawl_team_data.py
# 选择选项 1
# 程序会自动跳过已完成的数据
```

**查看进度：**
```bash
python crawl_team_data.py
# 选择选项 4
# 显示数据库统计信息
```

## 爬取顺序

### 第一阶段：最近4年数据（优先）
1. 2025-26 赛季
2. 2024-25 赛季
3. 2023-24 赛季
4. 2022-23 赛季

### 第二阶段：历史数据（4年后）
完成第一阶段后，可以修改代码中的 `SEASONS` 列表来爬取更早的数据。

## 数据库结构

### 表：team_games_crawler

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| team_abbr | TEXT | 球队缩写 |
| season | TEXT | 赛季 |
| game_date | TEXT | 比赛日期 |
| opponent | TEXT | 对手 |
| result | TEXT | 胜负（W/L） |
| team_score | INTEGER | 球队得分 |
| opponent_score | INTEGER | 对手得分 |
| ... | ... | 更多统计字段 |

## 示例查询

```sql
-- 查询勇士队最近的比赛
SELECT * FROM team_games_crawler 
WHERE team_abbr = 'GSW' 
ORDER BY game_date DESC 
LIMIT 10;

-- 查询某赛季所有球队战绩
SELECT team_abbr, 
       SUM(CASE WHEN result = 'W' THEN 1 ELSE 0 END) as wins,
       SUM(CASE WHEN result = 'L' THEN 1 ELSE 0 END) as losses
FROM team_games_crawler 
WHERE season = '2025-26' 
GROUP BY team_abbr;

-- 查询数据库统计
SELECT season, COUNT(*) as game_count 
FROM team_games_crawler 
GROUP BY season;
```

## 注意事项

1. **耐心等待**：由于反爬机制，爬取30支球队x4个赛季可能需要数小时
2. **避免中断**：建议使用断点续传功能，中断后可继续
3. **日志查看**：爬取过程中可查看 `team_crawler.log` 了解详情
4. **数据验证**：爬取完成后可使用选项4验证数据完整性

## 常见问题

### Q1: 程序运行很慢，正常吗？
A: 正常。为了避免被封禁，程序设置了3-5秒的随机延迟，这是故意的设计。

### Q2: 爬取中断了怎么办？
A: 不用担心，程序会自动保存进度。重新运行程序选择选项1，会从上次中断的位置继续。

### Q3: 如何查看爬取进度？
A: 
- 查看 `crawler_progress.json` 文件
- 或运行程序选择选项4查看统计信息

### Q4: 如何爬取更早的数据？
A: 修改 `crawl_team_data.py` 中的 `self.seasons` 列表，添加更早的赛季。

### Q5: 数据库在哪里？
A: 默认数据库文件为 `nba_data.db`，与爬虫程序在同一目录。

## API使用

### Python代码中使用

```python
from crawl_team_data import TeamDataCrawlerManager

manager = TeamDataCrawlerManager()

# 爬取所有数据
manager.crawl_all_recent_data()

# 显示统计
manager.show_statistics()

# 查询数据
from storage.team_data_storage import TeamDataStorage
storage = TeamDataStorage()
count = storage.get_statistics(team_abbr='GSW', season='2025-26')
print(f"GSW 2025-26赛季数据: {count} 条")
```

## 更新日志

### v1.0 (2026-06-03)
- 初始版本
- 支持最近4年数据爬取
- 支持断点续传
- 严格反爬机制