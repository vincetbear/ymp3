"""
Flask Web 應用 - 使用 pytubefix 下載 YouTube 影片/音訊
優化版本：添加速率限制、改善錯誤處理、效能監控
"""
from flask import Flask, render_template, request, jsonify, send_file, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pytubefix import YouTube
import os
import threading
import uuid
from datetime import datetime, timedelta
import json
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from threading import Semaphore
import psutil
from functools import wraps

# 導入配置和工具函數
try:
    from config import get_config
    from utils import (
        validate_youtube_url,
        clean_youtube_url,
        validate_bitrate,
        check_ffmpeg_available,
        validate_file_path,
        format_file_size,
        get_disk_space
    )
except ImportError:
    # 如果模組不存在，使用簡單的實作
    def get_config():
        class Config:
            DEBUG = False
            MAX_CONCURRENT_DOWNLOADS = 3
            FFMPEG_TIMEOUT = 300
            FILE_CLEANUP_HOURS = 1
            MAX_FILE_SIZE = 500 * 1024 * 1024
        return Config()
    
    def validate_youtube_url(url):
        return url
    
    def clean_youtube_url(url):
        return url
    
    def validate_bitrate(bitrate):
        return bitrate
    
    def check_ffmpeg_available():
        try:
            subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            return True
        except:
            return False
    
    def validate_file_path(path, base):
        return True
    
    def format_file_size(size):
        return f"{size / (1024*1024):.2f} MB"
    
    def get_disk_space(path):
        import shutil
        total, used, free = shutil.disk_usage(path)
        return (total // (1024*1024), used // (1024*1024), free // (1024*1024))

app = Flask(__name__)
config = get_config()

# 設定 Flask 配置
app.config['MAX_CONTENT_LENGTH'] = config.MAX_FILE_SIZE

CORS(app)

# 設定速率限制
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# 設定下載資料夾 (使用絕對路徑)
DOWNLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), 'downloads'))
print(f'📁 下載目錄: {DOWNLOAD_FOLDER}')

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)
    print(f'✅ 創建下載目錄: {DOWNLOAD_FOLDER}')
else:
    print(f'✅ 下載目錄已存在: {DOWNLOAD_FOLDER}')

# 設定日誌
def setup_logging(app):
    """設定應用日誌"""
    if not app.debug:
        # 確保日誌目錄存在
        log_dir = os.path.dirname(config.LOG_FILE) if hasattr(config, 'LOG_FILE') else 'logs'
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 檔案日誌處理器
        file_handler = RotatingFileHandler(
            config.LOG_FILE if hasattr(config, 'LOG_FILE') else 'logs/app.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('YouTube 下載工具啟動')

# 設定日誌
try:
    setup_logging(app)
except Exception as e:
    print(f'日誌設定失敗: {e}')

# 儲存下載任務狀態
download_tasks = {}

# 並發下載限制
download_semaphore = Semaphore(config.MAX_CONCURRENT_DOWNLOADS)

# 統一錯誤回應格式
def error_response(message, code='ERROR', status_code=400, details=None):
    """
    統一的錯誤回應格式
    
    Args:
        message: 錯誤訊息
        code: 錯誤代碼
        status_code: HTTP 狀態碼
        details: 額外的錯誤詳情
    """
    response = {
        'success': False,
        'error': {
            'code': code,
            'message': message
        },
        'request_id': g.get('request_id', None)
    }
    
    if details:
        response['error']['details'] = details
    
    return jsonify(response), status_code


def success_response(data=None, message=None):
    """
    統一的成功回應格式
    
    Args:
        data: 回應資料
        message: 成功訊息
    """
    response = {
        'success': True,
        'request_id': g.get('request_id', None)
    }
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    return jsonify(response)


# 請求ID中介層
@app.before_request
def before_request():
    """為每個請求生成唯一ID"""
    g.request_id = str(uuid.uuid4())
    g.start_time = datetime.now()


@app.after_request
def after_request(response):
    """記錄請求資訊"""
    if hasattr(g, 'start_time'):
        duration = (datetime.now() - g.start_time).total_seconds()
        app.logger.info(
            f'[{g.request_id}] {request.method} {request.path} '
            f'- {response.status_code} - {duration:.3f}s'
        )
    return response


def convert_to_mp3(input_file, bitrate='192k'):
    """
    使用 FFmpeg 將音訊轉換為 MP3
    
    Args:
        input_file: 輸入音訊檔案
        bitrate: MP3 位元率
    
    Returns:
        str: MP3 檔案路徑
    """
    # 驗證 bitrate 格式
    try:
        bitrate = validate_bitrate(bitrate)
    except:
        bitrate = '192k'  # 使用預設值
    
    # 驗證檔案存在
    if not os.path.exists(input_file):
        app.logger.error(f'輸入檔案不存在: {input_file}')
        return input_file
    
    # 驗證檔案路徑安全性
    if not validate_file_path(input_file, DOWNLOAD_FOLDER):
        app.logger.error(f'檔案路徑不安全: {input_file}')
        return input_file
    
    output_file = os.path.splitext(input_file)[0] + '.mp3'
    
    app.logger.info(f'開始轉換為 MP3: {os.path.basename(input_file)}')
    
    # 檢查 FFmpeg 是否可用
    if not check_ffmpeg_available():
        app.logger.error('FFmpeg 未正確安裝')
        return input_file
    
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-vn',
        '-ar', '44100',
        '-ac', '2',
        '-b:a', bitrate,
        '-y',
        output_file
    ]
    
    try:
        result = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=True,
            timeout=config.FFMPEG_TIMEOUT
        )
        
        if os.path.exists(output_file):
            output_size = os.path.getsize(output_file)
            input_size = os.path.getsize(input_file)
            
            # 刪除原始檔案
            os.remove(input_file)
            
            app.logger.info(f'MP3 轉換完成: {os.path.basename(output_file)} ({format_file_size(output_size)})')
            
            return output_file
        else:
            raise Exception('MP3 檔案未產生')
            
    except subprocess.TimeoutExpired:
        app.logger.error('MP3 轉換超時')
        return input_file
    except subprocess.CalledProcessError as e:
        app.logger.error(f'MP3 轉換失敗: {e}')
        return input_file
    except Exception as e:
        app.logger.error(f'MP3 轉換失敗: {e}', exc_info=True)
        return input_file


def progress_callback(stream, chunk, bytes_remaining):
    """下載進度回調"""
    task_id = getattr(stream, '_task_id', None)
    if task_id and task_id in download_tasks:
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100
        
        download_tasks[task_id]['progress'] = round(percentage, 1)
        download_tasks[task_id]['downloaded'] = bytes_downloaded
        download_tasks[task_id]['total'] = total_size


def complete_callback(stream, file_path):
    """下載完成回調"""
    task_id = getattr(stream, '_task_id', None)
    if task_id and task_id in download_tasks:
        download_tasks[task_id]['file_path'] = file_path
        print(f'✅ 下載完成: {os.path.basename(file_path)}')


def download_video_thread(task_id, url, download_type, quality):
    """背景執行緒下載影片"""
    # 使用 Semaphore 限制並發下載
    with download_semaphore:
        # 嘗試多個客戶端以避免 403 錯誤
        clients_to_try = ['IOS', 'ANDROID', 'WEB']
        last_error = None
        
        for client in clients_to_try:
            try:
                download_tasks[task_id]['status'] = 'downloading'
                download_tasks[task_id]['message'] = f'正在使用 {client} 客戶端下載...'
                
                app.logger.info(f'嘗試使用 {client} 客戶端下載 (task_id={task_id})')
                
                # 建立 YouTube 物件，使用 OAuth 認證避免 403 錯誤
                yt = YouTube(
                    url,
                    client=client,
                    use_oauth=True,
                    allow_oauth_cache=True,
                    on_progress_callback=progress_callback,
                    on_complete_callback=complete_callback
                )
                
                # 儲存 task_id 到 stream 物件
                if download_type == 'video':
                    # 影片模式
                    if quality == 'best':
                        stream = yt.streams.filter(progressive=True).order_by('resolution').desc().first()
                    else:
                        # 特定解析度
                        stream = yt.streams.filter(progressive=True, res=quality).first()
                        if not stream:
                            # 如果找不到指定解析度,使用最高畫質
                            stream = yt.streams.filter(progressive=True).order_by('resolution').desc().first()
                else:
                    # 音訊模式 - 獲取最高品質音訊
                    stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
                
                if not stream:
                    raise Exception('找不到可用的串流')
                
                # 設定 task_id
                stream._task_id = task_id
                
                # 儲存影片資訊
                download_tasks[task_id]['title'] = yt.title
                download_tasks[task_id]['author'] = yt.author
                download_tasks[task_id]['length'] = yt.length
                
                # 下載
                file_path = stream.download(output_path=DOWNLOAD_FOLDER)
                app.logger.info(f'下載完成: {os.path.basename(file_path)} ({format_file_size(os.path.getsize(file_path))})')
                
                # 如果是音訊,轉換為 MP3
                if download_type == 'audio':
                    app.logger.info('音訊模式 - 開始轉換為 MP3')
                    download_tasks[task_id]['status'] = 'converting'
                    download_tasks[task_id]['message'] = '正在轉換為 MP3...'
                    download_tasks[task_id]['progress'] = 95
                    
                    original_file = file_path
                    file_path = convert_to_mp3(file_path)
                    
                    # 檢查是否成功轉換
                    if file_path.endswith('.mp3'):
                        app.logger.info('MP3 轉換成功')
                    else:
                        app.logger.warning(f'轉換失敗，返回原始檔案 {os.path.splitext(file_path)[1]}')
                        download_tasks[task_id]['message'] = f'下載完成 (轉換失敗，格式: {os.path.splitext(file_path)[1]})'
                
                # 下載完成
                download_tasks[task_id]['status'] = 'completed'
                download_tasks[task_id]['message'] = '下載完成'
                download_tasks[task_id]['file_path'] = os.path.abspath(file_path)  # 使用絕對路徑
                download_tasks[task_id]['filename'] = os.path.basename(file_path)
                download_tasks[task_id]['progress'] = 100
                
                app.logger.info(f'任務完成: {download_tasks[task_id]["filename"]}')
                return  # 成功，退出函數
                
            except Exception as e:
                last_error = e
                app.logger.warning(f'{client} 客戶端失敗: {e}')
                continue
        
        # 所有客戶端都失敗
        download_tasks[task_id]['status'] = 'error'
        download_tasks[task_id]['message'] = f'所有客戶端都無法下載: {last_error}'
        app.logger.error(f'下載錯誤 (task_id={task_id}): {last_error}', exc_info=True)


@app.route('/')
def index():
    """首頁"""
    return render_template('index.html')


# 安全性 Headers
@app.after_request
def set_security_headers(response):
    """設定安全性 Headers"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


# 錯誤處理器
@app.errorhandler(404)
def not_found(error):
    """404 錯誤處理"""
    return error_response('找不到資源', code='NOT_FOUND', status_code=404)


@app.errorhandler(500)
def internal_error(error):
    """500 錯誤處理"""
    app.logger.error(f'[{g.get("request_id", "unknown")}] 伺服器錯誤: {error}', exc_info=True)
    return error_response('伺服器內部錯誤', code='INTERNAL_ERROR', status_code=500)


@app.errorhandler(413)
def request_entity_too_large(error):
    """413 錯誤處理（請求實體過大）"""
    return error_response('檔案過大', code='FILE_TOO_LARGE', status_code=413)


@app.errorhandler(429)
def ratelimit_handler(e):
    """速率限制錯誤處理"""
    return error_response(
        f'請求過於頻繁，請稍後再試',
        code='RATE_LIMIT_EXCEEDED',
        status_code=429,
        details={'retry_after': e.description}
    )


# 健康檢查端點
@app.route('/health')
def health_check():
    """健康檢查端點"""
    total, used, free = get_disk_space(DOWNLOAD_FOLDER)
    
    checks = {
        'status': 'healthy',
        'ffmpeg': check_ffmpeg_available(),
        'disk_space_mb': free,
        'active_tasks': len([t for t in download_tasks.values() if t['status'] in ['downloading', 'converting']])
    }
    
    # 如果 FFmpeg 不可用或磁碟空間不足，返回 503
    status_code = 200 if checks['ffmpeg'] and free > 100 else 503
    return jsonify(checks), status_code


# 系統監控端點
@app.route('/api/metrics')
@limiter.exempt  # 監控端點不受速率限制
def get_metrics():
    """獲取系統效能指標"""
    try:
        # CPU 和記憶體使用
        process = psutil.Process()
        memory_info = process.memory_info()
        
        # 磁碟空間
        total, used, free = get_disk_space(DOWNLOAD_FOLDER)
        
        # 任務統計
        task_stats = {
            'total': len(download_tasks),
            'pending': len([t for t in download_tasks.values() if t['status'] == 'pending']),
            'downloading': len([t for t in download_tasks.values() if t['status'] == 'downloading']),
            'converting': len([t for t in download_tasks.values() if t['status'] == 'converting']),
            'completed': len([t for t in download_tasks.values() if t['status'] == 'completed']),
            'error': len([t for t in download_tasks.values() if t['status'] == 'error'])
        }
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_mb': memory_info.rss // (1024 * 1024),
                'threads': threading.active_count()
            },
            'disk': {
                'total_mb': total,
                'used_mb': used,
                'free_mb': free,
                'usage_percent': round((used / total) * 100, 2) if total > 0 else 0
            },
            'tasks': task_stats,
            'downloads': {
                'folder': DOWNLOAD_FOLDER,
                'file_count': len([f for f in os.listdir(DOWNLOAD_FOLDER) if os.path.isfile(os.path.join(DOWNLOAD_FOLDER, f))])
            }
        }
        
        return success_response(data=metrics)
        
    except Exception as e:
        app.logger.error(f'獲取監控指標失敗: {e}', exc_info=True)
        return error_response('無法獲取系統指標', code='METRICS_ERROR', status_code=500)


@app.route('/api/info', methods=['POST'])
@limiter.limit("30 per minute")  # 每分鐘最多 30 次
def get_video_info():
    """獲取影片資訊"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return error_response('請提供影片網址', code='MISSING_URL', status_code=400)
        
        # 驗證 URL 安全性
        try:
            url = validate_youtube_url(url)
            url = clean_youtube_url(url)
        except ValueError as e:
            return error_response(str(e), code='INVALID_URL', status_code=400)
        
        # 嘗試多個客戶端以避免 403 錯誤
        clients_to_try = ['IOS', 'ANDROID', 'WEB']
        last_error = None
        yt = None
        
        for client in clients_to_try:
            try:
                yt = YouTube(
                    url,
                    client=client,
                    use_oauth=True,
                    allow_oauth_cache=True
                )
                # 嘗試獲取標題來驗證連接是否成功
                _ = yt.title
                break
            except Exception as e:
                last_error = e
                app.logger.warning(f'{client} 客戶端獲取資訊失敗: {e}')
                continue
        
        if yt is None:
            raise Exception(f'所有客戶端都無法獲取影片資訊: {last_error}')
        
        # 獲取可用的畫質選項
        video_streams = yt.streams.filter(progressive=True).order_by('resolution').desc()
        resolutions = []
        seen = set()
        for stream in video_streams:
            if stream.resolution and stream.resolution not in seen:
                resolutions.append(stream.resolution)
                seen.add(stream.resolution)
        
        # 獲取音訊串流資訊
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        
        info = {
            'title': yt.title,
            'author': yt.author,
            'length': yt.length,
            'views': yt.views,
            'thumbnail_url': yt.thumbnail_url,
            'description': yt.description[:200] + '...' if len(yt.description) > 200 else yt.description,
            'publish_date': str(yt.publish_date) if yt.publish_date else None,
            'resolutions': resolutions,
            'audio_bitrate': audio_stream.abr if audio_stream else None
        }
        
        app.logger.info(f'[{g.request_id}] 獲取影片資訊成功: {yt.title}')
        return success_response(data=info)
        
    except ValueError as e:
        app.logger.warning(f'[{g.request_id}] URL 驗證失敗: {e}')
        return error_response(str(e), code='INVALID_URL', status_code=400)
    except Exception as e:
        app.logger.error(f'[{g.request_id}] 獲取影片資訊失敗: {e}', exc_info=True)
        return error_response('無法獲取影片資訊，請確認網址是否正確', code='INFO_FETCH_ERROR', status_code=500)


@app.route('/api/download', methods=['POST'])
@limiter.limit("10 per hour")  # 每小時最多 10 次下載
def download_video():
    """開始下載任務"""
    try:
        data = request.get_json()
        url = data.get('url')
        download_type = data.get('type', 'video')  # video 或 audio
        quality = data.get('quality', 'best')      # best, 1080p, 720p, 480p, 360p
        
        if not url:
            return error_response('請提供影片網址', code='MISSING_URL', status_code=400)
        
        # 驗證 URL 安全性
        try:
            url = validate_youtube_url(url)
            url = clean_youtube_url(url)
        except ValueError as e:
            app.logger.warning(f'[{g.request_id}] 下載請求 URL 無效: {e}')
            return error_response(str(e), code='INVALID_URL', status_code=400)
        
        # 驗證下載類型
        if download_type not in ['video', 'audio']:
            return error_response('無效的下載類型', code='INVALID_TYPE', status_code=400)
        
        # 建立任務 ID
        task_id = str(uuid.uuid4())
        
        # 初始化任務狀態
        download_tasks[task_id] = {
            'id': task_id,
            'url': url,
            'type': download_type,
            'quality': quality,
            'status': 'pending',
            'progress': 0,
            'message': '準備下載...',
            'created_at': datetime.now().isoformat(),
            'request_id': g.request_id
        }
        
        app.logger.info(f'[{g.request_id}] 建立下載任務: task_id={task_id}, type={download_type}, quality={quality}')
        
        # 啟動背景執行緒
        thread = threading.Thread(
            target=download_video_thread,
            args=(task_id, url, download_type, quality)
        )
        thread.daemon = True
        thread.start()
        
        return success_response(
            data={'task_id': task_id},
            message='下載任務已建立'
        )
        
    except Exception as e:
        app.logger.error(f'[{g.request_id}] 建立下載任務失敗: {e}', exc_info=True)
        return error_response('建立下載任務失敗', code='TASK_CREATE_ERROR', status_code=500)


@app.route('/api/progress/<task_id>')
@limiter.limit("60 per minute")  # 輪詢進度每分鐘最多 60 次
def get_progress(task_id):
    """獲取下載進度"""
    # 驗證 task_id 格式
    try:
        uuid.UUID(task_id)
    except ValueError:
        return error_response('無效的任務 ID', code='INVALID_TASK_ID', status_code=400)
    
    if task_id not in download_tasks:
        return error_response('任務不存在', code='TASK_NOT_FOUND', status_code=404)
    
    task = download_tasks[task_id]
    return success_response(data=task)


@app.route('/api/file/<task_id>')
def download_file(task_id):
    """下載檔案"""
    app.logger.info(f'下載請求: task_id={task_id}')
    
    # 驗證 task_id 格式
    try:
        uuid.UUID(task_id)
    except ValueError:
        app.logger.warning(f'無效的任務 ID: {task_id}')
        return jsonify({'error': '無效的任務 ID'}), 400
    
    if task_id not in download_tasks:
        app.logger.warning(f'任務不存在: {task_id}')
        return jsonify({'error': '任務不存在'}), 404
    
    task = download_tasks[task_id]
    
    if task['status'] != 'completed':
        app.logger.warning(f'下載未完成: task_id={task_id}, status={task["status"]}')
        return jsonify({'error': f'下載未完成 (狀態: {task["status"]})', 'status': task['status']}), 400
    
    file_path = task.get('file_path')
    
    if not file_path:
        app.logger.error(f'檔案路徑為空: task_id={task_id}')
        return jsonify({'error': '檔案路徑不存在'}), 404
    
    # 驗證檔案路徑安全性
    if not validate_file_path(file_path, DOWNLOAD_FOLDER):
        app.logger.error(f'檔案路徑不安全: {file_path}')
        return jsonify({'error': '檔案路徑不安全'}), 403
    
    if not os.path.exists(file_path):
        app.logger.error(f'檔案不存在: {file_path}')
        return jsonify({'error': f'檔案不存在'}), 404
    
    # 檢查檔案大小
    file_size = os.path.getsize(file_path)
    if file_size > config.MAX_FILE_SIZE:
        app.logger.warning(f'檔案過大: {format_file_size(file_size)}')
        return jsonify({'error': '檔案過大，無法下載'}), 413
    
    app.logger.info(f'開始傳送檔案: {task["filename"]} ({format_file_size(file_size)})')
    
    try:
        return send_file(
            file_path,
            as_attachment=True,
            download_name=task['filename']
        )
    except Exception as e:
        app.logger.error(f'傳送檔案失敗: {e}', exc_info=True)
        return jsonify({'error': '傳送檔案失敗'}), 500


def cleanup_old_files():
    """清理超過指定時間的檔案"""
    try:
        now = datetime.now()
        cleanup_count = 0
        
        for filename in os.listdir(DOWNLOAD_FOLDER):
            try:
                file_path = os.path.join(DOWNLOAD_FOLDER, filename)
                if not os.path.isfile(file_path):
                    continue
                
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if now - file_time > timedelta(hours=config.FILE_CLEANUP_HOURS):
                    os.remove(file_path)
                    cleanup_count += 1
                    app.logger.info(f'清理舊檔案: {filename}')
            except OSError as e:
                app.logger.warning(f'無法刪除檔案 {filename}: {e}')
                continue
        
        if cleanup_count > 0:
            app.logger.info(f'清理完成，刪除 {cleanup_count} 個檔案')
            
    except Exception as e:
        app.logger.error(f'清理過程發生錯誤: {e}', exc_info=True)


def cleanup_old_tasks():
    """清理過期的任務記錄"""
    try:
        now = datetime.now()
        expired_tasks = []
        
        for task_id, task in list(download_tasks.items()):
            # 解析任務創建時間
            created_at = datetime.fromisoformat(task['created_at'])
            # 任務超過 2 小時就清理
            if now - created_at > timedelta(hours=2):
                expired_tasks.append(task_id)
        
        for task_id in expired_tasks:
            del download_tasks[task_id]
            app.logger.info(f'清理過期任務: {task_id}')
        
        if expired_tasks:
            app.logger.info(f'清理 {len(expired_tasks)} 個過期任務')
            
    except Exception as e:
        app.logger.error(f'清理任務時發生錯誤: {e}', exc_info=True)


# 啟動時清理舊檔案
cleanup_old_files()

# 定期清理 (每小時)
def periodic_cleanup():
    import time
    while True:
        time.sleep(3600)  # 1 小時
        cleanup_old_files()
        cleanup_old_tasks()

cleanup_thread = threading.Thread(target=periodic_cleanup)
cleanup_thread.daemon = True
cleanup_thread.start()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
