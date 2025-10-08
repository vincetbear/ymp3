# PWA 圖示製作指南

## 📱 需要的圖示尺寸

為了讓 PWA 在所有裝置上都有完美的圖示，需要以下尺寸：

```
icons/
├── icon-72x72.png      (Android)
├── icon-96x96.png      (Android)
├── icon-128x128.png    (Android/Desktop)
├── icon-144x144.png    (Android)
├── icon-152x152.png    (iOS)
├── icon-192x192.png    (Android/Desktop)
├── icon-384x384.png    (Android)
└── icon-512x512.png    (Android/Splash)
```

## 🎨 製作方法

### 方法 1: 使用線上工具（最簡單）

1. **訪問**: https://www.favicon-generator.org/
2. **上傳**: 一張 512x512 的圖片
3. **下載**: 自動產生所有尺寸
4. **放置**: 移動到 `web_version/static/icons/` 資料夾

### 方法 2: 使用 Photoshop/GIMP

1. 建立 512x512 畫布
2. 設計圖示（建議簡單圖案 + 背景色）
3. 匯出為 PNG
4. 使用圖片編輯工具縮放到各種尺寸

### 方法 3: 使用 Python 腳本自動產生

```python
from PIL import Image
import os

# 原始圖片（512x512）
base_image = Image.open('icon-512x512.png')

# 需要的尺寸
sizes = [72, 96, 128, 144, 152, 192, 384, 512]

# 產生各種尺寸
for size in sizes:
    img = base_image.resize((size, size), Image.LANCZOS)
    img.save(f'icon-{size}x{size}.png')
```

## 🎯 設計建議

### 顏色
- 主色：藍色 (#1976d2) - 與 App 主題一致
- 輔助色：白色或漸層

### 內容
- 簡單的圖示或文字
- 例如：
  - "YT" 字樣 + 下載箭頭
  - YouTube 播放符號 + 向下箭頭
  - 簡單的影片圖示

### 注意事項
- ✅ 使用高對比度
- ✅ 避免細節過多（小尺寸會看不清）
- ✅ 背景不要透明（建議用顏色）
- ✅ 保持簡潔

## 🚀 臨時方案（快速測試）

如果還沒有圖示，可以先使用純色 PNG：

1. 前往：https://via.placeholder.com/512x512/1976d2/FFFFFF/?text=YT
2. 下載圖片
3. 使用上面的 Python 腳本產生各種尺寸
4. 放到 `static/icons/` 資料夾

## 📝 圖示檢查清單

- [ ] 512x512 基礎圖示已製作
- [ ] 所有需要的尺寸已產生
- [ ] 圖示已放置到 `static/icons/` 資料夾
- [ ] `manifest.json` 中的路徑正確
- [ ] 在手機上測試安裝效果

## 💡 進階優化

### iOS 特殊圖示

在 `index.html` 中加入：

```html
<link rel="apple-touch-icon" href="/static/icons/icon-152x152.png">
<link rel="apple-touch-icon" sizes="180x180" href="/static/icons/icon-180x180.png">
```

### Splash Screen（啟動畫面）

iOS 需要額外的 splash screen：

```html
<link rel="apple-touch-startup-image" href="/static/splash.png">
```

---

**目前狀態**: 圖示資料夾已建立，但圖示檔案需要你自行製作或使用線上工具產生。

**建議**: 先使用臨時方案快速測試，之後再設計專業圖示。
