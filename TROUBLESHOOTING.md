# 🔧 常見問題與解決方案

## ❌ 錯誤：Sign in to confirm you're not a bot

### 問題描述
```
ERROR: [youtube] xxxxx: Sign in to confirm you're not a bot. 
This helps protect our community.
```

### 原因
YouTube 偵測到來自伺服器的請求，認為可能是機器人。

### 解決方案

#### ✅ 方案 1: 更新 yt-dlp 設定（已修復）

我已經在 `app.py` 中加入以下設定：

```python
ydl_opts = {
    # ... 其他設定
    'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
    'user_agent': 'Mozilla/5.0 ...',
}
```

**部署更新**：
```bash
git add .
git commit -m "Fix YouTube bot detection"
git push
```

Railway 會自動重新部署。

#### ✅ 方案 2: 使用 Cookies（更穩定）

如果問題持續，可以使用 YouTube Cookies：

1. **匯出 Cookies**
   - 安裝瀏覽器擴充：[Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt)
   - 登入 YouTube
   - 點擊擴充圖示，下載 `cookies.txt`

2. **上傳到 Railway**
   - 在 Railway Dashboard 上傳 `cookies.txt` 到專案根目錄
   - 或將內容加入環境變數

3. **修改程式碼**
   ```python
   ydl_opts = {
       # ... 其他設定
       'cookiefile': 'cookies.txt',  # 加入這行
   }
   ```

#### ✅ 方案 3: 使用代理伺服器

```python
ydl_opts = {
    # ... 其他設定
    'proxy': 'http://proxy-server:port',
}
```

#### ✅ 方案 4: 更新 yt-dlp

確保使用最新版本：
```bash
pip install --upgrade yt-dlp
```

---

## ❌ 錯誤：音訊下載失敗

### 問題
```
ERROR: Postprocessing: ffprobe and ffmpeg not found
```

### 解決方案

確認 `Aptfile` 存在且包含：
```
ffmpeg
```

重新部署後，Railway 會自動安裝 FFmpeg。

---

## ❌ 錯誤：檔案下載超時

### 問題
下載大檔案時超時。

### 解決方案

1. **增加逾時設定**
   ```python
   ydl_opts = {
       # ... 其他設定
       'socket_timeout': 300,  # 5分鐘
   }
   ```

2. **限制檔案大小**
   ```python
   ydl_opts = {
       # ... 其他設定
       'max_filesize': 500 * 1024 * 1024,  # 500MB
   }
   ```

---

## ❌ 錯誤：Railway 部署失敗

### 問題 1: Python 版本不符

**解決**：檢查 `runtime.txt`
```
python-3.11.0
```

### 問題 2: 相依套件安裝失敗

**解決**：清除快取重新部署
```bash
# 在 Railway Dashboard
Settings → 點擊 "Clear Build Cache" → Redeploy
```

### 問題 3: 找不到 Procfile

**解決**：確認 `Procfile` 內容
```
web: gunicorn app:app
```

---

## ❌ 錯誤：下載後無法播放

### 問題
下載的檔案無法播放。

### 原因
可能是格式轉換失敗。

### 解決方案

1. **檢查 FFmpeg**
   確認 FFmpeg 已安裝

2. **使用相容格式**
   ```python
   # 音訊
   'preferredcodec': 'mp3',  # 改為 m4a 或 aac
   
   # 影片
   'format': 'best[ext=mp4]',  # 指定 mp4 格式
   ```

---

## ❌ 錯誤：記憶體不足

### 問題
```
MemoryError or Process killed
```

### 原因
Railway 免費方案記憶體限制（512MB）

### 解決方案

1. **限制同時下載數**
   ```python
   # 加入全域鎖定
   import threading
   download_lock = threading.Semaphore(2)  # 最多同時2個下載
   ```

2. **清理暫存檔**
   ```python
   # 下載完立即刪除
   os.remove(file_path)
   ```

3. **升級方案**
   - Railway Pro: $20/月，2GB RAM

---

## ❌ PWA 無法安裝

### 問題
手機上沒有「安裝」按鈕。

### 原因
- 沒有使用 HTTPS
- Service Worker 未註冊
- manifest.json 錯誤

### 解決方案

1. **檢查 HTTPS**
   - Railway 自動提供 HTTPS ✅
   - 自訂網域需手動設定

2. **檢查 Service Worker**
   - 開啟瀏覽器開發者工具
   - Application → Service Workers
   - 確認已註冊

3. **檢查 Manifest**
   - Network 標籤查看 `manifest.json` 是否載入
   - 檢查路徑是否正確

---

## 💡 效能優化建議

### 1. 使用 Redis 快取

```python
import redis
r = redis.Redis(host='localhost', port=6379)

# 快取影片資訊
@app.route('/api/info', methods=['POST'])
def get_video_info():
    url = request.json.get('url')
    cached = r.get(url)
    if cached:
        return jsonify(json.loads(cached))
    # ... 取得資訊
    r.setex(url, 3600, json.dumps(info))  # 快取1小時
```

### 2. 背景任務佇列

使用 Celery 處理下載：
```python
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task
def download_task(task_id, url, download_type, quality):
    # 下載邏輯
    pass
```

### 3. CDN 加速

使用 Cloudflare 加速靜態資源：
- 註冊 Cloudflare
- 設定 DNS
- 開啟 CDN

---

## 🐛 除錯技巧

### 查看 Railway 日誌

1. 進入專案 Dashboard
2. 點擊 "Deployments"
3. 點擊最新的部署
4. 查看 "Logs"

### 本地測試

```bash
# 啟動本地伺服器
python app.py

# 測試 API
curl -X POST http://localhost:5000/api/download \
  -H "Content-Type: application/json" \
  -d '{"url":"https://youtube.com/watch?v=xxx","type":"video","quality":"720p"}'
```

### 測試 yt-dlp

```bash
# 直接測試 yt-dlp
yt-dlp --user-agent "Mozilla/5.0..." --extractor-args "youtube:player_client=android,web" "https://youtube.com/watch?v=xxx"
```

---

## 📞 仍有問題？

### 檢查清單

- [ ] yt-dlp 已更新到最新版本
- [ ] `extractor_args` 已加入
- [ ] FFmpeg 已安裝（Aptfile）
- [ ] Railway 日誌無錯誤
- [ ] 本地測試正常
- [ ] 網址格式正確

### 聯絡支援

1. **yt-dlp 問題**
   - GitHub: https://github.com/yt-dlp/yt-dlp/issues
   - 附上完整錯誤訊息

2. **Railway 問題**
   - Discord: https://discord.gg/railway
   - 文件: https://docs.railway.app

3. **本專案問題**
   - 檢查日誌
   - 嘗試本地重現

---

## 🔄 快速修復流程

```bash
# 1. 更新程式碼
git pull

# 2. 測試本地
python app.py

# 3. 推送更新
git add .
git commit -m "Fix: YouTube bot detection"
git push

# 4. 等待 Railway 自動部署（約 2-3 分鐘）

# 5. 測試線上版本
curl https://your-app.railway.app/api/info -X POST -H "Content-Type: application/json" -d '{"url":"測試網址"}'
```

---

**最後更新**: 2025年10月8日

如果以上方案都無法解決，可能是 YouTube 臨時加強了防護，建議：
1. 等待 yt-dlp 官方更新
2. 考慮使用其他影片來源
3. 使用本地桌面版（不受影響）
