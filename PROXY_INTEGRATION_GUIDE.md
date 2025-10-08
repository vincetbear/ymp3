# 代理服務整合指南

## 步驟 1: 註冊 WebShare.io

1. 前往 https://www.webshare.io/
2. 註冊帳號 (可使用免費試用)
3. 進入 Dashboard → Proxy → List
4. 複製代理資訊

## 步驟 2: 設定環境變數

在 Railway 新增環境變數:

```
PROXY_HOST=proxy.webshare.io
PROXY_PORT=80
PROXY_USER=your_username
PROXY_PASS=your_password
```

或使用完整格式:

```
PROXY_URL=http://username:password@proxy.webshare.io:80
```

## 步驟 3: 修改 app.py

在下載函數中加入:

```python
import os

# 獲取代理設定
proxy_url = os.environ.get('PROXY_URL')

if proxy_url:
    ydl_opts['proxy'] = proxy_url
    print(f"🔒 使用代理: {proxy_url.split('@')[1]}")  # 只顯示伺服器,不顯示密碼
```

## 步驟 4: 測試

本地測試:
```bash
export PROXY_URL="http://user:pass@proxy.webshare.io:80"
python app.py
```

部署到 Railway:
- 在 Railway Dashboard 設定環境變數
- 重新部署即可

## WebShare 代理格式範例

```
格式: protocol://username:password@host:port

HTTP 代理:
http://myuser:mypass@proxy.webshare.io:80

SOCKS5 代理:
socks5://myuser:mypass@proxy.webshare.io:1080
```

## 其他代理服務設定

### Bright Data
```python
PROXY_URL=http://customer-USERNAME-zone-ZONE:PASSWORD@brd.superproxy.io:22225
```

### ScraperAPI (不使用傳統代理)
```python
# 直接在請求 URL 加上 API key
url = f"http://api.scraperapi.com?api_key=YOUR_KEY&url={youtube_url}"
```

### Proxy-Cheap
```python
PROXY_URL=http://user:pass@residential-proxy.proxy-cheap.com:31112
```

## 成本估算

### WebShare.io
- 10 代理 + 無限頻寬 = $2.99/月
- 適合: 個人使用,每天 < 100 次下載

### Bright Data
- 按流量計費: ~$0.01/次下載
- 預估: 1000 次下載 ≈ $10-15/月
- 適合: 商業使用,大量下載

### ScraperAPI
- 免費: 1000 次/月
- 付費: $49/月無限次
- 適合: 測試和中等使用量

## 測試代理是否可用

```python
import requests

proxy = "http://user:pass@proxy.webshare.io:80"
proxies = {
    "http": proxy,
    "https": proxy
}

try:
    response = requests.get("https://www.youtube.com", proxies=proxies, timeout=10)
    print(f"✅ 代理可用! Status: {response.status_code}")
except Exception as e:
    print(f"❌ 代理失敗: {e}")
```

## 下一步

1. 選擇代理服務並註冊
2. 獲取代理憑證
3. 告訴我,我會立即修改 app.py 整合代理
4. 部署到 Railway 測試

您想用哪個服務? 我推薦先試 **WebShare.io** (有免費試用)!
