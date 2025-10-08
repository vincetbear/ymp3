# 🎯 最終部署檢查清單

## ✅ 已完成的修復

### 1. **Cookies 更新** ✅
- ✅ 重新登入 YouTube
- ✅ 重新匯出 cookies
- ✅ 生成新的 cookies_base64.txt
- ✅ 本地測試通過 (無過期警告)

### 2. **URL 清理邏輯** ✅
- ✅ 自動提取影片 ID
- ✅ 移除播放清單參數 (避免 `RD` 播放清單錯誤)
- ✅ 重建乾淨的 URL
- ✅ 程式碼已推送到 GitHub

### 3. **客戶端策略優化** ✅
- ✅ 有 cookies: 使用預設模式 (讓 yt-dlp 自動選擇)
- ✅ 無 cookies: 使用 iOS 客戶端
- ✅ 程式碼已推送到 GitHub

## 📋 Railway 設定步驟

### 步驟 1: 更新環境變數 (⚠️ 重要!)

1. **前往 Railway Dashboard**
   - URL: https://railway.app/dashboard
   - 選擇專案: `ymp3`

2. **更新 YOUTUBE_COOKIES_B64**
   ```
   點擊 Variables 標籤
   → 找到 YOUTUBE_COOKIES_B64
   → 點擊編輯 (鉛筆圖示)
   → 貼上新的 base64 內容 (從 cookies_base64.txt)
   → 點擊 Save/Update
   ```

3. **等待服務重啟**
   - Railway 會自動偵測變更
   - 等待約 1-2 分鐘

### 步驟 2: 驗證部署

1. **檢查部署日誌**
   ```
   Railway Dashboard
   → Deployments
   → 最新部署
   → View Logs
   ```
   
   尋找以下訊息:
   - ✅ `Starting gunicorn 23.0.0`
   - ✅ `Listening at: http://0.0.0.0:8080`
   - ✅ `✅ 使用環境變數中的 cookies`

2. **測試應用程式**
   - 開啟: https://ymp3-production.up.railway.app
   - 輸入測試 URL: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
   - 選擇格式: MP3 - 320kbps
   - 點擊「開始下載」

### 步驟 3: 確認成功

應該看到:
- ✅ 進度顯示: "正在準備下載..."
- ✅ 進度條正常移動
- ✅ 下載完成: "下載完成!"
- ✅ 檔案可以下載

## 🐛 如果仍然出現錯誤

### 錯誤 1: "Failed to extract any player response"
**原因**: Cookies 未更新或無效

**解決方案**:
1. 確認 Railway 環境變數已更新
2. 檢查 cookies_base64.txt 內容是否正確貼上
3. 重新啟動 Railway 服務

### 錯誤 2: "RDfLyHit9OnhU: Failed to parse JSON"
**原因**: URL 包含播放清單參數

**解決方案**:
- ✅ 已修復 - 最新程式碼會自動清理 URL
- 確認已部署最新版本 (commit: 86810cf)

### 錯誤 3: "cookies are no longer valid"
**原因**: Cookies 過期

**解決方案**:
1. 重新登出/登入 YouTube
2. 重新匯出 cookies
3. 執行 `python setup_cookies.py`
4. 更新 Railway 環境變數

## 📊 部署狀態

- **Git Commit**: `86810cf` ✅
- **GitHub 推送**: 完成 ✅
- **Railway 自動部署**: 進行中 ⏳
- **Cookies 更新**: 待完成 ⚠️ (需手動更新 Railway 環境變數)

## 🔄 定期維護

**Cookies 有效期**: 約 30-90 天

**維護步驟**:
1. 每月檢查一次應用程式是否正常
2. 如果出現認證錯誤,重新匯出 cookies
3. 更新 Railway 環境變數

## 📝 測試用影片 URL

```
✅ 正常影片:
https://www.youtube.com/watch?v=dQw4w9WgXcQ

✅ 短網址:
https://youtu.be/dQw4w9WgXcQ

✅ 帶播放清單 (會自動清理):
https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDfLyHit9OnhU
```

## 🎉 部署完成後

一旦確認所有測試通過:
1. ✅ 記錄你的應用程式 URL
2. ✅ 加入書籤以便快速存取
3. ✅ 分享給需要的人使用

---

**最後更新**: 2025-10-08
**狀態**: ⏳ 等待更新 Railway 環境變數
**下一步**: 更新 YOUTUBE_COOKIES_B64 環境變數
