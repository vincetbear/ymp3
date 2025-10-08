"""
測試 MP3 轉檔功能
"""
import yt_dlp
import os
import shutil

def test_mp3_conversion():
    """測試下載並轉換成 MP3"""
    
    # 測試 URL - 使用短影片測試
    test_url = "https://www.youtube.com/watch?v=fLyHit9OnhU"
    
    print("=" * 60)
    print("🧪 測試 MP3 轉檔功能")
    print("=" * 60)
    
    # 創建測試下載目錄
    test_folder = "test_downloads"
    if not os.path.exists(test_folder):
        os.makedirs(test_folder)
    
    # 檢查 ffmpeg 是否可用
    print("\n🔍 檢查 ffmpeg...")
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True,
                              timeout=5)
        if result.returncode == 0:
            print("✅ ffmpeg 已安裝")
            # 顯示 ffmpeg 版本
            first_line = result.stdout.split('\n')[0]
            print(f"   {first_line}")
        else:
            print("❌ ffmpeg 未安裝或無法執行")
            return False
    except FileNotFoundError:
        print("❌ ffmpeg 未安裝")
        print("\n💡 請安裝 ffmpeg:")
        print("   Windows: 下載 https://www.gyan.dev/ffmpeg/builds/")
        print("   或使用: choco install ffmpeg")
        print("   或使用: winget install ffmpeg")
        return False
    except Exception as e:
        print(f"❌ 檢查 ffmpeg 時發生錯誤: {e}")
        return False
    
    # 找 cookies 檔案
    print("\n🍪 檢查 cookies...")
    possible_cookies = [
        'youtube_cookies.txt',
        'youtube.com_cookies.txt',
        'www.youtube.com_cookies.txt'
    ]
    
    cookies_file = None
    for cookie_file in possible_cookies:
        if os.path.exists(cookie_file):
            cookies_file = cookie_file
            print(f"✅ 找到 cookies: {cookie_file}")
            break
    
    if not cookies_file:
        print("⚠️ 未找到 cookies,可能會失敗")
    
    # 設定 yt-dlp 選項
    print("\n📥 開始下載並轉換為 MP3...")
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(test_folder, 'test_%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    # 添加 cookies
    if cookies_file:
        ydl_opts['cookiefile'] = cookies_file
    
    # Android 客戶端
    ydl_opts['extractor_args'] = {
        'youtube': {
            'player_client': ['android', 'web'],
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"\n🎵 下載: {test_url}")
            info = ydl.extract_info(test_url, download=True)
            
            print("\n✅ 下載並轉換完成!")
            print(f"📹 標題: {info.get('title', 'Unknown')}")
            print(f"⏱️ 時長: {info.get('duration', 0)} 秒")
            
            # 檢查輸出檔案
            print(f"\n📁 檢查輸出檔案:")
            mp3_found = False
            for file in os.listdir(test_folder):
                print(f"   - {file}")
                if file.endswith('.mp3'):
                    mp3_found = True
                    file_path = os.path.join(test_folder, file)
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                    print(f"     大小: {file_size:.2f} MB")
            
            if mp3_found:
                print("\n🎉 成功!MP3 檔案已生成")
                return True
            else:
                print("\n⚠️ 警告:未找到 MP3 檔案")
                return False
            
    except Exception as e:
        print(f"\n❌ 失敗: {e}")
        return False
    finally:
        # 清理測試檔案
        print("\n🧹 清理測試檔案...")
        try:
            shutil.rmtree(test_folder)
            print("✅ 清理完成")
        except Exception as e:
            print(f"⚠️ 清理失敗: {e}")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("YouTube MP3 轉檔功能測試")
    print("=" * 60)
    
    success = test_mp3_conversion()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 測試通過!MP3 轉檔功能正常")
        print("\n✅ Web 版本已更新,可以推送到 Railway")
    else:
        print("❌ 測試失敗")
        print("\n💡 建議:")
        print("1. 確認 ffmpeg 已正確安裝")
        print("2. 檢查 cookies 是否有效")
        print("3. 確認網路連線正常")
    print("=" * 60)
