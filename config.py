"""
配置管理模組
集中管理應用配置和環境變數
"""
import os
from typing import Optional


class Config:
    """基礎配置"""
    
    # Flask 配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # 下載配置
    DOWNLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), 'downloads'))
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
    
    # FFmpeg 配置
    FFMPEG_TIMEOUT = int(os.environ.get('FFMPEG_TIMEOUT', '300'))  # 5 分鐘
    MP3_DEFAULT_BITRATE = os.environ.get('MP3_DEFAULT_BITRATE', '192k')
    
    # 檔案清理配置
    FILE_CLEANUP_HOURS = int(os.environ.get('FILE_CLEANUP_HOURS', '1'))
    CLEANUP_INTERVAL_SECONDS = 3600  # 1 小時
    
    # 任務配置
    MAX_CONCURRENT_DOWNLOADS = int(os.environ.get('MAX_CONCURRENT_DOWNLOADS', '3'))
    TASK_TIMEOUT = int(os.environ.get('TASK_TIMEOUT', '600'))  # 10 分鐘
    
    # 速率限制配置
    RATE_LIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    RATE_LIMIT_DEFAULT = os.environ.get('RATE_LIMIT_DEFAULT', '200 per day, 50 per hour')
    RATE_LIMIT_DOWNLOAD = os.environ.get('RATE_LIMIT_DOWNLOAD', '10 per hour')
    
    # CORS 配置
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    
    # 日誌配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', str(10 * 1024 * 1024)))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', '10'))


class DevelopmentConfig(Config):
    """開發環境配置"""
    DEBUG = True
    TESTING = False
    RATE_LIMIT_ENABLED = False  # 開發環境不限制速率


class ProductionConfig(Config):
    """生產環境配置"""
    DEBUG = False
    TESTING = False
    
    # 確保生產環境有設定 SECRET_KEY
    @classmethod
    def validate(cls) -> None:
        """驗證生產環境配置"""
        if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            raise ValueError('生產環境必須設定 SECRET_KEY 環境變數')


class TestingConfig(Config):
    """測試環境配置"""
    DEBUG = True
    TESTING = True
    DOWNLOAD_FOLDER = '/tmp/test_downloads'
    RATE_LIMIT_ENABLED = False
    FILE_CLEANUP_HOURS = 0  # 測試環境不清理


def get_config(env: Optional[str] = None) -> Config:
    """
    獲取配置物件
    
    Args:
        env: 環境名稱 ('development', 'production', 'testing')
             如果未指定，從 FLASK_ENV 環境變數讀取
    
    Returns:
        Config: 配置物件
    """
    if env is None:
        env = os.environ.get('FLASK_ENV', 'production')
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    config_class = config_map.get(env, ProductionConfig)
    
    # 生產環境驗證配置
    if env == 'production':
        config_class.validate()
    
    return config_class()
