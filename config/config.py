# -*- coding: utf-8 -*-
import os
from datetime import timedelta
from dotenv import load_dotenv

# 환경에 따른 .env 파일 로드
env = os.getenv('FLASK_ENV', 'development')
if env == 'production':
    load_dotenv('config/production.env')
elif env == 'development':
    load_dotenv('config/development.env')
else:
    load_dotenv('config/development.env')  # 기본값


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your-very-strong-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///instance/your_program.db"  # SQLite 기본값 (PostgreSQL 준비 완료)
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 성능 최적화 설정
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
        "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "3600")),
        "pool_pre_ping": True,
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
        "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
    }

    # 캐시 설정
    CACHE_TYPE = os.getenv("CACHE_TYPE", "simple")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "300"))
    CACHE_THRESHOLD = 1000
    CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL")

    # 세션 설정
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_SECURE = False  # 개발 환경
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_DOMAIN = None  # 개발환경: None 또는 ''로 설정 (localhost/127.0.0.1/192.168.45.44 모두 지원)

    # 로깅 설정
    LOG_LEVEL = "INFO"

    # 성능 모니터링 설정
    PERFORMANCE_MONITORING = True
    SLOW_QUERY_THRESHOLD = 1.0  # 1초 이상 쿼리 로깅

    # 보안 설정
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # 추가 보안 설정
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_DOMAIN = os.getenv("SESSION_COOKIE_DOMAIN")
    
    # JWT 설정
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # 비밀번호 정책
    PASSWORD_MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    PASSWORD_REQUIRE_UPPERCASE = os.getenv("PASSWORD_REQUIRE_UPPERCASE", "True").lower() == "true"
    PASSWORD_REQUIRE_LOWERCASE = os.getenv("PASSWORD_REQUIRE_LOWERCASE", "True").lower() == "true"
    PASSWORD_REQUIRE_DIGITS = os.getenv("PASSWORD_REQUIRE_DIGITS", "True").lower() == "true"
    PASSWORD_REQUIRE_SPECIAL = os.getenv("PASSWORD_REQUIRE_SPECIAL", "False").lower() == "true"
    
    # 로그인 시도 제한
    MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    LOGIN_LOCKOUT_DURATION = int(os.getenv("LOGIN_LOCKOUT_DURATION", "900"))  # 15분
    
    # API 요청 제한
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "200 per day;50 per hour")
    RATELIMIT_STORAGE_URL = os.getenv("RATELIMIT_STORAGE_URL", "memory://")
    
    # 추가 보안 강화 설정
    # CORS 설정
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    CORS_SUPPORTS_CREDENTIALS = True
    
    # HTTP 보안 헤더
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
    }
    
    # 파일 업로드 보안
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "16777216"))  # 16MB (16 * 1024 * 1024)
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}
    
    # 암호화 설정
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", SECRET_KEY)
    ENCRYPTION_ALGORITHM = "AES-256-GCM"
    
    # 세션 보안 강화
    SESSION_COOKIE_MAX_AGE = int(os.getenv("SESSION_COOKIE_MAX_AGE", "7200"))  # 2시간
    SESSION_COOKIE_REFRESH_EACH_REQUEST = True
    
    # 로그 보안
    LOG_SENSITIVE_DATA = os.getenv("LOG_SENSITIVE_DATA", "False").lower() == "true"
    LOG_IP_ADDRESSES = os.getenv("LOG_IP_ADDRESSES", "True").lower() == "true"
    
    # API 버전 관리
    API_VERSION = os.getenv("API_VERSION", "v1")
    API_DEPRECATION_WARNING = True


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SECRET_KEY = os.environ.get("SECRET_KEY")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret"
    WTF_CSRF_ENABLED = False
    # 필요한 추가 테스트 설정...


config_by_name = dict(
    development=DevelopmentConfig,
    production=ProductionConfig,
    default=DevelopmentConfig
) 