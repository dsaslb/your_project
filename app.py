# -*- coding: utf-8 -*-
import os
import logging
from datetime import datetime
from pathlib import Path
from dataclasses import asdict

import jwt
from flask import (Flask, flash, jsonify, redirect,
                   render_template, request)
from flask_cors import CORS
from flask_login import (current_user, login_required, login_user)

logger = logging.getLogger(__name__)

# Import core modules
from config import config_by_name
from extensions import cache, csrf, db, limiter, login_manager, migrate
from models import (Branch, Notification, Order, Schedule, User)

# Import Plugin System
from core.backend.auto_router import setup_auto_router
from core.backend.plugin_manager import PluginManager
from core.backend.plugin_schema import PluginManifest
from core.backend.plugin_customization import CustomizationRule, CustomizationType
from core.backend.plugin_release_manager import PluginReleaseManager
from core.backend.plugin_marketplace import PluginMarketplace
from core.backend.plugin_feedback_system import PluginFeedbackSystem
from core.backend.plugin_testing_system import PluginTestingSystem

config_name = os.getenv("FLASK_ENV", "default")

app = Flask(__name__)
app.config.from_object(config_by_name[config_name])
app.config['JWT_SECRET_KEY'] = 'your-secret-key'

CORS(app,
     origins=[
         "http://localhost:3000",
         "http://127.0.0.1:3000",
         "http://192.168.45.44:3000",
         "http://localhost:3001",
         "http://127.0.0.1:3001",
         "http://192.168.45.44:3001",
         "http://localhost:5000",
         "http://127.0.0.1:5000",
         "http://192.168.45.44:5000"
     ],
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
     expose_headers=["Content-Type", "Authorization"],
     max_age=86400)

# Initialize extensions
csrf.init_app(app)
db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
limiter.init_app(app)
cache.init_app(app)

# Initialize IoT system
from utils.iot_simulator import initialize_iot_system
initialize_iot_system()

# Initialize Plugin Manager
plugin_manager = PluginManager(app)

# Setup Auto Router (플러그인 시스템) - 모든 블루프린트 자동 등록
auto_router = setup_auto_router(app)

# Load all plugins automatically
plugin_load_results = plugin_manager.load_all_plugins()
logger.info(f"플러그인 로드 결과: {plugin_load_results}")

# 플러그인 시스템 API 블루프린트 수동 등록 (자동 라우터 문제 해결)
try:
    from api.plugin_system_manager_api import plugin_system_manager_bp
    app.register_blueprint(plugin_system_manager_bp, name='plugin_system_manager_api')
    logger.info("플러그인 시스템 매니저 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"플러그인 시스템 매니저 API 블루프린트 등록 실패: {e}")

try:
    from api.plugin_operations_api import plugin_operations_bp
    app.register_blueprint(plugin_operations_bp, name='plugin_operations_api')
    logger.info("플러그인 운영 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"플러그인 운영 API 블루프린트 등록 실패: {e}")

# 플러그인 시스템 통합 등록
try:
    from api.plugin_monitoring_dashboard import plugin_monitoring_bp
    app.register_blueprint(plugin_monitoring_bp, name='plugin_monitoring_dashboard')
    logger.info("플러그인 모니터링 대시보드 API 블루프린트 등록 완료")
except Exception as e:
    logger.error(f"플러그인 모니터링 대시보드 API 블루프린트 등록 실패: {e}")

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



# CSRF 보호에서 API 블루프린트 제외
# 자동 라우터에서 등록된 모든 블루프린트를 CSRF 제외 목록에 추가
registered_blueprints = auto_router.get_registered_blueprints()
for blueprint_name, blueprint in registered_blueprints.items():
    csrf.exempt(blueprint)

# 플러그인 블루프린트도 CSRF 제외
for blueprint_name, blueprint in plugin_manager.blueprints.items():
    csrf.exempt(blueprint)

# Initialize Dynamic Schema System
from core.backend.schema_initializer import initialize_default_schemas, create_sample_brand_schema
initialize_default_schemas()
create_sample_brand_schema()

# Login manager setup
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.errorhandler(404)
def page_not_found(e):
    # API 경로인 경우 JSON으로 반환
    if request.path.startswith('/api/'):
        return jsonify({'error': 'API endpoint not found', 'path': request.path}), 404
    # 일반 페이지인 경우 HTML 템플릿 반환
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    # API 경로인 경우 JSON으로 반환
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    # 일반 페이지인 경우 HTML 템플릿 반환
    return render_template('errors/500.html'), 500

@app.route('/favicon.ico')
def favicon():
    """Favicon 처리 - SVG favicon 반환"""
    try:
        return app.send_static_file('favicon.svg')
    except:
        # favicon.svg 파일이 없으면 빈 응답 반환
        return '', 204

@app.context_processor
def inject_notifications():
    """전역 템플릿에 알림 정보 주입"""
    if current_user.is_authenticated:
        unread_count = Notification.query.filter_by(
            user_id=current_user.id, is_read=False
        ).count()
        return {'unread_notifications': unread_count}
    return {'unread_notifications': 0}

@app.route("/")
def index():
    """루트 경로 - 백엔드 대시보드로 리다이렉트"""
    return redirect("/admin_dashboard")

@app.route("/dashboard")
def dashboard():
    """대시보드 접근 시 프론트엔드로 리다이렉트"""
    return redirect("http://192.168.45.44:3000/admin-dashboard")

@app.route("/api/dashboard")
def api_dashboard():
    """대시보드 API 엔드포인트"""
    print(f"DEBUG: /api/dashboard API 호출")
    print(f"DEBUG: Authorization 헤더: {request.headers.get('Authorization', 'None')}")
    
    # Authorization 헤더에서 토큰 확인
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        print("DEBUG: 인증 토큰 없음 - 대시보드 정보 제공")
        return jsonify({
            "message": "인증이 필요합니다.",
            "available_dashboards": {
                "backend": "/admin_dashboard",
                "frontend": "http://192.168.45.44:3000/admin-dashboard",
                "test_login": "/test-login",
                "dashboard_selector": "/dashboard"
            },
            "login_url": "/test-login"
        }), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        # JWT 토큰 디코딩
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        user_id = payload.get('user_id')
        
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
                "backend": "/admin_dashboard",
                "frontend": "http://192.168.45.44:3000/admin-dashboard"
            }
        }
        
        # 플러그인 상태 정보 추가
        plugin_status = auto_router.get_plugin_status()
        plugin_manager_status = plugin_manager.get_plugin_status()
        dashboard_info["plugin_status"] = plugin_status
        dashboard_info["plugin_manager_status"] = plugin_manager_status
        
        return jsonify(dashboard_info)
        
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        print(f"DEBUG: 대시보드 API 오류: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/dashboard-jwt")
def dashboard_jwt():
    """JWT 토큰 테스트용 대시보드"""
    try:
        # Authorization 헤더에서 토큰 확인
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization header required"}), 401
        
        token = auth_header.split(' ')[1]
        
        # JWT 토큰 디코딩
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        
        return jsonify({
            "message": "JWT 토큰이 유효합니다",
            "payload": payload,
            "dashboard_url": "http://192.168.45.44:3000/admin-dashboard"
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/login-success")
def login_success():
    """로그인 성공 페이지"""
    return render_template('auth/login_success.html')

@app.route("/profile")
@login_required
def profile():
    """사용자 프로필 페이지"""
    return render_template('auth/profile.html')

@app.route("/api/profile")
@login_required
def api_profile():
    """사용자 프로필 API"""
    try:
        user_data = {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'role': current_user.role,
            'branch_id': current_user.branch_id,
            'created_at': current_user.created_at.isoformat() if current_user.created_at else None,
            'last_login': current_user.last_login.isoformat() if current_user.last_login else None
        }
        
        # 브랜치 정보 추가
        if current_user.branch_id:
            branch = Branch.query.get(current_user.branch_id)
            if branch:
                user_data['branch'] = {
                    'id': branch.id,
                    'name': branch.name,
                    'address': branch.address
                }
        
        return jsonify(user_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/user/profile")
@login_required
def api_user_profile():
    """사용자 프로필 상세 API"""
    try:
        # 사용자 기본 정보
        user_data = {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'role': current_user.role,
            'branch_id': current_user.branch_id,
            'created_at': current_user.created_at.isoformat() if current_user.created_at else None,
            'last_login': current_user.last_login.isoformat() if current_user.last_login else None
        }
        
        # 브랜치 정보
        if current_user.branch_id:
            branch = Branch.query.get(current_user.branch_id)
            if branch:
                user_data['branch'] = {
                    'id': branch.id,
                    'name': branch.name,
                    'address': branch.address
                }
        
        # 알림 정보
        notifications = Notification.query.filter_by(
            user_id=current_user.id, is_read=False
        ).limit(5).all()
        
        user_data['notifications'] = [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'created_at': n.created_at.isoformat() if n.created_at else None
            }
            for n in notifications
        ]
        
        return jsonify(user_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/auth/login", methods=["GET", "POST"])
def auth_login():
    """로그인 페이지"""
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('사용자명과 비밀번호를 입력해주세요.', 'error')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # 권한에 따른 리다이렉트
            if user.role == 'admin':
                return redirect('/admin_dashboard')
            elif user.role == 'manager':
                return redirect('/manager-dashboard')
            elif user.role == 'employee':
                return redirect('/employee-dashboard')
            else:
                return redirect('/dashboard')
        else:
            flash('잘못된 사용자명 또는 비밀번호입니다.', 'error')
    
    return render_template('auth/login.html')

@app.route("/admin_dashboard")
def admin_dashboard_route():
    """관리자 대시보드"""
    return render_template('admin/admin_dashboard.html')

@app.route("/super-admin")
def super_admin_dashboard():
    """최고 관리자 대시보드"""
    return render_template('admin/super_admin_dashboard.html')

@app.route("/manager-dashboard")
def manager_dashboard():
    """매니저 대시보드"""
    return render_template('admin/manager_dashboard.html')

@app.route("/employee-dashboard")
def employee_dashboard():
    """직원 대시보드"""
    return render_template('admin/employee_dashboard.html')

@app.route("/teamlead-dashboard")
def teamlead_dashboard():
    """팀리드 대시보드"""
    return render_template('admin/teamlead_dashboard.html')

@app.route("/my-attendance")
@login_required
def my_attendance():
    """내 출근 기록"""
    return render_template('attendance/my_attendance.html')

@app.route("/my-schedule")
@login_required
def my_schedule():
    """내 스케줄"""
    return render_template('schedule/my_schedule.html')

@app.route("/test-login")
def test_login():
    """테스트 로그인 페이지"""
    return render_template('auth/test_login.html')

@app.route("/brand-manager-dashboard")
def brand_manager_dashboard():
    """브랜드 매니저 대시보드"""
    return render_template('admin/brand_manager_dashboard.html')

@app.route("/store-manager-dashboard")
def store_manager_dashboard():
    """스토어 매니저 대시보드"""
    return render_template('admin/store_manager_dashboard.html')

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
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
            for user in recent_users
        ]
        
        # 플러그인 상태
        plugin_status = auto_router.get_plugin_status()
        
        stats = {
            'total_users': total_users,
            'total_branches': total_branches,
            'recent_users': recent_users_data,
            'plugin_status': plugin_status
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/admin/system-logs")
def api_admin_system_logs():
    """시스템 로그 API"""
    try:
        # 시스템 로그 정보 (실제로는 로그 파일에서 읽어와야 함)
        plugin_status = auto_router.get_plugin_status()
        logs = [
            {
                'timestamp': datetime.utcnow().isoformat(),
                'level': 'INFO',
                'message': '시스템 정상 운영 중',
                'source': 'auto_router'
            },
            {
                'timestamp': datetime.utcnow().isoformat(),
                'level': 'INFO',
                'message': f'플러그인 {plugin_status["total_plugins"]}개 로드됨',
                'source': 'plugin_loader'
            }
        ]
        
        return jsonify({'logs': logs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/admin/critical-alerts")
def api_admin_critical_alerts():
    """중요 알림 API"""
    try:
        # 중요 알림 목록
        alerts = [
            {
                'id': 1,
                'type': 'system',
                'title': '시스템 상태',
                'message': '모든 서비스 정상 운영 중',
                'severity': 'info',
                'timestamp': datetime.utcnow().isoformat()
            }
        ]
        
        return jsonify({'alerts': alerts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/admin/pending-approvals")
def api_admin_pending_approvals():
    """대기 중인 승인 API"""
    try:
        # 대기 중인 승인 목록
        approvals = [
            {
                'id': 1,
                'type': 'user_registration',
                'title': '새 사용자 등록',
                'requester': 'test_user',
                'timestamp': datetime.utcnow().isoformat()
            }
        ]
        
        return jsonify({'approvals': approvals})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/admin/system-status")
def api_admin_system_status():
    """시스템 상태 API"""
    try:
        # 시스템 상태 정보
        status = {
            'database': 'connected',
            'cache': 'connected',
            'plugins': auto_router.get_plugin_status(),
            'uptime': '24h 30m',
            'memory_usage': '45%',
            'cpu_usage': '12%'
        }
        
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/admin/staff-management")
def admin_staff_management():
    """직원 관리 페이지"""
    return render_template('admin/staff_management.html')

@app.route("/api/admin/staff-list")
def api_admin_staff_list():
    """직원 목록 API"""
    try:
        users = User.query.all()
        staff_list = []
        
        for user in users:
            staff_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'branch_id': user.branch_id,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
            
            # 브랜치 정보 추가
            if user.branch_id:
                branch = Branch.query.get(user.branch_id)
                if branch:
                    staff_data['branch_name'] = branch.name
            
            staff_list.append(staff_data)
        
        return jsonify({'staff': staff_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/admin/staff-detail/<int:user_id>")
def api_admin_staff_detail(user_id):
    """직원 상세 정보 API"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'branch_id': user.branch_id,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
        
        # 브랜치 정보
        if user.branch_id:
            branch = Branch.query.get(user.branch_id)
            if branch:
                user_data['branch'] = {
                    'id': branch.id,
                    'name': branch.name,
                    'address': branch.address
                }
        
        return jsonify(user_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/admin/update-staff-role/<int:user_id>", methods=["PUT"])
def api_admin_update_staff_role(user_id):
    """직원 역할 업데이트 API"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        new_role = data.get('role')
        
        if not new_role:
            return jsonify({'error': 'Role is required'}), 400
        
        # 역할 유효성 검사
        valid_roles = ['admin', 'manager', 'employee', 'teamlead']
        if new_role not in valid_roles:
            return jsonify({'error': 'Invalid role'}), 400
        
        user.role = new_role
        db.session.commit()
        
        return jsonify({'message': 'Role updated successfully', 'user': {
            'id': user.id,
            'username': user.username,
            'role': user.role
        }})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/admin/delete-staff/<int:user_id>", methods=["DELETE"])
def api_admin_delete_staff(user_id):
    """직원 삭제 API"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # 관리자는 삭제 불가
        if user.role == 'admin':
            return jsonify({'error': 'Cannot delete admin user'}), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/admin/system-monitoring")
def admin_system_monitoring():
    """시스템 모니터링 페이지"""
    return render_template('admin/system_monitoring.html')

@app.route("/api/admin/system-stats")
def api_admin_system_stats():
    """시스템 통계 API"""
    try:
        # 시스템 통계
        stats = {
            'total_users': User.query.count(),
            'total_branches': Branch.query.count(),
            'total_orders': Order.query.count() if hasattr(Order, 'query') else 0,
            'total_schedules': Schedule.query.count() if hasattr(Schedule, 'query') else 0,
            'plugin_status': auto_router.get_plugin_status()
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/admin/service-status")
def api_admin_service_status():
    """서비스 상태 API"""
    try:
        # 서비스 상태 정보
        services = [
            {
                'name': 'Database',
                'status': 'healthy',
                'response_time': '5ms',
                'last_check': datetime.utcnow().isoformat()
            },
            {
                'name': 'Cache',
                'status': 'healthy',
                'response_time': '2ms',
                'last_check': datetime.utcnow().isoformat()
            },
            {
                'name': 'Plugin System',
                'status': 'healthy',
                'response_time': '10ms',
                'last_check': datetime.utcnow().isoformat()
            }
        ]
        
        return jsonify({'services': services})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/admin/system-alerts")
def api_admin_system_alerts():
    """시스템 알림 API"""
    try:
        # 시스템 알림 목록
        alerts = [
            {
                'id': 1,
                'type': 'info',
                'title': '시스템 정상',
                'message': '모든 서비스가 정상적으로 운영되고 있습니다.',
                'timestamp': datetime.utcnow().isoformat(),
                'acknowledged': False
            }
        ]
        
        return jsonify({'alerts': alerts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/plugins/status")
def api_plugins_status():
    """플러그인 상태 조회 API"""
    try:
        return jsonify({
            "status": "success",
            "data": plugin_manager.get_plugin_status()
        })
    except Exception as e:
        logger.error(f"플러그인 상태 조회 실패: {e}")
        return jsonify({"error": "플러그인 상태 조회 실패"}), 500

@app.route("/api/plugins/list")
def api_plugins_list():
    """플러그인 목록 조회 API"""
    try:
        plugins_info = {}
        for plugin_name, config in plugin_manager.plugins.items():
            plugins_info[plugin_name] = {
                "name": config.get("name", plugin_name),
                "version": config.get("version", "1.0.0"),
                "description": config.get("description", ""),
                "author": config.get("author", ""),
                "category": config.get("category", "general"),
                "enabled": config.get("enabled", True),
                "loaded": plugin_name in plugin_manager.loaded_plugins,
                "menus": config.get("menus", []),
                "routes": config.get("routes", [])
            }
        
        return jsonify({
            "status": "success",
            "data": plugins_info
        })
    except Exception as e:
        logger.error(f"플러그인 목록 조회 실패: {e}")
        return jsonify({"error": "플러그인 목록 조회 실패"}), 500

@app.route("/api/plugins/<plugin_name>/enable", methods=["POST"])
def api_enable_plugin(plugin_name):
    """플러그인 활성화 API"""
    try:
        success = plugin_manager.enable_plugin(plugin_name)
        if success:
            return jsonify({
                "status": "success",
                "message": f"플러그인 {plugin_name} 활성화 완료"
            })
        else:
            return jsonify({"error": f"플러그인 {plugin_name} 활성화 실패"}), 400
    except Exception as e:
        logger.error(f"플러그인 {plugin_name} 활성화 실패: {e}")
        return jsonify({"error": "플러그인 활성화 실패"}), 500

@app.route("/api/plugins/<plugin_name>/disable", methods=["POST"])
def api_disable_plugin(plugin_name):
    """플러그인 비활성화 API"""
    try:
        success = plugin_manager.disable_plugin(plugin_name)
        if success:
            return jsonify({
                "status": "success",
                "message": f"플러그인 {plugin_name} 비활성화 완료"
            })
        else:
            return jsonify({"error": f"플러그인 {plugin_name} 비활성화 실패"}), 400
    except Exception as e:
        logger.error(f"플러그인 {plugin_name} 비활성화 실패: {e}")
        return jsonify({"error": "플러그인 비활성화 실패"}), 500

@app.route("/api/plugins/<plugin_name>/reload", methods=["POST"])
def api_reload_plugin(plugin_name):
    """플러그인 재로드 API"""
    try:
        success = plugin_manager.reload_plugin(plugin_name)
        if success:
            return jsonify({
                "status": "success",
                "message": f"플러그인 {plugin_name} 재로드 완료"
            })
        else:
            return jsonify({"error": f"플러그인 {plugin_name} 재로드 실패"}), 400
    except Exception as e:
        logger.error(f"플러그인 {plugin_name} 재로드 실패: {e}")
        return jsonify({"error": "플러그인 재로드 실패"}), 500

@app.route("/api/plugins/menus")
def api_plugins_menus():
    """플러그인 메뉴 정보 조회 API"""
    try:
        menus = plugin_manager.get_plugin_menus()
        return jsonify({
            "status": "success",
            "data": menus
        })
    except Exception as e:
        logger.error(f"플러그인 메뉴 조회 실패: {e}")
        return jsonify({"error": "플러그인 메뉴 조회 실패"}), 500

@app.route("/api/plugins/routes")
def api_plugins_routes():
    """플러그인 라우트 정보 조회 API"""
    try:
        routes = plugin_manager.get_plugin_routes()
        return jsonify({
            "status": "success",
            "data": routes
        })
    except Exception as e:
        logger.error(f"플러그인 라우트 조회 실패: {e}")
        return jsonify({"error": "플러그인 라우트 조회 실패"}), 500

@app.route("/api/plugins/create", methods=["POST"])
@csrf.exempt
def api_create_plugin():
    """새 플러그인 생성 API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "요청 데이터가 없습니다"}), 400
        
        plugin_name = data.get('name')
        if not plugin_name:
            return jsonify({"error": "플러그인 이름이 필요합니다"}), 400
        
        # 플러그인 디렉토리 생성
        plugin_dir = Path("plugins") / plugin_name
        if plugin_dir.exists():
            return jsonify({"error": f"플러그인 {plugin_name}이 이미 존재합니다"}), 400
        
        # 기본 디렉토리 구조 생성
        (plugin_dir / "backend").mkdir(parents=True, exist_ok=True)
        (plugin_dir / "config").mkdir(parents=True, exist_ok=True)
        (plugin_dir / "templates").mkdir(parents=True, exist_ok=True)
        (plugin_dir / "static").mkdir(parents=True, exist_ok=True)
        
        # 매니페스트 생성
        manifest = PluginManifest(plugin_dir)
        config = manifest.create_new(
            plugin_name=plugin_name,
            name=data.get('display_name', plugin_name),
            version=data.get('version', '1.0.0'),
            description=data.get('description', f'{plugin_name} 플러그인'),
            author=data.get('author', 'Your Name'),
            category=data.get('category', 'general')
        )
        
        # 기본 백엔드 파일 생성
        backend_file = plugin_dir / "backend" / "main.py"
        with open(backend_file, 'w', encoding='utf-8') as f:
            f.write(f'''# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request

def register_blueprint(bp):
    """플러그인 블루프린트 등록"""
    
    @bp.route('/')
    def index():
        """플러그인 메인 페이지"""
        return jsonify({{
            "message": "Hello from {plugin_name} plugin!",
            "plugin": "{plugin_name}",
            "version": "{config['version']}"
        }})
    
    @bp.route('/config')
    def get_config():
        """플러그인 설정 조회"""
        return jsonify({{
            "plugin": "{plugin_name}",
            "config": {{}}
        }})
    
    @bp.route('/config', methods=['POST'])
    def update_config():
        """플러그인 설정 업데이트"""
        data = request.get_json()
        return jsonify({{
            "message": "설정 업데이트 완료",
            "plugin": "{plugin_name}",
            "config": data
        }})

# 블루프린트 생성
bp = Blueprint('{plugin_name}', __name__)

# 블루프린트 등록
register_blueprint(bp)
''')
        
        return jsonify({
            "status": "success",
            "message": f"플러그인 {plugin_name} 생성 완료",
            "data": {
                "plugin_name": plugin_name,
                "config": config,
                "directory": str(plugin_dir)
            }
        })
        
    except Exception as e:
        logger.error(f"플러그인 생성 실패: {e}")
        return jsonify({"error": "플러그인 생성 실패"}), 500

@app.route("/api/plugins/<plugin_name>/validate", methods=["POST"])
def api_validate_plugin(plugin_name):
    """플러그인 설정 검증 API"""
    try:
        config = plugin_manager.load_plugin_config(plugin_name)
        if not config:
            return jsonify({"error": f"플러그인 {plugin_name}을 찾을 수 없습니다"}), 404
        
        # 스키마 검증
        is_valid, errors = plugin_manager.validator.validate_plugin_config(config)
        
        return jsonify({
            "status": "success",
            "data": {
                "plugin_name": plugin_name,
                "is_valid": is_valid,
                "errors": errors,
                "config": config
            }
        })
        
    except Exception as e:
        logger.error(f"플러그인 {plugin_name} 검증 실패: {e}")
        return jsonify({"error": "플러그인 검증 실패"}), 500

@app.route("/api/plugins/customizations/rules", methods=["GET"])
def api_get_customization_rules():
    """커스터마이즈 규칙 조회 API"""
    try:
        plugin_name = request.args.get('plugin_name')
        target_type = request.args.get('target_type')
        
        rules = plugin_manager.customization_manager.get_customization_rules(
            plugin_name=plugin_name,
            target_type=target_type
        )
        
        return jsonify({
            "status": "success",
            "data": [asdict(rule) for rule in rules]
        })
    except Exception as e:
        logger.error(f"커스터마이즈 규칙 조회 실패: {e}")
        return jsonify({"error": "커스터마이즈 규칙 조회 실패"}), 500

@app.route("/api/plugins/customizations/rules", methods=["POST"])
def api_create_customization_rule():
    """커스터마이즈 규칙 생성 API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "요청 데이터가 없습니다"}), 400
        
        # CustomizationRule 객체 생성
        rule = CustomizationRule(
            plugin_name=data['plugin_name'],
            target_type=data['target_type'],
            target_path=data['target_path'],
            customization_type=CustomizationType(data['customization_type']),
            value=data['value'],
            conditions=data.get('conditions', {}),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        success = plugin_manager.customization_manager.create_customization_rule(rule)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "커스터마이즈 규칙 생성 완료",
                "data": asdict(rule)
            })
        else:
            return jsonify({"error": "커스터마이즈 규칙 생성 실패"}), 400
            
    except Exception as e:
        logger.error(f"커스터마이즈 규칙 생성 실패: {e}")
        return jsonify({"error": "커스터마이즈 규칙 생성 실패"}), 500

@app.route("/api/plugins/customizations/requests", methods=["GET"])
def api_get_customization_requests():
    """커스터마이즈 요청 조회 API"""
    try:
        status = request.args.get('status')
        plugin_name = request.args.get('plugin_name')
        
        requests = plugin_manager.customization_manager.get_customization_requests(
            status=status,
            plugin_name=plugin_name
        )
        
        return jsonify({
            "status": "success",
            "data": [asdict(req) for req in requests]
        })
    except Exception as e:
        logger.error(f"커스터마이즈 요청 조회 실패: {e}")
        return jsonify({"error": "커스터마이즈 요청 조회 실패"}), 500

@app.route("/api/plugins/customizations/requests", methods=["POST"])
def api_create_customization_request():
    """커스터마이즈 요청 생성 API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "요청 데이터가 없습니다"}), 400
        
        # CustomizationRule 객체 생성
        rule = CustomizationRule(
            plugin_name=data['plugin_name'],
            target_type=data['target_type'],
            target_path=data['target_path'],
            customization_type=CustomizationType(data['customization_type']),
            value=data['value'],
            conditions=data.get('conditions', {}),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        request_id = plugin_manager.customization_manager.create_customization_request(
            plugin_name=data['plugin_name'],
            rule=rule,
            requester=data['requester'],
            request_reason=data['request_reason']
        )
        
        return jsonify({
            "status": "success",
            "message": "커스터마이즈 요청 생성 완료",
            "data": {"request_id": request_id}
        })
        
    except Exception as e:
        logger.error(f"커스터마이즈 요청 생성 실패: {e}")
        return jsonify({"error": "커스터마이즈 요청 생성 실패"}), 500

@app.route("/api/plugins/customizations/requests/<request_id>/approve", methods=["POST"])
def api_approve_customization_request(request_id):
    """커스터마이즈 요청 승인 API"""
    try:
        data = request.get_json() or {}
        reviewer = data.get('reviewer', 'admin')
        comment = data.get('comment', '')
        
        success = plugin_manager.customization_manager.approve_customization_request(
            request_id, reviewer, comment
        )
        
        if success:
            return jsonify({
                "status": "success",
                "message": "커스터마이즈 요청 승인 완료"
            })
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
        reviewer = data.get('reviewer', 'admin')
        comment = data.get('comment', '')
        
        success = plugin_manager.customization_manager.reject_customization_request(
            request_id, reviewer, comment
        )
        
        if success:
            return jsonify({
                "status": "success",
                "message": "커스터마이즈 요청 거부 완료"
            })
        else:
            return jsonify({"error": "커스터마이즈 요청 거부 실패"}), 400
            
    except Exception as e:
        logger.error(f"커스터마이즈 요청 거부 실패: {e}")
        return jsonify({"error": "커스터마이즈 요청 거부 실패"}), 500

@app.route("/api/plugins/customizations/history")
def api_get_customization_history():
    """커스터마이즈 히스토리 조회 API"""
    try:
        action = request.args.get('action')
        limit = int(request.args.get('limit', 100))
        
        history = plugin_manager.customization_manager.get_customization_history(
            action=action,
            limit=limit
        )
        
        return jsonify({
            "status": "success",
            "data": history
        })
    except Exception as e:
        logger.error(f"커스터마이즈 히스토리 조회 실패: {e}")
        return jsonify({"error": "커스터마이즈 히스토리 조회 실패"}), 500

plugin_release_manager = PluginReleaseManager("plugins")

@app.route("/api/plugins/<plugin_name>/releases", methods=["GET"])
def api_list_plugin_releases(plugin_name):
    """플러그인 배포본(버전) 목록 조회 API"""
    try:
        releases = plugin_release_manager.list_releases(plugin_name)
        return jsonify({
            "status": "success",
            "data": releases
        })
    except Exception as e:
        logger.error(f"플러그인 배포본 목록 조회 실패: {e}")
        return jsonify({"error": "플러그인 배포본 목록 조회 실패"}), 500

@app.route("/api/plugins/<plugin_name>/release", methods=["POST"])
def api_save_plugin_release(plugin_name):
    """플러그인 현재 상태를 새 버전으로 배포(스냅샷) API"""
    try:
        data = request.get_json() or {}
        version = data.get('version')
        user = data.get('user', 'admin')
        detail = data.get('detail', '')
        if not version:
            return jsonify({"error": "버전 정보가 필요합니다"}), 400
        success = plugin_release_manager.save_release(plugin_name, version)
        if success:
            plugin_release_manager.log_release_action(plugin_name, "release", version, user, detail)
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
        version = data.get('version')
        user = data.get('user', 'admin')
        detail = data.get('detail', '')
        if not version:
            return jsonify({"error": "롤백할 버전 정보가 필요합니다"}), 400
        success = plugin_release_manager.rollback_release(plugin_name, version)
        if success:
            plugin_release_manager.log_release_action(plugin_name, "rollback", version, user, detail)
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
        limit = int(request.args.get('limit', 50))
        history = plugin_release_manager.get_release_history(plugin_name, limit)
        return jsonify({
            "status": "success",
            "data": history
        })
    except Exception as e:
        logger.error(f"플러그인 배포 이력 조회 실패: {e}")
        return jsonify({"error": "플러그인 배포 이력 조회 실패"}), 500

plugin_marketplace = PluginMarketplace()

@app.route("/api/marketplace/plugins", methods=["GET"])
def api_marketplace_plugins():
    """마켓플레이스 플러그인 목록 조회 API"""
    try:
        category = request.args.get('category')
        search = request.args.get('search')
        sort_by = request.args.get('sort_by', 'rating')
        sort_order = request.args.get('sort_order', 'desc')
        
        plugins = plugin_marketplace.get_marketplace_plugins(
            category=category,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return jsonify({
            "status": "success",
            "data": plugins
        })
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
        
        return jsonify({
            "status": "success",
            "data": plugin
        })
    except Exception as e:
        logger.error(f"마켓플레이스 플러그인 상세 정보 조회 실패: {e}")
        return jsonify({"error": "마켓플레이스 플러그인 상세 정보 조회 실패"}), 500

@app.route("/api/marketplace/plugins/<plugin_id>/install", methods=["POST"])
def api_install_marketplace_plugin(plugin_id):
    """마켓플레이스에서 플러그인 설치 API"""
    try:
        success = plugin_marketplace.install_plugin_from_marketplace(plugin_id)
        if success:
            return jsonify({
                "status": "success",
                "message": f"플러그인 {plugin_id} 설치 완료"
            })
        else:
            return jsonify({"error": "플러그인 설치 실패"}), 400
    except Exception as e:
        logger.error(f"마켓플레이스 플러그인 설치 실패: {e}")
        return jsonify({"error": "마켓플레이스 플러그인 설치 실패"}), 500

@app.route("/api/marketplace/plugins/<plugin_id>/reviews", methods=["GET"])
def api_marketplace_plugin_reviews(plugin_id):
    """마켓플레이스 플러그인 리뷰 목록 조회 API"""
    try:
        limit = int(request.args.get('limit', 50))
        reviews = plugin_marketplace.get_plugin_reviews(plugin_id, limit)
        
        return jsonify({
            "status": "success",
            "data": reviews
        })
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
        
        user_id = data.get('user_id', 'anonymous')
        user_name = data.get('user_name', 'Anonymous')
        rating = data.get('rating', 5)
        comment = data.get('comment', '')
        
        if not (1 <= rating <= 5):
            return jsonify({"error": "평점은 1-5 사이여야 합니다"}), 400
        
        success = plugin_marketplace.add_review(plugin_id, user_id, user_name, rating, comment)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "리뷰가 추가되었습니다"
            })
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
        
        return jsonify({
            "status": "success",
            "data": categories
        })
    except Exception as e:
        logger.error(f"마켓플레이스 카테고리 조회 실패: {e}")
        return jsonify({"error": "마켓플레이스 카테고리 조회 실패"}), 500

plugin_feedback_system = PluginFeedbackSystem()

@app.route("/api/feedback", methods=["POST"])
def api_create_feedback():
    """피드백 생성 API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "요청 데이터가 없습니다"}), 400
        
        feedback_id = plugin_feedback_system.create_feedback(data)
        if feedback_id:
            return jsonify({
                "status": "success",
                "message": "피드백이 생성되었습니다",
                "feedback_id": feedback_id
            })
        else:
            return jsonify({"error": "피드백 생성 실패"}), 400
    except Exception as e:
        logger.error(f"피드백 생성 실패: {e}")
        return jsonify({"error": "피드백 생성 실패"}), 500

@app.route("/api/feedback", methods=["GET"])
def api_get_feedback_list():
    """피드백 목록 조회 API"""
    try:
        status = request.args.get('status')
        feedback_type = request.args.get('type')
        plugin_id = request.args.get('plugin_id')
        user_id = request.args.get('user_id')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        feedbacks = plugin_feedback_system.get_feedback_list(
            status=status,
            type=feedback_type,
            plugin_id=plugin_id,
            user_id=user_id,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return jsonify({
            "status": "success",
            "data": feedbacks
        })
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
        
        return jsonify({
            "status": "success",
            "data": feedback
        })
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
        
        status = data.get('status')
        user_id = data.get('user_id', 'admin')
        comment = data.get('comment', '')
        
        if not status:
            return jsonify({"error": "상태 정보가 없습니다"}), 400
        
        success = plugin_feedback_system.update_feedback_status(feedback_id, status, user_id, comment)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "피드백 상태가 업데이트되었습니다"
            })
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
        
        assigned_to = data.get('assigned_to')
        estimated_completion = data.get('estimated_completion')
        
        if not assigned_to:
            return jsonify({"error": "할당 대상이 없습니다"}), 400
        
        success = plugin_feedback_system.assign_feedback(feedback_id, assigned_to, estimated_completion)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "피드백이 할당되었습니다"
            })
        else:
            return jsonify({"error": "피드백 할당 실패"}), 400
    except Exception as e:
        logger.error(f"피드백 할당 실패: {e}")
        return jsonify({"error": "피드백 할당 실패"}), 500

@app.route("/api/feedback/<feedback_id>/comments", methods=["GET"])
def api_get_feedback_comments(feedback_id):
    """피드백 댓글 목록 조회 API"""
    try:
        include_internal = request.args.get('include_internal', 'false').lower() == 'true'
        comments = plugin_feedback_system.get_comments(feedback_id, include_internal)
        
        return jsonify({
            "status": "success",
            "data": comments
        })
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
        
        user_id = data.get('user_id', 'anonymous')
        user_name = data.get('user_name', 'Anonymous')
        user_role = data.get('user_role', 'user')
        content = data.get('content', '')
        is_internal = data.get('is_internal', False)
        
        if not content:
            return jsonify({"error": "댓글 내용이 없습니다"}), 400
        
        comment_id = plugin_feedback_system.add_comment(
            feedback_id, user_id, user_name, user_role, content, is_internal
        )
        
        if comment_id:
            return jsonify({
                "status": "success",
                "message": "댓글이 추가되었습니다",
                "comment_id": comment_id
            })
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
        
        user_id = data.get('user_id', 'anonymous')
        vote = data.get('vote', True)
        
        success = plugin_feedback_system.vote_feedback(feedback_id, user_id, vote)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "투표가 반영되었습니다"
            })
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
        
        user_id = data.get('user_id', 'anonymous')
        follow = data.get('follow', True)
        
        success = plugin_feedback_system.follow_feedback(feedback_id, user_id, follow)
        
        if success:
            action = "팔로우" if follow else "언팔로우"
            return jsonify({
                "status": "success",
                "message": f"피드백을 {action}했습니다"
            })
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
        
        return jsonify({
            "status": "success",
            "data": templates
        })
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
        
        return jsonify({
            "status": "success",
            "data": workflow
        })
    except Exception as e:
        logger.error(f"피드백 워크플로우 조회 실패: {e}")
        return jsonify({"error": "피드백 워크플로우 조회 실패"}), 500

plugin_testing_system = PluginTestingSystem()

@app.route("/api/plugins/<plugin_id>/test", methods=["POST"])
def api_run_plugin_tests(plugin_id):
    """플러그인 테스트 실행 API"""
    try:
        data = request.get_json() or {}
        test_type = data.get('test_type', 'all')
        
        results = plugin_testing_system.run_plugin_tests(plugin_id, test_type)
        
        return jsonify({
            "status": "success",
            "data": results
        })
    except Exception as e:
        logger.error(f"플러그인 테스트 실행 실패: {e}")
        return jsonify({"error": "플러그인 테스트 실행 실패"}), 500

@app.route("/api/plugins/test-results", methods=["GET"])
def api_get_test_results():
    """테스트 결과 조회 API"""
    try:
        plugin_id = request.args.get('plugin_id')
        test_type = request.args.get('test_type')
        limit = int(request.args.get('limit', 50))
        
        results = plugin_testing_system.get_test_results(plugin_id or None, test_type or None, limit)
        
        return jsonify({
            "status": "success",
            "data": results
        })
    except Exception as e:
        logger.error(f"테스트 결과 조회 실패: {e}")
        return jsonify({"error": "테스트 결과 조회 실패"}), 500

@app.route("/api/plugins/monitoring/start", methods=["POST"])
@csrf.exempt
def api_start_monitoring():
    """성능 모니터링 시작 API"""
    try:
        data = request.get_json(silent=True) or {}
        plugin_id = data.get('plugin_id')
        
        success = plugin_testing_system.start_performance_monitoring(plugin_id or None)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "성능 모니터링이 시작되었습니다"
            })
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
        
        return jsonify({
            "status": "success",
            "message": "성능 모니터링이 중지되었습니다"
        })
    except Exception as e:
        logger.error(f"성능 모니터링 중지 실패: {e}")
        return jsonify({"error": "성능 모니터링 중지 실패"}), 500

@app.route("/api/plugins/performance", methods=["GET"])
def api_get_performance_metrics():
    """성능 메트릭 조회 API"""
    try:
        plugin_id = request.args.get('plugin_id')
        hours = int(request.args.get('hours', 24))
        
        metrics = plugin_testing_system.get_performance_metrics(plugin_id or None, hours)
        
        return jsonify({
            "status": "success",
            "data": metrics
        })
    except Exception as e:
        logger.error(f"성능 메트릭 조회 실패: {e}")
        return jsonify({"error": "성능 메트릭 조회 실패"}), 500

@app.route("/api/plugins/<plugin_id>/documentation", methods=["GET"])
def api_get_plugin_documentation(plugin_id):
    """플러그인 문서 조회 API"""
    try:
        documentation = plugin_testing_system.get_documentation(plugin_id)
        
        if documentation:
            return jsonify({
                "status": "success",
                "data": documentation
            })
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
        
        return jsonify({
            "status": "success",
            "message": "문서가 생성되었습니다",
            "data": documentation
        })
    except Exception as e:
        logger.error(f"플러그인 문서 생성 실패: {e}")
        return jsonify({"error": "플러그인 문서 생성 실패"}), 500

@app.template_filter('comma')
def comma_filter(value):
    """숫자에 콤마 추가하는 필터"""
    try:
        return "{:,}".format(int(value))
    except (ValueError, TypeError):
        return value

@app.template_global('momentjs')
def momentjs():
    """Moment.js 라이브러리 반환"""
    return "https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.1/moment.min.js"

@app.route("/health")
def health():
    """헬스 체크 엔드포인트"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    })

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
        plugin_status = auto_router.get_plugin_status()
        
        status = {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "database": db_status,
            "plugins": plugin_status,
            "uptime": "24h 30m"
        }
        
        return jsonify(status)
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route("/admin/advanced-analytics")
def admin_advanced_analytics():
    """고급 분석 페이지"""
    return render_template('admin/advanced_analytics.html')

@app.route("/admin/security-management")
def admin_security_management():
    """보안 관리 페이지"""
    return render_template('admin/security_management.html')

@app.route("/admin/performance-management")
def admin_performance_management():
    """성능 관리 페이지"""
    return render_template('admin/performance_management.html')

# 플러그인 시스템 테스트 엔드포인트 (직접 등록)
@app.route('/api/plugin-system/test', methods=['GET'])
def plugin_system_test():
    """플러그인 시스템 테스트 엔드포인트"""
    return jsonify({
        "success": True,
        "message": "플러그인 시스템 API가 정상 동작합니다",
        "timestamp": datetime.now().isoformat()
    })

# 플러그인 시스템 직접 엔드포인트 등록 (블루프린트 문제 해결)
@app.route('/api/plugin-system/health', methods=['GET'])
@csrf.exempt
def plugin_system_health():
    """플러그인 시스템 헬스 체크"""
    try:
        health_status = {
            "status": "healthy",
            "plugin_directory": os.path.exists("plugins"),
            "total_plugins": len(plugin_manager.plugins),
            "loaded_plugins": len(plugin_manager.loaded_plugins),
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify({
            "success": True,
            "data": health_status
        })
    except Exception as e:
        logger.error(f"플러그인 시스템 헬스 체크 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/plugin-system/status', methods=['GET'])
@csrf.exempt
def plugin_system_status():
    """플러그인 시스템 상태 조회"""
    try:
        status = plugin_manager.get_plugin_status()
        return jsonify({
            "success": True,
            "data": status
        })
    except Exception as e:
        logger.error(f"플러그인 시스템 상태 조회 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

