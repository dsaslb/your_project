import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

# 환경 인식: FLASK_ENV 값으로 .env 파일 선택
env = os.getenv('FLASK_ENV', 'development')
env_file = f'.env.{env}'
if os.path.exists(env_file):
    load_dotenv(env_file)
else:
    load_dotenv('.env.development')  # Fallback

class Config:
    """기본 설정 클래스"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///restaurant_dev.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = bool(int(os.getenv('DEBUG', '0')))
    
    # 파일 업로드 설정
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    
    # 이메일 설정
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = bool(int(os.getenv('MAIL_USE_TLS', '1')))
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    
    # 로깅 설정
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')  # 기본값 INFO
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # Slack 알림 설정
    SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL', '')
    SLACK_ENABLED = bool(os.getenv('SLACK_ENABLED', '0'))
    
    # 보안 헤더
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }
    
    # 캐시 설정
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300
    
    # 세션 설정
    PERMANENT_SESSION_LIFETIME = int(os.getenv('PERMANENT_SESSION_LIFETIME', 3600))  # 1시간
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CSRF 설정
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('CSRF_SECRET_KEY', 'csrf-key')
    
    # Rate limiting
    RATELIMIT_DEFAULT = "10 per minute"

class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True
    TESTING = False
    
    # 개발 환경에서는 보안 헤더 완화
    SECURITY_HEADERS = {}
    
    # 개발용 로깅 - 상세한 디버그 정보
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/restaurant_dev.log')

class ProductionConfig(Config):
    """운영 환경 설정"""
    DEBUG = False
    TESTING = False
    
    # 운영 환경 보안 강화
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # 운영용 로깅 - WARNING 이상만 기록
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/restaurant_prod.log')

class TestConfig(Config):
    """테스트 환경 설정"""
    TESTING = True
    DEBUG = True
    
    # In-memory-db
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # CSRF protection disabled for tests
    WTF_CSRF_ENABLED = False
    
    # Reduce password hashing rounds for speed
    BCRYPT_LOG_ROUNDS = 4
    
    # Secret key for JWT
    JWT_SECRET_KEY = 'test-secret-key'
    
    # 테스트용 보안 헤더 완화
    SECURITY_HEADERS = {}
    
    # 테스트용 로깅 - 디버그 정보 포함
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/restaurant_test.log')

# 설정 매핑
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestConfig,
    'default': DevelopmentConfig
} 