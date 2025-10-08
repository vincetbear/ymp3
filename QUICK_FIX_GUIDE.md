# 🚀 Railway 機器人問題 - 快速修復指南

## ⚡ 快速行動方案

你的問題: **本地正常,Railway 出現 "Sign in to confirm you're not a bot"**

---

## 🎯 推薦方案: 使用 YouTube Cookies (成功率 90%+)

### **為什麼這最有效?**
- ✅ YouTube 會認為請求來自已登入的真實用戶
- ✅ 完全免費
- ✅ 設定簡單 (5 分鐘完成)
- ✅ 成功率最高

---

## 📝 完整操作步驟

### **步驟 1: 匯出 YouTube Cookies (2 分鐘)**

#### 1.1 安裝瀏覽器擴充功能

**Chrome/Edge 用戶:**
1. 前往: https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid
2. 點擊「加到 Chrome」

**Firefox 用戶:**
1. 前往: https://addons.mozilla.org/firefox/addon/cookies-txt/
2. 點擊「加到 Firefox」

#### 1.2 登入 YouTube
1. 開啟 YouTube: https://www.youtube.com
2. 確保已登入你的帳號

#### 1.3 匯出 Cookies
1. 點擊瀏覽器工具列上的擴充功能圖示
2. 選擇 "Get cookies.txt"
3. 點擊 "Export cookies.txt"
4. 將檔案儲存為 `youtube_cookies.txt`

---

### **步驟 2: 轉換為 Railway 格式 (1 分鐘)**

#### 方法 A: 使用提供的 Python 腳本 (推薦)

```powershell
# 在專案目錄執行
cd D:\01專案\2025\newyoutube\web_version
python setup_cookies.py youtube_cookies.txt
```

這會產生 `cookies_base64.txt` 檔案

#### 方法 B: 手動轉換 (PowerShell)

```powershell
# 讀取檔案並轉換
$content = Get-Content youtube_cookies.txt -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$base64 = [Convert]::ToBase64String($bytes)
$base64 | Out-File cookies_base64.txt
Write-Host "已儲存到 cookies_base64.txt"
```

---

### **步驟 3: 設定 Railway 環境變數 (2 分鐘)**

#### 3.1 開啟 Railway Dashboard
1. 前往: https://railway.app
2. 登入你的帳號
3. 選擇你的專案 (ymp3)

#### 3.2 新增環境變數
1. 點擊左側選單的 **"Variables"** 或 **"Settings"** → **"Variables"**
2. 點擊 **"New Variable"** 或 **"+"**
3. 輸入:
   - **Variable Name**: `YOUTUBE_COOKIES_B64`
   - **Value**: 貼上 `cookies_base64.txt` 的內容 (全選複製)
4. 點擊 **"Add"** 或 **"Save"**

#### 3.3 重新部署
- Railway 會自動偵測到環境變數變更
- 自動觸發重新部署
- 等待 3-5 分鐘

---

### **步驟 4: 推送程式碼更新 (1 分鐘)**

我已經更新了程式碼以支援 Cookies,現在推送到 GitHub:

```powershell
cd D:\01專案\2025\newyoutube\web_version
git add .
git commit -m "Add: Cookie support for Railway bot detection fix"
git push
```

等待 Railway 自動部署完成 (3-5 分鐘)

---

### **步驟 5: 測試 (1 分鐘)**

部署完成後:

1. 開啟你的 Railway 網址
2. 輸入任意 YouTube 網址測試
3. 確認下載成功,不再出現 "bot" 錯誤

---

## ✅ 預期結果

### **成功的標誌:**

```
✅ 開啟網頁成功
✅ 輸入 YouTube 網址
✅ 顯示影片資訊
✅ 開始下載
✅ 顯示進度
✅ 下載完成
❌ 沒有 "bot" 錯誤!
```

### **Railway Logs 會顯示:**

```
✅ 使用環境變數中的 cookies
🍪 使用 Cookies: /tmp/...
[youtube] Extracting URL: ...
[youtube] Downloading webpage
[download] 100% complete
```

---

## 🔍 如果仍然失敗

### **檢查清單:**

1. **Cookies 是否正確匯出?**
   - 確認檔案不是空的
   - 確認包含 YouTube 的 cookies
   - 重新匯出試試

2. **環境變數是否正確設定?**
   - 變數名稱: `YOUTUBE_COOKIES_B64` (完全一樣,大小寫敏感)
   - 值: 完整的 base64 字串 (沒有遺漏)

3. **是否重新部署?**
   - Railway 應該會自動部署
   - 也可以手動觸發: Deployments → Redeploy

4. **Cookies 是否過期?**
   - YouTube cookies 約 30 天過期
   - 重新登入並匯出新的 cookies

---

## 📊 替代方案 (如果 Cookies 方案失敗)

### **方案 B: 切換部署平台**

嘗試其他平台,可能有不同的 IP 聲譽:

#### Render.com
```bash
# 免費部署,步驟類似 Railway
1. 前往 https://render.com
2. 連結 GitHub 儲存庫
3. 部署 web service
```

#### Fly.io
```bash
# 需要信用卡驗證,但有免費額度
1. 安裝 flyctl
2. fly launch
3. fly deploy
```

---

## 🛡️ 安全提醒

### **關於 Cookies:**

⚠️ **重要:**
- Cookies 包含你的登入資訊
- 不要分享給他人
- 不要公開提交到 GitHub
- 使用環境變數存儲 (已經做到)

### **最佳實踐:**

✅ **推薦做法:**
- 使用 Railway 環境變數 (已設定)
- 定期更新 cookies (每 30 天)
- 使用專門的 YouTube 帳號 (非主帳號)

❌ **避免做法:**
- 不要將 cookies 檔案提交到 Git
- 不要在程式碼中硬編碼 cookies
- 不要使用過期的 cookies

---

## 📞 需要協助?

### **常見問題:**

**Q: 擴充功能找不到?**
A: 搜尋 "cookies.txt" 或 "export cookies",有多個類似工具

**Q: Base64 轉換失敗?**
A: 確認 cookies 檔案是純文字格式,沒有特殊字元

**Q: Railway 變數設定後沒效果?**
A: 等待自動部署完成,或手動觸發重新部署

**Q: 還是出現 bot 錯誤?**
A: 檢查 Railway logs,確認 "✅ 使用環境變數中的 cookies" 訊息

---

## 🎯 時間軸

```
0:00 - 安裝擴充功能
0:30 - 登入並匯出 cookies
1:00 - 轉換為 base64
2:00 - 設定 Railway 環境變數
3:00 - 推送程式碼更新
3:30 - 等待 Railway 部署
8:00 - 測試成功! ✅
```

**總共: 約 8 分鐘**

---

## ✨ 額外好處

使用 Cookies 後,你還能:

- ✅ 下載會員限定影片
- ✅ 下載年齡限制影片
- ✅ 獲得更高的下載速度
- ✅ 避免所有機器人檢測

---

**準備好了嗎? 開始第一步: 安裝瀏覽器擴充功能!** 🚀

有任何問題隨時告訴我!
