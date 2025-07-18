import os
from datetime import timedelta

class ProductionConfig:
    """프로덕션 환경 설정"""
    
    # 기본 설정
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-production-secret-key-change-this'
    DEBUG = False
    TESTING = False
    
    # 데이터베이스 설정
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///production.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 30
    }
    
    # 세션 설정
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 보안 설정
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # 로깅 설정
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/production.log'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # 캐시 설정
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # 플러그인 설정
    PLUGIN_AUTO_RELOAD = False
    PLUGIN_CACHE_ENABLED = True
    PLUGIN_PERFORMANCE_MONITORING = True
    
    # API 설정
    API_RATE_LIMIT = '100 per minute'
    API_RATE_LIMIT_STORAGE_URL = 'redis://localhost:6379/1'
    
    # 파일 업로드 설정
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip'}
    
    # 이메일 설정
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # 모니터링 설정
    ENABLE_PERFORMANCE_MONITORING = True
    ENABLE_ERROR_TRACKING = True
    ENABLE_ANALYTICS = True
    
    # 백업 설정
    BACKUP_ENABLED = True
    BACKUP_SCHEDULE = '0 2 * * *'  # 매일 새벽 2시
    BACKUP_RETENTION_DAYS = 30
    
    # SSL/TLS 설정
    SSL_CONTEXT = 'adhoc'  # 자체 서명 인증서 사용
    
    # CORS 설정
    CORS_ORIGINS = [
        'https://your-domain.com',
        'https://www.your-domain.com'
    ]
    
    # 세션 저장소 설정
    SESSION_TYPE = 'redis'
    SESSION_REDIS = 'redis://localhost:6379/2'
    
    # 워커 프로세스 설정
    WORKER_PROCESSES = 4
    WORKER_THREADS = 2
    
    # 메모리 최적화
    SQLALCHEMY_POOL_SIZE = 20
    SQLALCHEMY_MAX_OVERFLOW = 30
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_POOL_RECYCLE = 3600 