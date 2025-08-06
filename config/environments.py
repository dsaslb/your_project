"""
환경별 설정 관리
개발, 테스트, 스테이징, 프로덕션 환경별 설정 분리
"""

import os
from typing import Dict, Any

class EnvironmentConfig:
    """환경별 설정 기본 클래스"""
    
    # 기본 설정
    DEBUG = False
    TESTING = False
    
    # 데이터베이스 설정
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 보안 설정
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')
    
    # 세션 설정
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CORS 설정
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_DEFAULT = "200 per day;50 per hour;10 per minute"
    
    # 캐시 설정
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 300
    
    # 로깅 설정
    LOG_LEVEL = "INFO"
    LOG_FILE = "logs/app.log"
    
    # 파일 업로드 설정
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = "uploads"
    
    # 이메일 설정
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    
    # Redis 설정
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # 외부 API 설정
    KAKAO_API_KEY = os.getenv('KAKAO_API_KEY')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    # 모니터링 설정
    ENABLE_METRICS = True
    METRICS_PORT = 9090
    
    # 플러그인 설정
    PLUGIN_DIR = "plugins"
    PLUGIN_AUTO_LOAD = True
    
    @classmethod
    def init_app(cls, app):
        """앱 초기화 시 추가 설정"""
        pass

class DevelopmentConfig(EnvironmentConfig):
    """개발 환경 설정"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    
    # 개발용 데이터베이스
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URL', 'sqlite:///dev.db')
    
    # 개발용 CORS (더 관대한 설정)
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://192.168.45.44:3000",
        "http://192.168.45.44:3001",
        "http://192.168.45.44:8080",
    ]
    
    # 개발용 Rate Limiting (더 관대한 설정)
    RATELIMIT_DEFAULT = "1000 per day;200 per hour;50 per minute"
    
    # 개발용 캐시
    CACHE_TYPE = "simple"
    
    @classmethod
    def init_app(cls, app):
        super().init_app(app)
        # 개발용 추가 설정
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

class TestingConfig(EnvironmentConfig):
    """테스트 환경 설정"""
    TESTING = True
    DEBUG = True
    
    # 테스트용 데이터베이스
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'sqlite:///test.db')
    
    # 테스트용 캐시
    CACHE_TYPE = "null"
    
    # 테스트용 Rate Limiting (비활성화)
    RATELIMIT_ENABLED = False
    
    # 테스트용 로깅
    LOG_LEVEL = "DEBUG"
    LOG_FILE = "logs/test.log"

class StagingConfig(EnvironmentConfig):
    """스테이징 환경 설정"""
    DEBUG = False
    
    # 스테이징용 데이터베이스
    SQLALCHEMY_DATABASE_URI = os.getenv('STAGING_DATABASE_URL')
    
    # 스테이징용 CORS
    CORS_ORIGINS = [
        "https://staging.yourprogram.com",
        "https://staging-admin.yourprogram.com",
    ]
    
    # 스테이징용 보안 설정
    SESSION_COOKIE_SECURE = True
    
    # 스테이징용 로깅
    LOG_LEVEL = "WARNING"
    LOG_FILE = "logs/staging.log"
    
    @classmethod
    def init_app(cls, app):
        super().init_app(app)
        # 스테이징용 추가 설정
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler(
                cls.LOG_FILE, maxBytes=10240000, backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('Staging startup')

class ProductionConfig(EnvironmentConfig):
    """프로덕션 환경 설정"""
    DEBUG = False
    
    # 프로덕션용 데이터베이스
    SQLALCHEMY_DATABASE_URI = os.getenv('PRODUCTION_DATABASE_URL')
    
    # 프로덕션용 CORS
    CORS_ORIGINS = [
        "https://yourprogram.com",
        "https://admin.yourprogram.com",
        "https://api.yourprogram.com",
    ]
    
    # 프로덕션용 보안 설정
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # 프로덕션용 Rate Limiting (더 엄격한 설정)
    RATELIMIT_DEFAULT = "100 per day;20 per hour;5 per minute"
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # 프로덕션용 캐시
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # 프로덕션용 로깅
    LOG_LEVEL = "ERROR"
    LOG_FILE = "logs/production.log"
    
    @classmethod
    def init_app(cls, app):
        super().init_app(app)
        # 프로덕션용 추가 설정
        import logging
        from logging.handlers import RotatingFileHandler, SMTPHandler
        
        if not app.debug and not app.testing:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            
            # 파일 로깅
            file_handler = RotatingFileHandler(
                cls.LOG_FILE, maxBytes=10240000, backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            # 이메일 로깅 (에러만)
            if app.config.get('MAIL_SERVER'):
                auth = None
                if app.config.get('MAIL_USERNAME') or app.config.get('MAIL_PASSWORD'):
                    auth = (app.config.get('MAIL_USERNAME'), app.config.get('MAIL_PASSWORD'))
                secure = None
                if app.config.get('MAIL_USE_TLS'):
                    secure = ()
                mail_handler = SMTPHandler(
                    mailhost=(app.config.get('MAIL_SERVER'), app.config.get('MAIL_PORT')),
                    fromaddr='no-reply@' + app.config.get('MAIL_SERVER'),
                    toaddrs=app.config.get('ADMINS', []),
                    subject='Your Program Failure',
                    credentials=auth,
                    secure=secure
                )
                mail_handler.setLevel(logging.ERROR)
                app.logger.addHandler(mail_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('Production startup')

# 환경별 설정 매핑
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 