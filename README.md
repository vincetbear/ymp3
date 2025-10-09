# YouTube 下載工具

一個功能完整的 YouTube 影片/音訊下載工具,支援桌面版和 Web 版,具備自動 MP3 轉檔、Cookies 認證和代理支援。

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

### 桌面版 (Windows .exe)

- ✅ **影片下載**: 支援多種解析度 (1080p, 720p, 480p, 360p, 最佳畫質)
- ✅ **音訊下載**: 自動轉換為 MP3 格式 (128/192/320 kbps)
- ✅ **圖形介面**: 友善的 Tkinter GUI
- ✅ **進度顯示**: 即時下載進度、速度和剩餘時間
- ✅ **路徑選擇**: 自訂下載儲存位置
- ✅ **獨立執行**: 單一 .exe 檔案,無需安裝 Python

### Web 版 (Railway 部署)

- ✅ **影片下載**: 多種畫質選擇
- ✅ **音訊下載**: 自動轉換為 192kbps MP3
- ✅ **Cookies 認證**: 繞過 YouTube bot 偵測
- ✅ **代理支援**: 100+ WebShare 代理 IP 輪替 (可選)
- ✅ **PWA 支援**: 可安裝為手機應用程式
- ✅ **自動清理**: 定期刪除超過 1 小時的檔案
- ✅ **跨平台**: 支援桌面、平板、手機
- ✅ **雲端部署**: Railway 自動部署和擴展

---

## 🏗️ 系統架構

### 桌面版架構

```
youtube_downloader.py (主程式)
├── Tkinter GUI
├── yt-dlp (YouTube 下載引擎)
├── FFmpeg (音訊轉檔)
└── PyInstaller (打包為 .exe)
```

**核心技術**:
- **Python 3.13.5**: 主要開發語言
- **Tkinter**: 圖形使用者介面
- **yt-dlp 2025.09.26**: YouTube 下載核心
- **FFmpeg**: 音訊/影片轉檔
- **PyInstaller**: 打包為獨立執行檔

### Web 版架構

```
Flask 應用程式
├── 前端 (PWA)
│   ├── HTML/CSS/JavaScript
│   ├── Service Worker
│   └── Manifest (PWA 設定)
├── 後端 (Flask API)
│   ├── /api/info (獲取影片資訊)
│   ├── /api/download (下載任務)
│   ├── /api/progress/<task_id> (進度查詢)
│   └── /api/file/<filename> (檔案下載)
├── 下載引擎
│   ├── yt-dlp (YouTube 下載)
│   ├── FFmpeg (MP3 轉檔)
│   └── Cookies 認證
└── 代理系統 (可選)
    ├── WebShare 代理池
    └── 隨機 IP 輪替
```

**核心技術**:
- **Flask 3.1.0**: Web 框架
- **yt-dlp >=2025.1.7**: YouTube 下載
- **FFmpeg**: MP3 轉檔
- **Gunicorn 23.0.0**: WSGI 伺服器
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

### Cookies 認證系統

**為什麼需要 Cookies?**

YouTube 會偵測自動化下載並要求登入驗證。使用 Cookies 可以:
- 繞過 bot 偵測
- 存取需登入的內容
- 提高下載成功率

**實作方式**:

1. **本地環境**: 讀取 `youtube.com_cookies.txt` 檔案
2. **Railway 環境**: 從環境變數 `YOUTUBE_COOKIES_B64` 解碼

```python
def get_cookies_file():
    # 優先使用環境變數 (Railway)
    cookies_b64 = os.environ.get('YOUTUBE_COOKIES_B64')
    if cookies_b64:
        cookies_content = base64.b64decode(cookies_b64).decode('utf-8')
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        temp_file.write(cookies_content)
        return temp_file.name
    
    # 備用: 本地檔案
    for cookie_file in ['youtube_cookies.txt', 'youtube.com_cookies.txt']:
        if os.path.exists(cookie_file):
            return cookie_file
    
    return None
```

**Cookies 匯出**:

使用 yt-dlp 從瀏覽器匯出:
```bash
yt-dlp --cookies-from-browser chrome --cookies youtube.com_cookies.txt "https://www.youtube.com"
```

### 代理系統 (可選)

**WebShare 代理池**:
- 100+ 代理 IP
- 隨機輪替機制
- 自動負載平衡

**實作**:
```python
def get_random_proxy():
    if not PROXY_IPS:
        return None
    proxy_ip = random.choice(PROXY_IPS)
    return f"http://{USERNAME}:{PASSWORD}@{proxy_ip}"
```

**使用時機**:
- Cookies 失效時
- 需要更換 IP 時
- 設定 `USE_PROXY=true` 時

---

## 📦 安裝與部署

### 本地安裝 (桌面版)

#### 系統需求
- Windows 10/11
- FFmpeg (必須)

#### 安裝步驟

1. **下載 FFmpeg**:
   - 訪問: https://www.gyan.dev/ffmpeg/builds/
   - 下載 "ffmpeg-release-essentials.zip"
   - 解壓到 `C:\ffmpeg`
   - 添加到系統 PATH: `C:\ffmpeg\bin`

2. **安裝 Python 依賴** (如果要從源碼執行):
   ```powershell
   cd D:\01專案\2025\newyoutube
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **執行程式**:
   - 直接執行: `dist\YouTube下載工具.exe`
   - 或從源碼: `python youtube_downloader.py`

#### 重新打包 .exe

```powershell
python -m PyInstaller --clean --onefile --noconsole --name "YouTube下載工具" youtube_downloader.py
```

輸出位置: `dist\YouTube下載工具.exe` (約 84 MB)

### Railway 部署 (Web 版)

#### 前置準備

1. **GitHub 帳號**
2. **Railway 帳號**: https://railway.app
3. **Cookies Base64**: 從本地生成

#### 部署步驟

##### 1. 推送到 GitHub

```powershell
cd d:\01專案\2025\newyoutube\web_version
git add .
git commit -m "Initial commit"
git push
```

##### 2. 連接 Railway

1. 登入 Railway: https://railway.app/dashboard
2. 點擊 "New Project"
3. 選擇 "Deploy from GitHub repo"
4. 選擇 `vincetbear/ymp3`
5. Railway 自動偵測並部署

##### 3. 設定環境變數

在 Railway 專案的 **Variables** 標籤添加:

**必要變數**:
```bash
YOUTUBE_COOKIES_B64=<cookies的base64編碼>
```

**可選變數** (啟用代理):
```bash
USE_PROXY=true
WEBSHARE_USERNAME=ellpsmsi
WEBSHARE_PASSWORD=5x76u62w6hou
PROXY_IPS=23.94.138.113:6387,192.241.104.29:8123,...
```

##### 4. 生成 Cookies Base64

```powershell
cd d:\01專案\2025\newyoutube\web_version
python -c "import base64; print(base64.b64encode(open('youtube.com_cookies.txt', 'rb').read()).decode())"
```

複製輸出的字串,設定為 `YOUTUBE_COOKIES_B64` 環境變數。

##### 5. 驗證部署

查看 Railway 日誌,應該看到:
```
✅ 使用環境變數中的 cookies
🔒 WebShare 代理池已載入: 100 個代理 (如果啟用)
```

#### Railway 配置檔案

**nixpacks.toml** (建置配置):
```toml
[phases.setup]
nixPkgs = ["python39", "ffmpeg-full"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "gunicorn app:app --bind 0.0.0.0:$PORT"
```

**Aptfile** (系統依賴):
```
ffmpeg
```

**requirements.txt** (Python 依賴):
```
Flask==3.1.0
flask-cors==5.0.0
yt-dlp>=2025.1.7
gunicorn==23.0.0
requests>=2.31.0
```

---

## 📱 使用說明

### 桌面版使用

1. **執行程式**: 雙擊 `YouTube下載工具.exe`

2. **輸入網址**: 貼上 YouTube 影片網址
   ```
   例如: https://www.youtube.com/watch?v=xxxxx
   ```

3. **選擇類型**:
   - 影片 (MP4) - 選擇畫質
   - 音訊 (MP3) - 選擇音質

4. **選擇路徑**: 點擊「瀏覽」選擇儲存位置

5. **開始下載**: 點擊「🚀 開始下載」

6. **等待完成**: 查看進度條和狀態

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

## ⚙️ 環境變數設定

### Railway 環境變數

#### YOUTUBE_COOKIES_B64 (必要)

YouTube 認證 cookies 的 base64 編碼。

**生成方式**:
```powershell
python -c "import base64; print(base64.b64encode(open('youtube.com_cookies.txt', 'rb').read()).decode())"
```

**設定位置**: Railway → Variables → Add Variable

**範例值**: 
```
IyBOZXRzY2FwZSBIVFRQIENvb2tpZSBGaWxlDQojIFRoaXMgZmlsZS...
```

**有效期**: 數週到數月,過期後需重新匯出

#### USE_PROXY (可選)

是否啟用代理系統。

**預設值**: `false`

**啟用代理**: `true`

**說明**: 只在 cookies 不足時才需要啟用

#### WEBSHARE_USERNAME (可選)

WebShare 代理帳號用戶名。

**預設值**: `ellpsmsi`

**用途**: 代理認證

#### WEBSHARE_PASSWORD (可選)

WebShare 代理帳號密碼。

**預設值**: `5x76u62w6hou`

**用途**: 代理認證

#### PROXY_IPS (可選)

代理 IP 列表,逗號分隔。

**格式**: `IP:PORT,IP:PORT,...`

**範例**: 
```
23.94.138.113:6387,192.241.104.29:8123,82.27.216.28:5359
```

**預設**: 內建 100+ 代理 IP

---

## 🔍 疑難排解

### 常見問題

#### 1. 下載失敗: "Sign in to confirm you're not a bot"

**原因**: Cookies 未設定或已過期

**解決方案**:

**Railway**:
1. 確認 `YOUTUBE_COOKIES_B64` 環境變數已設定
2. 重新匯出 cookies 並更新環境變數

**本地**:
1. 重新匯出 cookies:
   ```powershell
   yt-dlp --cookies-from-browser chrome --cookies youtube.com_cookies.txt "https://www.youtube.com"
   ```

#### 2. MP3 轉檔失敗

**原因**: FFmpeg 未安裝或不在 PATH

**解決方案**:

**Windows**:
1. 下載 FFmpeg: https://www.gyan.dev/ffmpeg/builds/
2. 解壓到 `C:\ffmpeg`
3. 添加到 PATH: `C:\ffmpeg\bin`
4. 重啟終端機

**驗證安裝**:
```powershell
ffmpeg -version
```

**Railway**: 已自動安裝,無需設定

#### 3. Railway 部署失敗

**檢查清單**:
- ✅ `requirements.txt` 存在且正確
- ✅ `nixpacks.toml` 或 `Aptfile` 包含 ffmpeg
- ✅ `Procfile` 或 `nixpacks.toml` 有啟動指令
- ✅ 環境變數已設定

**查看日誌**:
Railway → Deployments → View Logs

#### 4. 代理連接超時

**原因**: WebShare 代理速度慢或不穩定

**解決方案**:
1. 關閉代理: 刪除 `USE_PROXY` 環境變數
2. Cookies 已足夠繞過 bot 偵測

#### 5. 下載速度慢

**可能原因**:
- 網路速度限制
- YouTube 伺服器速度
- 使用代理時的額外延遲

**建議**:
- 關閉代理使用 (如果已有 cookies)
- 選擇較低畫質
- 檢查網路連線

### 測試工具

專案包含多個測試腳本:

#### test_cookies_only.py
測試 cookies 是否有效
```powershell
python test_cookies_only.py
```

#### test_mp3_conversion.py
測試 MP3 轉檔功能
```powershell
python test_mp3_conversion.py
```

#### test_specific_video.py
測試特定影片下載
```powershell
python test_specific_video.py
```

#### test_cookies_proxy.py
測試 cookies + 代理組合
```powershell
python test_cookies_proxy.py
```

### 日誌查看

#### 本地
查看終端機輸出

#### Railway
Railway → Deployments → View Logs

**成功日誌**:
```
✅ 使用環境變數中的 cookies
🎵 下載音訊格式並轉換為 MP3
✅ 下載完成
```

**錯誤日誌**:
```
❌ 下載失敗: ERROR: [youtube] Sign in to confirm...
⚠️ 未找到 cookies
```

---

## 📊 專案結構

```
newyoutube/
├── youtube_downloader.py      # 桌面版主程式
├── requirements.txt            # Python 依賴
├── .venv/                      # 虛擬環境
├── dist/
│   └── YouTube下載工具.exe   # 打包後的執行檔
└── web_version/
    ├── app.py                 # Flask 主應用
    ├── proxy_config.py        # 代理配置
    ├── requirements.txt       # Web 版依賴
    ├── runtime.txt            # Python 版本
    ├── nixpacks.toml          # Railway 建置配置
    ├── Aptfile                # 系統依賴
    ├── Dockerfile             # Docker 配置 (備用)
    ├── templates/
    │   └── index.html         # 前端 HTML
    ├── static/
    │   ├── manifest.json      # PWA 設定
    │   ├── service-worker.js  # Service Worker
    │   └── icons/             # PWA 圖示
    ├── downloads/             # 下載檔案暫存
    └── test_*.py              # 測試腳本
```

---

## 🔐 安全性

### Cookies 保護

- ✅ 本地 cookies 檔案已加入 `.gitignore`
- ✅ 不推送到公開 GitHub
- ✅ Railway 環境變數已加密
- ⚠️ 不要公開分享 cookies base64

### 代理帳號

- ⚠️ WebShare 帳號密碼已在代碼中 (僅供測試)
- 💡 生產環境應使用環境變數
- 💡 定期更換密碼

### 檔案清理

Web 版自動清理超過 1 小時的檔案:
```python
def cleanup_old_files():
    for filename in os.listdir(DOWNLOAD_FOLDER):
        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        if now - file_time > timedelta(hours=1):
            os.remove(file_path)
```

---

## 📈 效能與限制

### 效能指標

| 項目 | 桌面版 | Web 版 |
|-----|--------|--------|
| 下載速度 | 快速 | 中等 (受 Railway 頻寬限制) |
| MP3 轉檔 | 5-10 秒 | 5-10 秒 |
| 並發下載 | 1 | 多個 (Railway 自動擴展) |
| 檔案大小限制 | 無 | 受 Railway 磁碟限制 |
| 儲存時間 | 永久 | 1 小時 (自動清理) |

### 系統限制

#### Railway 免費方案
- 每月 500 小時執行時間
- 512 MB RAM
- 1 GB 磁碟空間
- 自動休眠 (無流量時)

#### YouTube 限制
- 某些影片有地區限制
- 某些影片需要會員
- 私人或已刪除的影片無法下載

#### FFmpeg 依賴
- 必須安裝 FFmpeg 才能轉 MP3
- Railway 已自動安裝
- 本地需手動安裝

---

## 🛠️ 開發與維護

### 本地開發

#### 啟動 Flask 開發伺服器

```powershell
cd d:\01專案\2025\newyoutube\web_version
python app.py
```

訪問: http://localhost:5000

#### 更新 yt-dlp

```powershell
pip install --upgrade yt-dlp
```

#### 更新 Cookies

定期重新匯出 (建議每 2-4 週):
```powershell
yt-dlp --cookies-from-browser chrome --cookies youtube.com_cookies.txt "https://www.youtube.com"
```

### 部署更新

```powershell
cd d:\01專案\2025\newyoutube\web_version
git add .
git commit -m "Update features"
git push
```

Railway 會自動偵測並重新部署。

### 監控

#### Railway 日誌
定期檢查部署日誌,確認無錯誤。

#### Cookies 有效性
如果下載開始失敗,可能是 cookies 過期,需重新匯出。

---

## 📄 授權

本專案僅供個人學習和使用。

**注意事項**:
- 請遵守 YouTube 服務條款
- 不要用於商業用途
- 尊重版權內容

---

## 🤝 支援

### 文件
本 README 包含完整的安裝、部署和使用說明。

### 測試
使用專案中的測試腳本驗證功能。

### 問題排查
參考「疑難排解」章節。

---

## 📝 版本歷史

### v1.0.0 (2025-10-08)

**桌面版**:
- ✅ 完整的 Tkinter GUI
- ✅ 影片和音訊下載
- ✅ MP3 自動轉檔
- ✅ 打包為獨立 .exe

**Web 版**:
- ✅ Flask REST API
- ✅ PWA 前端
- ✅ Cookies 認證系統
- ✅ MP3 自動轉檔
- ✅ 100+ 代理 IP 輪替 (可選)
- ✅ Railway 自動部署
- ✅ 自動檔案清理

**部署**:
- ✅ Railway 雲端部署
- ✅ GitHub 自動同步
- ✅ 環境變數配置

---

## 🎯 總結

這是一個功能完整的 YouTube 下載解決方案:

**桌面用戶**: 使用 `YouTube下載工具.exe`,簡單快速

**Web 用戶**: 訪問 Railway 部署的網站,隨時隨地下載

**開發者**: 完整的源碼和文檔,易於擴展和維護

所有核心功能已完成並測試通過,包括:
- ✅ 影片/音訊下載
- ✅ MP3 自動轉檔
- ✅ Cookies 認證
- ✅ 代理支援
- ✅ PWA 應用
- ✅ 雲端部署

**立即開始**: 參考「安裝與部署」章節! 🚀
