@echo off
cd /d "%~dp0"
echo.
echo  🐼 AI 学习助手
echo  ═══════════════
echo.
echo  请选择启动方式：
echo  1) 桌面 App 模式（推荐 — 打开 Chrome 无边框窗口）
echo  2) 浏览器模式（在浏览器中打开）
echo.
set /p choice="输入 1 或 2，回车确认: "

if "%choice%"=="1" (
    echo.
    echo  正在启动桌面 App...
    echo  如果是首次使用，请先配置 API Key
    echo  启动后请稍候几秒...
    .venv\Scripts\python.exe app.py
) else (
    echo.
    echo  正在启动服务器...
    echo  打开浏览器访问: http://127.0.0.1:8085
    start http://127.0.0.1:8085
    .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8085 --reload
)

pause
