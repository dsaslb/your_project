"""
환경 변수 설정 예시
실제 사용 시 .env 파일로 복사하여 사용하세요.
"""

import os
from pathlib import Path

# 프로젝트 루트 디렉토리
BASE_DIR = Path(__file__).resolve().parent.parent

# 환경 변수 기본값 설정
ENV_VARS = {
    # Flask 설정
    'FLASK_ENV': 'development',
    'FLASK_DEBUG': 'True',
    'SECRET_KEY': 'your-secret-key-here-change-in-production',
    'JWT_SECRET_KEY': 'your-jwt-secret-key-here-change-in-production',
    
    # 데이터베이스 설정
    'DATABASE_URL': f'sqlite:///{BASE_DIR}/your_program.db',
    # PostgreSQL 사용 시: 'postgresql://username:password@localhost:5432/your_program'
    
    # Redis 설정 (캐싱, 세션)
    'REDIS_URL': 'redis://localhost:6379/0',
    
    # API 설정
    'API_VERSION': 'v1',
    'API_TITLE': 'Your Program API',
    'API_DESCRIPTION': '업종별 맞춤형 통합 관리 시스템 API',
    
    # CORS 설정
    'CORS_ORIGINS': 'http://localhost:3000,http://127.0.0.1:3000,http://192.168.45.44:3000',
    
    # 이메일 설정 (SMTP)
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': '587',
    'MAIL_USE_TLS': 'True',
    'MAIL_USERNAME': 'your-email@gmail.com',
    'MAIL_PASSWORD': 'your-app-password',
    
    # 파일 업로드 설정
    'UPLOAD_FOLDER': str(BASE_DIR / 'uploads'),
    'MAX_CONTENT_LENGTH': '16777216',  # 16MB
    
    # 로깅 설정
    'LOG_LEVEL': 'INFO',
    'LOG_FILE': str(BASE_DIR / 'logs' / 'app.log'),
    
    # 보안 설정
    'SESSION_COOKIE_SECURE': 'False',  # 개발환경에서는 False, 운영환경에서는 True
    'SESSION_COOKIE_HTTPONLY': 'True',
    'SESSION_COOKIE_SAMESITE': 'Lax',
    
    # 모니터링 설정
    'ENABLE_METRICS': 'True',
    'METRICS_PORT': '9090',
    
    # 플러그인 설정
    'PLUGIN_DIR': str(BASE_DIR / 'plugins'),
    'PLUGIN_MARKETPLACE_URL': 'https://marketplace.yourprogram.com',
    
    # 외부 API 설정
    'KAKAO_API_KEY': 'your-kakao-api-key',
    'GOOGLE_MAPS_API_KEY': 'your-google-maps-api-key',
    
    # 개발/테스트 설정
    'TESTING': 'False',
    'MOCK_EXTERNAL_APIS': 'False',
    
    # 성능 설정
    'CACHE_TIMEOUT': '300',  # 5분
    'QUERY_TIMEOUT': '30',   # 30초
    'MAX_CONNECTIONS': '100',
}

def load_env_vars():
    """환경 변수를 로드하고 기본값을 설정합니다."""
    for key, default_value in ENV_VARS.items():
        if key not in os.environ:
            os.environ[key] = default_value

def get_env_var(key: str, default: str = None) -> str:
    """환경 변수를 안전하게 가져옵니다."""
    return os.environ.get(key, default or ENV_VARS.get(key, ''))

def get_env_bool(key: str, default: bool = False) -> bool:
    """불린 환경 변수를 가져옵니다."""
    value = get_env_var(key, str(default))
    return value.lower() in ('true', '1', 'yes', 'on')

def get_env_int(key: str, default: int = 0) -> int:
    """정수 환경 변수를 가져옵니다."""
    try:
        return int(get_env_var(key, str(default)))
    except (ValueError, TypeError):
        return default

def get_env_float(key: str, default: float = 0.0) -> float:
    """실수 환경 변수를 가져옵니다."""
    try:
        return float(get_env_var(key, str(default)))
    except (ValueError, TypeError):
        return default

# 환경별 설정
class Config:
    """기본 설정 클래스"""
    SECRET_KEY = get_env_var('SECRET_KEY')
    JWT_SECRET_KEY = get_env_var('JWT_SECRET_KEY')
    
    # 데이터베이스
    SQLALCHEMY_DATABASE_URI = get_env_var('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis
    REDIS_URL = get_env_var('REDIS_URL')
    
    # API
    API_VERSION = get_env_var('API_VERSION')
    API_TITLE = get_env_var('API_TITLE')
    API_DESCRIPTION = get_env_var('API_DESCRIPTION')
    
    # CORS
    CORS_ORIGINS = get_env_var('CORS_ORIGINS').split(',')
    
    # 이메일
    MAIL_SERVER = get_env_var('MAIL_SERVER')
    MAIL_PORT = get_env_int('MAIL_PORT')
    MAIL_USE_TLS = get_env_bool('MAIL_USE_TLS')
    MAIL_USERNAME = get_env_var('MAIL_USERNAME')
    MAIL_PASSWORD = get_env_var('MAIL_PASSWORD')
    
    # 파일 업로드
    UPLOAD_FOLDER = get_env_var('UPLOAD_FOLDER')
    MAX_CONTENT_LENGTH = get_env_int('MAX_CONTENT_LENGTH')
    
    # 로깅
    LOG_LEVEL = get_env_var('LOG_LEVEL')
    LOG_FILE = get_env_var('LOG_FILE')
    
    # 보안
    SESSION_COOKIE_SECURE = get_env_bool('SESSION_COOKIE_SECURE')
    SESSION_COOKIE_HTTPONLY = get_env_bool('SESSION_COOKIE_HTTPONLY')
    SESSION_COOKIE_SAMESITE = get_env_var('SESSION_COOKIE_SAMESITE')
    
    # 모니터링
    ENABLE_METRICS = get_env_bool('ENABLE_METRICS')
    METRICS_PORT = get_env_int('METRICS_PORT')
    
    # 플러그인
    PLUGIN_DIR = get_env_var('PLUGIN_DIR')
    PLUGIN_MARKETPLACE_URL = get_env_var('PLUGIN_MARKETPLACE_URL')
    
    # 외부 API
    KAKAO_API_KEY = get_env_var('KAKAO_API_KEY')
    GOOGLE_MAPS_API_KEY = get_env_var('GOOGLE_MAPS_API_KEY')
    
    # 개발/테스트
    TESTING = get_env_bool('TESTING')
    MOCK_EXTERNAL_APIS = get_env_bool('MOCK_EXTERNAL_APIS')
    
    # 성능
    CACHE_TIMEOUT = get_env_int('CACHE_TIMEOUT')
    QUERY_TIMEOUT = get_env_int('QUERY_TIMEOUT')
    MAX_CONNECTIONS = get_env_int('MAX_CONNECTIONS')

class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """운영 환경 설정"""
    DEBUG = False
    FLASK_ENV = 'production'
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """테스트 환경 설정"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# 설정 매핑
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
} 