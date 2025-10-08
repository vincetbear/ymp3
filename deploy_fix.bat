@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   修復 YouTube 機器人檢測錯誤
echo ========================================
echo.
echo 正在提交修復到 GitHub...
echo.

git add .
git commit -m "Fix: YouTube bot detection - Add extractor_args and user_agent"
git push

echo.
echo ========================================
echo   完成！
echo ========================================
echo.
echo 已推送更新到 GitHub
echo Railway 將在 2-3 分鐘內自動部署
echo.
echo 請前往 Railway Dashboard 查看部署進度：
echo https://railway.app
echo.
echo 部署完成後，重新測試下載功能即可
echo.
pause
