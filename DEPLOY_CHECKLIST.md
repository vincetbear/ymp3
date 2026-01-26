# ✅ Railway 部署前檢查清單

## 📋 部署前確認

### 1. 必要檔案檢查

在 `web_version/` 目錄中:

- [ ] `app_pytubefix.py` - Flask 主應用
- [ ] `pytubefix_downloader.py` - 核心下載模組
- [ ] `requirements.txt` - Python 依賴
- [ ] `nixpacks.toml` - Railway 建置配置
- [ ] `Procfile` - 啟動指令
- [ ] `Aptfile` - 系統依賴 (FFmpeg)
- [ ] `runtime.txt` - Python 版本
- [ ] `templates/index.html` - Web UI
- [ ] `static/` 資料夾 - 靜態資源

### 2. 配置檔案檢查

#### requirements.txt 內容:
```
flask==3.1.0
flask-cors==5.0.0
pytubefix>=10.0.0
gunicorn==23.0.0
```

✅ 確認: 
- [ ] 包含 `pytubefix>=10.0.0`
- [ ] 包含 `gunicorn==23.0.0`
- [ ] 不包含 `yt-dlp` (舊版)

#### nixpacks.toml 內容:
```toml
[start]
cmd = "gunicorn app_pytubefix:app --bind 0.0.0.0:$PORT"
```

✅ 確認:
- [ ] 啟動指令為 `app_pytubefix:app`
- [ ] 包含 `ffmpeg-full` 在 nixPkgs

#### Procfile 內容:
```
web: gunicorn app_pytubefix:app
```

✅ 確認:
- [ ] 指向 `app_pytubefix:app`

#### Aptfile 內容:
```
ffmpeg
```

✅ 確認:
- [ ] 包含 `ffmpeg` (MP3 轉換必需)

### 3. .gitignore 檢查

確認以下項目被排除:

- [ ] `downloads/` - 下載暫存
- [ ] `test_*.py` - 測試檔案
- [ ] `*cookies*.txt` - Cookies 檔案
- [ ] `__pycache__/` - Python 快取
- [ ] `.venv/` - 虛擬環境

### 4. 本地測試

在推送前進行本地測試:

```bash
cd web_version
python app_pytubefix.py
```

測試項目:

- [ ] 伺服器正常啟動
- [ ] 訪問 http://localhost:5000 正常
- [ ] 可以獲取影片資訊
- [ ] 可以下載影片
- [ ] 可以下載音訊並轉 MP3
- [ ] MP3 轉換成功

### 5. Git 提交檢查

```bash
# 查看狀態
git status

# 確認只提交必要檔案
git add web_version/app_pytubefix.py
git add web_version/pytubefix_downloader.py
git add web_version/requirements.txt
git add web_version/nixpacks.toml
git add web_version/Procfile
git add web_version/Aptfile
git add web_version/runtime.txt
git add web_version/templates/
git add web_version/static/
git add web_version/.gitignore

# 提交
git commit -m "🚀 準備 Railway 部署 - pytubefix 版本"
```

✅ 確認:
- [ ] 不包含測試檔案
- [ ] 不包含 downloads/ 內容
- [ ] 不包含 cookies 檔案
- [ ] 不包含 .venv/

---

## 🚀 部署步驟

### 步驟 1: 推送到 GitHub

```bash
git push origin main
```

### 步驟 2: 連接 Railway

1. 前往 https://railway.app/dashboard
2. 點擊 "New Project"
3. 選擇 "Deploy from GitHub repo"
4. 選擇 `vincetbear/ymp3`

### 步驟 3: 設定根目錄

1. 點擊你的服務
2. Settings → Root Directory
3. 輸入: `web_version`
4. 儲存

### 步驟 4: 生成域名

1. Settings → Domains
2. 點擊 "Generate Domain"
3. 複製 URL

### 步驟 5: 驗證部署

查看部署日誌,確認:

- [ ] Python 安裝成功
- [ ] FFmpeg 安裝成功
- [ ] pytubefix 安裝成功
- [ ] Gunicorn 啟動成功
- [ ] 沒有錯誤訊息

### 步驟 6: 測試應用

訪問 Railway URL,測試:

- [ ] 頁面正常載入
- [ ] 可以輸入 YouTube 網址
- [ ] 可以獲取影片資訊
- [ ] 可以下載影片
- [ ] 可以下載音訊 (MP3)
- [ ] 進度顯示正常

---

## 📝 快速命令

```bash
# 一鍵部署腳本
cd d:\01專案\2025\newyoutube

# 檢查狀態
git status

# 添加檔案
git add web_version/

# 提交
git commit -m "🚀 部署 pytubefix 版本到 Railway"

# 推送
git push origin main

# Railway 會自動偵測並部署!
```

---

## ❌ 常見錯誤

### 錯誤 1: "No such file or directory: app.py"

**原因**: 未設定 Root Directory 或啟動指令錯誤

**解決**:
1. Settings → Root Directory → `web_version`
2. 確認 nixpacks.toml 指向 `app_pytubefix:app`

### 錯誤 2: "ModuleNotFoundError: No module named 'pytubefix'"

**原因**: requirements.txt 未正確安裝

**解決**:
1. 確認 requirements.txt 包含 `pytubefix>=10.0.0`
2. 重新部署

### 錯誤 3: "ffmpeg: not found"

**原因**: FFmpeg 未安裝

**解決**:
1. 確認 Aptfile 包含 `ffmpeg`
2. 確認 nixpacks.toml 包含 `ffmpeg-full`
3. 重新部署

### 錯誤 4: "Address already in use"

**原因**: 端口衝突

**解決**:
Railway 會自動設定 $PORT,無需手動配置

---

## ✅ 成功指標

部署成功後應該看到:

### 建置日誌:
```
✓ Installing Python 3.9
✓ Installing FFmpeg
✓ Installing pytubefix
✓ Installing Flask
✓ Installing Gunicorn
✓ Build successful
```

### 運行日誌:
```
Starting server...
Gunicorn running on port 8080
Listening on 0.0.0.0:8080
```

### 訪問測試:
- ✅ Railway URL 可以訪問
- ✅ Web UI 正常顯示
- ✅ 可以下載影片
- ✅ MP3 轉換正常

---

## 🎉 部署完成!

恭喜!你的 YouTube 下載器已經部署到 Railway!

**下一步**:

1. 分享你的 Railway URL
2. 添加自訂域名 (可選)
3. 監控使用量和效能
4. 享受你的應用!

**Railway URL 範例**:
```
https://ymp3-production.up.railway.app
```

---

**準備就緒!開始部署吧!** 🚀
