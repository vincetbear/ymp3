#!/usr/bin/env python3
"""
測試 WebShare 代理連線
"""
import requests
import sys

# 測試不同的代理格式
PROXY_CONFIGS = [
    {
        'name': 'HTTP 代理 - proxy.webshare.io:80',
        'url': 'http://ellpsmsi:5x76u62w6hou@proxy.webshare.io:80'
    },
    {
        'name': 'HTTP 代理 - p.webshare.io:80',
        'url': 'http://ellpsmsi:5x76u62w6hou@p.webshare.io:80'
    },
    {
        'name': 'SOCKS5 代理 - proxy.webshare.io:1080',
        'url': 'socks5://ellpsmsi:5x76u62w6hou@proxy.webshare.io:1080'
    },
    {
        'name': 'SOCKS5 代理 - p.webshare.io:1080',
        'url': 'socks5://ellpsmsi:5x76u62w6hou@p.webshare.io:1080'
    },
]

print("🧪 測試 WebShare 代理連線\n")
print("=" * 80)

working_proxies = []

for i, config in enumerate(PROXY_CONFIGS, 1):
    print(f"\n[{i}/{len(PROXY_CONFIGS)}] 測試: {config['name']}")
    
    try:
        proxies = {
            'http': config['url'],
            'https': config['url']
        }
        
        # 測試連線到 Google
        response = requests.get(
            'https://www.google.com',
            proxies=proxies,
            timeout=15,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        if response.status_code == 200:
            print(f"  ✅ 成功! Status: {response.status_code}")
            print(f"  📊 回應大小: {len(response.content)} bytes")
            working_proxies.append(config)
        else:
            print(f"  ❌ HTTP {response.status_code}")
            
    except requests.exceptions.ProxyError as e:
        print(f"  ❌ 代理錯誤: {str(e)[:100]}")
    except requests.exceptions.Timeout:
        print(f"  ⏱️  超時 (>15s)")
    except Exception as e:
        print(f"  ❌ 錯誤: {str(e)[:100]}")

print("\n" + "=" * 80)
print(f"\n📊 測試結果:")
print(f"  ✅ 可用: {len(working_proxies)}/{len(PROXY_CONFIGS)}")

if working_proxies:
    print(f"\n✨ 可用的代理:")
    for proxy in working_proxies:
        print(f"  ✅ {proxy['name']}")
        print(f"     URL: {proxy['url']}")
    
    print(f"\n🎯 建議使用:")
    print(f"  {working_proxies[0]['url']}")
else:
    print("\n😞 沒有找到可用的代理")
    print("\n可能的問題:")
    print("  1. 用戶名或密碼錯誤")
    print("  2. WebShare 帳號未啟用")
    print("  3. 代理伺服器地址已變更")
    print("\n請前往 WebShare Dashboard 確認:")
    print("  https://www.webshare.io/")
    print("  查看 'Proxy' → 'List' 取得正確的代理資訊")
