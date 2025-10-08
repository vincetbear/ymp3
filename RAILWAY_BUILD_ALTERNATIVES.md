# 🔧 Railway 構建失敗 - 替代方案

## 問題
Railway Nixpacks 配置複雜,構建失敗

## 方案 A: 簡化配置 (已嘗試 - Commit: df9a1bb)
```toml
[build]
builder = "NIXPACKS"

[build.nixPkgs]
packages = ["ffmpeg"]
```

## 方案 B: 使用 railway.json (如果 A 失敗)

刪除 `nixpacks.toml` 和 `railway.toml`,建立 `railway.json`:

```json
{
  "build": {
    "builder": "NIXPACKS",
    "nixpacksPlan": {
      "phases": {
        "setup": {
          "nixPkgs": ["ffmpeg"]
        }
      }
    }
  }
}
```

## 方案 C: 使用環境變數

在 Railway Dashboard 設定環境變數:
```
NIXPACKS_PKGS=ffmpeg
```

## 方案 D: 修改 requirements.txt (最簡單)

在 `requirements.txt` 後面添加:
```
# Note: Railway needs to install ffmpeg separately
# Use: railway.toml or NIXPACKS_PKGS=ffmpeg
```

然後在 Railway Dashboard → Settings → Deploy 中添加:
```
Install Command: apt-get update && apt-get install -y ffmpeg && pip install -r requirements.txt
```

## 方案 E: 只下載音訊,不轉換

修改 `app.py`,直接下載 m4a/webm 格式,不轉換為 mp3:

```python
if download_type == 'audio':
    ydl_opts.update({
        'format': 'bestaudio/best',
        # 不使用 postprocessors,直接下載原始音訊
    })
```

## 推薦順序

1. 等待方案 A 構建結果
2. 如果失敗 → 方案 C (設定環境變數)
3. 如果仍失敗 → 方案 E (不轉換 mp3)
4. 最後才考慮 → 方案 D (自定義構建命令)

---

**目前狀態**: 等待方案 A (Commit: df9a1bb) 構建結果
