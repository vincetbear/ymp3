from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import threading
import uuid
from datetime import datetime, timedelta
import json

app = Flask(__name__)
CORS(app)

# 設定下載資料夾
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'downloads')
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# 儲存下載任務狀態
download_tasks = {}

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
        # 設定 yt-dlp 選項
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, f'{task_id}_%(title)s.%(ext)s'),
            'progress_hooks': [lambda d: progress_hook(d, progress_obj)],
            'quiet': True,
            'no_warnings': True,
            # 避免 YouTube 機器人檢測
            'cookiesfrombrowser': None,
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        
        if download_type == 'audio':
            # 音訊下載
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality,
                }],
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
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            # 避免 YouTube 機器人檢測
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
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
