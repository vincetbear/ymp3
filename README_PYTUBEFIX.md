# 🎬 YouTube 下載器 (pytubefix 版本)

一個簡潔高效的 YouTube 影片/音訊下載 Web 應用,使用 pytubefix 套件,支援自動 MP3 轉換。

---

## ✨ 功能特色

- ✅ **影片下載**: 支援多種解析度 (1080p, 720p, 480p, 360p, 最佳畫質)
- ✅ **音訊下載**: 自動轉換為 MP3 格式 (192kbps)
- ✅ **即時進度**: 下載進度即時顯示
- ✅ **自動清理**: 1 小時後自動刪除檔案
- ✅ **無需 Cookies**: 目前不需要 YouTube cookies (簡化部署)
- ✅ **PWA 支援**: 可安裝為手機應用程式
- ✅ **Railway 部署**: 一鍵部署到雲端

---

## 🚀 快速開始

### Railway 部署 (推薦)

1. **Fork 此專案**到你的 GitHub

2. **連接 Railway**
   - 訪問 [Railway.app](https://railway.app)
   - 選擇 "Deploy from GitHub repo"
   - 選擇你的儲存庫

3. **設定根目錄**
   - Settings → Root Directory
   - 輸入: `web_version`

4. **生成域名**
   - Settings → Domains
   - 點擊 "Generate Domain"

5. **完成!** 訪問你的 Railway URL

### 本地開發

```bash
# 1. 安裝依賴
cd web_version
pip install -r requirements.txt

# 2. 啟動應用
python app_pytubefix.py

# 3. 訪問
http://localhost:5000
```

---

## 🔧 技術架構

### 後端

- **Flask**: Web 框架
- **pytubefix**: YouTube 下載引擎
- **FFmpeg**: MP3 音訊轉換
- **Gunicorn**: WSGI 伺服器 (生產環境)

### 前端

- **HTML5/CSS3/JavaScript**: Web UI
- **PWA**: 離線支援和應用安裝
- **Service Worker**: 快取和離線功能

### 部署

- **Railway**: 雲端平台
- **Nixpacks**: 自動建置系統
- **FFmpeg**: 系統依賴 (via Aptfile)

---

## 📦 專案結構

```
web_version/
├── app_pytubefix.py           # Flask 主應用 ⭐
├── pytubefix_downloader.py    # 核心下載模組 ⭐
├── requirements.txt            # Python 依賴
├── nixpacks.toml              # Railway 建置配置
├── Procfile                   # 啟動指令
├── Aptfile                    # 系統依賴 (FFmpeg)
├── runtime.txt                # Python 版本
├── templates/
│   └── index.html            # Web UI
├── static/
│   ├── css/
│   ├── js/
│   └── icons/
└── downloads/                 # 下載暫存 (自動清理)
```

---

## 🎯 API 端點

### POST `/api/info`

獲取影片資訊

**請求:**
```json
{
  "url": "https://www.youtube.com/watch?v=xxxxx"
}
```

**回應:**
```json
{
  "title": "影片標題",
  "author": "作者",
  "length": 254,
  "views": 807,
  "resolutions": ["360p", "720p"],
  "audio_bitrate": "160kbps"
}
```

### POST `/api/download`

開始下載任務

**請求:**
```json
{
  "url": "https://www.youtube.com/watch?v=xxxxx",
  "type": "audio",      // 或 "video"
  "quality": "best"     // 或 "1080p", "720p", etc.
}
```

**回應:**
```json
{
  "task_id": "uuid",
  "message": "下載任務已建立"
}
```

### GET `/api/progress/<task_id>`

查詢下載進度

**回應:**
```json
{
  "status": "downloading",  // pending, downloading, converting, completed, error
  "progress": 85.3,
  "message": "正在下載...",
  "filename": "video.mp3"
}
```

### GET `/api/file/<task_id>`

下載完成的檔案

---

## 🔍 使用範例

### Python 腳本

```python
from pytubefix_downloader import download_audio, download_video

# 下載音訊並轉 MP3
mp3_file = download_audio(
    url='https://www.youtube.com/watch?v=xxxxx',
    output_path='downloads',
    bitrate='192k'
)

# 下載影片
video_file = download_video(
    url='https://www.youtube.com/watch?v=xxxxx',
    output_path='downloads',
    quality='720p'
)
```

### cURL API 測試

```bash
# 獲取影片資訊
curl -X POST "https://你的域名.railway.app/api/info" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=xxxxx"}'

# 下載音訊
curl -X POST "https://你的域名.railway.app/api/download" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=xxxxx", "type": "audio"}'
```

---

## ⚙️ 配置說明

### requirements.txt

```
flask==3.1.0
flask-cors==5.0.0
pytubefix>=10.0.0
gunicorn==23.0.0
```

### nixpacks.toml

```toml
[phases.setup]
nixPkgs = ["python39", "ffmpeg-full"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "gunicorn app_pytubefix:app --bind 0.0.0.0:$PORT"
```

### Aptfile

```
ffmpeg
```

---

## 🐛 疑難排解

### 問題 1: Railway 部署失敗

**解決**:
1. 確認 Root Directory 設定為 `web_version`
2. 檢查所有配置檔案都存在
3. 查看部署日誌找出錯誤

### 問題 2: MP3 轉換失敗

**解決**:
1. 確認 FFmpeg 已安裝 (查看建置日誌)
2. 確認 `nixpacks.toml` 包含 `ffmpeg-full`
3. 確認 `Aptfile` 包含 `ffmpeg`

### 問題 3: 下載失敗 - Bot 偵測

**目前狀態**: pytubefix 測試不需要 cookies

**如果遇到**: 需要添加 cookies 支援 (參考舊版 app.py)

---

## 📊 效能資訊

### Railway 免費方案

- 每月 500 小時執行時間
- 512 MB RAM
- 1 GB 磁碟空間
- 自動休眠 (無流量時)

### 轉換效能

- MP3 轉換時間: ~5-10 秒 (4 分鐘影片)
- 原始 m4a: ~4 MB
- 轉換後 MP3 (192kbps): ~6 MB

---

## 🔐 安全性

### 自動清理

- 下載檔案 1 小時後自動刪除
- 節省磁碟空間
- 保護使用者隱私

### .gitignore

```
downloads/
*cookies*.txt
test_*.py
*.log
```

---

## 📝 授權

本專案僅供個人學習和使用。

**注意事項**:
- 請遵守 YouTube 服務條款
- 不要用於商業用途
- 尊重版權內容

---

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request!

### 開發

```bash
# Fork 專案
git clone https://github.com/你的帳號/ymp3.git
cd ymp3/web_version

# 安裝依賴
pip install -r requirements.txt

# 執行測試
python test_direct.py

# 啟動開發伺服器
python app_pytubefix.py
```

---

## 📚 相關連結

- [pytubefix 文檔](https://pytubefix.readthedocs.io/)
- [Railway 文檔](https://docs.railway.app/)
- [Flask 文檔](https://flask.palletsprojects.com/)
- [FFmpeg 文檔](https://ffmpeg.org/documentation.html)

---

## 🎊 致謝

- [pytubefix](https://github.com/JuanBindez/pytubefix) - YouTube 下載核心
- [Flask](https://flask.palletsprojects.com/) - Web 框架
- [Railway](https://railway.app/) - 雲端部署平台
- [FFmpeg](https://ffmpeg.org/) - 音訊轉換工具

---

**使用 pytubefix 構建,部署於 Railway** 🚀
