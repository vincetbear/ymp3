# 備用方案: 不使用 ffmpeg 轉換

如果 Railway 無法安裝 ffmpeg,可以使用此版本的 app.py

## 修改重點

```python
if download_type == 'audio':
    # 不轉換為 mp3,直接下載最佳音訊格式
    ydl_opts.update({
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, f'{task_id}_%(title)s.%(ext)s'),
        # 移除 postprocessors - 不進行格式轉換
    })
```

## 優點
- ✅ 不需要 ffmpeg
- ✅ 下載速度更快(不需轉換)
- ✅ Railway 構建簡單

## 缺點
- ⚠️ 檔案格式可能是 m4a, webm, opus 等(不一定是 mp3)
- ⚠️ 某些播放器可能不支援

## 折衷方案

提供兩種下載選項:
1. **MP3 (需要 ffmpeg)** - 如果 Railway 支援
2. **原始音訊 (不需要 ffmpeg)** - 作為備用

讓使用者在前端選擇。

---

**目前狀態**: 先等待 railway.toml 方案的結果
**如果成功**: 不需要此備用方案
**如果失敗**: 使用此方案修改 app.py
