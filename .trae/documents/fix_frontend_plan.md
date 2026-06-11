# 前端显示问题修复计划

## 问题分析

从服务器日志可以看到以下404错误：
- `GET /rockets HTTP/1.1` 404 Not Found
- `GET /legendary-players HTTP/1.1` 404 Not Found  
- `GET /rankings HTTP/1.1` 404 Not Found

**问题原因**：`app.py` 中只挂载了静态文件目录，但没有为各个HTML页面定义路由。需要添加路由来返回对应的HTML文件。

## 修复方案

### 1. 添加HTML页面路由
在 `app.py` 中添加以下路由：
- `/rockets` → 返回 `static/rockets.html`
- `/lakers` → 返回 `static/lakers.html`
- `/spurs` → 返回 `static/spurs.html`
- `/team-history` → 返回 `static/team_history.html`
- `/matchup` → 返回 `static/matchup.html`
- `/player-compare` → 返回 `static/player_compare.html`
- `/legendary-players` → 返回 `static/legendary_players.html`
- `/player-radar` → 返回 `static/player_radar.html`
- `/rankings` → 返回 `static/rankings.html`

### 2. 检查数据API调用
确保前端页面中的API调用路径正确，指向 `/api/` 开头的端点。

## 文件修改

### 修改文件：`app.py`
- 添加静态页面路由
- 使用 `FileResponse` 返回HTML文件

### 检查文件：各静态HTML文件
- 确保AJAX请求的API路径正确

## 实施步骤

1. 修改 `app.py` 添加页面路由
2. 重启服务器测试

## 风险评估

- 低风险：只是添加路由，不影响现有功能
- 需要确保静态文件路径正确