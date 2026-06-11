@echo off
chcp 65001 >nul
title NBA数据平台

echo.
echo ========================================
echo    NBA数据平台 - 启动脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 检查端口8000占用情况...
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo 发现端口8000已被占用，正在关闭...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 >nul
)

echo [2/3] 启动FastAPI服务器...
echo.
start "NBA数据平台" cmd /c "python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 >nul

echo [3/3] 检查服务器状态...
curl -s http://localhost:8000 >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo    服务器启动成功！
    echo ========================================
    echo.
    echo 访问地址：
    echo   首页:      http://localhost:8000/
    echo   马刺专区:  http://localhost:8000/spurs
    echo   球员生涯:  http://localhost:8000/player-career
    echo   球员详情:  http://localhost:8000/player-profile?id=wembanyama
    echo   传奇球员:  http://localhost:8000/legendary-players
    echo.
    echo 按任意键打开浏览器...
    pause >nul
    start http://localhost:8000/
) else (
    echo.
    echo [错误] 服务器启动失败，请检查日志
    echo.
    pause
)
