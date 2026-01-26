"""
使用 yt-dlp 下載 YouTube 影片/音訊
yt-dlp 有更成熟的防封鎖機制，適合雲端伺服器使用
"""
import yt_dlp
import os
import re

def sanitize_filename(filename):
    """清理檔案名稱，移除非法字元"""
    # 移除非法字元
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # 限制長度
    if len(filename) > 200:
        filename = filename[:200]
    return filename.strip()


def download_video(url, output_path='downloads', quality='highest'):
    """
    使用 yt-dlp 下載 YouTube 影片
    
    Args:
        url: YouTube 影片網址
        output_path: 下載路徑
        quality: 畫質選擇 (highest, 1080p, 720p, 480p, 360p)
    
    Returns:
        str: 下載的檔案路徑
    """
    print(f'📹 [yt-dlp] 下載影片模式')
    print(f'   畫質: {quality}')
    
    os.makedirs(output_path, exist_ok=True)
    
    # 設定畫質格式
    if quality == 'highest':
        format_spec = 'best[ext=mp4]/best'
    elif quality in ['1080p', '720p', '480p', '360p']:
        height = quality.replace('p', '')
        format_spec = f'best[height<={height}][ext=mp4]/best[height<={height}]'
    else:
        format_spec = 'best[ext=mp4]/best'
    
    # yt-dlp 選項
    ydl_opts = {
        'format': format_spec,
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        # 防封鎖設定
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
        # 重試設定
        'retries': 5,
        'fragment_retries': 5,
        'skip_unavailable_fragments': True,
        # 額外選項
        'ignoreerrors': False,
        'no_check_certificate': True,
        'prefer_insecure': True,
        'socket_timeout': 30,
        # 使用 extractor 參數繞過限制
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android', 'web'],
                'skip': ['dash', 'hls'],
            }
        },
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # 確認檔案存在
            if os.path.exists(filename):
                print(f'✅ 影片下載完成: {os.path.basename(filename)}')
                return filename
            
            # 嘗試找到下載的檔案
            for ext in ['mp4', 'webm', 'mkv']:
                test_path = filename.rsplit('.', 1)[0] + '.' + ext
                if os.path.exists(test_path):
                    print(f'✅ 影片下載完成: {os.path.basename(test_path)}')
                    return test_path
            
            raise Exception(f'下載檔案未找到: {filename}')
            
    except Exception as e:
        print(f'❌ yt-dlp 下載失敗: {e}')
        raise


def download_audio(url, output_path='downloads', bitrate='192k'):
    """
    使用 yt-dlp 下載 YouTube 音訊並轉換為 MP3
    
    Args:
        url: YouTube 影片網址
        output_path: 下載路徑
        bitrate: MP3 位元率 (128k, 192k, 320k)
    
    Returns:
        str: MP3 檔案路徑
    """
    print(f'🎵 [yt-dlp] 下載音訊模式 (轉換為 MP3)')
    print(f'   位元率: {bitrate}')
    
    os.makedirs(output_path, exist_ok=True)
    
    # yt-dlp 選項 - 直接轉換為 MP3
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        # MP3 轉換
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': bitrate.replace('k', ''),
        }],
        # 防封鎖設定
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
        # 重試設定
        'retries': 5,
        'fragment_retries': 5,
        'skip_unavailable_fragments': True,
        # 額外選項
        'ignoreerrors': False,
        'no_check_certificate': True,
        'prefer_insecure': True,
        'socket_timeout': 30,
        # 使用 extractor 參數繞過限制
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android', 'web'],
                'skip': ['dash', 'hls'],
            }
        },
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # MP3 檔案名稱
            base_filename = ydl.prepare_filename(info)
            mp3_filename = os.path.splitext(base_filename)[0] + '.mp3'
            
            # 確認檔案存在
            if os.path.exists(mp3_filename):
                print(f'✅ MP3 下載完成: {os.path.basename(mp3_filename)}')
                return mp3_filename
            
            raise Exception(f'MP3 檔案未找到: {mp3_filename}')
            
    except Exception as e:
        print(f'❌ yt-dlp 下載失敗: {e}')
        raise


def get_video_info(url):
    """
    使用 yt-dlp 獲取影片資訊
    
    Args:
        url: YouTube 影片網址
    
    Returns:
        dict: 影片資訊
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'skip_download': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android', 'web'],
            }
        },
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return {
                'title': info.get('title', 'Unknown'),
                'author': info.get('uploader', info.get('channel', 'Unknown')),
                'length': info.get('duration', 0),
                'views': info.get('view_count', 0),
                'description': info.get('description', ''),
                'thumbnail_url': info.get('thumbnail', ''),
                'publish_date': info.get('upload_date', None),
                'keywords': info.get('tags', []) or []
            }
    except Exception as e:
        print(f'❌ yt-dlp 獲取資訊失敗: {e}')
        raise


# 測試程式碼
if __name__ == '__main__':
    # 測試 URL
    test_url = 'https://www.youtube.com/watch?v=fLyHit9OnhU'
    
    print('='*60)
    print('🎬 yt-dlp YouTube 下載測試')
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
    
    # 測試下載音訊
    try:
        print('='*60)
        print('測試: 下載音訊並轉換為 MP3')
        print('='*60)
        mp3_file = download_audio(test_url, output_path='test_downloads', bitrate='192k')
        print(f'\n✅ 最終檔案: {mp3_file}\n')
    except Exception as e:
        print(f'❌ 下載音訊失敗: {e}\n')
        import traceback
        traceback.print_exc()
    
    print('='*60)
    print('✅ 測試完成!')
    print('='*60)
