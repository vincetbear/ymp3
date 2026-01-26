# 🔧 FFmpeg 安裝問題修復

## ❌ 問題診斷

### 錯誤訊息
```
❌ 錯誤: 找不到 FFmpeg
⚠️ 警告: 轉換失敗,返回原始檔案 .m4a
```

### 根本原因
Railway 使用 **Nixpacks** 建置系統時:
1. ❌ `Aptfile` 被忽略 (Nixpacks 不讀取 Aptfile)
2. ❌ `nixPkgs = ["ffmpeg-full"]` 在 Nix 套件庫中可能不存在或版本不相容
3. ❌ FFmpeg 未正確安裝到系統中

---

## ✅ 解決方案

### 修復 1: 使用 `aptPkgs` 而非 `nixPkgs`

**檔案**: `nixpacks.toml`

**修改前** (錯誤):
```toml
[phases.setup]
nixPkgs = ["python39", "ffmpeg-full"]
```

**修改後** (正確):
```toml
[phases.setup]
nixPkgs = ["python39"]
aptPkgs = ["ffmpeg"]  # ✅ 使用 apt 安裝 FFmpeg
```

**原因**:
- `aptPkgs` 使用 Ubuntu 的 apt 套件管理器
- `ffmpeg` 在 Ubuntu apt 中是標準套件,穩定可靠
- `nixPkgs` 中的 `ffmpeg-full` 可能不存在或有相依性問題

### 修復 2: 刪除 `Aptfile`

**原因**: Nixpacks 不讀取 `Aptfile`,改用 `nixpacks.toml` 的 `aptPkgs`

**操作**:
```bash
git rm Aptfile
```

### 修復 3: 增加安裝驗證

**檔案**: `nixpacks.toml`

```toml
[phases.install]
cmds = [
    "pip install -r requirements.txt",
    "ffmpeg -version || echo 'WARNING: FFmpeg not found!'",  # ✅ 驗證安裝
    "chmod +x start.sh"
]
```

**功能**: 建置時檢查 FFmpeg 是否成功安裝

### 修復 4: 創建啟動檢查腳本

**新檔案**: `start.sh`

```bash
#!/bin/bash
# Railway 啟動前檢查腳本

echo "=========================================="
echo "Railway 環境檢查"
echo "=========================================="

# 檢查 FFmpeg
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg 已安裝"
    ffmpeg -version | head -n 1
else
    echo "❌ 錯誤: 找不到 FFmpeg!"
    exit 1
fi

# 啟動 Gunicorn
exec gunicorn app_pytubefix:app --bind 0.0.0.0:$PORT --workers 2 --timeout 300
```

**功能**:
- 啟動前驗證 FFmpeg
- 如果 FFmpeg 不存在,立即失敗並顯示錯誤
- 設定 timeout 為 300 秒 (5 分鐘,支援長影片轉換)

### 修復 5: 更新啟動命令

**檔案**: `nixpacks.toml`

**修改前**:
```toml
[start]
cmd = "gunicorn app_pytubefix:app --bind 0.0.0.0:$PORT"
```

**修改後**:
```toml
[start]
cmd = "./start.sh"
```

---

## 📋 完整配置

### `nixpacks.toml` (最終版本)
```toml
[phases.setup]
nixPkgs = ["python39"]
aptPkgs = ["ffmpeg"]

[phases.install]
cmds = [
    "pip install -r requirements.txt",
    "ffmpeg -version || echo 'WARNING: FFmpeg not found!'",
    "chmod +x start.sh"
]

[start]
cmd = "./start.sh"
```

### `start.sh` (新增)
```bash
#!/bin/bash
echo "Railway 環境檢查"
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg 已安裝"
    ffmpeg -version | head -n 1
else
    echo "❌ 錯誤: 找不到 FFmpeg!"
    exit 1
fi
exec gunicorn app_pytubefix:app --bind 0.0.0.0:$PORT --workers 2 --timeout 300
```

---

## 🚀 部署步驟

### Git 提交
```bash
git rm Aptfile
git add nixpacks.toml start.sh
git commit -m "🔧 修復 FFmpeg 安裝 - 使用 aptPkgs + 啟動檢查腳本"
git push origin main
```

**狀態**: ✅ 已推送 (Commit: 8c0f60e)

### Railway 自動部署
Railway 會自動偵測更新並重新部署

---

## 📊 預期日誌輸出

### 建置階段 (Install Phase)
```
Installing packages with apt...
  ffmpeg
✅ ffmpeg is already the newest version
```

```
Verifying FFmpeg installation...
ffmpeg version 4.x.x
✅ FFmpeg verification passed
```

### 啟動階段 (Start)
```
==========================================
Railway 環境檢查
==========================================
Python 版本:
Python 3.9.x

檢查 FFmpeg:
✅ FFmpeg 已安裝
ffmpeg version 4.4.x Copyright (c) 2000-2021 the FFmpeg developers

檢查 Python 套件:
✅ pytubefix 10.0.0
✅ Flask 3.1.0

==========================================
環境檢查完成
==========================================

[INFO] Starting gunicorn 23.0.0
[INFO] Listening at: http://0.0.0.0:8080
[INFO] Using worker: sync
[INFO] Booting worker with pid: X
```

### 音訊下載時
```
✅ 下載完成: xxx.m4a
🔄 音訊模式 - 開始轉換為 MP3...
🎵 開始轉換為 MP3: xxx.m4a
✅ FFmpeg 可用                    # ← 這行應該出現!
🔄 執行轉換命令...
✅ MP3 轉換完成!
   原始大小: 4.12 MB
   MP3 大小: 5.82 MB
✅ MP3 轉換成功!
```

---

## 🧪 測試步驟

### 1. 等待 Railway 部署完成
- 前往 Railway Dashboard
- 查看 Deployments 標籤
- 等待狀態變為 "Active"

### 2. 檢查部署日誌

**查找關鍵字**:
```
✅ FFmpeg 已安裝
Railway 環境檢查完成
Starting gunicorn
```

**如果看到**:
- ✅ `✅ FFmpeg 已安裝` → FFmpeg 安裝成功
- ❌ `❌ 錯誤: 找不到 FFmpeg!` → 安裝失敗,繼續排查

### 3. 測試音訊下載

1. 清除瀏覽器快取 (`Ctrl + Shift + R`)
2. 貼上 YouTube 網址
3. 選擇「🎵 音訊」模式
4. 點擊「開始下載」
5. 等待進度到 100%
6. 檢查日誌是否有:
   ```
   ✅ FFmpeg 可用
   ✅ MP3 轉換完成!
   ```
7. 點擊「📥 下載檔案」
8. **檢查下載的檔案格式**:
   - ✅ 應該是 `.mp3` 格式
   - ✅ 檔案大小約 5-6 MB (4 分鐘影片)
   - ✅ 音質 192 kbps

---

## 🐛 疑難排解

### 問題 1: 建置時仍找不到 FFmpeg

**檢查**: Railway 建置日誌中是否有:
```
Installing packages with apt...
  ffmpeg
```

**解決方案**:
1. 確認 `nixpacks.toml` 包含 `aptPkgs = ["ffmpeg"]`
2. 確認檔案已推送到 GitHub
3. 在 Railway 觸發手動重新部署:
   - Settings → Deployments → Redeploy

### 問題 2: 啟動時 FFmpeg 檢查失敗

**症狀**: 日誌顯示:
```
❌ 錯誤: 找不到 FFmpeg!
Worker failed to boot
```

**檢查**:
1. 確認 `start.sh` 有執行權限:
   ```bash
   chmod +x start.sh
   ```
2. 確認 `nixpacks.toml` 的 install 階段包含:
   ```toml
   "chmod +x start.sh"
   ```

**臨時解決**:
如果 `start.sh` 失敗,可以暫時改回直接啟動:
```toml
[start]
cmd = "gunicorn app_pytubefix:app --bind 0.0.0.0:$PORT --timeout 300"
```

### 問題 3: 轉換超時

**症狀**: 日誌顯示:
```
❌ MP3 轉換超時 (5 分鐘)
```

**解決方案**:
1. 確認 `start.sh` 中的 `--timeout 300` 已設定
2. 或在 `nixpacks.toml` 中直接設定:
   ```toml
   cmd = "gunicorn app_pytubefix:app --timeout 600"  # 10 分鐘
   ```

---

## 📈 改進總結

| 項目 | 修改前 | 修改後 |
|------|--------|--------|
| **FFmpeg 安裝方式** | `nixPkgs = ["ffmpeg-full"]` ❌ | `aptPkgs = ["ffmpeg"]` ✅ |
| **Aptfile** | 存在但被忽略 ❌ | 刪除 ✅ |
| **安裝驗證** | 無 ❌ | `ffmpeg -version` ✅ |
| **啟動檢查** | 無 ❌ | `start.sh` 腳本 ✅ |
| **Gunicorn 超時** | 預設 30 秒 ❌ | 300 秒 (5 分鐘) ✅ |
| **Worker 數量** | 預設 1 個 | 2 個 ✅ |

---

## 🎯 預期結果

### 成功標誌

1. **Railway 建置日誌**:
   ```
   Installing packages with apt...
   ✅ ffmpeg installed
   ```

2. **Railway 啟動日誌**:
   ```
   ✅ FFmpeg 已安裝
   ffmpeg version 4.4.x
   環境檢查完成
   ```

3. **音訊下載日誌**:
   ```
   ✅ FFmpeg 可用
   ✅ MP3 轉換完成!
   ```

4. **下載的檔案**:
   - 格式: `.mp3` ✅
   - 音質: 192 kbps ✅
   - 大小: 合理 (約 1-2 MB/分鐘) ✅

---

## 📚 相關檔案

- ✅ `nixpacks.toml` - Railway 建置配置 (已更新)
- ✅ `start.sh` - 啟動檢查腳本 (新增)
- ✅ `app_pytubefix.py` - Flask 主應用 (MP3 轉換邏輯)
- ❌ `Aptfile` - 已刪除 (改用 aptPkgs)

---

**修復時間**: 2025-10-09  
**提交**: 8c0f60e  
**狀態**: ✅ 已推送,等待 Railway 重新部署  
**預期**: FFmpeg 正確安裝,MP3 轉換成功 🎵
