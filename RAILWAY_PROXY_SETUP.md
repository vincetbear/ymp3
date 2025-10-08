# Railway 環境變數設定指南

## 🚀 立即設定 (3 分鐘完成)

### 步驟 1: 登入 Railway

1. 前往 https://railway.app/
2. 登入您的帳號
3. 選擇您的專案 (ymp3)

### 步驟 2: 設定環境變數

1. 點擊專案
2. 選擇 "Variables" 標籤
3. 點擊 "Add Variable" 或 "+ New Variable"

### 步驟 3: 新增代理設定

**變數名稱:** `PROXY_URL`

**變數值:**
```
http://vincetbear@gmail.com:2Giiiali@proxy.webshare.io:80
```

> ⚠️ **重要:** 貼上時請確保格式正確,沒有多餘的空格

### 步驟 4: 儲存並重新部署

1. 點擊 "Add" 或 "Save"
2. Railway 會自動重新部署
3. 等待 3-5 分鐘

---

## ✅ 驗證設定

### 部署完成後,檢查日誌:

1. 在 Railway Dashboard 點擊 "Deployments"
2. 選擇最新的部署
3. 查看 "Logs"

**應該看到:**
```
🔒 使用代理伺服器: proxy.webshare.io:80
```

**如果看到:**
```
⚠️ 未設定代理,可能會遇到 YouTube bot 偵測
```
表示環境變數沒有正確設定。

---

## 🧪 測試下載

部署完成後,測試一個影片:

1. 開啟您的 Railway URL
2. 貼上測試影片: `https://www.youtube.com/watch?v=fLyHit9OnhU`
3. 選擇 "音訊" 或 "影片"
4. 點擊下載

**預期結果:**
- ✅ 成功獲取影片資訊
- ✅ 開始下載
- ✅ 下載完成

**如果失敗:**
- 檢查 Railway Logs 確認代理是否正確設定
- 確認 WebShare 帳號是否啟用
- 確認代理憑證是否正確

---

## 📊 完整的環境變數列表

您的 Railway 專案應該有以下環境變數:

```
PROXY_URL=http://vincetbear@gmail.com:2Giiiali@proxy.webshare.io:80
```

其他舊的環境變數可以刪除:
- ❌ `YOUTUBE_COOKIES_B64` (不再需要)

---

## 🔧 故障排除

### 問題 1: 仍然出現 "Sign in to confirm you're not a bot"

**解決方案:**
1. 確認環境變數名稱完全正確: `PROXY_URL` (大寫)
2. 確認代理格式: `http://用戶名:密碼@伺服器:埠號`
3. 檢查 WebShare 帳號是否啟用

### 問題 2: "Connection refused" 或 "Proxy error"

**解決方案:**
1. 檢查 WebShare 帳號狀態
2. 確認密碼沒有特殊字元問題
3. 嘗試使用其他 WebShare 代理埠 (如 1080 for SOCKS5)

### 問題 3: 下載很慢

**原因:**
- 代理伺服器會增加一些延遲 (正常)

**改善:**
- 升級 WebShare 方案獲得更快的代理
- 或使用更接近 Railway 伺服器的代理位置

---

## 📈 監控使用量

### 在 WebShare Dashboard:

1. 登入 https://www.webshare.io/
2. 前往 Dashboard
3. 查看 "Bandwidth Usage"

**Starter Plan ($2.99/月):**
- 10 個代理
- 無限頻寬
- 適合個人使用 (每天 < 100 次下載)

---

## 🎉 完成!

設定完成後,您的 YouTube 下載器就能:

- ✅ 成功繞過 YouTube bot 偵測
- ✅ 下載影片和音訊
- ✅ 支援多種品質選擇
- ✅ 在手機和電腦上使用

**下一步:**
- 測試幾個影片確認一切正常
- 分享給朋友使用! 🚀
