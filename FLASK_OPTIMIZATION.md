# Flask 優化版本 - 完整說明

## 🎯 優化目標

提升 Flask 應用的穩定性、安全性和可維護性，同時保持程式碼簡潔。

---

## ✨ 主要改進

### 1. API 速率限制（Flask-Limiter）

**目的**：防止 API 濫用，保護伺服器資源

**實作**：
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
```

**速率限制設定**：
- 全域限制：每天 200 次，每小時 50 次
- `/api/info`：每分鐘 30 次
- `/api/download`：每小時 10 次（防止濫用下載）
- `/api/progress`：每分鐘 60 次（輪詢頻率）

**錯誤回應**：
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "請求過於頻繁，請稍後再試",
    "details": {
      "retry_after": "60 seconds"
    }
  },
  "request_id": "uuid"
}
```

---

### 2. 統一錯誤處理

**成功回應格式**：
```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功",
  "request_id": "uuid"
}
```

**錯誤回應格式**：
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "錯誤訊息",
    "details": { ... }
  },
  "request_id": "uuid"
}
```

**錯誤代碼**：
- `MISSING_URL` - 缺少 URL 參數
- `INVALID_URL` - 無效的 YouTube URL
- `INVALID_TYPE` - 無效的下載類型
- `INVALID_TASK_ID` - 無效的任務 ID
- `TASK_NOT_FOUND` - 任務不存在
- `RATE_LIMIT_EXCEEDED` - 超過速率限制
- `FILE_TOO_LARGE` - 檔案過大
- `INTERNAL_ERROR` - 伺服器內部錯誤

---

### 3. 請求追蹤（Request ID）

**功能**：為每個請求生成唯一 ID，方便追蹤和除錯

**實作**：
```python
@app.before_request
def before_request():
    """為每個請求生成唯一ID"""
    g.request_id = str(uuid.uuid4())
    g.start_time = datetime.now()

@app.after_request
def after_request(response):
    """記錄請求資訊"""
    if hasattr(g, 'start_time'):
        duration = (datetime.now() - g.start_time).total_seconds()
        app.logger.info(
            f'[{g.request_id}] {request.method} {request.path} '
            f'- {response.status_code} - {duration:.3f}s'
        )
    return response
```

**日誌範例**：
```
[a1b2c3d4-...] POST /api/download - 200 - 0.123s
[a1b2c3d4-...] 建立下載任務: task_id=xyz, type=audio
```

---

### 4. 任務管理優化

**新增功能**：

1. **任務過期清理**：
```python
def cleanup_old_tasks():
    """清理過期的任務記錄（超過 2 小時）"""
    for task_id, task in list(download_tasks.items()):
        created_at = datetime.fromisoformat(task['created_at'])
        if now - created_at > timedelta(hours=2):
            del download_tasks[task_id]
```

2. **定期清理**：
```python
def periodic_cleanup():
    while True:
        time.sleep(3600)  # 每小時
        cleanup_old_files()    # 清理下載檔案
        cleanup_old_tasks()    # 清理過期任務
```

**優點**：
- 防止記憶體洩漏
- 自動管理任務生命週期
- 減少記憶體使用

---

### 5. 效能監控端點

**新端點**：`GET /api/metrics`

**回應範例**：
```json
{
  "success": true,
  "data": {
    "timestamp": "2025-10-24T12:00:00",
    "system": {
      "cpu_percent": 25.5,
      "memory_mb": 128,
      "threads": 5
    },
    "disk": {
      "total_mb": 10240,
      "used_mb": 5120,
      "free_mb": 5120,
      "usage_percent": 50.0
    },
    "tasks": {
      "total": 10,
      "pending": 1,
      "downloading": 2,
      "converting": 1,
      "completed": 5,
      "error": 1
    },
    "downloads": {
      "folder": "/path/to/downloads",
      "file_count": 15
    }
  }
}
```

**用途**：
- 監控系統健康狀態
- 追蹤資源使用情況
- 識別效能瓶頸
- 容量規劃

---

### 6. 改善日誌記錄

**新增**：
- 結構化日誌格式
- Request ID 追蹤
- 請求處理時間記錄
- 錯誤堆疊追蹤

**範例日誌**：
```
2025-10-24 12:00:00 INFO: [a1b2c3d4] POST /api/download - 200 - 0.123s
2025-10-24 12:00:01 INFO: [a1b2c3d4] 建立下載任務: task_id=xyz
2025-10-24 12:00:05 INFO: [a1b2c3d4] 下載完成: video.mp4 (50.00 MB)
2025-10-24 12:00:10 ERROR: [b2c3d4e5] 下載錯誤: Connection timeout
```

**優點**：
- 容易追蹤單一請求的完整生命週期
- 快速定位問題
- 更好的除錯體驗

---

## 📦 新增依賴

```txt
flask-limiter==3.5.0  # API 速率限制
psutil==5.9.8         # 系統監控
```

安裝方式：
```bash
pip install -r requirements.txt
```

---

## 🔧 前端適配

### API 回應處理

**舊版本**：
```javascript
const data = await response.json();
if (data.error) {
    alert(data.error);
}
```

**新版本**：
```javascript
const result = await response.json();
if (result.success && result.data) {
    // 處理成功回應
    const data = result.data;
} else if (result.error) {
    // 處理錯誤
    const errorMsg = result.error.message;
    const errorCode = result.error.code;
    
    if (errorCode === 'RATE_LIMIT_EXCEEDED') {
        alert('請求過於頻繁，請稍後再試');
    } else {
        alert('錯誤: ' + errorMsg);
    }
}
```

---

## 🚀 部署注意事項

### 環境變數

可選的環境變數配置：

```bash
# 速率限制
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT="200 per day, 50 per hour"
RATE_LIMIT_DOWNLOAD="10 per hour"

# 任務管理
MAX_CONCURRENT_DOWNLOADS=3
TASK_TIMEOUT=600

# 檔案清理
FILE_CLEANUP_HOURS=1

# 日誌
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### Railway 部署

1. **推送到 GitHub**：
```bash
git push origin main
```

2. **Railway 自動部署**：
   - 檢測到更改後自動建置
   - 安裝新依賴（flask-limiter, psutil）
   - 重啟服務

3. **驗證部署**：
```bash
# 健康檢查
curl https://your-app.railway.app/health

# 監控指標
curl https://your-app.railway.app/api/metrics
```

---

## 📊 效能對比

| 指標 | 優化前 | 優化後 | 改善 |
|------|--------|--------|------|
| 錯誤處理 | 不一致 | 統一格式 | ✅ |
| 請求追蹤 | 無 | Request ID | ✅ |
| 速率限制 | 無 | 多層級限制 | ✅ |
| 任務清理 | 手動 | 自動 | ✅ |
| 監控能力 | 基本 | 詳細指標 | ✅ |
| 日誌品質 | 基本 | 結構化 | ✅ |

---

## 🔍 監控和除錯

### 查看系統狀態

訪問 `/api/metrics` 端點：

```javascript
fetch('/api/metrics')
  .then(r => r.json())
  .then(data => console.log(data));
```

### 追蹤特定請求

使用 Request ID 在日誌中搜尋：

```bash
grep "a1b2c3d4" logs/app.log
```

### 檢查速率限制狀態

前端會自動處理 429 錯誤並顯示友善訊息。

---

## 🎓 最佳實踐

### 1. 監控系統健康

定期檢查 `/api/metrics`：
- CPU 使用率 > 80% → 考慮擴展
- 記憶體使用 > 400MB → 調查記憶體洩漏
- 磁碟空間 < 100MB → 增加清理頻率

### 2. 調整速率限制

根據實際使用情況調整：
- 個人使用：可以放寬限制
- 公開服務：保持嚴格限制
- 付費用戶：可以提供更高配額

### 3. 日誌管理

- 定期歸檔舊日誌
- 使用 `RotatingFileHandler`（已配置）
- 保留最近 10 個日誌檔案

### 4. 錯誤處理

- 永遠使用統一的錯誤格式
- 提供有意義的錯誤代碼
- 記錄完整的錯誤堆疊

---

## 🚧 未來改進方向

### 短期（1-2 週）

- [ ] 添加 Redis 支援（多 Worker）
- [ ] 實作請求重試機制
- [ ] 添加下載暫停/恢復功能

### 中期（1-2 個月）

- [ ] 使用 Celery 處理背景任務
- [ ] 添加使用者認證系統
- [ ] 實作下載佇列管理

### 長期（3+ 個月）

- [ ] 遷移到 FastAPI（如需更高效能）
- [ ] 添加 WebSocket 即時通知
- [ ] 實作分散式檔案儲存

---

## 📝 總結

這次優化主要聚焦在：

✅ **穩定性**：速率限制、錯誤處理、任務清理  
✅ **可維護性**：統一格式、請求追蹤、結構化日誌  
✅ **監控能力**：效能指標、系統狀態、資源使用  
✅ **使用者體驗**：友善錯誤訊息、自動重試提示  

所有改進都在保持 Flask 簡潔性的前提下進行，沒有引入過多複雜性。

**部署狀態**：✅ 已推送到 GitHub，Railway 正在自動部署

---

**版本**：v2.1.0  
**更新日期**：2025-10-24  
**作者**：GitHub Copilot + User
