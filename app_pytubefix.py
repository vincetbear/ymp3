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

app = Flask(__name__)
CORS(app)

# 設定下載資料夾
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'downloads')
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# 儲存下載任務狀態
download_tasks = {}


def convert_to_mp3(input_file, bitrate='192k'):
    """
    使用 FFmpeg 將音訊轉換為 MP3
    
    Args:
        input_file: 輸入音訊檔案
        bitrate: MP3 位元率
    
    Returns:
        str: MP3 檔案路徑
    """
    output_file = os.path.splitext(input_file)[0] + '.mp3'
    
    print(f'🎵 開始轉換為 MP3: {os.path.basename(input_file)}')
    print(f'   輸入檔案: {input_file}')
    print(f'   輸出檔案: {output_file}')
    print(f'   位元率: {bitrate}')
    
    # 檢查 FFmpeg 是否可用
    try:
        ffmpeg_check = subprocess.run(
            ['ffmpeg', '-version'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            timeout=5
        )
        if ffmpeg_check.returncode != 0:
            raise Exception('FFmpeg 未正確安裝')
        print('✅ FFmpeg 可用')
    except FileNotFoundError:
        print('❌ 錯誤: 找不到 FFmpeg')
        return input_file
    except Exception as e:
        print(f'❌ FFmpeg 檢查失敗: {e}')
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
        print(f'🔄 執行轉換命令...')
        result = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=True,
            timeout=300  # 5 分鐘超時
        )
        
        if os.path.exists(output_file):
            output_size = os.path.getsize(output_file)
            input_size = os.path.getsize(input_file)
            
            # 刪除原始檔案
            os.remove(input_file)
            
            print(f'✅ MP3 轉換完成!')
            print(f'   原始大小: {input_size / (1024*1024):.2f} MB')
            print(f'   MP3 大小: {output_size / (1024*1024):.2f} MB')
            print(f'   檔案名稱: {os.path.basename(output_file)}')
            
            return output_file
        else:
            raise Exception('MP3 檔案未產生')
            
    except subprocess.TimeoutExpired:
        print(f'❌ MP3 轉換超時 (5 分鐘)')
        return input_file
    except subprocess.CalledProcessError as e:
        print(f'❌ MP3 轉換失敗 (FFmpeg 錯誤)')
        print(f'   返回碼: {e.returncode}')
        print(f'   錯誤輸出: {e.stderr.decode("utf-8", errors="ignore")[:500]}')
        return input_file
    except Exception as e:
        print(f'❌ MP3 轉換失敗: {e}')
        import traceback
        traceback.print_exc()
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
        print(f'✅ 下載完成: {os.path.basename(file_path)}')
        print(f'   檔案大小: {os.path.getsize(file_path) / (1024*1024):.2f} MB')
        print(f'   檔案格式: {os.path.splitext(file_path)[1]}')
        
        # 如果是音訊,轉換為 MP3
        if download_type == 'audio':
            print(f'🔄 音訊模式 - 開始轉換為 MP3...')
            download_tasks[task_id]['status'] = 'converting'
            download_tasks[task_id]['message'] = '正在轉換為 MP3...'
            download_tasks[task_id]['progress'] = 95
            
            original_file = file_path
            file_path = convert_to_mp3(file_path)
            
            # 檢查是否成功轉換
            if file_path.endswith('.mp3'):
                print(f'✅ MP3 轉換成功!')
            else:
                print(f'⚠️ 警告: 轉換失敗,返回原始檔案 {os.path.splitext(file_path)[1]}')
                download_tasks[task_id]['message'] = f'下載完成 (轉換失敗,格式: {os.path.splitext(file_path)[1]})'
        
        # 下載完成
        download_tasks[task_id]['status'] = 'completed'
        download_tasks[task_id]['message'] = '下載完成'
        download_tasks[task_id]['file_path'] = file_path
        download_tasks[task_id]['filename'] = os.path.basename(file_path)
        download_tasks[task_id]['progress'] = 100
        
    except Exception as e:
        download_tasks[task_id]['status'] = 'error'
        download_tasks[task_id]['message'] = str(e)
        print(f'❌ 下載錯誤: {e}')
        import traceback
        traceback.print_exc()


@app.route('/')
def index():
    """首頁"""
    return render_template('index.html')


@app.route('/api/info', methods=['POST'])
def get_video_info():
    """獲取影片資訊"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': '請提供影片網址'}), 400
        
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
        
        return jsonify(info)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
        return jsonify({'error': str(e)}), 500


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
    if task_id not in download_tasks:
        return jsonify({'error': '任務不存在'}), 404
    
    task = download_tasks[task_id]
    
    if task['status'] != 'completed':
        return jsonify({'error': '下載未完成'}), 400
    
    file_path = task.get('file_path')
    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': '檔案不存在'}), 404
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=task['filename']
    )


def cleanup_old_files():
    """清理超過 1 小時的檔案"""
    try:
        now = datetime.now()
        for filename in os.listdir(DOWNLOAD_FOLDER):
            file_path = os.path.join(DOWNLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if now - file_time > timedelta(hours=1):
                    os.remove(file_path)
                    print(f'🗑️  清理舊檔案: {filename}')
    except Exception as e:
        print(f'⚠️ 清理檔案錯誤: {e}')


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
    app.run(host='0.0.0.0', port=port, debug=True)
