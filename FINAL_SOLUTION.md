# 🎉 最終解決方案:使用 Cookies

## ✅ 問題解決了!

經過測試,**只需要 YouTube Cookies 就可以繞過 bot 偵測**,不需要代理!

測試結果:
```
✅ 成功獲取影片資訊!
📹 標題: 遺憾終究拾不起@靚舞藝術舞集-倫巴身段基礎班
⏱️ 時長: 254 秒
```

---

## 🚀 部署到 Railway

### 步驟 1: 設定環境變數

登入 Railway 控制台:<https://railway.app/dashboard>

找到專案 `vincetbear/ymp3`,進入 **Variables** 設定:

#### 必要變數

```bash
YOUTUBE_COOKIES_B64=IyBOZXRzY2FwZSBIVFRQIENvb2tpZSBGaWxlDQojIFRoaXMgZmlsZSBpcyBnZW5lcmF0ZWQgYnkgeXQtZGxwLiAgRG8gbm90IGVkaXQuDQoNCi55b3V0dWJlLmNvbQlUUlVFCS8JRkFMU0UJMAlQUkVGCWY2PTQwMDAwMDAxJmY3PTEwMCZobD1lbiZ0ej1VVEMmZjQ9NDAwMDAwMCZmNT0zMDAwMA0KLnlvdXR1YmUuY29tCVRSVUUJLwlUUlVFCTE3OTMwODkxMDYJX19TZWN1cmUtM1BTSUQJZy5hMDAwMWdnVzlLU1FUZ2FxazRCM2xYdGJCQzl3blBWZzY4clpBZmd5dVYyTGlTeW1qZm1kTVBaZUx4aEEzdGtqLWtIb3ZCdS1YZ0FDZ1lLQWFjU0FSVVNGUUhHWDJNaUxBRjFUN2ZnXzljWXJobkhVaUVXamhvVkFVRjh5S3FWYlpjS19IV2RqRWlFTzZqUzRDd2owMDc2DQoueW91dHViZS5jb20JVFJVRQkvCVRSVUUJMTc5MzA4OTEwNglfX1NlY3VyZS0zUEFQSVNJRAlJdU82M3R1Z1lTT05MZ2N2L0F6X3Q4OC1CZGFqdW5qZk44DQoueW91dHViZS5jb20JVFJVRQkvCVRSVUUJMTc5MTQzODA3MglfX1NlY3VyZS0xUFNJRFRTCXNpZHRzLUNqUUJta0Q1U3piOU9KUzF2d1AwUHpva2VELUJkdlZVMVNGTnFGZUxsdkMzN0g0Z3pqUXE4RjR0RVhpOUZfMEIwc2htZnJfSEVBQQ0KLnlvdXR1YmUuY29tCVRSVUUJLwlUUlVFCTE3OTE0MzgwNzIJX19TZWN1cmUtM1BTSURUUwlzaWR0cy1DalFCbWtENVN6YjlPSlMxdndQMFB6b2tlRC1CZHZWVTFTRk5xRmVMbHZDMzdINGd6alFxOEY0dEVYaTlGXzBCMHNobWZyX0hFQUENCi55b3V0dWJlLmNvbQlUUlVFCS8JVFJVRQkxNzkxNDM4MzU1CV9fU2VjdXJlLTNQU0lEQ0MJQUtFeVh6WGhwd3NQcmlIVUItVm85N2djeF9yaUIwNkg3dm5BLU4xcWZ5LUF2aG5RSTI2dzZOU3g1RVRkdzFvcGV5NVBWdUZlY3JRDQoueW91dHViZS5jb20JVFJVRQkvCVRSVUUJMTc3NTQ1NjUxMQlfX1NlY3VyZS1ST0xMT1VUX1RPS0VOCUNOemxocEQwczhlaUNoQ1owNmlaLTVPUUF4aVFnSXFhLTVPUUF3JTNEJTNEDQoueW91dHViZS5jb20JVFJVRQkvCVRSVUUJMTc3NTQ2NTA1NQlWSVNJVE9SX0lORk8xX0xJVkUJWk9hVzl6WXA2djQNCi55b3V0dWJlLmNvbQlUUlVFCS8JVFJVRQkxNzc1NDY1MDU1CVZJU0lUT1JfUFJJVkFDWV9NRVRBREFUQQlDZ0pVVnhJRUdnQWdSdyUzRCUzRA0KLnlvdXR1YmUuY29tCVRSVUUJLwlUUlVFCTE4MjI5NzkwODAJX19TZWN1cmUtWVRfVFZGQVMJdD00ODg4NjImcz0yDQoueW91dHViZS5jb20JVFJVRQkvCVRSVUUJMTc3NTQ1OTA4MAlERVZJQ0VfSU5GTwlDaHhPZWxVeFQwUmplazFxVFhsTlJHZDNUMFJCTWs5RVFUTlBRVDA5RUlpYW1NY0dHUCtGbU1jRw0KLnlvdXR1YmUuY29tCVRSVUUJLwlUUlVFCTAJU09DUwlDQUkNCi55b3V0dWJlLmNvbQlUUlVFCS8JVFJVRQkxNzU5OTE0ODU1CUdQUwkxDQoueW91dHViZS5jb20JVFJVRQkvCVRSVUUJMAlZU0MJRWd1bUR0bFVtMHcNCi55b3V0dWJlLmNvbQlUUlVFCS90dglUUlVFCTE3OTI3MzkwODAJX19TZWN1cmUtWVRfREVSUAlDTWJyeVp4eA0K
```

#### 可選變數(如果要啟用代理)

```bash
USE_PROXY=true
WEBSHARE_USERNAME=ellpsmsi
WEBSHARE_PASSWORD=5x76u62w6hou
PROXY_IPS=23.94.138.113:6387,192.241.104.29:8123
```

**建議**: 先不要設定代理,因為 cookies 已經足夠了!

---

### 步驟 2: 推送代碼到 GitHub

```powershell
cd d:\01專案\2025\newyoutube\web_version
git add .
git commit -m "✨ 添加 Cookies 支援,解決 YouTube bot 偵測問題"
git push
```

Railway 會自動偵測到推送並重新部署。

---

### 步驟 3: 驗證部署

1. 等待 Railway 部署完成(約 1-3 分鐘)
2. 查看部署日誌,應該看到:
   ```
   ✅ 使用環境變數中的 cookies
   ```

3. 訪問你的網站測試下載

---

## 📝 代碼更新說明

### 修改的檔案

1. **app.py**
   - ✅ 添加 cookies 支援 (優先)
   - ✅ 代理變為可選 (設定 `USE_PROXY=true` 才啟用)
   - ✅ 支援多種 cookies 檔案名稱
   - ✅ 增加代理超時時間 (30秒)

2. **proxy_config.py**
   - ✅ 100 個 WebShare 代理 IP

3. **測試檔案**
   - ✅ test_cookies_only.py - 測試 cookies
   - ✅ test_cookies_proxy.py - 測試 cookies + 代理

---

## 🔄 如何更新 Cookies

當 cookies 過期時(通常幾個月後):

### 方法 1: 使用瀏覽器擴充功能

1. 安裝 "Get cookies.txt LOCALLY" Chrome 擴充功能
2. 登入 YouTube
3. 點擊擴充功能,匯出 cookies
4. 將檔案內容轉成 base64
5. 更新 Railway 環境變數

### 方法 2: 使用 yt-dlp 匯出

```powershell
# 從瀏覽器匯出 cookies
yt-dlp --cookies-from-browser chrome --cookies youtube.com_cookies.txt "https://www.youtube.com"

# 轉成 base64
python -c "import base64; print(base64.b64encode(open('youtube.com_cookies.txt', 'rb').read()).decode())"
```

---

## 🎯 優點

相比使用代理:

- ✅ **速度快** - 不需要通過代理伺服器
- ✅ **穩定** - 不受代理超時影響
- ✅ **免費** - 不需要付費代理服務
- ✅ **簡單** - 只需要一個環境變數

---

## ⚠️ 注意事項

1. **Cookies 會過期**
   - 通常有效期: 幾個月
   - 過期後需要重新匯出

2. **不要公開分享 Cookies**
   - Cookies 包含你的登入資訊
   - 只在 Railway 環境變數中使用(已加密)

3. **定期檢查**
   - 如果下載開始失敗,可能是 cookies 過期了
   - 重新匯出並更新環境變數即可

---

## 🆘 疑難排解

### 如果仍然失敗

1. **檢查 cookies 是否過期**
   ```powershell
   cd d:\01專案\2025\newyoutube\web_version
   python test_cookies_only.py
   ```

2. **重新匯出 cookies**
   - 確保已登入 YouTube
   - 使用最新的 cookies

3. **啟用代理作為備用**
   - 在 Railway 設定 `USE_PROXY=true`
   - 但速度會較慢

---

**下一步**: 推送代碼到 GitHub,Railway 會自動部署! 🚀
