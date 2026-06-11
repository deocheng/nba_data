# API管理文档

## 1. API命名规范

### 1.1 路径命名规则
- 使用小写字母和连字符(-)
- 使用复数形式表示资源集合
- 使用RESTful风格的路径结构

### 1.2 响应格式规范
- **成功响应**: 返回包含数据的对象，或直接返回数据
- **错误响应**: 使用HTTP状态码，返回明确的错误信息

### 1.3 字段命名规则
- 使用蛇形命名(snake_case)
- 统一百分比数据格式：使用小数(0.0-1.0)存储，前端显示时乘以100
- 场均数据前缀: avg_

## 2. 当前API列表

### 2.1 球队API - [活跃]

| 路径 | 方法 | 状态 | 说明 |
|------|------|------|------|
| `/api/teams` | GET | 活跃 | 获取所有球队列表 |
| `/api/teams/search` | GET | 活跃 | 搜索球队 |
| `/api/teams/{team_id}` | GET | 活跃 | 根据ID获取球队详情 |
| `/api/teams/{team_id}/games` | GET | 活跃 | 获取球队比赛数据 |
| `/api/teams/{team_id}/recent_games` | GET | 活跃 | 获取球队近期比赛 |
| `/api/teams/{team_id}/record` | GET | 活跃 | 获取球队战绩统计 |
| `/api/teams/{team_id}/games_chart` | GET | 活跃 | 获取球队比赛图表数据 |
| `/api/teams/{team_id}/roster` | GET | 活跃 | 获取球队阵容 |
| `/api/teams/{team_id}/transactions` | GET | 活跃 | 获取球队交易记录 |

### 2.2 赛季API - [活跃]

| 路径 | 方法 | 状态 | 说明 |
|------|------|------|------|
| `/api/seasons` | GET | 活跃 | 获取可用赛季列表 |

### 2.3 传奇球员API - [活跃]

| 路径 | 方法 | 状态 | 说明 |
|------|------|------|------|
| `/api/legendary_players` | GET | 活跃 | 获取传奇球员列表 |
| `/api/legendary_players/{player_id}` | GET | 活跃 | 获取球员详情 |
| `/api/legendary_players/{player_id}/stats` | GET | 活跃 | 获取球员生涯统计 |
| `/api/legendary_players/{player_id}/seasons` | GET | 活跃 | 获取球员赛季数据 |
| `/api/legendary_players/{player_id}/timeline` | GET | 活跃 | 获取球员时间线 |

### 2.4 球员对比API - [活跃]

| 路径 | 方法 | 状态 | 说明 |
|------|------|------|------|
| `/api/players/list` | GET | 活跃 | 获取球员列表 |
| `/api/players/compare` | GET | 活跃 | 对比两个球员 |
| `/api/players/{player_id}/seasons` | GET | 活跃 | 获取球员赛季列表 |

### 2.5 已废弃/不使用的API - [待清理]

| 路径 | 方法 | 状态 | 说明 |
|------|------|------|------|
| ~~`/api/players`~~ | GET | 废弃 | 旧版球员列表API(已删除) |
| ~~`/api/players/{player_name}`~~ | GET | 废弃 | 旧版球员生涯数据API(已删除) |
| ~~`/api/players/{player_name}/stats`~~ | GET | 废弃 | 旧版球员统计API(已删除) |

## 3. 待处理事项

- [ ] 项目完成后清理所有标记为[废弃]的API
- [ ] 统一所有API的响应格式
- [ ] 完善API文档(Swagger/OpenAPI)
- [ ] 添加API版本管理

## 4. 数据格式规范

### 4.1 百分比数据
- **存储格式**: 小数格式(0.0-1.0)，例如0.498表示49.8%
- **API返回格式**: 小数格式(0.0-1.0)
- **前端显示格式**: 乘以100后显示，保留1位小数，例如49.8%

### 4.2 常用字段映射

| 字段名 | 说明 | 示例 |
|--------|------|------|
| avg_points | 场均得分 | 30.1 |
| avg_rebounds | 场均篮板 | 6.2 |
| avg_assists | 场均助攻 | 5.3 |
| avg_steals | 场均抢断 | 2.3 |
| avg_blocks | 场均盖帽 | 0.8 |
| fg_pct | 投篮命中率 | 0.498 |
| three_p_pct | 三分命中率 | 0.327 |
| ft_pct | 罚球命中率 | 0.835 |

## 5. API测试记录

最后测试时间: 2026-05-13
- 传奇球员API: ✓ 正常
- 球员对比API: ✓ 正常
- 球队API: ✓ 正常
