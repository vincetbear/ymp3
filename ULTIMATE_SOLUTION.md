# YouTube 下載器 - 終極解決方案

## 問題現狀

經過多次嘗試,我們遇到以下問題:

1. **yt-dlp 直接連線** → YouTube bot 偵測,要求登入
2. **iOS/Android 客戶端模擬** → Railway IP 被封鎖
3. **Invidious API** → 公開實例不穩定 (401, 502, 連線中斷)

## 解決方案

### 方案 A: 使用代理服務 ⭐ (推薦)

使用代理輪換服務繞過 IP 封鎖:

```python
# 免費代理池
PROXY_LIST = [
    'socks5://proxy1.example.com:1080',
    'socks5://proxy2.example.com:1080',
    # ...
]

ydl_opts['proxy'] = random.choice(PROXY_LIST)
```

**優點:**
- ✅ 完整支援所有 YouTube 功能
- ✅ 不依賴第三方 API
- ✅ 可轉換 MP3

**缺點:**
- ❌ 需要付費代理服務 (免費代理不可靠)
- ❌ 增加延遲

**推薦服務:**
- [Bright Data](https://brightdata.com/) - $500/月起
- [Oxylabs](https://oxylabs.io/) - $300/月起
- [Smartproxy](https://smartproxy.com/) - $75/月起

### 方案 B: 使用無伺服器函數

在不同的雲端平台運行下載邏輯,避免 IP 被封鎖:

1. **Vercel Edge Functions** - 分散式 IP
2. **Cloudflare Workers** - 全球 CDN IP
3. **AWS Lambda** - 定期輪換 IP

### 方案 C: 降級方案 - 只提供影片資訊

如果下載功能無法實現,至少提供:

```
1. 影片標題
2. 縮圖
3. 播放器嵌入
4. YouTube 直接連結
```

使用者點擊後在新視窗開啟 YouTube,自行下載。

### 方案 D: 桌面版解決方案

**放棄 Web 版**,專注於桌面版:

- ✅ 桌面版運行在使用者本機,不受 IP 封鎖
- ✅ 可以使用使用者的 YouTube cookies
- ✅ 功能完整,不受限制

**建議:** 將桌面版 `.exe` 上傳到 GitHub Releases,提供下載

### 方案 E: 合作使用者本機代理

Web 介面 → 使用者本機安裝代理程式 → 透過使用者 IP 下載

類似 BitTorrent 的 P2P 架構。

## 立即可行的方案

考慮到成本和技術可行性,建議:

### 選項 1: 桌面版 + Web 版混合

1. **Web 版:** 提供影片資訊、播放器嵌入
2. **桌面版:** 提供完整下載功能
3. Web 上顯示「下載桌面版以獲得完整功能」

### 選項 2: 等待 Invidious 恢復

某些 Invidious 實例可能會恢復,可以:

1. 定期檢查實例狀態
2. 自動切換到可用實例
3. 當無可用實例時顯示友善錯誤訊息

### 選項 3: 付費代理 (企業方案)

如果這是商業項目,投資代理服務:

```bash
# 每月約 $75-100 USD
# 可處理 10,000+ 次下載
```

## 下一步

請選擇您偏好的方案:

A. 投資付費代理服務 (立即可用,但需成本)
B. 改用桌面版 + Web版提供資訊 (免費,但功能受限)
C. 等待 Invidious 恢復 (不確定性高)
D. 其他建議?
