# NBA数据平台 - 服务器启动脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   NBA数据平台 - 启动服务器" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 切换到脚本目录
Set-Location $PSScriptRoot

# 检查端口8000
Write-Host "[1/3] 检查端口8000..." -ForegroundColor Yellow
$portCheck = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue

if ($portCheck) {
    Write-Host "发现端口8000被占用，正在关闭旧进程..." -ForegroundColor Red
    $portCheck.OwningProcess | ForEach-Object {
        Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
        Write-Host "  已关闭进程: $_" -ForegroundColor Gray
    }
    Start-Sleep -Seconds 2
}

# 启动服务器
Write-Host "[2/3] 启动FastAPI服务器..." -ForegroundColor Yellow
Write-Host ""

$serverJob = Start-Job -ScriptBlock {
    param($path)
    Set-Location $path
    python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
}

# 等待服务器启动
Write-Host "[3/3] 等待服务器启动..." -ForegroundColor Yellow
$maxWait = 10
$waited = 0

while ($waited -lt $maxWait) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000" -TimeoutSec 1 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host ""
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "   服务器启动成功！" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "访问地址：" -ForegroundColor Cyan
            Write-Host "  首页:      http://localhost:8000/" -ForegroundColor White
            Write-Host "  马刺专区:  http://localhost:8000/spurs" -ForegroundColor White
            Write-Host "  球员生涯:  http://localhost:8000/player-career" -ForegroundColor White
            Write-Host "  球员详情:  http://localhost:8000/player-profile?id=wembanyama" -ForegroundColor White
            Write-Host "  传奇球员:  http://localhost:8000/legendary-players" -ForegroundColor White
            Write-Host ""
            Write-Host "按任意键打开浏览器..." -ForegroundColor Yellow
            
            # 打开浏览器
            Start-Process "http://localhost:8000/"
            break
        }
    } catch {
        # 服务器还未启动，继续等待
    }
    
    $waited++
    Start-Sleep -Seconds 1
    Write-Host "." -NoNewline
}

if ($waited -ge $maxWait) {
    Write-Host ""
    Write-Host "[错误] 服务器启动超时，请检查日志" -ForegroundColor Red
}

# 保持脚本运行
Write-Host ""
Write-Host "服务器正在后台运行，按 Ctrl+C 停止" -ForegroundColor Yellow
Write-Host ""

# 等待服务器进程
try {
    while ($true) {
        Start-Sleep -Seconds 5
        # 检查服务器是否还在运行
        $check = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
        if (-not $check) {
            Write-Host ""
            Write-Host "[提示] 服务器已停止" -ForegroundColor Yellow
            break
        }
    }
} finally {
    # 清理
    if ($serverJob) {
        Stop-Job -Job $serverJob -ErrorAction SilentlyContinue
        Remove-Job -Job $serverJob -Force -ErrorAction SilentlyContinue
    }
}
