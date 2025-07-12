"""
Core Framework Backend
확장형 모듈 시스템의 백엔드 코어
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
import os
import logging

# 전역 객체들
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name='development'):
    """Flask 앱 팩토리 함수"""
    app = Flask(__name__)
    
    # 설정 로드
    app.config.from_object(f'core.config.{config_name.capitalize()}Config')
    
    # 확장 초기화
    db.init_app(app)
    login_manager.init_app(app)
    CORS(app)
    
    # 로깅 설정
    setup_logging(app)
    
    # 모듈 시스템 초기화
    from core.modules import ModuleManager
    module_manager = ModuleManager(app)
    module_manager.load_modules()
    
    # 코어 라우트 등록
    from core.routes import register_core_routes
    register_core_routes(app)
    
    return app

def setup_logging(app):
    """로깅 설정"""
    if not app.debug:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ) 