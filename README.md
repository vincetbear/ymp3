# YouTube 下載工具

一個功能完整的 YouTube 影片/音訊下載工具，支援 Web 版部署，具備自動 MP3 轉檔功能。

---

## 📋 目錄

- [功能特色](#功能特色)
- [系統架構](#系統架構)
- [技術規格](#技術規格)
- [安裝與部署](#安裝與部署)
- [使用說明](#使用說明)
- [環境變數設定](#環境變數設定)
- [疑難排解](#疑難排解)

---

## ✨ 功能特色

### Web 版 (Railway 部署)

- ✅ **影片下載**: 多種畫質選擇 (最佳/1080p/720p/480p/360p)
- ✅ **音訊下載**: 自動轉換為 MP3 格式，支援多種位元率 (96-320 kbps)
- ✅ **即時預覽**: 輸入網址後自動顯示影片縮圖和資訊
- ✅ **進度追蹤**: 即時下載進度顯示
- ✅ **自動清空**: 下載完成後自動清空輸入框，方便連續使用
- ✅ **PWA 支援**: 可安裝為手機應用程式
- ✅ **跨平台**: 支援桌面、平板、手機
- ✅ **雲端部署**: Railway 自動部署和擴展
- ✅ **單一 Worker**: 避免記憶體不同步問題

---

## 🏗️ 系統架構

### Web 版架構

```txt
Flask 應用程式
├── 前端 (HTML/CSS/JavaScript)
│   ├── 影片資訊預覽
│   ├── 即時進度顯示
│   └── 自動清空輸入框
├── 後端 (Flask API)
│   ├── /api/info (獲取影片資訊)
│   ├── /api/download (下載任務)
│   ├── /api/progress/<task_id> (進度查詢)
│   └── /api/file/<task_id> (檔案下載)
└── 下載引擎
    ├── pytubefix (YouTube 下載)
    └── FFmpeg (MP3 轉檔)
```

**核心技術**:
- **Flask 3.1.0**: Web 框架
- **pytubefix**: YouTube 下載核心（持續更新中）
- **FFmpeg**: MP3 轉檔
- **Gunicorn 23.0.0**: WSGI 伺服器（單一 Worker 模式）
- **Railway**: 雲端部署平台

---

## 🔧 技術規格

### 支援的影片格式

#### 下載來源
- YouTube 影片
- YouTube 音訊串流

#### 輸出格式
- **影片**: MP4, WebM (取決於 YouTube 提供的格式)
- **音訊**: MP3 (自動轉檔)

### 品質選項

#### 影片品質
- **最佳畫質**: YouTube 提供的最高品質
- **1080p**: Full HD
- **720p**: HD
- **480p**: SD
- **360p**: 低畫質

#### 音訊品質
- **桌面版**: 128 kbps / 192 kbps / 320 kbps
- **Web 版**: 192 kbps (預設)

### MP3 轉檔

使用 FFmpeg 後處理器:
```python
'postprocessors': [{
    'key': 'FFmpegExtractAudio',
    'preferredcodec': 'mp3',
    'preferredquality': '192',
}]
```

**轉檔流程**:
1. 下載最佳音訊流
2. 使用 FFmpeg 轉換為 MP3
3. 自動刪除原始檔案
4. 保留 MP3 輸出

**效能**:
- 轉檔時間: 約 5-10 秒 (4 分鐘影片)
- 檔案大小: 約原始檔案的 50%

### 單一 Worker 架構

**為什麼使用單一 Worker?**

使用 Gunicorn 單一 Worker 模式可以確保:
- ✅ 所有請求訪問同一個記憶體空間
- ✅ `download_tasks` 字典在所有 API 端點間同步
- ✅ 避免 404 錯誤（進度查詢和檔案下載）
- ✅ 簡化狀態管理

**設定方式**:

```bash
gunicorn app_pytubefix:app --bind 0.0.0.0:$PORT --workers 1 --timeout 300
```

**適用場景**:
- 小型應用程式（個人使用）
- 下載任務使用背景執行緒處理
- 不需要高並發支援

**未來改進**:
- 使用 Redis 或資料庫儲存任務狀態
- 支援多 Worker 部署

---

## 📦 安裝與部署

### Railway 部署 (Web 版)

#### 前置準備

1. **GitHub 帳號**
2. **Railway 帳號**
3. GitHub Repository: `vincetbear/ymp3`

#### 部署步驟

##### 1. 推送到 GitHub

```powershell
cd d:\01專案\2025\newyoutube\web_version
git add .
git commit -m "Update"
git push
```

##### 2. Railway 自動部署

- Railway 會自動偵測 GitHub 推送
- 自動執行建置和部署
- 約 2-3 分鐘完成

##### 3. 驗證部署

查看 Railway 日誌,應該看到:
```txt
✅ FFmpeg 已安裝
� 啟動 Gunicorn (1 worker)
```

#### Railway 配置檔案

**Dockerfile** (容器配置):
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p downloads
CMD gunicorn app_pytubefix:app --bind 0.0.0.0:$PORT --workers 1 --timeout 300
```

**requirements.txt** (Python 依賴):
```txt
flask==3.1.0
flask-cors==5.0.0
pytubefix
gunicorn==23.0.0
```

---

## 📱 使用說明

### Web 版使用

#### 桌面瀏覽器

1. **訪問網站**: `https://你的域名.railway.app`

2. **輸入網址**: 貼上 YouTube 連結

3. **選擇類型和畫質**:
   - 影片: 最佳/1080p/720p/480p/360p
   - 音訊: 自動轉為 MP3

4. **開始下載**: 點擊「開始下載」按鈕

5. **查看進度**: 即時顯示下載進度

6. **下載完成**: 自動觸發檔案下載

#### 手機使用 (PWA)

1. **訪問網站**: 使用手機瀏覽器

2. **安裝應用**:
   - **iOS**: Safari → 分享 → 加入主畫面
   - **Android**: Chrome → 選單 → 安裝應用程式

3. **使用**: 與桌面版相同流程

---

## ⚙️ 配置說明

### 檔案結構

```txt
web_version/
├── app_pytubefix.py       # Flask 主應用程式
├── requirements.txt        # Python 依賴
├── Dockerfile             # Docker 容器配置
├── start.sh              # 啟動腳本
├── templates/
│   └── index.html        # 前端頁面
├── static/
│   ├── js/app.js        # 前端 JavaScript
│   └── css/style.css    # 樣式
└── downloads/           # 下載檔案暫存
```

---

## 🔍 疑難排解

### 常見問題

#### 1. 下載失敗

**可能原因**:
- YouTube 網址錯誤或影片已刪除
- 影片有地區限制
- pytubefix 需要更新

**解決方案**:
- 確認網址正確且影片可正常播放
- 檢查 Railway 部署日誌
- 更新 pytubefix 版本

#### 2. MP3 轉檔失敗

**原因**: FFmpeg 未正確安裝

**Railway**: 已自動安裝在 Dockerfile 中，無需設定

**檢查方式**:
查看 Railway 日誌應顯示: `✅ FFmpeg 已安裝`

#### 3. 404 錯誤

**原因**: 多 Worker 導致記憶體不同步

**已解決**: 使用單一 Worker 模式 (`--workers 1`)

#### 4. 下載速度慢

**可能原因**:
- YouTube 伺服器速度
- Railway 頻寬限制
- 影片檔案較大

**建議**:
- 選擇較低畫質
- 等待下載完成（通常 1-3 分鐘）

### 日誌查看

**Railway 日誌**:
Railway → Deployments → View Logs

**成功日誌範例**:
```txt
✅ FFmpeg 已安裝
🚀 啟動 Gunicorn (1 worker)
📥 下載請求: task_id=xxx
✅ 下載完成
```

---



---

## ️ 開發與維護

### 本地開發

```powershell
cd d:\01專案\2025\newyoutube\web_version
python app_pytubefix.py
```

訪問: <http://localhost:5000>

### 部署更新

```powershell
git add .
git commit -m "Update"
git push
```

Railway 會自動偵測並重新部署。

### 升級 pytubefix

```powershell
pip install --upgrade pytubefix
```

更新 `requirements.txt` 後推送到 GitHub。

---

## 📄 授權

本專案僅供個人學習和使用。

**注意事項**:
- 請遵守 YouTube 服務條款
- 不要用於商業用途
- 尊重版權內容

---



---

## 📝 版本歷史

### v2.0.0 (2025-10-24)

**主要更新**:
- ✅ 升級 pytubefix 到最新版本
- ✅ 使用 Dockerfile 部署（更穩定）
- ✅ 單一 Worker 架構（解決 404 問題）
- ✅ 下載完成後自動清空輸入框
- ✅ 簡化環境設定（移除 Cookies 和代理需求）

**技術改進**:
- 從 yt-dlp 遷移到 pytubefix
- 優化記憶體管理和狀態同步
- 改善錯誤處理和日誌記錄
- FFmpeg 自動安裝

---

## 🎯 總結

這是一個簡潔高效的 YouTube 下載工具:

**核心功能**:
- ✅ 支援影片和音訊下載
- ✅ 自動轉換為 MP3 格式
- ✅ 即時進度顯示
- ✅ Railway 一鍵部署
- ✅ 跨平台支援（桌面/手機）

**技術特色**:
- 使用最新版 pytubefix 下載引擎
- Docker 容器化部署
- 單一 Worker 確保穩定性
- 自動清理下載檔案

**立即開始**: 參考「安裝與部署」章節! 🚀
