@echo off
title 熊猫学习助手
cd /d "%~dp0"

echo.
echo  🐼 熊猫学习助手
echo  ═══════════════
echo.
echo  端口: 5000
echo.
echo  1) 桌面 App 模式（推荐 — 无边框窗口）
echo  2) 浏览器模式
echo.
set /p choice="输入 1 或 2，回车确认: "

if "%choice%"=="1" (
    .venv\Scripts\python.exe app.py
) else (
    start http://127.0.0.1:5000
    .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 5000
)
pause
