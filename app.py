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
    """下載影片或音訊"""
    progress_obj = download_tasks[task_id]
    
    try:
        # 獲取 cookies 檔案
        cookies_file = get_cookies_file()
        
        # 設定 yt-dlp 選項 - 2024 最新策略
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, f'{task_id}_%(title)s.%(ext)s'),
            'progress_hooks': [lambda d: progress_hook(d, progress_obj)],
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'no_check_certificate': True,
            'geo_bypass': True,
            'force_ipv4': True,
        }
        
        # 暫時禁用 cookies,只使用 iOS 客戶端(測試用)
        # cookies_file = get_cookies_file()  # 暫時註解掉
        cookies_file = None  # 強制不使用 cookies
        
        # 使用 iOS 客戶端策略(最穩定)
        ydl_opts['extractor_args'] = {
            'youtube': {
                'player_client': ['ios', 'android', 'web'],
                'skip': ['hls', 'dash'],
                'player_skip': ['webpage', 'configs'],
            }
        }
        ydl_opts['http_headers'] = {
            'User-Agent': 'com.google.ios.youtube/19.29.1 (iPhone16,2; U; CPU iOS 17_5_1 like Mac OS X;)',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'X-YouTube-Client-Name': '5',
            'X-YouTube-Client-Version': '19.29.1',
        }
        print("📱 使用 iOS 客戶端模式 (不使用 cookies)")
        
        if download_type == 'audio':
            # 音訊下載 - 直接下載音訊,不轉換格式(避免需要 ffmpeg)
            ydl_opts.update({
                'format': 'bestaudio/best',
                # 移除 postprocessors 以避免需要 ffmpeg
            })
        else:
            # 影片下載
            if quality == 'best':
                ydl_opts['format'] = 'best'
            else:
                height = quality.replace('p', '')
                ydl_opts['format'] = f'bestvideo[height<={height}]+bestaudio/best[height<={height}]'
        
        # 開始下載
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            progress_obj.title = info.get('title', 'Unknown')
            
            # 找到下載的檔案
            for file in os.listdir(DOWNLOAD_FOLDER):
                if file.startswith(task_id):
                    progress_obj.filename = file
                    break
        
        progress_obj.status = 'completed'
        progress_obj.progress = '100%'
        
    except Exception as e:
        progress_obj.status = 'error'
        progress_obj.error = str(e)

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
    """取得影片資訊（不下載）"""
    data = request.json
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': '請提供 YouTube 網址'}), 400
    
    # 清理和驗證 URL
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
    
    try:
        # 獲取 cookies 檔案
        cookies_file = get_cookies_file()
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'force_ipv4': True,
        }
        
        # 根據是否有 cookies 選擇不同策略
        if cookies_file:
            # 有 cookies: 明確使用 web 客戶端
            ydl_opts['cookiefile'] = cookies_file
        # 暫時禁用 cookies,只使用 iOS 客戶端
        cookies_file = None
        
        # 使用 iOS 客戶端策略(最穩定)
        ydl_opts['extractor_args'] = {
            'youtube': {
                'player_client': ['ios', 'android', 'web'],
                'skip': ['hls', 'dash'],
                'player_skip': ['webpage', 'configs'],
            }
        }
        ydl_opts['http_headers'] = {
            'User-Agent': 'com.google.ios.youtube/19.29.1 (iPhone16,2; U; CPU iOS 17_5_1 like Mac OS X;)',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'X-YouTube-Client-Name': '5',
            'X-YouTube-Client-Version': '19.29.1',
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
