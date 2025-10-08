# 🌐 YouTube 下載工具 - Web 版本 (PWA)

一個基於 Flask 的 YouTube 下載工具，支援 PWA (Progressive Web App)，可安裝到手機桌面。

## ✨ 特色功能

- 📱 **PWA 支援** - 可安裝到手機/桌面
- 🎥 **影片下載** - 支援多種解析度 (4K/1080p/720p 等)
- 🎵 **音訊下載** - MP3 格式，多種音質選擇
- 📊 **即時進度** - 顯示下載進度、速度、剩餘時間
- 🌈 **響應式設計** - 完美支援手機、平板、電腦
- 🚀 **快速部署** - 一鍵部署到 Railway/Render/Fly.io

## 🖼️ 介面預覽

### 手機版
- 大按鈕設計，方便觸控操作
- 自動適應螢幕大小
- 支援深色模式

### 電腦版
- 清爽簡潔的卡片式設計
- 即時預覽影片資訊
- 流暢的動畫效果

## 🚀 快速開始

### 本地運行

1. **安裝相依套件**
```bash
pip install -r requirements.txt
```

2. **啟動應用程式**
```bash
python app.py
```

3. **開啟瀏覽器**
```
http://localhost:5000
```

### 手機測試（同一區網）

1. 查看電腦 IP：
```bash
ipconfig  # Windows
ifconfig  # macOS/Linux
```

2. 手機瀏覽器輸入：
```
http://[你的IP]:5000
```

## 📦 部署到雲端

### Railway（推薦）

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

**步驟：**
1. 點擊上方按鈕
2. 連接 GitHub
3. 選擇此 repository
4. 等待部署完成

### Render

1. 前往 [Render.com](https://render.com)
2. New → Web Service
3. 連接 GitHub Repository
4. 設定：
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

### Fly.io

```bash
fly launch
fly deploy
```

詳細部署指南請參考 [DEPLOYMENT.md](DEPLOYMENT.md)

## 📱 PWA 安裝

### iOS
1. Safari 開啟網站
2. 點擊「分享」按鈕
3. 選擇「加入主畫面」

### Android
1. Chrome 開啟網站
2. 選單 → 「安裝應用程式」
3. 點擊「安裝」

## 🛠️ 技術棧

- **後端**: Flask (Python)
- **前端**: HTML5 + CSS3 + JavaScript
- **下載引擎**: yt-dlp
- **部署**: Gunicorn
- **PWA**: Service Worker + Web App Manifest

## 📂 專案結構

```
web_version/
├── app.py                      # Flask 後端
├── requirements.txt            # Python 相依套件
├── Procfile                    # 部署設定
├── runtime.txt                 # Python 版本
├── Aptfile                     # 系統套件 (FFmpeg)
├── static/
│   ├── css/
│   │   └── style.css          # 響應式樣式
│   ├── js/
│   │   ├── app.js             # 前端邏輯
│   │   └── sw.js              # Service Worker
│   ├── icons/                 # PWA 圖示
│   └── manifest.json          # PWA 設定檔
├── templates/
│   └── index.html             # 主頁面
└── downloads/                 # 暫存下載檔案
```

## 🔧 API 端點

### POST /api/download
開始下載任務

**請求**:
```json
{
  "url": "https://youtube.com/watch?v=...",
  "type": "video",
  "quality": "1080p"
}
```

**回應**:
```json
{
  "task_id": "abc123",
  "message": "下載任務已開始"
}
```

### GET /api/progress/:task_id
查詢下載進度

**回應**:
```json
{
  "status": "downloading",
  "progress": "45%",
  "speed": "2.5 MiB/s",
  "eta": "00:30"
}
```

### GET /api/download/:task_id
下載檔案

### POST /api/info
取得影片資訊（不下載）

## ⚙️ 環境變數

```env
FLASK_ENV=production
PORT=5000
MAX_CONTENT_LENGTH=524288000  # 500MB
```

## 🔒 安全性

- CORS 保護
- 檔案大小限制
- 自動清理舊檔案（1小時）
- HTTPS 強制（生產環境）

## 📝 注意事項

1. **合法使用**: 請遵守 YouTube 服務條款
2. **個人用途**: 僅供個人學習與合法使用
3. **儲存空間**: 免費方案有儲存限制
4. **FFmpeg**: 音訊下載需要 FFmpeg（已在 Aptfile 設定）

## 🐛 疑難排解

### 下載失敗
- 檢查網址是否正確
- 確認網路連線
- 查看伺服器日誌

### 音訊轉換失敗
- 確認 FFmpeg 已安裝
- 檢查伺服器支援

### PWA 無法安裝
- 確認使用 HTTPS
- 檢查 manifest.json
- Service Worker 是否註冊成功

## 📊 效能優化

### 建議設定（生產環境）

1. **使用 CDN**
   - Cloudflare
   - 加速靜態資源

2. **Redis 快取**
   - 快取影片資訊
   - 減少 API 請求

3. **背景任務**
   - Celery 處理下載
   - 避免請求超時

## 🔄 更新日誌

### v1.0.0 (2025-10-08)
- ✨ 首次發布
- 🎨 響應式 PWA 設計
- 📱 支援手機安裝
- 🚀 一鍵雲端部署

## 📄 授權

僅供學習與個人合法使用。

## 🙏 致謝

- [Flask](https://flask.palletsprojects.com/) - Web 框架
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube 下載核心
- [Railway](https://railway.app) - 部署平台

## 📞 支援

遇到問題？請查看：
1. [部署指南](DEPLOYMENT.md)
2. [常見問題](DEPLOYMENT.md#常見問題)

---

**製作日期**: 2025年10月8日
**版本**: 1.0.0
