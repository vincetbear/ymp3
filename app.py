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
from proxy_config import get_random_proxy, get_proxy_display

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
    # 嘗試多個可能的 cookies 檔案名稱
    possible_cookies = [
        'youtube_cookies.txt',
        'youtube.com_cookies.txt',
        'www.youtube.com_cookies.txt'
    ]
    
    for cookie_file in possible_cookies:
        local_cookies = os.path.join(os.path.dirname(__file__), cookie_file)
        if os.path.exists(local_cookies):
            print(f"✅ 使用本地 cookies 檔案: {cookie_file}")
            return local_cookies
    
    print("ℹ️ 未找到 cookies,使用無 cookies 模式")
    return None


# Invidious 公開實例列表 (按可靠性排序) - 更新到 2025 年仍在運作的實例
INVIDIOUS_INSTANCES = [
    'https://inv.nadeko.net',
    'https://invidious.fdn.fr',
    'https://inv.tux.pizza',
    'https://invidious.privacyredirect.com',
    'https://yewtu.be',
    'https://invidious.nerdvpn.de',
    'https://vid.puffyan.us',
    'https://invidious.drgns.space',
    'https://invidious.protokolla.fi',
    'https://yt.artemislena.eu',
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
            print(f"🔍 嘗試 Invidious 實例: {instance}")
            response = requests.get(url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功從 Invidious 獲取資訊: {instance}")
                print(f"📹 影片標題: {data.get('title', 'Unknown')}")
                return data
            else:
                print(f"⚠️ HTTP {response.status_code} from {instance}")
        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout: {instance}")
        except Exception as e:
            print(f"❌ 錯誤 {instance}: {str(e)[:100]}")
            continue
    print("❌ 所有 Invidious 實例都失敗")
    return None

def download_from_invidious(video_id, download_type, quality):
    """使用 Invidious API 獲取下載連結"""
    info = get_video_info_from_invidious(video_id)
    if not info:
        raise Exception("無法從 Invidious 獲取影片資訊")
    
    print(f"📊 獲取的格式數量: adaptiveFormats={len(info.get('adaptiveFormats', []))}, formatStreams={len(info.get('formatStreams', []))}")
    
    if download_type == 'audio':
        # 優先使用 adaptiveFormats (分離的音訊)
        audio_formats = [f for f in info.get('adaptiveFormats', []) if f.get('type', '').startswith('audio')]
        
        # 如果沒有,嘗試從 formatStreams 獲取
        if not audio_formats:
            print("⚠️ adaptiveFormats 中沒有音訊,嘗試 formatStreams")
            audio_formats = info.get('formatStreams', [])
        
        if not audio_formats:
            raise Exception("找不到任何音訊格式")
        
        # 選擇最高品質的音訊
        best_audio = max(audio_formats, key=lambda x: x.get('bitrate', 0))
        print(f"🎵 選擇音訊格式: bitrate={best_audio.get('bitrate')}, type={best_audio.get('type')}")
        
        return {
            'url': best_audio.get('url'),
            'title': info.get('title', 'Unknown'),
            'ext': 'm4a',
        }
    else:
        # 獲取影片串流
        if quality == 'best':
            formats = info.get('formatStreams', [])
        else:
            height = quality.replace('p', '')
            formats = [f for f in info.get('formatStreams', []) if str(f.get('resolution', '')).startswith(height)]
        
        if not formats:
            # 回退到 adaptiveFormats
            formats = info.get('adaptiveFormats', [])
        
        if not formats:
            raise Exception(f"找不到任何影片格式")
        
        best_format = formats[0]
        print(f"🎬 選擇影片格式: resolution={best_format.get('resolution')}, type={best_format.get('type')}")
        
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
    """下載影片或音訊 - 使用 yt-dlp + 代理"""
    progress_obj = download_tasks[task_id]
    
    try:
        print(f"🎬 開始下載: {url}")
        progress_obj.status = 'downloading'
        
        # 設定 yt-dlp 選項
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, f'{task_id}_%(title)s.%(ext)s'),
            'progress_hooks': [lambda d: progress_hook(d, progress_obj)],
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
        }
        
        # 使用 cookies (重要: 避免 bot 偵測)
        cookies_file = get_cookies_file()
        if cookies_file:
            ydl_opts['cookiefile'] = cookies_file
            print(f"🍪 使用 cookies 檔案")
        
        # 代理設定 (可選,如果 cookies 足夠則不需要)
        # 設定為環境變數 USE_PROXY=true 才啟用
        use_proxy = os.environ.get('USE_PROXY', 'false').lower() == 'true'
        if use_proxy:
            proxy_url = get_random_proxy()
            if proxy_url:
                ydl_opts['proxy'] = proxy_url
                # 增加超時時間避免代理太慢
                ydl_opts['socket_timeout'] = 30
                print(f"🔒 使用代理: {get_proxy_display(proxy_url)}")
        
        # 使用 Android 客戶端策略
        ydl_opts['extractor_args'] = {
            'youtube': {
                'player_client': ['android', 'web'],
            }
        }
        
        # 根據下載類型設定格式
        if download_type == 'audio':
            # 音訊下載 - 不轉 MP3 (避免 ffmpeg 依賴)
            ydl_opts['format'] = 'bestaudio/best'
            print(f"🎵 下載音訊格式")
        else:
            # 影片下載
            if quality == 'best':
                ydl_opts['format'] = 'best'
            else:
                height = quality.replace('p', '')
                ydl_opts['format'] = f'bestvideo[height<={height}]+bestaudio/best[height<={height}]'
            print(f"🎬 下載影片格式: {quality}")
        
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
        print(f"✅ 下載完成: {progress_obj.filename}")
        
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
    """取得影片資訊 - 使用 yt-dlp + 代理"""
    data = request.json
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': '請提供 YouTube 網址'}), 400
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
        }
        
        # 使用 cookies (重要: 避免 bot 偵測)
        cookies_file = get_cookies_file()
        if cookies_file:
            ydl_opts['cookiefile'] = cookies_file
            print(f"🍪 使用 cookies 檔案")
        
        # 代理設定 (可選)
        use_proxy = os.environ.get('USE_PROXY', 'false').lower() == 'true'
        if use_proxy:
            proxy_url = get_random_proxy()
            if proxy_url:
                ydl_opts['proxy'] = proxy_url
                ydl_opts['socket_timeout'] = 30
                print(f"🔒 獲取資訊使用代理: {get_proxy_display(proxy_url)}")
        
        # Android 客戶端
        ydl_opts['extractor_args'] = {
            'youtube': {
                'player_client': ['android', 'web'],
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
