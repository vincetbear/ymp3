# 🚨 FFmpeg 安裝失敗 - 終極修復指南

## ❌ 持續出現的錯誤

```
❌ 錯誤: 找不到 FFmpeg
⚠️ 警告: 轉換失敗,返回原始檔案 .m4a
```

---

## 🔄 修復歷程

### 嘗試 1: 使用 `aptPkgs` ❌
```toml
[phases.setup]
aptPkgs = ["ffmpeg"]
```
**結果**: 失敗 - Nixpacks 在某些情況下不執行 aptPkgs

### 嘗試 2: 使用 `nixPkgs` ❌
```toml
[phases.setup]
nixPkgs = ["ffmpeg-full"]
```
**結果**: 失敗 - Nix 套件庫中 ffmpeg-full 不存在或有相依性問題

### 嘗試 3: 直接使用 `apt-get` ✅ (當前方案)
```toml
[phases.install]
cmds = [
    "apt-get update && apt-get install -y ffmpeg",
    "ffmpeg -version"
]
```
**狀態**: 測試中

---

## ✅ 當前修復方案

### 方案 A: Nixpacks (主要方案)

**檔案**: `nixpacks.toml`

```toml
[phases.setup]
nixPkgs = ["python39"]

[phases.install]
cmds = [
    "apt-get update && apt-get install -y ffmpeg",
    "ffmpeg -version",
    "pip install -r requirements.txt",
    "chmod +x start.sh"
]

[start]
cmd = "./start.sh"
```

**特點**:
- ✅ 在 install 階段直接使用 apt-get
- ✅ 立即驗證 FFmpeg 安裝
- ✅ 使用 start.sh 啟動前再次檢查

### 方案 B: Dockerfile (備援方案)

**檔案**: `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

RUN ffmpeg -version

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p downloads

EXPOSE 8080

CMD gunicorn app_pytubefix:app --bind 0.0.0.0:$PORT --workers 2 --timeout 300
```

**使用方法**: 
1. Railway 會自動偵測 Dockerfile
2. 如果 Dockerfile 存在,Railway 會優先使用它而非 Nixpacks
3. 這是最可靠的方法

### 增強的 `start.sh`

```bash
#!/bin/bash
# 檢查 FFmpeg
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg 已安裝"
    ffmpeg -version | head -n 1
else
    echo "⚠️ FFmpeg 未找到,嘗試安裝..."
    apt-get update && apt-get install -y ffmpeg || echo "❌ FFmpeg 安裝失敗"
    
    # 再次檢查
    if command -v ffmpeg &> /dev/null; then
        echo "✅ FFmpeg 安裝成功"
    else
        echo "❌ 錯誤: 無法安裝 FFmpeg!"
        echo "⚠️ 音訊下載將只能保存為 m4a 格式"
    fi
fi

# 啟動 Gunicorn (不因 FFmpeg 失敗而停止)
exec gunicorn app_pytubefix:app --bind 0.0.0.0:$PORT --workers 2 --timeout 300
```

**改進**:
- ✅ 啟動時再次嘗試安裝 FFmpeg
- ✅ 即使 FFmpeg 失敗,應用程式仍會啟動
- ✅ 音訊檔案會保留為 m4a (總比無法下載好)

---

## 📊 三層防護策略

| 階段 | 方法 | 說明 |
|------|------|------|
| **1. Build (Dockerfile)** | `apt-get install ffmpeg` | 建置時安裝 FFmpeg |
| **2. Install (nixpacks)** | `apt-get install ffmpeg` | Nixpacks install 階段安裝 |
| **3. Start (start.sh)** | 檢查並嘗試安裝 | 啟動時最後一道防線 |

---

## 🧪 部署後驗證步驟

### 1. 檢查 Railway 建置日誌

**搜尋關鍵字**: `ffmpeg`

**預期輸出**:
```
Installing ffmpeg...
Get:1 http://deb.debian.org/debian bullseye/main amd64 ffmpeg amd64 7:4.3.6-0+deb11u1 [1565 kB]
Fetched 1565 kB in 1s (1024 kB/s)
Selecting previously unselected package ffmpeg.
Setting up ffmpeg (7:4.3.6-0+deb11u1) ...
ffmpeg version 4.3.6-0+deb11u1
✅ FFmpeg installed successfully
```

### 2. 檢查啟動日誌

**預期輸出**:
```
==========================================
Railway 環境檢查
==========================================
Python 版本:
Python 3.11.x

檢查 FFmpeg:
✅ FFmpeg 已安裝
ffmpeg version 4.3.6-0+deb11u1

檢查 Python 套件:
✅ pytubefix 10.0.0
✅ Flask 3.1.0

==========================================
環境檢查完成
==========================================

[INFO] Starting gunicorn 23.0.0
[INFO] Listening at: http://0.0.0.0:8080
```

### 3. 測試音訊下載

**測試 URL**: 任何 YouTube 短影片 (< 5 分鐘)

**預期日誌**:
```
✅ 下載完成: test_video.m4a
🔄 音訊模式 - 開始轉換為 MP3...
🎵 開始轉換為 MP3: test_video.m4a
✅ FFmpeg 可用               ← 這行必須出現!
🔄 執行轉換命令...
✅ MP3 轉換完成!
   原始大小: 4.12 MB
   MP3 大小: 5.82 MB
✅ MP3 轉換成功!
```

---

## 🐛 如果 FFmpeg 仍然安裝失敗

### 選項 1: 強制使用 Dockerfile

1. **確認 Dockerfile 存在**:
   ```bash
   git add Dockerfile
   git commit -m "使用 Dockerfile 建置"
   git push origin main
   ```

2. **在 Railway 中確認**:
   - Settings → Build → 確認使用 Dockerfile
   - 或刪除 `nixpacks.toml` 強制使用 Dockerfile

### 選項 2: 接受 m4a 格式

如果 FFmpeg 真的無法安裝:

1. **修改前端說明**:
   - 告知使用者音訊格式為 m4a
   - m4a 也是高品質音訊格式 (AAC 編碼)
   - 大部分播放器都支援 m4a

2. **移除轉換邏輯** (可選):
   ```python
   # 註解掉 MP3 轉換
   # if download_type == 'audio':
   #     file_path = convert_to_mp3(file_path)
   ```

### 選項 3: 聯絡 Railway 支援

如果以上方法都失敗:

1. **提交 Railway 支援票證**:
   - 說明 FFmpeg 安裝問題
   - 提供建置日誌
   - 詢問是否有系統限制

2. **考慮其他平台**:
   - Render.com (免費方案支援 Dockerfile)
   - Fly.io (免費額度,完整 Docker 支援)
   - Heroku (付費,穩定)

---

## 📋 部署檢查清單

### 部署前
- [x] `nixpacks.toml` 包含 `apt-get install ffmpeg`
- [x] `Dockerfile` 已創建 (備援)
- [x] `start.sh` 有啟動時 FFmpeg 檢查
- [x] `start.sh` 有執行權限
- [x] 所有檔案已推送到 GitHub

### 部署後
- [ ] 檢查建置日誌是否有 "Installing ffmpeg"
- [ ] 檢查建置日誌是否有 "ffmpeg version"
- [ ] 檢查啟動日誌是否有 "✅ FFmpeg 已安裝"
- [ ] 測試音訊下載
- [ ] 確認下載的檔案為 .mp3 格式

### 如果失敗
- [ ] 截圖建置日誌 (完整的)
- [ ] 截圖啟動日誌 (包含 FFmpeg 檢查部分)
- [ ] 檢查 Railway 是否使用 Dockerfile 建置
- [ ] 嘗試手動重新部署

---

## 🎯 當前狀態

**Git 提交**: f0ae969  
**修改內容**:
- ✅ `nixpacks.toml` - apt-get 直接安裝
- ✅ `start.sh` - 啟動時嘗試安裝
- ✅ `Dockerfile` - 備援方案

**部署狀態**: 🔄 Railway 自動部署中

**下一步**: 
1. 等待 Railway 部署完成 (3-5 分鐘)
2. 檢查建置日誌
3. 測試音訊下載
4. 如果仍失敗,提供日誌截圖

---

## 💡 臨時解決方案

如果您急需使用,可以:

1. **接受 m4a 格式**:
   - m4a 音質優秀 (AAC 編碼)
   - VLC, iTunes, Windows Media Player 都支援
   - 檔案更小 (相較於 MP3)

2. **本地轉換**:
   - 下載 m4a 後
   - 使用線上轉換器 (如 CloudConvert)
   - 或本地 FFmpeg 轉換

3. **本地運行**:
   - 在您的電腦上運行 `app_pytubefix.py`
   - 本地有 FFmpeg,轉換會成功
   - 使用 `python app_pytubefix.py` 啟動

---

**建立時間**: 2025-10-09  
**最後嘗試**: 3 種不同的 FFmpeg 安裝方法  
**當前希望**: Dockerfile 方案應該會成功 🤞
