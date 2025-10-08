# 🚀 Flask Web App + PWA 完整部署指南

## 📋 目錄
1. [本地測試](#本地測試)
2. [部署到 Railway](#部署到-railway-推薦)
3. [部署到 Render](#部署到-render)
4. [部署到 Fly.io](#部署到-flyio)
5. [部署到 Vercel](#部署到-vercel)
6. [自訂網域設定](#自訂網域設定)
7. [PWA 安裝指南](#pwa-安裝指南)

---

## 🏠 本地測試

### 步驟 1: 安裝相依套件

```powershell
cd web_version
pip install -r requirements.txt
```

### 步驟 2: 執行應用程式

```powershell
python app.py
```

### 步驟 3: 開啟瀏覽器

訪問：`http://localhost:5000`

### 步驟 4: 手機測試（同一區網）

1. 查看你的電腦 IP 位址：
```powershell
ipconfig
```

2. 在手機瀏覽器輸入：
```
http://[你的IP]:5000
```
例如：`http://192.168.1.100:5000`

---

## 🚂 部署到 Railway（推薦）

### 為什麼選 Railway？
- ✅ 免費額度每月 $5
- ✅ 自動 HTTPS
- ✅ 簡單易用
- ✅ 支援 GitHub 自動部署

### 部署步驟

#### 1. 準備 Git Repository

```powershell
# 初始化 Git（在 web_version 資料夾）
cd web_version
git init
git add .
git commit -m "Initial commit"

# 推送到 GitHub
# 先在 GitHub 建立新的 repository
git remote add origin https://github.com/你的使用者名稱/youtube-downloader-web.git
git branch -M main
git push -u origin main
```

#### 2. 建立必要檔案

**Procfile**（告訴 Railway 如何啟動）：
```
web: gunicorn app:app
```

**runtime.txt**（指定 Python 版本）：
```
python-3.11.0
```

**.gitignore**：
```
__pycache__/
*.pyc
.env
downloads/
venv/
.venv/
```

#### 3. Railway 部署

1. 前往 [Railway.app](https://railway.app)
2. 點擊「Start a New Project」
3. 選擇「Deploy from GitHub repo」
4. 選擇你的 repository
5. Railway 會自動偵測並部署

#### 4. 環境變數設定（可選）

在 Railway Dashboard 中設定：
```
FLASK_ENV=production
MAX_CONTENT_LENGTH=524288000  # 500MB
```

#### 5. 取得網址

部署完成後，Railway 會提供一個網址，例如：
```
https://youtube-downloader-production.up.railway.app
```

---

## 🎨 部署到 Render

### 部署步驟

#### 1. 建立 Render 帳號

前往 [Render.com](https://render.com)

#### 2. 建立 Web Service

1. 點擊「New +」→「Web Service」
2. 連接 GitHub Repository
3. 設定：
   - **Name**: youtube-downloader
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free

#### 3. 環境變數

```
PYTHON_VERSION=3.11.0
```

#### 4. 部署

點擊「Create Web Service」，Render 會自動部署。

---

## ✈️ 部署到 Fly.io

### 部署步驟

#### 1. 安裝 Fly CLI

```powershell
# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex
```

#### 2. 登入 Fly.io

```powershell
fly auth login
```

#### 3. 初始化專案

```powershell
cd web_version
fly launch
```

選項：
- App Name: youtube-downloader（或自訂）
- Region: 選擇離你最近的（例如：Tokyo）
- Database: No

#### 4. 建立 fly.toml

```toml
app = "youtube-downloader"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512
```

#### 5. 部署

```powershell
fly deploy
```

#### 6. 開啟應用

```powershell
fly open
```

---

## ⚡部署到 Vercel（需調整）

> ⚠️ **注意**: Vercel 主要用於前端，部署 Flask 需要使用 Serverless Functions

### 替代方案：前後端分離

**前端**: Vercel（靜態 HTML/CSS/JS）
**後端**: Railway/Render（Flask API）

這樣可以享受 Vercel 的 CDN 加速。

---

## 🌐 自訂網域設定

### Railway

1. 進入專案 Settings
2. 點擊「Domains」
3. 新增自訂網域
4. 在你的網域提供商設定 CNAME：
   ```
   CNAME record:
   Name: www (或 @)
   Value: [railway-provided-domain]
   ```

### Render

1. 進入專案 Settings
2. 點擊「Custom Domain」
3. 輸入你的網域
4. 依照指示設定 DNS

---

## 📱 PWA 安裝指南

### iOS (Safari)

1. 開啟網站
2. 點擊分享按鈕（底部中間的方框+箭頭）
3. 選擇「加入主畫面」
4. 設定名稱，點擊「新增」

### Android (Chrome)

1. 開啟網站
2. 點擊選單（右上角三個點）
3. 選擇「安裝應用程式」或「加到主畫面」
4. 點擊「安裝」

### 桌面瀏覽器

1. 開啟網站
2. 網址列右側會出現「安裝」圖示（⊕）
3. 點擊安裝

---

## 🔧 生產環境優化

### 1. 修改 app.py（生產環境設定）

```python
# 在檔案最後修改
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

### 2. 加入檔案大小限制

```python
# 在 app.py 開頭加入
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB
```

### 3. 定期清理檔案

使用 Railway 的 Cron Jobs 或建立背景任務：

```python
# 在 app.py 加入
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(func=cleanup_old_files, trigger="interval", hours=1)
scheduler.start()
```

### 4. 加入速率限制

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)
```

---

## 📊 監控與日誌

### Railway

1. 進入專案 Dashboard
2. 點擊「Deployments」查看部署歷史
3. 點擊「Logs」查看即時日誌

### Render

1. 進入專案頁面
2. 點擊「Logs」標籤
3. 即時查看應用程式輸出

---

## 🐛 常見問題

### 1. 部署後無法下載

**原因**: 可能是檔案大小超過限制

**解決**:
- Railway: 升級到付費方案
- Render: 使用持久化儲存
- 考慮使用 S3/雲端儲存

### 2. 下載速度很慢

**原因**: 伺服器位置或頻寬限制

**解決**:
- 選擇離使用者更近的伺服器位置
- 升級伺服器規格

### 3. FFmpeg 錯誤

**解決**: 確保在 Dockerfile 或 buildpack 中安裝 FFmpeg

**Railway/Render**: 加入 `apt-packages` 檔案：
```
ffmpeg
```

---

## 💰 成本估算

### Railway
- 免費額度：每月 $5（約 500 小時）
- 付費：$5/月起

### Render
- 免費方案：有限制，但夠個人使用
- 付費：$7/月起

### Fly.io
- 免費額度：3 個小型 VM
- 付費：按用量計費

---

## 🎯 推薦部署流程

### 個人使用（免費）
```
Railway 免費方案
↓
自動 HTTPS
↓
分享連結給朋友
```

### 進階使用（付費）
```
Railway/Render 付費方案
↓
自訂網域
↓
CDN 加速（Cloudflare）
↓
監控與備份
```

---

## 🚀 快速開始部署（最簡單）

### 選擇 Railway 一鍵部署

1. 點擊這個按鈕（在 GitHub README 中加入）：
   
   [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

2. 連接 GitHub
3. 選擇 repository
4. 等待部署完成
5. 取得網址並分享！

---

## 📝 部署檢查清單

- [ ] 程式碼推送到 GitHub
- [ ] requirements.txt 已更新
- [ ] Procfile 已建立
- [ ] .gitignore 已設定
- [ ] 選擇部署平台
- [ ] 環境變數已設定
- [ ] 測試部署成功
- [ ] 手機測試 PWA 安裝
- [ ] 設定自訂網域（可選）
- [ ] 設定監控與日誌

---

## 🎉 完成！

部署完成後，你會得到一個可以在任何裝置上使用的 YouTube 下載工具！

**範例網址**: `https://your-app.railway.app`

分享給朋友，在手機上安裝 PWA，享受便捷的下載體驗！

---

需要幫助？查看各平台的官方文件：
- [Railway Docs](https://docs.railway.app)
- [Render Docs](https://render.com/docs)
- [Fly.io Docs](https://fly.io/docs)
