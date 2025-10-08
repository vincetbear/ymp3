# 🔍 WebShare 代理設定問題排查

## ❌ 當前問題

代理連線失敗,可能原因:
1. 用戶名或密碼不正確
2. 代理伺服器地址錯誤
3. WebShare 帳號未啟用或過期

---

## ✅ 解決方案: 從 WebShare 獲取正確資訊

### 步驟 1: 登入 WebShare Dashboard

1. 前往: https://www.webshare.io/
2. 登入您的帳號
3. 確認帳號狀態是 **Active** (已啟用)

### 步驟 2: 取得代理清單

1. 左側選單點擊 **"Proxy"** → **"List"**
2. 您會看到代理列表

### 步驟 3: 複製正確的代理資訊

在代理列表中,您會看到類似這樣的資訊:

```
Proxy Address: xxx.xxx.xxx.xxx:port
Username: your_username
Password: your_password
```

**或者** WebShare 可能提供直接的代理 URL:

```
Protocol://Username:Password@ProxyHost:Port
```

### 步驟 4: 確認格式

WebShare 的代理通常是以下格式之一:

#### 格式 A: 使用 IP 地址
```
http://ellpsmsi:5x76u62w6hou@123.456.789.012:80
```

#### 格式 B: 使用域名
```
http://ellpsmsi:5x76u62w6hou@proxy.webshare.io:80
```

#### 格式 C: SOCKS5 (需要安裝額外套件)
```
socks5://ellpsmsi:5x76u62w6hou@proxy.webshare.io:1080
```

---

## 📋 請提供以下資訊

從 WebShare Dashboard 的 "Proxy List" 複製以下資訊:

1. **Proxy Host/Address:** (例如: 123.456.789.012 或 proxy.webshare.io)
2. **Port:** (例如: 80 或 9999)
3. **Username:** (例如: ellpsmsi)
4. **Password:** (例如: 5x76u62w6hou)
5. **Protocol:** (HTTP 或 SOCKS5)

---

## 🔧 常見問題

### Q1: 我的 WebShare 是免費試用版嗎?

**檢查方法:**
- Dashboard 上方應該顯示您的方案
- 免費試用: "Trial" 或 "Free Plan"
- 付費方案: "Starter", "Professional" 等

**免費試用限制:**
- 通常只提供 10 個代理
- 有效期 24 小時
- 可能有流量限制

### Q2: 代理一直顯示 404 錯誤?

**可能原因:**
1. 用戶名/密碼包含特殊字元需要編碼
2. 代理伺服器地址錯誤
3. 帳號未付費或已過期

**解決方法:**
- 檢查帳號狀態
- 使用 IP 地址而不是域名
- 確認沒有複製到多餘的空格

### Q3: WebShare 提供的是 IP 地址而不是域名?

**沒問題!** 使用這個格式:

```
http://username:password@12.34.56.78:9999
```

其中 `12.34.56.78:9999` 是從 WebShare 複製的 IP 和埠號。

---

## 🎯 替代方案 (如果 WebShare 不可用)

如果 WebShare 無法使用,可以考慮:

### 方案 1: 使用其他代理服務

**Proxy-Cheap** ($5/月)
- https://www.proxy-cheap.com/
- 提供住宅代理
- 設定簡單

**ScraperAPI** (免費 1000 次/月)
- https://www.scraperapi.com/
- 不需要手動設定代理
- 自動處理輪換

### 方案 2: 暫時移除代理,使用 Invidious

回到之前的 Invidious 方案:
- 等待 Invidious 實例恢復
- 定期檢查可用實例
- 雖然不穩定但免費

### 方案 3: 純桌面版

- 桌面版完全正常運作
- 不受 IP 限制
- 功能完整

---

## 📞 下一步

請提供從 WebShare 複製的正確代理資訊,格式如下:

```
Proxy Host: ____________
Port: ____________
Username: ____________
Password: ____________
Protocol: HTTP / SOCKS5
```

或直接提供完整的代理 URL:

```
http://username:password@host:port
```

我會立即幫您更新設定! 🚀
