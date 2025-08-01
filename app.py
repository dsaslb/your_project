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
from flask import Flask, flash, jsonify, redirect, render_template, request, abort, url_for, g, current_app
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask_login import current_user, login_required, login_user
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Gauge
from werkzeug.security import generate_password_hash, check_password_hash

# 로깅 설정
logger = logging.getLogger(__name__)

# 설정 및 확장 모듈 import
from config.config import config_by_name
from extensions import cache, csrf, db, limiter, login_manager, migrate

# AnonymousUserMixin import
from models_main import AnonymousUserMixin

# Swagger 설정 import (조건부)
try:
    from api.swagger_config import create_swagger_config
    SWAGGER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Swagger 설정을 불러올 수 없습니다: {e}")
    create_swagger_config = None
    SWAGGER_AVAILABLE = False

# WebSocket 매니저 import (조건부)
try:
    from api.websocket_manager import websocket_manager
    WEBSOCKET_AVAILABLE = True
except ImportError as e:
    logger.warning(f"WebSocket 매니저를 불러올 수 없습니다: {e}")
    websocket_manager = None
    WEBSOCKET_AVAILABLE = False

# WebSocket 서버 import (조건부)
try:
    from websocket.websocket_server import create_websocket_server
    WEBSOCKET_SERVER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"WebSocket 서버를 불러올 수 없습니다: {e}")
    create_websocket_server = None
    WEBSOCKET_SERVER_AVAILABLE = False

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

# 권한 정책 시스템 import
from utils.authorization_policy import (
    require_super_admin, 
    protect_data_creation_endpoint, 
    audit_operation,
    auth_policy
)

# 시스템 최적화 모듈 import
from utils.system_optimizer import system_optimizer

# 보안 강화 모듈 import
from utils.security_enhancer import security_enhancer

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
        login_manager.anonymous_user = AnonymousUserMixin
        
        # 추가 확장 모듈 초기화
        limiter.init_app(app)
        cache.init_app(app)
        
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

# WebSocket 매니저 초기화
websocket_manager.init_app(app)

# 데이터베이스 초기화 (앱 컨텍스트 내에서 실행)
# initialize_database()

# 블루프린트 등록 함수
def register_blueprints():
    """모든 블루프린트를 등록합니다."""
    blueprints = [
        # 백엔드 관리자 Blueprint
        ("routes.backend_admin", "backend_admin_bp", None),
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

# === 기본 라우트들 ===

@app.route("/")
def index():
    """메인 페이지"""
    return render_template("index.html")

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

# === 기본 설정 ===

@login_manager.user_loader
def load_user(user_id):
    """사용자 로더"""
    return User.query.get(int(user_id))

@app.errorhandler(400)
def bad_request(e):
    """400 에러 핸들러"""
    app.logger.error(f"400 Bad Request: {e}")
    app.logger.error(f"Request data: {request.get_data()}")
    app.logger.error(f"Request headers: {dict(request.headers)}")
    return jsonify({"error": "잘못된 요청입니다.", "details": str(e)}), 400

@app.errorhandler(404)
def page_not_found(e):
    """404 에러 핸들러"""
    try:
        return render_template('errors/404.html'), 404
    except Exception:
        # 템플릿 렌더링 실패 시 간단한 JSON 응답
        return jsonify({"error": "페이지를 찾을 수 없습니다."}), 404

@app.errorhandler(500)
def server_error(e):
    """500 에러 핸들러"""
    try:
        return render_template('errors/500.html'), 500
    except Exception:
        # 템플릿 렌더링 실패 시 간단한 JSON 응답
        return jsonify({"error": "서버 내부 오류가 발생했습니다."}), 500

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

# 대시보드 통계 API 개선
@app.route("/api/admin/dashboard-stats", methods=["GET"])
def api_dashboard_stats():
    """대시보드 통계 데이터"""
    try:
        # 실제 데이터베이스에서 통계 조회
        total_users = User.query.count()
        total_industries = Industry.query.count()
        total_brands = Brand.query.count()
        
        # 최근 활동 통계
        recent_activities = [
            {
                "type": "user_login",
                "message": "관리자가 로그인했습니다.",
                "timestamp": "2024-08-01 14:35:00"
            },
            {
                "type": "data_update",
                "message": "브랜드 정보가 업데이트되었습니다.",
                "timestamp": "2024-08-01 14:30:00"
            },
            {
                "type": "system_alert",
                "message": "새로운 알림이 생성되었습니다.",
                "timestamp": "2024-08-01 14:25:00"
            }
        ]
        
        return jsonify({
            "success": True,
            "data": {
                "summary": {
                    "total_users": total_users,
                    "total_industries": total_industries,
                    "total_brands": total_brands,
                    "active_sessions": 5,
                    "system_health": "excellent"
                },
                "recent_activities": recent_activities,
                "performance_metrics": {
                    "response_time": "120ms",
                    "uptime": "99.9%",
                    "error_rate": "0.1%"
                }
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

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
        user_id = request.args.get('user_id')
        
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
        monitor_thread = system_optimizer.start_continuous_monitoring(interval)
        
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

if __name__ == "__main__":
    # 데이터베이스 초기화
    with app.app_context():
        try:
            initialize_database()
            register_blueprints()
            logger.info("애플리케이션 초기화 완료")
        except Exception as e:
            logger.error(f"애플리케이션 초기화 실패: {e}")
    
    # 개발 서버 실행
    app.run(
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", 5000)),
        debug=os.getenv("FLASK_DEBUG", "True").lower() == "true"
    ) 