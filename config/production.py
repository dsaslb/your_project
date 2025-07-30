"""
프로덕션 환경 설정
운영 환경에서 사용할 설정값들
"""

import os
from config.config import Config

class ProductionConfig(Config):
    """프로덕션 환경 설정"""
    
    # 기본 설정
    DEBUG = False
    TESTING = False
    
    # 보안 설정
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-production-secret-key-change-this'
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # 데이터베이스 설정
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://your_user:your_password@localhost/your_program_prod'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 30
    }
    
    # Redis 설정
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # 로깅 설정
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/production.log'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # 세션 설정
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1시간
    
    # 파일 업로드 설정
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}
    
    # 이메일 설정
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # AI 모델 설정
    AI_MODELS_DIR = 'ai/models'
    AI_CACHE_SIZE = 1000
    AI_BATCH_SIZE = 32
    
    # 성능 최적화 설정
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300
    
    # 모니터링 설정
    ENABLE_METRICS = True
    METRICS_PORT = 9090
    HEALTH_CHECK_INTERVAL = 30
    
    # 백업 설정
    BACKUP_DIR = 'backups'
    BACKUP_RETENTION_DAYS = 30
    AUTO_BACKUP_ENABLED = True
    
    # 보안 설정
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_DEFAULT = "100 per minute"
    RATE_LIMIT_STORAGE_URL = REDIS_URL
    
    # SSL/TLS 설정
    SSL_CONTEXT = 'adhoc'  # 자체 서명 인증서 사용
    
    # CORS 설정
    CORS_ORIGINS = [
        'https://your-domain.com',
        'https://www.your-domain.com',
        'https://admin.your-domain.com'
    ]
    
    # API 설정
    API_RATE_LIMIT = "1000 per hour"
    API_VERSION = 'v1'
    
    # 웹소켓 설정
    SOCKETIO_ASYNC_MODE = 'eventlet'
    SOCKETIO_PING_TIMEOUT = 60
    SOCKETIO_PING_INTERVAL = 25
    
    # 플러그인 설정
    PLUGIN_DIR = 'plugins'
    PLUGIN_AUTO_LOAD = True
    PLUGIN_SANDBOX_ENABLED = True
    
    # 알림 설정
    NOTIFICATION_ENABLED = True
    NOTIFICATION_PROVIDERS = ['email', 'slack', 'telegram']
    
    # 분석 설정
    ANALYTICS_ENABLED = True
    ANALYTICS_RETENTION_DAYS = 90
    
    # 캐시 설정
    QUERY_CACHE_ENABLED = True
    QUERY_CACHE_TIMEOUT = 300
    API_CACHE_ENABLED = True
    API_CACHE_TIMEOUT = 600
    
    # 로그 설정
    ACCESS_LOG_ENABLED = True
    ERROR_LOG_ENABLED = True
    PERFORMANCE_LOG_ENABLED = True
    
    # 백업 설정
    DATABASE_BACKUP_ENABLED = True
    DATABASE_BACKUP_SCHEDULE = '0 2 * * *'  # 매일 새벽 2시
    FILE_BACKUP_ENABLED = True
    FILE_BACKUP_SCHEDULE = '0 3 * * *'  # 매일 새벽 3시 