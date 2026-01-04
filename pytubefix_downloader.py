"""
使用 pytubefix 下載 YouTube 影片/音訊
音訊檔案自動轉換為 MP3
"""
from pytubefix import YouTube
import os
import subprocess

def convert_to_mp3(input_file, output_file=None, bitrate='192k'):
    """
    使用 FFmpeg 將音訊檔案轉換為 MP3
    
    Args:
        input_file: 輸入音訊檔案路徑
        output_file: 輸出 MP3 檔案路徑 (如果為 None 則自動產生)
        bitrate: MP3 位元率 (預設 192k)
    
    Returns:
        str: 輸出 MP3 檔案路徑
    """
    if output_file is None:
        # 自動產生輸出檔名 (替換副檔名為 .mp3)
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}.mp3"
    
    print(f'🎵 開始轉換為 MP3...')
    print(f'   輸入: {os.path.basename(input_file)}')
    print(f'   輸出: {os.path.basename(output_file)}')
    print(f'   位元率: {bitrate}')
    
    # FFmpeg 指令
    cmd = [
        'ffmpeg',
        '-i', input_file,           # 輸入檔案
        '-vn',                       # 不處理影片
        '-ar', '44100',              # 取樣率 44.1kHz
        '-ac', '2',                  # 立體聲
        '-b:a', bitrate,             # 位元率
        '-y',                        # 覆蓋輸出檔案
        output_file
    ]
    
    try:
        # 執行 FFmpeg
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        
        # 檢查輸出檔案
        if os.path.exists(output_file):
            input_size = os.path.getsize(input_file) / (1024 * 1024)
            output_size = os.path.getsize(output_file) / (1024 * 1024)
            print(f'✅ 轉換完成!')
            print(f'   原始檔案: {input_size:.2f} MB')
            print(f'   MP3 檔案: {output_size:.2f} MB')
            
            # 刪除原始檔案
            os.remove(input_file)
            print(f'🗑️  已刪除原始檔案: {os.path.basename(input_file)}')
            
            return output_file
        else:
            raise Exception('MP3 檔案未產生')
            
    except subprocess.CalledProcessError as e:
        print(f'❌ FFmpeg 轉換失敗:')
        print(f'   錯誤訊息: {e.stderr.decode("utf-8", errors="ignore")}')
        raise
    except Exception as e:
        print(f'❌ 轉換錯誤: {e}')
        raise


def download_video(url, output_path='downloads', quality='highest'):
    """
    下載 YouTube 影片
    
    Args:
        url: YouTube 影片網址
        output_path: 下載路徑
        quality: 畫質選擇 (highest, 1080p, 720p, 480p, 360p)
    
    Returns:
        str: 下載的檔案路徑
    """
    print(f'📹 下載影片模式')
    print(f'   畫質: {quality}')
    
    # 建立 YouTube 物件（使用預設 ANDROID_VR 客戶端）
    yt = YouTube(url)
    
    # 根據畫質選擇串流
    if quality == 'highest':
        # 最高畫質 (progressive - 包含音訊)
        stream = yt.streams.filter(progressive=True).order_by('resolution').desc().first()
    else:
        # 特定解析度
        stream = yt.streams.filter(progressive=True, res=quality).first()
        if not stream:
            print(f'⚠️  找不到 {quality} 畫質,使用最高畫質')
            stream = yt.streams.filter(progressive=True).order_by('resolution').desc().first()
    
    print(f'   選擇串流: {stream}')
    
    # 下載
    os.makedirs(output_path, exist_ok=True)
    file_path = stream.download(output_path=output_path)
    
    print(f'✅ 影片下載完成: {os.path.basename(file_path)}')
    return file_path


def download_audio(url, output_path='downloads', bitrate='192k'):
    """
    下載 YouTube 音訊並轉換為 MP3
    
    Args:
        url: YouTube 影片網址
        output_path: 下載路徑
        bitrate: MP3 位元率 (128k, 192k, 320k)
    
    Returns:
        str: MP3 檔案路徑
    """
    print(f'🎵 下載音訊模式 (轉換為 MP3)')
    print(f'   位元率: {bitrate}')
    
    # 建立 YouTube 物件（使用預設 ANDROID_VR 客戶端）
    yt = YouTube(url)
    
    # 獲取最高品質音訊
    stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
    
    print(f'   選擇串流: {stream}')
    print(f'   音訊格式: {stream.mime_type}')
    print(f'   音訊編碼: {stream.audio_codec}')
    print(f'   位元率: {stream.abr}')
    
    # 下載音訊
    os.makedirs(output_path, exist_ok=True)
    audio_file = stream.download(output_path=output_path)
    
    print(f'✅ 音訊下載完成: {os.path.basename(audio_file)}')
    
    # 轉換為 MP3
    mp3_file = convert_to_mp3(audio_file, bitrate=bitrate)
    
    return mp3_file


def get_video_info(url):
    """
    獲取影片資訊
    
    Args:
        url: YouTube 影片網址
    
    Returns:
        dict: 影片資訊
    """
    # 使用預設 ANDROID_VR 客戶端
    yt = YouTube(url)
    
    return {
        'title': yt.title,
        'author': yt.author,
        'length': yt.length,
        'views': yt.views,
        'description': yt.description,
        'thumbnail_url': yt.thumbnail_url,
        'publish_date': str(yt.publish_date) if yt.publish_date else None,
        'keywords': yt.keywords if hasattr(yt, 'keywords') else []
    }


# 測試程式碼
if __name__ == '__main__':
    # 測試 URL
    test_url = 'https://www.youtube.com/watch?v=fLyHit9OnhU'
    
    print('='*60)
    print('🎬 pytubefix YouTube 下載測試')
    print('='*60)
    print(f'影片 URL: {test_url}\n')
    
    # 獲取影片資訊
    try:
        print('📋 獲取影片資訊...')
        info = get_video_info(test_url)
        print(f'標題: {info["title"]}')
        print(f'作者: {info["author"]}')
        print(f'長度: {info["length"]} 秒')
        print(f'觀看次數: {info["views"]:,}')
        print()
    except Exception as e:
        print(f'❌ 獲取資訊失敗: {e}\n')
    
    # 測試下載音訊並轉 MP3
    try:
        print('='*60)
        print('測試 1: 下載音訊並轉換為 MP3')
        print('='*60)
        mp3_file = download_audio(test_url, output_path='test_downloads', bitrate='192k')
        print(f'\n✅ 最終檔案: {mp3_file}\n')
    except Exception as e:
        print(f'❌ 下載音訊失敗: {e}\n')
        import traceback
        traceback.print_exc()
    
    # 測試下載影片
    try:
        print('='*60)
        print('測試 2: 下載影片')
        print('='*60)
        video_file = download_video(test_url, output_path='test_downloads', quality='360p')
        print(f'\n✅ 最終檔案: {video_file}\n')
    except Exception as e:
        print(f'❌ 下載影片失敗: {e}\n')
        import traceback
        traceback.print_exc()
    
    print('='*60)
    print('✅ 測試完成!')
    print('='*60)
