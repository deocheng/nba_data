# NBA数据平台 - 操作说明

## 快速启动

### 方法1：使用Python命令（推荐）
```powershell
cd c:\autopick\AutoPick\nba_data
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

### 方法2：检查并启动
```powershell
# 1. 先清理端口
Get-NetTCPConnection -LocalPort 8000 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }

# 2. 启动服务器
cd c:\autopick\AutoPick\nba_data
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

## 访问地址

服务器启动后，访问：
- **首页**: http://localhost:8000/
- **马刺专区**: http://localhost:8000/spurs
- **球员生涯**: http://localhost:8000/player-career
- **球员详情**: http://localhost:8000/player-profile?id=wembanyama
  - 可以换成: wembanyama, chetholmgren, tim_duncan, kobe_bryant, lebron_james
- **传奇球员**: http://localhost:8000/legendary-players
- **球员对比**: http://localhost:8000/player-compare

## 测试API

在另一个终端中测试：
```powershell
# 测试Chet Holmgren
curl http://localhost:8000/api/player/chetholmgren/profile

# 测试Wembanyama
curl http://localhost:8000/api/player/wembanyama/profile

# 测试首页
curl http://localhost:8000/
```

## 停止服务器

```powershell
# 方法1：直接关闭
Get-NetTCPConnection -LocalPort 8000 | ForEach-Object { Stop-Process -Id $_.