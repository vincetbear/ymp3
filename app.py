from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import threading
import uuid
from datetime import datetime, timedelta
import json
import base64
import tempfile
import requests
import re
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)
CORS(app)

# 設定下載資料夾
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'downloads')
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# 儲存下載任務狀態
download_tasks = {}

def get_cookies_file():
    """從環境變數或檔案獲取 YouTube cookies"""
    # 優先使用環境變數 (Railway 部署時使用)
    cookies_b64 = os.environ.get('YOUTUBE_COOKIES_B64')
    if cookies_b64:
        try:
            # 解碼 base64 並寫入臨時檔案
            cookies_content = base64.b64decode(cookies_b64).decode('utf-8')
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
            temp_file.write(cookies_content)
            temp_file.close()
            print(f"✅ 使用環境變數中的 cookies")
            return temp_file.name
        except Exception as e:
            print(f"⚠️ 環境變數 cookies 解碼失敗: {str(e)}")
    
    # 備用: 使用本地檔案
    local_cookies = os.path.join(os.path.dirname(__file__), 'youtube_cookies.txt')
    if os.path.exists(local_cookies):
        print(f"✅ 使用本地 cookies 檔案")
        return local_cookies
    
    print("ℹ️ 未找到 cookies,使用無 cookies 模式")
    return None


# Invidious 公開實例列表 (按可靠性排序)
INVIDIOUS_INSTANCES = [
    'https://invidious.privacyredirect.com',
    'https://invidious.snopyta.org',
    'https://yewtu.be',
    'https://invidious.kavin.rocks',
    'https://vid.puffyan.us',
    'https://inv.riverside.rocks',
]

def extract_video_id(url):
    """從 YouTube URL 提取影片 ID"""
    video_id = None
    if 'youtube.com/watch' in url:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        video_id = query_params.get('v', [None])[0]
    elif 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[-1].split('?')[0]
    return video_id

def get_video_info_from_invidious(video_id):
    """使用 Invidious API 獲取影片資訊"""
    for instance in INVIDIOUS_INSTANCES:
        try:
            url = f"{instance}/api/v1/videos/{video_id}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功從 Invidious 獲取資訊: {instance}")
                return data
        except Exception as e:
            print(f"❌ Invidious 實例失敗 {instance}: {e}")
            continue
    return None

def download_from_invidious(video_id, download_type, quality):
    """使用 Invidious API 獲取下載連結"""
    info = get_video_info_from_invidious(video_id)
    if not info:
        raise Exception("無法從 Invidious 獲取影片資訊")
    
    if download_type == 'audio':
        # 獲取音訊串流
        audio_formats = [f for f in info.get('adaptiveFormats', []) if f.get('type', '').startswith('audio')]
        if not audio_formats:
            raise Exception("找不到音訊格式")
        
        # 選擇最高品質的音訊
        best_audio = max(audio_formats, key=lambda x: x.get('bitrate', 0))
        return {
            'url': best_audio.get('url'),
            'title': info.get('title', 'Unknown'),
            'ext': 'mp4',  # Invidious 通常返回 m4a
        }
    else:
        # 獲取影片串流
        if quality == 'best':
            formats = info.get('formatStreams', [])
        else:
            height = quality.replace('p', '')
            formats = [f for f in info.get('formatStreams', []) if str(f.get('resolution', '')).startswith(height)]
        
        if not formats:
            raise Exception(f"找不到 {quality} 品質的影片")
        
        best_format = formats[0]
        return {
            'url': best_format.get('url'),
            'title': info.get('title', 'Unknown'),
            'ext': 'mp4',
        }


class DownloadProgress:
    def __init__(self, task_id):
        self.task_id = task_id
        self.status = 'preparing'
        self.progress = 0
        self.speed = ''
        self.eta = ''
        self.title = ''
        self.filename = ''
        self.error = None
        
    def to_dict(self):
        return {
            'task_id': self.task_id,
            'status': self.status,
            'progress': self.progress,
            'speed': self.speed,
            'eta': self.eta,
            'title': self.title,
            'filename': self.filename,
            'error': self.error
        }

def progress_hook(d, progress_obj):
    """yt-dlp 進度回調"""
    if d['status'] == 'downloading':
        try:
            progress_obj.status = 'downloading'
            progress_obj.progress = d.get('_percent_str', '0%').strip()
            progress_obj.speed = d.get('_speed_str', 'N/A')
            progress_obj.eta = d.get('_eta_str', 'N/A')
        except:
            pass
    elif d['status'] == 'finished':
        progress_obj.status = 'processing'
        progress_obj.progress = '100%'

def download_video(task_id, url, download_type, quality):
    """下載影片或音訊 - 使用 Invidious API"""
    progress_obj = download_tasks[task_id]
    
    try:
        # 提取影片 ID
        video_id = extract_video_id(url)
        if not video_id:
            raise Exception("無效的 YouTube URL")
        
        print(f"🎬 開始下載影片 ID: {video_id}")
        progress_obj.status = 'downloading'
        
        # 使用 Invidious 獲取影片資訊和下載連結
        try:
            stream_info = download_from_invidious(video_id, download_type, quality)
            download_url = stream_info['url']
            title = stream_info['title']
            ext = 'mp3' if download_type == 'audio' else 'mp4'
            
            print(f"✅ 從 Invidious 獲取下載連結")
            progress_obj.title = title
            
            # 下載檔案
            filename = f"{task_id}_{title}.{ext}"
            # 清理檔名中的非法字元
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            filepath = os.path.join(DOWNLOAD_FOLDER, filename)
            
            # 使用 requests 下載
            response = requests.get(download_url, stream=True, timeout=300)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filepath, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress_obj.progress = f"{int(downloaded * 100 / total_size)}%"
            
            progress_obj.filename = filename
            
            # 如果是音訊且需要轉 MP3
            if download_type == 'audio' and ext != 'mp3':
                print("🔄 轉換為 MP3...")
                progress_obj.status = 'processing'
                
                # 使用 ffmpeg 轉換
                import subprocess
                mp3_filename = filename.replace(f'.{ext}', '.mp3')
                mp3_filepath = os.path.join(DOWNLOAD_FOLDER, mp3_filename)
                
                cmd = [
                    'ffmpeg', '-i', filepath,
                    '-vn', '-ar', '44100', '-ac', '2',
                    '-b:a', f'{quality}k',
                    mp3_filepath
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                
                # 刪除原始檔案
                os.remove(filepath)
                progress_obj.filename = mp3_filename
            
            progress_obj.status = 'completed'
            progress_obj.progress = '100%'
            print(f"✅ 下載完成: {progress_obj.filename}")
            
        except Exception as e:
            print(f"❌ Invidious 下載失敗,嘗試使用 yt-dlp: {e}")
            # 如果 Invidious 失敗,回退到 yt-dlp
            
            # 設定 yt-dlp 選項
            ydl_opts = {
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, f'{task_id}_%(title)s.%(ext)s'),
                'progress_hooks': [lambda d: progress_hook(d, progress_obj)],
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'geo_bypass': True,
                'force_ipv4': True,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android_embedded', 'android', 'ios'],
                        'skip': ['hls', 'dash', 'translated_subs'],
                        'player_skip': ['webpage', 'configs', 'js'],
                    }
                },
                'http_headers': {
                    'User-Agent': 'com.google.android.youtube/19.14.40 (Linux; U; Android 13; en_US)',
                },
            }
            
            if download_type == 'audio':
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': quality,
                    }],
                })
            else:
                if quality == 'best':
                    ydl_opts['format'] = 'best'
                else:
                    height = quality.replace('p', '')
                    ydl_opts['format'] = f'bestvideo[height<={height}]+bestaudio/best[height<={height}]'
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                progress_obj.title = info.get('title', 'Unknown')
                
                for file in os.listdir(DOWNLOAD_FOLDER):
                    if file.startswith(task_id):
                        progress_obj.filename = file
                        break
            
            progress_obj.status = 'completed'
            progress_obj.progress = '100%'
        
    except Exception as e:
        progress_obj.status = 'error'
        progress_obj.error = str(e)
        print(f"❌ 下載失敗: {e}")

@app.route('/')
def index():
    """主頁面"""
    return render_template('index.html')

@app.route('/api/download', methods=['POST'])
def start_download():
    """開始下載任務"""
    data = request.json
    url = data.get('url', '').strip()
    download_type = data.get('type', 'video')
    quality = data.get('quality', 'best')
    
    if not url:
        return jsonify({'error': '請提供 YouTube 網址'}), 400
    
    # 清理和驗證 URL
    # 移除播放清單參數,只保留影片 ID
    import re
    from urllib.parse import urlparse, parse_qs
    
    # 提取影片 ID
    video_id = None
    if 'youtube.com/watch' in url:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        video_id = query_params.get('v', [None])[0]
    elif 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[-1].split('?')[0]
    
    if video_id:
        # 重建乾淨的 URL (不含播放清單)
        url = f'https://www.youtube.com/watch?v={video_id}'
        print(f"📹 清理後的 URL: {url}")
    
    # 建立任務 ID
    task_id = str(uuid.uuid4())[:8]
    
    # 建立進度追蹤物件
    progress_obj = DownloadProgress(task_id)
    download_tasks[task_id] = progress_obj
    
    # 在背景執行下載
    thread = threading.Thread(
        target=download_video,
        args=(task_id, url, download_type, quality)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'task_id': task_id,
        'message': '下載任務已開始'
    })

@app.route('/api/progress/<task_id>')
def get_progress(task_id):
    """取得下載進度"""
    if task_id not in download_tasks:
        return jsonify({'error': '任務不存在'}), 404
    
    return jsonify(download_tasks[task_id].to_dict())

@app.route('/api/download/<task_id>')
def download_file(task_id):
    """下載檔案"""
    if task_id not in download_tasks:
        return jsonify({'error': '任務不存在'}), 404
    
    progress_obj = download_tasks[task_id]
    
    if progress_obj.status != 'completed':
        return jsonify({'error': '檔案尚未準備好'}), 400
    
    file_path = os.path.join(DOWNLOAD_FOLDER, progress_obj.filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': '檔案不存在'}), 404
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=progress_obj.filename
    )

@app.route('/api/info', methods=['POST'])
def get_video_info():
    """取得影片資訊（不下載） - 使用 Invidious API"""
    data = request.json
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': '請提供 YouTube 網址'}), 400
    
    # 提取影片 ID
    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({'error': '無效的 YouTube URL'}), 400
    
    try:
        # 優先使用 Invidious
        info = get_video_info_from_invidious(video_id)
        
        if info:
            return jsonify({
                'title': info.get('title', 'Unknown'),
                'duration': info.get('lengthSeconds', 0),
                'thumbnail': info.get('videoThumbnails', [{}])[0].get('url', ''),
                'uploader': info.get('author', 'Unknown'),
            })
        
        # 如果 Invidious 失敗,回退到 yt-dlp
        print("⚠️ Invidious 失敗,使用 yt-dlp")
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'force_ipv4': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android_embedded', 'android', 'ios'],
                }
            },
            'http_headers': {
                'User-Agent': 'com.google.android.youtube/19.14.40 (Linux; U; Android 13; en_US)',
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return jsonify({
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
                'uploader': info.get('uploader', 'Unknown'),
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# 清理舊檔案（每小時執行）
def cleanup_old_files():
    """刪除超過 1 小時的檔案"""
    try:
        now = datetime.now()
        for filename in os.listdir(DOWNLOAD_FOLDER):
            file_path = os.path.join(DOWNLOAD_FOLDER, filename)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            if now - file_time > timedelta(hours=1):
                os.remove(file_path)
                print(f"Cleaned up: {filename}")
    except Exception as e:
        print(f"Cleanup error: {e}")

# 定期清理（在生產環境中應使用 celery 或 cron）
if __name__ == '__main__':
    # 啟動時清理一次
    cleanup_old_files()
    
    # 開發環境
    app.run(host='0.0.0.0', port=5000, debug=True)
