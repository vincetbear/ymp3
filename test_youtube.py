"""
測試 YouTube Cookies 和下載功能
用於驗證 cookies 是否正確以及 yt-dlp 設定是否有效
"""

import yt_dlp
import os
import base64

def test_cookies():
    """測試 cookies 是否有效"""
    print("=" * 60)
    print("測試 1: 檢查 Cookies 檔案")
    print("=" * 60)
    
    # 檢查 cookies 檔案
    cookies_files = [
        'youtube.com_cookies.txt',
        'youtube_cookies.txt',
        'cookies.txt'
    ]
    
    cookies_file = None
    for f in cookies_files:
        if os.path.exists(f):
            cookies_file = f
            print(f"✅ 找到 cookies 檔案: {f}")
            # 顯示檔案大小
            size = os.path.getsize(f)
            print(f"   檔案大小: {size} bytes")
            break
    
    if not cookies_file:
        print("❌ 找不到 cookies 檔案")
        print("   請確認以下檔案之一存在:")
        for f in cookies_files:
            print(f"   - {f}")
        return None
    
    return cookies_file

def test_yt_dlp_version():
    """測試 yt-dlp 版本"""
    print("\n" + "=" * 60)
    print("測試 2: 檢查 yt-dlp 版本")
    print("=" * 60)
    
    try:
        import yt_dlp
        version = yt_dlp.version.__version__
        print(f"✅ yt-dlp 版本: {version}")
        
        # 檢查是否是最新版本
        if version < '2024.12.0':
            print(f"⚠️ 警告: 版本較舊,建議更新到 2024.12.6 或更新")
            print(f"   執行: pip install --upgrade yt-dlp")
        else:
            print(f"✅ 版本足夠新")
        
        return version
    except Exception as e:
        print(f"❌ 無法獲取版本: {str(e)}")
        return None

def test_video_info(cookies_file=None):
    """測試獲取影片資訊"""
    print("\n" + "=" * 60)
    print("測試 3: 獲取影片資訊")
    print("=" * 60)
    
    test_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    print(f"測試網址: {test_url}")
    
    # 使用最新的 iOS 策略
    ydl_opts = {
        'quiet': False,  # 顯示詳細資訊
        'verbose': True,  # 更詳細的輸出
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android', 'web'],
                'skip': ['hls', 'dash'],
                'player_skip': ['webpage', 'configs'],
            }
        },
        'http_headers': {
            'User-Agent': 'com.google.ios.youtube/19.29.1 (iPhone16,2; U; CPU iOS 17_5_1 like Mac OS X;)',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'X-YouTube-Client-Name': '5',
            'X-YouTube-Client-Version': '19.29.1',
        },
        'nocheckcertificate': True,
        'geo_bypass': True,
        'force_ipv4': True,
    }
    
    # 如果有 cookies,加入
    if cookies_file:
        ydl_opts['cookiefile'] = cookies_file
        print(f"🍪 使用 Cookies: {cookies_file}")
    
    print("\n開始測試...")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(test_url, download=False)
            print("\n✅ 成功獲取影片資訊!")
            print(f"   標題: {info.get('title', 'Unknown')}")
            print(f"   時長: {info.get('duration', 0)} 秒")
            print(f"   上傳者: {info.get('uploader', 'Unknown')}")
            return True
    except Exception as e:
        print(f"\n❌ 失敗: {str(e)}")
        print("\n錯誤詳情:")
        import traceback
        traceback.print_exc()
        return False

def test_different_strategies(cookies_file=None):
    """測試不同的客戶端策略"""
    print("\n" + "=" * 60)
    print("測試 4: 測試不同的客戶端策略")
    print("=" * 60)
    
    test_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    
    strategies = {
        'iOS 優先': ['ios', 'android', 'web'],
        'Android 優先': ['android', 'ios', 'web'],
        'Web 優先': ['web', 'android', 'ios'],
        '僅 iOS': ['ios'],
        '僅 Android': ['android'],
    }
    
    results = {}
    
    for name, clients in strategies.items():
        print(f"\n測試策略: {name} ({clients})")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {
                'youtube': {
                    'player_client': clients,
                    'skip': ['hls', 'dash'],
                    'player_skip': ['webpage', 'configs'],
                }
            },
            'http_headers': {
                'User-Agent': 'com.google.ios.youtube/19.29.1 (iPhone16,2; U; CPU iOS 17_5_1 like Mac OS X;)',
                'X-YouTube-Client-Name': '5',
                'X-YouTube-Client-Version': '19.29.1',
            },
            'nocheckcertificate': True,
            'force_ipv4': True,
        }
        
        if cookies_file:
            ydl_opts['cookiefile'] = cookies_file
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(test_url, download=False)
                print(f"   ✅ 成功! 標題: {info.get('title', 'Unknown')[:50]}")
                results[name] = True
        except Exception as e:
            error_msg = str(e)[:100]
            print(f"   ❌ 失敗: {error_msg}")
            results[name] = False
    
    return results

def main():
    print("\n" + "=" * 60)
    print("YouTube 下載功能測試工具")
    print("=" * 60)
    
    # 測試 1: 檢查 cookies
    cookies_file = test_cookies()
    
    # 測試 2: 檢查版本
    version = test_yt_dlp_version()
    
    # 測試 3: 測試獲取影片資訊
    success = test_video_info(cookies_file)
    
    # 測試 4: 測試不同策略
    if not success:
        print("\n由於測試 3 失敗,進行更詳細的策略測試...")
        results = test_different_strategies(cookies_file)
        
        print("\n" + "=" * 60)
        print("測試結果摘要:")
        print("=" * 60)
        for name, result in results.items():
            status = "✅ 成功" if result else "❌ 失敗"
            print(f"{name:15} {status}")
    
    # 最終建議
    print("\n" + "=" * 60)
    print("建議:")
    print("=" * 60)
    
    if success:
        print("✅ 本地測試成功!")
        print("   如果 Railway 仍有問題,請確認:")
        print("   1. Railway 環境變數 YOUTUBE_COOKIES_B64 已設定")
        print("   2. Railway 使用的 yt-dlp 版本 >= 2024.12.6")
        print("   3. 查看 Railway logs 的詳細錯誤訊息")
    else:
        print("❌ 本地測試失敗")
        print("\n可能的原因:")
        print("1. yt-dlp 版本太舊 - 執行: pip install --upgrade yt-dlp")
        print("2. Cookies 無效或過期 - 重新匯出 cookies")
        print("3. 網路連線問題 - 檢查網路設定")
        print("4. YouTube 臨時封鎖 - 稍後再試")
        print("\n建議執行:")
        print("   pip install --upgrade yt-dlp")
        print("   然後重新執行此測試")

if __name__ == '__main__':
    main()
