#!/usr/bin/env python3
"""
測試 Invidious 實例是否可用
"""
import requests
import time

# 測試影片 ID (一個流行的影片)
TEST_VIDEO_ID = "fLyHit9OnhU"

INVIDIOUS_INSTANCES = [
    'https://inv.nadeko.net',
    'https://invidious.fdn.fr',
    'https://inv.tux.pizza',
    'https://invidious.privacyredirect.com',
    'https://yewtu.be',
    'https://invidious.nerdvpn.de',
    'https://vid.puffyan.us',
    'https://invidious.drgns.space',
    'https://invidious.protokolla.fi',
    'https://yt.artemislena.eu',
]

print(f"🧪 測試 Invidious 實例 (影片 ID: {TEST_VIDEO_ID})\n")
print("=" * 80)

working_instances = []
failed_instances = []

for i, instance in enumerate(INVIDIOUS_INSTANCES, 1):
    print(f"\n[{i}/{len(INVIDIOUS_INSTANCES)}] 測試: {instance}")
    try:
        url = f"{instance}/api/v1/videos/{TEST_VIDEO_ID}"
        start_time = time.time()
        
        response = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            title = data.get('title', 'Unknown')
            author = data.get('author', 'Unknown')
            duration = data.get('lengthSeconds', 0)
            
            # 檢查是否有可用的格式
            adaptive_count = len(data.get('adaptiveFormats', []))
            stream_count = len(data.get('formatStreams', []))
            
            print(f"  ✅ 成功! ({elapsed:.2f}s)")
            print(f"  📹 標題: {title}")
            print(f"  👤 作者: {author}")
            print(f"  ⏱️  長度: {duration}s")
            print(f"  📊 格式: {adaptive_count} adaptive, {stream_count} streams")
            
            working_instances.append({
                'url': instance,
                'response_time': elapsed,
                'title': title
            })
        else:
            print(f"  ❌ HTTP {response.status_code}")
            failed_instances.append(f"{instance} (HTTP {response.status_code})")
            
    except requests.exceptions.Timeout:
        print(f"  ⏱️  超時 (>15s)")
        failed_instances.append(f"{instance} (Timeout)")
    except Exception as e:
        print(f"  ❌ 錯誤: {str(e)[:100]}")
        failed_instances.append(f"{instance} ({str(e)[:50]})")

print("\n" + "=" * 80)
print(f"\n📊 測試結果:")
print(f"  ✅ 可用: {len(working_instances)}/{len(INVIDIOUS_INSTANCES)}")
print(f"  ❌ 失敗: {len(failed_instances)}/{len(INVIDIOUS_INSTANCES)}")

if working_instances:
    print(f"\n✨ 可用的實例 (按回應時間排序):")
    working_instances.sort(key=lambda x: x['response_time'])
    for i, instance in enumerate(working_instances, 1):
        print(f"  {i}. {instance['url']} ({instance['response_time']:.2f}s)")

if failed_instances:
    print(f"\n⚠️  失敗的實例:")
    for instance in failed_instances:
        print(f"  - {instance}")

print("\n" + "=" * 80)

if working_instances:
    print(f"\n🎉 找到 {len(working_instances)} 個可用實例!")
    print(f"建議使用最快的實例: {working_instances[0]['url']}")
else:
    print("\n😞 沒有找到任何可用的 Invidious 實例")
    print("可能的原因:")
    print("  1. 網路連線問題")
    print("  2. 所有實例都暫時停機")
    print("  3. 防火牆封鎖")
