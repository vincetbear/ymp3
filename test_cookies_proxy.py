"""
測試 cookies + 代理組合下載
"""
import yt_dlp
import os
from proxy_config import get_random_proxy, get_proxy_display

def test_download_with_cookies_and_proxy():
    """測試使用 cookies 和代理下載"""
    
    # 測試 URL - 你剛才失敗的影片
    test_url = "https://www.youtube.com/watch?v=fLyHit9OnhU"
    
    print("=" * 60)
    print("🧪 測試 YouTube 下載 (Cookies + 代理)")
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
    
    # 獲取隨機代理
    proxy_url = get_random_proxy()
    if proxy_url:
        print(f"🔒 使用代理: {get_proxy_display(proxy_url)}")
    else:
        print("⚠️ 無代理")
    
    # 設定 yt-dlp 選項
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'cookiefile': cookies_file,  # 使用 cookies
    }
    
    # 添加代理
    if proxy_url:
        ydl_opts['proxy'] = proxy_url
    
    # 使用 Android 客戶端
    ydl_opts['extractor_args'] = {
        'youtube': {
            'player_client': ['android', 'web'],
        }
    }
    
    # 只獲取資訊,不下載
    print("\n📋 測試獲取影片資訊...")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(test_url, download=False)
            
            print("\n✅ 成功獲取影片資訊!")
            print(f"📹 標題: {info.get('title', 'Unknown')}")
            print(f"⏱️ 時長: {info.get('duration', 0)} 秒")
            print(f"👤 上傳者: {info.get('uploader', 'Unknown')}")
            print(f"👁️ 觀看次數: {info.get('view_count', 0):,}")
            
            return True
            
    except Exception as e:
        print(f"\n❌ 失敗: {e}")
        return False

if __name__ == "__main__":
    success = test_download_with_cookies_and_proxy()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 測試成功! Cookies + 代理組合可以正常工作")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("💡 建議:")
        print("1. 確認 cookies 是否過期 (登入 YouTube 重新匯出)")
        print("2. 嘗試更換代理 IP")
        print("3. 檢查網路連線")
        print("=" * 60)
