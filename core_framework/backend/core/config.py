"""
설정 관리 시스템
환경별 설정 분리 및 관리
"""

import os
from datetime import timedelta

class Config:
    """기본 설정 클래스"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///core_framework.db'
    
    # 세션 설정
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # 파일 업로드 설정
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    
    # 로깅 설정
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/core_framework.log'
    
    # 모듈 설정
    MODULES_DIR = 'modules'
    AUTO_LOAD_MODULES = True
    
    # API 설정
    API_PREFIX = '/api/v1'
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']

class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev_core_framework.db'
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """운영 환경 설정"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """테스트 환경 설정"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_core_framework.db'
    WTF_CSRF_ENABLED = False

# 설정 매핑
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 