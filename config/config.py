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