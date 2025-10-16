"""
Flask Web 應用 - 使用 pytubefix 下載 YouTube 影片/音訊
"""
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
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
        try:
            download_tasks[task_id]['status'] = 'downloading'
            download_tasks[task_id]['message'] = '正在下載...'
            
            # 建立 YouTube 物件
            yt = YouTube(
                url,
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
            
        except Exception as e:
            download_tasks[task_id]['status'] = 'error'
            download_tasks[task_id]['message'] = str(e)
            app.logger.error(f'下載錯誤 (task_id={task_id}): {e}', exc_info=True)


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
    return jsonify({'error': '找不到資源'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500 錯誤處理"""
    app.logger.error(f'伺服器錯誤: {error}')
    return jsonify({'error': '伺服器內部錯誤'}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """413 錯誤處理（請求實體過大）"""
    return jsonify({'error': '檔案過大'}), 413


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


@app.route('/api/info', methods=['POST'])
def get_video_info():
    """獲取影片資訊"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': '請提供影片網址'}), 400
        
        # 驗證 URL 安全性
        try:
            url = validate_youtube_url(url)
            url = clean_youtube_url(url)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        # 建立 YouTube 物件
        yt = YouTube(url)
        
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
        
        app.logger.info(f'獲取影片資訊成功: {yt.title}')
        return jsonify(info)
        
    except ValueError as e:
        app.logger.warning(f'URL 驗證失敗: {e}')
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        app.logger.error(f'獲取影片資訊失敗: {e}', exc_info=True)
        return jsonify({'error': '無法獲取影片資訊，請確認網址是否正確'}), 500


@app.route('/api/download', methods=['POST'])
def download_video():
    """開始下載任務"""
    try:
        data = request.get_json()
        url = data.get('url')
        download_type = data.get('type', 'video')  # video 或 audio
        quality = data.get('quality', 'best')      # best, 1080p, 720p, 480p, 360p
        
        if not url:
            return jsonify({'error': '請提供影片網址'}), 400
        
        # 驗證 URL 安全性
        try:
            url = validate_youtube_url(url)
            url = clean_youtube_url(url)
        except ValueError as e:
            app.logger.warning(f'下載請求 URL 無效: {e}')
            return jsonify({'error': str(e)}), 400
        
        # 驗證下載類型
        if download_type not in ['video', 'audio']:
            return jsonify({'error': '無效的下載類型'}), 400
        
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
            'created_at': datetime.now().isoformat()
        }
        
        app.logger.info(f'建立下載任務: task_id={task_id}, type={download_type}, quality={quality}')
        
        # 啟動背景執行緒
        thread = threading.Thread(
            target=download_video_thread,
            args=(task_id, url, download_type, quality)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'task_id': task_id,
            'message': '下載任務已建立'
        })
        
    except Exception as e:
        app.logger.error(f'建立下載任務失敗: {e}', exc_info=True)
        return jsonify({'error': '建立下載任務失敗'}), 500


@app.route('/api/progress/<task_id>')
def get_progress(task_id):
    """獲取下載進度"""
    if task_id not in download_tasks:
        return jsonify({'error': '任務不存在'}), 404
    
    task = download_tasks[task_id]
    return jsonify(task)


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


# 啟動時清理舊檔案
cleanup_old_files()

# 定期清理 (每小時)
def periodic_cleanup():
    import time
    while True:
        time.sleep(3600)  # 1 小時
        cleanup_old_files()

cleanup_thread = threading.Thread(target=periodic_cleanup)
cleanup_thread.daemon = True
cleanup_thread.start()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
