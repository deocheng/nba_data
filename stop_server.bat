@echo off
chcp 65001 >nul
title NBA数据平台 - 停止服务器

echo.
echo ========================================
echo    NBA数据平台 - 停止服务器
echo ========================================
echo.

echo 正在查找并关闭NBA数据平台服务器...

netstat -ano | findstr ":8000" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo 发现服务器进程，正在关闭...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
        echo 关闭进程 PID: %%a
        taskkill /F /PID %%a >nul 2>&1
    )
    echo.
    echo 服务器已成功关闭
) else (
    echo 未发现运行中的服务器
)

echo.
pause
