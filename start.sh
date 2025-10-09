#!/bin/bash
# Railway 啟動前檢查腳本

echo "=========================================="
echo "Railway 環境檢查"
echo "=========================================="

# 檢查 Python 版本
echo "Python 版本:"
python --version

# 檢查 FFmpeg
echo ""
echo "檢查 FFmpeg:"
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg 已安裝"
    ffmpeg -version | head -n 1
else
    echo "❌ 錯誤: 找不到 FFmpeg!"
    echo "請檢查 nixpacks.toml 中的 aptPkgs 配置"
    exit 1
fi

# 檢查必要的 Python 套件
echo ""
echo "檢查 Python 套件:"
python -c "import pytubefix; print(f'✅ pytubefix {pytubefix.__version__}')" || echo "❌ pytubefix 未安裝"
python -c "import flask; print(f'✅ Flask {flask.__version__}')" || echo "❌ Flask 未安裝"

echo ""
echo "=========================================="
echo "環境檢查完成"
echo "=========================================="
echo ""

# 啟動 Gunicorn
exec gunicorn app_pytubefix:app --bind 0.0.0.0:$PORT --workers 2 --timeout 300
