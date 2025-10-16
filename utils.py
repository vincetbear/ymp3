"""
工具函數模組
提供共用的輔助函數
"""
import os
import re
import subprocess
from urllib.parse import urlparse
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def validate_youtube_url(url: str) -> str:
    """
    驗證 YouTube URL 的安全性
    
    Args:
        url: 要驗證的 URL
    
    Returns:
        str: 驗證通過的 URL
    
    Raises:
        ValueError: URL 無效或不安全
    """
    if not url or not isinstance(url, str):
        raise ValueError("無效的 URL")
    
    # 清理 URL（移除前後空白）
    url = url.strip()
    
    # 長度檢查
    if len(url) > 2048:
        raise ValueError("URL 過長")
    
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValueError(f"URL 解析失敗: {e}")
    
    # 檢查協議
    if parsed.scheme not in ['http', 'https']:
        raise ValueError("URL 必須使用 HTTP 或 HTTPS 協議")
    
    # 檢查主機名
    allowed_hosts = [
        'www.youtube.com',
        'youtube.com',
        'youtu.be',
        'm.youtube.com'
    ]
    
    if parsed.hostname not in allowed_hosts:
        raise ValueError(f"只允許 YouTube 網址，不允許: {parsed.hostname}")
    
    # 檢查是否包含危險字符
    dangerous_chars = ['<', '>', '"', "'", '`']
    if any(char in url for char in dangerous_chars):
        raise ValueError("URL 包含不安全的字符")
    
    return url


def clean_youtube_url(url: str) -> str:
    """
    清理 YouTube URL，移除不必要的參數
    
    Args:
        url: YouTube URL
    
    Returns:
        str: 清理後的 URL
    """
    try:
        parsed = urlparse(url)
        
        # 從 youtube.com/watch 提取
        if parsed.hostname and 'youtube.com' in parsed.hostname and parsed.path == '/watch':
            from urllib.parse import parse_qs
            query_params = parse_qs(parsed.query)
            video_id = query_params.get('v', [None])[0]
            if video_id:
                return f'https://www.youtube.com/watch?v={video_id}'
        
        # 從 youtu.be 提取
        elif parsed.hostname == 'youtu.be':
            video_id = parsed.path.lstrip('/').split('?')[0]
            if video_id:
                return f'https://www.youtube.com/watch?v={video_id}'
        
    except Exception as e:
        logger.warning(f'URL 清理失敗: {e}')
    
    return url


def validate_bitrate(bitrate: str) -> str:
    """
    驗證音訊位元率格式
    
    Args:
        bitrate: 位元率字串 (如 '192k')
    
    Returns:
        str: 驗證通過的位元率
    
    Raises:
        ValueError: 位元率格式無效
    """
    if not re.match(r'^\d+k$', bitrate):
        raise ValueError(f"無效的位元率格式: {bitrate}")
    
    # 檢查位元率範圍 (32k - 320k)
    bitrate_value = int(bitrate[:-1])
    if bitrate_value < 32 or bitrate_value > 320:
        raise ValueError(f"位元率必須在 32k 到 320k 之間: {bitrate}")
    
    return bitrate


def check_ffmpeg_available() -> bool:
    """
    檢查 FFmpeg 是否可用
    
    Returns:
        bool: FFmpeg 是否可用
    """
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    except Exception as e:
        logger.error(f'FFmpeg 檢查失敗: {e}')
        return False


def get_ffmpeg_version() -> Optional[str]:
    """
    獲取 FFmpeg 版本
    
    Returns:
        Optional[str]: FFmpeg 版本字串，如果不可用則返回 None
    """
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
            text=True
        )
        if result.returncode == 0:
            # 提取版本號（第一行）
            first_line = result.stdout.split('\n')[0]
            return first_line
    except Exception as e:
        logger.error(f'獲取 FFmpeg 版本失敗: {e}')
    
    return None


def validate_file_path(file_path: str, allowed_directory: str) -> bool:
    """
    驗證檔案路徑是否在允許的目錄內
    
    Args:
        file_path: 要驗證的檔案路徑
        allowed_directory: 允許的目錄路徑
    
    Returns:
        bool: 檔案路徑是否安全
    """
    try:
        abs_file_path = os.path.abspath(file_path)
        abs_allowed_dir = os.path.abspath(allowed_directory)
        
        # 確保檔案路徑在允許的目錄內
        return abs_file_path.startswith(abs_allowed_dir + os.sep) or abs_file_path == abs_allowed_dir
    except Exception as e:
        logger.error(f'檔案路徑驗證失敗: {e}')
        return False


def format_file_size(size_bytes: int) -> str:
    """
    格式化檔案大小為人類可讀格式
    
    Args:
        size_bytes: 檔案大小（位元組）
    
    Returns:
        str: 格式化的檔案大小
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def format_duration(seconds: int) -> str:
    """
    格式化時長為人類可讀格式
    
    Args:
        seconds: 秒數
    
    Returns:
        str: 格式化的時長 (HH:MM:SS 或 MM:SS)
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def sanitize_filename(filename: str) -> str:
    """
    清理檔案名稱，移除不安全的字符
    
    Args:
        filename: 原始檔案名稱
    
    Returns:
        str: 清理後的檔案名稱
    """
    # 移除或替換不安全的字符
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # 移除前後空白
    filename = filename.strip()
    
    # 限制長度
    max_length = 200
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length - len(ext)] + ext
    
    return filename


def get_disk_space(path: str) -> Tuple[int, int, int]:
    """
    獲取磁碟空間資訊
    
    Args:
        path: 要檢查的路徑
    
    Returns:
        Tuple[int, int, int]: (總空間 MB, 已使用 MB, 可用 MB)
    """
    import shutil
    
    try:
        total, used, free = shutil.disk_usage(path)
        return (
            total // (1024 * 1024),
            used // (1024 * 1024),
            free // (1024 * 1024)
        )
    except Exception as e:
        logger.error(f'獲取磁碟空間失敗: {e}')
        return (0, 0, 0)
