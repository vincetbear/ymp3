# 🎯 Railway 部署測試指南

## ✅ 最新更新 (2025-10-08)

### Commit: bcf33dd
- ✅ 後端 URL 清理邏輯 (app.py)
- ✅ 前端 URL 清理邏輯 (app.js)
- ✅ 自動移除播放清單參數
- ✅ 更新 cookies 處理

## 📋 測試前準備

### 1. 確認 Railway 環境變數已更新
- ✅ `YOUTUBE_COOKIES_B64` 已更新為最新值
- ✅ 從 `cookies_base64.txt` 複製的完整內容

### 2. 等待部署完成
- ⏳ Railway 自動部署需要 3-5 分鐘
- 📍 檢查 Railway Dashboard → Deployments
- ✅ 確認最新 commit `bcf33dd` 已部署

## 🧪 測試步驟

### 測試 1: 基本影片下載

1. **開啟應用程式**
   ```
   https://ymp3-production.up.railway.app
   ```

2. **輸入測試 URL**
   ```
   https://www.youtube.com/watch?v=dQw4w9WgXcQ
   ```

3. **選擇格式**
   - 選擇: MP3
   - 品質: 320 kbps

4. **開始下載**
   - 點擊「開始下載」
   - 觀察進度顯示

5. **預期結果**
   - ✅ 顯示「正在準備下載...」
   - ✅ 進度條正常顯示
   - ✅ 下載完成
   - ✅ 可以下載檔案

### 測試 2: 帶播放清單的 URL (重點!)

1. **輸入包含播放清單的 URL**
   ```
   https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDfLyHit9OnhU
   ```

2. **檢查 URL 自動清理**
   - 輸入後,URL 應該自動變成:
   ```
   https://www.youtube.com/watch?v=dQw4w9WgXcQ
   ```
   (播放清單參數 `&list=RDfLyHit9OnhU` 被移除)

3. **下載測試**
   - 選擇 MP3 320kbps
   - 點擊下載

4. **預期結果**
   - ✅ URL 自動清理完成
   - ✅ 不再出現 `RDfLyHit9OnhU` 錯誤
   - ✅ 成功下載影片

### 測試 3: 短網址

1. **輸入短網址**
   ```
   https://youtu.be/dQw4w9WgXcQ
   ```

2. **預期結果**
   - ✅ 自動轉換為標準格式
   - ✅ 成功提取影片資訊
   - ✅ 成功下載

### 測試 4: 短網址 + 播放清單

1. **輸入**
   ```
   https://youtu.be/dQw4w9WgXcQ?list=RDfLyHit9OnhU
   ```

2. **預期結果**
   - ✅ 自動清理為: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
   - ✅ 成功下載

## 🐛 錯誤診斷

### 如果仍出現 "RDfLyHit9OnhU: Failed to parse JSON"

**可能原因**:
1. Railway 還在使用舊版本程式碼
2. 瀏覽器快取了舊的 JavaScript

**解決方案**:

#### 方案 1: 清除瀏覽器快取
```
Ctrl + Shift + R (Windows)
Cmd + Shift + R (Mac)
```

#### 方案 2: 檢查 Railway 部署狀態
1. 前往 Railway Dashboard
2. Deployments 標籤
3. 確認最新部署的 commit hash 是 `bcf33dd`
4. 如果不是,等待自動部署完成

#### 方案 3: 手動觸發重新部署
1. Railway Dashboard → Settings
2. 點擊 "Redeploy"

#### 方案 4: 檢查日誌
```
Railway Dashboard → Deployments → View Logs
```

尋找:
- ✅ `📹 清理後的 URL: https://www.youtube.com/watch?v=...`
- ✅ `🍪 使用 Cookies 標準模式`
- ❌ 不應該看到 `RDfLyHit9OnhU`

## 📊 成功指標

- [ ] 基本 URL 可以下載
- [ ] 帶播放清單的 URL 會自動清理
- [ ] 短網址可以正常處理
- [ ] 沒有 "Failed to parse JSON" 錯誤
- [ ] 沒有 "cookies are no longer valid" 警告

## 🎉 測試通過後

一旦所有測試通過:
1. ✅ 應用程式已準備好使用
2. ✅ Cookies 有效期約 30-90 天
3. ✅ 如果未來出現錯誤,重複 cookies 更新流程

## 📝 測試記錄

| 測試項目 | 測試 URL | 結果 | 備註 |
|---------|---------|------|------|
| 基本影片 | dQw4w9WgXcQ | ⏳ | 待測試 |
| 帶播放清單 | dQw4w9WgXcQ&list=... | ⏳ | 待測試 |
| 短網址 | youtu.be/dQw4w9WgXcQ | ⏳ | 待測試 |
| 短網址+清單 | youtu.be/...?list=... | ⏳ | 待測試 |

---

**部署時間**: 2025-10-08 06:35
**Commit**: bcf33dd
**狀態**: ⏳ 等待 Railway 部署完成 (約 3-5 分鐘)
**下一步**: 清除瀏覽器快取後測試
