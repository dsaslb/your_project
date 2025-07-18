# -*- coding: utf-8 -*-
import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your-secret-key-here"
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL") or "sqlite:///C:/your_program/instance/your_program.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 성능 최적화 설정
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
        "max_overflow": 20,
    }

    # 캐시 설정 (Redis 없이 메모리 캐시 사용)
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_THRESHOLD = 1000

    # 세션 설정
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_SECURE = False  # 개발 환경
    SESSION_COOKIE_HTTPONLY = True

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


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
