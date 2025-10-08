"""
測試只使用 cookies (不用代理)
"""
import yt_dlp
import os

def test_cookies_only():
    """測試只使用 cookies"""
    
    test_url = "https://www.youtube.com/watch?v=fLyHit9OnhU"
    
    print("=" * 60)
    print("🧪 測試 YouTube 下載 (只用 Cookies,不用代理)")
    print("=" * 60)
    
    # 找 cookies 檔案
    possible_cookies = [
        'youtube_cookies.txt',
        'youtube.com_cookies.txt',
        'www.youtube.com_cookies.txt'
    ]
    
    cookies_file = None
    for cookie_file in possible_cookies:
        if os.path.exists(cookie_file):
            cookies_file = cookie_file
            print(f"✅ 找到 cookies 檔案: {cookie_file}")
            break
    
    if not cookies_file:
        print("❌ 找不到 cookies 檔案")
        return
    
    # 設定 yt-dlp 選項
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'cookiefile': cookies_file,  # 使用 cookies
    }
    
    # 使用 Android 客戶端
    ydl_opts['extractor_args'] = {
        'youtube': {
            'player_client': ['android', 'web'],
        }
    }
    
    # 只獲取資訊
    print("\n📋 測試獲取影片資訊...")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(test_url, download=False)
            
            print("\n✅ 成功獲取影片資訊!")
            print(f"📹 標題: {info.get('title', 'Unknown')}")
            print(f"⏱️ 時長: {info.get('duration', 0)} 秒")
            print(f"👤 上傳者: {info.get('uploader', 'Unknown')}")
            
            return True
            
    except Exception as e:
        print(f"\n❌ 失敗: {e}")
        return False

if __name__ == "__main__":
    success = test_cookies_only()
    
    if success:
        print("\n🎉 Cookies 有效!")
    else:
        print("\n❌ Cookies 可能已過期,請重新匯出")
