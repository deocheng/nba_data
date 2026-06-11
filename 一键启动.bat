@echo off
chcp 65001 >nul
title NBA Data Platform

cd /d "%~dp0"

echo.
echo ========================================
echo    NBA Data Platform - Quick Start
echo ========================================
echo.

echo Starting server...
echo.

start "NBA Server" cmd /k "python -m uvicorn app:app --host 0.0.0.0 --port 8000"

timeout /t 3 >nul

echo.
echo Server should be running!
echo.
echo Access: http://localhost:8000/
echo.
echo Press any key to open browser...
pause >nul

start http://localhost:8000/

echo.
echo Done! Server is running in a new window.
echo Press Ctrl+C in that window to stop.
echo.
pause
