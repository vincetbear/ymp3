"""
自動更新 app.py 中的代理配置
"""

# 讀取檔案
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 添加 import (在已有的 import 之後)
old_import = "from urllib.parse import urlparse, parse_qs"
new_import = "from urllib.parse import urlparse, parse_qs\nfrom proxy_config import get_random_proxy, get_proxy_display"

if "from proxy_config import" not in content:
    content = content.replace(old_import, new_import)
    print("✅ 已添加 proxy_config import")
else:
    print("ℹ️ proxy_config import 已存在")

# 2. 移除舊的 PROXY_URL 配置
old_config = """# 代理設定 - 從環境變數讀取
PROXY_URL = os.environ.get('PROXY_URL', None)
if PROXY_URL:
    print(f"🔒 使用代理伺服器: {PROXY_URL.split('@')[1] if '@' in PROXY_URL else PROXY_URL}")
else:
    print("⚠️ 未設定代理,可能會遇到 YouTube bot 偵測")

"""

if old_config in content:
    content = content.replace(old_config, "")
    print("✅ 已移除舊的 PROXY_URL 配置")
else:
    print("ℹ️ 舊的 PROXY_URL 配置不存在")

# 3. 替換 download_video 函數中的代理使用 (使用正則表達式來處理 emoji 顯示問題)
import re

# 使用更靈活的匹配模式
pattern1 = r"        # 如果有設定代理,使用代理\s*\n\s*if PROXY_URL:\s*\n\s*ydl_opts\['proxy'\] = PROXY_URL\s*\n\s*print\(f\"[^\"]*使用代理[^\"]*\"\)"

new_proxy_code1 = """        # 使用隨機代理
        proxy_url = get_random_proxy()
        if proxy_url:
            ydl_opts['proxy'] = proxy_url
            print(f"🔒 使用代理: {get_proxy_display(proxy_url)}")"""

match1 = re.search(pattern1, content)
if match1:
    content = re.sub(pattern1, new_proxy_code1, content)
    print("✅ 已更新 download_video 函數的代理使用")
else:
    print("⚠️ 找不到 download_video 函數的舊代理代碼")

# 4. 替換 get_video_info 函數中的代理使用
old_proxy_code2 = """        # 如果有代理,使用代理
        if PROXY_URL:
            ydl_opts['proxy'] = PROXY_URL"""

new_proxy_code2 = """        # 使用隨機代理
        proxy_url = get_random_proxy()
        if proxy_url:
            ydl_opts['proxy'] = proxy_url
            print(f"🔒 獲取資訊使用代理: {get_proxy_display(proxy_url)}")"""

if old_proxy_code2 in content:
    content = content.replace(old_proxy_code2, new_proxy_code2)
    print("✅ 已更新 get_video_info 函數的代理使用")
else:
    print("⚠️ 找不到 get_video_info 函數的舊代理代碼")

# 寫回檔案
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✨ app.py 更新完成!")
print("\n接下來請:")
print("1. 檢查 app.py 是否正確")
print("2. 設定 Railway 環境變數")
print("3. 部署到 Railway")
