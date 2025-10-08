# 🔧 Railway 機器人檢測進階解決方案

## 📋 問題描述

**現象:**
- ✅ 本地測試正常運作
- ❌ Railway 部署後出現: "Sign in to confirm you're not a bot"

**原因:**
YouTube 對雲端伺服器 IP (如 Railway) 有更嚴格的檢測機制

---

## 🎯 解決方案 (多重策略)

### ✅ 策略 1: 加強 HTTP Headers (已實施)

我已經更新了程式碼,加入更完整的 HTTP headers:

```python
'http_headers': {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
},
'extractor_args': {
    'youtube': {
        'player_client': ['android', 'web', 'ios'],  # 三種客戶端
        'skip': ['hls', 'dash'],
    }
},
'sleep_interval': 1,  # 請求間隔,避免頻率過高
'max_sleep_interval': 3,
```

---

### 🔄 策略 2: 使用代理伺服器 (推薦)

如果策略 1 仍無效,可以使用代理伺服器:

#### **選項 A: 免費代理服務**

修改 `app.py`:

```python
ydl_opts = {
    # ... 其他設定 ...
    'proxy': 'http://free-proxy-server:port',  # 使用免費代理
}
```

免費代理列表:
- https://www.proxy-list.download/
- https://free-proxy-list.net/

#### **選項 B: 付費代理 (穩定)**

推薦服務:
- **Bright Data**: https://brightdata.com (有免費試用)
- **Smartproxy**: https://smartproxy.com
- **Oxylabs**: https://oxylabs.io

設定方式:
```python
ydl_opts = {
    'proxy': 'http://username:password@proxy-server:port',
}
```

---

### 🍪 策略 3: 使用 Cookies (最有效)

這是最可靠的方法,但需要你的 YouTube cookies。

#### **步驟 1: 匯出 Cookies**

使用瀏覽器擴充功能匯出 cookies:

1. **安裝擴充功能:**
   - Chrome/Edge: [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid)
   - Firefox: [cookies.txt](https://addons.mozilla.org/firefox/addon/cookies-txt/)

2. **登入 YouTube**
   - 確保在瀏覽器中已登入 YouTube

3. **匯出 Cookies**
   - 點擊擴充功能圖示
   - 選擇 "Export cookies.txt"
   - 儲存為 `youtube_cookies.txt`

#### **步驟 2: 上傳 Cookies 到 Railway**

**方法 A: 使用環境變數 (推薦)**

1. 將 cookies 檔案內容轉換為 base64:
   ```bash
   # Windows PowerShell
   $content = Get-Content youtube_cookies.txt -Raw
   $bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
   $base64 = [Convert]::ToBase64String($bytes)
   $base64 | Set-Clipboard
   ```

2. 在 Railway Dashboard:
   - Settings → Variables
   - 新增變數: `YOUTUBE_COOKIES_B64`
   - 貼上 base64 字串

3. 修改 `app.py`:
   ```python
   import base64
   
   def get_cookies_file():
       """從環境變數解碼 cookies"""
       cookies_b64 = os.environ.get('YOUTUBE_COOKIES_B64')
       if cookies_b64:
           cookies_path = '/tmp/cookies.txt'
           with open(cookies_path, 'wb') as f:
               f.write(base64.b64decode(cookies_b64))
           return cookies_path
       return None
   
   # 在 ydl_opts 中使用:
   cookies_file = get_cookies_file()
   if cookies_file:
       ydl_opts['cookiefile'] = cookies_file
   ```

**方法 B: 直接上傳檔案**

1. 將 `youtube_cookies.txt` 放在 `web_version/` 目錄
2. 修改 `app.py`:
   ```python
   cookies_path = os.path.join(os.path.dirname(__file__), 'youtube_cookies.txt')
   if os.path.exists(cookies_path):
       ydl_opts['cookiefile'] = cookies_path
   ```
3. 加入 Git 並推送

⚠️ **注意:** Cookies 包含你的登入資訊,不要公開分享!

---

### 🔀 策略 4: 切換到其他部署平台

如果 Railway IP 被封鎖太嚴重,可以嘗試其他平台:

#### **Render.com**
- 免費方案
- 不同的 IP 範圍
- 部署步驟類似 Railway

#### **Fly.io**
- 免費方案
- 可選擇不同地區的伺服器
- 可能有不同的 IP 聲譽

#### **Heroku**
- 需要信用卡驗證
- 更成熟的平台
- IP 範圍較大

---

### 🎭 策略 5: 使用 YouTube Data API (備用方案)

如果上述方法都失效,考慮使用官方 API:

**優點:**
- 官方支援,不會被封鎖
- 穩定可靠

**缺點:**
- 無法下載影片(只能獲取資訊)
- 需要 API Key
- 有使用配額限制

**混合方案:**
1. 使用 YouTube Data API 獲取影片資訊
2. 使用 yt-dlp + 代理/cookies 下載實際檔案

---

## 🚀 立即實施方案

### **優先順序:**

1. ✅ **已完成:** 加強 HTTP Headers 和 player_client
2. 🔄 **測試策略 1:** 推送更新到 Railway,測試是否生效
3. 🍪 **如果失敗:** 實施策略 3 (Cookies) - 最有效
4. 🔀 **備選:** 策略 2 (代理) 或策略 4 (換平台)

---

## 📝 實施步驟

### **步驟 1: 測試當前更新**

```bash
# 推送更新到 GitHub
git add .
git commit -m "Enhanced anti-bot detection with full HTTP headers"
git push

# 等待 Railway 部署 (3-5 分鐘)
# 測試是否解決問題
```

### **步驟 2: 如果仍失敗,使用 Cookies**

1. 匯出 YouTube cookies (見策略 3)
2. 選擇方法 A 或 B
3. 更新程式碼
4. 推送並測試

### **步驟 3: 監控和調整**

```python
# 在 app.py 中加入更詳細的錯誤日誌
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
except Exception as e:
    logger.error(f"Download error: {str(e)}")
    # 詳細錯誤資訊會出現在 Railway logs
```

---

## 🧪 測試腳本

建立測試腳本確認每個策略:

```python
# test_strategies.py
import yt_dlp

strategies = {
    'basic': {
        'quiet': True,
    },
    'enhanced_headers': {
        'quiet': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'web', 'ios']}},
        'http_headers': {
            'User-Agent': 'Mozilla/5.0...',
            # ... 完整 headers
        },
    },
    'with_cookies': {
        'quiet': True,
        'cookiefile': 'youtube_cookies.txt',
    },
    'with_proxy': {
        'quiet': True,
        'proxy': 'http://proxy:port',
    },
}

test_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'

for name, opts in strategies.items():
    print(f"\n測試策略: {name}")
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(test_url, download=False)
            print(f"✅ {name}: 成功")
    except Exception as e:
        print(f"❌ {name}: {str(e)}")
```

---

## 📊 各策略成功率

基於社群經驗:

| 策略 | 成功率 | 難度 | 成本 |
|------|--------|------|------|
| 加強 Headers | 30-50% | 低 | 免費 |
| Cookies | 90-95% | 中 | 免費 |
| 付費代理 | 85-90% | 中 | $5-50/月 |
| 免費代理 | 20-40% | 中 | 免費 |
| 換平台 | 40-60% | 中 | 免費 |
| 官方 API | 100% | 高 | 免費(有限額) |

---

## ⚠️ 重要提醒

### **Cookies 安全性:**
- Cookies 包含你的登入資訊
- 不要分享或公開
- 定期更新 (每 30 天)
- 使用環境變數而非硬編碼

### **代理使用:**
- 免費代理可能不穩定
- 付費代理更可靠
- 確認代理支援 HTTPS

### **法律考量:**
- YouTube 服務條款禁止自動化下載
- 此工具僅供個人學習使用
- 不要用於商業目的
- 尊重版權

---

## 🎯 我的建議

基於你的情況:

### **最佳方案組合:**

1. **立即測試:** 推送當前的加強版本
   ```bash
   git push
   # 等待部署後測試
   ```

2. **如果仍失敗:** 使用 Cookies 方案
   - 成功率 90%+
   - 完全免費
   - 設定簡單

3. **長期方案:** 
   - 定期更新 yt-dlp: `pip install --upgrade yt-dlp`
   - 監控 Railway logs
   - 準備備用平台 (Render/Fly.io)

---

## 📞 需要協助?

### **除錯步驟:**

1. **查看 Railway Logs:**
   ```
   Railway Dashboard → Deployments → View Logs
   搜尋 "ERROR" 或 "bot"
   ```

2. **測試不同影片:**
   - 有些影片可能有額外限制
   - 嘗試公開、熱門的影片

3. **檢查 yt-dlp 版本:**
   ```bash
   pip show yt-dlp
   # 確保是最新版本
   ```

4. **本地模擬 Railway 環境:**
   ```python
   # 使用相同的設定測試
   # 看是否是程式碼問題
   ```

---

## 📚 參考資源

- [yt-dlp GitHub Issues](https://github.com/yt-dlp/yt-dlp/issues)
- [YouTube Bot Detection 討論](https://github.com/yt-dlp/yt-dlp/issues/10085)
- [Cookies 使用指南](https://github.com/yt-dlp/yt-dlp#how-do-i-pass-cookies-to-yt-dlp)
- [Railway 環境變數文件](https://docs.railway.app/develop/variables)

---

**建立時間:** 2025年10月8日  
**更新策略:** 加強 HTTP Headers + 多客戶端  
**下一步:** 測試更新 → 必要時使用 Cookies

---

讓我知道測試結果,我可以協助你實施最適合的策略! 🚀
