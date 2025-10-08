@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   YouTube 下載工具 - Web 版本啟動
echo ========================================
echo.

cd web_version

echo 正在啟動 Flask 伺服器...
echo.
echo 本地訪問: http://localhost:5000
echo 手機訪問: http://[你的IP]:5000
echo.
echo 按 Ctrl+C 停止伺服器
echo.

D:\01專案\2025\newyoutube\.venv\Scripts\python.exe app.py

pause
