# -*- coding: utf-8 -*-
import os
from datetime import date, datetime, timedelta

import jwt
from flask import (Flask, current_app, flash, jsonify, redirect,
                   render_template, request)
from flask_cors import CORS
from flask_login import (current_user, login_required, login_user)

# Import core modules
from config import config_by_name
from extensions import cache, csrf, db, limiter, login_manager, migrate
from models import (Branch, Notification, Order, Schedule, User)

# Import Plugin System
from core.backend.auto_router import setup_auto_router

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

# Setup Auto Router (플러그인 시스템) - 모든 블루프린트 자동 등록
auto_router = setup_auto_router(app)

# CSRF 보호에서 API 블루프린트 제외
# 자동 라우터에서 등록된 모든 블루프린트를 CSRF 제외 목록에 추가
registered_blueprints = auto_router.get_registered_blueprints()
for blueprint_name, blueprint in registered_blueprints.items():
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
        dashboard_info["plugin_status"] = plugin_status
        
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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

