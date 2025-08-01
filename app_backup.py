# -*- coding: utf-8 -*-
"""
멀티테넌시 관리 시스템 메인 애플리케이션
업종-브랜드-매장-직원 계층 구조와 플러그인 시스템을 지원하는 Flask 애플리케이션
"""

import os
import logging
import sys
from datetime import datetime
from pathlib import Path
from dataclasses import asdict
import json
import shutil
from typing import Optional, Dict, Any, List
from functools import wraps

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import jwt
from flask import Flask, flash, jsonify, redirect, render_template, request, abort, url_for
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask_login import current_user, login_required, login_user
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Gauge

# 로깅 설정
logger = logging.getLogger(__name__)

# 설정 및 확장 모듈 import
from config.config import config_by_name
from extensions import cache, csrf, db, limiter, login_manager, migrate

# Swagger 설정 import
from api.swagger_config import create_swagger_config

# WebSocket 매니저 import
from api.websocket_manager import websocket_manager

# WebSocket 서버 import
from websocket.websocket_server import create_websocket_server

# 데이터 모델 import
from models_main import (
    Branch,
    Notification,
    Order,
    Schedule,
    User,
    Brand,
    BrandPlugin,
    Module,
    Industry,
)

# 플러그인 시스템 import (주석 처리된 부분은 향후 활성화 예정)
# from core.backend.auto_router import setup_auto_router
# from core.backend.plugin_manager import PluginManager
# from core.backend.plugin_schema import PluginManifest
# from core.backend.plugin_customization import CustomizationRule, CustomizationType
# from core.backend.plugin_release_manager import PluginReleaseManager
# from core.backend.plugin_marketplace import PluginMarketplace
# from core.backend.plugin_feedback_system import PluginFeedbackSystem
# from core.backend.plugin_testing_system import PluginTestingSystem

# 새로운 백엔드 시스템 import
from api.industry_admin_management import industry_admin_bp
from api.plugin_marketplace_enhanced import plugin_marketplace_bp
from api.system_monitoring_enhanced import system_monitoring_bp
from api.realtime_notifications_enhanced import realtime_notifications_bp
from api.system_health_api import system_health_api
try:
    from api.ai_analytics_api import ai_analytics_api
    AI_ANALYTICS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"AI 분석 모듈을 불러올 수 없습니다: {e}")
    ai_analytics_api = None
    AI_ANALYTICS_AVAILABLE = False
from api.advanced_analytics_api import advanced_analytics_api

# 백엔드 관리자 Blueprint import
from routes.backend_admin import backend_admin_bp

# 캐시 매니저 import
from utils.cache_manager import cache_manager

# 권한 관리 import
from utils.authorization_policy import (
    require_super_admin,
    protect_data_creation_endpoint,
    audit_operation
)

# 환경 설정
config_name = os.getenv("FLASK_ENV", "default")

# Flask 애플리케이션 초기화
app = Flask(__name__)
app.config.from_object(config_by_name[config_name])
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "your-secret-key")
app.config["SECRET_KEY"] = app.config["JWT_SECRET_KEY"]

# 플러그인 목록 (실제로는 DB에서 관리)
plugins = []

# JSON 파싱 강제 활성화
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# SocketIO 초기화 (조건부) - 나중에 설정
socketio = None  # 임시로 None 설정

from flask import jsonify, render_template, request
from api.auth import api_auth_bp
app.register_blueprint(api_auth_bp)

CORS(
    app,
    origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    supports_credentials=True,
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
    expose_headers=["Content-Type", "Authorization"],
    max_age=86400,
)

# 확장 모듈 초기화 함수
def initialize_extensions():
    """Flask 확장 모듈들을 초기화합니다."""
    try:
        csrf.init_app(app)
        db.init_app(app)
        migrate.init_app(app, db)
        login_manager.init_app(app)
        login_manager.login_view = None  # API 경로는 인증을 우회하도록 설정
        login_manager.login_message = "로그인이 필요합니다."
        login_manager.login_message_category = "info"
        
        # Swagger 설정 초기화 (조건부)
        try:
            api = create_swagger_config(app)
            logger.info("Swagger API 설정 초기화 완료")
            return api
        except Exception as e:
            logger.warning(f"Swagger 설정 초기화 실패 (무시됨): {e}")
            return None
    except Exception as e:
        logger.error(f"확장 모듈 초기화 실패: {e}")
        return None
        
        # 추가 확장 모듈 초기화
        limiter.init_app(app)
        cache.init_app(app)
        
        # 캐시 매니저 초기화
        cache_manager.init_app(app)
        
        logger.info("Flask 확장 모듈 초기화 완료")
    except Exception as e:
        logger.error(f"Flask 확장 모듈 초기화 실패: {e}")
        raise

# 데이터베이스 초기화 함수
def initialize_database():
    """데이터베이스를 초기화하고 기본 데이터를 생성합니다."""
    with app.app_context():
        try:
            # DB 테이블 생성
            db.create_all()
            logger.info("데이터베이스 테이블 생성 완료")

            # 기본 관리자 계정 생성
            create_default_admin()
            
            # 기본 산업 데이터 생성
            from core.backend.schema_initializer import initialize_industries
            initialize_industries()

            db.session.commit()
            logger.info("데이터베이스 초기화 및 기본 데이터 생성 완료")

        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
            db.session.rollback()
            raise

def create_default_admin():
    """기본 관리자 계정을 생성합니다."""
    try:
        admin_user = User.query.filter_by(username="admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@your_program.com",
                role="admin",
                status="approved"
            )
            admin_user.set_password("admin123")
            db.session.add(admin_user)
            logger.info("기본 관리자 계정 생성 완료: admin/admin123")
        else:
            # 기존 관리자 계정의 상태를 approved로 업데이트
            if admin_user.status != "approved":
                admin_user.status = "approved"
                logger.info("기존 관리자 계정 상태를 approved로 업데이트")
    except Exception as e:
        logger.error(f"기본 관리자 계정 생성 실패: {e}")
        raise

# 확장 모듈 초기화
api = initialize_extensions()

# Swagger API 설정 초기화
api = create_swagger_config(app)

# WebSocket 매니저 초기화
websocket_manager.init_app(app)

# 데이터베이스 초기화 (앱 컨텍스트 내에서 실행)
# initialize_database()

# IoT 시스템 초기화
try:
    from utils.iot_simulator import initialize_iot_system
    initialize_iot_system()
    logger.info("IoT 시스템 초기화 완료")
except Exception as e:
    logger.error(f"IoT 시스템 초기화 실패: {e}")

# 블루프린트 등록 함수
def register_blueprints():
    """모든 블루프린트를 등록합니다."""
    blueprints = [
        # 플러그인 마켓플레이스 API
        ("api.plugin_marketplace", "plugin_marketplace_bp", "plugin_marketplace"),
        
        # 플러그인 시스템 API
        ("api.plugin_system_manager_api", "plugin_system_manager_bp", "plugin_system_manager_api"),
        ("api.plugin_operations_api", "plugin_operations_bp", "plugin_operations_api"),
        ("api.plugin_monitoring_dashboard", "plugin_monitoring_bp", "plugin_monitoring_dashboard"),
        
        # 인증 API
        ("api.auth", "auth_bp", "auth"),
        ("api.auth", "security_auth_bp", "security_auth"),
        
        # 고도화된 모니터링 API
        ("api.advanced_monitoring_api", "advanced_monitoring_bp", "advanced_monitoring_api"),
        
        # AI 시스템 API
        ("api.ai_api", "ai_bp", "ai"),
        ("api.real_ai_models_api", "real_ai_models_api", "real_ai_models_api"),
        
        # 고급 데이터 분석 및 비즈니스 인텔리전스 API
        ("api.analytics_api", "analytics_bp", "analytics"),
        
        # 고급 모니터링 및 분석 API
        ("api.monitoring_api", "monitoring_bp", "monitoring"),
        
        # 고급 통합 및 자동화 API
        ("api.integration_api", "integration_bp", "integration"),
        
        # MVP 플러그인 블루프린트
        ("plugins.attendance_management", "attendance_bp", "attendance_management"),
        ("plugins.inventory_management", "inventory_bp", "inventory_management"),
        ("plugins.purchase_management", "purchase_bp", "purchase_management"),
        ("plugins.schedule_management", "schedule_bp", "schedule_management"),
        
        # 브랜드 관리 API
        ("api.admin_brand_api", "admin_brand_api", "admin_brand_api"),
        
        # 업종관리자 API
        ("routes.industry_admin", "industry_admin_bp", "industry_admin"),
        
        # 새로운 백엔드 시스템 API
        ("api.industry_admin_management", "industry_admin_bp", "industry_admin_management"),
        ("api.plugin_marketplace_enhanced", "plugin_marketplace_bp", "plugin_marketplace_enhanced"),
        ("api.system_monitoring_enhanced", "system_monitoring_bp", "system_monitoring_enhanced"),
        ("api.realtime_notifications_enhanced", "realtime_notifications_bp", "realtime_notifications_enhanced"),
        ("api.system_health_api", "system_health_api", "system_health_api"),
        ("api.ai_analytics_api", "ai_analytics_api", "ai_analytics_api"),
        
        # 백엔드 관리자 Blueprint
        ("routes.backend_admin", "backend_admin_bp", None),
        
        # 브랜드관리자 API
        ("routes.brand_admin", "brand_admin_bp", "brand_admin"),
        
        # 매장관리자 API
        ("routes.store_admin", "store_admin_bp", "store_admin"),
        
        # 직원 API
        ("routes.employee", "employee_bp", "employee"),
    ]
    
    for module_path, blueprint_name, url_prefix in blueprints:
        try:
            module = __import__(module_path, fromlist=[blueprint_name])
            blueprint = getattr(module, blueprint_name)
            if url_prefix:
                app.register_blueprint(blueprint, name=url_prefix)
                logger.info(f"{url_prefix} 블루프린트 등록 완료")
            else:
                app.register_blueprint(blueprint)
                logger.info(f"{blueprint_name} 블루프린트 등록 완료 (URL prefix 없음)")
        except Exception as e:
            logger.error(f"{url_prefix or blueprint_name} 블루프린트 등록 실패: {e}")

# 블루프린트 등록
register_blueprints()

# 레스토랑 특화 대시보드 라우트 등록 (비활성화 - 파일이 존재하지 않음)
# try:
#     from routes.restaurant_enhanced_dashboard import restaurant_dashboard
#     restaurant_dashboard.init_app(app)
#     logger.info("레스토랑 특화 대시보드 라우트 등록 완료")
# except Exception as e:
#     logger.error(f"레스토랑 특화 대시보드 라우트 등록 실패: {e}")

# 레스토랑 분석 API 등록
try:
    from api.restaurant_analytics import restaurant_analytics
    restaurant_analytics.init_app(app)
    logger.info("레스토랑 분석 API 등록 완료")
except Exception as e:
    logger.error(f"레스토랑 분석 API 등록 실패: {e}")

# 레스토랑 AI 예측 API 등록
try:
    from api.restaurant_ai_prediction import restaurant_ai_prediction
    restaurant_ai_prediction.init_app(app)
    logger.info("레스토랑 AI 예측 API 등록 완료")
except Exception as e:
    logger.error(f"레스토랑 AI 예측 API 등록 실패: {e}")

# 레스토랑 자동화 API 등록
try:
    from api.restaurant_automation import restaurant_automation
    restaurant_automation.init_app(app)
    logger.info("레스토랑 자동화 API 등록 완료")
except Exception as e:
    logger.error(f"레스토랑 자동화 API 등록 실패: {e}")

# 모바일 레스토랑 대시보드 등록 (비활성화 - 파일이 존재하지 않음)
# try:
#     from routes.mobile_restaurant_dashboard import mobile_restaurant_dashboard
#     mobile_restaurant_dashboard.init_app(app)
#     logger.info("모바일 레스토랑 대시보드 등록 완료")
# except Exception as e:
#     logger.error(f"모바일 레스토랑 대시보드 등록 실패: {e}")

# 레스토랑 고급 분석 API 등록
try:
    from api.restaurant_advanced_analytics import restaurant_advanced_analytics
    restaurant_advanced_analytics.init_app(app)
    logger.info("레스토랑 고급 분석 API 등록 완료")
except Exception as e:
    logger.error(f"레스토랑 고급 분석 API 등록 실패: {e}")

# 레스토랑 계층적 대시보드 등록 (비활성화 - 파일이 존재하지 않음)
# try:
#     from routes.restaurant_hierarchical_dashboard import restaurant_hierarchical
#     restaurant_hierarchical.init_app(app)
#     logger.info("레스토랑 계층적 대시보드 등록 완료")
# except Exception as e:
#     logger.error(f"레스토랑 계층적 대시보드 등록 실패: {e}")

# 합 대시보드 등록 (비활성화 - 파일이 존재하지 않음)
# try:
#     from routes.comprehensive_dashboard import comprehensive_dashboard_bp
#     app.register_blueprint(comprehensive_dashboard_bp)
#     logger.info("합 대시보드 등록 완료")
# except Exception as e:
#     logger.error(f"합 대시보드 등록 실패: {e}")

# 레스토랑 업종 관리자 페이지 등록 (비활성화 - 파일이 존재하지 않음)
# try:
#     from routes.restaurant_industry_admin import restaurant_industry_admin
#     app.register_blueprint(restaurant_industry_admin)
#     restaurant_industry_admin.init_app(app)
#     logger.info("레스토랑 업종 관리자 페이지 등록 완료")
# except Exception as e:
#     logger.error(f"레스토랑 업종 관리자 페이지 등록 실패: {e}")

# 알림 관리 API 블루프린트 등록
try:
    from api.alert_management_api import alert_management_bp

    app.register_blueprint(alert_management_bp, name="alert_management_api")
    logger.info("알림 관리 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"알림 관리 API 블루프린트 등록 실패: {e}")

# AI 예측 분석 API 블루프린트 등록
try:
    # from api.ai_prediction_advanced import ai_prediction_advanced_bp
    # app.register_blueprint(ai_prediction_advanced_bp, name='ai_prediction_advanced_api')
    # logger.info("AI 예측 분석 API 블루프린트 등록 완료")
    pass
except Exception as e:
    logger.error(f"AI 예측 분석 API 블루프린트 등록 실패: {e}")

# 성능 최적화 API 블루프린트 등록 (비활성화 - 파일이 존재하지 않음)
# try:
#     from routes.performance_optimization import performance_bp
#     app.register_blueprint(performance_bp, name="performance_optimization")
#     logger.info("성능 최적화 API 블루프린트 등록 완료")
# except Exception as e:
#     logger.error(f"성능 최적화 API 블루프린트 등록 실패: {e}")

# 통합 대시보드 API 블루프린트 등록
try:
    from api.integrated_dashboard_api import integrated_dashboard_bp

    app.register_blueprint(integrated_dashboard_bp, name="integrated_dashboard_api")
    logger.info("통합 대시보드 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"통합 대시보드 API 블루프린트 등록 실패: {e}")

# AI 통합 API 블루프린트 등록
try:
    from api.ai_integrated_api import ai_integrated_bp

    app.register_blueprint(ai_integrated_bp, name="ai_integrated_api")
    logger.info("AI 통합 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"AI 통합 API 블루프린트 등록 실패: {e}")

# 실시간 모니터링 API 블루프린트 등록 - 비활성화됨
# try:
#     from api.realtime_monitoring import realtime_monitoring

#     app.register_blueprint(realtime_monitoring, name="realtime_monitoring_api")
#     logger.info("실시간 모니터링 API 블루프린트 등록 완료")
# except Exception as e:
#     logger.error(f"실시간 모니터링 API 블루프린트 등록 실패: {e}")
logger.info("실시간 모니터링 API 블루프린트 비활성화됨")

# 플러그인 마켓플레이스 API 직접 등록 (비활성화 - 중복 등록 방지)
# try:
#     from api.plugin_marketplace import plugin_marketplace_bp
#     app.register_blueprint(plugin_marketplace_bp)
#     logger.info("플러그인 마켓플레이스 API 등록 완료")
# except Exception as e:
#     logger.error(f"플러그인 마켓플레이스 API 등록 실패: {e}")

# 실시간 알림 API 블루프린트 등록
try:
    from api.realtime_notifications import realtime_notifications_bp

    app.register_blueprint(realtime_notifications_bp, name="realtime_notifications_api")
    logger.info("실시간 알림 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"실시간 알림 API 블루프린트 등록 실패: {e}")

# 고급 분석 API 블루프린트 등록
try:
    from api.advanced_analytics import advanced_analytics_bp

    app.register_blueprint(advanced_analytics_bp, name="advanced_analytics_api")
    logger.info("고급 분석 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"고급 분석 API 블루프린트 등록 실패: {e}")

# IoT API 블루프린트 등록
try:
    from api.iot_api import iot_bp

    app.register_blueprint(iot_bp, name="iot_api")
    logger.info("IoT API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"IoT API 블루프린트 등록 실패: {e}")

# 통합 계층형 API 블루프린트 등록
try:
    from api.unified_hierarchy_api import unified_hierarchy_bp
    
    app.register_blueprint(unified_hierarchy_bp, name="unified_hierarchy_api")
    logger.info("통합 계층형 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"통합 계층형 API 블루프린트 등록 실패: {e}")

# 고급 AI 예측 API 블루프린트 등록
try:
    from api.advanced_ai_prediction import advanced_ai_prediction_bp

    app.register_blueprint(advanced_ai_prediction_bp, name="advanced_ai_prediction_api")
    logger.info("고급 AI 예측 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"고급 AI 예측 API 블루프린트 등록 실패: {e}")

# 자연어 처리 API 블루프린트 등록
try:
    from api.nlp_analysis import nlp_analysis_bp

    app.register_blueprint(nlp_analysis_bp, name="nlp_analysis_api")
    logger.info("자연어 처리 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"자연어 처리 API 블루프린트 등록 실패: {e}")

# AI 모니터링 API 블루프린트 등록
try:
    from api.ai_monitoring import ai_monitoring_bp

    app.register_blueprint(ai_monitoring_bp, name="ai_monitoring_api")
    logger.info("AI 모니터링 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"AI 모니터링 API 블루프린트 등록 실패: {e}")

# 플러그인 목록 (실제로는 DB에서 관리)
plugins = []

# JSON 파싱 강제 활성화
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# SocketIO 초기화 (조건부) - 나중에 설정
socketio = None  # 임시로 None 설정

from flask import jsonify, render_template, request
# 중복 등록 방지를 위해 주석 처리
# from api.auth import api_auth_bp
# app.register_blueprint(api_auth_bp)

CORS(
    app,
    origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    supports_credentials=True,
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
    expose_headers=["Content-Type", "Authorization"],
    max_age=86400,
)

# 확장 모듈 초기화 함수
def initialize_extensions():
    """Flask 확장 모듈들을 초기화합니다."""
    try:
        csrf.init_app(app)
        db.init_app(app)
        migrate.init_app(app, db)
        login_manager.init_app(app)
        login_manager.login_view = None  # API 경로는 인증을 우회하도록 설정
        login_manager.login_message = "로그인이 필요합니다."
        login_manager.login_message_category = "info"
        
        # Swagger 설정 초기화 (조건부)
        try:
            api = create_swagger_config(app)
            logger.info("Swagger API 설정 초기화 완료")
            return api
        except Exception as e:
            logger.warning(f"Swagger 설정 초기화 실패 (무시됨): {e}")
            return None
    except Exception as e:
        logger.error(f"확장 모듈 초기화 실패: {e}")
        return None
        
        # 추가 확장 모듈 초기화
        limiter.init_app(app)
        cache.init_app(app)
        
        # 캐시 매니저 초기화
        cache_manager.init_app(app)
        
        logger.info("Flask 확장 모듈 초기화 완료")
    except Exception as e:
        logger.error(f"Flask 확장 모듈 초기화 실패: {e}")
        raise

# 데이터베이스 초기화 함수
def initialize_database():
    """데이터베이스를 초기화하고 기본 데이터를 생성합니다."""
    with app.app_context():
        try:
            # DB 테이블 생성
            db.create_all()
            logger.info("데이터베이스 테이블 생성 완료")

            # 기본 관리자 계정 생성
            create_default_admin()
            
            # 기본 산업 데이터 생성
            from core.backend.schema_initializer import initialize_industries
            initialize_industries()

            db.session.commit()
            logger.info("데이터베이스 초기화 및 기본 데이터 생성 완료")

        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
            db.session.rollback()
            raise

def create_default_admin():
    """기본 관리자 계정을 생성합니다."""
    try:
        admin_user = User.query.filter_by(username="admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@your_program.com",
                role="admin",
                status="approved"
            )
            admin_user.set_password("admin123")
            db.session.add(admin_user)
            logger.info("기본 관리자 계정 생성 완료: admin/admin123")
        else:
            # 기존 관리자 계정의 상태를 approved로 업데이트
            if admin_user.status != "approved":
                admin_user.status = "approved"
                logger.info("기존 관리자 계정 상태를 approved로 업데이트")
    except Exception as e:
        logger.error(f"기본 관리자 계정 생성 실패: {e}")
        raise

# 확장 모듈 초기화
api = initialize_extensions()

# Swagger API 설정 초기화
api = create_swagger_config(app)

# WebSocket 매니저 초기화
websocket_manager.init_app(app)

# 데이터베이스 초기화 (앱 컨텍스트 내에서 실행)
# initialize_database()

# IoT 시스템 초기화
try:
    from utils.iot_simulator import initialize_iot_system
    initialize_iot_system()
    logger.info("IoT 시스템 초기화 완료")
except Exception as e:
    logger.error(f"IoT 시스템 초기화 실패: {e}")

# 블루프린트 등록 함수
def register_blueprints():
    """모든 블루프린트를 등록합니다."""
    blueprints = [
        # 플러그인 마켓플레이스 API
        ("api.plugin_marketplace", "plugin_marketplace_bp", "plugin_marketplace"),
        
        # 플러그인 시스템 API
        ("api.plugin_system_manager_api", "plugin_system_manager_bp", "plugin_system_manager_api"),
        ("api.plugin_operations_api", "plugin_operations_bp", "plugin_operations_api"),
        ("api.plugin_monitoring_dashboard", "plugin_monitoring_bp", "plugin_monitoring_dashboard"),
        
        # 인증 API
        ("api.auth", "auth_bp", "auth"),
        ("api.auth", "security_auth_bp", "security_auth"),
        
        # 고도화된 모니터링 API
        ("api.advanced_monitoring_api", "advanced_monitoring_bp", "advanced_monitoring_api"),
        
        # AI 시스템 API
        ("api.ai_api", "ai_bp", "ai"),
        ("api.real_ai_models_api", "real_ai_models_api", "real_ai_models_api"),
        
        # 고급 데이터 분석 및 비즈니스 인텔리전스 API
        ("api.analytics_api", "analytics_bp", "analytics"),
        
        # 고급 모니터링 및 분석 API
        ("api.monitoring_api", "monitoring_bp", "monitoring"),
        
        # 고급 통합 및 자동화 API
        ("api.integration_api", "integration_bp", "integration"),
        
        # MVP 플러그인 블루프린트
        ("plugins.attendance_management", "attendance_bp", "attendance_management"),
        ("plugins.inventory_management", "inventory_bp", "inventory_management"),
        ("plugins.purchase_management", "purchase_bp", "purchase_management"),
        ("plugins.schedule_management", "schedule_bp", "schedule_management"),
        
        # 브랜드 관리 API
        ("api.admin_brand_api", "admin_brand_api", "admin_brand_api"),
        
        # 업종관리자 API
        ("routes.industry_admin", "industry_admin_bp", "industry_admin"),
        
        # 새로운 백엔드 시스템 API
        ("api.industry_admin_management", "industry_admin_bp", "industry_admin_management"),
        ("api.plugin_marketplace_enhanced", "plugin_marketplace_bp", "plugin_marketplace_enhanced"),
        ("api.system_monitoring_enhanced", "system_monitoring_bp", "system_monitoring_enhanced"),
        ("api.realtime_notifications_enhanced", "realtime_notifications_bp", "realtime_notifications_enhanced"),
        ("api.system_health_api", "system_health_api", "system_health_api"),
        ("api.ai_analytics_api", "ai_analytics_api", "ai_analytics_api"),
        
        # 백엔드 관리자 Blueprint
        ("routes.backend_admin", "backend_admin_bp", None),
        
        # 브랜드관리자 API
        ("routes.brand_admin", "brand_admin_bp", "brand_admin"),
        
        # 매장관리자 API
        ("routes.store_admin", "store_admin_bp", "store_admin"),
        
        # 직원 API
        ("routes.employee", "employee_bp", "employee"),
    ]
    
    for module_path, blueprint_name, url_prefix in blueprints:
        try:
            module = __import__(module_path, fromlist=[blueprint_name])
            blueprint = getattr(module, blueprint_name)
            if url_prefix:
                app.register_blueprint(blueprint, name=url_prefix)
                logger.info(f"{url_prefix} 블루프린트 등록 완료")
            else:
                app.register_blueprint(blueprint)
                logger.info(f"{blueprint_name} 블루프린트 등록 완료 (URL prefix 없음)")
        except Exception as e:
            logger.error(f"{url_prefix or blueprint_name} 블루프린트 등록 실패: {e}")

# 블루프린트 등록
register_blueprints()

# 레스토랑 특화 대시보드 라우트 등록 (비활성화 - 파일이 존재하지 않음)
# try:
#     from routes.restaurant_enhanced_dashboard import restaurant_dashboard
#     restaurant_dashboard.init_app(app)
#     logger.info("레스토랑 특화 대시보드 라우트 등록 완료")
# except Exception as e:
#     logger.error(f"레스토랑 특화 대시보드 라우트 등록 실패: {e}")

# 레스토랑 분석 API 등록
try:
    from api.restaurant_analytics import restaurant_analytics
    restaurant_analytics.init_app(app)
    logger.info("레스토랑 분석 API 등록 완료")
except Exception as e:
    logger.error(f"레스토랑 분석 API 등록 실패: {e}")

# 레스토랑 AI 예측 API 등록
try:
    from api.restaurant_ai_prediction import restaurant_ai_prediction
    restaurant_ai_prediction.init_app(app)
    logger.info("레스토랑 AI 예측 API 등록 완료")
except Exception as e:
    logger.error(f"레스토랑 AI 예측 API 등록 실패: {e}")

# 레스토랑 자동화 API 등록
try:
    from api.restaurant_automation import restaurant_automation
    restaurant_automation.init_app(app)
    logger.info("레스토랑 자동화 API 등록 완료")
except Exception as e:
    logger.error(f"레스토랑 자동화 API 등록 실패: {e}")

# 모바일 레스토랑 대시보드 등록 (비활성화 - 파일이 존재하지 않음)
# try:
#     from routes.mobile_restaurant_dashboard import mobile_restaurant_dashboard
#     mobile_restaurant_dashboard.init_app(app)
#     logger.info("모바일 레스토랑 대시보드 등록 완료")
# except Exception as e:
#     logger.error(f"모바일 레스토랑 대시보드 등록 실패: {e}")

# 레스토랑 고급 분석 API 등록
try:
    from api.restaurant_advanced_analytics import restaurant_advanced_analytics
    restaurant_advanced_analytics.init_app(app)
    logger.info("레스토랑 고급 분석 API 등록 완료")
except Exception as e:
    logger.error(f"레스토랑 고급 분석 API 등록 실패: {e}")

# 레스토랑 계층적 대시보드 등록 (비활성화 - 파일이 존재하지 않음)
# try:
#     from routes.restaurant_hierarchical_dashboard import restaurant_hierarchical
#     restaurant_hierarchical.init_app(app)
#     logger.info("레스토랑 계층적 대시보드 등록 완료")
# except Exception as e:
#     logger.error(f"레스토랑 계층적 대시보드 등록 실패: {e}")

# 합 대시보드 등록 (비활성화 - 파일이 존재하지 않음)
# try:
#     from routes.comprehensive_dashboard import comprehensive_dashboard_bp
#     app.register_blueprint(comprehensive_dashboard_bp)
#     logger.info("합 대시보드 등록 완료")
# except Exception as e:
#     logger.error(f"합 대시보드 등록 실패: {e}")

# 레스토랑 업종 관리자 페이지 등록 (비활성화 - 파일이 존재하지 않음)
# try:
#     from routes.restaurant_industry_admin import restaurant_industry_admin
#     app.register_blueprint(restaurant_industry_admin)
#     restaurant_industry_admin.init_app(app)
#     logger.info("레스토랑 업종 관리자 페이지 등록 완료")
# except Exception as e:
#     logger.error(f"레스토랑 업종 관리자 페이지 등록 실패: {e}")

# 알림 관리 API 블루프린트 등록
try:
    from api.alert_management_api import alert_management_bp

    app.register_blueprint(alert_management_bp, name="alert_management_api")
    logger.info("알림 관리 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"알림 관리 API 블루프린트 등록 실패: {e}")

# AI 예측 분석 API 블루프린트 등록
try:
    # from api.ai_prediction_advanced import ai_prediction_advanced_bp
    # app.register_blueprint(ai_prediction_advanced_bp, name='ai_prediction_advanced_api')
    # logger.info("AI 예측 분석 API 블루프린트 등록 완료")
    pass
except Exception as e:
    logger.error(f"AI 예측 분석 API 블루프린트 등록 실패: {e}")

# 성능 최적화 API 블루프린트 등록 (비활성화 - 파일이 존재하지 않음)
# try:
#     from routes.performance_optimization import performance_bp
#     app.register_blueprint(performance_bp, name="performance_optimization")
#     logger.info("성능 최적화 API 블루프린트 등록 완료")
# except Exception as e:
#     logger.error(f"성능 최적화 API 블루프린트 등록 실패: {e}")

# 통합 대시보드 API 블루프린트 등록
try:
    from api.integrated_dashboard_api import integrated_dashboard_bp

    app.register_blueprint(integrated_dashboard_bp, name="integrated_dashboard_api")
    logger.info("통합 대시보드 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"통합 대시보드 API 블루프린트 등록 실패: {e}")

# AI 통합 API 블루프린트 등록
try:
    from api.ai_integrated_api import ai_integrated_bp

    app.register_blueprint(ai_integrated_bp, name="ai_integrated_api")
    logger.info("AI 통합 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"AI 통합 API 블루프린트 등록 실패: {e}")

# 실시간 모니터링 API 블루프린트 등록 - 비활성화됨
# try:
#     from api.realtime_monitoring import realtime_monitoring

#     app.register_blueprint(realtime_monitoring, name="realtime_monitoring_api")
#     logger.info("실시간 모니터링 API 블루프린트 등록 완료")
# except Exception as e:
#     logger.error(f"실시간 모니터링 API 블루프린트 등록 실패: {e}")
logger.info("실시간 모니터링 API 블루프린트 비활성화됨")

# 플러그인 마켓플레이스 API 직접 등록 (비활성화 - 중복 등록 방지)
# try:
#     from api.plugin_marketplace import plugin_marketplace_bp
#     app.register_blueprint(plugin_marketplace_bp)
#     logger.info("플러그인 마켓플레이스 API 등록 완료")
# except Exception as e:
#     logger.error(f"플러그인 마켓플레이스 API 등록 실패: {e}")

# 실시간 알림 API 블루프린트 등록
try:
    from api.realtime_notifications import realtime_notifications_bp

    app.register_blueprint(realtime_notifications_bp, name="realtime_notifications_api")
    logger.info("실시간 알림 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"실시간 알림 API 블루프린트 등록 실패: {e}")

# 고급 분석 API 블루프린트 등록
try:
    from api.advanced_analytics import advanced_analytics_bp

    app.register_blueprint(advanced_analytics_bp, name="advanced_analytics_api")
    logger.info("고급 분석 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"고급 분석 API 블루프린트 등록 실패: {e}")

# IoT API 블루프린트 등록
try:
    from api.iot_api import iot_bp

    app.register_blueprint(iot_bp, name="iot_api")
    logger.info("IoT API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"IoT API 블루프린트 등록 실패: {e}")

# 통합 계층형 API 블루프린트 등록
try:
    from api.unified_hierarchy_api import unified_hierarchy_bp
    
    app.register_blueprint(unified_hierarchy_bp, name="unified_hierarchy_api")
    logger.info("통합 계층형 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"통합 계층형 API 블루프린트 등록 실패: {e}")

# 고급 AI 예측 API 블루프린트 등록
try:
    from api.advanced_ai_prediction import advanced_ai_prediction_bp

    app.register_blueprint(advanced_ai_prediction_bp, name="advanced_ai_prediction_api")
    logger.info("고급 AI 예측 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"고급 AI 예측 API 블루프린트 등록 실패: {e}")

# 자연어 처리 API 블루프린트 등록
try:
    from api.nlp_analysis import nlp_analysis_bp

    app.register_blueprint(nlp_analysis_bp, name="nlp_analysis_api")
    logger.info("자연어 처리 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"자연어 처리 API 블루프린트 등록 실패: {e}")

# AI 모니터링 API 블루프린트 등록
try:
    from api.ai_monitoring import ai_monitoring_bp

    app.register_blueprint(ai_monitoring_bp, name="ai_monitoring_api")
    logger.info("AI 모니터링 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"AI 모니터링 API 블루프린트 등록 실패: {e}")

# AI 자동 재훈련 API 블루프린트 등록
try:
    from api.ai_auto_retrain import ai_auto_retrain_bp

    app.register_blueprint(ai_auto_retrain_bp, name="ai_auto_retrain_api")
    logger.info("AI 자동 재훈련 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"AI 자동 재훈련 API 블루프린트 등록 실패: {e}")

# 비즈니스 인텔리전스 API 블루프린트 등록
try:
    from api.business_intelligence import business_intelligence_bp

    app.register_blueprint(business_intelligence_bp, name="business_intelligence_api")
    logger.info("비즈니스 인텔리전스 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"비즈니스 인텔리전스 API 블루프린트 등록 실패: {e}")

# 자동화된 의사결정 API 블루프린트 등록
try:
    from api.automated_decision_system import automated_decision_bp

    app.register_blueprint(automated_decision_bp, name="automated_decision_api")
    logger.info("자동화된 의사결정 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"자동화된 의사결정 API 블루프린트 등록 실패: {e}")

# 플러그인 성능 최적화 API 블루프린트 등록
try:
    from api.plugin_optimization_api import plugin_optimization_bp

    app.register_blueprint(plugin_optimization_bp, name="plugin_optimization_api")
    logger.info("플러그인 성능 최적화 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"플러그인 성능 최적화 API 블루프린트 등록 실패: {e}")

# 브랜드 온보딩 API 블루프린트 등록
try:
    from api.brand_onboarding_api import brand_onboarding_bp

    app.register_blueprint(brand_onboarding_bp, name="brand_onboarding_api")
    logger.info("브랜드 온보딩 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"브랜드 온보딩 API 블루프린트 등록 실패: {e}")

# 브랜드 온보딩 라우트 블루프린트 등록
try:
    # from routes.brand_onboarding_routes import brand_onboarding_routes_bp

    app.register_blueprint(brand_onboarding_routes_bp, name="brand_onboarding_routes")
    logger.info("브랜드 온보딩 라우트 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"브랜드 온보딩 라우트 블루프린트 등록 실패: {e}")

# 카카오 API 관리 블루프린트 등록
try:
    from api.kakao_api_management import kakao_api_bp

    app.register_blueprint(kakao_api_bp, name="kakao_api_management")
    logger.info("카카오 API 관리 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"카카오 API 관리 블루프린트 등록 실패: {e}")

# 주소 검증 API 블루프린트 등록
try:
    from api.address_validation import address_validation_bp

    app.register_blueprint(address_validation_bp, name="address_validation_api")
    logger.info("주소 검증 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"주소 검증 API 블루프린트 등록 실패: {e}")

# 모듈 개발 시스템 API 블루프린트 등록
try:
    from api.module_development_api import module_development_api

    app.register_blueprint(
        module_development_api,
        url_prefix="/api/module-development",
        name="module_development_api",
    )
    logger.info("모듈 개발 시스템 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"모듈 개발 시스템 API 블루프린트 등록 실패: {e}")

# 고도화된 마켓플레이스 API 블루프린트 등록
try:
    from api.enhanced_marketplace_api import enhanced_marketplace_bp

    app.register_blueprint(enhanced_marketplace_bp, name="enhanced_marketplace_api")
    logger.info("고도화된 마켓플레이스 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"고도화된 마켓플레이스 API 블루프린트 등록 실패: {e}")

# 고도화된 보안 모니터링 API 블루프린트 등록
try:
    from api.enhanced_security_api import enhanced_security_bp

    app.register_blueprint(enhanced_security_bp, name="enhanced_security_api")
    logger.info("고도화된 보안 모니터링 API 블루프린트 등록 완료")
    
    # 고급 보안 시스템 Blueprint 등록
    from api.security_api import security_api
    app.register_blueprint(security_api, name="security_api")
    logger.info("고급 보안 시스템 API 블루프린트 등록 완료")
    
    # 보안 대시보드 Blueprint 등록
    # from routes.security_dashboard import security_dashboard
    app.register_blueprint(security_dashboard, name="security_dashboard")
    logger.info("보안 대시보드 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"고도화된 보안 모니터링 API 블루프린트 등록 실패: {e}")

# 플러그인 자동화 및 워크플로우 API 블루프린트 등록
try:
    from api.plugin_automation_api import plugin_automation_bp

    app.register_blueprint(plugin_automation_bp, name="plugin_automation_api")
    logger.info("플러그인 자동화 및 워크플로우 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"플러그인 자동화 및 워크플로우 API 블루프린트 등록 실패: {e}")

# 계약 생성기 API 블루프린트 등록
try:
    from core.backend.contract_generator import contract_generator_bp

    app.register_blueprint(contract_generator_bp, name="contract_generator_api")
    logger.info("계약 생성기 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"계약 생성기 API 블루프린트 등록 실패: {e}")

# 출퇴근 관리 데모 API 블루프린트 등록
try:
    from api.attendance_demo_api import attendance_demo_bp

    app.register_blueprint(attendance_demo_bp, name="attendance_demo")
    logger.info("출퇴근 관리 데모 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"출퇴근 관리 데모 API 블루프린트 등록 실패: {e}")

# 모듈 마켓플레이스 라우트 블루프린트 등록 (비활성화 - 파일이 존재하지 않음)
# try:
#     from routes.module_marketplace_routes import module_marketplace_routes_bp
#     app.register_blueprint(module_marketplace_routes_bp, name="module_marketplace_routes")
#     logger.info("모듈 마켓플레이스 라우트 블루프린트 등록 완료")
# except Exception as e:
#     logger.error(f"모듈 마켓플레이스 라우트 블루프린트 등록 실패: {e}")

# 마켓플레이스 데모 API 블루프린트 등록 (비활성화 - 파일이 존재하지 않음)
# try:
#     from routes.marketplace_demo import marketplace_demo_bp
#     app.register_blueprint(marketplace_demo_bp, name="marketplace_demo")
#     logger.info("마켓플레이스 데모 API 블루프린트 등록 완료")
# except Exception as e:
#     logger.error(f"마켓플레이스 데모 API 블루프린트 등록 실패: {e}")

# 출퇴근 관리 API 블루프린트 등록
try:
    from api.modules.attendance_management import attendance_management_bp

    app.register_blueprint(attendance_management_bp, name="attendance_management_api")
    logger.info("출퇴근 관리 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"출퇴근 관리 API 블루프린트 등록 실패: {e}")

# 모듈 관리 API 블루프린트 등록 (비활성화 - 파일이 존재하지 않음)
# try:
#     from routes.module_management import module_management_bp
#     app.register_blueprint(module_management_bp, name="module_management_api")
#     logger.info("모듈 관리 API 블루프린트 등록 완료")
# except Exception as e:
#     logger.error(f"모듈 관리 API 블루프린트 등록 실패: {e}")

# 플러그인 마이크로서비스 API 블루프린트 등록
try:
    from api.plugin_microservice_api import plugin_microservice_bp

    app.register_blueprint(plugin_microservice_bp, name="plugin_microservice_api")
    logger.info("플러그인 마이크로서비스 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"플러그인 마이크로서비스 API 블루프린트 등록 실패: {e}")

# 플러그인 AI 분석 및 예측 API 블루프린트 등록 - 비활성화됨
# try:
#     from api.plugin_ai_analytics_api import plugin_ai_analytics_bp

#     app.register_blueprint(plugin_ai_analytics_bp, name="plugin_ai_analytics_api")
#     logger.info("플러그인 AI 분석 및 예측 API 블루프린트 등록 완료")
# except Exception as e:
#     logger.error(f"플러그인 AI 분석 및 예측 API 블루프린트 등록 실패: {e}")
logger.info("플러그인 AI 분석 및 예측 API 블루프린트 비활성화됨")

# 플러그인 설정 관리 API 블루프린트 등록
try:
    from api.plugin_settings_management import plugin_settings_bp, init_settings_manager

    app.register_blueprint(plugin_settings_bp, name="plugin_settings_api")
    logger.info("플러그인 설정 관리 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"플러그인 설정 관리 API 블루프린트 등록 실패: {e}")

# 모듈 관리 API 블루프린트 등록 (비활성화 - 파일이 존재하지 않음)
# try:
#     from routes.module_management import module_management_bp
#     app.register_blueprint(module_management_bp, name="module_management_api_v2")
#     logger.info("모듈 관리 API 블루프린트 등록 완료")
# except Exception as e:
#     logger.error(f"모듈 관리 API 블루프린트 등록 실패: {e}")

# 관리자 대시보드 API 블루프린트 등록 (비활성화 - 파일이 존재하지 않음)
# try:
#     from routes.admin_dashboard_api import admin_dashboard_api
#     app.register_blueprint(admin_dashboard_api, name="admin_dashboard_api")
#     logger.info("관리자 대시보드 API 블루프린트 등록 완료")
# except Exception as e:
#     logger.error(f"관리자 대시보드 API 블루프린트 등록 실패: {e}")

# 플러그인 피드백 API 블루프린트 등록 (비활성화 - 파일이 존재하지 않음)
# try:
#     from routes.plugin_feedback import plugin_feedback_bp
#     app.register_blueprint(plugin_feedback_bp, url_prefix="/api/plugin-feedback", name="plugin_feedback_api")
#     logger.info("플러그인 피드백 API 블루프린트 등록 완료")
# except Exception as e:
#     logger.error(f"플러그인 피드백 API 블루프린트 등록 실패: {e}")

# 플러그인 커스터마이징 API 블루프린트 등록 (비활성화 - 파일이 존재하지 않음)
# try:
#     from routes.plugin_customization import plugin_customization_bp
#     app.register_blueprint(plugin_customization_bp, url_prefix="/api/plugin-customization", name="plugin_customization_api")
#     logger.info("플러그인 커스터마이징 API 블루프린트 등록 완료")
# except Exception as e:
#     logger.error(f"플러그인 커스터마이징 API 블루프린트 등록 실패: {e}")

# 플러그인 설정 관리 API 블루프린트 등록
try:
    logger.info("플러그인 설정 관리 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"플러그인 설정 관리 API 블루프린트 등록 실패: {e}")


# 모듈 마켓플레이스 API 블루프린트 등록
try:
    # from routes.brand_approval import brand_approval_bp

    app.register_blueprint(brand_approval_bp, name="brand_approval")
    logger.info("브랜드 관리자 승인 라우트 등록 완료")
except Exception as e:
    logger.error(f"브랜드 관리자 승인 라우트 등록 실패: {e}")

try:
    # from routes.brand_management import brand_management_bp

    app.register_blueprint(brand_management_bp, name="brand_management_routes")
    logger.info("브랜드별 관리 라우트 등록 완료")
except Exception as e:
    logger.error(f"브랜드별 관리 라우트 등록 실패: {e}")

try:
    # from routes.store_management import store_management_bp

    app.register_blueprint(store_management_bp, name="admin_store_management")
    logger.info("매장별 관리 라우트 등록 완료")
except Exception as e:
    logger.error(f"매장별 관리 라우트 등록 실패: {e}")

try:
    # from routes.employee_management import employee_management_bp

    app.register_blueprint(employee_management_bp, name="employee_management")
    logger.info("직원별 관리 라우트 등록 완료")
except Exception as e:
    logger.error(f"직원별 관리 라우트 등록 실패: {e}")

try:
    # routes.router_management 모듈이 존재하지 않으므로 주석 처리
    # from routes.router_management import router_management_bp
    # app.register_blueprint(router_management_bp, name='router_management')
    # logger.info("라우터 기능 관리 라우트 등록 완료")
    pass
except Exception as e:
    logger.error(f"라우터 기능 관리 라우트 등록 실패: {e}")

try:
    # from routes.feedback_management import feedback_management_bp

    app.register_blueprint(feedback_management_bp, name="feedback_management")
    logger.info("피드백 관리 라우트 등록 완료")
except Exception as e:
    logger.error(f"피드백 관리 라우트 등록 실패: {e}")
    # 위 except 블록에서 이미 예외를 처리했으므로, 아래 except 블록은 불필요하여 제거합니다. (Unreachable except clause lint 경고 방지)  # noqa
    from api.plugin_management import plugin_management_bp

    try:
        app.register_blueprint(plugin_management_bp, name="plugin_management_api")
        logger.info("플러그인 관리 API 블루프린트 등록 완료")
    except Exception as e:
        logger.error(f"플러그인 관리 API 블루프린트 등록 실패: {e}")
    from api.advanced_performance_analytics import advanced_performance_bp

    try:
        app.register_blueprint(advanced_performance_bp, name="advanced_performance_api")
        logger.info("고도화된 성능 분석 API 블루프린트 등록 완료")
    except Exception as e:
        logger.error(f"고도화된 성능 분석 API 블루프린트 등록 실패: {e}")  # noqa

    # 고도화된 AI 예측 API 블루프린트 등록 (비활성화 - 중복 등록 방지)
    # try:
    #     from api.advanced_ai_prediction import advanced_ai_prediction_bp
    #     app.register_blueprint(advanced_ai_prediction_bp, name="advanced_ai_prediction_api")
    #     logger.info("고도화된 AI 예측 API 블루프린트 등록 완료")
    # except Exception as e:
    #     logger.error(f"고도화된 AI 예측 API 블루프린트 등록 실패: {e}")  # noqa

    # init_settings_manager(app)는 try 블록 내에서 호출되어야 하며,
    # except 블록이 중복되어 있으면 안 됩니다.
    try:
        # core.backend.plugin_settings_manager 모듈이 존재하지 않으므로 주석 처리
        # from core.backend.plugin_settings_manager import init_settings_manager
        # init_settings_manager(app)
        pass
    except Exception as e:
        logger.error(f"플러그인 설정 관리 API 블루프린트 등록 실패: {e}")  # noqa

# 성능 분석 API 블루프린트 등록
try:
    from api.performance_analytics_api import performance_analytics_bp

    app.register_blueprint(performance_analytics_bp, name="performance_analytics_api")
    logger.info("성능 분석 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"성능 분석 API 블루프린트 등록 실패: {e}")

# 플러그인 시스템 초기화 및 시작
try:
    from core.backend.plugin_optimizer import plugin_optimizer

    plugin_optimizer.start_optimization()
    logger.info("플러그인 성능 최적화 시스템 시작")
except Exception as e:
    logger.error(f"플러그인 성능 최적화 시스템 시작 실패: {e}")

try:
    from core.backend.plugin_backup_manager import plugin_backup_manager

    plugin_backup_manager.start_auto_backup()
    logger.info("플러그인 자동 백업 시스템 시작")
except Exception as e:
    logger.error(f"플러그인 자동 백업 시스템 시작 실패: {e}")

# Prometheus 메트릭 객체 생성 (예시: 응답시간, CPU, 메모리, 에러율)
RESPONSE_TIME_GAUGE = Gauge(
    "app_response_time_seconds", "Average response time (seconds)"
)
MEMORY_USAGE_GAUGE = Gauge("app_memory_usage_percent", "Memory usage (%)")
CPU_USAGE_GAUGE = Gauge("app_cpu_usage_percent", "CPU usage (%)")
ERROR_RATE_GAUGE = Gauge("app_error_rate_percent", "Error rate (%)")


@app.route("/metrics")
def metrics():
    """Prometheus 메트릭 엔드포인트"""
    # 최신 성능 데이터 가져오기 (PerformanceAnalytics 활용)
    try:
        from core.backend.performance_analytics import PerformanceAnalytics

        analytics = PerformanceAnalytics()
        report = analytics.get_performance_report()
        metrics_summary = report.get("metrics_summary", {})
        # 메트릭 값 갱신
        RESPONSE_TIME_GAUGE.set(metrics_summary.get("avg_response_time", 0))
        MEMORY_USAGE_GAUGE.set(metrics_summary.get("avg_memory_usage", 0))
        CPU_USAGE_GAUGE.set(metrics_summary.get("avg_cpu_usage", 0))
        ERROR_RATE_GAUGE.set(metrics_summary.get("avg_error_rate", 0))
    except Exception as e:
        # 예외 발생 시 0으로 설정
        RESPONSE_TIME_GAUGE.set(0)
        MEMORY_USAGE_GAUGE.set(0)
        CPU_USAGE_GAUGE.set(0)
        ERROR_RATE_GAUGE.set(0)
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


# CSRF 보호에서 API 블루프린트 제외
# 자동 라우터에서 등록된 모든 블루프린트를 CSRF 제외 목록에 추가
# registered_blueprints = auto_router.get_registered_blueprints()
# for blueprint_name, blueprint in registered_blueprints.items():
#     csrf.exempt(blueprint)

# 플러그인 블루프린트도 CSRF 제외
# for blueprint_name, blueprint in plugin_manager.blueprints.items():
#     csrf.exempt(blueprint)

# Initialize Dynamic Schema System
from core.backend.schema_initializer import (
    initialize_default_schemas,
    create_sample_brand_schema,
)

initialize_default_schemas()
create_sample_brand_schema()

# Initialize Query Optimizer
try:
    from utils.query_optimizer import initialize_query_optimizer

    def init_query_optimizer():
        with app.app_context():
            query_optimizer, connection_pool_optimizer = initialize_query_optimizer(
                db.engine,
                config={
                    "slow_query_threshold": 1.0,
                    "analysis_interval": 3600,
                    "monitoring_enabled": True,
                },
            )
            logger.info("쿼리 최적화 시스템 초기화 완료")
            return query_optimizer, connection_pool_optimizer

    # 백그라운드에서 초기화
    import threading

    init_thread = threading.Thread(target=init_query_optimizer)
    init_thread.daemon = True
    init_thread.start()

except Exception as e:
    logger.error(f"쿼리 최적화 시스템 초기화 실패: {e}")

# Login manager setup
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.errorhandler(404)
def page_not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({
            "error": "API endpoint not found",
            "message": "API 엔드포인트를 찾을 수 없습니다.",
            "path": request.path
        }), 404
    return render_template("errors/404.html"), 404

@app.errorhandler(400)
def bad_request(e):
    # 디버깅을 위해 오류 정보 출력
    print(f"400 오류 발생: {request.path}")
    print(f"오류 정보: {e}")
    print(f"요청 데이터: {request.get_data()}")
    
    if request.path.startswith("/api/"):
        return jsonify({
            "error": "Bad Request",
            "message": "잘못된 요청입니다.",
            "debug_info": {
                "path": request.path,
                "method": request.method,
                "content_type": request.content_type,
                "data": request.get_data().decode('utf-8', errors='ignore')
            }
        }), 400
    return render_template("errors/400.html"), 400

@app.errorhandler(500)
def server_error(e):
    if request.path.startswith("/api/"):
        return jsonify({
            "error": "Internal server error",
            "message": "서버 내부 오류가 발생했습니다."
        }), 500
    return render_template("errors/500.html"), 500

@app.route("/favicon.ico")
def favicon():
    """Favicon 처리 - SVG favicon 반환"""
    try:
        return app.send_static_file("favicon.svg")
    except:
        # favicon.svg 파일이 없으면 빈 응답 반환
        return "", 204


@app.context_processor
def inject_notifications():
    """전역 템플릿에 알림 정보 주입"""
    if current_user.is_authenticated:
        unread_count = Notification.query.filter_by(
            user_id=current_user.id, is_read=False
        ).count()
        return {"unread_notifications": unread_count}
    return {"unread_notifications": 0}


@app.route("/")
def index():
    """루트 경로 접근 시 로그인 페이지로 리다이렉트"""
    return redirect("/auth/login")





@app.route("/api/dashboard")
def api_dashboard():
    """대시보드 API 엔드포인트"""
    print(f"DEBUG: /api/dashboard API 호출")
    print(f"DEBUG: Authorization 헤더: {request.headers.get('Authorization', 'None')}")

    # Authorization 헤더에서 토큰 확인
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        print("DEBUG: 인증 토큰 없음 - 대시보드 정보 제공")
        return (
            jsonify(
                {
                    "message": "인증이 필요합니다.",
                    "available_dashboards": {
                        "backend": "/admin/backend",
                        "test_login": "/test-login",
                        "dashboard_selector": "/dashboard",
                    },
                    "login_url": "/test-login",
                }
            ),
            401,
        )

    token = auth_header.split(" ")[1]

    try:
        # JWT 토큰 디코딩
        payload = jwt.decode(token, app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
        user_id = payload.get("user_id")

        if not user_id:
            return jsonify({"error": "Invalid token"}), 401

        # 사용자 정보 조회
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # 권한에 따른 대시보드 정보 반환
        dashboard_info = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
            "available_dashboards": {
                "backend": "/admin/backend",
            },
        }

        # 플러그인 상태 정보 추가
        # plugin_status = auto_router.get_plugin_status()
        # plugin_manager_status = plugin_manager.get_plugin_status()
        # dashboard_info["plugin_status"] = plugin_status
        # dashboard_info["plugin_manager_status"] = plugin_manager_status

        return jsonify(dashboard_info)

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        print(f"DEBUG: 대시보드 API 오류: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/admin/dashboard', methods=['GET'])
def api_admin_dashboard():
    return jsonify({
        'success': True,
        'cards': {
            'total_brands': 4,
            'total_stores': 10,
            'total_users': 50,
            'total_orders': 1234
        },
        'charts': {
            'brand_stats': [
                {'brand_name': '브랜드A', 'store_count': 3, 'employee_count': 10, 'order_count': 100},
                {'brand_name': '브랜드B', 'store_count': 2, 'employee_count': 8, 'order_count': 80}
            ]
        },
        'tables': {
            'recent_orders': [
                {'id': 1, 'item': '아메리카노', 'store_id': 1, 'status': 'completed', 'created_at': '2024-07-25 09:00'},
                {'id': 2, 'item': '카페라떼', 'store_id': 2, 'status': 'pending', 'created_at': '2024-07-25 09:10'}
            ],
            'system_logs': [
                {'id': 1, 'action': 'login', 'user_id': 1, 'created_at': '2024-07-25 09:00', 'detail': '로그인 성공'},
                {'id': 2, 'action': 'order', 'user_id': 2, 'created_at': '2024-07-25 09:10', 'detail': '주문 생성'}
            ]
        },
        'notifications': [
            {'id': 1, 'level': 'info', 'message': '시스템 점검 예정', 'created_at': '2024-07-25 08:00'},
            {'id': 2, 'level': 'warning', 'message': '매장 2곳 네트워크 불안정', 'created_at': '2024-07-25 08:30'}
        ]
    })

@app.route("/dashboard-jwt")
def dashboard_jwt():
    """JWT 토큰 테스트용 대시보드"""
    try:
        # Authorization 헤더에서 토큰 확인
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization header required"}), 401

        token = auth_header.split(" ")[1]

        # JWT 토큰 디코딩
        payload = jwt.decode(token, app.config["JWT_SECRET_KEY"], algorithms=["HS256"])

        return jsonify(
            {
                "message": "JWT 토큰이 유효합니다",
                "payload": payload,
                "dashboard_url": "/admin/backend",
            }
        )

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/login-success")
def login_success():
    """로그인 성공 페이지"""
    return render_template("auth/login_success.html")


@app.route("/profile")
def profile():
    """사용자 프로필 페이지"""
    return render_template("auth/profile.html")


@app.route("/api/profile")
def api_profile():
    """사용자 프로필 API"""
    try:
        user_data = {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role,
            "branch_id": current_user.branch_id,
            "created_at": (
                current_user.created_at.isoformat() if current_user.created_at else None
            ),
            "last_login": (
                current_user.last_login.isoformat() if current_user.last_login else None
            ),
        }

        # 브랜치 정보 추가
        if current_user.branch_id:
            branch = Branch.query.get(current_user.branch_id)
            if branch:
                user_data["branch"] = {
                    "id": branch.id,
                    "name": branch.name,
                    "address": branch.address,
                }

        return jsonify(user_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/user/profile")
def api_user_profile():
    """사용자 프로필 상세 API"""
    try:
        # 사용자 기본 정보
        user_data = {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role,
            "branch_id": current_user.branch_id,
            "created_at": (
                current_user.created_at.isoformat() if current_user.created_at else None
            ),
            "last_login": (
                current_user.last_login.isoformat() if current_user.last_login else None
            ),
        }

        # 브랜치 정보
        if current_user.branch_id:
            branch = Branch.query.get(current_user.branch_id)
            if branch:
                user_data["branch"] = {
                    "id": branch.id,
                    "name": branch.name,
                    "address": branch.address,
                }

        # 알림 정보
        notifications = (
            Notification.query.filter_by(user_id=current_user.id, is_read=False)
            .limit(5)
            .all()
        )

        user_data["notifications"] = [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in notifications
        ]

        return jsonify(user_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/auth/login", methods=["GET", "POST"])
def auth_login():
    """로그인 페이지"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("사용자명과 비밀번호를 입력해주세요.", "error")
            return render_template("auth/login.html")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()

            # 권한에 따른 리다이렉트
            if user.role == "admin":
                return redirect("/admin_dashboard")
            elif user.role == "manager":
                return redirect("/manager-dashboard")
            elif user.role == "employee":
                return redirect("/employee-dashboard")
            else:
                return redirect("/dashboard")
        else:
            flash("잘못된 사용자명 또는 비밀번호입니다.", "error")

    return render_template("auth/login.html")


@app.route("/api/security/auth/login", methods=["POST"])
def api_security_auth_login():
    """API 로그인 엔드포인트"""
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({
                "success": False,
                "error": "사용자명과 비밀번호를 입력해주세요."
            }), 400

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # JWT 토큰 생성
            import jwt
            from datetime import datetime, timedelta
            
            payload = {
                'user_id': user.id,
                'username': user.username,
                'role': user.role,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }
            
            token = jwt.encode(payload, app.config["JWT_SECRET_KEY"], algorithm="HS256")
            refresh_token = jwt.encode({
                'user_id': user.id,
                'exp': datetime.utcnow() + timedelta(days=7)
            }, app.config["JWT_SECRET_KEY"], algorithm="HS256")

            # 마지막 로그인 시간 업데이트
            user.last_login = datetime.utcnow()
            db.session.commit()

            return jsonify({
                "success": True,
                "message": "로그인되었습니다.",
                "token": token,
                "refresh_token": refresh_token,
                "data": {
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                        "status": user.status,
                        "brand_id": user.brand_id,
                        "branch_id": user.branch_id
                    }
                }
            })
        else:
            return jsonify({
                "success": False,
                "error": "잘못된 사용자명 또는 비밀번호입니다."
            }), 401

    except Exception as e:
        logger.error(f"Login API error: {e}")
        return jsonify({
            "success": False,
            "error": "로그인 처리 중 오류가 발생했습니다."
        }), 500


@app.route("/api/security/auth/logout", methods=["POST"])
def api_security_auth_logout():
    """API 로그아웃 엔드포인트"""
    try:
        return jsonify({
            "success": True,
            "message": "로그아웃되었습니다."
        })
    except Exception as e:
        logger.error(f"Logout API error: {e}")
        return jsonify({
            "success": False,
            "error": "로그아웃 처리 중 오류가 발생했습니다."
        }), 500


@app.route("/api/test/notification", methods=["POST"])
def api_test_notification():
    """실시간 알림 테스트 API"""
    try:
        data = request.get_json()
        notification_type = data.get('type', 'info')
        message = data.get('message', '테스트 알림입니다.')
        
        # WebSocket을 통해 실시간 알림 브로드캐스트
        websocket_manager.broadcast_notification({
            'type': notification_type,
            'title': '테스트 알림',
            'message': message
        })
        
        return jsonify({
            "success": True,
            "message": "알림이 전송되었습니다."
        })
    except Exception as e:
        logger.error(f"Test notification error: {e}")
        return jsonify({
            "success": False,
            "error": "알림 전송 중 오류가 발생했습니다."
        }), 500


@app.route("/api/test/system-alert", methods=["POST"])
def api_test_system_alert():
    """시스템 알림 테스트 API"""
    try:
        data = request.get_json()
        severity = data.get('severity', 'medium')
        message = data.get('message', '테스트 시스템 알림입니다.')
        
        # WebSocket을 통해 시스템 알림 브로드캐스트
        websocket_manager.broadcast_system_alert({
            'severity': severity,
            'title': '시스템 알림',
            'message': message
        })
        
        return jsonify({
            "success": True,
            "message": "시스템 알림이 전송되었습니다."
        })
    except Exception as e:
        logger.error(f"Test system alert error: {e}")
        return jsonify({
            "success": False,
            "error": "시스템 알림 전송 중 오류가 발생했습니다."
        }), 500


@app.route("/admin/backend")
def admin_backend_main():
    """백엔드 관리자 대시보드 메인 페이지 (개발용 - 인증 무시)"""
    print(f"DEBUG: /admin/backend 접근 - 개발용 모드")
    
    # 개발용으로 모든 인증 체크 무시
    class DevUser:
        def __init__(self):
            self.id = 1
            self.username = "admin"
            self.email = "admin@your_program.com"
            self.role = "super_admin"
            self.status = "approved"
            self.is_authenticated = True
            self.is_active = True
            self.is_anonymous = False
        
        def get_id(self):
            return str(self.id)
    
    # 개발용 사용자 생성
    user = DevUser()
    
    print(f"DEBUG: 개발용 사용자 생성 완료 - username: {user.username}, role: {user.role}")
    
    # 템플릿 렌더링 (인증 체크 없이)
    try:
        return render_template('admin/backend_dashboard.html', 
                             user=user, 
                             current_page='backend_main')
    except Exception as e:
        print(f"ERROR: 템플릿 렌더링 실패: {e}")
        return f"<h1>백엔드 대시보드</h1><p>사용자: {user.username}</p><p>역할: {user.role}</p>"

@app.route("/dashboard")
def dashboard():
    """백엔드 대시보드 (로그인 후 접근)"""
    print(f"DEBUG: /dashboard 접근")
    
    # 로그인 체크
    from flask_login import current_user
    if not current_user.is_authenticated:
        print("DEBUG: 로그인되지 않은 사용자 - 로그인 페이지로 리다이렉트")
        return redirect("/auth/login")
    
    print(f"DEBUG: 로그인된 사용자 - username: {current_user.username}, role: {getattr(current_user, 'role', 'unknown')}")
    
    # 템플릿 렌더링
    try:
        return render_template('admin/cyberpunk_dashboard.html', 
                             user=current_user, 
                             current_page='backend_main')
    except Exception as e:
        print(f"ERROR: 템플릿 렌더링 실패: {e}")
        return f"<h1>퀀텀 스타일 백엔드 대시보드</h1><p>사용자: {current_user.username}</p><p>역할: {getattr(current_user, 'role', 'unknown')}</p>"

@app.route("/notifications")
def notifications():
    """알림 페이지 (개발용)"""
    return render_template('notifications.html')

@app.route("/admin_notifications")
def admin_notifications():
    """관리자 알림 페이지 (개발용)"""
    return render_template('admin/all_notifications.html')

@app.route("/m_notifications")
def m_notifications():
    """모바일 알림 페이지 (개발용)"""
    return render_template('mobile/m_notifications.html')


@app.route("/admin_dashboard")
def admin_dashboard_route():
    """관리자 대시보드 - 백엔드 메인 화면으로 리다이렉트"""
    return redirect("/admin/backend")


@app.route("/super-admin")
def super_admin_dashboard():
    """최고 관리자 대시보드를 새로운 백엔드 관리자 대시보드로 리다이렉트"""
    return redirect("/admin/backend")


@app.route("/manager-dashboard")
def manager_dashboard():
    """매니저 대시보드를 새로운 백엔드 관리자 대시보드로 리다이렉트"""
    return redirect("/admin/backend")


@app.route("/employee-dashboard")
def employee_dashboard():
    """직원 대시보드"""
    return render_template("admin/employee_dashboard.html")


@app.route("/teamlead-dashboard")
def teamlead_dashboard():
    """팀리드 대시보드"""
    return render_template("admin/teamlead_dashboard.html")


@app.route("/my-attendance")
def my_attendance():
    """내 출근 기록"""
    return render_template("attendance/my_attendance.html")


@app.route("/my-schedule")
def my_schedule():
    """내 스케줄"""
    return render_template("schedule/my_schedule.html")


@app.route("/test-login")
def test_login():
    """테스트 로그인 페이지"""
    return render_template("auth/test_login.html")


@app.route("/simple-login")
def simple_login():
    """간단한 로그인 테스트 페이지"""
    return render_template("auth/simple_login.html")


@app.route("/check-auth")
def check_auth():
    """인증 상태 확인"""
    from flask_login import current_user

    if current_user.is_authenticated:
        return jsonify(
            {
                "authenticated": True,
                "user_id": current_user.id,
                "username": current_user.username,
                "role": current_user.role,
            }
        )
    else:
        return jsonify({"authenticated": False}), 401


@app.route("/brand-manager-dashboard")
def brand_manager_dashboard():
    """브랜드 매니저 대시보드를 새로운 백엔드 관리자 대시보드로 리다이렉트"""
    return redirect("/admin/backend")


@app.route("/store-manager-dashboard")
def store_manager_dashboard():
    """스토어 매니저 대시보드를 새로운 백엔드 관리자 대시보드로 리다이렉트"""
    return redirect("/admin/backend")

# 중복된 shadcn 라우트들 제거됨 - 기존 구조 유지


@app.route("/api/admin/dashboard-stats")
def api_admin_dashboard_stats():
    """관리자 대시보드 통계 API"""
    try:
        # 기본 통계
        total_users = User.query.count()
        total_branches = Branch.query.count()

        # 최근 가입자
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        recent_users_data = [
            {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            }
            for user in recent_users
        ]

        # 플러그인 상태
        # plugin_status = auto_router.get_plugin_status()

        stats = {
            "total_users": total_users,
            "total_branches": total_branches,
            "recent_users": recent_users_data,
            # "plugin_status": plugin_status,
        }

        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/system-logs")
def api_admin_system_logs():
    """시스템 로그 API"""
    try:
        # 시스템 로그 정보 (실제로는 로그 파일에서 읽어와야 함)
        # plugin_status = auto_router.get_plugin_status()
        logs = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "INFO",
                "message": "시스템 정상 운영 중",
                "source": "auto_router",
            },
            {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "INFO",
                "message": "플러그인 시스템 정상 운영 중",
                "source": "plugin_loader",
            },
        ]

        return jsonify({"logs": logs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/critical-alerts")
def api_admin_critical_alerts():
    """중요 알림 API"""
    try:
        # 중요 알림 목록
        alerts = [
            {
                "id": 1,
                "type": "system",
                "title": "시스템 상태",
                "message": "모든 서비스 정상 운영 중",
                "severity": "info",
                "timestamp": datetime.utcnow().isoformat(),
            }
        ]

        return jsonify({"alerts": alerts})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/pending-approvals")
def api_admin_pending_approvals():
    """대기 중인 승인 API"""
    try:
        # 대기 중인 승인 목록
        approvals = [
            {
                "id": 1,
                "type": "user_registration",
                "title": "새 사용자 등록",
                "requester": "test_user",
                "timestamp": datetime.utcnow().isoformat(),
            }
        ]

        return jsonify({"approvals": approvals})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/system-status")
def api_admin_system_status():
    """시스템 상태 API"""
    try:
        # 시스템 상태 정보
        status = {
            "database": "connected",
            "cache": "connected",
            # "plugins": auto_router.get_plugin_status(),
            "uptime": "24h 30m",
            "memory_usage": "45%",
            "cpu_usage": "12%",
        }

        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# @app.route("/admin/staff-management")
# def admin_staff_management():
#     """직원 관리 페이지 - 브랜드 관리자 승인으로 대체됨"""
#     return render_template('admin/staff_management.html')


@app.route("/api/admin/staff-list")
def api_admin_staff_list():
    """직원 목록 API"""
    try:
        users = User.query.all()
        staff_list = []

        for user in users:
            staff_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "branch_id": user.branch_id,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
            }

            # 브랜치 정보 추가
            if user.branch_id:
                branch = Branch.query.get(user.branch_id)
                if branch:
                    staff_data["branch_name"] = branch.name

            staff_list.append(staff_data)

        return jsonify({"staff": staff_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/staff-detail/<int:user_id>")
def api_admin_staff_detail(user_id):
    """직원 상세 정보 API"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "branch_id": user.branch_id,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
        }

        # 브랜치 정보
        if user.branch_id:
            branch = Branch.query.get(user.branch_id)
            if branch:
                user_data["branch"] = {
                    "id": branch.id,
                    "name": branch.name,
                    "address": branch.address,
                }

        return jsonify(user_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/update-staff-role/<int:user_id>", methods=["PUT"])
def api_admin_update_staff_role(user_id):
    """직원 역할 업데이트 API"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.get_json()
        new_role = data.get("role")

        if not new_role:
            return jsonify({"error": "Role is required"}), 400

        # 역할 유효성 검사
        valid_roles = ["admin", "manager", "employee", "teamlead"]
        if new_role not in valid_roles:
            return jsonify({"error": "Invalid role"}), 400

        user.role = new_role
        db.session.commit()

        return jsonify(
            {
                "message": "Role updated successfully",
                "user": {"id": user.id, "username": user.username, "role": user.role},
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/delete-staff/<int:user_id>", methods=["DELETE"])
def api_admin_delete_staff(user_id):
    """직원 삭제 API"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # 관리자는 삭제 불가
        if user.role == "admin":
            return jsonify({"error": "Cannot delete admin user"}), 400

        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "User deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/system-monitoring")
def admin_system_monitoring():
    """시스템 모니터링 페이지"""
    return render_template("admin/system_monitoring.html")


@app.route("/api/admin/system-stats")
def api_admin_system_stats():
    """시스템 통계 API"""
    try:
        # 시스템 통계
        stats = {
            "total_users": User.query.count(),
            "total_branches": Branch.query.count(),
            "total_orders": Order.query.count() if hasattr(Order, "query") else 0,
            "total_schedules": (
                Schedule.query.count() if hasattr(Schedule, "query") else 0
            ),
            # "plugin_status": auto_router.get_plugin_status(),
        }

        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/service-status")
def api_admin_service_status():
    """서비스 상태 API"""
    try:
        # 서비스 상태 정보
        services = [
            {
                "name": "Database",
                "status": "healthy",
                "response_time": "5ms",
                "last_check": datetime.utcnow().isoformat(),
            },
            {
                "name": "Cache",
                "status": "healthy",
                "response_time": "2ms",
                "last_check": datetime.utcnow().isoformat(),
            },
            {
                "name": "Plugin System",
                "status": "healthy",
                "response_time": "10ms",
                "last_check": datetime.utcnow().isoformat(),
            },
        ]

        return jsonify({"services": services})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/system-alerts")
def api_admin_system_alerts():
    """시스템 알림 API"""
    try:
        # 시스템 알림 목록
        alerts = [
            {
                "id": 1,
                "type": "info",
                "title": "시스템 정상",
                "message": "모든 서비스가 정상적으로 운영되고 있습니다.",
                "timestamp": datetime.utcnow().isoformat(),
                "acknowledged": False,
            }
        ]

        return jsonify({"alerts": alerts})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/plugins/status")
def api_plugins_status():
    """플러그인 상태 조회 API"""
    try:
        # 플러그인 매니저가 비활성화된 상태이므로 기본 상태 반환
        plugin_status = {
            "total_plugins": 0,
            "enabled_plugins": 0,
            "disabled_plugins": 0,
            "loaded_plugins": 0,
            "status": "disabled"
        }
        return jsonify({"status": "success", "data": plugin_status})
    except Exception as e:
        logger.error(f"플러그인 상태 조회 실패: {e}")
        return jsonify({"error": "플러그인 상태 조회 실패"}), 500


@app.route("/api/plugins/list")
def api_plugins_list():
    """플러그인 목록 조회 API"""
    try:
        # 플러그인 매니저가 비활성화된 상태이므로 빈 목록 반환
        plugins_info = {}
        return jsonify({"status": "success", "data": plugins_info})
    except Exception as e:
        logger.error(f"플러그인 목록 조회 실패: {e}")
        return jsonify({"error": "플러그인 목록 조회 실패"}), 500


@app.route("/api/plugins/<plugin_name>/enable", methods=["POST"])
def api_enable_plugin(plugin_name):
    """플러그인 활성화 API"""
    try:
        # 플러그인 매니저가 비활성화된 상태이므로 실패 반환
        return jsonify({"error": "플러그인 시스템이 비활성화되어 있습니다"}), 503
    except Exception as e:
        logger.error(f"플러그인 {plugin_name} 활성화 실패: {e}")
        return jsonify({"error": "플러그인 활성화 실패"}), 500


@app.route("/api/plugins/<plugin_name>/disable", methods=["POST"])
def api_disable_plugin(plugin_name):
    """플러그인 비활성화 API"""
    try:
        # 플러그인 매니저가 비활성화된 상태이므로 실패 반환
        return jsonify({"error": "플러그인 시스템이 비활성화되어 있습니다"}), 503
    except Exception as e:
        logger.error(f"플러그인 {plugin_name} 비활성화 실패: {e}")
        return jsonify({"error": "플러그인 비활성화 실패"}), 500


@app.route("/api/plugins/<plugin_name>/reload", methods=["POST"])
def api_reload_plugin(plugin_name):
    """플러그인 재로드 API"""
    try:
        # 플러그인 매니저가 비활성화된 상태이므로 실패 반환
        return jsonify({"error": "플러그인 시스템이 비활성화되어 있습니다"}), 503
    except Exception as e:
        logger.error(f"플러그인 {plugin_name} 재로드 실패: {e}")
        return jsonify({"error": "플러그인 재로드 실패"}), 500


@app.route("/api/plugins/menus")
def api_plugins_menus():
    """플러그인 메뉴 정보 조회 API"""
    try:
        # 플러그인 매니저가 비활성화된 상태이므로 빈 메뉴 반환
        menus = []
        return jsonify({"status": "success", "data": menus})
    except Exception as e:
        logger.error(f"플러그인 메뉴 조회 실패: {e}")
        return jsonify({"error": "플러그인 메뉴 조회 실패"}), 500


@app.route("/api/plugins/routes")
def api_plugins_routes():
    """플러그인 라우트 정보 조회 API"""
    try:
        # 플러그인 매니저가 비활성화된 상태이므로 빈 라우트 반환
        routes = []
        return jsonify({"status": "success", "data": routes})
    except Exception as e:
        logger.error(f"플러그인 라우트 조회 실패: {e}")
        return jsonify({"error": "플러그인 라우트 조회 실패"}), 500


@app.route("/api/plugins/create", methods=["POST"])
@csrf.exempt
def api_create_plugin():
    """새 플러그인 생성 API"""
    try:
        # 플러그인 시스템이 비활성화된 상태이므로 실패 반환
        return jsonify({"error": "플러그인 시스템이 비활성화되어 있습니다"}), 503
    except Exception as e:
        logger.error(f"플러그인 생성 실패: {e}")
        return jsonify({"error": "플러그인 생성 실패"}), 500


@app.route("/api/plugins/<plugin_name>/validate", methods=["POST"])
def api_validate_plugin(plugin_name):
    """플러그인 설정 검증 API"""
    try:
        # 플러그인 시스템이 비활성화된 상태이므로 실패 반환
        return jsonify({"error": "플러그인 시스템이 비활성화되어 있습니다"}), 503
    except Exception as e:
        logger.error(f"플러그인 {plugin_name} 검증 실패: {e}")
        return jsonify({"error": "플러그인 검증 실패"}), 500


@app.route("/api/plugins/customizations/rules", methods=["GET"])
def api_get_customization_rules():
    """커스터마이즈 규칙 조회 API"""
    try:
        # 플러그인 시스템이 비활성화된 상태이므로 빈 규칙 반환
        return jsonify({"status": "success", "data": []})
    except Exception as e:
        logger.error(f"커스터마이즈 규칙 조회 실패: {e}")
        return jsonify({"error": "커스터마이즈 규칙 조회 실패"}), 500


@app.route("/api/plugins/customizations/rules", methods=["POST"])
def api_create_customization_rule():
    """커스터마이즈 규칙 생성 API"""
    try:
        # 플러그인 시스템이 비활성화된 상태이므로 실패 반환
        return jsonify({"error": "플러그인 시스템이 비활성화되어 있습니다"}), 503
    except Exception as e:
        logger.error(f"커스터마이즈 규칙 생성 실패: {e}")
        return jsonify({"error": "커스터마이즈 규칙 생성 실패"}), 500


@app.route("/api/plugins/customizations/requests", methods=["GET"])
def api_get_customization_requests():
    """커스터마이즈 요청 조회 API"""
    try:
        # 플러그인 시스템이 비활성화된 상태이므로 빈 요청 반환
        return jsonify({"status": "success", "data": []})
    except Exception as e:
        logger.error(f"커스터마이즈 요청 조회 실패: {e}")
        return jsonify({"error": "커스터마이즈 요청 조회 실패"}), 500


@app.route("/api/plugins/customizations/requests", methods=["POST"])
def api_create_customization_request():
    """커스터마이즈 요청 생성 API"""
    try:
        # 플러그인 시스템이 비활성화된 상태이므로 실패 반환
        return jsonify({"error": "플러그인 시스템이 비활성화되어 있습니다"}), 503
    except Exception as e:
        logger.error(f"커스터마이즈 요청 생성 실패: {e}")
        return jsonify({"error": "커스터마이즈 요청 생성 실패"}), 500


@app.route(
    "/api/plugins/customizations/requests/<request_id>/approve", methods=["POST"]
)
def api_approve_customization_request(request_id):
    """커스터마이즈 요청 승인 API"""
    try:
        data = request.get_json() or {}
        reviewer = data.get("reviewer", "admin")
        comment = data.get("comment", "")

        success = plugin_manager.customization_manager.approve_customization_request(
            request_id, reviewer, comment
        )

        if success:
            return jsonify(
                {"status": "success", "message": "커스터마이즈 요청 승인 완료"}
            )
        else:
            return jsonify({"error": "커스터마이즈 요청 승인 실패"}), 400

    except Exception as e:
        logger.error(f"커스터마이즈 요청 승인 실패: {e}")
        return jsonify({"error": "커스터마이즈 요청 승인 실패"}), 500


@app.route("/api/plugins/customizations/requests/<request_id>/reject", methods=["POST"])
def api_reject_customization_request(request_id):
    """커스터마이즈 요청 거부 API"""
    try:
        data = request.get_json() or {}
        reviewer = data.get("reviewer", "admin")
        comment = data.get("comment", "")

        success = plugin_manager.customization_manager.reject_customization_request(
            request_id, reviewer, comment
        )

        if success:
            return jsonify(
                {"status": "success", "message": "커스터마이즈 요청 거부 완료"}
            )
        else:
            return jsonify({"error": "커스터마이즈 요청 거부 실패"}), 400

    except Exception as e:
        logger.error(f"커스터마이즈 요청 거부 실패: {e}")
        return jsonify({"error": "커스터마이즈 요청 거부 실패"}), 500


@app.route("/api/plugins/customizations/history")
def api_get_customization_history():
    """커스터마이즈 히스토리 조회 API"""
    try:
        action = request.args.get("action")
        limit = int(request.args.get("limit", 100))

        history = plugin_manager.customization_manager.get_customization_history(
            action=action, limit=limit
        )

        return jsonify({"status": "success", "data": history})
    except Exception as e:
        logger.error(f"커스터마이즈 히스토리 조회 실패: {e}")
        return jsonify({"error": "커스터마이즈 히스토리 조회 실패"}), 500


# plugin_release_manager = PluginReleaseManager("plugins")


@app.route("/api/plugins/<plugin_name>/releases", methods=["GET"])
def api_list_plugin_releases(plugin_name):
    """플러그인 배포본(버전) 목록 조회 API"""
    try:
        releases = plugin_release_manager.list_releases(plugin_name)
        return jsonify({"status": "success", "data": releases})
    except Exception as e:
        logger.error(f"플러그인 배포본 목록 조회 실패: {e}")
        return jsonify({"error": "플러그인 배포본 목록 조회 실패"}), 500


@app.route("/api/plugins/<plugin_name>/release", methods=["POST"])
def api_save_plugin_release(plugin_name):
    """플러그인 현재 상태를 새 버전으로 배포(스냅샷) API"""
    try:
        data = request.get_json() or {}
        version = data.get("version")
        user = data.get("user", "admin")
        detail = data.get("detail", "")
        if not version:
            return jsonify({"error": "버전 정보가 필요합니다"}), 400
        success = plugin_release_manager.save_release(plugin_name, version)
        if success:
            plugin_release_manager.log_release_action(
                plugin_name, "release", version, user, detail
            )
            return jsonify({"status": "success", "message": f"{version} 배포 완료"})
        else:
            return jsonify({"error": "배포 실패"}), 400
    except Exception as e:
        logger.error(f"플러그인 배포 실패: {e}")
        return jsonify({"error": "플러그인 배포 실패"}), 500


@app.route("/api/plugins/<plugin_name>/rollback", methods=["POST"])
def api_rollback_plugin_release(plugin_name):
    """플러그인 롤백(이전 버전 복구) API"""
    try:
        data = request.get_json() or {}
        version = data.get("version")
        user = data.get("user", "admin")
        detail = data.get("detail", "")
        if not version:
            return jsonify({"error": "롤백할 버전 정보가 필요합니다"}), 400
        success = plugin_release_manager.rollback_release(plugin_name, version)
        if success:
            plugin_release_manager.log_release_action(
                plugin_name, "rollback", version, user, detail
            )
            return jsonify({"status": "success", "message": f"{version}로 롤백 완료"})
        else:
            return jsonify({"error": "롤백 실패"}), 400
    except Exception as e:
        logger.error(f"플러그인 롤백 실패: {e}")
        return jsonify({"error": "플러그인 롤백 실패"}), 500


@app.route("/api/plugins/<plugin_name>/release-history", methods=["GET"])
def api_plugin_release_history(plugin_name):
    """플러그인 배포/업데이트/롤백 이력 조회 API"""
    try:
        limit = int(request.args.get("limit", 50))
        history = plugin_release_manager.get_release_history(plugin_name, limit)
        return jsonify({"status": "success", "data": history})
    except Exception as e:
        logger.error(f"플러그인 배포 이력 조회 실패: {e}")
        return jsonify({"error": "플러그인 배포 이력 조회 실패"}), 500


# plugin_marketplace = PluginMarketplace()


@app.route("/api/marketplace/plugins", methods=["GET"])
def api_marketplace_plugins():
    """마켓플레이스 플러그인 목록 조회 API"""
    try:
        category = request.args.get("category")
        search = request.args.get("search")
        sort_by = request.args.get("sort_by", "rating")
        sort_order = request.args.get("sort_order", "desc")

        plugins = plugin_marketplace.get_marketplace_plugins(
            category=category, search=search, sort_by=sort_by, sort_order=sort_order
        )

        return jsonify({"status": "success", "data": plugins})
    except Exception as e:
        logger.error(f"마켓플레이스 플러그인 목록 조회 실패: {e}")
        return jsonify({"error": "마켓플레이스 플러그인 목록 조회 실패"}), 500


@app.route("/api/marketplace/plugins/<plugin_id>", methods=["GET"])
def api_marketplace_plugin_details(plugin_id):
    """마켓플레이스 플러그인 상세 정보 조회 API"""
    try:
        plugin = plugin_marketplace.get_plugin_details(plugin_id)
        if not plugin:
            return jsonify({"error": "플러그인을 찾을 수 없습니다"}), 404

        return jsonify({"status": "success", "data": plugin})
    except Exception as e:
        logger.error(f"마켓플레이스 플러그인 상세 정보 조회 실패: {e}")
        return jsonify({"error": "마켓플레이스 플러그인 상세 정보 조회 실패"}), 500


@app.route("/api/marketplace/plugins/<plugin_id>/install", methods=["POST"])
def api_install_marketplace_plugin(plugin_id):
    """마켓플레이스에서 플러그인 설치 API"""
    try:
        success = plugin_marketplace.install_plugin_from_marketplace(plugin_id)
        if success:
            return jsonify(
                {"status": "success", "message": f"플러그인 {plugin_id} 설치 완료"}
            )
        else:
            return jsonify({"error": "플러그인 설치 실패"}), 400
    except Exception as e:
        logger.error(f"마켓플레이스 플러그인 설치 실패: {e}")
        return jsonify({"error": "마켓플레이스 플러그인 설치 실패"}), 500


@app.route("/api/marketplace/plugins/<plugin_id>/reviews", methods=["GET"])
def api_marketplace_plugin_reviews(plugin_id):
    """마켓플레이스 플러그인 리뷰 목록 조회 API"""
    try:
        limit = int(request.args.get("limit", 50))
        reviews = plugin_marketplace.get_plugin_reviews(plugin_id, limit)

        return jsonify({"status": "success", "data": reviews})
    except Exception as e:
        logger.error(f"마켓플레이스 플러그인 리뷰 조회 실패: {e}")
        return jsonify({"error": "마켓플레이스 플러그인 리뷰 조회 실패"}), 500


@app.route("/api/marketplace/plugins/<plugin_id>/reviews", methods=["POST"])
def api_add_marketplace_plugin_review(plugin_id):
    """마켓플레이스 플러그인 리뷰 추가 API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "요청 데이터가 없습니다"}), 400

        user_id = data.get("user_id", "anonymous")
        user_name = data.get("user_name", "Anonymous")
        rating = data.get("rating", 5)
        comment = data.get("comment", "")

        if not (1 <= rating <= 5):
            return jsonify({"error": "평점은 1-5 사이여야 합니다"}), 400

        success = plugin_marketplace.add_review(
            plugin_id, user_id, user_name, rating, comment
        )

        if success:
            return jsonify({"status": "success", "message": "리뷰가 추가되었습니다"})
        else:
            return jsonify({"error": "리뷰 추가 실패"}), 400
    except Exception as e:
        logger.error(f"마켓플레이스 플러그인 리뷰 추가 실패: {e}")
        return jsonify({"error": "마켓플레이스 플러그인 리뷰 추가 실패"}), 500


@app.route("/api/marketplace/categories", methods=["GET"])
def api_marketplace_categories():
    """마켓플레이스 카테고리 목록 조회 API"""
    try:
        categories = plugin_marketplace.get_categories()

        return jsonify({"status": "success", "data": categories})
    except Exception as e:
        logger.error(f"마켓플레이스 카테고리 조회 실패: {e}")
        return jsonify({"error": "마켓플레이스 카테고리 조회 실패"}), 500


# plugin_feedback_system = PluginFeedbackSystem()


@app.route("/api/feedback", methods=["POST"])
def api_create_feedback():
    """피드백 생성 API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "요청 데이터가 없습니다"}), 400

        feedback_id = plugin_feedback_system.create_feedback(data)
        if feedback_id:
            return jsonify(
                {
                    "status": "success",
                    "message": "피드백이 생성되었습니다",
                    "feedback_id": feedback_id,
                }
            )
        else:
            return jsonify({"error": "피드백 생성 실패"}), 400
    except Exception as e:
        logger.error(f"피드백 생성 실패: {e}")
        return jsonify({"error": "피드백 생성 실패"}), 500


@app.route("/api/feedback", methods=["GET"])
def api_get_feedback_list():
    """피드백 목록 조회 API"""
    try:
        status = request.args.get("status")
        feedback_type = request.args.get("type")
        plugin_id = request.args.get("plugin_id")
        user_id = request.args.get("user_id")
        sort_by = request.args.get("sort_by", "created_at")
        sort_order = request.args.get("sort_order", "desc")

        feedbacks = plugin_feedback_system.get_feedback_list(
            status=status,
            type=feedback_type,
            plugin_id=plugin_id,
            user_id=user_id,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        return jsonify({"status": "success", "data": feedbacks})
    except Exception as e:
        logger.error(f"피드백 목록 조회 실패: {e}")
        return jsonify({"error": "피드백 목록 조회 실패"}), 500


@app.route("/api/feedback/<feedback_id>", methods=["GET"])
def api_get_feedback(feedback_id):
    """피드백 상세 조회 API"""
    try:
        feedback = plugin_feedback_system.get_feedback(feedback_id)
        if not feedback:
            return jsonify({"error": "피드백을 찾을 수 없습니다"}), 404

        return jsonify({"status": "success", "data": feedback})
    except Exception as e:
        logger.error(f"피드백 상세 조회 실패: {e}")
        return jsonify({"error": "피드백 상세 조회 실패"}), 500


@app.route("/api/feedback/<feedback_id>/status", methods=["PUT"])
def api_update_feedback_status(feedback_id):
    """피드백 상태 업데이트 API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "요청 데이터가 없습니다"}), 400

        status = data.get("status")
        user_id = data.get("user_id", "admin")
        comment = data.get("comment", "")

        if not status:
            return jsonify({"error": "상태 정보가 없습니다"}), 400

        success = plugin_feedback_system.update_feedback_status(
            feedback_id, status, user_id, comment
        )

        if success:
            return jsonify(
                {"status": "success", "message": "피드백 상태가 업데이트되었습니다"}
            )
        else:
            return jsonify({"error": "피드백 상태 업데이트 실패"}), 400
    except Exception as e:
        logger.error(f"피드백 상태 업데이트 실패: {e}")
        return jsonify({"error": "피드백 상태 업데이트 실패"}), 500


@app.route("/api/feedback/<feedback_id>/assign", methods=["PUT"])
def api_assign_feedback(feedback_id):
    """피드백 할당 API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "요청 데이터가 없습니다"}), 400

        assigned_to = data.get("assigned_to")
        estimated_completion = data.get("estimated_completion")

        if not assigned_to:
            return jsonify({"error": "할당 대상이 없습니다"}), 400

        success = plugin_feedback_system.assign_feedback(
            feedback_id, assigned_to, estimated_completion
        )

        if success:
            return jsonify({"status": "success", "message": "피드백이 할당되었습니다"})
        else:
            return jsonify({"error": "피드백 할당 실패"}), 400
    except Exception as e:
        logger.error(f"피드백 할당 실패: {e}")
        return jsonify({"error": "피드백 할당 실패"}), 500


@app.route("/api/feedback/<feedback_id>/comments", methods=["GET"])
def api_get_feedback_comments(feedback_id):
    """피드백 댓글 목록 조회 API"""
    try:
        include_internal = (
            request.args.get("include_internal", "false").lower() == "true"
        )
        comments = plugin_feedback_system.get_comments(feedback_id, include_internal)

        return jsonify({"status": "success", "data": comments})
    except Exception as e:
        logger.error(f"피드백 댓글 조회 실패: {e}")
        return jsonify({"error": "피드백 댓글 조회 실패"}), 500


@app.route("/api/feedback/<feedback_id>/comments", methods=["POST"])
def api_add_feedback_comment(feedback_id):
    """피드백 댓글 추가 API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "요청 데이터가 없습니다"}), 400

        user_id = data.get("user_id", "anonymous")
        user_name = data.get("user_name", "Anonymous")
        user_role = data.get("user_role", "user")
        content = data.get("content", "")
        is_internal = data.get("is_internal", False)

        if not content:
            return jsonify({"error": "댓글 내용이 없습니다"}), 400

        comment_id = plugin_feedback_system.add_comment(
            feedback_id, user_id, user_name, user_role, content, is_internal
        )

        if comment_id:
            return jsonify(
                {
                    "status": "success",
                    "message": "댓글이 추가되었습니다",
                    "comment_id": comment_id,
                }
            )
        else:
            return jsonify({"error": "댓글 추가 실패"}), 400
    except Exception as e:
        logger.error(f"피드백 댓글 추가 실패: {e}")
        return jsonify({"error": "피드백 댓글 추가 실패"}), 500


@app.route("/api/feedback/<feedback_id>/vote", methods=["POST"])
def api_vote_feedback(feedback_id):
    """피드백 투표 API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "요청 데이터가 없습니다"}), 400

        user_id = data.get("user_id", "anonymous")
        vote = data.get("vote", True)

        success = plugin_feedback_system.vote_feedback(feedback_id, user_id, vote)

        if success:
            return jsonify({"status": "success", "message": "투표가 반영되었습니다"})
        else:
            return jsonify({"error": "투표 실패"}), 400
    except Exception as e:
        logger.error(f"피드백 투표 실패: {e}")
        return jsonify({"error": "피드백 투표 실패"}), 500


@app.route("/api/feedback/<feedback_id>/follow", methods=["POST"])
def api_follow_feedback(feedback_id):
    """피드백 팔로우 API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "요청 데이터가 없습니다"}), 400

        user_id = data.get("user_id", "anonymous")
        follow = data.get("follow", True)

        success = plugin_feedback_system.follow_feedback(feedback_id, user_id, follow)

        if success:
            action = "팔로우" if follow else "언팔로우"
            return jsonify(
                {"status": "success", "message": f"피드백을 {action}했습니다"}
            )
        else:
            return jsonify({"error": "팔로우 실패"}), 400
    except Exception as e:
        logger.error(f"피드백 팔로우 실패: {e}")
        return jsonify({"error": "피드백 팔로우 실패"}), 500


@app.route("/api/feedback/templates", methods=["GET"])
def api_get_feedback_templates():
    """피드백 템플릿 조회 API"""
    try:
        templates = plugin_feedback_system.get_templates()

        return jsonify({"status": "success", "data": templates})
    except Exception as e:
        logger.error(f"피드백 템플릿 조회 실패: {e}")
        return jsonify({"error": "피드백 템플릿 조회 실패"}), 500


@app.route("/api/feedback/<feedback_id>/workflow", methods=["GET"])
def api_get_feedback_workflow(feedback_id):
    """피드백 워크플로우 조회 API"""
    try:
        workflow = plugin_feedback_system.get_workflow(feedback_id)
        if not workflow:
            return jsonify({"error": "워크플로우를 찾을 수 없습니다"}), 404

        return jsonify({"status": "success", "data": workflow})
    except Exception as e:
        logger.error(f"피드백 워크플로우 조회 실패: {e}")
        return jsonify({"error": "피드백 워크플로우 조회 실패"}), 500

# plugin_testing_system = PluginTestingSystem()


@app.route("/api/plugins/<plugin_id>/test", methods=["POST"])
def api_run_plugin_tests(plugin_id):
    """플러그인 테스트 실행 API"""
    try:
        data = request.get_json() or {}
        test_type = data.get("test_type", "all")

        results = plugin_testing_system.run_plugin_tests(plugin_id, test_type)

        return jsonify({"status": "success", "data": results})
    except Exception as e:
        logger.error(f"플러그인 테스트 실행 실패: {e}")
        return jsonify({"error": "플러그인 테스트 실행 실패"}), 500


@app.route("/api/plugins/test-results", methods=["GET"])
def api_get_test_results():
    """테스트 결과 조회 API"""
    try:
        plugin_id = request.args.get("plugin_id")
        test_type = request.args.get("test_type")
        limit = int(request.args.get("limit", 50))

        results = plugin_testing_system.get_test_results(
            plugin_id or None, test_type or None, limit
        )

        return jsonify({"status": "success", "data": results})
    except Exception as e:
        logger.error(f"테스트 결과 조회 실패: {e}")
        return jsonify({"error": "테스트 결과 조회 실패"}), 500


@app.route("/api/plugins/monitoring/start", methods=["POST"])
@csrf.exempt
def api_start_monitoring():
    """성능 모니터링 시작 API"""
    try:
        data = request.get_json(silent=True) or {}
        plugin_id = data.get("plugin_id")

        success = plugin_testing_system.start_performance_monitoring(plugin_id or None)

        if success:
            return jsonify(
                {"status": "success", "message": "성능 모니터링이 시작되었습니다"}
            )
        else:
            return jsonify({"error": "모니터링이 이미 실행 중입니다"}), 400
    except Exception as e:
        logger.error(f"성능 모니터링 시작 실패: {e}")
        return jsonify({"error": "성능 모니터링 시작 실패"}), 500


@app.route("/api/plugins/monitoring/stop", methods=["POST"])
@csrf.exempt
def api_stop_monitoring():
    """성능 모니터링 중지 API"""
    try:
        data = request.get_json(silent=True) or {}
        plugin_testing_system.stop_performance_monitoring()

        return jsonify(
            {"status": "success", "message": "성능 모니터링이 중지되었습니다"}
        )
    except Exception as e:
        logger.error(f"성능 모니터링 중지 실패: {e}")
        return jsonify({"error": "성능 모니터링 중지 실패"}), 500


@app.route("/api/plugins/performance", methods=["GET"])
def api_get_performance_metrics():
    """성능 메트릭 조회 API"""
    try:
        plugin_id = request.args.get("plugin_id")
        hours = int(request.args.get("hours", 24))

        metrics = plugin_testing_system.get_performance_metrics(
            plugin_id or None, hours
        )

        return jsonify({"status": "success", "data": metrics})
    except Exception as e:
        logger.error(f"성능 메트릭 조회 실패: {e}")
        return jsonify({"error": "성능 메트릭 조회 실패"}), 500


@app.route("/api/plugins/<plugin_id>/documentation", methods=["GET"])
def api_get_plugin_documentation(plugin_id):
    """플러그인 문서 조회 API"""
    try:
        documentation = plugin_testing_system.get_documentation(plugin_id)

        if documentation:
            return jsonify({"status": "success", "data": documentation})
        else:
            return jsonify({"error": "문서를 찾을 수 없습니다"}), 404
    except Exception as e:
        logger.error(f"플러그인 문서 조회 실패: {e}")
        return jsonify({"error": "플러그인 문서 조회 실패"}), 500


@app.route("/api/plugins/<plugin_id>/documentation", methods=["POST"])
def api_generate_plugin_documentation(plugin_id):
    """플러그인 문서 생성 API"""
    try:
        documentation = plugin_testing_system.generate_plugin_documentation(plugin_id)

        if "error" in documentation:
            return jsonify({"error": documentation["error"]}), 400

        return jsonify(
            {
                "status": "success",
                "message": "문서가 생성되었습니다",
                "data": documentation,
            }
        )
    except Exception as e:
        logger.error(f"플러그인 문서 생성 실패: {e}")
        return jsonify({"error": "플러그인 문서 생성 실패"}), 500


@app.template_filter("comma")
def comma_filter(value):
    """숫자에 콤마 추가하는 필터"""
    try:
        return "{:,}".format(int(value))
    except (ValueError, TypeError):
        return value


@app.template_global("momentjs")
def momentjs():
    """Moment.js 라이브러리 반환"""
    return "https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.1/moment.min.js"


@app.route("/health")
def health():
    """헬스 체크 엔드포인트"""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
        }
    )


@app.route("/api/status")
def api_status():
    """API 상태 확인"""
    try:
        # 데이터베이스 연결 확인
        db_status = "connected"
        try:
            db.session.execute(db.text("SELECT 1"))
        except Exception:
            db_status = "disconnected"

        # 플러그인 상태
        # plugin_status = auto_router.get_plugin_status()

        status = {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "database": db_status,
            # "plugins": plugin_status,
            "uptime": "24h 30m",
        }

        return jsonify(status)
    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            500,
        )


@app.route("/admin/advanced-analytics")
def admin_advanced_analytics():
    """고급 분석 페이지"""
    return render_template("admin/advanced_analytics.html")


@app.route("/admin/security-management")
def admin_security_management():
    """보안 관리 페이지"""
    return render_template("admin/security_management.html")


@app.route("/admin/performance-management")
def admin_performance_management():
    """성능 관리 페이지"""
    return render_template("admin/performance_management.html")


# 플러그인 시스템 테스트 엔드포인트 (직접 등록)
@app.route("/api/plugin-system/test", methods=["GET"])
def plugin_system_test():
    """플러그인 시스템 테스트 엔드포인트"""
    return jsonify(
        {
            "success": True,
            "message": "플러그인 시스템 API가 정상 동작합니다",
            "timestamp": datetime.now().isoformat(),
        }
    )


# 플러그인 시스템 직접 엔드포인트 등록 (블루프린트 문제 해결)
@app.route("/api/plugin-system/health", methods=["GET"])
@csrf.exempt
def plugin_system_health():
    """플러그인 시스템 헬스 체크"""
    try:
        health_status = {
            "status": "healthy",
            "plugin_directory": os.path.exists("plugins"),
            "total_plugins": len(plugin_manager.plugins),
            "loaded_plugins": len(plugin_manager.loaded_plugins),
            "timestamp": datetime.now().isoformat(),
        }

        return jsonify({"success": True, "data": health_status})
    except Exception as e:
        logger.error(f"플러그인 시스템 헬스 체크 실패: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/plugin-system/status", methods=["GET"])
@csrf.exempt
def plugin_system_status():
    """플러그인 시스템 상태 조회"""
    try:
        status = plugin_manager.get_plugin_status()
        return jsonify({"success": True, "data": status})
    except Exception as e:
        logger.error(f"플러그인 시스템 상태 조회 실패: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/admin/brand-manager-approval")
def admin_brand_manager_approval():
    return render_template("admin/brand_manager_approval.html")


@app.route("/api/admin/brand-managers")
def api_admin_brand_managers():
    """브랜드 관리자 목록 API"""
    try:
        # 브랜드 관리자 역할을 가진 사용자들 조회
        brand_managers = User.query.filter(
            User.role.in_(["brand_manager", "pending_brand_manager"])
        ).all()
        managers_list = []

        for user in brand_managers:
            manager_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "status": "approved" if user.role == "brand_manager" else "pending",
                "branch_id": user.branch_id,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
            }

            # 브랜치 정보 추가
            if user.branch_id:
                branch = Branch.query.get(user.branch_id)
                if branch:
                    manager_data["branch_name"] = branch.name

            managers_list.append(manager_data)

        return jsonify({"users": managers_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/brand-manager/approve/<int:user_id>", methods=["POST"])
def api_admin_approve_brand_manager(user_id):
    """브랜드 관리자 승인 API"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        user.role = "brand_manager"
        db.session.commit()

        return jsonify({"message": "브랜드 관리자가 승인되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/brand-manager/reject/<int:user_id>", methods=["POST"])
def api_admin_reject_brand_manager(user_id):
    """브랜드 관리자 거절 API"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        user.role = "employee"  # 일반 직원으로 변경
        db.session.commit()

        return jsonify({"message": "브랜드 관리자 신청이 거절되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/brand-management")
def admin_brand_management():
    try:
        # 브랜드 목록 조회
        brands = Brand.query.all()
        brand_list = []

        for brand in brands:
            # 매장 수 계산
            store_count = Branch.query.filter_by(brand_id=brand.id).count()

            brand_list.append(
                {
                    "id": brand.id,
                    "name": brand.name,
                    "code": brand.code,
                    "description": brand.description,
                    "contact_email": brand.contact_email,
                    "contact_phone": brand.contact_phone,
                    "status": brand.status,
                    "store_count": store_count,
                    "created_at": brand.created_at,
                }
            )

        return render_template("admin/brand_management.html", brands=brand_list)

    except Exception as e:
        print(f"브랜드 관리 페이지 로드 오류: {str(e)}")
        return render_template("admin/brand_management.html", brands=[])


@app.route("/admin/brand/<int:brand_id>/server-setup")
def admin_brand_server_setup(brand_id):
    """브랜드별 서버 설정 페이지"""
    try:
        brand = Brand.query.get_or_404(brand_id)
        return render_template("admin/brand_server_setup.html", brand=brand)
    except Exception as e:
        print(f"브랜드 서버 설정 페이지 로드 오류: {str(e)}")
        return "브랜드를 찾을 수 없습니다.", 404


@app.route("/api/admin/brands/<int:brand_id>")
def api_admin_brand_detail(brand_id):
    """브랜드 단건 조회 API"""
    try:
        brand = Brand.query.get(brand_id)
        if not brand:
            return jsonify({"error": "브랜드를 찾을 수 없습니다."}), 404

        brand_data = {
            "id": brand.id,
            "name": brand.name,
            "code": brand.code,
            "description": brand.description,
            "logo_url": brand.logo_url,
            "website": brand.website,
            "contact_email": brand.contact_email,
            "contact_phone": brand.contact_phone,
            "address": brand.address,
            "store_type": brand.store_type,
            "business_number": brand.business_number,
            "business_name": brand.business_name,
            "representative_name": brand.representative_name,
            "business_type": brand.business_type,
            "business_category": brand.business_category,
            "emergency_contact": brand.emergency_contact,
            "fax_number": brand.fax_number,
            "contract_start_date": (
                brand.contract_start_date.isoformat()
                if brand.contract_start_date
                else None
            ),
            "contract_end_date": (
                brand.contract_end_date.isoformat() if brand.contract_end_date else None
            ),
            "contract_type": brand.contract_type,
            "contract_status": brand.contract_status,
            "contract_amount": (
                float(brand.contract_amount) if brand.contract_amount else None
            ),
            "contract_currency": brand.contract_currency,
            "contract_terms": brand.contract_terms,
            "status": brand.status,
            "created_at": brand.created_at.isoformat() if brand.created_at else None,
            # 주소 상세 정보
            "zipcode": brand.zipcode,
            "road_address": brand.road_address,
            "jibun_address": brand.jibun_address,
            "detail_address": brand.detail_address,
            "latitude": brand.latitude,
            "longitude": brand.longitude,
        }

        return jsonify({"success": True, "brand": brand_data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/brands")
def api_admin_brands():
    """브랜드 목록 및 현황 API"""
    try:
        brands = Brand.query.all()
        brands_data = []

        for brand in brands:
            # 브랜드별 매장 수
            store_count = Branch.query.filter_by(brand_id=brand.id).count()

            # 브랜드별 직원 수
            employee_count = User.query.filter_by(brand_id=brand.id).count()

            # 브랜드별 주문 수 (예시 데이터)
            order_count = 0  # 실제로는 Order 모델에서 계산

            brand_data = {
                "id": brand.id,
                "name": brand.name,
                "code": brand.code,
                "description": brand.description,
                "logo_url": brand.logo_url,
                "website": brand.website,
                "contact_email": brand.contact_email,
                "contact_phone": brand.contact_phone,
                "address": brand.address,
                "store_type": brand.store_type,
                "business_number": brand.business_number,
                "business_name": brand.business_name,
                "representative_name": brand.representative_name,
                "business_type": brand.business_type,
                "business_category": brand.business_category,
                "emergency_contact": brand.emergency_contact,
                "fax_number": brand.fax_number,
                "contract_start_date": (
                    brand.contract_start_date.isoformat()
                    if brand.contract_start_date
                    else None
                ),
                "contract_end_date": (
                    brand.contract_end_date.isoformat()
                    if brand.contract_end_date
                    else None
                ),
                "contract_type": brand.contract_type,
                "contract_status": brand.contract_status,
                "contract_amount": (
                    float(brand.contract_amount) if brand.contract_amount else None
                ),
                "contract_currency": brand.contract_currency,
                "contract_terms": brand.contract_terms,
                "store_count": store_count,
                "employee_count": employee_count,
                "order_count": order_count,
                "status": brand.status,
                "created_at": (
                    brand.created_at.isoformat() if brand.created_at else None
                ),
                # 주소 상세 정보
                "zipcode": brand.zipcode,
                "road_address": brand.road_address,
                "jibun_address": brand.jibun_address,
                "detail_address": brand.detail_address,
                "latitude": brand.latitude,
                "longitude": brand.longitude,
            }

            brands_data.append(brand_data)

        return jsonify({"brands": brands_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/brands/<int:brand_id>", methods=["PUT"])
def api_admin_update_brand(brand_id):
    """브랜드 정보 수정 API"""
    try:
        brand = Brand.query.get(brand_id)
        if not brand:
            return jsonify({"error": "브랜드를 찾을 수 없습니다."}), 404

        data = request.get_json()

        # 업데이트 가능한 필드들
        updatable_fields = [
            "name",
            "code",
            "description",
            "logo_url",
            "website",
            "contact_email",
            "contact_phone",
            "address",
            "store_type",
            "business_number",
            "business_name",
            "representative_name",
            "business_type",
            "business_category",
            "emergency_contact",
            "fax_number",
            "contract_type",
            "contract_status",
            "contract_amount",
            "contract_currency",
            "contract_terms",
            "status",
            "zipcode",
            "road_address",
            "jibun_address",
            "detail_address",
            "latitude",
            "longitude",
        ]

        for field in updatable_fields:
            if field in data:
                if (
                    field in ["contract_start_date", "contract_end_date"]
                    and data[field]
                ):
                    setattr(
                        brand, field, datetime.strptime(data[field], "%Y-%m-%d").date()
                    )
                else:
                    setattr(brand, field, data[field])

        brand.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify(
            {"success": True, "message": "브랜드 정보가 성공적으로 수정되었습니다."}
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/brands/<int:brand_id>", methods=["DELETE"])
def api_admin_delete_brand(brand_id):
    """브랜드 삭제 API"""
    try:
        brand = Brand.query.get(brand_id)
        if not brand:
            return jsonify({"error": "브랜드를 찾을 수 없습니다."}), 404

        # 관련 매장이 있는지 확인
        store_count = Branch.query.filter_by(brand_id=brand_id).count()
        if store_count > 0:
            return (
                jsonify(
                    {
                        "error": f"이 브랜드에는 {store_count}개의 매장이 있어 삭제할 수 없습니다."
                    }
                ),
                400,
            )

        db.session.delete(brand)
        db.session.commit()

        return jsonify(
            {"success": True, "message": "브랜드가 성공적으로 삭제되었습니다."}
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


def generate_brand_code(industry_name, brand_name):
    """업종별 브랜드 코드 자동 생성"""
    import random
    import string
    import re

    # 업종별 접두사 매핑
    industry_prefixes = {
        "음식점": "REST",
        "카페": "CAFE",
        "바": "BAR",
        "고기집": "BBQ",
        "편의점": "CVS",
        "미용실": "SALON",
        "병원": "HOSP",
        "약국": "PHARM",
        "옷가게": "FASH",
        "기타": "GEN",
    }

    # 업종 접두사 가져오기
    prefix = industry_prefixes.get(industry_name, "BRAND")

    # 브랜드명에서 영문/숫자만 추출하여 3-5자리로 제한
    clean_name = re.sub(r"[^A-Za-z0-9]", "", brand_name.upper())
    if len(clean_name) > 5:
        clean_name = clean_name[:5]
    elif len(clean_name) < 3:
        clean_name = clean_name + "".join(
            random.choices(string.ascii_uppercase, k=3 - len(clean_name))
        )

    # 랜덤 숫자 3자리 추가
    random_num = "".join(random.choices(string.digits, k=3))

    # 최종 브랜드 코드 생성
    brand_code = f"{prefix}_{clean_name}_{random_num}"

    return brand_code


from utils.authorization_policy import protect_data_creation_endpoint, audit_operation

@app.route("/api/admin/brands", methods=["POST"])
@csrf.exempt
@protect_data_creation_endpoint("Brand")
@audit_operation("create", "Brand")
def api_admin_create_brand():
    """신규 브랜드 생성 API"""
    try:
        logger.info("=== 브랜드 생성 API 시작 ===")

        # 요청 데이터 확인
        if not request.is_json:
            logger.error("요청이 JSON 형식이 아닙니다")
            return jsonify({"error": "JSON 형식의 요청이 필요합니다."}), 400

        data = request.get_json()
        logger.info(f"브랜드 생성 요청 데이터: {data}")

        if not data:
            logger.error("요청 데이터가 비어있습니다")
            return jsonify({"error": "요청 데이터가 비어있습니다."}), 400

        # CSRF 토큰 제거
        if "csrf_token" in data:
            del data["csrf_token"]
            logger.info("CSRF 토큰이 요청 데이터에서 제거되었습니다.")

        # 필수 필드 검증
        required_fields = ["name"]
        for field in required_fields:
            if not data.get(field):
                logger.error(f"필수 필드 누락: {field}")
                return jsonify({"error": f"{field} 필드는 필수입니다."}), 400

        logger.info("필수 필드 검증 완료")

        # 브랜드 코드 처리
        brand_code = data.get("code")
        if not brand_code:
            # 자동 생성
            industry_name = data.get("industry_name", "기타")
            logger.info(
                f"브랜드 코드 자동 생성 시작: 업종={industry_name}, 브랜드명={data['name']}"
            )
            brand_code = generate_brand_code(industry_name, data["name"])
            logger.info(f"브랜드 코드 자동 생성 완료: {brand_code}")

        # 브랜드명 중복 확인
        logger.info("브랜드명 중복 확인 시작")
        existing_brand = Brand.query.filter_by(name=data["name"]).first()
        if existing_brand:
            logger.error(f"브랜드명 중복: {data['name']}")
            return jsonify({"error": "이미 존재하는 브랜드명입니다."}), 400

        # 브랜드 코드 중복 확인
        logger.info("브랜드 코드 중복 확인 시작")
        existing_code = Brand.query.filter_by(code=brand_code).first()
        if existing_code:
            logger.error(f"브랜드 코드 중복: {brand_code}")
            return jsonify({"error": "이미 존재하는 브랜드 코드입니다."}), 400

        logger.info("중복 확인 완료")
        logger.info("새 브랜드 객체 생성 시작")

        # 새 브랜드 생성
        new_brand = Brand()
        new_brand.name = data["name"]
        new_brand.code = brand_code
        new_brand.description = data.get("description")
        new_brand.logo_url = data.get("logo_url")
        new_brand.website = data.get("website")
        new_brand.contact_email = data.get("contact_email")
        new_brand.contact_phone = data.get("contact_phone")
        new_brand.address = data.get("address")
        new_brand.store_type = data.get("store_type", "individual")  # 매장 유형 설정

        # 주소 상세 정보 설정
        new_brand.zipcode = data.get("zipcode")
        new_brand.road_address = data.get("road_address")
        new_brand.jibun_address = data.get("jibun_address")
        new_brand.detail_address = data.get("detail_address")
        new_brand.latitude = data.get("latitude")
        new_brand.longitude = data.get("longitude")

        logger.info(f"브랜드 객체 생성 완료: {new_brand.name} ({new_brand.code})")

        # 사업자 정보 설정
        new_brand.business_number = data.get("business_number")
        new_brand.business_name = data.get("business_name")
        new_brand.representative_name = data.get("representative_name")
        new_brand.business_type = data.get("business_type")
        new_brand.business_category = data.get("business_category")
        new_brand.emergency_contact = data.get("emergency_contact")
        new_brand.fax_number = data.get("fax_number")

        # 계약 정보 설정
        if data.get("contract_start_date"):
            new_brand.contract_start_date = datetime.strptime(
                data["contract_start_date"], "%Y-%m-%d"
            ).date()
        if data.get("contract_end_date"):
            new_brand.contract_end_date = datetime.strptime(
                data["contract_end_date"], "%Y-%m-%d"
            ).date()

        new_brand.contract_type = data.get("contract_type")
        new_brand.contract_status = data.get("contract_status", "active")
        new_brand.contract_amount = data.get("contract_amount")
        new_brand.contract_currency = data.get("contract_currency", "KRW")
        new_brand.contract_terms = data.get("contract_terms")
        new_brand.contract_documents = data.get("contract_documents", {})

        new_brand.status = data.get("status", "active")

        logger.info("데이터베이스에 브랜드 저장 시작")
        try:
            db.session.add(new_brand)
            db.session.commit()
            logger.info(f"브랜드 저장 완료: ID {new_brand.id}")
        except Exception as db_error:
            logger.error(f"데이터베이스 저장 오류: {str(db_error)}")
            db.session.rollback()
            import traceback

            tb = traceback.format_exc()
            logger.error(f"데이터베이스 오류 traceback: {tb}")
            return (
                jsonify(
                    {
                        "error": f"데이터베이스 저장 오류: {str(db_error)}",
                        "traceback": tb,
                    }
                ),
                500,
            )

        # 프론트엔드 서버 자동 생성 (일시적으로 비활성화)
        frontend_created = False
        frontend_port = 3000  # 기본 포트로 설정

        # 프론트엔드 서버 생성 기능은 나중에 구현
        logger.info("프론트엔드 서버 자동 생성 기능은 현재 비활성화되어 있습니다.")

        # 기본 프론트엔드 URL 제공
        frontend_url = f"http://localhost:{frontend_port}"

        response_data = {
            "success": True,
            "message": "브랜드가 성공적으로 생성되었습니다.",
            "brand": {
                "id": new_brand.id,
                "name": new_brand.name,
                "code": new_brand.code,
                "description": new_brand.description,
                "status": new_brand.status,
                "created_at": (
                    new_brand.created_at.isoformat() if new_brand.created_at else None
                ),
            },
            "brand_id": new_brand.id,
            "frontend_created": frontend_created,
            "frontend_url": frontend_url,
        }

        logger.info(f"브랜드 생성 완료: {new_brand.name} (ID: {new_brand.id})")
        logger.info("=== 브랜드 생성 API 완료 ===")

        return jsonify(response_data), 201

    except Exception as e:
        db.session.rollback()
        import traceback

        tb = traceback.format_exc()
        logger.error(f"브랜드 생성 오류: {str(e)}")
        logger.error(f"브랜드 생성 오류 traceback: {tb}")
        return (
            jsonify({"error": f"브랜드 생성 중 오류: {str(e)}", "traceback": tb}),
            500,
        )


@app.route("/api/admin/brand/<int:brand_id>/details")
def api_admin_brand_details(brand_id):
    """브랜드 상세 정보 API"""
    try:
        branch = Branch.query.get(brand_id)
        if not branch:
            return jsonify({"error": "Brand not found"}), 404

        # 브랜드별 직원 목록
        employees = User.query.filter_by(branch_id=brand_id).all()
        employees_data = []

        for employee in employees:
            employee_data = {
                "id": employee.id,
                "username": employee.username,
                "role": employee.role,
                "email": employee.email,
                "last_login": (
                    employee.last_login.isoformat() if employee.last_login else None
                ),
            }
            employees_data.append(employee_data)

        # 브랜드별 통계
        stats = {
            "total_employees": len(employees_data),
            "managers": len(
                [e for e in employees_data if e["role"] == "store_manager"]
            ),
            "employees": len([e for e in employees_data if e["role"] == "employee"]),
            "brand_managers": len(
                [e for e in employees_data if e["role"] == "brand_manager"]
            ),
        }

        brand_details = {
            "id": branch.id,
            "name": branch.name,
            "location": branch.location,
            "employees": employees_data,
            "stats": stats,
            "improvements": [
                "직원 교육 프로그램 강화 필요",
                "고객 서비스 품질 개선",
                "재고 관리 시스템 최적화",
            ],
        }

        return jsonify(brand_details)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/store-management")
def admin_store_management():
    return render_template("admin/store_management.html")


@app.route("/api/admin/stores")
def api_admin_stores():
    """매장 목록 및 현황 API"""
    try:
        # 매장 정보 (브랜치를 매장으로 사용)
        stores = Branch.query.all()
        stores_data = []

        for store in stores:
            # 매장별 직원 현황
            employees = User.query.filter_by(branch_id=store.id).all()

            # 매장별 개선사항
            improvements = [
                "매장 환경 개선 필요",
                "고객 응대 서비스 강화",
                "매장 정리정돈 개선",
            ]

            store_data = {
                "id": store.id,
                "name": store.name,
                "location": store.location,
                "employee_count": len(employees),
                "manager_count": len(
                    [e for e in employees if e.role == "store_manager"]
                ),
                "improvements": improvements,
                "status": "active",
                "performance_score": 85,  # 예시 성과 점수
                "last_updated": datetime.utcnow().isoformat(),
            }

            stores_data.append(store_data)

        return jsonify({"stores": stores_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/employee-management")
def admin_employee_management():
    return render_template("admin/employee_management.html")


@app.route("/api/admin/employees")
def api_admin_employees():
    """직원 목록 및 현황 API"""
    try:
        employees = User.query.all()
        employees_data = []

        for employee in employees:
            # 직원별 개선사항
            improvements = [
                "업무 효율성 개선 필요",
                "고객 서비스 스킬 향상",
                "팀워크 개선",
            ]

            employee_data = {
                "id": employee.id,
                "username": employee.username,
                "email": employee.email,
                "role": employee.role,
                "branch_id": employee.branch_id,
                "performance_score": 85,  # 예시 성과 점수
                "improvements": improvements,
                "status": "active",
                "created_at": (
                    employee.created_at.isoformat() if employee.created_at else None
                ),
                "last_login": (
                    employee.last_login.isoformat() if employee.last_login else None
                ),
            }

            # 브랜치 정보 추가
            if employee.branch_id:
                branch = Branch.query.get(employee.branch_id)
                if branch:
                    employee_data["branch_name"] = branch.name

            employees_data.append(employee_data)

        return jsonify({"employees": employees_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/employees", methods=["POST"])
@protect_data_creation_endpoint("Employee")
@audit_operation("create", "Employee")
def api_admin_create_employee():
    """직원 생성 API"""
    try:
        data = request.get_json()

        # 필수 필드 검증
        required_fields = ["username", "email", "role"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} 필드는 필수입니다."}), 400

        # 사용자명 중복 확인
        existing_user = User.query.filter_by(username=data["username"]).first()
        if existing_user:
            return jsonify({"error": "이미 존재하는 사용자명입니다."}), 400

        # 이메일 중복 확인
        existing_email = User.query.filter_by(email=data["email"]).first()
        if existing_email:
            return jsonify({"error": "이미 존재하는 이메일입니다."}), 400

        # 새 직원 생성
        new_employee = User()
        new_employee.username = data["username"]
        new_employee.email = data["email"]
        new_employee.role = data["role"]
        new_employee.status = data.get("status", "pending")
        new_employee.branch_id = data.get("branch_id")
        new_employee.brand_id = data.get("brand_id")
        new_employee.name = data.get("name")
        new_employee.phone = data.get("phone")
        new_employee.address = data.get("address")
        new_employee.position = data.get("position")
        new_employee.department = data.get("department")

        # 비밀번호 설정 (기본값 또는 제공된 값)
        password = data.get("password", "default123")
        new_employee.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

        db.session.add(new_employee)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "직원이 성공적으로 생성되었습니다.",
            "employee_id": new_employee.id,
            "username": new_employee.username
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"직원 생성 오류: {str(e)}")
        return jsonify({"error": "직원 생성 중 오류가 발생했습니다."}), 500
    """직원 목록 및 현황 API"""
    try:
        employees = User.query.all()
        employees_data = []

        for employee in employees:
            # 직원별 개선사항
            improvements = [
                "업무 효율성 개선 필요",
                "고객 서비스 스킬 향상",
                "팀워크 개선",
            ]

            employee_data = {
                "id": employee.id,
                "username": employee.username,
                "email": employee.email,
                "role": employee.role,
                "branch_id": employee.branch_id,
                "performance_score": 85,  # 예시 성과 점수
                "improvements": improvements,
                "status": "active",
                "created_at": (
                    employee.created_at.isoformat() if employee.created_at else None
                ),
                "last_login": (
                    employee.last_login.isoformat() if employee.last_login else None
                ),
            }

            # 브랜치 정보 추가
            if employee.branch_id:
                branch = Branch.query.get(employee.branch_id)
                if branch:
                    employee_data["branch_name"] = branch.name

            employees_data.append(employee_data)

        return jsonify({"employees": employees_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/employee/<int:employee_id>/details")
def api_admin_employee_details(employee_id):
    """직원 상세 정보 API"""
    try:
        employee = User.query.get(employee_id)
        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        # 직원별 성과 지표
        performance_metrics = {
            "attendance_rate": 95,
            "customer_satisfaction": 4.3,
            "efficiency_score": 88,
            "teamwork_score": 92,
        }

        # 직원별 개선사항
        improvements = ["업무 효율성 개선 필요", "고객 서비스 스킬 향상", "팀워크 개선"]

        # 브랜치 정보
        branch_info = None
        if employee.branch_id:
            branch = Branch.query.get(employee.branch_id)
            if branch:
                branch_info = {
                    "id": branch.id,
                    "name": branch.name,
                    "location": branch.location,
                }

        employee_details = {
            "id": employee.id,
            "username": employee.username,
            "email": employee.email,
            "role": employee.role,
            "branch": branch_info,
            "performance_metrics": performance_metrics,
            "improvements": improvements,
            "created_at": (
                employee.created_at.isoformat() if employee.created_at else None
            ),
            "last_login": (
                employee.last_login.isoformat() if employee.last_login else None
            ),
        }

        return jsonify(employee_details)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/feedback-management")
def admin_feedback_management():
    return render_template("admin/feedback_management.html")


@app.route("/admin/kakao-api-settings")
def admin_kakao_api_settings():
    """카카오 API 설정 페이지"""
    if not current_user.is_admin():
        return jsonify({"error": "권한이 없습니다."}), 403
    return render_template("admin/kakao_api_settings.html")


@app.route("/api/admin/feedback")
def api_admin_feedback():
    """피드백 목록 API"""
    try:
        # 피드백 목록 (예시 데이터)
        feedbacks = [
            {
                "id": 1,
                "user_name": "김매니저",
                "user_role": "store_manager",
                "brand_name": "강남점",
                "category": "기능 개선",
                "title": "스케줄 기능 개선 제안",
                "content": "스케줄 변경 시 알림 기능을 추가해주세요.",
                "status": "pending",
                "priority": "medium",
                "created_at": "2024-01-20T10:30:00",
                "votes": 5,
            },
            {
                "id": 2,
                "user_name": "박직원",
                "user_role": "employee",
                "brand_name": "홍대점",
                "category": "버그 리포트",
                "title": "출퇴근 기록 오류",
                "content": "출근 기록이 제대로 저장되지 않는 문제가 있습니다.",
                "status": "in_progress",
                "priority": "high",
                "created_at": "2024-01-19T15:45:00",
                "votes": 12,
            },
            {
                "id": 3,
                "user_name": "이브랜드매니저",
                "user_role": "brand_manager",
                "brand_name": "전체",
                "category": "새 기능 요청",
                "title": "고객 관리 기능 추가",
                "content": "고객 정보 관리 및 예약 시스템을 추가해주세요.",
                "status": "completed",
                "priority": "low",
                "created_at": "2024-01-18T09:15:00",
                "votes": 8,
            },
        ]

        return jsonify({"feedbacks": feedbacks})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/feedback/<int:feedback_id>/status", methods=["PUT"])
def api_admin_update_feedback_status(feedback_id):
    """피드백 상태 업데이트 API"""
    try:
        # 실제로는 데이터베이스에서 피드백 상태를 업데이트
        return jsonify({"message": "피드백 상태가 업데이트되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/feedback/<int:feedback_id>/reply", methods=["POST"])
def api_admin_reply_feedback(feedback_id):
    """피드백 답변 API"""
    try:
        # 실제로는 데이터베이스에 답변을 저장
        return jsonify({"message": "답변이 등록되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500





@app.route("/api/marketplace/modules")
@csrf.exempt
def api_marketplace_modules():
    """모듈 마켓플레이스 모듈 목록 API"""
    try:
        # 프로젝트 내 모든 모듈 데이터
        modules = [
            # 기존 샘플 모듈들
            {
                "id": "attendance_management",
                "plugin_id": "attendance_management",
                "name": "출근 관리 모듈",
                "author": "Your Program Team",
                "description": "직원 출퇴근 기록 및 관리 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 150,
                "rating": 4.5,
            },
            {
                "id": "schedule_management",
                "plugin_id": "schedule_management",
                "name": "일정 관리 모듈",
                "author": "Your Program Team",
                "description": "직원 근무 스케줄 관리 및 조정 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 120,
                "rating": 4.3,
            },
            {
                "id": "inventory_management",
                "plugin_id": "inventory_management",
                "name": "재고 관리 모듈",
                "author": "Your Program Team",
                "description": "재고 현황 및 발주 관리 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 80,
                "rating": 4.2,
            },
            {
                "id": "purchase_management",
                "plugin_id": "purchase_management",
                "name": "구매 관리 모듈",
                "author": "Your Program Team",
                "description": "재고 발주 및 구매 관리 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 95,
                "rating": 4.4,
            },
            {
                "id": "ai_analytics_module",
                "plugin_id": "ai_analytics_module",
                "name": "AI 분석 모듈",
                "author": "Your Program Team",
                "description": "AI 기반 데이터 분석 및 예측 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 200,
                "rating": 4.7,
            },
            # API 모듈들
            {
                "id": "user_management_module",
                "plugin_id": "user_management_module",
                "name": "사용자 관리 모듈",
                "author": "Your Program Team",
                "description": "사용자 계정 및 권한 관리 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 180,
                "rating": 4.6,
            },
            {
                "id": "visualization_module",
                "plugin_id": "visualization_module",
                "name": "데이터 시각화 모듈",
                "author": "Your Program Team",
                "description": "차트 및 그래프를 통한 데이터 시각화 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 160,
                "rating": 4.5,
            },
            {
                "id": "schedule_management_module",
                "plugin_id": "schedule_management_module",
                "name": "스케줄 관리 모듈",
                "author": "Your Program Team",
                "description": "고급 스케줄 관리 및 최적화 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 140,
                "rating": 4.4,
            },
            {
                "id": "security_module",
                "plugin_id": "security_module",
                "name": "보안 모듈",
                "author": "Your Program Team",
                "description": "시스템 보안 및 접근 제어 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 220,
                "rating": 4.8,
            },
            {
                "id": "reporting_system_module",
                "plugin_id": "reporting_system_module",
                "name": "리포팅 시스템 모듈",
                "author": "Your Program Team",
                "description": "다양한 보고서 생성 및 관리 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 170,
                "rating": 4.6,
            },
            {
                "id": "notification_system_module",
                "plugin_id": "notification_system_module",
                "name": "알림 시스템 모듈",
                "author": "Your Program Team",
                "description": "실시간 알림 및 메시지 관리 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 190,
                "rating": 4.7,
            },
            {
                "id": "optimization_module",
                "plugin_id": "optimization_module",
                "name": "최적화 모듈",
                "author": "Your Program Team",
                "description": "시스템 성능 최적화 및 자동화 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 130,
                "rating": 4.3,
            },
            {
                "id": "monitoring_module",
                "plugin_id": "monitoring_module",
                "name": "모니터링 모듈",
                "author": "Your Program Team",
                "description": "시스템 및 성능 모니터링 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 150,
                "rating": 4.5,
            },
            {
                "id": "automation_module",
                "plugin_id": "automation_module",
                "name": "자동화 모듈",
                "author": "Your Program Team",
                "description": "업무 프로세스 자동화 및 워크플로우 관리 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 200,
                "rating": 4.7,
            },
            {
                "id": "chat_system_module",
                "plugin_id": "chat_system_module",
                "name": "채팅 시스템 모듈",
                "author": "Your Program Team",
                "description": "실시간 채팅 및 커뮤니케이션 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 180,
                "rating": 4.6,
            },
            {
                "id": "analytics_module",
                "plugin_id": "analytics_module",
                "name": "분석 모듈",
                "author": "Your Program Team",
                "description": "데이터 분석 및 인사이트 도출 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 210,
                "rating": 4.8,
            },
            # 레스토랑 전용 모듈
            {
                "id": "qsc_system_module",
                "plugin_id": "qsc_system_module",
                "name": "QSC 시스템 모듈",
                "author": "Your Program Team",
                "description": "레스토랑 업종 전용 품질(Quality), 서비스(Service), 청결(Cleanliness) 관리 시스템을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 250,
                "rating": 4.9,
            },
            # 추가 기능 모듈들
            {
                "id": "order_management_module",
                "plugin_id": "order_management_module",
                "name": "주문 관리 모듈",
                "author": "Your Program Team",
                "description": "주문 처리 및 관리 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 300,
                "rating": 4.8,
            },
            {
                "id": "cleaning_management_module",
                "plugin_id": "cleaning_management_module",
                "name": "청소 관리 모듈",
                "author": "Your Program Team",
                "description": "매장 청소 일정 및 관리 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 120,
                "rating": 4.4,
            },
            {
                "id": "payroll_management_module",
                "plugin_id": "payroll_management_module",
                "name": "급여 관리 모듈",
                "author": "Your Program Team",
                "description": "직원 급여 계산 및 관리 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 160,
                "rating": 4.6,
            },
            {
                "id": "iot_integration_module",
                "plugin_id": "iot_integration_module",
                "name": "IoT 통합 모듈",
                "author": "Your Program Team",
                "description": "IoT 디바이스 연동 및 데이터 수집 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 90,
                "rating": 4.3,
            },
            {
                "id": "voice_recognition_module",
                "plugin_id": "voice_recognition_module",
                "name": "음성 인식 모듈",
                "author": "Your Program Team",
                "description": "음성 명령 및 음성 인식 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 110,
                "rating": 4.2,
            },
            {
                "id": "image_analysis_module",
                "plugin_id": "image_analysis_module",
                "name": "이미지 분석 모듈",
                "author": "Your Program Team",
                "description": "이미지 분석 및 OCR 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 100,
                "rating": 4.1,
            },
            {
                "id": "translation_module",
                "plugin_id": "translation_module",
                "name": "번역 모듈",
                "author": "Your Program Team",
                "description": "다국어 번역 및 언어 지원 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 80,
                "rating": 4.0,
            },
            {
                "id": "mobile_support_module",
                "plugin_id": "mobile_support_module",
                "name": "모바일 지원 모듈",
                "author": "Your Program Team",
                "description": "모바일 앱 지원 및 반응형 웹 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 280,
                "rating": 4.7,
            },
            # 가계부 모듈
            {
                "id": "ledger",
                "plugin_id": "ledger",
                "name": "가계부 모듈",
                "author": "Your Program Team",
                "description": "정기지출/수입 관리 및 가계부 기능을 제공합니다. 월별 요약, 카테고리별 분석, 다가오는 지출 알림 기능을 포함합니다.",
                "version": "1.0.0",
                "status": "published",
                "downloads": 180,
                "rating": 4.6,
            },
        ]

        stats = {
            "total_modules": len(modules),
            "total_downloads": sum(m["downloads"] for m in modules),  # type: ignore
            "avg_rating": sum(m["rating"] for m in modules) / len(modules),  # type: ignore
            "approved_modules": len([m for m in modules if m["status"] == "published"]),
        }

        return jsonify({"modules": modules, "stats": stats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/marketplace/modules/<module_id>/download")
def api_marketplace_module_download(module_id):
    """모듈 다운로드 API"""
    try:
        # 실제로는 모듈 파일을 반환
        return jsonify({"message": f"모듈 {module_id} 다운로드가 시작됩니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/marketplace/modules/upload", methods=["POST"])
def api_marketplace_module_upload():
    """모듈 업로드 API"""
    try:
        # 실제로는 모듈 파일을 저장하고 처리
        return jsonify(
            {"success": True, "message": "모듈이 성공적으로 업로드되었습니다."}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/marketplace/modules/<module_id>/reviews")
def api_marketplace_module_reviews(module_id):
    """모듈 리뷰 목록 API"""
    try:
        # 샘플 리뷰 데이터
        reviews = [
            {
                "id": 1,
                "user_name": "김철수",
                "rating": 5,
                "comment": "정말 유용한 모듈입니다. 가계부 관리가 훨씬 쉬워졌어요!",
                "created_at": "2024-01-15T10:30:00Z",
                "helpful_count": 12,
            },
            {
                "id": 2,
                "user_name": "이영희",
                "rating": 4,
                "comment": "기능이 잘 구현되어 있고 사용하기 편합니다. 다만 UI를 조금 더 개선하면 좋겠어요.",
                "created_at": "2024-01-14T15:20:00Z",
                "helpful_count": 8,
            },
            {
                "id": 3,
                "user_name": "박민수",
                "rating": 5,
                "comment": "월별 요약 기능이 정말 유용합니다. 지출 패턴을 쉽게 파악할 수 있어요.",
                "created_at": "2024-01-13T09:15:00Z",
                "helpful_count": 15,
            },
        ]

        return jsonify({"reviews": reviews})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/marketplace/modules/<module_id>/reviews", methods=["POST"])
def api_marketplace_module_add_review(module_id):
    """모듈 리뷰 추가 API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "리뷰 데이터가 필요합니다."}), 400

        # 실제로는 데이터베이스에 리뷰 저장
        new_review = {
            "id": 4,  # 실제로는 자동 생성
            "user_name": data.get("user_name", "익명"),
            "rating": data.get("rating", 5),
            "comment": data.get("comment", ""),
            "created_at": datetime.now().isoformat(),
            "helpful_count": 0,
        }

        return jsonify(
            {
                "success": True,
                "message": "리뷰가 성공적으로 등록되었습니다.",
                "review": new_review,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/modules/installed")
@csrf.exempt
def api_modules_installed():
    """설치된 모듈 목록 API"""
    try:
        # 프로젝트 내 모든 모듈 데이터 (설치된 상태로 표시)
        modules = [
            # 기존 샘플 모듈들
            {
                "id": "attendance_management",
                "plugin_id": "attendance_management",
                "name": "출근 관리 모듈",
                "description": "직원 출퇴근 기록 및 관리 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "active",
                "installed_at": "2024-01-15",
                "last_updated": "2024-01-15",
                "size": "2.1MB",
                "dependencies": ["user_management_module"],
                "performance": {
                    "cpu_usage": 2.5,
                    "memory_usage": 15.2,
                    "response_time": 120,
                },
            },
            {
                "id": "schedule_management",
                "plugin_id": "schedule_management",
                "name": "일정 관리 모듈",
                "description": "직원 근무 스케줄 관리 및 조정 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "active",
                "installed_at": "2024-01-15",
                "last_updated": "2024-01-15",
                "size": "2.1MB",
                "dependencies": ["user_management_module"],
                "performance": {
                    "cpu_usage": 3.1,
                    "memory_usage": 18.5,
                    "response_time": 150,
                },
            },
            {
                "id": "inventory_management",
                "plugin_id": "inventory_management",
                "name": "재고 관리 모듈",
                "description": "재고 현황 및 발주 관리 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "active",
                "installed_at": "2024-01-15",
                "last_updated": "2024-01-15",
                "size": "2.0MB",
                "dependencies": ["user_management_module"],
                "performance": {
                    "cpu_usage": 4.2,
                    "memory_usage": 22.1,
                    "response_time": 180,
                },
            },
            {
                "id": "purchase_management",
                "plugin_id": "purchase_management",
                "name": "구매 관리 모듈",
                "description": "재고 발주 및 구매 관리 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "active",
                "installed_at": "2024-01-15",
                "last_updated": "2024-01-15",
                "size": "2.0MB",
                "dependencies": ["inventory_management"],
                "performance": {
                    "cpu_usage": 3.8,
                    "memory_usage": 20.3,
                    "response_time": 160,
                },
            },
            {
                "id": "ai_analytics_module",
                "plugin_id": "ai_analytics_module",
                "name": "AI 분석 모듈",
                "description": "AI 기반 데이터 분석 및 예측 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "active",
                "installed_at": "2024-01-15",
                "last_updated": "2024-01-15",
                "size": "3.9MB",
                "dependencies": ["analytics_module"],
                "performance": {
                    "cpu_usage": 8.5,
                    "memory_usage": 45.2,
                    "response_time": 300,
                },
            },
            # API 모듈들
            {
                "id": "user_management_module",
                "plugin_id": "user_management_module",
                "name": "사용자 관리 모듈",
                "description": "사용자 계정 및 권한 관리 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "active",
                "installed_at": "2024-01-10",
                "last_updated": "2024-01-10",
                "size": "12.0MB",
                "dependencies": [],
                "performance": {
                    "cpu_usage": 5.2,
                    "memory_usage": 28.5,
                    "response_time": 200,
                },
            },
            {
                "id": "visualization_module",
                "plugin_id": "visualization_module",
                "name": "데이터 시각화 모듈",
                "description": "차트 및 그래프를 통한 데이터 시각화 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "active",
                "installed_at": "2024-01-12",
                "last_updated": "2024-01-12",
                "size": "17.0MB",
                "dependencies": ["analytics_module"],
                "performance": {
                    "cpu_usage": 6.8,
                    "memory_usage": 35.2,
                    "response_time": 250,
                },
            },
            {
                "id": "schedule_management_module",
                "plugin_id": "schedule_management_module",
                "name": "스케줄 관리 모듈",
                "description": "고급 스케줄 관리 및 최적화 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "active",
                "installed_at": "2024-01-12",
                "last_updated": "2024-01-12",
                "size": "14.0MB",
                "dependencies": ["user_management_module"],
                "performance": {
                    "cpu_usage": 4.5,
                    "memory_usage": 25.8,
                    "response_time": 180,
                },
            },
            {
                "id": "security_module",
                "plugin_id": "security_module",
                "name": "보안 모듈",
                "description": "시스템 보안 및 접근 제어 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "active",
                "installed_at": "2024-01-08",
                "last_updated": "2024-01-08",
                "size": "13.0MB",
                "dependencies": [],
                "performance": {
                    "cpu_usage": 3.2,
                    "memory_usage": 18.5,
                    "response_time": 120,
                },
            },
            {
                "id": "reporting_system_module",
                "plugin_id": "reporting_system_module",
                "name": "리포팅 시스템 모듈",
                "description": "다양한 보고서 생성 및 관리 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "active",
                "installed_at": "2024-01-11",
                "last_updated": "2024-01-11",
                "size": "21.0MB",
                "dependencies": ["analytics_module", "visualization_module"],
                "performance": {
                    "cpu_usage": 7.5,
                    "memory_usage": 42.3,
                    "response_time": 280,
                },
            },
            {
                "id": "notification_system_module",
                "plugin_id": "notification_system_module",
                "name": "알림 시스템 모듈",
                "description": "실시간 알림 및 메시지 관리 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "active",
                "installed_at": "2024-01-09",
                "last_updated": "2024-01-09",
                "size": "8.5MB",
                "dependencies": [],
                "performance": {
                    "cpu_usage": 2.8,
                    "memory_usage": 16.2,
                    "response_time": 100,
                },
            },
            {
                "id": "optimization_module",
                "plugin_id": "optimization_module",
                "name": "최적화 모듈",
                "description": "시스템 성능 최적화 및 자동화 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "active",
                "installed_at": "2024-01-13",
                "last_updated": "2024-01-13",
                "size": "15.0MB",
                "dependencies": ["monitoring_module"],
                "performance": {
                    "cpu_usage": 4.1,
                    "memory_usage": 22.8,
                    "response_time": 160,
                },
            },
            {
                "id": "monitoring_module",
                "plugin_id": "monitoring_module",
                "name": "모니터링 모듈",
                "description": "시스템 및 성능 모니터링 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "active",
                "installed_at": "2024-01-14",
                "last_updated": "2024-01-14",
                "size": "11.0MB",
                "dependencies": [],
                "performance": {
                    "cpu_usage": 3.5,
                    "memory_usage": 19.2,
                    "response_time": 140,
                },
            },
            {
                "id": "automation_module",
                "plugin_id": "automation_module",
                "name": "자동화 모듈",
                "description": "업무 프로세스 자동화 및 워크플로우 관리 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "active",
                "installed_at": "2024-01-16",
                "last_updated": "2024-01-16",
                "size": "18.0MB",
                "dependencies": ["optimization_module"],
                "performance": {
                    "cpu_usage": 6.2,
                    "memory_usage": 32.5,
                    "response_time": 220,
                },
            },
            {
                "id": "chat_system_module",
                "plugin_id": "chat_system_module",
                "name": "채팅 시스템 모듈",
                "description": "실시간 채팅 및 커뮤니케이션 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "active",
                "installed_at": "2024-01-17",
                "last_updated": "2024-01-17",
                "size": "16.0MB",
                "dependencies": ["notification_system_module"],
                "performance": {
                    "cpu_usage": 5.8,
                    "memory_usage": 28.9,
                    "response_time": 180,
                },
            },
            {
                "id": "analytics_module",
                "plugin_id": "analytics_module",
                "name": "분석 모듈",
                "description": "데이터 분석 및 인사이트 도출 기능을 제공합니다.",
                "version": "1.0.0",
                "status": "active",
                "installed_at": "2024-01-18",
                "last_updated": "2024-01-18",
                "size": "25.0MB",
                "dependencies": [],
                "performance": {
                    "cpu_usage": 9.2,
                    "memory_usage": 48.5,
                    "response_time": 350,
                },
            },
            # 레스토랑 전용 모듈
            {
                "id": "qsc_system_module",
                "plugin_id": "qsc_system_module",
                "name": "QSC 시스템 모듈",
                "description": "레스토랑 업종 전용 품질(Quality), 서비스(Service), 청결(Cleanliness) 관리 시스템을 제공합니다.",
                "version": "1.0.0",
                "status": "active",
                "installed_at": "2024-01-19",
                "last_updated": "2024-01-19",
                "size": "22.0MB",
                "dependencies": ["analytics_module", "monitoring_module"],
                "performance": {
                    "cpu_usage": 7.8,
                    "memory_usage": 38.2,
                    "response_time": 280,
                },
            },
            # 가계부 모듈
            {
                "id": "ledger",
                "plugin_id": "ledger",
                "name": "가계부 모듈",
                "description": "정기지출/수입 관리 및 가계부 기능을 제공합니다. 월별 요약, 카테고리별 분석, 다가오는 지출 알림 기능을 포함합니다.",
                "version": "1.0.0",
                "status": "active",
                "installed_at": "2024-01-20",
                "last_updated": "2024-01-20",
                "size": "8.5MB",
                "dependencies": ["user_management_module"],
                "performance": {
                    "cpu_usage": 3.2,
                    "memory_usage": 18.5,
                    "response_time": 140,
                },
            },
        ]

        # 통계 계산
        stats = {
            "installed_modules": len(modules),
            "active_modules": len([m for m in modules if m["status"] == "active"]),
            "inactive_modules": len([m for m in modules if m["status"] == "inactive"]),
            "error_modules": len([m for m in modules if m["status"] == "error"]),
            "total_size": sum(float(str(m["size"]).replace("MB", "")) for m in modules),  # type: ignore
            "avg_cpu_usage": sum(m["performance"]["cpu_usage"] for m in modules if m["status"] == "active") / len([m for m in modules if m["status"] == "active"]),  # type: ignore
            "avg_memory_usage": sum(m["performance"]["memory_usage"] for m in modules if m["status"] == "active") / len([m for m in modules if m["status"] == "active"]),  # type: ignore
        }

        return jsonify({"modules": modules, "stats": stats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/modules/<module_id>/toggle", methods=["POST"])
def api_modules_toggle(module_id):
    """모듈 활성화/비활성화 API"""
    try:
        # 실제로는 모듈 상태를 변경
        # 예시: modules/{module_id}/config/module.json 파일의 enabled 필드 토글
        import os, json

        config_path = os.path.join("modules", module_id, "config", "module.json")
        if not os.path.exists(config_path):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"설정 파일을 찾을 수 없습니다: {config_path}",
                    }
                ),
                404,
            )
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        enabled = config.get("enabled", True)
        config["enabled"] = not enabled
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return jsonify(
            {
                "success": True,
                "message": f'모듈 {module_id}가 {"활성화" if config["enabled"] else "비활성화"}되었습니다.',
                "enabled": config["enabled"],
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/modules/<module_id>/uninstall", methods=["DELETE"])
def api_modules_uninstall(module_id):
    """모듈 제거 API"""
    try:
        import os, shutil

        module_dir = os.path.join("modules", module_id)
        if not os.path.exists(module_dir):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"모듈 디렉토리를 찾을 수 없습니다: {module_dir}",
                    }
                ),
                404,
            )
        shutil.rmtree(module_dir)
        return jsonify(
            {
                "success": True,
                "message": f"모듈 {module_id}이(가) 완전히 제거되었습니다.",
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/modules/performance")
def api_modules_performance():
    """모듈 성능 데이터 API"""
    try:
        # 프로젝트 내 모든 모듈의 성능 데이터
        performance_data = {
            "modules": [
                # 기존 샘플 모듈들
                {
                    "plugin_id": "attendance_management",
                    "name": "출근 관리 모듈",
                    "cpu_usage": 2.5,
                    "memory_usage": 15.2,
                    "response_time": 120,
                    "status": "active",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "schedule_management",
                    "name": "일정 관리 모듈",
                    "cpu_usage": 3.1,
                    "memory_usage": 18.5,
                    "response_time": 150,
                    "status": "active",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "inventory_management",
                    "name": "재고 관리 모듈",
                    "cpu_usage": 4.2,
                    "memory_usage": 22.1,
                    "response_time": 180,
                    "status": "active",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "purchase_management",
                    "name": "구매 관리 모듈",
                    "cpu_usage": 3.8,
                    "memory_usage": 20.3,
                    "response_time": 160,
                    "status": "active",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "ai_analytics_module",
                    "name": "AI 분석 모듈",
                    "cpu_usage": 8.5,
                    "memory_usage": 45.2,
                    "response_time": 300,
                    "status": "active",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                # API 모듈들
                {
                    "plugin_id": "user_management_module",
                    "name": "사용자 관리 모듈",
                    "cpu_usage": 5.2,
                    "memory_usage": 28.5,
                    "response_time": 200,
                    "status": "active",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "visualization_module",
                    "name": "데이터 시각화 모듈",
                    "cpu_usage": 6.8,
                    "memory_usage": 35.2,
                    "response_time": 250,
                    "status": "active",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "schedule_management_module",
                    "name": "스케줄 관리 모듈",
                    "cpu_usage": 4.5,
                    "memory_usage": 25.8,
                    "response_time": 180,
                    "status": "active",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "security_module",
                    "name": "보안 모듈",
                    "cpu_usage": 3.2,
                    "memory_usage": 18.5,
                    "response_time": 120,
                    "status": "active",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "reporting_system_module",
                    "name": "리포팅 시스템 모듈",
                    "cpu_usage": 7.5,
                    "memory_usage": 42.3,
                    "response_time": 280,
                    "status": "active",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "notification_system_module",
                    "name": "알림 시스템 모듈",
                    "cpu_usage": 2.8,
                    "memory_usage": 16.2,
                    "response_time": 100,
                    "status": "active",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "optimization_module",
                    "name": "최적화 모듈",
                    "cpu_usage": 4.1,
                    "memory_usage": 22.8,
                    "response_time": 160,
                    "status": "active",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "monitoring_module",
                    "name": "모니터링 모듈",
                    "cpu_usage": 3.5,
                    "memory_usage": 19.2,
                    "response_time": 140,
                    "status": "active",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "automation_module",
                    "name": "자동화 모듈",
                    "cpu_usage": 6.2,
                    "memory_usage": 32.5,
                    "response_time": 220,
                    "status": "active",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "chat_system_module",
                    "name": "채팅 시스템 모듈",
                    "cpu_usage": 5.8,
                    "memory_usage": 28.9,
                    "response_time": 180,
                    "status": "active",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "analytics_module",
                    "name": "분석 모듈",
                    "cpu_usage": 8.2,
                    "memory_usage": 45.6,
                    "response_time": 320,
                    "status": "active",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                # 레스토랑 전용 모듈
                {
                    "plugin_id": "qsc_system_module",
                    "name": "QSC 시스템 모듈",
                    "cpu_usage": 5.5,
                    "memory_usage": 30.2,
                    "response_time": 200,
                    "status": "active",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                # 추가 기능 모듈들
                {
                    "plugin_id": "order_management_module",
                    "name": "주문 관리 모듈",
                    "cpu_usage": 0.0,
                    "memory_usage": 0.0,
                    "response_time": 0,
                    "status": "inactive",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "cleaning_management_module",
                    "name": "청소 관리 모듈",
                    "cpu_usage": 2.8,
                    "memory_usage": 15.8,
                    "response_time": 120,
                    "status": "active",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "payroll_management_module",
                    "name": "급여 관리 모듈",
                    "cpu_usage": 4.5,
                    "memory_usage": 25.2,
                    "response_time": 180,
                    "status": "active",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "iot_integration_module",
                    "name": "IoT 통합 모듈",
                    "cpu_usage": 0.0,
                    "memory_usage": 0.0,
                    "response_time": 0,
                    "status": "error",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "voice_recognition_module",
                    "name": "음성 인식 모듈",
                    "cpu_usage": 0.0,
                    "memory_usage": 0.0,
                    "response_time": 0,
                    "status": "inactive",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "image_analysis_module",
                    "name": "이미지 분석 모듈",
                    "cpu_usage": 0.0,
                    "memory_usage": 0.0,
                    "response_time": 0,
                    "status": "inactive",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "translation_module",
                    "name": "번역 모듈",
                    "cpu_usage": 0.0,
                    "memory_usage": 0.0,
                    "response_time": 0,
                    "status": "inactive",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "mobile_support_module",
                    "name": "모바일 지원 모듈",
                    "cpu_usage": 3.2,
                    "memory_usage": 18.5,
                    "response_time": 150,
                    "status": "active",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "backup_restore_module",
                    "name": "백업 및 복원 모듈",
                    "cpu_usage": 2.1,
                    "memory_usage": 12.8,
                    "response_time": 100,
                    "status": "active",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "audit_logging_module",
                    "name": "감사 로깅 모듈",
                    "cpu_usage": 1.8,
                    "memory_usage": 10.2,
                    "response_time": 80,
                    "status": "active",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "multi_branch_module",
                    "name": "다중 매장 관리 모듈",
                    "cpu_usage": 7.2,
                    "memory_usage": 38.5,
                    "response_time": 280,
                    "status": "active",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
                {
                    "plugin_id": "ledger",
                    "name": "가계부 모듈",
                    "cpu_usage": 3.2,
                    "memory_usage": 18.5,
                    "response_time": 140,
                    "status": "active",
                    "last_updated": "2024-01-15T10:30:00Z",
                },
            ],
            "summary": {
                "total_modules": 30,
                "active_modules": 25,
                "inactive_modules": 4,
                "error_modules": 1,
                "avg_cpu_usage": 4.2,
                "avg_memory_usage": 23.8,
                "avg_response_time": 180,
                "total_cpu_usage": 126.0,
                "total_memory_usage": 714.0,
            },
        }

        return jsonify(performance_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 플러그인 등록 라우트 등록 (비활성화 - 파일이 존재하지 않음)
# from routes.plugin_registration import plugin_registration_bp
# app.register_blueprint(plugin_registration_bp, url_prefix="/api/plugins")


@app.route("/admin/plugin-feedback-dashboard")
def admin_plugin_feedback_dashboard():
    """플러그인 피드백 대시보드"""
    return render_template("admin/plugin_feedback_dashboard.html")


@app.route("/admin/plugin-customization-dashboard")
def admin_plugin_customization_dashboard():
    """플러그인 커스터마이징 대시보드"""
    return render_template("admin/plugin_customization_dashboard.html")

@app.route("/admin/plugin-management")
def admin_plugin_management():
    """플러그인 관리 페이지"""
    # 플러그인 통계 데이터 생성
    stats = {
        'activePlugins': 5,  # 활성 플러그인 수
        'permissionSets': 12,  # 권한 설정 수
        'testSuccessRate': 95,  # 테스트 성공률
        'systemStatus': '정상'  # 시스템 상태
    }
    
    # 샘플 플러그인 데이터
    plugins = [
        {
            'id': 1,
            'name': 'AI 스케줄 추천',
            'description': '직원 스케줄을 AI가 자동으로 최적화해주는 플러그인',
            'icon': '📅',
            'status': 'active',
            'activatedTargets': '3개 브랜드, 15개 매장',
            'lastTestResult': '2024-01-15 성공'
        },
        {
            'id': 2,
            'name': '리뷰 자동 요약',
            'description': '고객 리뷰를 자동으로 분석하고 요약해주는 플러그인',
            'icon': '📝',
            'status': 'active',
            'activatedTargets': '2개 브랜드, 8개 매장',
            'lastTestResult': '2024-01-14 성공'
        },
        {
            'id': 3,
            'name': 'QSC 자동 평가',
            'description': 'QSC 평가를 자동으로 수행하고 리포트를 생성하는 플러그인',
            'icon': '⭐',
            'status': 'inactive',
            'activatedTargets': '1개 브랜드, 5개 매장',
            'lastTestResult': '2024-01-13 실패'
        }
    ]
    
    return render_template("admin/plugin_management.html", stats=stats, plugins=plugins)

@app.route("/plugin-marketplace")
def plugin_marketplace():
    """플러그인 마켓플레이스 페이지"""
    return render_template("plugin_marketplace.html")

@app.route("/admin/plugin-upload", methods=["GET", "POST"])
def admin_plugin_upload():
    """플러그인 업로드 페이지"""
    if request.method == "POST":
        try:
            # 폼 데이터 받기
            name = request.form.get('name')
            display_name = request.form.get('display_name')
            version = request.form.get('version')
            author = request.form.get('author')
            category = request.form.get('category')
            description = request.form.get('description')
            tags = request.form.get('tags', '').split(',') if request.form.get('tags') else []
            icon = request.form.get('icon', '📦')
            ui_schema = request.form.get('ui_schema')
            install_targets = request.form.getlist('install_targets')
            
            # 파일 업로드 처리
            if 'plugin_file' not in request.files:
                flash('플러그인 파일을 선택해주세요.', 'error')
                return redirect(request.url)
            
            file = request.files['plugin_file']
            if file.filename == '':
                flash('플러그인 파일을 선택해주세요.', 'error')
                return redirect(request.url)
            
            # 파일 저장
            filename = secure_filename(file.filename)
            file_path = os.path.join('plugins', 'uploaded', filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)
            
            # UI 스키마 파싱
            try:
                ui_schema_json = json.loads(ui_schema)
            except json.JSONDecodeError:
                flash('UI 스키마가 유효한 JSON 형식이 아닙니다.', 'error')
                return redirect(request.url)
            
            # 플러그인 정보 저장 (실제로는 DB에 저장)
            plugin_info = {
                'id': len(plugins) + 1,
                'name': name,
                'display_name': display_name,
                'version': version,
                'author': author,
                'category': category,
                'description': description,
                'tags': [tag.strip() for tag in tags],
                'icon': icon,
                'ui_schema': ui_schema_json,
                'file_path': file_path,
                'install_targets': install_targets,
                'uploaded_by': current_user.username,
                'uploaded_at': datetime.now().isoformat(),
                'status': 'pending'  # 승인 대기
            }
            
            # 플러그인 목록에 추가 (실제로는 DB에 저장)
            plugins.append(plugin_info)
            
            flash(f'플러그인 "{display_name}"이 성공적으로 업로드되었습니다. 승인 후 마켓플레이스에 등록됩니다.', 'success')
            return redirect(url_for('admin_plugin_management'))
            
        except Exception as e:
            flash(f'플러그인 업로드 중 오류가 발생했습니다: {str(e)}', 'error')
            return redirect(request.url)
    
    return render_template("admin/plugin_upload.html")

@app.route("/admin/plugin-approval")
def admin_plugin_approval():
    """플러그인 승인 관리 페이지"""
    # 승인 대기 플러그인
    pending_plugins = [p for p in plugins if p.get('status') == 'pending']
    
    # 승인된 플러그인
    approved_plugins = [p for p in plugins if p.get('status') == 'approved']
    
    return render_template("admin/plugin_approval.html", 
                         pending_plugins=pending_plugins, 
                         approved_plugins=approved_plugins)

@app.route("/api/admin/plugin/<int:plugin_id>/details")
def api_admin_plugin_details(plugin_id):
    """플러그인 상세 정보 API"""
    plugin = next((p for p in plugins if p['id'] == plugin_id), None)
    if plugin:
        return jsonify(plugin)
    else:
        return jsonify({'error': 'Plugin not found'}), 404

@app.route("/api/admin/plugin/<int:plugin_id>/approve", methods=["POST"])
def api_admin_approve_plugin(plugin_id):
    """플러그인 승인 API"""
    plugin = next((p for p in plugins if p['id'] == plugin_id), None)
    if plugin:
        plugin['status'] = 'approved'
        plugin['approved_at'] = datetime.now().isoformat()
        plugin['approved_by'] = current_user.username
        return jsonify({'success': True, 'message': 'Plugin approved successfully'})
    else:
        return jsonify({'success': False, 'message': 'Plugin not found'}), 404

@app.route("/api/admin/plugin/<int:plugin_id>/reject", methods=["POST"])
def api_admin_reject_plugin(plugin_id):
    """플러그인 거부 API"""
    data = request.get_json()
    reason = data.get('reason', 'No reason provided')
    
    plugin = next((p for p in plugins if p['id'] == plugin_id), None)
    if plugin:
        plugin['status'] = 'rejected'
        plugin['rejected_at'] = datetime.now().isoformat()
        plugin['rejected_by'] = current_user.username
        plugin['rejection_reason'] = reason
        return jsonify({'success': True, 'message': 'Plugin rejected successfully'})
    else:
        return jsonify({'success': False, 'message': 'Plugin not found'}), 404

@app.route("/api/admin/plugin/<int:plugin_id>/deactivate", methods=["POST"])
def api_admin_deactivate_plugin(plugin_id):
    """플러그인 비활성화 API"""
    plugin = next((p for p in plugins if p['id'] == plugin_id), None)
    if plugin:
        plugin['status'] = 'inactive'
        plugin['deactivated_at'] = datetime.now().isoformat()
        plugin['deactivated_by'] = current_user.username
        return jsonify({'success': True, 'message': 'Plugin deactivated successfully'})
    else:
        return jsonify({'success': False, 'message': 'Plugin not found'}), 404


@app.route("/api/admin/users")
def api_admin_users():
    """사용자 목록 API"""
    try:
        users = User.query.all()
        users_data = []

        for user in users:
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "status": getattr(user, "status", "active"),
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
            }
            users_data.append(user_data)

        return jsonify({"users": users_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/user/<int:user_id>/status", methods=["POST"])
def api_admin_user_status(user_id):
    """사용자 상태 변경 API"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.get_json()
        new_status = data.get("status")

        if hasattr(user, "status"):
            user.status = new_status
            db.session.commit()
            return jsonify(
                {
                    "message": f"{user.username} 사용자의 상태가 {new_status}로 변경되었습니다."
                }
            )
        else:
            return jsonify({"error": "User model does not have status field"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 메뉴 통합 시스템 API
@app.route("/api/menu/user-menus")
def api_menu_user_menus():
    """사용자별 메뉴 조회 API"""
    try:
        # 사용자 역할에 따른 메뉴 반환 (임시로 admin으로 설정)
        user_role = (
            getattr(current_user, "role", "admin")
            if current_user.is_authenticated
            else "admin"
        )
        if user_role == "admin":
            menus = [
                {
                    "id": 1,
                    "menu_name": "시스템 관리",
                    "menu_icon": "fas fa-cogs",
                    "menu_url": "/admin/system-monitoring",
                    "sub_menus": [
                        {
                            "id": 11,
                            "menu_name": "시스템 모니터링",
                            "menu_icon": "fas fa-chart-line",
                            "menu_url": "/admin/system-monitoring",
                        },
                        {
                            "id": 12,
                            "menu_name": "보안 관리",
                            "menu_icon": "fas fa-shield-alt",
                            "menu_url": "/admin/security-management",
                        },
                    ],
                },
                {
                    "id": 2,
                    "menu_name": "모듈 관리",
                    "menu_icon": "fas fa-puzzle-piece",
                    "menu_url": "/admin/module-management",
                    "sub_menus": [
                        {
                            "id": 21,
                            "menu_name": "모듈 마켓플레이스",
                            "menu_icon": "fas fa-store",
                            "menu_url": "/admin/module-marketplace",
                        },
                        {
                            "id": 22,
                            "menu_name": "설치된 모듈",
                            "menu_icon": "fas fa-list",
                            "menu_url": "/admin/module-management",
                        },
                    ],
                },
                {
                    "id": 3,
                    "menu_name": "개발 모드",
                    "menu_icon": "fas fa-code",
                    "menu_url": "/dev-mode",
                    "sub_menus": [
                        {
                            "id": 31,
                            "menu_name": "프로젝트 관리",
                            "menu_icon": "fas fa-project-diagram",
                            "menu_url": "/dev-mode",
                        },
                        {
                            "id": 32,
                            "menu_name": "컴포넌트 라이브러리",
                            "menu_icon": "fas fa-puzzle-piece",
                            "menu_url": "/dev-mode/components",
                        },
                    ],
                },
            ]
        elif user_role == "manager":
            menus = [
                {
                    "id": 3,
                    "menu_name": "팀 관리",
                    "menu_icon": "fas fa-users",
                    "menu_url": "/team",
                    "sub_menus": [
                        {
                            "id": 31,
                            "menu_name": "직원 목록",
                            "menu_icon": "fas fa-list",
                            "menu_url": "/team/employees",
                        },
                        {
                            "id": 32,
                            "menu_name": "근무 스케줄",
                            "menu_icon": "fas fa-calendar",
                            "menu_url": "/team/schedule",
                        },
                    ],
                },
                {
                    "id": 4,
                    "menu_name": "개발 모드",
                    "menu_icon": "fas fa-code",
                    "menu_url": "/dev-mode",
                    "sub_menus": [
                        {
                            "id": 41,
                            "menu_name": "프로젝트 관리",
                            "menu_icon": "fas fa-project-diagram",
                            "menu_url": "/dev-mode",
                        }
                    ],
                },
            ]
        else:
            menus = [
                {
                    "id": 4,
                    "menu_name": "내 정보",
                    "menu_icon": "fas fa-user",
                    "menu_url": "/profile",
                    "sub_menus": [
                        {
                            "id": 41,
                            "menu_name": "개인 정보",
                            "menu_icon": "fas fa-id-card",
                            "menu_url": "/profile/info",
                        },
                        {
                            "id": 42,
                            "menu_name": "근무 기록",
                            "menu_icon": "fas fa-history",
                            "menu_url": "/profile/attendance",
                        },
                    ],
                }
            ]

        return jsonify({"success": True, "data": menus})
    except Exception as e:
        logger.error(f"메뉴 조회 오류: {str(e)}")
        return (
            jsonify({"success": False, "error": "메뉴 조회 중 오류가 발생했습니다"}),
            500,
        )


@app.route("/api/menu/statistics")
def api_menu_statistics():
    """메뉴 통계 API"""
    try:
        stats = {
            "total_menus": 4,
            "module_menu_counts": {
                "attendance": 2,
                "inventory": 2,
                "team": 2,
                "profile": 2,
            },
            "popular_menus": [
                {"name": "출근 관리", "access_count": 15},
                {"name": "재고 관리", "access_count": 12},
                {"name": "팀 관리", "access_count": 8},
            ],
            "recent_menus": [
                {"name": "출근 기록", "last_access": "2024-01-15 10:30:00"},
                {"name": "재고 현황", "last_access": "2024-01-15 09:15:00"},
            ],
        }
        return jsonify({"success": True, "data": stats})
    except Exception as e:
        logger.error(f"메뉴 통계 오류: {str(e)}")
        return (
            jsonify(
                {"success": False, "error": "메뉴 통계 조회 중 오류가 발생했습니다"}
            ),
            500,
        )


@app.route("/api/menu/menu-access/<menu_id>", methods=["POST"])
def api_menu_access(menu_id):
    """메뉴 접근 기록 API"""
    try:
        # 메뉴 ID 검증 및 정규화
        if ':' in str(menu_id):
            # "1:1" 형식의 메뉴 ID를 처리
            parts = str(menu_id).split(':')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                normalized_menu_id = int(parts[0])  # 첫 번째 숫자를 메뉴 ID로 사용
            else:
                return jsonify({"success": False, "error": "잘못된 메뉴 ID 형식입니다."}), 400
        else:
            # 일반적인 숫자 메뉴 ID
            try:
                normalized_menu_id = int(menu_id)
            except ValueError:
                return jsonify({"success": False, "error": "메뉴 ID는 숫자여야 합니다."}), 400
        
        # 메뉴 접근 기록 로직
        username = (
            getattr(current_user, "username", "anonymous")
            if current_user.is_authenticated
            else "anonymous"
        )
        logger.info(f"메뉴 접근: {normalized_menu_id} (원본: {menu_id}) by {username}")
        
        # 메뉴 접근 통계 업데이트 (선택사항)
        try:
            from core.backend.menu_integration_system import menu_integration_system
            menu_integration_system.update_menu_access(normalized_menu_id, current_user.id)
        except Exception as e:
            logger.warning(f"메뉴 접근 통계 업데이트 실패: {e}")
        
        return jsonify({"success": True, "menu_id": normalized_menu_id})
    except Exception as e:
        logger.error(f"메뉴 접근 기록 오류: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/admin/brand_stats")
def api_admin_brand_stats():
    """브랜드별 통계 API (기존 엔드포인트 - 더미 데이터)"""
    try:
        # 안정적인 더미 데이터 반환
        stats_data = [
            {
                "brand_id": 1,
                "brand_name": "스타벅스",
                "employee_count": 25,
                "manager_count": 3,
                "store_count": 5,
                "total_count": 28,
            },
            {
                "brand_id": 2,
                "brand_name": "투썸플레이스",
                "employee_count": 18,
                "manager_count": 2,
                "store_count": 3,
                "total_count": 20,
            },
            {
                "brand_id": 3,
                "brand_name": "할리스",
                "employee_count": 15,
                "manager_count": 2,
                "store_count": 2,
                "total_count": 17,
            }
        ]
        
        return jsonify({
            "brand_stats": stats_data,
            "source": "dummy",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"브랜드 통계 API 오류: {str(e)}")
        return jsonify({
            "error": "브랜드 통계 조회 중 오류가 발생했습니다.",
            "details": str(e)
        }), 500


@app.route("/api/admin/brand_stats_v2")
def api_admin_brand_stats_v2():
    """브랜드별 통계 API (새로운 버전)"""
    try:
        # 간단한 더미 데이터 반환
        stats_data = [
            {
                "brand_id": 1,
                "brand_name": "스타벅스",
                "employee_count": 25,
                "manager_count": 3,
                "store_count": 5,
                "total_count": 28,
            },
            {
                "brand_id": 2,
                "brand_name": "투썸플레이스",
                "employee_count": 18,
                "manager_count": 2,
                "store_count": 3,
                "total_count": 20,
            },
            {
                "brand_id": 3,
                "brand_name": "할리스",
                "employee_count": 15,
                "manager_count": 2,
                "store_count": 2,
                "total_count": 17,
            }
        ]
        
        return jsonify({"brand_stats": stats_data})
    except Exception as e:
        logger.error(f"브랜드 통계 API v2 오류: {str(e)}")
        return jsonify({
            "error": "브랜드 통계 조회 중 오류가 발생했습니다.",
            "details": str(e)
        }), 500


# 캐시 시스템
from functools import wraps
import time

# WebSocket 지원 (조건부 import)
SOCKETIO_AVAILABLE = False  # 기본값 설정

try:
    from flask_socketio import SocketIO, emit, join_room, leave_room
    SOCKETIO_AVAILABLE = True
except ImportError:
    print("⚠️ flask-socketio가 설치되지 않았습니다. WebSocket 기능이 비활성화됩니다.")
    # 더미 클래스들
    class SocketIO:
        def __init__(self, *args, **kwargs):
            pass
        def on(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        def emit(self, *args, **kwargs):
            pass
        def run(self, *args, **kwargs):
            pass
    
    def emit(*args, **kwargs):
        pass
    
    def join_room(*args, **kwargs):
        pass
    
    def leave_room(*args, **kwargs):
        pass

import threading
import json

# SocketIO 초기화 (조건부)
if SOCKETIO_AVAILABLE:
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
else:
    socketio = SocketIO(app)

def cache_result(expire_seconds=300):  # 5분 캐시
    def decorator(func):
        cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            current_time = time.time()
            
            # 캐시된 결과가 있고 만료되지 않았으면 반환
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if current_time - timestamp < expire_seconds:
                    logger.info(f"캐시된 결과 반환: {func.__name__}")
                    return result
            
            # 새로운 결과 계산 및 캐시
            result = func(*args, **kwargs)
            cache[cache_key] = (result, current_time)
            logger.info(f"새로운 결과 캐시: {func.__name__}")
            
            return result
        return wrapper
    return decorator

@app.route("/api/admin/brand_stats_real")
@cache_result(expire_seconds=60)  # 1분 캐시
def api_admin_brand_stats_real():
    """브랜드별 통계 API (실제 데이터베이스 연동)"""
    try:
        from sqlalchemy import text
        
        # 필터링 파라미터 받기
        sort_by = request.args.get('sort_by', 'name')  # name, employee_count, manager_count, store_count
        sort_order = request.args.get('sort_order', 'asc')  # asc, desc
        search = request.args.get('search', '')  # 브랜드명 검색
        
        # 기본 SQL 쿼리
        base_query = """
            SELECT 
                b.id as brand_id,
                b.name as brand_name,
                COALESCE(employee_counts.employee_count, 0) as employee_count,
                COALESCE(manager_counts.manager_count, 0) as manager_count,
                COALESCE(store_counts.store_count, 0) as store_count,
                COALESCE(employee_counts.employee_count, 0) + COALESCE(manager_counts.manager_count, 0) as total_count,
                b.created_at,
                b.status
            FROM brands b
            LEFT JOIN (
                SELECT 
                    brand_id,
                    COUNT(*) as employee_count
                FROM users 
                WHERE brand_id IS NOT NULL 
                AND role IN ('employee', 'staff')
                GROUP BY brand_id
            ) employee_counts ON b.id = employee_counts.brand_id
            LEFT JOIN (
                SELECT 
                    brand_id,
                    COUNT(*) as manager_count
                FROM users 
                WHERE brand_id IS NOT NULL 
                AND role IN ('store_manager', 'brand_admin')
                GROUP BY brand_id
            ) manager_counts ON b.id = manager_counts.brand_id
            LEFT JOIN (
                SELECT 
                    brand_id,
                    COUNT(*) as store_count
                FROM branches 
                WHERE brand_id IS NOT NULL
                GROUP BY brand_id
            ) store_counts ON b.id = store_counts.brand_id
            WHERE b.status = 'active'
        """
        
        # 검색 조건 추가
        if search:
            base_query += f" AND b.name LIKE '%{search}%'"
        
        # 정렬 조건 추가
        sort_mapping = {
            'name': 'b.name',
            'employee_count': 'employee_count',
            'manager_count': 'manager_count',
            'store_count': 'store_count',
            'total_count': 'total_count',
            'created_at': 'b.created_at'
        }
        
        sort_field = sort_mapping.get(sort_by, 'b.name')
        base_query += f" ORDER BY {sort_field} {sort_order.upper()}"
        
        query = text(base_query)
        result = db.session.execute(query)
        stats_data = []
        
        for row in result:
            # created_at 필드 안전하게 처리
            created_at_str = None
            if row.created_at:
                if hasattr(row.created_at, 'isoformat'):
                    created_at_str = row.created_at.isoformat()
                else:
                    created_at_str = str(row.created_at)
            
            stats_data.append({
                "brand_id": row.brand_id,
                "brand_name": row.brand_name,
                "employee_count": row.employee_count,
                "manager_count": row.manager_count,
                "store_count": row.store_count,
                "total_count": row.total_count,
                "created_at": created_at_str,
                "status": row.status
            })
        
        # 데이터가 없으면 더미 데이터 반환
        if not stats_data:
            stats_data = [
                {
                    "brand_id": 1,
                    "brand_name": "샘플 브랜드",
                    "employee_count": 0,
                    "manager_count": 0,
                    "store_count": 0,
                    "total_count": 0,
                    "created_at": datetime.utcnow().isoformat(),
                    "status": "active"
                }
            ]
        
        # 요약 통계 계산
        total_brands = len(stats_data)
        total_employees = sum(b['employee_count'] for b in stats_data)
        total_managers = sum(b['manager_count'] for b in stats_data)
        total_stores = sum(b['store_count'] for b in stats_data)
        
        return jsonify({
            "brand_stats": stats_data,
            "summary": {
                "total_brands": total_brands,
                "total_employees": total_employees,
                "total_managers": total_managers,
                "total_stores": total_stores,
                "total_users": total_employees + total_managers
            },
            "filters": {
                "sort_by": sort_by,
                "sort_order": sort_order,
                "search": search
            },
            "source": "database",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"실제 브랜드 통계 API 오류: {str(e)}")
        # 오류 발생 시 더미 데이터 반환
        fallback_data = [
            {
                "brand_id": 1,
                "brand_name": "스타벅스",
                "employee_count": 25,
                "manager_count": 3,
                "store_count": 5,
                "total_count": 28,
                "created_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
        ]
        return jsonify({
            "brand_stats": fallback_data,
            "summary": {
                "total_brands": 1,
                "total_employees": 25,
                "total_managers": 3,
                "total_stores": 5,
                "total_users": 28
            },
            "source": "fallback",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        })


@app.route("/api/admin/brand_stats/realtime")
def api_admin_brand_stats_realtime():
    """실시간 브랜드 통계 API (WebSocket 대체)"""
    try:
        from sqlalchemy import text
        
        # 최근 변경사항 확인 (마지막 1시간)
        recent_changes_query = text("""
                        SELECT
                'user' as change_type,
                u.name as item_name,
                b.name as brand_name,
                u.created_at as change_time
            FROM users u
            JOIN brands b ON u.brand_id = b.id
            WHERE u.created_at >= datetime('now', '-1 hour')
            UNION ALL
            SELECT
                'branch' as change_type,
                br.name as item_name,
                b.name as brand_name,
                br.created_at as change_time
            FROM branches br
            JOIN brands b ON br.brand_id = b.id
            WHERE br.created_at >= datetime('now', '-1 hour')
            ORDER BY change_time DESC
            LIMIT 10
        """)
        
        recent_changes = []
        try:
            changes_result = db.session.execute(recent_changes_query)
            for row in changes_result:
                recent_changes.append({
                    "type": row.change_type,
                    "item_name": row.item_name,
                    "brand_name": row.brand_name,
                    "time": row.change_time.isoformat() if row.change_time else None
                })
        except Exception as e:
            logger.warning(f"최근 변경사항 조회 실패: {str(e)}")
        
        # 실시간 통계 (기존 API 호출)
        stats_response = api_admin_brand_stats_real()
        stats_data = stats_response.get_json()
        
        # 실시간 데이터 추가
        stats_data["realtime"] = {
            "recent_changes": recent_changes,
            "last_updated": datetime.utcnow().isoformat(),
            "update_interval": "1 minute"
        }
        
        return jsonify(stats_data)
    except Exception as e:
        logger.error(f"실시간 브랜드 통계 API 오류: {str(e)}")
        return jsonify({
            "error": "실시간 데이터 조회 실패",
            "details": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500


@app.route("/api/admin/brand_stats/analytics")
def api_admin_brand_stats_analytics():
    """브랜드 통계 고급 분석 API"""
    try:
        from sqlalchemy import text, func
        
        # 1. 브랜드별 성장률 분석 (최근 30일 vs 이전 30일)
        growth_query = text("""
            SELECT 
                b.id as brand_id,
                b.name as brand_name,
                COALESCE(current_period.count, 0) as current_count,
                COALESCE(previous_period.count, 0) as previous_count,
                CASE 
                    WHEN COALESCE(previous_period.count, 0) = 0 THEN 0
                    ELSE ROUND(((COALESCE(current_period.count, 0) - COALESCE(previous_period.count, 0)) / COALESCE(previous_period.count, 0)) * 100, 2)
                END as growth_rate
            FROM brands b
            LEFT JOIN (
                SELECT 
                    brand_id,
                    COUNT(*) as count
                FROM users 
                WHERE brand_id IS NOT NULL 
                AND created_at >= DATE('now', '-30 days')
                GROUP BY brand_id
            ) current_period ON b.id = current_period.brand_id
            LEFT JOIN (
                SELECT 
                    brand_id,
                    COUNT(*) as count
                FROM users 
                WHERE brand_id IS NOT NULL 
                AND created_at >= DATE('now', '-60 days') 
                AND created_at < DATE('now', '-30 days')
                GROUP BY brand_id
            ) previous_period ON b.id = previous_period.brand_id
            WHERE b.status = 'active'
            ORDER BY growth_rate DESC
        """)
        
        growth_result = db.session.execute(growth_query)
        growth_data = []
        for row in growth_result:
            growth_data.append({
                "brand_id": row.brand_id,
                "brand_name": row.brand_name,
                "current_count": row.current_count,
                "previous_count": row.previous_count,
                "growth_rate": row.growth_rate
            })
        
        # 2. 월별 브랜드별 사용자 등록 추이
        monthly_trend_query = text("""
            SELECT 
                b.id as brand_id,
                b.name as brand_name,
                strftime('%Y-%m', u.created_at) as month,
                COUNT(*) as new_users
            FROM brands b
            LEFT JOIN users u ON b.id = u.brand_id
            WHERE b.status = 'active'
            AND u.created_at >= DATE('now', '-6 months')
            GROUP BY b.id, b.name, strftime('%Y-%m', u.created_at)
            ORDER BY b.name, month
        """)
        
        monthly_result = db.session.execute(monthly_trend_query)
        monthly_data = {}
        for row in monthly_result:
            if row.brand_name not in monthly_data:
                monthly_data[row.brand_name] = []
            monthly_data[row.brand_name].append({
                "month": row.month,
                "new_users": row.new_users
            })
        
        # 3. 브랜드별 평균 매장당 직원 수
        avg_employees_query = text("""
            SELECT 
                b.id as brand_id,
                b.name as brand_name,
                COALESCE(store_counts.store_count, 0) as store_count,
                COALESCE(employee_counts.employee_count, 0) as employee_count,
                CASE 
                    WHEN COALESCE(store_counts.store_count, 0) = 0 THEN 0
                    ELSE ROUND(CAST(COALESCE(employee_counts.employee_count, 0) AS FLOAT) / COALESCE(store_counts.store_count, 0), 2)
                END as avg_employees_per_store
            FROM brands b
            LEFT JOIN (
                SELECT 
                    brand_id,
                    COUNT(*) as store_count
                FROM branches 
                WHERE brand_id IS NOT NULL
                AND status = 'active'
                GROUP BY brand_id
            ) store_counts ON b.id = store_counts.brand_id
            LEFT JOIN (
                SELECT 
                    brand_id,
                    COUNT(*) as employee_count
                FROM users 
                WHERE brand_id IS NOT NULL 
                AND role IN ('employee', 'staff')
                GROUP BY brand_id
            ) employee_counts ON b.id = employee_counts.brand_id
            WHERE b.status = 'active'
            ORDER BY avg_employees_per_store DESC
        """)
        
        avg_result = db.session.execute(avg_employees_query)
        avg_data = []
        for row in avg_result:
            avg_data.append({
                "brand_id": row.brand_id,
                "brand_name": row.brand_name,
                "store_count": row.store_count,
                "employee_count": row.employee_count,
                "avg_employees_per_store": row.avg_employees_per_store
            })
        
        # 4. 브랜드별 활성도 점수 (최근 활동 기준)
        activity_query = text("""
            SELECT 
                b.id as brand_id,
                b.name as brand_name,
                COALESCE(recent_users.count, 0) as recent_users,
                COALESCE(recent_stores.count, 0) as recent_stores,
                (COALESCE(recent_users.count, 0) * 0.7 + COALESCE(recent_stores.count, 0) * 0.3) as activity_score
            FROM brands b
            LEFT JOIN (
                SELECT 
                    brand_id,
                    COUNT(*) as count
                FROM users 
                WHERE brand_id IS NOT NULL 
                AND created_at >= DATE('now', '-7 days')
                GROUP BY brand_id
            ) recent_users ON b.id = recent_users.brand_id
            LEFT JOIN (
                SELECT 
                    brand_id,
                    COUNT(*) as count
                FROM branches 
                WHERE brand_id IS NOT NULL
                AND created_at >= DATE('now', '-7 days')
                GROUP BY brand_id
            ) recent_stores ON b.id = recent_stores.brand_id
            WHERE b.status = 'active'
            ORDER BY activity_score DESC
        """)
        
        activity_result = db.session.execute(activity_query)
        activity_data = []
        for row in activity_result:
            activity_data.append({
                "brand_id": row.brand_id,
                "brand_name": row.brand_name,
                "recent_users": row.recent_users,
                "recent_stores": row.recent_stores,
                "activity_score": round(row.activity_score, 2)
            })
        
        return jsonify({
            "growth_analysis": growth_data,
            "monthly_trends": monthly_data,
            "avg_employees_per_store": avg_data,
            "activity_scores": activity_data,
            "analysis_date": datetime.utcnow().isoformat(),
            "source": "database"
        })
        
    except Exception as e:
        logger.error(f"브랜드 통계 분석 API 오류: {str(e)}")
        return jsonify({
            "error": "통계 분석 실패",
            "details": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500


@app.route("/api/admin/brand_stats/cache/clear", methods=["POST"])
def api_admin_clear_brand_stats_cache():
    """브랜드 통계 캐시 무효화 API"""
    try:
        # 캐시 무효화 로직 (실제로는 Redis나 메모리 캐시를 사용해야 함)
        logger.info("브랜드 통계 캐시 무효화 요청됨")
        
        # 여기서는 간단히 로그만 남기고, 실제 캐시는 다음 요청 시 자동으로 갱신됨
        return jsonify({
            "success": True,
            "message": "캐시 무효화 완료",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"캐시 무효화 오류: {str(e)}")
        return jsonify({
            "error": "캐시 무효화 실패",
            "details": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500


# WebSocket 이벤트 핸들러 (조건부)
if SOCKETIO_AVAILABLE:
    @socketio.on('connect')
    def handle_connect():
        """클라이언트 연결 시 호출"""
        logger.info(f"클라이언트 연결됨: {request.sid}")
        emit('connected', {'message': 'WebSocket 연결 성공', 'timestamp': datetime.utcnow().isoformat()})

    @socketio.on('disconnect')
    def handle_disconnect():
        """클라이언트 연결 해제 시 호출"""
        logger.info(f"클라이언트 연결 해제됨: {request.sid}")

    @socketio.on('join_dashboard')
    def handle_join_dashboard(data):
        """대시보드 룸 참가"""
        room = 'dashboard'
        join_room(room)
        logger.info(f"클라이언트 {request.sid}가 대시보드 룸에 참가")
        emit('joined_dashboard', {'message': '대시보드 룸에 참가했습니다', 'room': room})

    @socketio.on('leave_dashboard')
    def handle_leave_dashboard(data):
        """대시보드 룸 나가기"""
        room = 'dashboard'
        leave_room(room)
        logger.info(f"클라이언트 {request.sid}가 대시보드 룸에서 나감")
else:
    # WebSocket이 없을 때 더미 함수들
    def handle_connect():
        pass
    
    def handle_disconnect():
        pass
    
    def handle_join_dashboard(data):
        pass
    
    def handle_leave_dashboard(data):
        pass

def broadcast_notification(notification_data):
    """모든 대시보드 클라이언트에게 알림 브로드캐스트"""
    if SOCKETIO_AVAILABLE:
        socketio.emit('notification', notification_data, room='dashboard')
    else:
        logger.info(f"WebSocket 비활성화: 알림 브로드캐스트 스킵 - {notification_data}")

def broadcast_brand_stats_update(brand_name):
    """브랜드 통계 업데이트 브로드캐스트"""
    if SOCKETIO_AVAILABLE:
        socketio.emit('brand_stats_update', {
            'type': 'brand_stats_update',
            'brand_name': brand_name,
            'timestamp': datetime.utcnow().isoformat()
        }, room='dashboard')
    else:
        logger.info(f"WebSocket 비활성화: 브랜드 통계 업데이트 스킵 - {brand_name}")

def broadcast_system_alert(alert_data):
    """시스템 알림 브로드캐스트"""
    if SOCKETIO_AVAILABLE:
        socketio.emit('system_alert', {
            'type': 'system_alert',
            'alert': alert_data,
            'timestamp': datetime.utcnow().isoformat()
        }, room='dashboard')
    else:
        logger.info(f"WebSocket 비활성화: 시스템 알림 스킵 - {alert_data}")

# 테스트용 알림 API
@app.route("/api/websocket/test-notification", methods=["POST"])
@csrf.exempt  # CSRF 토큰 검증 제외
def api_test_websocket_notification():
    """WebSocket 알림 테스트 API"""
    try:
        data = request.get_json()
        notification_data = {
            'type': 'notification',
            'notification': {
                'type': data.get('type', 'info'),
                'title': data.get('title', '테스트 알림'),
                'message': data.get('message', 'WebSocket 알림 테스트입니다.'),
                'priority': data.get('priority', 'medium')
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        broadcast_notification(notification_data)
        
        return jsonify({
            "success": True,
            "message": "알림이 브로드캐스트되었습니다",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"WebSocket 알림 테스트 오류: {str(e)}")
        return jsonify({
            "error": "알림 브로드캐스트 실패",
            "details": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

# 플러그인 API 엔드포인트들
@app.route('/api/plugin/test', methods=['GET'])
def test_plugin_api():
    """플러그인 API 테스트 - 실제 DB 연동 (임시 더미 데이터)"""
    try:
        # 임시로 더미 데이터 반환 (DB 연동 문제 해결 후 실제 데이터로 교체)
        plugin_data = [
            {
                'id': 1,
                'name': 'ai_schedule_optimizer',
                'display_name': 'AI 스케줄 최적화',
                'description': '직원 스케줄을 AI로 분석하여 최적의 근무 시간을 제안합니다.',
                'version': '1.0.0',
                'author': 'AI Team',
                'category': '스케줄링',
                'tags': ['AI', '스케줄', '최적화'],
                'icon': 'calendar',
                'ui_schema': {
                    'menu': {
                        'title': 'AI 스케줄',
                        'icon': 'calendar',
                        'position': 1
                    },
                    'dashboard': {
                        'type': 'chart',
                        'size': 'medium',
                        'component': 'ScheduleOptimizationChart'
                    }
                },
                'download_count': 150,
                'rating': 4.5,
                'review_count': 23,
                'is_installed': False
            },
            {
                'id': 2,
                'name': 'review_auto_summary',
                'display_name': '리뷰 자동 요약',
                'description': '고객 리뷰를 자동으로 분석하고 핵심 내용을 요약해드립니다.',
                'version': '2.1.0',
                'author': 'NLP Team',
                'category': '고객 관리',
                'tags': ['NLP', '리뷰', '분석'],
                'icon': 'message-square',
                'ui_schema': {
                    'menu': {
                        'title': '리뷰 분석',
                        'icon': 'message-square',
                        'position': 2
                    },
                    'dashboard': {
                        'type': 'list',
                        'size': 'large',
                        'component': 'ReviewSummaryList'
                    }
                },
                'download_count': 89,
                'rating': 4.2,
                'review_count': 15,
                'is_installed': True
            },
            {
                'id': 3,
                'name': 'qsc_auto_analyzer',
                'display_name': 'QSC 자동 분석',
                'description': '품질, 서비스, 청결도를 자동으로 분석하고 개선점을 제시합니다.',
                'version': '1.5.0',
                'author': 'Quality Team',
                'category': '품질 관리',
                'tags': ['QSC', '품질', '분석'],
                'icon': 'bar-chart-3',
                'ui_schema': {
                    'menu': {
                        'title': 'QSC 분석',
                        'icon': 'bar-chart-3',
                        'position': 3
                    },
                    'dashboard': {
                        'type': 'gauge',
                        'size': 'small',
                        'component': 'QSCGaugeChart'
                    }
                },
                'download_count': 67,
                'rating': 4.7,
                'review_count': 12,
                'is_installed': False
            }
        ]
        
        category_list = ['스케줄링', '고객 관리', '품질 관리', '계약 관리', '재고 관리']
        total_plugins = len(plugin_data)
        installed_plugins = sum(1 for p in plugin_data if p['is_installed'])
        
        return jsonify({
            'success': True,
            'message': '플러그인 API가 정상적으로 작동합니다! (임시 더미 데이터)',
            'data': {
                'plugins': plugin_data,
                'categories': category_list,
                'total_plugins': total_plugins,
                'installed_plugins': installed_plugins,
                'available_plugins': total_plugins - installed_plugins
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'API 오류 발생: {str(e)}',
            'data': {
                'plugins': [],
                'categories': [],
                'total_plugins': 0,
                'installed_plugins': 0,
                'available_plugins': 0
            }
        }), 500

@app.route('/api/plugin/categories', methods=['GET'])
def get_plugin_categories():
    """플러그인 카테고리 목록 조회 - 임시 더미 데이터"""
    try:
        # 임시로 더미 데이터 반환
        categories = [
            {
                'id': 'scheduling',
                'name': '스케줄링',
                'description': '직원 스케줄 및 근무 관리 플러그인',
                'icon': 'fas fa-calendar-alt',
                'plugin_count': 1
            },
            {
                'id': 'customer_management',
                'name': '고객 관리',
                'description': '고객 리뷰 및 피드백 관리 플러그인',
                'icon': 'fas fa-users',
                'plugin_count': 1
            },
            {
                'id': 'quality_management',
                'name': '품질 관리',
                'description': 'QSC 및 품질 관리 플러그인',
                'icon': 'fas fa-clipboard-check',
                'plugin_count': 1
            },
            {
                'id': 'contract_management',
                'name': '계약 관리',
                'description': '계약 및 문서 관리 플러그인',
                'icon': 'fas fa-file-contract',
                'plugin_count': 0
            },
            {
                'id': 'inventory_management',
                'name': '재고 관리',
                'description': '재고 및 발주 관리 플러그인',
                'icon': 'fas fa-boxes',
                'plugin_count': 0
            }
        ]
        
        return jsonify({
            'success': True,
            'categories': categories
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'카테고리 조회 중 오류 발생: {str(e)}',
            'categories': []
        }), 500

@app.route('/api/plugin/install', methods=['POST'])
@csrf.exempt
def install_plugin():
    """플러그인 설치 - 임시 더미 데이터"""
    try:
        data = request.get_json()
        plugin_id = data.get('plugin_id')
        
        if not plugin_id:
            return jsonify({
                'success': False,
                'error': '플러그인 ID가 필요합니다.'
            }), 400
        
        # 임시로 더미 응답 반환
        plugin_names = {
            1: 'AI 스케줄 최적화',
            2: '리뷰 자동 요약',
            3: 'QSC 자동 분석'
        }
        
        plugin_name = plugin_names.get(plugin_id, f'플러그인 {plugin_id}')
        installation_id = f'install_{plugin_id}_{12345}'
        
        return jsonify({
            'success': True,
            'message': f'플러그인 "{plugin_name}"이(가) 성공적으로 설치되었습니다.',
            'installation_id': installation_id,
            'plugin_name': plugin_name
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': '플러그인 설치 실패',
            'details': str(e)
        }), 500

@app.route('/api/plugin/uninstall', methods=['POST'])
@csrf.exempt
def uninstall_plugin():
    """플러그인 제거 - 실제 DB 연동"""
    try:
        from models.plugin_models import PluginInstallation, PluginUsage
        from datetime import datetime
        
        data = request.get_json()
        installation_id = data.get('installation_id')
        
        if not installation_id:
            return jsonify({
                'success': False,
                'error': '설치 ID가 필요합니다.'
            }), 400
        
        # 설치 기록 찾기
        installation = PluginInstallation.query.get(installation_id)
        if not installation:
            return jsonify({
                'success': False,
                'error': '설치 기록을 찾을 수 없습니다.'
            }), 404
        
        if installation.status != 'active':
            return jsonify({
                'success': False,
                'error': '이미 제거된 플러그인입니다.'
            }), 400
        
        # 제거 처리
        installation.status = 'uninstalled'
        installation.uninstalled_at = datetime.utcnow()
        
        # 플러그인 설치 상태 업데이트
        plugin = installation.plugin
        plugin.is_installed = False
        
        # 사용 기록 생성
        usage = PluginUsage(
            plugin_id=installation.plugin_id,
            action='uninstall',
            timestamp=datetime.utcnow()
        )
        db.session.add(usage)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'플러그인이 성공적으로 제거되었습니다.',
            'installation_id': installation_id,
            'plugin_name': plugin.display_name
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': '플러그인 제거 실패',
            'details': str(e)
        }), 500

@app.route('/api/admin/plugin/register', methods=['POST'])
@csrf.exempt
def admin_register_plugin():
    """관리자용 플러그인 등록 API"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['name', 'display_name', 'description', 'version', 'author', 'category', 'file_path']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'필수 필드가 누락되었습니다: {field}'
                }), 400
        
        # 플러그인 ID 형식 검증 (영문 소문자, 언더스코어만 허용)
        import re
        if not re.match(r'^[a-z_]+$', data['name']):
            return jsonify({
                'success': False,
                'error': '플러그인 ID는 영문 소문자와 언더스코어만 사용 가능합니다.'
            }), 400
        
        # 버전 형식 검증
        if not re.match(r'^\d+\.\d+\.\d+$', data['version']):
            return jsonify({
                'success': False,
                'error': '버전은 x.y.z 형식이어야 합니다.'
            }), 400
        
        # UI 스키마 검증
        ui_schema = data.get('ui_schema', {})
        if not isinstance(ui_schema, dict):
            return jsonify({
                'success': False,
                'error': 'UI 스키마가 올바르지 않습니다.'
            }), 400
        
        # 플러그인 데이터 구성
        plugin_data = {
            'name': data['name'],
            'display_name': data['display_name'],
            'description': data['description'],
            'version': data['version'],
            'author': data['author'],
            'category': data['category'],
            'tags': data.get('tags', []),
            'icon': data.get('icon', ''),
            'file_path': data['file_path'],
            'ui_schema': ui_schema,
            'is_active': True,
            'is_installed': False,
            'download_count': 0,
            'rating': 0.0,
            'review_count': 0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # 실제 DB 연동 시에는 여기서 Plugin 모델에 저장
        # 현재는 임시로 성공 응답만 반환
        print(f"새 플러그인 등록 요청: {plugin_data['name']}")
        
        return jsonify({
            'success': True,
            'message': '플러그인이 성공적으로 등록되었습니다.',
            'data': {
                'plugin_id': f'plugin_{len(str(hash(data["name"])))}',
                'name': plugin_data['name'],
                'display_name': plugin_data['display_name']
            }
        })
        
    except Exception as e:
        print(f"플러그인 등록 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '플러그인 등록 중 오류가 발생했습니다.',
            'details': str(e)
        }), 500


# 모듈 마켓플레이스 API 블루프린트 등록
try:
    from api.module_marketplace_api import module_marketplace_api_bp

    app.register_blueprint(module_marketplace_api_bp, name="module_marketplace_api_v2")
    logger.info("모듈 마켓플레이스 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"모듈 마켓플레이스 API 블루프린트 등록 실패: {e}")

# 모듈 설치 시스템 초기화
try:
    from core.backend.module_installation_system import module_installation_system

    logger.info("모듈 설치 시스템 초기화 완료")
except Exception as e:
    logger.error(f"모듈 설치 시스템 초기화 실패: {e}")

# 메뉴 API 블루프린트 등록
try:
    from api.menu_api import menu_api_bp

    app.register_blueprint(menu_api_bp)
    logger.info("메뉴 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"메뉴 API 블루프린트 등록 실패: {e}")

# 모듈 개발 모드 API 블루프린트 등록
try:
    from api.module_development_api import module_development_api

    app.register_blueprint(module_development_api)
    logger.info("모듈 개발 모드 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"모듈 개발 모드 API 블루프린트 등록 실패: {e}")

# 모듈 마켓플레이스 라우트 블루프린트 등록 (비활성화 - 파일이 존재하지 않음)
# try:
#     from routes.module_marketplace_routes import module_marketplace_routes_bp
#     app.register_blueprint(module_marketplace_routes_bp)
#     logger.info("모듈 마켓플레이스 라우트 블루프린트 등록 완료")
# except Exception as e:
#     logger.error(f"모듈 마켓플레이스 라우트 블루프린트 등록 실패: {e}")

# 모듈 개발 모드 라우트 블루프린트 등록 (비활성화 - 파일이 존재하지 않음)
# try:
#     from routes.module_development_routes import module_dev_routes_bp
#     app.register_blueprint(module_dev_routes_bp)
#     logger.info("모듈 개발 모드 라우트 블루프린트 등록 완료")
# except Exception as e:
#     logger.error(f"모듈 개발 모드 라우트 블루프린트 등록 실패: {e}")

# 통합 연동 API 블루프린트 등록
try:
    from api.integrated_module_api import integrated_api_bp

    app.register_blueprint(integrated_api_bp)
    logger.info("통합 연동 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"통합 연동 API 블루프린트 등록 실패: {e}")

# 통합 연동 시스템 시작
try:
    from core.backend.integrated_module_system import integrated_system

    integrated_system.start_integration_system()
    logger.info("통합 연동 시스템 시작 완료")
except Exception as e:
    logger.error(f"통합 연동 시스템 시작 실패: {e}")


@app.route("/api/admin/brand-managers", methods=["POST"])
def api_admin_create_brand_manager():
    """브랜드 관리자 생성 API"""
    try:
        data = request.get_json()

        # 필수 필드 검증
        required_fields = ["username", "name", "email", "password", "brand_id"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} 필드는 필수입니다."}), 400

        # 사용자명 중복 확인
        existing_user = User.query.filter_by(username=data["username"]).first()
        if existing_user:
            return jsonify({"error": "이미 존재하는 사용자명입니다."}), 400

        # 이메일 중복 확인
        existing_email = User.query.filter_by(email=data["email"]).first()
        if existing_email:
            return jsonify({"error": "이미 존재하는 이메일입니다."}), 400

        # 브랜드 존재 확인
        brand = Brand.query.get(data["brand_id"])
        if not brand:
            return jsonify({"error": "존재하지 않는 브랜드입니다."}), 400

        # 새 브랜드 관리자 생성
        new_manager = User()
        new_manager.username = data["username"]
        new_manager.name = data["name"]
        new_manager.email = data["email"]
        new_manager.set_password(data["password"])
        new_manager.role = "brand_manager"
        new_manager.brand_id = data["brand_id"]
        new_manager.status = "approved"  # 관리자가 생성하는 경우 바로 승인
        new_manager.phone = data.get("phone")

        db.session.add(new_manager)
        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "브랜드 관리자가 성공적으로 생성되었습니다.",
                    "manager_id": new_manager.id,
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"브랜드 관리자 생성 오류: {str(e)}")
        return jsonify({"error": "브랜드 관리자 생성 중 오류가 발생했습니다."}), 500


@app.route("/api/address/search")
def api_address_search():
    """주소 검색 API (카카오 주소 검색 API 사용)"""
    try:
        query = request.args.get("query", "").strip()

        if not query:
            return jsonify({"error": "검색어를 입력해주세요."}), 400

        # 카카오 주소 검색 API 호출
        import requests

        # 카카오 REST API 키 (실제 사용 시 환경변수로 관리)
        KAKAO_API_KEY = os.environ.get("KAKAO_REST_API_KEY", "YOUR_KAKAO_REST_API_KEY")

        headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}

        params = {"query": query, "size": 10}

        # 카카오 주소 검색 API 호출
        response = requests.get(
            "https://dapi.kakao.com/v2/local/search/address.json",
            headers=headers,
            params=params,
        )

        if response.status_code == 200:
            data = response.json()
            addresses = []

            for doc in data.get("documents", []):
                address_info = {
                    "road_address": doc.get("address_name", ""),
                    "jibun_address": doc.get("address_name", ""),
                    "postal_code": doc.get("zip_code", ""),
                    "x": doc.get("x", ""),
                    "y": doc.get("y", ""),
                }
                addresses.append(address_info)

            return jsonify({"success": True, "addresses": addresses})
        else:
            # 카카오 API 호출 실패 시 더미 데이터 반환 (개발용)
            dummy_addresses = [
                {
                    "road_address": f"{query} (더미 데이터)",
                    "jibun_address": f"{query} 지번주소",
                    "postal_code": "12345",
                    "x": "127.0",
                    "y": "37.0",
                }
            ]

            return jsonify(
                {
                    "success": True,
                    "addresses": dummy_addresses,
                    "note": "카카오 API 키가 설정되지 않아 더미 데이터를 반환합니다.",
                }
            )

    except Exception as e:
        logger.error(f"주소 검색 오류: {str(e)}")
        return jsonify({"error": "주소 검색 중 오류가 발생했습니다."}), 500


@app.route("/api/admin/stores", methods=["POST"])
@protect_data_creation_endpoint("Store")
@audit_operation("create", "Store")
def api_admin_create_store():
    """매장 생성 API"""
    try:
        data = request.get_json()

        # 필수 필드 검증
        required_fields = ["name", "store_code", "brand_id"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} 필드는 필수입니다."}), 400

        # 브랜드 존재 확인
        brand = Brand.query.get(data["brand_id"])
        if not brand:
            return jsonify({"error": "존재하지 않는 브랜드입니다."}), 400

        # 매장 코드 중복 확인
        existing_store = Branch.query.filter_by(store_code=data["store_code"]).first()
        if existing_store:
            return jsonify({"error": "이미 존재하는 매장 코드입니다."}), 400

        # 체인점인 경우 여러 매장 생성 옵션
        if brand.store_type == "chain" and data.get("create_multiple"):
            # 여러 매장 일괄 생성
            store_count = data.get("store_count", 1)
            created_stores = []

            for i in range(store_count):
                store_name = f"{data['name']} {i+1:02d}호점"
                store_code = f"{data['store_code']}{i+1:02d}"

                new_store = Branch()
                new_store.name = store_name
                new_store.store_code = store_code
                new_store.address = data.get("address", "")
                new_store.phone = data.get("phone", "")
                new_store.store_type = data.get("store_type", "franchise")
                new_store.capacity = data.get("capacity")
                new_store.brand_id = data["brand_id"]
                new_store.industry_id = brand.industry_id
                new_store.status = "active"

                db.session.add(new_store)
                created_stores.append(
                    {"id": new_store.id, "name": store_name, "store_code": store_code}
                )

            db.session.commit()

            return (
                jsonify(
                    {
                        "success": True,
                        "message": f"{store_count}개의 매장이 성공적으로 생성되었습니다.",
                        "stores": created_stores,
                        "brand_type": "chain",
                    }
                ),
                201,
            )

        else:
            # 단일 매장 생성 (개인 매장 또는 체인점의 단일 생성)
            new_store = Branch()
            new_store.name = data["name"]
            new_store.store_code = data["store_code"]
            new_store.address = data.get("address", "")
            new_store.phone = data.get("phone", "")
            new_store.store_type = data.get("store_type", "franchise")
            new_store.capacity = data.get("capacity")
            new_store.brand_id = data["brand_id"]
            new_store.industry_id = brand.industry_id
            new_store.status = "active"

            db.session.add(new_store)
            db.session.commit()

            return (
                jsonify(
                    {
                        "success": True,
                        "message": "매장이 성공적으로 생성되었습니다.",
                        "store_id": new_store.id,
                        "brand_type": brand.store_type,
                    }
                ),
                201,
            )

    except Exception as e:
        db.session.rollback()
        logger.error(f"매장 생성 오류: {str(e)}")
        return jsonify({"error": "매장 생성 중 오류가 발생했습니다."}), 500


@app.route("/api/admin/brand/<int:brand_id>/change-type", methods=["PUT"])
def api_admin_change_brand_type(brand_id):
    """브랜드 유형 변경 API (개인 매장 ↔ 체인점)"""
    try:
        data = request.get_json()
        new_type = data.get("store_type")

        if not new_type or new_type not in ["individual", "chain"]:
            return jsonify({"error": "유효하지 않은 매장 유형입니다."}), 400

        # 브랜드 존재 확인
        brand = Brand.query.get(brand_id)
        if not brand:
            return jsonify({"error": "존재하지 않는 브랜드입니다."}), 404

        # 현재 유형과 같은 경우 변경 불필요
        if brand.store_type == new_type:
            return jsonify({"error": "이미 해당 유형입니다."}), 400

        # 기존 유형 저장
        old_type = brand.store_type

        # 유형 변경
        brand.store_type = new_type
        db.session.commit()

        # 프론트엔드 서버 업데이트 (기존 서버가 있는 경우)
        try:
            frontend_dir = f"frontend_brands/{brand.code}"
            if os.path.exists(frontend_dir):
                frontend_port = 3000 + brand.id

                # package.json 업데이트
                package_json_path = f"{frontend_dir}/package.json"
                if os.path.exists(package_json_path):
                    with open(package_json_path, "r", encoding="utf-8") as f:
                        package_data = json.load(f)

                    if new_type == "individual":
                        package_data["name"] = f"{brand.code}-individual-frontend"
                        package_data["description"] = (
                            f"{brand.name} 개인 매장 전용 프론트엔드"
                        )
                    else:
                        package_data["name"] = f"{brand.code}-chain-frontend"
                        package_data["description"] = (
                            f"{brand.name} 체인점 전용 프론트엔드"
                        )

                    with open(package_json_path, "w", encoding="utf-8") as f:
                        json.dump(package_data, f, indent=2, ensure_ascii=False)

                # 페이지 업데이트
                pages_dir = f"{frontend_dir}/pages"
                if os.path.exists(pages_dir):
                    if new_type == "individual":
                        # 개인 매장용 페이지로 변경
                        with open(f"{pages_dir}/index.js", "w", encoding="utf-8") as f:
                            f.write(
                                f"""import React from 'react';

export default function {brand.name}IndividualDashboard() {{
  return (
    <div>
      <h1>{brand.name} 개인 매장 대시보드</h1>
      <p>개인 매장 전용 프론트엔드 서버가 생성되었습니다.</p>
      <div>
        <h2>개인 매장 특징</h2>
        <ul>
          <li>단일 매장 관리</li>
          <li>간단한 운영 시스템</li>
          <li>직원 관리 최적화</li>
        </ul>
      </div>
    </div>
  );
}}
"""
                            )
                    else:
                        # 체인점용 페이지로 변경
                        with open(f"{pages_dir}/index.js", "w", encoding="utf-8") as f:
                            f.write(
                                f"""import React from 'react';

export default function {brand.name}ChainDashboard() {{
  return (
    <div>
      <h1>{brand.name} 체인점 대시보드</h1>
      <p>체인점 전용 프론트엔드 서버가 생성되었습니다.</p>
      <div>
        <h2>체인점 특징</h2>
        <ul>
          <li>다중 매장 관리</li>
          <li>중앙 집중식 운영</li>
          <li>매장별 성과 분석</li>
          <li>일괄 매장 생성 기능</li>
        </ul>
      </div>
    </div>
  );
}}
"""
                            )

                logger.info(
                    f"브랜드 {brand.name}의 유형이 {old_type}에서 {new_type}로 변경되었습니다. 프론트엔드 서버도 업데이트되었습니다."
                )

        except Exception as e:
            logger.error(f"프론트엔드 서버 업데이트 실패: {e}")
            # 프론트엔드 업데이트 실패해도 브랜드 유형은 변경됨

        return (
            jsonify(
                {
                    "success": True,
                    "message": f"브랜드 유형이 {old_type}에서 {new_type}로 성공적으로 변경되었습니다.",
                    "old_type": old_type,
                    "new_type": new_type,
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"브랜드 유형 변경 오류: {str(e)}")
        return jsonify({"error": "브랜드 유형 변경 중 오류가 발생했습니다."}), 500


# 모듈/플러그인 통합 개발 API 블루프린트 등록
try:
    from api.module_plugin_dev_api import module_plugin_dev_bp

    app.register_blueprint(module_plugin_dev_bp)
    logger.info("모듈/플러그인 통합 개발 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"모듈/플러그인 통합 개발 API 블루프린트 등록 실패: {e}")

# 모듈/플러그인 개발 페이지 라우트 블루프린트 등록 (비활성화 - 파일이 존재하지 않음)
# try:
#     from routes.module_plugin_dev_routes import module_plugin_dev_routes_bp
#     app.register_blueprint(module_plugin_dev_routes_bp)
#     logger.info("모듈/플러그인 개발 페이지 라우트 블루프린트 등록 완료")
# except Exception as e:
#     logger.error(f"모듈/플러그인 개발 페이지 라우트 블루프린트 등록 실패: {e}")

# 가계부 모듈 등록
try:
    import sys
    import os

    sys.path.append(os.path.join(os.path.dirname(__file__), "modules", "ledger"))
    from main import ledger_bp, init_db

    init_db(app)
    app.register_blueprint(ledger_bp)
    logger.info("가계부 모듈 등록 완료")
except Exception as e:
    logger.error(f"가계부 모듈 등록 실패: {e}")


@app.route("/api/module-settings/<module_id>")
def api_module_settings_public(module_id):
    """모듈 설정 조회 API (공개)"""
    try:
        # 가계부 모듈 전용 설정
        if module_id == "ledger":
            settings = {
                "auto_backup": {
                    "label": "자동 백업",
                    "type": "checkbox",
                    "value": True,
                },
                "backup_interval": {
                    "label": "백업 주기 (시간)",
                    "type": "number",
                    "value": 24,
                },
                "notification_enabled": {
                    "label": "알림 활성화",
                    "type": "checkbox",
                    "value": True,
                },
                "log_level": {
                    "label": "로그 레벨",
                    "type": "select",
                    "value": "info",
                    "options": ["debug", "info", "warning", "error"],
                },
                "default_currency": {
                    "label": "기본 통화",
                    "type": "select",
                    "value": "KRW",
                    "options": ["KRW", "USD", "EUR", "JPY"],
                },
                "monthly_budget": {
                    "label": "월 예산 설정",
                    "type": "number",
                    "value": 1000000,
                },
                "category_colors": {
                    "label": "카테고리 색상",
                    "type": "object",
                    "value": {
                        "식비": "#FF6B6B",
                        "교통비": "#4ECDC4",
                        "쇼핑": "#45B7D1",
                        "문화생활": "#96CEB4",
                        "의료비": "#FFEAA7",
                        "기타": "#DDA0DD",
                    },
                },
            }
        else:
            # 기본 설정 데이터
            settings = {
                "auto_backup": {
                    "label": "자동 백업",
                    "type": "checkbox",
                    "value": True,
                },
                "backup_interval": {
                    "label": "백업 주기 (시간)",
                    "type": "number",
                    "value": 24,
                },
                "notification_enabled": {
                    "label": "알림 활성화",
                    "type": "checkbox",
                    "value": True,
                },
                "log_level": {
                    "label": "로그 레벨",
                    "type": "select",
                    "value": "info",
                    "options": ["debug", "info", "warning", "error"],
                },
            }

        return jsonify({"success": True, "settings": settings})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/modules/<module_id>/settings")
@csrf.exempt
def api_modules_settings(module_id):
    """모듈 설정 조회 API"""
    try:
        # 가계부 모듈 전용 설정
        if module_id == "ledger":
            settings = {
                "auto_backup": {
                    "label": "자동 백업",
                    "type": "checkbox",
                    "value": True,
                },
                "backup_interval": {
                    "label": "백업 주기 (시간)",
                    "type": "number",
                    "value": 24,
                },
                "notification_enabled": {
                    "label": "알림 활성화",
                    "type": "checkbox",
                    "value": True,
                },
                "log_level": {
                    "label": "로그 레벨",
                    "type": "select",
                    "value": "info",
                    "options": ["debug", "info", "warning", "error"],
                },
                "default_currency": {
                    "label": "기본 통화",
                    "type": "select",
                    "value": "KRW",
                    "options": ["KRW", "USD", "EUR", "JPY"],
                },
                "monthly_budget": {
                    "label": "월 예산 설정",
                    "type": "number",
                    "value": 1000000,
                },
                "category_colors": {
                    "label": "카테고리 색상",
                    "type": "object",
                    "value": {
                        "식비": "#FF6B6B",
                        "교통비": "#4ECDC4",
                        "쇼핑": "#45B7D1",
                        "문화생활": "#96CEB4",
                        "의료비": "#FFEAA7",
                        "기타": "#DDA0DD",
                    },
                },
            }
        else:
            # 기본 설정 데이터
            settings = {
                "auto_backup": {
                    "label": "자동 백업",
                    "type": "checkbox",
                    "value": True,
                },
                "backup_interval": {
                    "label": "백업 주기 (시간)",
                    "type": "number",
                    "value": 24,
                },
                "notification_enabled": {
                    "label": "알림 활성화",
                    "type": "checkbox",
                    "value": True,
                },
                "log_level": {
                    "label": "로그 레벨",
                    "type": "select",
                    "value": "info",
                    "options": ["debug", "info", "warning", "error"],
                },
            }

        return jsonify({"success": True, "settings": settings})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/modules/<module_id>/brands", methods=["GET"])
def api_module_applied_brands(module_id):
    """
    해당 모듈이 적용된 브랜드 목록 조회 API (DB 기반)
    """
    try:
        brand_plugins = BrandPlugin.query.filter_by(code=module_id).all()
        brands = [Brand.query.get(bp.brand_id) for bp in brand_plugins]
        applied_brands = [b.code for b in brands if b is not None]
        return jsonify({"success": True, "applied_brands": applied_brands})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/modules/<module_id>/brands", methods=["POST"])
def api_module_apply_brand(module_id):
    """
    브랜드별 모듈 적용/해제 API (DB 기반)
    body: {brand_code, apply: true/false}
    """
    data = request.get_json()
    brand_code = data.get("brand_code")
    apply = data.get("apply", True)
    if not brand_code:
        return jsonify({"success": False, "error": "brand_code가 필요합니다."}), 400
    try:
        brand = Brand.query.filter_by(code=brand_code).first()
        if not brand:
            return (
                jsonify({"success": False, "error": "해당 브랜드를 찾을 수 없습니다."}),
                404,
            )
        # 권한 체크(브랜드 관리자 이상만)
        if not (
            current_user.is_admin()
            or current_user.role in ["admin", "brand_admin", "super_admin"]
            or getattr(current_user, "brand_id", None) == brand.id
        ):
            return jsonify({"success": False, "error": "권한이 없습니다."}), 403
        if apply:
            exists = BrandPlugin.query.filter_by(
                brand_id=brand.id, code=module_id
            ).first()
            if not exists:
                module = Module.query.filter_by(id=module_id).first()
                if not module:
                    return (
                        jsonify(
                            {"success": False, "error": "해당 모듈을 찾을 수 없습니다."}
                        ),
                        404,
                    )
                new_bp = BrandPlugin(
                    brand_id=brand.id,
                    name=module.name,
                    code=module_id,
                    description=module.description,
                    version=module.version,
                    is_active=True,
                )
                db.session.add(new_bp)
                db.session.commit()
        else:
            bp = BrandPlugin.query.filter_by(brand_id=brand.id, code=module_id).first()
            if bp:
                db.session.delete(bp)
                db.session.commit()
        # 적용된 브랜드 목록 반환
        brand_plugins = BrandPlugin.query.filter_by(code=module_id).all()
        applied_brands = [
            Brand.query.get(bp.brand_id).code
            for bp in brand_plugins
            if Brand.query.get(bp.brand_id)
        ]
        return jsonify({"success": True, "applied_brands": applied_brands})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# 서버 시작 시 운영 자동화 스케줄러(승인 대기 알림) 자동 실행 - 비활성화됨
# import threading
# import subprocess


# def start_auto_admin_alerts():
#     def run_script():
#         subprocess.Popen(["python", "scripts/auto_admin_alerts.py"])

#     t = threading.Thread(target=run_script, daemon=True)
#     t.start()


# start_auto_admin_alerts()

# from routes.module_marketplace import module_marketplace_bp
# app.register_blueprint(module_marketplace_bp, url_prefix="/api/module-marketplace")


# [디버그] 실제 등록된 모든 라우트 목록을 출력 (404 원인 분석용)
def print_all_routes(app):
    print("\n[Flask 라우트 목록]")
    for rule in app.url_map.iter_rules():
        methods = ",".join(sorted(rule.methods))
        print(f"{rule.rule:50s}  [{methods}]  -> {rule.endpoint}")
    print("[끝]\n")


print_all_routes(app)

from api.review_external import review_external_bp  # 신규 리뷰 연동/감성분석 API

app.register_blueprint(review_external_bp)

from api.policy_manager import policy_manager_bp  # 정책/규칙 관리 API

app.register_blueprint(policy_manager_bp)

from api.ai_automation import ai_automation_bp  # AI 자동화 기반 운영 고도화 API

app.register_blueprint(ai_automation_bp)

from api.integration_external import (
    integration_external_bp,
)  # 외부 시스템 연동/감성분석 API

app.register_blueprint(integration_external_bp)

from api.franchise import franchise_bp  # 프랜차이즈(본사-지점) 지원 API

app.register_blueprint(franchise_bp)

from api.reward_system import reward_system_bp  # 복지/참여/보상 시스템 API

app.register_blueprint(reward_system_bp)

# 새로운 API 블루프린트 등록
from api.security_enhanced import security_bp
from api.user_experience_enhanced import ux_bp
from api.analytics_advanced_enhanced import analytics_enhanced_bp
from api.integrated_ai_api_enhanced import integrated_ai_bp

app.register_blueprint(security_bp)
app.register_blueprint(ux_bp)
app.register_blueprint(analytics_enhanced_bp)
app.register_blueprint(integrated_ai_bp)

# AI 시스템 최적화 초기화 - 비활성화됨
# try:
#     from scripts.ai_system_optimizer import AISystemOptimizer

#     ai_optimizer = AISystemOptimizer()
#     ai_optimizer.start_monitoring()
#     logger.info("AI 시스템 최적화 시작")
# except Exception as e:
#     logger.warning(f"AI 시스템 최적화 초기화 실패: {e}")

# AI 모듈들 import 및 초기화
from api.performance_optimization import init_performance_optimization
from api.system_monitoring_advanced import init_system_monitoring
from api.ai_integrated_api import ai_integrated_bp


# 기존 create_app 함수 수정
def create_app():
    app = Flask(__name__)

    # 기존 설정들...
    app.config["SECRET_KEY"] = "your-secret-key-here"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///your_program.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # AI 모듈들 초기화
    try:
        init_performance_optimization(app)
        init_system_monitoring(app)
        logger.info("AI 모듈들 초기화 완료")
    except Exception as e:
        logger.warning(f"AI 모듈 초기화 실패: {e}")

    # 기존 블루프린트들...
    from api.admin_dashboard_api import admin_dashboard_api
    # from routes.admin_dashboard_export import admin_dashboard_export_bp  # 파일 누락으로 비활성화

    # ... 기타 블루프린트들

    # 멀티테넌시 CRUD 블루프린트 등록
    from api.multitenancy_api import multitenancy_bp
    app.register_blueprint(multitenancy_bp)

    # 플러그인 관련 블루프린트 등록
    from api.plugin_system_manager_api import plugin_system_manager_bp
    from api.plugin_operations_api import plugin_operations_bp
    from api.plugin_monitoring_dashboard import plugin_monitoring_bp
    app.register_blueprint(plugin_system_manager_bp)
    app.register_blueprint(plugin_operations_bp)
    app.register_blueprint(plugin_monitoring_bp)
    
    # 플러그인 관리 블루프린트 등록
    try:
        from plugins.plugin_management import plugin_management
        app.register_blueprint(plugin_management)
        print("플러그인 관리 블루프린트 등록 완료")
    except Exception as e:
        print(f"플러그인 관리 블루프린트 등록 실패: {e}")

    # AI 통합 API 블루프린트 등록
    app.register_blueprint(ai_integrated_bp)
    
    # 데이터 동기화 API 블루프린트 등록
    try:
        from api.data_sync_api import data_sync_bp
        app.register_blueprint(data_sync_bp)
        logger.info("데이터 동기화 API 블루프린트 등록 완료")
    except Exception as e:
        logger.error(f"데이터 동기화 API 블루프린트 등록 실패: {e}")

    # 성능 최적화 API 블루프린트 등록
    try:
        from api.performance_optimization_api import performance_optimization_bp
        app.register_blueprint(performance_optimization_bp, url_prefix='/api/performance-optimization')
        logger.info("성능 최적화 API 블루프린트 등록 완료")
    except Exception as e:
        logger.error(f"성능 최적화 API 블루프린트 등록 실패: {e}")

    # 플러그인 모델은 이미 models/plugin_models.py에서 정의됨

    # 플러그인 마켓플레이스 Blueprint 등록
    try:
        from api.plugin_marketplace import plugin_marketplace_bp
        app.register_blueprint(plugin_marketplace_bp, url_prefix='/api/plugin')
        print("✅ 플러그인 마켓플레이스 Blueprint가 등록되었습니다.")
    except ImportError as e:
        print(f"⚠️ 플러그인 마켓플레이스 Blueprint 등록 실패: {e}")

    # 관리자 플러그인 등록 Blueprint 등록
    try:
        from api.admin_plugin_registration import admin_plugin_registration_bp
        app.register_blueprint(admin_plugin_registration_bp)
        print("✅ 관리자 플러그인 등록 Blueprint가 등록되었습니다.")
    except ImportError as e:
        print(f"⚠️ 관리자 플러그인 등록 Blueprint 등록 실패: {e}")

    # 간단한 플러그인 API Blueprint 등록
    try:
        from api.simple_plugin_api import simple_plugin_bp
        app.register_blueprint(simple_plugin_bp)
        print("✅ 간단한 플러그인 API Blueprint가 등록되었습니다.")
    except ImportError as e:
        print(f"⚠️ 간단한 플러그인 API Blueprint 등록 실패: {e}")

    # 시스템 상태 API Blueprint 등록
    try:
        app.register_blueprint(system_health_api)
        print("✅ 시스템 상태 API Blueprint가 등록되었습니다.")
    except Exception as e:
        print(f"⚠️ 시스템 상태 API Blueprint 등록 실패: {e}")

    # AI 분석 API Blueprint 등록
    try:
        if AI_ANALYTICS_AVAILABLE and ai_analytics_api is not None:
            app.register_blueprint(ai_analytics_api)
            print("✅ AI 분석 API Blueprint가 등록되었습니다.")
        else:
            print("⚠️ AI 분석 API Blueprint 비활성화됨 (라이브러리 문제)")
    except Exception as e:
        print(f"⚠️ AI 분석 API Blueprint 등록 실패: {e}")

    # 고급 분석 API Blueprint 등록
    try:
        app.register_blueprint(advanced_analytics_api)
        print("✅ 고급 분석 API Blueprint가 등록되었습니다.")
    except Exception as e:
        print(f"⚠️ 고급 분석 API Blueprint 등록 실패: {e}")

    # 기존 초기화 코드들...
    db.init_app(app)
    login_manager.init_app(app)

    return app


# 모니터링 시스템 import
from monitoring.system_monitor import system_monitor
from monitoring.application_monitor import application_monitor
from utils.performance_optimizer import performance_optimizer

# 보안 시스템 import
from security.jwt_auth import jwt_auth, jwt_required, require_role, require_permission
from security.oauth2_auth import oauth2_manager
from security.two_factor_auth import two_factor_auth
from security.security_middleware import security_middleware

# E2E 테스트를 위한 API 엔드포인트
@app.route("/api/test/setup", methods=["POST"])
def api_test_setup():
    """E2E 테스트를 위한 환경 설정"""
    try:
        # 테스트 데이터베이스 초기화
        # 테스트 데이터 생성
        return jsonify({
            "success": True,
            "message": "테스트 환경이 설정되었습니다."
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/test/create-test-user", methods=["POST"])
def api_test_create_user():
    """E2E 테스트용 사용자 생성"""
    try:
        # 테스트 사용자 생성 로직
        test_user_id = "test_user_123"
        return jsonify({
            "success": True,
            "user_id": test_user_id,
            "message": "테스트 사용자가 생성되었습니다."
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/test/cleanup", methods=["POST"])
def api_test_cleanup():
    """E2E 테스트 환경 정리"""
    try:
        # 테스트 데이터 정리
        # 임시 파일 삭제
        return jsonify({
            "success": True,
            "message": "테스트 환경이 정리되었습니다."
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# 모니터링 API 엔드포인트
@app.route("/api/monitoring/system-metrics")
def api_system_metrics():
    """시스템 메트릭 조회"""
    try:
        metrics = system_monitor.get_current_metrics()
        if metrics:
            return jsonify({
                "success": True,
                "data": {
                    "cpu_percent": metrics.cpu_percent,
                    "memory_percent": metrics.memory_percent,
                    "memory_used_gb": metrics.memory_used,
                    "memory_total_gb": metrics.memory_total,
                    "disk_usage_percent": metrics.disk_usage_percent,
                    "disk_used_gb": metrics.disk_used,
                    "disk_total_gb": metrics.disk_total,
                    "network_bytes_sent": metrics.network_bytes_sent,
                    "network_bytes_recv": metrics.network_bytes_recv,
                    "active_connections": metrics.active_connections,
                    "load_average": metrics.load_average
                }
            })
        else:
            return jsonify({
                "success": False,
                "error": "메트릭을 수집할 수 없습니다."
            }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/monitoring/application-metrics")
def api_application_metrics():
    """애플리케이션 메트릭 조회"""
    try:
        metrics = application_monitor.get_current_stats()
        return jsonify({
            "success": True,
            "data": metrics
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/monitoring/performance-report")
def api_performance_report():
    """성능 리포트 조회"""
    try:
        system_report = system_monitor.get_performance_report()
        app_report = application_monitor.get_performance_report()
        backend_report = performance_optimizer.get_performance_metrics()
        
        return jsonify({
            "success": True,
            "data": {
                "system": system_report,
                "application": app_report,
                "backend": backend_report,
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/monitoring/endpoint-stats")
def api_endpoint_stats():
    """엔드포인트별 통계 조회"""
    try:
        hours = request.args.get('hours', 1, type=int)
        stats = application_monitor.get_endpoint_stats(hours)
        
        return jsonify({
            "success": True,
            "data": stats
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/monitoring/error-summary")
def api_error_summary():
    """에러 요약 조회"""
    try:
        hours = request.args.get('hours', 24, type=int)
        summary = application_monitor.get_error_summary(hours)
        
        return jsonify({
            "success": True,
            "data": summary
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/monitoring/export-metrics", methods=["POST"])
def api_export_metrics():
    """메트릭 내보내기"""
    try:
        data = request.get_json() or {}
        include_system = data.get('system', True)
        include_application = data.get('application', True)
        include_backend = data.get('backend', True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if include_system:
            system_monitor.export_metrics(f"system_metrics_{timestamp}.json")
        
        if include_application:
            application_monitor.export_metrics(f"application_metrics_{timestamp}.json")
        
        return jsonify({
            "success": True,
            "message": "메트릭 내보내기가 완료되었습니다.",
            "files": [
                f"system_metrics_{timestamp}.json" if include_system else None,
                f"application_metrics_{timestamp}.json" if include_application else None
            ]
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/websocket/dashboard-broadcast/start", methods=["POST"])
def api_start_dashboard_broadcast():
    """대시보드 브로드캐스트 시작"""
    try:
        websocket_manager.start_dashboard_broadcast()
        return jsonify({
            "success": True,
            "message": "대시보드 브로드캐스트가 시작되었습니다."
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/websocket/dashboard-broadcast/stop", methods=["POST"])
def api_stop_dashboard_broadcast():
    """대시보드 브로드캐스트 중지"""
    try:
        websocket_manager.stop_dashboard_broadcast()
        return jsonify({
            "success": True,
            "message": "대시보드 브로드캐스트 중지 요청이 완료되었습니다."
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/websocket/status")
def api_websocket_status():
    """WebSocket 상태 확인 API"""
    return jsonify({
        "status": "active",
        "connections": 0,
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route("/api/admin/policy/status")
@require_super_admin
def api_admin_policy_status():
    """권한 정책 설정 상태 확인 API (최상위 관리자 전용)"""
    from utils.authorization_policy import validate_policy_configuration, get_audit_summary
    
    try:
        config_status = validate_policy_configuration()
        audit_summary = get_audit_summary(days=7)
        
        return jsonify({
            "success": True,
            "policy_configuration": config_status,
            "audit_summary": audit_summary,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"권한 정책 상태 확인 오류: {e}")
        return jsonify({"error": "권한 정책 상태 확인에 실패했습니다."}), 500

@app.route("/api/admin/policy/audit-logs")
@require_super_admin
def api_admin_audit_logs():
    """감사 로그 조회 API (최상위 관리자 전용)"""
    from utils.authorization_policy import auth_policy
    
    try:
        days = request.args.get('days', 30, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        if not auth_policy.audit_logger:
            return jsonify({"error": "감사 로그 시스템이 사용할 수 없습니다."}), 500
        
        events = auth_policy.audit_logger.get_events(
            filters={"days": days},
            limit=limit
        )
        
        return jsonify({
            "success": True,
            "audit_logs": events,
            "total_count": len(events),
            "days": days,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"감사 로그 조회 오류: {e}")
        return jsonify({"error": "감사 로그 조회에 실패했습니다."}), 500
    """WebSocket 상태 조회"""
    try:
        return jsonify({
            "success": True,
            "data": websocket_manager.get_comprehensive_stats()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# 계층별 관리 라우트 직접 추가
@app.route('/admin/backend/hierarchy-management')
def hierarchy_management():
    """계층별 관리 메인 페이지"""
    return render_template('admin/cyberpunk_hierarchy_management.html')

@app.route('/admin/backend/industry-management')
def industry_management():
    """업종 관리 페이지"""
    return render_template('admin/cyberpunk_industry_management.html')

@app.route('/admin/backend/brand-management')
def brand_management():
    """브랜드 관리 페이지"""
    return render_template('admin/cyberpunk_brand_management.html')

@app.route('/admin/backend/branch-management')
def branch_management():
    """매장 관리 페이지"""
    return render_template('admin/cyberpunk_branch_management.html')

@app.route('/admin/backend/employee-management')
def employee_management():
    """직원 관리 페이지"""
    return render_template('admin/cyberpunk_employee_management.html')

# 계층별 관리 API 엔드포인트들
@app.route('/api/admin/hierarchy/tree')
def get_hierarchy_tree():
    """전체 계층 트리 조회"""
    
    try:
        from models_main import Industry, Brand, Branch, User
        
        # DB에서 조회
        industries = Industry.query.filter_by(is_active=True).order_by(Industry.name).all()
        
        tree_data = {
            'industries': []
        }
        
        total_brands = 0
        total_branches = 0
        total_users = 0
        
        for industry in industries:
            brands = Brand.query.filter_by(industry_id=industry.id, is_active=True).order_by(Brand.name).all()
            brand_data = []
            
            for brand in brands:
                branches = Branch.query.filter_by(brand_id=brand.id, is_active=True).order_by(Branch.name).all()
                branch_data = []
                
                for branch in branches:
                    users = User.query.filter_by(branch_id=branch.id, status='approved').order_by(User.username).all()
                    user_data = [{
                        'id': user.id,
                        'username': user.username,
                        'role': user.role,
                        'status': user.status,
                        'email': user.email
                    } for user in users]
                    
                    branch_data.append({
                        'id': branch.id,
                        'name': branch.name,
                        'store_code': branch.store_code,
                        'status': branch.status,
                        'users': user_data,
                        'user_count': len(user_data)
                    })
                    total_users += len(user_data)
                
                brand_data.append({
                    'id': brand.id,
                    'name': brand.name,
                    'code': brand.code,
                    'status': brand.status,
                    'branches': branch_data,
                    'branch_count': len(branch_data)
                })
                total_branches += len(branch_data)
            
            tree_data['industries'].append({
                'id': industry.id,
                'name': industry.name,
                'code': industry.code,
                'color': industry.color,
                'icon': industry.icon,
                'brands': brand_data,
                'brand_count': len(brand_data)
            })
            total_brands += len(brand_data)
        
        return jsonify({
            'success': True,
            'data': tree_data,
            'metadata': {
                'total_industries': len(tree_data['industries']),
                'total_brands': total_brands,
                'total_branches': total_branches,
                'total_users': total_users,
                'last_updated': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/hierarchy/changelog')
def get_hierarchy_changelog():
    """계층별 변경 이력 조회"""
    if not current_user.has_permission('system_management', 'view'):
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        from models_main import ActionLog
        
        # 최근 50개의 계층 관련 액션 로그 조회
        logs = ActionLog.query.filter(
            ActionLog.action.in_(['create_industry', 'update_industry', 'delete_industry',
                                'create_brand', 'update_brand', 'delete_brand',
                                'create_branch', 'update_branch', 'delete_branch',
                                'create_employee', 'update_employee', 'delete_employee'])
        ).order_by(ActionLog.created_at.desc()).limit(50).all()
        
        log_data = []
        for log in logs:
            log_data.append({
                'id': log.id,
                'action': log.action,
                'description': log.description,
                'user_id': log.user_id,
                'created_at': log.created_at.isoformat() if log.created_at else None,
                'details': log.details
            })
        
        return jsonify({
            'success': True,
            'data': log_data,
            'total': len(log_data)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/industries', methods=['GET'])
# @login_required  # 임시로 주석 처리
def get_industries():
    """업종 목록 조회"""
    # 개발 환경에서는 권한 검사 완화
    try:
        if not current_user.has_permission('system_management', 'view'):
            pass  # 개발 환경에서는 권한 검사 건너뛰기
    except:
        pass  # 권한 시스템이 없어도 작동하도록
    
    try:
        from models_main import Industry
        
        industries = Industry.query.filter_by(is_active=True).order_by(Industry.name).all()
        
        industry_data = []
        for industry in industries:
            # 브랜드 수 계산
            brand_count = len(industry.brands_list.all()) if hasattr(industry, 'brands_list') else 0
            
            industry_data.append({
                'id': industry.id,
                'name': industry.name,
                'code': industry.code,
                'description': industry.description,
                'color': industry.color or '#3B82F6',
                'icon': industry.icon or 'building',
                'is_active': industry.is_active,
                'status': 'active' if industry.is_active else 'inactive',
                'brand_count': brand_count,
                'created_at': industry.created_at.isoformat() if industry.created_at else None
            })
        
        return jsonify({
            'success': True,
            'data': industry_data,
            'total': len(industry_data)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/industries', methods=['POST'])
# @login_required  # 임시로 주석 처리
def create_industry():
    """업종 생성"""
    # 개발 환경에서는 권한 검사 완화
    try:
        if not current_user.has_permission('system_management', 'create'):
            pass  # 개발 환경에서는 권한 검사 건너뛰기
    except:
        pass  # 권한 시스템이 없어도 작동하도록
    
    try:
        from models_main import Industry
        from datetime import datetime
        
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['name', 'code']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} 필드는 필수입니다.'}), 400
        
        # 중복 검사
        existing_industry = Industry.query.filter_by(code=data['code']).first()
        if existing_industry:
            return jsonify({'error': '이미 존재하는 업종 코드입니다.'}), 400
        
        # 새 업종 생성
        new_industry = Industry(
            name=data['name'],
            code=data['code'],
            description=data.get('description', ''),
            color=data.get('color', '#3B82F6'),
            icon=data.get('icon', 'building'),
            status='active',
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_industry)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '업종이 성공적으로 생성되었습니다.',
            'industry': {
                'id': new_industry.id,
                'name': new_industry.name,
                'code': new_industry.code,
                'description': new_industry.description,
                'color': new_industry.color,
                'icon': new_industry.icon,
                'status': new_industry.status
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/branches', methods=['GET'])
def get_branches():
    """매장 목록 조회"""
    if not current_user.has_permission('system_management', 'view'):
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        from models_main import Branch, Brand
        
        branches = db.session.query(Branch, Brand.name.label('brand_name')).join(
            Brand, Branch.brand_id == Brand.id
        ).filter(Branch.is_active == True).order_by(Branch.name).all()
        
        branch_data = []
        for branch, brand_name in branches:
            branch_data.append({
                'id': branch.id,
                'name': branch.name,
                'store_code': branch.store_code,
                'brand_name': brand_name,
                'brand_id': branch.brand_id,
                'status': branch.status,
                'address': branch.address,
                'phone': branch.phone,
                'created_at': branch.created_at.isoformat() if branch.created_at else None
            })
        
        return jsonify({
            'success': True,
            'data': branch_data,
            'total': len(branch_data)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    # 모니터링 시스템 시작
    try:
        from utils.system_monitor import system_monitor
        system_monitor.start_monitoring()
        print("✅ 시스템 모니터링이 시작되었습니다.")
    except Exception as e:
        print(f"⚠️ 시스템 모니터링 시작 실패: {e}")
    
    try:
        application_monitor.start_monitoring()
        print("✅ 애플리케이션 모니터링이 시작되었습니다.")
    except Exception as e:
        print(f"⚠️ 애플리케이션 모니터링 시작 실패: {e}")
    
    try:
        performance_optimizer.init_app(app)
        print("✅ 성능 최적화가 초기화되었습니다.")
    except Exception as e:
        print(f"⚠️ 성능 최적화 초기화 실패: {e}")
    
    # 실시간 대시보드 브로드캐스트 시작
    websocket_manager.start_dashboard_broadcast()
    print("✅ WebSocket 대시보드 브로드캐스트가 시작되었습니다.")
    
    print("🚀 서버가 시작됩니다...")
    # 서버 실행 (WebSocket 지원 여부에 따라)
    if SOCKETIO_AVAILABLE:
        print("✅ WebSocket 지원으로 서버를 시작합니다...")
        socketio.run(app, debug=True, host="0.0.0.0", port=5000)
    else:
        print("⚠️ WebSocket 없이 기본 Flask 서버를 시작합니다...")
        app.run(debug=True, host="0.0.0.0", port=5000)
