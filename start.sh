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
    echo "⚠️ FFmpeg 未找到,嘗試安裝..."
    apt-get update && apt-get install -y ffmpeg || echo "❌ FFmpeg 安裝失敗"
    
    # 再次檢查
    if command -v ffmpeg &> /dev/null; then
        echo "✅ FFmpeg 安裝成功"
        ffmpeg -version | head -n 1
    else
        echo "❌ 錯誤: 無法安裝 FFmpeg!"
        echo "⚠️ 音訊下載將只能保存為 m4a 格式"
    fi
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
