"""測試 cookies 有效性"""
import yt_dlp
import os
import sys

def test_cookies():
    """測試本地 cookies 檔案是否有效"""
    
    cookies_file = 'youtube.com_cookies.txt'
    
    if not os.path.exists(cookies_file):
        print(f"❌ Cookies 檔案不存在: {cookies_file}")
        return False
    
    print(f"✅ 找到 cookies 檔案: {cookies_file}")
    
    # 測試影片 URL
    test_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    
    # 配置 1: 只使用 cookies,不指定 player_client
    print("\n" + "="*60)
    print("測試 1: Cookies + 預設模式 (不指定 player_client)")
    print("="*60)
    
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'cookiefile': cookies_file,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
        'nocheckcertificate': True,
        'geo_bypass': True,
        'force_ipv4': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"正在提取影片資訊: {test_url}")
            info = ydl.extract_info(test_url, download=False)
            print(f"\n✅ 測試 1 成功!")
            print(f"標題: {info.get('title')}")
            print(f"時長: {info.get('duration')} 秒")
            return True
    except Exception as e:
        print(f"\n❌ 測試 1 失敗: {str(e)}")
    
    # 配置 2: Cookies + Web 客戶端
    print("\n" + "="*60)
    print("測試 2: Cookies + Web 客戶端")
    print("="*60)
    
    ydl_opts['extractor_args'] = {
        'youtube': {
            'player_client': ['web'],
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"正在提取影片資訊: {test_url}")
            info = ydl.extract_info(test_url, download=False)
            print(f"\n✅ 測試 2 成功!")
            print(f"標題: {info.get('title')}")
            print(f"時長: {info.get('duration')} 秒")
            return True
    except Exception as e:
        print(f"\n❌ 測試 2 失敗: {str(e)}")
    
    # 配置 3: 無 cookies,使用 iOS 客戶端
    print("\n" + "="*60)
    print("測試 3: 無 Cookies + iOS 客戶端")
    print("="*60)
    
    ydl_opts_no_cookies = {
        'quiet': False,
        'no_warnings': False,
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android', 'web'],
                'skip': ['hls', 'dash'],
                'player_skip': ['webpage', 'configs'],
            }
        },
        'http_headers': {
            'User-Agent': 'com.google.ios.youtube/19.29.1 (iPhone16,2; U; CPU iOS 17_5_1 like Mac OS X;)',
        },
        'nocheckcertificate': True,
        'geo_bypass': True,
        'force_ipv4': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts_no_cookies) as ydl:
            print(f"正在提取影片資訊: {test_url}")
            info = ydl.extract_info(test_url, download=False)
            print(f"\n✅ 測試 3 成功!")
            print(f"標題: {info.get('title')}")
            print(f"時長: {info.get('duration')} 秒")
            return True
    except Exception as e:
        print(f"\n❌ 測試 3 失敗: {str(e)}")
    
    return False

if __name__ == '__main__':
    print("YouTube Cookies 有效性測試")
    print("="*60)
    
    success = test_cookies()
    
    if success:
        print("\n" + "="*60)
        print("✅ 至少有一個配置成功!")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ 所有配置都失敗,可能需要:")
        print("1. 重新登入 YouTube")
        print("2. 重新匯出 cookies")
        print("3. 檢查 cookies 是否過期")
        print("="*60)
        sys.exit(1)
