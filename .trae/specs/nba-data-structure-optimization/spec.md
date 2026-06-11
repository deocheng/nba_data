# NBA数据表结构优化规格

## 问题分析

### 当前状态

**马刺队 (SAS)**:
- 数据库表: `tbl_2023_2024spurs`, `tbl_2024_2025spurs`, `tbl_2025_2026spurs`
- 赛程数据: 只有最近3个赛季
- 问题: 缺少队史数据 (1989-2026LAL.csv 未导入)

**湖人队 (LAL)**:
- 数据库表: **无任何LAL相关表！**
- CSV文件: `1989-2026LAL.csv` (历史数据), `2025-2026LAL.xlsx` (已清空)
- 问题: 
  - 历史数据 `1989-2026LAL.csv` 未导入数据库
  - 2025-2026LAL.xlsx 数据被清空
  - API展示时回退到 `team_games` 表中的全部历史数据

**根本原因**:
1. **导入脚本不统一**: 马刺用 `tbl_*` 前缀，湖人没有导入
2. **表命名不规范**: 不同球队使用不同的表前缀
3. **数据结构不一致**: 有些是 per_team 表，有些是统一的 team_games 表
4. **队史数据遗漏**: 大量历史CSV文件未导入

### 目标

统一30支球队的数据表结构，确保：
1. 每支球队都有最近3个赛季的独立数据表
2. 所有历史比赛数据统一存储在 `team_games` 表
3. 所有球员数据统一存储在 `players` + `player_team_seasons` 表
4. API统一从数据库获取数据，无需fallback到JSON

## 表结构设计

### 核心事实表

```sql
-- 球队比赛记录 (统一存储所有比赛)
CREATE TABLE team_games (
    game_id SERIAL PRIMARY KEY,
    team_id VARCHAR(10) NOT NULL,        -- 球队缩写: SAS, LAL, HOU...
    season_id VARCHAR(10) NOT NULL,      -- 赛季: 2025-26, 2024-25...
    game_date DATE NOT NULL,
    opp_team VARCHAR(10),               -- 对手缩写
    is_home BOOLEAN DEFAULT FALSE,
    team_score INTEGER,
    opp_score INTEGER,
    result VARCHAR(1),                    -- W/L
    game_type VARCHAR(20),               -- regular/playoffs
    created_at TIMESTAMP DEFAULT NOW()
);

-- 球员-球队-赛季汇总 (统一存储所有球员统计)
CREATE TABLE player_team_seasons (
    id SERIAL PRIMARY KEY,
    player_id VARCHAR(50) NOT NULL,
    team_id VARCHAR(10) NOT NULL,
    season_id VARCHAR(10) NOT NULL,
    games_played INTEGER,
    minutes_played FLOAT,
    avg_points FLOAT,
    avg_rebounds FLOAT,
    avg_assists FLOAT,
    avg_steals FLOAT,
    avg_blocks FLOAT,
    per FLOAT,
    ws FLOAT,
    bpm FLOAT,
    vorp FLOAT,
    UNIQUE(player_id, team_id, season_id)
);

-- 球员基础信息
CREATE TABLE players (
    player_id VARCHAR(50) PRIMARY KEY,
    player_name VARCHAR(100) NOT NULL,
    position VARCHAR(10),
    jersey_number VARCHAR(5),
    height VARCHAR(20),
    weight INTEGER,
    college VARCHAR(100),
    draft_year INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 球队信息
CREATE TABLE teams (
    team_id VARCHAR(10) PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    team_abbr VARCHAR(10) NOT NULL,
    city VARCHAR(50),
    conference VARCHAR(20),
    division VARCHAR(30),
    arena VARCHAR(100),
    founded_year INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 近期赛季详细表 (可选，用于高阶分析)

对于最近3个赛季，保留详细数据表:

```sql
-- 马刺队 2025-26 赛季详细表
CREATE TABLE 2025_26_sas_per_game (...);
CREATE TABLE 2025_26_sas_advanced (...);
-- 等等
```

**命名规范**:
- `{season}_{team_abbr}_{data_type}` 
- 例如: `2025_26_sas_per_game`, `2025_26_lal_advanced`

## 导入流程

### 步骤1: 导入历史比赛数据 → team_games

对于 `1989-2026LAL.csv` 和 `1989-2026SAS.csv`:
1. 解析CSV
2. 插入到 `team_games` 表
3. 标记 `game_type` (regular/playoffs)

### 步骤2: 导入近期赛季详细数据

对于每个球队最近3个赛季的Excel:
1. 导入到 `{season}_{team_abbr}_{type}` 表
2. 导入球员到 `players` 表
3. 导入统计到 `player_team_seasons` 表

### 步骤3: 清理旧数据

- 删除不一致的表前缀 (如 `tbl_*`)
- 删除重复的表
- 删除无用的JSON fallback

## 影响范围

### 受影响的文件

- `app.py` - API接口
- `import_xlsx_teams.py` - 导入脚本
- `CSV/` 目录下所有数据文件
- `PROJECT_SPEC.md` - 项目规范

### API变更

- `/api/teams/{team_id}/games` 
  - 从 `team_games` 表获取所有历史数据
  - 从 `{season}_{team_abbr}_*` 表获取详细统计
  - 按 season 参数过滤

- `/api/teams/{team_id}/roster`
  - 从 `players` + `player_team_seasons` 获取
  - 无需fallback

## 实施计划

1. 导出并记录当前数据库状态
2. 设计统一的表结构
3. 创建数据迁移脚本
4. 重新导入所有数据
5. 更新API代码
6. 验证数据完整性
7. 更新项目文档

## 成功标准

1. ✅ 所有30支球队都有统一的数据表结构
2. ✅ 赛程展示按时间倒序，最近3个赛季可切换
3. ✅ API无任何JSON fallback
4. ✅ 队史数据完整展示
5. ✅ 项目文档明确数据规范
