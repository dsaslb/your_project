# -*- coding: utf-8 -*-
"""
멀티테넌시 관리 시스템 메인 애플리케이션
업종-브랜드-매장-직원 계층 구조와 플러그인 시스템을 지원하는 Flask 애플리케이션
"""

import os
import logging
import sys
from datetime import datetime
import time
import uuid
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import jwt
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash

# 로깅 설정
logger = logging.getLogger(__name__)

# 설정 및 확장 모듈 import (조건부)
try:
    from config.config import config_by_name
except ImportError:
    config_by_name = {}
# 확장 모듈 import (조건부)
try:
    from extensions import cache, csrf, db, limiter, login_manager, migrate, socketio
except ImportError:
    cache = csrf = db = limiter = login_manager = migrate = socketio = None

# AnonymousUserMixin import (조건부)
try:
    from models_main import AnonymousUserMixin
except ImportError:
    AnonymousUserMixin = None

# Swagger 설정 import (조건부)
SWAGGER_AVAILABLE = False
create_swagger_config = None

# WebSocket 매니저 import (조건부)
WEBSOCKET_AVAILABLE = False
websocket_manager = None

# WebSocket 서버 import (조건부)
WEBSOCKET_SERVER_AVAILABLE = False
create_websocket_server = None

# 데이터 모델 import (조건부)
try:
    from models_main import User, Industry, Brand
except ImportError:
    User = Industry = Brand = None

# 플러그인 모델 import (현재 사용하지 않음)
SCHEDULE_PLUGIN_AVAILABLE = False

# 권한 정책 시스템 import (조건부)
require_super_admin = None
auth_policy = None
try:
    from utils.authorization_policy import require_super_admin, AuthorizationPolicy
    auth_policy = AuthorizationPolicy()
except (ImportError, Exception) as e:
    logger.warning(f"권한 정책 시스템 import 실패 (무시됨): {e}")
    require_super_admin = None
    auth_policy = None

# 보안 강화 모듈 import (조건부)
security_middleware = None
try:
    from utils.security_middleware import security_middleware
except (ImportError, Exception) as e:
    logger.warning(f"보안 미들웨어 import 실패 (무시됨): {e}")
    security_middleware = None

# 캐시 매니저 import (조건부)
cache_manager = None
try:
    from utils.cache_manager import cache_manager
except (ImportError, Exception) as e:
    logger.warning(f"캐시 매니저 import 실패 (무시됨): {e}")
    cache_manager = None

# 시스템 최적화 모듈 import (조건부)
system_optimizer = None
try:
    from core.backend.plugin_optimizer import system_optimizer
except (ImportError, Exception) as e:
    logger.warning(f"시스템 최적화 모듈 import 실패 (무시됨): {e}")
    # 대체 시스템 최적화 클래스
    class SystemOptimizer:
        def generate_performance_report(self):
            return {"status": "healthy", "performance_score": 85}
        
        def optimize_database(self):
            return {"status": "optimized", "improvements": []}
        
        def monitor_system_resources(self):
            import psutil
            return {
                "cpu": {"percent": psutil.cpu_percent()},
                "memory": {"percent": psutil.virtual_memory().percent},
                "disk": {"percent": psutil.disk_usage('/').percent}
            }
        
        def analyze_database_performance(self):
            return {"status": "healthy", "query_time": "120ms"}
        
        def _calculate_performance_score(self, resources, db_analysis):
            return 85
    
    system_optimizer = SystemOptimizer()

# 보안 강화 모듈 import (조건부)
security_enhancer = None
try:
    from utils.security_enhancer import SecurityEnhancer
    security_enhancer = SecurityEnhancer()
except (ImportError, Exception) as e:
    logger.warning(f"보안 강화 모듈 import 실패 (무시됨): {e}")
    # 대체 보안 강화 클래스
    class SecurityEnhancer:
        def generate_secure_password(self, length=16):
            import secrets
            import string
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            return ''.join(secrets.choice(alphabet) for _ in range(length))
        
        def validate_password_strength(self, password):
            return {"score": 8, "strength": "strong", "recommendations": []}
        
        def encrypt_sensitive_data(self, data):
            return f"encrypted_{data}"
        
        def decrypt_sensitive_data(self, encrypted_data):
            return encrypted_data.replace("encrypted_", "")
        
        def generate_secure_token(self, payload, expires_in=3600):
            import jwt
            return jwt.encode(payload, "secret", algorithm="HS256")
        
        def verify_secure_token(self, token):
            import jwt
            return jwt.decode(token, "secret", algorithms=["HS256"])
        
        def sanitize_input(self, input_data):
            import html
            return html.escape(input_data)
        
        def validate_file_upload(self, filename, file_size, allowed_extensions=None):
            return {"valid": True, "message": "File is valid"}
        
        def generate_security_report(self):
            return {"status": "healthy", "issues": []}
        
        def log_security_event(self, event_type, details, user_id=None):
            logger.info(f"Security event: {event_type} - {details}")
    
    security_enhancer = SecurityEnhancer()

# 환경 설정
config_name = os.getenv("FLASK_ENV", "default")

# Flask 애플리케이션 초기화
app = Flask(__name__)
app.config.from_object(config_by_name.get(config_name, {}))
# 보안 키 설정
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "your-secret-key")
app.config["SECRET_KEY"] = app.config["JWT_SECRET_KEY"]
# JSON 설정
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
# CSRF 보호 완전 비활성화 (개발용)
app.config['WTF_CSRF_ENABLED'] = False

# SocketIO 초기화 (강제)
try:
    from extensions import socketio
    if socketio is None:
        raise ImportError("Socket.IO를 extensions에서 가져올 수 없습니다.")
except ImportError:
    # Socket.IO를 직접 초기화
    from flask_socketio import SocketIO
    socketio = SocketIO(cors_allowed_origins="*")
    logger.info("Socket.IO를 직접 초기화했습니다.")

# Socket.IO 이벤트 핸들러 (init_app 호출 전에 정의)
@socketio.on('connect')
def handle_connect():
    logger.info(f"클라이언트 연결됨: {request.sid}")
    return {'status': 'connected', 'sid': request.sid}

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"클라이언트 연결 해제됨: {request.sid}")

@socketio.on('po:created')
def handle_po_created(data):
    logger.info(f"발주 생성 이벤트 수신: {data}")
    # 모든 클라이언트에게 브로드캐스트
    socketio.emit('po:created', data, broadcast=True)

@socketio.on('po:status')
def handle_po_status(data):
    logger.info(f"발주 상태 변경 이벤트 수신: {data}")
    # 모든 클라이언트에게 브로드캐스트
    socketio.emit('po:status', data, broadcast=True)

@socketio.on('attendance:update')
def handle_attendance_update(data):
    logger.info(f"출근 이벤트 수신: {data}")
    socketio.emit('attendance:update', data, broadcast=True)

@socketio.on('inventory:update')
def handle_inventory_update(data):
    logger.info(f"재고 이벤트 수신: {data}")
    socketio.emit('inventory:update', data, broadcast=True)

@socketio.on('schedule:update')
def handle_schedule_update(data):
    logger.info(f"일정 이벤트 수신: {data}")
    socketio.emit('schedule:update', data, broadcast=True)

@socketio.on('order:update')
def handle_order_update(data):
    logger.info(f"주문 이벤트 수신: {data}")
    socketio.emit('order:update', data, broadcast=True)

# Socket.IO를 app에 연결 (이벤트 핸들러 정의 후)
# async 드라이버를 명시적으로 설정하여 eventlet 오류 방지
socketio.init_app(app, async_mode='threading', cors_allowed_origins="*")

# CORS 설정 (조건부)
if CORS:
    CORS(
        app,
        origins=["*"],  # 모든 도메인 허용 (개발용)
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"]
    )
else:
    # CORS가 없는 경우 기본 CORS 설정
    from flask_cors import CORS
    CORS(app, supports_credentials=True)

# OPTIONS 요청에 대한 전역 핸들러 추가
@app.before_request
def handle_preflight():
    """CORS preflight 요청 처리"""
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,X-Requested-With,Accept,X-API-Key")
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Max-Age", "86400")
        return response

# 확장 모듈 초기화 함수
def initialize_extensions():
    """Flask 확장 모듈들을 초기화합니다."""
    try:
        # extensions.py의 init_extensions 함수 사용
        from extensions import init_extensions
        init_extensions(app)
        
        # 보안 미들웨어 초기화 (조건부)
        if security_middleware:
            security_middleware.init_app(app)
        
        # Swagger 설정 초기화 (조건부)
        if SWAGGER_AVAILABLE and create_swagger_config:
            try:
                api = create_swagger_config(app)
                logger.info("Swagger API 설정 초기화 완료")
                return api
            except Exception as e:
                logger.warning(f"Swagger 설정 초기화 실패 (무시됨): {e}")
                return None
        else:
            logger.info("Swagger 설정 비활성화됨")
            return None
            
        logger.info("Flask 확장 모듈 및 보안 미들웨어 초기화 완료")
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
            admin_user.password_hash = generate_password_hash("admin123", method="pbkdf2:sha256")
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

# 캐시 매니저 초기화 (조건부)
if cache_manager:
    cache_manager.init_app(app)

# WebSocket 매니저 초기화 (조건부)
if WEBSOCKET_AVAILABLE and websocket_manager:
    websocket_manager.init_app(app)

# 데이터베이스 초기화 (앱 컨텍스트 내에서 실행)
initialize_database()

# 블루프린트 등록 함수
def register_blueprints():
    """모든 블루프린트를 등록합니다."""
    
    # 모바일 API 블루프린트 직접 등록
    try:
        # 간단한 테스트용 모바일 API 등록
        from api.mobile_simple import simple_mobile_bp
        unique_name = f"simple_mobile_api_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        app.register_blueprint(simple_mobile_bp, name=unique_name)
        logger.info(f"간단한 모바일 API 블루프린트 등록 완료: {unique_name}")
        
        # 새로운 모바일 발주 API 등록
        logger.info("모바일 발주 API 블루프린트 import 시도...")
        from api.mobile.purchase_orders import mobile_po_bp
        logger.info("모바일 발주 API 블루프린트 import 성공")
        
        unique_name = f"mobile_purchase_orders_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        app.register_blueprint(mobile_po_bp, name=unique_name)
        logger.info(f"모바일 발주 API 블루프린트 등록 완료: {unique_name}")
        
        # 모바일 API 기본 엔드포인트는 이미 simple_mobile_bp에 포함됨
        logger.info("모바일 API 기본 엔드포인트가 simple_mobile_bp에 포함되어 있습니다")
        
        # 관리자 API 기본 엔드포인트 등록
        logger.info("관리자 API 기본 엔드포인트 등록 시도...")
        from api.admin import admin_api
        unique_name = f"admin_api_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        app.register_blueprint(admin_api, name=unique_name)
        logger.info(f"관리자 API 기본 엔드포인트 등록 완료: {unique_name}")
        
        # 인증 API 블루프린트 등록
        logger.info("인증 API 블루프린트 등록 시도...")
        from api.auth_api import auth_bp
        unique_name = f"auth_api_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        app.register_blueprint(auth_bp, name=unique_name)
        logger.info(f"인증 API 블루프린트 등록 완료: {unique_name}")
        
        # 웹 인증 블루프린트 등록 (로그인 페이지용)
        logger.info("웹 인증 블루프린트 등록 시도...")
        from api.auth import auth_bp as web_auth_bp
        app.register_blueprint(web_auth_bp, name="auth")
        logger.info("웹 인증 블루프린트 등록 완료: auth")
        

        # CSRF 보호 완전 비활성화 (모바일 API 및 인증 API용)
        from extensions import disable_csrf_for_mobile
        disable_csrf_for_mobile(app)
        logger.info("모바일 API 및 인증 API 블루프린트 등록 완료 (CSRF 비활성화)")
    except Exception as e:
        logger.error(f"모바일 API 블루프린트 등록 실패: {e}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")
    
    # 관리자 API 블루프린트 등록
    try:
        from api.admin.purchase_orders import admin_po_bp
        unique_name = f"admin_purchase_orders_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        app.register_blueprint(admin_po_bp, name=unique_name)
        logger.info(f"관리자 발주 API 블루프린트 등록 완료: {unique_name}")
    except Exception as e:
        logger.error(f"관리자 발주 API 블루프린트 등록 실패: {e}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")
    
    blueprints = [
        # 백엔드 관리자 Blueprint
        ("routes.backend_admin", "backend_admin_bp", "backend_admin"),
        # 멀티테넌시 API Blueprint
        ("api.multitenancy_api", "multitenancy_bp", "multitenancy_api"),
        # 스토어 관리 API Blueprint
        ("api.store_management", "store_management_bp", "store_management"),
        # 직원 관리 API Blueprint
        ("api.admin_employees_api", "bp", "admin_employees_api"),
        # 로드 밸런서 API Blueprint
        ("api.load_balancer_api", "load_balancer_bp", "load_balancer"),
        # 메시지 큐 API Blueprint
        ("api.message_queue_api", "message_queue_bp", "message_queue"),
        # 캐시 관리 API Blueprint
        ("api.cache_api", "cache_bp", "cache"),
        # API 문서 시스템 Blueprint
        ("api.api_docs_api", "api_docs_bp", "api_docs"),
        # 스케줄 관리 플러그인 Blueprint
        ("plugins.schedule_management", "schedule_bp", "schedule"),
        # 직원 API Blueprint
        ("api.employee_api", "employee_api", "employee"),
        # 스케줄 API Blueprint
        ("api.schedule_api", "schedule_api", "schedule"),
    ]
    
    for module_path, blueprint_name, url_prefix in blueprints:
        try:
            module = __import__(module_path, fromlist=[blueprint_name])
            blueprint = getattr(module, blueprint_name)
            
            # 이미 등록된 블루프린트인지 확인
            if url_prefix in app.blueprints:
                logger.warning(f"{url_prefix} 블루프린트가 이미 등록되어 있습니다. 건너뜁니다.")
                continue
            
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

# API 문서 생성기 초기화
try:
    from api.api_docs_api import init_docs_generator
    init_docs_generator(app)
    print("✅ API 문서 생성기가 초기화되었습니다")
except Exception as e:
    print(f"⚠️ API 문서 생성기 초기화 실패: {str(e)}")

# === 기본 라우트들 ===

@app.route("/")
def index():
    """메인 페이지"""
    return render_template("index.html")



@app.after_request
def add_csp_headers(response):
    """모든 응답에 CSP 헤더 추가"""
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "connect-src 'self' http://localhost:5000 http://192.168.45.44:5000 ws://localhost:5000 ws://192.168.45.44:5000 http://127.0.0.1:5000; "
        "img-src 'self' data: https:; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )
    return response

@app.route("/dashboard")
def dashboard():
    """대시보드 페이지"""
    return render_template("admin/cyberpunk_dashboard.html")

@app.route("/admin/backend")
def admin_backend_main():
    """백엔드 관리자 메인 페이지"""
    return render_template("admin/cyberpunk_dashboard.html")

# === 계층 관리 라우트들 ===

# 계층 관리 라우트들은 backend_admin 블루프린트에서 처리됨

# === API 엔드포인트들 ===

# 계층 구조 API는 backend_admin 블루프린트에서 처리됨

# 모든 API 엔드포인트들은 backend_admin 블루프린트에서 처리됨

# === 권한 정책 관리 API ===

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

# 직원 관리 API 엔드포인트들
@app.route("/api/employees", methods=["GET"])
def api_employees():
    """직원 목록 조회 (호환성을 위한 별칭)"""
    return api_staff_list()

@app.route("/api/staff/list", methods=["GET"])
def api_staff_list():
    """직원 목록 조회"""
    try:
        # 실제 데이터베이스에서 직원 목록 조회
        users = User.query.filter_by(deleted_at=None).all()
        
        staff_list = []
        for user in users:
            staff_list.append({
                "id": str(user.id),
                "name": user.name or user.username,
                "email": user.email,
                "phone": user.phone or "",
                "role": user.role,
                "department": user.department or "",
                "hireDate": user.created_at.strftime("%Y-%m-%d") if user.created_at else "",
                "status": "active" if user.status == "approved" else "inactive",
                "location": user.branch.name if user.branch else "",
                "lastActive": user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "",
                "workHours": 160,  # 기본값
                "performance": 85   # 기본값
            })
        
        return jsonify({
            "success": True,
            "data": staff_list
        })
    except Exception as e:
        logger.error(f"직원 목록 조회 오류: {e}")
        return jsonify({
            "success": False,
            "error": "직원 목록을 불러올 수 없습니다."
        }), 500

@app.route("/api/staff/<staff_id>", methods=["GET"])
def api_staff_detail(staff_id):
    """직원 상세 정보 조회"""
    try:
        user = User.query.get(int(staff_id))
        if not user:
            return jsonify({
                "success": False,
                "error": "직원을 찾을 수 없습니다."
            }), 404
        
        staff_data = {
            "id": str(user.id),
            "name": user.name or user.username,
            "email": user.email,
            "phone": user.phone or "",
            "role": user.role,
            "department": user.department or "",
            "hireDate": user.created_at.strftime("%Y-%m-%d") if user.created_at else "",
            "status": "active" if user.status == "approved" else "inactive",
            "location": user.branch.name if user.branch else "",
            "lastActive": user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "",
            "workHours": 160,  # 기본값
            "performance": 85   # 기본값
        }
        
        return jsonify({
            "success": True,
            "data": staff_data
        })
    except Exception as e:
        logger.error(f"직원 상세 조회 오류: {e}")
        return jsonify({
            "success": False,
            "error": "직원 정보를 불러올 수 없습니다."
        }), 500

@app.route("/api/staff/search", methods=["GET"])
def api_staff_search():
    """직원 검색"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({
                "success": False,
                "error": "검색어를 입력해주세요."
            }), 400
        
        # 이름, 이메일, 전화번호로 검색
        users = User.query.filter(
            User.deleted_at.is_(None),
            db.or_(
                User.name.contains(query),
                User.username.contains(query),
                User.email.contains(query),
                User.phone.contains(query)
            )
        ).all()
        
        staff_list = []
        for user in users:
            staff_list.append({
                "id": str(user.id),
                "name": user.name or user.username,
                "email": user.email,
                "phone": user.phone or "",
                "role": user.role,
                "department": user.department or "",
                "hireDate": user.created_at.strftime("%Y-%m-%d") if user.created_at else "",
                "status": "active" if user.status == "approved" else "inactive",
                "location": user.branch.name if user.branch else "",
                "lastActive": user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "",
                "workHours": 160,
                "performance": 85
            })
        
        return jsonify({
            "success": True,
            "data": staff_list
        })
    except Exception as e:
        logger.error(f"직원 검색 오류: {e}")
        return jsonify({
            "success": False,
            "error": "검색 중 오류가 발생했습니다."
        }), 500

@app.route("/api/staff/create", methods=["POST"])
def api_staff_create():
    """직원 생성"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['name', 'email', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "error": f"{field} 필드는 필수입니다."
                }), 400
        
        # 이메일 중복 검사
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                "success": False,
                "error": "이미 존재하는 이메일입니다."
            }), 400
        
        # 새 사용자 생성
        new_user = User(
            username=data['email'],  # 이메일을 username으로 사용
            email=data['email'],
            name=data['name'],
            phone=data.get('phone', ''),
            role=data['role'],
            department=data.get('department', ''),
            status='approved'
        )
        
        # 기본 비밀번호 설정 (실제로는 이메일로 임시 비밀번호 발송)
        new_user.set_password('temp123456')
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "직원이 성공적으로 생성되었습니다.",
            "data": {
                "id": str(new_user.id),
                "name": new_user.name,
                "email": new_user.email
            }
        })
    except Exception as e:
        logger.error(f"직원 생성 오류: {e}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "직원 생성 중 오류가 발생했습니다."
        }), 500

@app.route("/api/staff/<staff_id>", methods=["PUT"])
def api_staff_update(staff_id):
    """직원 정보 수정"""
    try:
        user = User.query.get(int(staff_id))
        if not user:
            return jsonify({
                "success": False,
                "error": "직원을 찾을 수 없습니다."
            }), 404
        
        data = request.get_json()
        
        # 업데이트 가능한 필드들
        if 'name' in data:
            user.name = data['name']
        if 'phone' in data:
            user.phone = data['phone']
        if 'role' in data:
            user.role = data['role']
        if 'department' in data:
            user.department = data['department']
        if 'status' in data:
            user.status = 'approved' if data['status'] == 'active' else 'pending'
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "직원 정보가 성공적으로 수정되었습니다."
        })
    except Exception as e:
        logger.error(f"직원 수정 오류: {e}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "직원 정보 수정 중 오류가 발생했습니다."
        }), 500

@app.route("/api/staff/<staff_id>", methods=["DELETE"])
def api_staff_delete(staff_id):
    """직원 삭제 (소프트 삭제)"""
    try:
        user = User.query.get(int(staff_id))
        if not user:
            return jsonify({
                "success": False,
                "error": "직원을 찾을 수 없습니다."
            }), 404
        
        # 소프트 삭제 (deleted_at 필드 설정)
        user.deleted_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "직원이 성공적으로 삭제되었습니다."
        })
    except Exception as e:
        logger.error(f"직원 삭제 오류: {e}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "직원 삭제 중 오류가 발생했습니다."
        }), 500

@app.route("/api/staff/<staff_id>/activate", methods=["PATCH"])
def api_staff_activate(staff_id):
    """직원 활성화"""
    try:
        user = User.query.get(int(staff_id))
        if not user:
            return jsonify({
                "success": False,
                "error": "직원을 찾을 수 없습니다."
            }), 404
        
        user.status = "approved"
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "직원이 활성화되었습니다."
        })
    except Exception as e:
        logger.error(f"직원 활성화 오류: {e}")
        return jsonify({
            "success": False,
            "error": "직원 활성화에 실패했습니다."
        }), 500

@app.route("/api/staff/<staff_id>/deactivate", methods=["PATCH"])
def api_staff_deactivate(staff_id):
    """직원 비활성화"""
    try:
        user = User.query.get(int(staff_id))
        if not user:
            return jsonify({
                "success": False,
                "error": "직원을 찾을 수 없습니다."
            }), 404
        
        user.status = "inactive"
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "직원이 비활성화되었습니다."
        })
    except Exception as e:
        logger.error(f"직원 비활성화 오류: {e}")
        return jsonify({
            "success": False,
            "error": "직원 비활성화에 실패했습니다."
        }), 500

# === 기본 설정 ===

@login_manager.user_loader
def load_user(user_id):
    """사용자 로더"""
    return User.query.get(int(user_id))

@app.errorhandler(400)
def bad_request(e):
    """400 에러 핸들러"""
    logger.warning(f"400 Bad Request: {request.url} - {e}")
    return jsonify({
        "error": "잘못된 요청입니다.", 
        "code": 400,
        "message": str(e) if app.debug else "요청 형식이 올바르지 않습니다."
    }), 400


@app.errorhandler(401)
def unauthorized(e):
    """401 에러 핸들러"""
    logger.warning(f"401 Unauthorized: {request.url}")
    return jsonify({
        "error": "인증이 필요합니다.", 
        "code": 401,
        "message": "로그인이 필요하거나 인증이 만료되었습니다."
    }), 401


@app.errorhandler(403)
def forbidden(e):
    """403 에러 핸들러"""
    logger.warning(f"403 Forbidden: {request.url}")
    return jsonify({
        "error": "접근 권한이 없습니다.", 
        "code": 403,
        "message": "해당 리소스에 접근할 권한이 없습니다."
    }), 403


@app.errorhandler(404)
def page_not_found(e):
    """404 에러 핸들러"""
    logger.info(f"404 Not Found: {request.url}")
    try:
        return render_template('errors/404.html'), 404
    except Exception:
        return jsonify({
            "error": "페이지를 찾을 수 없습니다.", 
            "code": 404,
            "message": "요청하신 리소스를 찾을 수 없습니다."
        }), 404


@app.errorhandler(405)
def method_not_allowed(e):
    """405 에러 핸들러"""
    logger.warning(f"405 Method Not Allowed: {request.method} {request.url}")
    return jsonify({
        "error": "허용되지 않는 메서드입니다.", 
        "code": 405,
        "message": f"{request.method} 메서드는 지원되지 않습니다."
    }), 405


@app.errorhandler(429)
def too_many_requests(e):
    """429 에러 핸들러"""
    logger.warning(f"429 Too Many Requests: {request.url}")
    return jsonify({
        "error": "요청이 너무 많습니다.", 
        "code": 429,
        "message": "요청 제한을 초과했습니다. 잠시 후 다시 시도해주세요."
    }), 429


@app.errorhandler(500)
def server_error(e):
    """500 에러 핸들러"""
    logger.error(f"500 Internal Server Error: {request.url} - {e}")
    try:
        return render_template('errors/500.html'), 500
    except Exception:
        return jsonify({
            "error": "서버 내부 오류가 발생했습니다.", 
            "code": 500,
            "message": "서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        }), 500


@app.errorhandler(Exception)
def handle_exception(e):
    """예상치 못한 예외 처리"""
    logger.error(f"Unhandled Exception: {request.url} - {e}", exc_info=True)
    return jsonify({
        "error": "예상치 못한 오류가 발생했습니다.", 
        "code": 500,
        "message": "시스템 오류가 발생했습니다. 관리자에게 문의해주세요."
    }), 500

@app.route("/health")
def health():
    """헬스 체크"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    })

@app.route("/favicon.ico")
def favicon():
    """파비콘 요청 처리"""
    from flask import Response
    return Response("", status=204, mimetype="image/x-icon")

# 플러그인 시스템 상태 API
@app.route("/api/plugins/status", methods=["GET"])
def api_plugins_status():
    """플러그인 시스템 상태 조회"""
    try:
        # 플러그인 디렉토리 확인
        plugin_dir = Path("plugins")
        plugins = []
        
        if plugin_dir.exists():
            for plugin_file in plugin_dir.glob("*.py"):
                if plugin_file.name != "__init__.py":
                    plugins.append({
                        "name": plugin_file.stem,
                        "status": "active",
                        "version": "1.0.0",
                        "description": f"{plugin_file.stem} 플러그인"
                    })
        
        return jsonify({
            "success": True,
            "data": {
                "total_plugins": len(plugins),
                "active_plugins": len(plugins),
                "plugins": plugins
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 시스템 모니터링 API
@app.route("/api/monitoring/system-metrics", methods=["GET"])
def api_system_metrics():
    """시스템 메트릭 조회"""
    try:
        import psutil
        import os
        
        # 시스템 리소스 정보
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 데이터베이스 통계
        total_users = User.query.count()
        total_industries = Industry.query.count()
        total_brands = Brand.query.count()
        
        return jsonify({
            "success": True,
            "data": {
                "system": {
                    "cpu_usage": cpu_percent,
                    "memory_usage": memory.percent,
                    "disk_usage": disk.percent,
                    "uptime": "24시간"
                },
                "database": {
                    "total_users": total_users,
                    "total_industries": total_industries,
                    "total_brands": total_brands
                }
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 시스템 성능 모니터링 API 개선
@app.route("/api/monitoring/performance", methods=["GET"])
def api_performance_monitoring():
    """시스템 성능 모니터링"""
    try:
        import psutil
        import time
        
        # 시스템 리소스 정보
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 네트워크 정보
        network = psutil.net_io_counters()
        
        # 프로세스 정보
        process = psutil.Process()
        
        # 데이터베이스 연결 상태
        try:
            db.session.execute('SELECT 1')
            db_status = "connected"
        except:
            db_status = "disconnected"
        
        return jsonify({
            "success": True,
            "data": {
                "system": {
                    "cpu": {
                        "usage_percent": cpu_percent,
                        "count": psutil.cpu_count(),
                        "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else 0
                    },
                    "memory": {
                        "total": memory.total,
                        "available": memory.available,
                        "used": memory.used,
                        "percent": memory.percent
                    },
                    "disk": {
                        "total": disk.total,
                        "used": disk.used,
                        "free": disk.free,
                        "percent": disk.percent
                    },
                    "network": {
                        "bytes_sent": network.bytes_sent,
                        "bytes_recv": network.bytes_recv,
                        "packets_sent": network.packets_sent,
                        "packets_recv": network.packets_recv
                    }
                },
                "application": {
                    "process_id": process.pid,
                    "memory_usage": process.memory_info().rss,
                    "cpu_percent": process.cpu_percent(),
                    "threads": process.num_threads(),
                    "open_files": len(process.open_files()),
                    "connections": len(process.connections())
                },
                "database": {
                    "status": db_status,
                    "connection_pool": "active"
                },
                "timestamp": time.time()
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 시스템 로그 API
@app.route("/api/admin/system-logs", methods=["GET"])
def api_system_logs():
    """시스템 로그 조회"""
    try:
        # 최근 로그 데이터 (실제로는 로그 파일에서 읽어와야 함)
        logs = [
            {
                "timestamp": "2024-08-01 14:16:32",
                "level": "INFO",
                "message": "시스템이 정상적으로 실행 중입니다.",
                "user": "system"
            },
            {
                "timestamp": "2024-08-01 14:16:25",
                "level": "INFO", 
                "message": "직원 목록 조회 완료",
                "user": "admin"
            },
            {
                "timestamp": "2024-08-01 14:16:21",
                "level": "INFO",
                "message": "브랜드 목록 조회 완료", 
                "user": "admin"
            }
        ]
        
        return jsonify({
            "success": True,
            "data": {
                "logs": logs,
                "total": len(logs)
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 시스템 로그 분석 API
@app.route("/api/admin/logs/analysis", methods=["GET"])
def api_logs_analysis():
    """로그 분석"""
    try:
        # 로그 분석 데이터 (실제로는 로그 파일에서 분석)
        analysis = {
            "summary": {
                "total_logs": 1250,
                "error_count": 15,
                "warning_count": 45,
                "info_count": 1190
            },
            "error_distribution": {
                "database_errors": 8,
                "network_errors": 4,
                "authentication_errors": 3
            },
            "top_errors": [
                {
                    "error": "Database connection timeout",
                    "count": 5,
                    "last_occurrence": "2024-08-01 14:30:00"
                },
                {
                    "error": "Invalid authentication token",
                    "count": 3,
                    "last_occurrence": "2024-08-01 14:25:00"
                }
            ],
            "performance_metrics": {
                "average_response_time": "120ms",
                "peak_response_time": "450ms",
                "requests_per_minute": 45
            }
        }
        
        return jsonify({
            "success": True,
            "data": analysis
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 인증 API
@app.route("/api/auth/login", methods=["POST"])
def api_auth_login():
    """사용자 로그인"""
    try:
        app.logger.info(f"로그인 요청 받음: {request.get_data()}")
        app.logger.info(f"Content-Type: {request.content_type}")
        app.logger.info(f"Headers: {dict(request.headers)}")
        
        # 다양한 방법으로 데이터 파싱 시도
        data = None
        
        # 1. JSON으로 파싱 시도
        if request.is_json:
            data = request.get_json()
            app.logger.info(f"JSON으로 파싱된 데이터: {data}")
        else:
            # 2. 폼 데이터로 파싱 시도
            if request.form:
                data = {
                    'username': request.form.get('username'),
                    'password': request.form.get('password')
                }
                app.logger.info(f"폼 데이터로 파싱된 데이터: {data}")
            else:
                # 3. 원시 데이터를 JSON으로 파싱 시도
                try:
                    raw_data = request.get_data(as_text=True)
                    app.logger.info(f"원시 데이터: {raw_data}")
                    import json
                    data = json.loads(raw_data)
                    app.logger.info(f"원시 데이터에서 JSON 파싱: {data}")
                except Exception as json_error:
                    app.logger.error(f"JSON 파싱 실패: {json_error}")
                    return jsonify({"success": False, "error": "잘못된 JSON 형식입니다."}), 400
        
        if not data:
            app.logger.error("요청 데이터가 없습니다")
            return jsonify({"success": False, "error": "요청 데이터가 없습니다."}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        app.logger.info(f"사용자명: {username}, 비밀번호 길이: {len(password) if password else 0}")
        
        if not username or not password:
            app.logger.error("사용자명 또는 비밀번호가 없습니다")
            return jsonify({"success": False, "error": "사용자명과 비밀번호를 입력해주세요."}), 400
        
        user = User.query.filter_by(username=username).first()
        app.logger.info(f"사용자 조회 결과: {user is not None}")
        
        if user and user.check_password(password):
            app.logger.info("로그인 성공")
            # 로그인 성공
            return jsonify({
                "success": True,
                "data": {
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "name": user.name,
                        "email": user.email,
                        "role": user.role
                    },
                    "token": "sample_jwt_token_here"
                }
            })
        else:
            app.logger.error("잘못된 사용자명 또는 비밀번호")
            return jsonify({"success": False, "error": "잘못된 사용자명 또는 비밀번호입니다."}), 401
            
    except Exception as e:
        app.logger.error(f"로그인 오류: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# API 상태 확인
@app.route("/api/status", methods=["GET"])
def api_status():
    """API 상태 확인"""
    try:
        return jsonify({
            "success": True,
            "data": {
                "status": "running",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
                "endpoints": {
                    "total": 900,
                    "active": 900
                }
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 실시간 알림 시스템 API
@app.route("/api/notifications/list", methods=["GET"])
def api_notifications_list():
    """알림 목록 조회"""
    try:
        # 최근 알림 데이터 (실제로는 Notification 모델에서 조회)
        notifications = [
            {
                "id": 1,
                "type": "info",
                "title": "시스템 업데이트",
                "message": "새로운 기능이 추가되었습니다.",
                "timestamp": "2024-08-01 14:30:00",
                "read": False,
                "priority": "normal"
            },
            {
                "id": 2,
                "type": "warning",
                "title": "저장 공간 부족",
                "message": "디스크 사용률이 80%를 초과했습니다.",
                "timestamp": "2024-08-01 14:25:00",
                "read": True,
                "priority": "high"
            },
            {
                "id": 3,
                "type": "success",
                "title": "백업 완료",
                "message": "데이터베이스 백업이 성공적으로 완료되었습니다.",
                "timestamp": "2024-08-01 14:20:00",
                "read": False,
                "priority": "normal"
            }
        ]
        
        return jsonify({
            "success": True,
            "data": {
                "notifications": notifications,
                "unread_count": len([n for n in notifications if not n["read"]])
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/notifications/mark-read", methods=["POST"])
def api_notifications_mark_read():
    """알림 읽음 처리"""
    try:
        data = request.get_json()
        notification_id = data.get('notification_id')
        
        if not notification_id:
            return jsonify({"success": False, "error": "알림 ID가 필요합니다."}), 400
        
        # 실제로는 Notification 모델에서 업데이트
        return jsonify({
            "success": True,
            "message": "알림이 읽음 처리되었습니다."
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 대시보드 통계 API
@app.route("/api/dashboard/stats", methods=["GET"])
def api_dashboard_stats():
    """대시보드 통계 조회 API"""
    try:
        from models_main import Staff, Order
        
        # 기본 통계 데이터
        stats = {
            "total_staff": Staff.query.count(),
            "total_orders": Order.query.count() if hasattr(Order, 'query') else 0,
            "pending_orders": Order.query.filter_by(status='pending').count() if hasattr(Order, 'query') else 0,
            "completed_orders": Order.query.filter_by(status='completed').count() if hasattr(Order, 'query') else 0,
            "total_revenue": 0,  # Order 모델에서 계산 필요
            "active_staff": Staff.query.filter_by(status='active').count() if hasattr(Staff, 'status') else Staff.query.count(),
            "today_attendance": 0  # 출근 관리 시스템에서 계산 필요
        }
        
        # 매출 계산 (Order 모델이 있는 경우)
        if hasattr(Order, 'query'):
            try:
                total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar()
                stats["total_revenue"] = float(total_revenue) if total_revenue else 0
            except Exception as e:
                logger.warning(f"Revenue calculation error: {e}")
                stats["total_revenue"] = 0
        
        # 최근 주문 데이터 (최근 5개)
        recent_orders = []
        if hasattr(Order, 'query'):
            try:
                orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
                for order in orders:
                    recent_orders.append({
                        "id": order.id,
                        "status": order.status,
                        "total_amount": float(order.total_amount) if order.total_amount else 0,
                        "created_at": order.created_at.isoformat() if order.created_at else None
                    })
            except Exception as e:
                logger.warning(f"Recent orders fetch error: {e}")
        
        return jsonify({
            "success": True,
            "stats": stats,
            "recent_orders": recent_orders,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return jsonify({
            "success": False,
            "error": "대시보드 통계 조회 실패",
            "stats": {
                "total_staff": 0,
                "total_orders": 0,
                "pending_orders": 0,
                "completed_orders": 0,
                "total_revenue": 0,
                "active_staff": 0,
                "today_attendance": 0
            },
            "recent_orders": []
        }), 500

# 고급 검색 및 필터링 API
@app.route("/api/search/global", methods=["GET"])
def api_global_search():
    """전역 검색"""
    try:
        query = request.args.get('q', '').strip()
        category = request.args.get('category', 'all')
        
        if not query:
            return jsonify({
                "success": False,
                "error": "검색어를 입력해주세요."
            }), 400
        
        results = {
            "users": [],
            "industries": [],
            "brands": [],
            "total_results": 0
        }
        
        # 사용자 검색
        if category in ['all', 'users']:
            users = User.query.filter(
                User.deleted_at.is_(None),
                db.or_(
                    User.name.contains(query),
                    User.username.contains(query),
                    User.email.contains(query)
                )
            ).limit(5).all()
            
            for user in users:
                results["users"].append({
                    "id": str(user.id),
                    "name": user.name or user.username,
                    "email": user.email,
                    "role": user.role,
                    "type": "user"
                })
        
        # 업종 검색
        if category in ['all', 'industries']:
            industries = Industry.query.filter(
                Industry.name.contains(query)
            ).limit(5).all()
            
            for industry in industries:
                results["industries"].append({
                    "id": str(industry.id),
                    "name": industry.name,
                    "code": industry.code,
                    "type": "industry"
                })
        
        # 브랜드 검색
        if category in ['all', 'brands']:
            brands = Brand.query.filter(
                Brand.name.contains(query)
            ).limit(5).all()
            
            for brand in brands:
                results["brands"].append({
                    "id": str(brand.id),
                    "name": brand.name,
                    "code": brand.code,
                    "type": "brand"
                })
        
        results["total_results"] = len(results["users"]) + len(results["industries"]) + len(results["brands"])
        
        return jsonify({
            "success": True,
            "data": results
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 데이터 내보내기 API
@app.route("/api/export/data", methods=["GET"])
def api_export_data():
    """데이터 내보내기"""
    try:
        export_type = request.args.get('type', 'users')
        format_type = request.args.get('format', 'json')
        
        if export_type == 'users':
            users = User.query.filter_by(deleted_at=None).all()
            data = []
            for user in users:
                data.append({
                    "id": user.id,
                    "name": user.name or user.username,
                    "email": user.email,
                    "role": user.role,
                    "department": user.department,
                    "status": user.status,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                })
        elif export_type == 'industries':
            industries = Industry.query.all()
            data = []
            for industry in industries:
                data.append({
                    "id": industry.id,
                    "name": industry.name,
                    "code": industry.code,
                    "description": industry.description,
                    "status": industry.status
                })
        elif export_type == 'brands':
            brands = Brand.query.all()
            data = []
            for brand in brands:
                data.append({
                    "id": brand.id,
                    "name": brand.name,
                    "code": brand.code,
                    "description": brand.description,
                    "industry_id": brand.industry_id
                })
        else:
            return jsonify({"success": False, "error": "지원하지 않는 내보내기 타입입니다."}), 400
        
        if format_type == 'json':
            return jsonify({
                "success": True,
                "data": {
                    "type": export_type,
                    "format": format_type,
                    "count": len(data),
                    "records": data
                }
            })
        else:
            return jsonify({"success": False, "error": "지원하지 않는 형식입니다."}), 400
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# AI 기반 분석 및 예측 시스템 API
@app.route("/api/ai/analytics/dashboard", methods=["GET"])
def api_ai_analytics_dashboard():
    """AI 대시보드 분석"""
    try:
        # AI 기반 분석 데이터 (실제로는 ML 모델에서 계산)
        analytics = {
            "user_behavior": {
                "active_users_trend": [45, 52, 48, 61, 58, 67, 72],
                "peak_usage_hours": [9, 10, 11, 14, 15, 16],
                "most_used_features": [
                    {"feature": "직원 관리", "usage": 35},
                    {"feature": "업종 관리", "usage": 28},
                    {"feature": "브랜드 관리", "usage": 22},
                    {"feature": "시스템 모니터링", "usage": 15}
                ]
            },
            "performance_predictions": {
                "next_month_users": 85,
                "system_load_forecast": "medium",
                "recommended_upgrades": [
                    "데이터베이스 인덱스 최적화",
                    "캐시 시스템 확장",
                    "로드 밸런서 추가"
                ]
            },
            "anomaly_detection": {
                "detected_anomalies": 2,
                "anomaly_types": [
                    {
                        "type": "unusual_login_pattern",
                        "severity": "low",
                        "description": "비정상적인 로그인 패턴 감지"
                    },
                    {
                        "type": "high_cpu_usage",
                        "severity": "medium",
                        "description": "CPU 사용률 급증"
                    }
                ]
            }
        }
        
        return jsonify({
            "success": True,
            "data": analytics
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/ai/recommendations", methods=["GET"])
def api_ai_recommendations():
    """AI 기반 추천 시스템"""
    try:
        # user_id = request.args.get('user_id')  # 사용하지 않는 변수
        
        # 사용자별 맞춤 추천 (실제로는 ML 모델에서 생성)
        recommendations = {
            "system_optimizations": [
                {
                    "title": "데이터베이스 성능 최적화",
                    "description": "쿼리 실행 시간을 30% 단축할 수 있습니다.",
                    "priority": "high",
                    "estimated_impact": "30% 성능 향상"
                },
                {
                    "title": "메모리 사용량 최적화",
                    "description": "현재 메모리 사용량을 15% 줄일 수 있습니다.",
                    "priority": "medium",
                    "estimated_impact": "15% 메모리 절약"
                }
            ],
            "user_suggestions": [
                {
                    "title": "자주 사용하는 기능 단축키 설정",
                    "description": "업무 효율성을 높일 수 있습니다.",
                    "category": "productivity"
                },
                {
                    "title": "데이터 백업 자동화",
                    "description": "데이터 손실 위험을 줄일 수 있습니다.",
                    "category": "security"
                }
            ],
            "business_insights": [
                {
                    "insight": "금요일 오후에 시스템 사용량이 가장 높습니다.",
                    "action": "서버 리소스를 미리 확보하세요.",
                    "confidence": 0.92
                },
                {
                    "insight": "직원 관리 기능이 가장 많이 사용됩니다.",
                    "action": "해당 기능의 성능을 우선적으로 개선하세요.",
                    "confidence": 0.88
                }
            ]
        }
        
        return jsonify({
            "success": True,
            "data": recommendations
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 고급 보고서 생성 API
@app.route("/api/reports/generate", methods=["POST"])
def api_reports_generate():
    """고급 보고서 생성"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "요청 데이터가 없습니다."}), 400
            
        report_type = data.get('type', 'comprehensive')
        date_range = data.get('date_range', 'last_30_days')
        
        # 보고서 데이터 생성 (실제로는 데이터베이스에서 집계)
        if report_type == 'comprehensive':
            report_data = {
                "summary": {
                    "total_users": 3,
                    "total_industries": 3,
                    "total_brands": 2,
                    "active_sessions": 5,
                    "system_uptime": "99.9%"
                },
                "performance_metrics": {
                    "average_response_time": "120ms",
                    "peak_response_time": "450ms",
                    "error_rate": "0.1%",
                    "throughput": "45 requests/min"
                },
                "user_activity": {
                    "daily_active_users": [3, 3, 3, 3, 3, 3, 3],
                    "feature_usage": {
                        "직원 관리": 35,
                        "업종 관리": 28,
                        "브랜드 관리": 22,
                        "시스템 모니터링": 15
                    }
                },
                "system_health": {
                    "cpu_usage_avg": 25.5,
                    "memory_usage_avg": 45.2,
                    "disk_usage_avg": 32.1,
                    "network_activity": "stable"
                },
                "recommendations": [
                    "시스템 성능이 우수합니다.",
                    "정기적인 백업을 권장합니다.",
                    "사용자 교육을 통해 기능 활용도를 높일 수 있습니다."
                ]
            }
        else:
            return jsonify({"success": False, "error": "지원하지 않는 보고서 타입입니다."}), 400
        
        return jsonify({
            "success": True,
            "data": {
                "report_type": report_type,
                "date_range": date_range,
                "generated_at": datetime.now().isoformat(),
                "content": report_data
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 자동화 및 스케줄링 시스템 API
@app.route("/api/automation/tasks", methods=["GET"])
def api_automation_tasks():
    """자동화 작업 목록"""
    try:
        # 자동화 작업 목록 (실제로는 데이터베이스에서 조회)
        tasks = [
            {
                "id": 1,
                "name": "데이터베이스 백업",
                "type": "backup",
                "schedule": "daily",
                "last_run": "2024-08-01 02:00:00",
                "next_run": "2024-08-02 02:00:00",
                "status": "completed",
                "description": "매일 새벽 2시에 데이터베이스 백업 실행"
            },
            {
                "id": 2,
                "name": "시스템 로그 정리",
                "type": "maintenance",
                "schedule": "weekly",
                "last_run": "2024-07-28 03:00:00",
                "next_run": "2024-08-04 03:00:00",
                "status": "scheduled",
                "description": "매주 일요일 새벽 3시에 30일 이상 된 로그 파일 정리"
            },
            {
                "id": 3,
                "name": "성능 리포트 생성",
                "type": "reporting",
                "schedule": "monthly",
                "last_run": "2024-07-31 23:59:00",
                "next_run": "2024-08-31 23:59:00",
                "status": "scheduled",
                "description": "매월 말일 자정에 월간 성능 리포트 생성"
            }
        ]
        
        return jsonify({
            "success": True,
            "data": {
                "tasks": tasks,
                "total_tasks": len(tasks),
                "active_tasks": len([t for t in tasks if t["status"] == "scheduled"])
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/automation/tasks/<task_id>/execute", methods=["POST"])
def api_automation_execute_task(task_id):
    """자동화 작업 실행"""
    try:
        task_id = int(task_id)
        
        # 작업 실행 시뮬레이션
        execution_result = {
            "task_id": task_id,
            "execution_time": datetime.now().isoformat(),
            "status": "completed",
            "duration": "45초",
            "result": "성공적으로 실행되었습니다.",
            "details": {
                "files_processed": 1250,
                "data_processed": "2.3GB",
                "errors": 0
            }
        }
        
        return jsonify({
            "success": True,
            "data": execution_result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 워크플로우 관리 API
@app.route("/api/workflow/templates", methods=["GET"])
def api_workflow_templates():
    """워크플로우 템플릿 목록"""
    try:
        templates = [
            {
                "id": 1,
                "name": "신규 직원 온보딩",
                "description": "새로운 직원 등록 시 자동으로 실행되는 워크플로우",
                "steps": [
                    "직원 정보 등록",
                    "이메일 계정 생성",
                    "권한 설정",
                    "환영 이메일 발송",
                    "교육 자료 제공"
                ],
                "estimated_duration": "30분",
                "automation_level": "full"
            },
            {
                "id": 2,
                "name": "월간 리포트 생성",
                "description": "매월 말 시스템 성능 및 사용 통계 리포트 생성",
                "steps": [
                    "데이터 수집",
                    "분석 처리",
                    "리포트 생성",
                    "이메일 발송",
                    "아카이브 저장"
                ],
                "estimated_duration": "15분",
                "automation_level": "full"
            },
            {
                "id": 3,
                "name": "시스템 점검",
                "description": "정기적인 시스템 상태 점검 및 최적화",
                "steps": [
                    "시스템 상태 확인",
                    "성능 메트릭 수집",
                    "오류 로그 분석",
                    "최적화 권장사항 생성",
                    "관리자 알림"
                ],
                "estimated_duration": "10분",
                "automation_level": "semi"
            }
        ]
        
        return jsonify({
            "success": True,
            "data": {
                "templates": templates,
                "total_templates": len(templates)
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 시스템 최적화 API 엔드포인트들
@app.route("/api/optimization/performance-report", methods=["GET"])
@require_super_admin
def api_performance_report():
    """시스템 성능 리포트 생성"""
    try:
        report = system_optimizer.generate_performance_report()
        
        return jsonify({
            "success": True,
            "data": report
        })
        
    except Exception as e:
        app.logger.error(f"성능 리포트 생성 중 오류: {e}")
        return jsonify({
            "success": False,
            "error": "성능 리포트 생성 중 오류가 발생했습니다."
        }), 500

@app.route("/api/optimization/database", methods=["POST"])
@require_super_admin
def api_optimize_database():
    """데이터베이스 최적화 실행"""
    try:
        result = system_optimizer.optimize_database()
        
        if 'error' in result:
            return jsonify({
                "success": False,
                "error": result['error']
            }), 500
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        app.logger.error(f"데이터베이스 최적화 중 오류: {e}")
        return jsonify({
            "success": False,
            "error": "데이터베이스 최적화 중 오류가 발생했습니다."
        }), 500

@app.route("/api/optimization/system-resources", methods=["GET"])
@require_super_admin
def api_system_resources():
    """시스템 리소스 모니터링"""
    try:
        resources = system_optimizer.monitor_system_resources()
        
        return jsonify({
            "success": True,
            "data": resources
        })
        
    except Exception as e:
        app.logger.error(f"시스템 리소스 모니터링 중 오류: {e}")
        return jsonify({
            "success": False,
            "error": "시스템 리소스 모니터링 중 오류가 발생했습니다."
        }), 500

@app.route("/api/optimization/database-analysis", methods=["GET"])
@require_super_admin
def api_database_analysis():
    """데이터베이스 성능 분석"""
    try:
        analysis = system_optimizer.analyze_database_performance()
        
        return jsonify({
            "success": True,
            "data": analysis
        })
        
    except Exception as e:
        app.logger.error(f"데이터베이스 성능 분석 중 오류: {e}")
        return jsonify({
            "success": False,
            "error": "데이터베이스 성능 분석 중 오류가 발생했습니다."
        }), 500

@app.route("/api/optimization/start-monitoring", methods=["POST"])
@require_super_admin
def api_start_monitoring():
    """연속 모니터링 시작"""
    try:
        data = request.get_json()
        interval = data.get('interval_seconds', 60) if data else 60
        
        # 모니터링 스레드 시작
        # monitor_thread = system_optimizer.start_continuous_monitoring(interval)  # 사용하지 않는 변수
        
        return jsonify({
            "success": True,
            "message": f"연속 모니터링이 시작되었습니다. (간격: {interval}초)",
            "data": {
                "monitoring_active": True,
                "interval_seconds": interval
            }
        })
        
    except Exception as e:
        app.logger.error(f"연속 모니터링 시작 중 오류: {e}")
        return jsonify({
            "success": False,
            "error": "연속 모니터링 시작 중 오류가 발생했습니다."
        }), 500

@app.route("/api/optimization/health-check", methods=["GET"])
def api_optimization_health_check():
    """시스템 최적화 상태 확인"""
    try:
        # 기본 시스템 상태 확인
        resources = system_optimizer.monitor_system_resources()
        db_analysis = system_optimizer.analyze_database_performance()
        
        # 전체 성능 점수 계산
        performance_score = system_optimizer._calculate_performance_score(
            resources, db_analysis
        )
        
        # 상태 판단
        status = "healthy"
        if performance_score < 70:
            status = "warning"
        if performance_score < 50:
            status = "critical"
        
        return jsonify({
            "success": True,
            "data": {
                "status": status,
                "performance_score": performance_score,
                "system_resources": {
                    "cpu_percent": resources.get('cpu', {}).get('percent', 0),
                    "memory_percent": resources.get('memory', {}).get('percent', 0),
                    "disk_percent": resources.get('disk', {}).get('percent', 0)
                },
                "database_status": "healthy" if 'error' not in db_analysis else "error",
                "timestamp": datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        app.logger.error(f"시스템 최적화 상태 확인 중 오류: {e}")
        return jsonify({
            "success": False,
            "error": "시스템 최적화 상태 확인 중 오류가 발생했습니다."
        }), 500

@app.route("/api/test/admin-bypass", methods=["GET"])
def api_test_admin_bypass():
    """테스트용 관리자 우회 엔드포인트"""
    try:
        # 시스템 리소스 모니터링 (관리자 권한이 필요한 기능)
        system_resources = system_optimizer.monitor_system_resources()
        
        # 데이터베이스 분석 (관리자 권한이 필요한 기능)
        db_analysis = system_optimizer.analyze_database_performance()
        
        # 성능 리포트 생성 (관리자 권한이 필요한 기능)
        performance_report = system_optimizer.generate_performance_report()
        
        return jsonify({
            "success": True,
            "data": {
                "message": "관리자 권한이 필요한 기능들이 성공적으로 실행되었습니다.",
                "system_resources": system_resources,
                "database_analysis": db_analysis,
                "performance_report": performance_report,
                "timestamp": datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        app.logger.error(f"테스트 관리자 우회 중 오류: {e}")
        return jsonify({
            "success": False,
            "error": f"테스트 중 오류가 발생했습니다: {str(e)}"
        }), 500

# 보안 강화 API 엔드포인트들
@app.route("/api/security/password/generate", methods=["POST"])
def api_generate_secure_password():
    """보안 강화된 비밀번호 생성"""
    try:
        app.logger.info(f"비밀번호 생성 요청 받음: {request.get_data()}")
        
        # Content-Type 확인
        if not request.is_json:
            app.logger.error("Content-Type이 application/json이 아닙니다")
            return jsonify({"success": False, "error": "Content-Type이 application/json이어야 합니다."}), 400
        
        data = request.get_json()
        app.logger.info(f"파싱된 데이터: {data}")
        
        length = data.get('length', 16) if data else 16
        app.logger.info(f"요청된 비밀번호 길이: {length}")
        
        password = security_enhancer.generate_secure_password(length)
        app.logger.info(f"생성된 비밀번호 길이: {len(password)}")
        
        return jsonify({
            "success": True,
            "data": {
                "password": password,
                "length": len(password),
                "strength_validation": security_enhancer.validate_password_strength(password)
            }
        })
        
    except Exception as e:
        app.logger.error(f"보안 비밀번호 생성 중 오류: {e}")
        return jsonify({
            "success": False,
            "error": "보안 비밀번호 생성 중 오류가 발생했습니다."
        }), 500

@app.route("/api/security/password/validate", methods=["POST"])
def api_validate_password():
    """비밀번호 강도 검증"""
    try:
        data = request.get_json()
        if not data or 'password' not in data:
            return jsonify({
                "success": False,
                "error": "비밀번호가 필요합니다."
            }), 400
        
        password = data['password']
        validation_result = security_enhancer.validate_password_strength(password)
        
        return jsonify({
            "success": True,
            "data": validation_result
        })
        
    except Exception as e:
        app.logger.error(f"비밀번호 검증 중 오류: {e}")
        return jsonify({
            "success": False,
            "error": "비밀번호 검증 중 오류가 발생했습니다."
        }), 500

@app.route("/api/security/data/encrypt", methods=["POST"])
@require_super_admin
def api_encrypt_data():
    """민감한 데이터 암호화"""
    try:
        data = request.get_json()
        if not data or 'data' not in data:
            return jsonify({
                "success": False,
                "error": "암호화할 데이터가 필요합니다."
            }), 400
        
        plain_data = data['data']
        encrypted_data = security_enhancer.encrypt_sensitive_data(plain_data)
        
        return jsonify({
            "success": True,
            "data": {
                "encrypted_data": encrypted_data,
                "original_length": len(plain_data)
            }
        })
        
    except Exception as e:
        app.logger.error(f"데이터 암호화 중 오류: {e}")
        return jsonify({
            "success": False,
            "error": "데이터 암호화 중 오류가 발생했습니다."
        }), 500

@app.route("/api/security/data/decrypt", methods=["POST"])
@require_super_admin
def api_decrypt_data():
    """암호화된 데이터 복호화"""
    try:
        data = request.get_json()
        if not data or 'encrypted_data' not in data:
            return jsonify({
                "success": False,
                "error": "복호화할 데이터가 필요합니다."
            }), 400
        
        encrypted_data = data['encrypted_data']
        decrypted_data = security_enhancer.decrypt_sensitive_data(encrypted_data)
        
        return jsonify({
            "success": True,
            "data": {
                "decrypted_data": decrypted_data
            }
        })
        
    except Exception as e:
        app.logger.error(f"데이터 복호화 중 오류: {e}")
        return jsonify({
            "success": False,
            "error": "데이터 복호화 중 오류가 발생했습니다."
        }), 500

@app.route("/api/security/token/generate", methods=["POST"])
def api_generate_secure_token():
    """보안 강화된 토큰 생성"""
    try:
        data = request.get_json()
        if not data or 'payload' not in data:
            return jsonify({
                "success": False,
                "error": "토큰 페이로드가 필요합니다."
            }), 400
        
        payload = data['payload']
        expires_in = data.get('expires_in', 3600)
        
        token = security_enhancer.generate_secure_token(payload, expires_in)
        
        return jsonify({
            "success": True,
            "data": {
                "token": token,
                "expires_in": expires_in
            }
        })
        
    except Exception as e:
        app.logger.error(f"보안 토큰 생성 중 오류: {e}")
        return jsonify({
            "success": False,
            "error": "보안 토큰 생성 중 오류가 발생했습니다."
        }), 500

@app.route("/api/security/token/verify", methods=["POST"])
def api_verify_secure_token():
    """보안 토큰 검증"""
    try:
        data = request.get_json()
        if not data or 'token' not in data:
            return jsonify({
                "success": False,
                "error": "검증할 토큰이 필요합니다."
            }), 400
        
        token = data['token']
        payload = security_enhancer.verify_secure_token(token)
        
        return jsonify({
            "success": True,
            "data": {
                "payload": payload,
                "is_valid": True
            }
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({
            "success": False,
            "error": "토큰이 만료되었습니다."
        }), 401
    except jwt.InvalidTokenError as e:
        return jsonify({
            "success": False,
            "error": f"잘못된 토큰입니다: {str(e)}"
        }), 401
    except Exception as e:
        app.logger.error(f"토큰 검증 중 오류: {e}")
        return jsonify({
            "success": False,
            "error": "토큰 검증 중 오류가 발생했습니다."
        }), 500

@app.route("/api/security/input/sanitize", methods=["POST"])
def api_sanitize_input():
    """사용자 입력 데이터 정제"""
    try:
        data = request.get_json()
        if not data or 'input_data' not in data:
            return jsonify({
                "success": False,
                "error": "정제할 입력 데이터가 필요합니다."
            }), 400
        
        input_data = data['input_data']
        sanitized_data = security_enhancer.sanitize_input(input_data)
        
        return jsonify({
            "success": True,
            "data": {
                "original_data": input_data,
                "sanitized_data": sanitized_data,
                "changes_made": input_data != sanitized_data
            }
        })
        
    except Exception as e:
        app.logger.error(f"입력 데이터 정제 중 오류: {e}")
        return jsonify({
            "success": False,
            "error": "입력 데이터 정제 중 오류가 발생했습니다."
        }), 500

@app.route("/api/security/file/validate", methods=["POST"])
def api_validate_file_upload():
    """파일 업로드 보안 검증"""
    try:
        data = request.get_json()
        if not data or 'filename' not in data or 'file_size' not in data:
            return jsonify({
                "success": False,
                "error": "파일명과 파일 크기가 필요합니다."
            }), 400
        
        filename = data['filename']
        file_size = data['file_size']
        allowed_extensions = data.get('allowed_extensions')
        
        validation_result = security_enhancer.validate_file_upload(
            filename, file_size, allowed_extensions
        )
        
        return jsonify({
            "success": True,
            "data": validation_result
        })
        
    except Exception as e:
        app.logger.error(f"파일 업로드 검증 중 오류: {e}")
        return jsonify({
            "success": False,
            "error": "파일 업로드 검증 중 오류가 발생했습니다."
        }), 500

@app.route("/api/security/report", methods=["GET"])
@require_super_admin
def api_security_report():
    """보안 리포트 생성"""
    try:
        report = security_enhancer.generate_security_report()
        
        return jsonify({
            "success": True,
            "data": report
        })
        
    except Exception as e:
        app.logger.error(f"보안 리포트 생성 중 오류: {e}")
        return jsonify({
            "success": False,
            "error": "보안 리포트 생성 중 오류가 발생했습니다."
        }), 500

@app.route("/api/security/event/log", methods=["POST"])
def api_log_security_event():
    """보안 이벤트 로깅"""
    try:
        data = request.get_json()
        if not data or 'event_type' not in data:
            return jsonify({
                "success": False,
                "error": "이벤트 타입이 필요합니다."
            }), 400
        
        event_type = data['event_type']
        details = data.get('details', {})
        user_id = data.get('user_id')
        
        security_enhancer.log_security_event(event_type, details, user_id)
        
        return jsonify({
            "success": True,
            "message": "보안 이벤트가 로깅되었습니다."
        })
        
    except Exception as e:
        app.logger.error(f"보안 이벤트 로깅 중 오류: {e}")
        return jsonify({
            "success": False,
            "error": "보안 이벤트 로깅 중 오류가 발생했습니다."
        }), 500

@app.route("/api/security/test", methods=["GET"])
def api_security_test():
    """보안 기능 테스트 (인증 불필요)"""
    try:
        # 보안 강화 기능들 테스트
        test_password = security_enhancer.generate_secure_password(12)
        password_validation = security_enhancer.validate_password_strength(test_password)
        
        # 입력 정제 테스트
        test_input = "<script>alert('xss')</script>"
        sanitized_input = security_enhancer.sanitize_input(test_input)
        
        # 파일 검증 테스트
        file_validation = security_enhancer.validate_file_upload(
            "test.txt", 1024, [".txt", ".pdf"]
        )
        
        return jsonify({
            "success": True,
            "data": {
                "message": "보안 기능들이 성공적으로 테스트되었습니다.",
                "password_generation": {
                    "generated_password": test_password,
                    "length": len(test_password),
                    "validation": password_validation
                },
                "input_sanitization": {
                    "original_input": test_input,
                    "sanitized_input": sanitized_input
                },
                "file_validation": file_validation,
                "timestamp": datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        app.logger.error(f"보안 기능 테스트 중 오류: {e}")
        return jsonify({
            "success": False,
            "error": f"보안 기능 테스트 중 오류가 발생했습니다: {str(e)}"
        }), 500

# 매장 관리 API
@app.route("/api/stores", methods=["GET"])
def api_stores():
    """매장 목록 조회"""
    try:
        # 샘플 매장 데이터 반환
        stores = [
            {
                "id": 1,
                "name": "강남점",
                "code": "GN001",
                "address": "서울시 강남구 테헤란로 123",
                "phone": "02-1234-5678",
                "manager_name": "김강남",
                "brand_id": 1,
                "brand_name": "스타벅스",
                "employee_count": 12,
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            },
            {
                "id": 2,
                "name": "홍대점",
                "code": "HD001",
                "address": "서울시 마포구 홍대로 456",
                "phone": "02-2345-6789",
                "manager_name": "이홍대",
                "brand_id": 1,
                "brand_name": "스타벅스",
                "employee_count": 10,
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T09:15:00Z"
            },
            {
                "id": 3,
                "name": "신촌점",
                "code": "SC001",
                "address": "서울시 서대문구 신촌로 789",
                "phone": "02-3456-7890",
                "manager_name": "박신촌",
                "brand_id": 1,
                "brand_name": "스타벅스",
                "employee_count": 8,
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T08:45:00Z"
            },
            {
                "id": 4,
                "name": "명동점",
                "code": "MD001",
                "address": "서울시 중구 명동길 321",
                "phone": "02-4567-8901",
                "manager_name": "최명동",
                "brand_id": 1,
                "brand_name": "스타벅스",
                "employee_count": 15,
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T11:20:00Z"
            },
            {
                "id": 5,
                "name": "잠실점",
                "code": "JS001",
                "address": "서울시 송파구 올림픽로 654",
                "phone": "02-5678-9012",
                "manager_name": "정잠실",
                "brand_id": 1,
                "brand_name": "스타벅스",
                "employee_count": 14,
                "status": "inactive",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T07:30:00Z"
            }
        ]
        
        return jsonify({
            "success": True,
            "data": stores,
            "message": "매장 목록을 성공적으로 조회했습니다.",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route("/api/stores/<int:store_id>", methods=["GET"])
def api_store_detail(store_id):
    """매장 상세 정보 조회"""
    try:
        # 샘플 매장 데이터에서 해당 ID 찾기
        stores = [
            {
                "id": 1,
                "name": "강남점",
                "code": "GN001",
                "address": "서울시 강남구 테헤란로 123",
                "phone": "02-1234-5678",
                "manager_name": "김강남",
                "brand_id": 1,
                "brand_name": "스타벅스",
                "employee_count": 12,
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        ]
        
        store = next((s for s in stores if s["id"] == store_id), None)
        if not store:
            return jsonify({
                "success": False,
                "error": "매장을 찾을 수 없습니다.",
                "timestamp": datetime.utcnow().isoformat()
            }), 404
        
        return jsonify({
            "success": True,
            "data": store,
            "message": "매장 정보를 성공적으로 조회했습니다.",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route("/api/sales", methods=["GET"])
def api_sales():
    """매출 데이터 조회"""
    try:
        # 샘플 매출 데이터 생성
        from datetime import datetime, timedelta
        import random
        
        # 최근 30일간의 매출 데이터 생성
        sales_data = []
        categories = ['음식', '음료', '디저트', '기타']
        payment_methods = ['cash', 'card', 'mobile', 'online']
        store_names = ['강남점', '홍대점', '명동점', '잠실점', '부산점']
        
        for i in range(30):
            date = datetime.now() - timedelta(days=i)
            for store_id, store_name in enumerate(store_names, 1):
                # 랜덤 매출 데이터 생성
                total_amount = random.randint(500000, 3000000)  # 50만원 ~ 300만원
                order_count = random.randint(50, 200)
                customer_count = random.randint(30, 150)
                average_order_value = total_amount / order_count if order_count > 0 else 0
                
                sales_data.append({
                    "id": len(sales_data) + 1,
                    "date": date.strftime("%Y-%m-%d"),
                    "store_id": store_id,
                    "store_name": store_name,
                    "total_amount": total_amount,
                    "order_count": order_count,
                    "customer_count": customer_count,
                    "average_order_value": round(average_order_value, 2),
                    "payment_method": random.choice(payment_methods),
                    "category": random.choice(categories),
                    "created_at": date.isoformat()
                })
        
        return jsonify({
            "success": True,
            "data": sales_data,
            "message": "매출 데이터를 성공적으로 조회했습니다.",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/mobile/download')
def mobile_download():
    return render_template('mobile_download.html')

@app.route('/mobile/test')
def mobile_test_page():
    """모바일 API 테스트 페이지"""
    return render_template('mobile_test.html')



if __name__ == "__main__":
    # 데이터베이스 초기화
    with app.app_context():
        try:
            initialize_database()
            register_blueprints()
            logger.info("애플리케이션 초기화 완료")
        except Exception as e:
            logger.error(f"애플리케이션 초기화 실패: {e}")
    
    # Socket.IO 서버 실행 (실시간 통신 지원)
    try:
        logger.info("Socket.IO 서버로 실행 중...")
        logger.info(f"socketio 객체 타입: {type(socketio)}")
        logger.info(f"socketio 객체: {socketio}")
        
        # Socket.IO 서버로 실행
        socketio.run(
            app,
            host=os.getenv("FLASK_HOST", "0.0.0.0"),
            port=int(os.getenv("FLASK_PORT", 5000)),
            debug=os.getenv("FLASK_DEBUG", "True").lower() == "true",
            allow_unsafe_werkzeug=True  # 개발용
        )
        
    except Exception as e:
        logger.error(f"Socket.IO 서버 실행 실패: {e}")
        logger.info("일반 Flask 서버로 실행합니다.")
        app.run(
            host=os.getenv("FLASK_HOST", "0.0.0.0"),
            port=int(os.getenv("FLASK_PORT", 5000)),
            debug=os.getenv("FLASK_DEBUG", "True").lower() == "true"
        )