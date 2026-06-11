# NBA数据平台 - 前端API与数据库表结构对应文档

**文档版本**: v1.0
**创建日期**: 2026-05-16
**状态**: 正式版

---

## 一、项目规范（重要）

### 1.1 核心原则
- **所有前端展示的数据必须通过API从数据库获取**
- **禁止直接读取JSON文件作为数据源**
- **CSV文件仅作为原始数据导入源**

### 1.2 赛季格式规范
| 用途 | 格式 | 示例 |
|------|------|------|
| URL参数 | `2025-26` (单年份格式) | `?season=2025-26` |
| 数据库存储 | `2025-2026` (完整赛季格式) | `season_id = '2025-2026'` |

**转换函数** (`app.py` 第208-215行):
```python
def normalize_season(season: str) -> str:
    if not season:
        return season
    parts = season.split('-')
    if len(parts) == 2 and len(parts[0]) == 4 and len(parts[1]) == 2:
        return f"{parts[0]}-20{parts[1]}"
    return season
```

### 1.3 球队ID规范
| 字段 | 说明 | 示例 |
|------|------|------|
| `teams.team_id` | 数字ID或缩写 | `LAL`, `SAS` |
| `teams.team_abbr` | 球队缩写 | `LAL`, `SAS` |
| `team_games.team_id` | 使用 `team_abbr` | `LAL`, `SAS` |

---

## 二、数据库表结构

### 2.1 teams - 球队信息表

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| team_id | VARCHAR | 主键，使用缩写 | `LAL` |
| team_name | VARCHAR | 球队中文名 | `洛杉矶湖人` |
| team_name_en | VARCHAR | 球队英文名 | `Los Angeles Lakers` |
| team_abbr | VARCHAR | 球队缩写 | `LAL` |
| conference | VARCHAR | 赛区 | `Western` |
| conference_cn | VARCHAR | 赛区中文 | `西部` |
| division | VARCHAR | 分区 | `Pacific` |
| division_cn | VARCHAR | 分区中文 | `太平洋赛区` |
| city | VARCHAR | 城市 | `Los Angeles` |
| arena | VARCHAR | 球馆 | `Crypto.com Arena` |
| founded_year | INTEGER | 成立年份 | `1947` |

### 2.2 players - 球员基础信息表

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| player_id | VARCHAR | 主键 | `lebron_james` |
| player_name | VARCHAR | 球员中文名 | `勒布朗·詹姆斯` |
| player_name_en | VARCHAR | 球员英文名 | `LeBron James` |
| position | VARCHAR | 位置 | `F` |
| position_cn | VARCHAR | 位置中文 | `前锋` |
| height | VARCHAR | 身高 | `2.06m` |
| weight | VARCHAR | 体重 | `113kg` |
| jersey_number | VARCHAR | 球衣号码 | `23` |
| birth_date | DATE | 出生日期 | `1984-12-30` |
| birth_place | VARCHAR | 出生地 | `Akron, Ohio` |
| draft_year | INTEGER | 选秀年份 | `2003` |
| draft_pick | VARCHAR | 选秀顺位 | `首轮第1顺位` |
| retire_year | INTEGER | 退役年份 | `NULL` (未退役) |

### 2.3 seasons - 赛季维度表

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| season_id | VARCHAR | 主键 | `2025-26` |
| season_type | VARCHAR | 赛季类型 | `regular` |
| season_type_cn | VARCHAR | 赛季类型中文 | `常规赛` |
| start_date | DATE | 开始日期 | `2025-10-22` |
| end_date | DATE | 结束日期 | `2026-04-15` |
| is_current | BOOLEAN | 是否当前赛季 | `TRUE` |

### 2.4 team_games - 球队比赛数据表（核心）

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| id | SERIAL | 主键 | `1` |
| game_id | VARCHAR | 比赛ID | `0022500001` |
| team_id | VARCHAR | 球队缩写 | `LAL` |
| season_id | VARCHAR | 赛季ID | `2025-2026` |
| game_date | DATE | 比赛日期 | `2025-10-22` |
| game_number | INTEGER | 场次号 | `1` |
| is_home | BOOLEAN | 是否主场 | `TRUE` |
| opp_team_id | VARCHAR | 对手ID | `OKC` |
| opp_team_abbr | VARCHAR | 对手缩写 | `OKC` |
| opp_team_name | VARCHAR | 对手名称 | `Oklahoma City Thunder` |
| result | VARCHAR | 比赛结果 | `W` / `L` |
| team_score | INTEGER | 球队得分 | `110` |
| opp_score | INTEGER | 对手得分 | `98` |
| ot_flag | VARCHAR | 加时标志 | `OT` / `NULL` |
| **game_type** | VARCHAR | **比赛类型** | **`regular` / `playin` / `playoff`** |
| is_playoff | BOOLEAN | 是否季后赛 | `TRUE` / `FALSE` |
| created_at | TIMESTAMP | 创建时间 | `2026-05-16` |

**game_type 字段说明**:
| 值 | 说明 | 颜色 |
|-----|------|------|
| `regular` | 常规赛 | 蓝色(胜)/红色(负) |
| `playin` | 附加赛 | 金色(胜)/灰色(负) |
| `playoff` | 季后赛 | 金色(胜)/灰色(负) |

### 2.5 player_game_logs - 球员比赛日志表

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| id | SERIAL | 主键 | `1` |
| player_id | VARCHAR | 球员ID | `lebron_james` |
| team_id | VARCHAR | 球队缩写 | `LAL` |
| game_id | VARCHAR | 比赛ID | `0022500001` |
| season_id | VARCHAR | 赛季ID | `2025-2026` |
| game_date | DATE | 比赛日期 | `2025-10-22` |
| game_number | INTEGER | 场次号 | `1` |
| is_home | BOOLEAN | 是否主场 | `TRUE` |
| opp_team_id | VARCHAR | 对手ID | `OKC` |
| opp_team_abbr | VARCHAR | 对手缩写 | `OKC` |
| result | VARCHAR | 比赛结果 | `W` / `L` |
| minutes_played | FLOAT | 上场时间 | `32.5` |
| points | INTEGER | 得分 | `25` |
| rebounds | INTEGER | 篮板 | `8` |
| assists | INTEGER | 助攻 | `10` |
| steals | INTEGER | 抢断 | `2` |
| blocks | INTEGER | 盖帽 | `1` |
| fg_made | INTEGER | 投篮命中 | `10` |
| fg_att | INTEGER | 投篮出手 | `18` |
| three_made | INTEGER | 三分命中 | `3` |
| three_att | INTEGER | 三分出手 | `6` |
| ft_made | INTEGER | 罚球命中 | `2` |
| ft_att | INTEGER | 罚球出手 | `3` |
| plus_minus | INTEGER | 正负值 | `+15` |
| created_at | TIMESTAMP | 创建时间 | `2026-05-16` |

### 2.6 player_team_seasons - 球员-球队-赛季汇总表（核心）

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| id | SERIAL | 主键 | `1` |
| player_id | VARCHAR | 球员ID | `lebron_james` |
| team_id | VARCHAR | 球队缩写 | `LAL` |
| season_id | VARCHAR | 赛季ID | `2025-2026` |
| games_played | INTEGER | 出场次数 | `70` |
| minutes_played | FLOAT | 总上场时间 | `2100.5` |
| points | INTEGER | 总得分 | `1750` |
| rebounds | INTEGER | 总篮板 | `560` |
| assists | INTEGER | 总助攻 | `630` |
| steals | INTEGER | 总抢断 | `105` |
| blocks | INTEGER | 总盖帽 | `70` |
| fg_made | INTEGER | 投篮命中 | `650` |
| fg_att | INTEGER | 投篮出手 | `1200` |
| three_made | INTEGER | 三分命中 | `180` |
| three_att | INTEGER | 三分出手 | `500` |
| ft_made | INTEGER | 罚球命中 | `270` |
| ft_att | INTEGER | 罚球出手 | `320` |
| **avg_points** | FLOAT | **场均得分** | **25.0** |
| **avg_rebounds** | FLOAT | **场均篮板** | **8.0** |
| **avg_assists** | FLOAT | **场均助攻** | **9.0** |
| avg_steals | FLOAT | 场均抢断 | `1.5` |
| avg_blocks | FLOAT | 场均盖帽 | `1.0` |
| fg_pct | FLOAT | 投篮命中率 | `0.542` |
| three_pct | FLOAT | 三分命中率 | `0.360` |
| ft_pct | FLOAT | 罚球命中率 | `0.844` |
| per | FLOAT | 效率值 | `26.5` |
| ts_pct | FLOAT | 真实命中率 | `0.580` |
| usg_pct | FLOAT | 使用率 | `0.300` |
| ws | FLOAT | 胜利贡献值 | `12.5` |
| ws_per_48 | FLOAT | 每48分钟WS | `0.285` |
| bpm | FLOAT | _box plus/minus | `6.2` |
| vorp | FLOAT | 替代值 | `4.8` |
| offensive_rating | FLOAT | 进攻效率 | `118.5` |
| defensive_rating | FLOAT | 防守效率 | `108.2` |
| created_at | TIMESTAMP | 创建时间 | `2026-05-16` |

**唯一约束**: `(player_id, team_id, season_id)`

---

## 三、API与数据库对应关系

### 3.1 球队API - `/api/teams`

#### GET `/api/teams`
- **功能**: 获取所有球队列表
- **数据源**: `teams` 表
- **返回字段**: team_id, team_name, team_abbr, city, conference, division, arena, founded_year

#### GET `/api/teams/search`
- **功能**: 搜索球队
- **数据源**: `teams` 表
- **查询条件**: team_name, team_abbr, city (模糊匹配)

#### GET `/api/teams/{team_id}`
- **功能**: 根据ID获取球队详情
- **数据源**: `teams` 表
- **查询条件**: team_id 或 team_abbr

#### GET `/api/teams/{team_id}/games`
- **功能**: 获取球队比赛数据
- **数据源**: `team_games` 表
- **查询条件**: team_id (team_abbr), season_id
- **返回字段**:
  - game_date, team_score, opp_score, opp_team_abbr
  - result (W/L), is_home, game_type, season_id
- **赛季格式**: 需要调用 `normalize_season()` 转换

#### GET `/api/teams/{team_id}/recent_games`
- **功能**: 获取球队近期比赛（近10场）
- **数据源**: `team_games` 表
- **参数**: count (默认10)

#### GET `/api/teams/{team_id}/record`
- **功能**: 获取球队赛季战绩统计
- **数据源**: `team_games` 表
- **返回**: wins, losses, win_rate, home_record, away_record

#### GET `/api/teams/{team_id}/games_chart`
- **功能**: 获取球队比赛图表数据
- **数据源**: `team_games` 表
- **返回**: labels[], team_scores[], opp_scores[], colors[], details[]
- **颜色规则**:
  ```javascript
  colors: game.is_win ? '#3B82F6' : '#EF4444'  // 蓝色胜/红色负
  ```

#### GET `/api/teams/{team_id}/roster`
- **功能**: 获取球队花名册
- **数据源**: `players` + `player_team_seasons` 表
- **查询条件**: team_id (player_id LIKE `{team_abbr.lower()}%`)
- **返回字段**: player_id, player_name, position, jersey_number, avg_points, avg_rebounds, avg_assists

#### GET `/api/teams/{team_id}/transactions`
- **功能**: 获取球队交易记录
- **数据源**: `transactions` 表（暂无）

### 3.2 赛季API - `/api/seasons`

#### GET `/api/seasons`
- **功能**: 获取可用赛季列表
- **数据源**: `team_games` 表
- **返回**: DISTINCT season_id ORDER BY DESC

### 3.3 球队历史API - `/api/teams/{team_id}/history`

#### GET `/api/teams/{team_id}/history`
- **功能**: 获取球队历史战绩数据
- **数据源**: `historical_games` 表（备用: CSV文件）
- **返回字段**: seasons[], total_seasons, all_time_wins, all_time_losses

#### GET `/api/teams/{team_id}/season/{season_id}`
- **功能**: 获取球队特定赛季详情
- **数据源**: `historical_games` 表（备用: CSV文件）
- **返回字段**: games[], total_games, wins, losses, win_rate, avg_points

#### GET `/api/teams/{team_id}/season_chart/{season_id}`
- **功能**: 获取球队特定赛季的图表数据（**重要**）
- **数据源**: `team_games` 表
- **返回字段**:
  ```python
  {
      "game_date": "2025-10-22",
      "team_score": 110,
      "opp_score": 98,
      "opp_team": "OKC",
      "is_win": True,
      "game_type": "regular",  # regular/playin/playoff
      "is_special": False,     # game_type in ['playin', 'playoff']
      "display_score": 110,    # 胜为正分，负为负分
      "month": 10
  }
  ```
- **赛季格式**: 支持 `2025-26` 和 `2025-2026`

### 3.4 传奇球员API - `/api/legendary_players`

#### GET `/api/legendary_players`
- **功能**: 获取传奇球员列表
- **数据源**: `players` + `player_team_seasons` 表

#### GET `/api/legendary_players/{player_id}`
- **功能**: 获取球员详情
- **数据源**: `players` 表

#### GET `/api/legendary_players/{player_id}/stats`
- **功能**: 获取球员生涯统计
- **数据源**: `player_team_seasons` 表
- **汇总字段**: SUM(points), AVG(avg_points), 等

#### GET `/api/legendary_players/{player_id}/seasons`
- **功能**: 获取球员赛季数据
- **数据源**: `player_team_seasons` 表

#### GET `/api/legendary_players/{player_id}/timeline`
- **功能**: 获取球员时间线
- **数据源**: `player_team_seasons` + `player_game_logs` 表

### 3.5 球员对比API - `/api/players`

#### GET `/api/players/list`
- **功能**: 获取球员列表
- **数据源**: `players` 表

#### GET `/api/players/compare`
- **功能**: 对比两个球员
- **数据源**: `player_team_seasons` 表
- **参数**: player1_id, player2_id, season_id

### 3.6 其他API

| API路径 | 功能 | 数据源表 |
|---------|------|---------|
| `/api/advanced_stats` | 高阶数据 | player_team_seasons |
| `/api/matchup` | 对阵数据 | team_games |
| `/api/player_radar` | 雷达图数据 | player_team_seasons |
| `/api/rankings` | 排行榜数据 | player_team_seasons |
| `/api/spurs` | 马刺队专属数据 | spurs_2025_2026_roster, tbl_202X_XXXspurs |

---

## 四、比赛类型判断逻辑

### 4.1 game_type 字段使用（推荐）

```python
# 判断是否是特殊比赛（附加赛或季后赛）
is_special = game_type in ['playin', 'playoff']
```

### 4.2 柱状图颜色规则（team_history.html / season-chart-test.html）

```javascript
const barColors = games.map(g => {
    if (g.is_special) {
        // 附加赛或季后赛：金色(胜) / 灰色(负)
        return g.is_win ? '#FFD700' : '#4B5563';
    }
    // 常规赛：蓝色(胜) / 红色(负)
    return g.is_win ? '#3B82F6' : '#EF4444';
});
```

### 4.3 颜色对应表

| 比赛类型 | 胜负 | 颜色代码 | 颜色名称 |
|---------|------|---------|---------|
| regular | 胜 | #3B82F6 | 蓝色 |
| regular | 负 | #EF4444 | 红色 |
| playin | 胜 | #FFD700 | 金色 |
| playin | 负 | #4B5563 | 灰色 |
| playoff | 胜 | #FFD700 | 金色 |
| playoff | 负 | #4B5563 | 灰色 |

---

## 五、常见问题与解决方案

### 5.1 赛季格式不匹配

**问题**: API传入 `2025-26`，但数据库存储 `2025-2026`

**解决方案**: 在API入口处调用 `normalize_season()` 函数

```python
@app.get("/api/teams/{team_id}/games")
def get_team_games(team_id: str, season: str = "2025-26"):
    season_id = normalize_season(season)  # 转换为 2025-2026
    # ... 查询数据库
```

### 5.2 team_id 查询问题

**问题**: 前端传入 `LAL`，但数据库 `team_games.team_id` 可能存储不同格式

**解决方案**: 在查询时同时匹配 team_id 和 team_abbr

```python
cursor.execute("""
    SELECT team_id, team_name, team_abbr
    FROM teams
    WHERE team_id = %s OR team_abbr = %s
""", (team_id, team_id))
```

### 5.3 game_type 字段为空

**问题**: 部分历史数据可能没有设置 game_type

**解决方案**: 默认设为 `regular`

```python
game_type = game_dict.get('game_type') or 'regular'
```

### 5.4 is_playoff 与 game_type 混用

**问题**: 之前代码中同时使用 is_playoff 和 game_type，导致逻辑混乱

**解决方案**: 统一使用 game_type 字段

```python
# 错误示例（已废弃）
if game_date.month >= 4 and game_date.month <= 6:
    is_playoff = True

# 正确示例
is_special = game_type in ['playin', 'playoff']
```

---

## 六、数据流向图

```
┌─────────────────────────────────────────────────────────────┐
│                        前端页面                              │
│  (team_history.html, season-chart-test.html, etc.)         │
└────────────────────────┬────────────────────────────────────┘
                         │ AJAX/Fetch
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI 路由                            │
│  /api/teams/{team_id}/season_chart/{season_id}            │
└────────────────────────┬────────────────────────────────────┘
                         │ 调用
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   API模块 (api/team_history.py)             │
│  - normalize_season()  # 赛季格式转换                        │
│  - get_team_season_chart()  # 查询team_games表              │
└────────────────────────┬────────────────────────────────────┘
                         │ SQL查询
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   PostgreSQL 数据库                         │
│  - team_games (game_type, team_score, opp_score, etc.)    │
│  - players, teams, player_team_seasons                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 七、文档维护

| 版本 | 日期 | 修改内容 | 作者 |
|------|------|---------|------|
| v1.0 | 2026-05-16 | 初始版本，完整梳理API和数据库对应关系 | Grok |

**下次更新计划**:
- [ ] 添加更多API端点的详细说明
- [ ] 补充错误处理示例
- [ ] 添加性能优化建议
