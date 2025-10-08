# 🚀 Railway 快速設定清單

## 立即執行 (2 分鐘)

### 1️⃣ 登入 Railway
- 前往: https://railway.app/
- 登入您的帳號
- 開啟專案: **ymp3**

### 2️⃣ 設定代理環境變數

**位置:** Railway Dashboard → Variables 標籤

**變數名稱:**
```
PROXY_URL
```

**變數值:** (複製下面整行,直接貼上)
```
http://ellpsmsi:5x76u62w6hou@proxy.webshare.io:80
```

### 3️⃣ 儲存並等待部署

- 點擊 "Add" 或 "Save"
- Railway 自動重新部署
- 等待 3-5 分鐘

---

## ✅ 檢查部署

### 查看日誌確認:

**Railway Dashboard → Deployments → Logs**

**應該看到:**
```
🔒 使用代理伺服器: proxy.webshare.io:80
```

---

## 🧪 測試

部署完成後,開啟您的應用並測試:

**測試影片:**
```
https://www.youtube.com/watch?v=fLyHit9OnhU
```

**預期:**
- ✅ 成功獲取影片資訊
- ✅ 下載開始
- ✅ 下載完成

---

## ⚠️ 重要提醒

### 如果設定後仍然失敗:

1. **確認環境變數名稱:** 必須是 `PROXY_URL` (全大寫)
2. **確認格式:** `http://username:password@server:port`
3. **檢查 WebShare 帳號:** 確認已啟用且有額度
4. **重新部署:** 手動觸發一次部署

### 手動重新部署:

Railway Dashboard → Deployments → 右上角 "Redeploy"

---

## 📋 完成後的狀態

### Railway 環境變數應該有:

```
✅ PROXY_URL = http://ellpsmsi:5x76u62w6hou@proxy.webshare.io:80
```

### 可以刪除的舊變數:

```
❌ YOUTUBE_COOKIES_B64 (不再需要)
```

---

## 🎉 完成!

設定完成後:
- YouTube 下載器將使用代理繞過限制
- 支援影片和音訊下載
- 可在手機和電腦使用

**下一步:** 開始使用並享受! 🚀
