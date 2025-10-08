"""診斷 Railway cookies 的腳本"""
import base64
import os
import tempfile

print("=" * 60)
print("Railway Cookies 診斷工具")
print("=" * 60)

# 模擬 Railway 環境
# 從本地檔案讀取 base64 cookies
try:
    with open('cookies_base64.txt', 'r') as f:
        cookies_b64 = f.read().strip()
    
    print(f"\n✅ 成功讀取 cookies_base64.txt")
    print(f"   Base64 長度: {len(cookies_b64)} 字元")
    
    # 解碼
    try:
        decoded = base64.b64decode(cookies_b64).decode('utf-8')
        print(f"\n✅ Base64 解碼成功")
        print(f"   解碼後長度: {len(decoded)} 字元")
        print(f"   前 100 字元: {decoded[:100]}")
        
        # 寫入臨時檔案
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write(decoded)
            tmp_path = tmp.name
        
        print(f"\n✅ 已寫入臨時檔案: {tmp_path}")
        
        # 檢查檔案內容
        with open(tmp_path, 'r') as f:
            lines = f.readlines()
        
        print(f"\n📊 Cookies 檔案分析:")
        print(f"   總行數: {len(lines)}")
        print(f"   Cookie 行數: {sum(1 for line in lines if not line.startswith('#') and line.strip())}")
        
        # 檢查關鍵 cookies
        important_cookies = ['LOGIN_INFO', 'SID', 'HSID', 'SSID']
        found_cookies = []
        
        for line in lines:
            for cookie_name in important_cookies:
                if cookie_name in line and not line.startswith('#'):
                    found_cookies.append(cookie_name)
        
        print(f"\n🔑 重要 Cookies:")
        for cookie in important_cookies:
            status = "✅" if cookie in found_cookies else "❌"
            print(f"   {status} {cookie}")
        
        # 清理臨時檔案
        os.unlink(tmp_path)
        
        if len(found_cookies) >= 2:
            print(f"\n✅ Cookies 格式正確,包含認證資訊")
            print(f"\n建議:")
            print(f"1. 確認 Railway 環境變數 YOUTUBE_COOKIES_B64 設定正確")
            print(f"2. 確認環境變數內容與 cookies_base64.txt 一致")
            print(f"3. Railway 重新部署後測試")
        else:
            print(f"\n⚠️ Cookies 可能不完整或已過期")
            print(f"\n建議:")
            print(f"1. 重新登入 YouTube")
            print(f"2. 重新匯出 cookies")
            print(f"3. 重新執行 setup_cookies.py")
        
    except Exception as e:
        print(f"\n❌ Base64 解碼失敗: {e}")
        print(f"\n建議:")
        print(f"1. 檢查 cookies_base64.txt 是否損壞")
        print(f"2. 重新執行 python setup_cookies.py")
        
except FileNotFoundError:
    print(f"\n❌ 找不到 cookies_base64.txt")
    print(f"\n請先執行: python setup_cookies.py")
except Exception as e:
    print(f"\n❌ 錯誤: {e}")

print("\n" + "=" * 60)
