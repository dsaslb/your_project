import os
from collections import defaultdict
from datetime import date, datetime, timedelta

import click
import jwt
from dateutil import parser as date_parser
from flask import (Flask, current_app, flash, jsonify, redirect,
                   render_template, request, send_file, session, url_for)
from flask_cors import CORS
from flask_login import (AnonymousUserMixin, UserMixin, current_user,
                         login_required, login_user, logout_user)
from werkzeug.security import check_password_hash, generate_password_hash

# Import API Blueprints
from api.admin_log import admin_log_bp
from api.admin_report import admin_report_bp
from api.admin_report_stat import admin_report_stat_bp
from api.auth import api_auth_bp, auth_bp
from api.health import health_bp
from api.comment import api_comment_bp
from api.comment_report import comment_report_bp
from api.contracts import contracts_bp
from api.notice import api_notice_bp
from api.report import api_report_bp
from api.staff import staff_bp as api_staff_bp
from api.brand_management import brand_management_bp
from api.store_management import store_management_bp
from api.ai_management import ai_management_bp
from api.approval_workflow import approval_workflow_bp
from api.improvement_requests import improvement_requests_bp
from api.global_data import global_data_bp
from api.ai_analytics import ai_analytics_bp
from api.security_api import security_bp
from api.performance_optimization import performance_bp
from api.integration_api import integration_bp
from api.modules.user_management import user_management
from api.modules.notification_system import notification_system
from api.modules.schedule_management import schedule_management
from api.modules.optimization import optimization
from api.modules.monitoring import monitoring

# Import Route Blueprints
from routes.notifications import notifications_bp
from routes.dashboard import dashboard_bp
from routes.schedule import schedule_bp
from routes.staff import staff_bp as routes_staff_bp
from routes.staff_management import staff_bp as staff_management_bp
from routes.orders import orders_bp
from routes.notice_api import notice_api_bp
from routes.attendance import attendance_bp
from routes.payroll import payroll_bp
from routes.notice import notice_bp

# Import notification functions
from utils.notify import (send_admin_only_notification,
                          send_notification_enhanced,
                          send_notification_to_role)
from routes.admin_dashboard_api import admin_dashboard_api
from api.gateway import gateway as api_gateway

# Import core modules
from config import config_by_name
from extensions import cache, csrf, db, limiter, login_manager, migrate
from models import (Branch, CleaningPlan, FeedbackIssue, Notice, Notification,
                    Order, Report, Schedule, SystemLog, User)

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

# Exempt API blueprints from CSRF protection
api_blueprints = [
    api_auth_bp, api_notice_bp, api_comment_bp, api_report_bp,
    admin_report_bp, admin_log_bp, admin_report_stat_bp,
    comment_report_bp, api_staff_bp, contracts_bp, health_bp,
    brand_management_bp, store_management_bp, ai_management_bp, approval_workflow_bp,
    improvement_requests_bp, user_management, notification_system, schedule_management,
    optimization, monitoring
]

for bp in api_blueprints:
    csrf.exempt(bp)

# Register API Blueprints
app.register_blueprint(api_auth_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(api_notice_bp)
app.register_blueprint(api_comment_bp)
app.register_blueprint(api_report_bp)
app.register_blueprint(admin_report_bp)
app.register_blueprint(admin_log_bp)
app.register_blueprint(admin_report_stat_bp)
app.register_blueprint(comment_report_bp)
app.register_blueprint(api_staff_bp, url_prefix='/api')
app.register_blueprint(contracts_bp)
app.register_blueprint(health_bp, url_prefix='/api')
app.register_blueprint(brand_management_bp, url_prefix='/api')
app.register_blueprint(store_management_bp, url_prefix='/api')
app.register_blueprint(ai_management_bp, url_prefix='/api')
app.register_blueprint(approval_workflow_bp, url_prefix='/api')
app.register_blueprint(improvement_requests_bp, url_prefix='/api')
app.register_blueprint(global_data_bp)
app.register_blueprint(ai_analytics_bp)
app.register_blueprint(security_bp)
app.register_blueprint(performance_bp)
app.register_blueprint(integration_bp)
app.register_blueprint(user_management, url_prefix='/api/modules/user')
app.register_blueprint(notification_system, url_prefix='/api/modules/notification')
app.register_blueprint(schedule_management, url_prefix='/api/modules/schedule')
app.register_blueprint(optimization, url_prefix='/api/modules/optimization')
app.register_blueprint(monitoring, url_prefix='/api/modules/monitoring')

# Register Route Blueprints
app.register_blueprint(payroll_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(notice_api_bp)

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
    """루트 경로 - 로그인 페이지"""
    return render_template('login.html')


@app.route("/dashboard")
def dashboard():
    """대시보드 API 엔드포인트"""
    # Authorization 헤더에서 토큰 확인
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"message": "인증 토큰이 필요합니다."}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({"message": "유효하지 않은 사용자입니다."}), 401
        
        # 기본 통계 데이터
        total_users = User.query.count()
        total_orders = Order.query.count()
        total_schedules = Schedule.query.count()
        
        # 오늘의 통계
        today = date.today()
        today_orders = Order.query.filter(
            Order.created_at >= today
        ).count()
        
        today_schedules = Schedule.query.filter(
            Schedule.date == today
        ).count()
        
        # 주간 통계
        week_ago = today - timedelta(days=7)
        weekly_orders = Order.query.filter(
            Order.created_at >= week_ago
        ).count()
        
        # 월간 통계
        month_ago = today - timedelta(days=30)
        monthly_orders = Order.query.filter(
            Order.created_at >= month_ago
        ).count()
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'email': user.email
            },
            'stats': {
                'total_users': total_users,
                'total_orders': total_orders,
                'total_schedules': total_schedules,
                'today_orders': today_orders,
                'today_schedules': today_schedules,
                'weekly_orders': weekly_orders,
                'monthly_orders': monthly_orders,
                'total_revenue': 1500000,  # 더미 데이터
                'low_stock_items': 3,  # 더미 데이터
            },
            'last_updated': datetime.now().isoformat()
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "토큰이 만료되었습니다."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "유효하지 않은 토큰입니다."}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/dashboard-jwt")
def dashboard_jwt():
    """JWT 토큰 기반 대시보드"""
    # Authorization 헤더에서 토큰 확인
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"message": "인증 토큰이 필요합니다."}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({"message": "유효하지 않은 사용자입니다."}), 401
            
        # 대시보드 템플릿 렌더링 (사용자 정보 포함)
        return render_template('dashboard.html', user=user)
        
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "토큰이 만료되었습니다."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "유효하지 않은 토큰입니다."}), 401

@app.route("/dashboard-simple")
def dashboard_simple():
    """간단한 대시보드 - 토큰 파라미터로 접근"""
    return render_template('dashboard_simple.html')

@app.route("/login-success")
def login_success():
    """로그인 성공 페이지"""
    return render_template('login_success.html')

@app.route("/profile")
@login_required
def profile():
    return render_template('profile.html')


@app.route("/api/profile")
@login_required
def api_profile():
    """사용자 프로필 정보 API"""
    try:
        return jsonify({
            'id': current_user.id,
            'username': current_user.username,
            'name': current_user.name,
            'email': current_user.email,
            'role': current_user.role,
            'is_active': current_user.is_active,
            'created_at': current_user.created_at.isoformat() if current_user.created_at else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/user/profile")
@login_required
def api_user_profile():
    """사용자 프로필 정보 API (대체 경로)"""
    try:
        return jsonify({
            'id': current_user.id,
            'username': current_user.username,
            'name': current_user.name,
            'email': current_user.email,
            'role': current_user.role,
            'is_active': current_user.is_active,
            'created_at': current_user.created_at.isoformat() if current_user.created_at else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/auth/login", methods=["POST"])
def auth_login():
    """프론트엔드 로그인 요청 처리"""
    try:
        # Content-Type에 관계없이 JSON 데이터 처리
        if request.is_json:
            data = request.get_json()
        else:
            # form 데이터도 처리
            data = {
                "username": request.form.get("username"),
                "password": request.form.get("password")
            }
        
        if not data or not data.get("username") or not data.get("password"):
            return jsonify({"message": "사용자명과 비밀번호를 입력해주세요."}), 400

        user = User.query.filter_by(username=data["username"]).first()
        if not user or not user.check_password(data["password"]):
            return jsonify({"message": "잘못된 사용자명 또는 비밀번호입니다."}), 401

        if user.status != "approved":
            return jsonify({"message": "승인 대기 중인 계정입니다."}), 401

        # JWT 토큰 생성
        secret_key = current_app.config.get('JWT_SECRET_KEY', 'your-secret-key')
        
        # 액세스 토큰 (1시간)
        access_token = jwt.encode(
            {
                'user_id': user.id,
                'username': user.username,
                'role': user.role,
                'exp': datetime.utcnow() + timedelta(hours=1)
            },
            secret_key,
            algorithm='HS256'
        )
        
        # 리프레시 토큰 (7일)
        refresh_token = jwt.encode(
            {
                'user_id': user.id,
                'exp': datetime.utcnow() + timedelta(days=7)
            },
            secret_key,
            algorithm='HS256'
        )

        # 사용자 정보 반환 (비밀번호 제외)
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "status": user.status,
            "branch_id": user.branch_id,
        }

        return jsonify({
            "message": "로그인 성공",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user_data,
            "redirect_to": "/dashboard"
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"로그인 처리 중 오류가 발생했습니다: {str(e)}"}), 500


@app.route("/admin_dashboard")
def admin_dashboard():
    # 최고관리자 대시보드 최신 UI/UX 템플릿 렌더링 (더미 데이터 포함)
    total_staff = 42
    total_branches = 7
    notifications = [
        {"title": "신규 직원 등록 요청", "type": "info"},
        {"title": "매장 점검 필요", "type": "warning"},
        {"title": "긴급 시스템 점검", "type": "critical"}
    ]
    total_sales = 12345678
    return render_template(
        'admin_dashboard.html',
        total_staff=total_staff,
        total_branches=total_branches,
        notifications=notifications,
        total_sales=total_sales
    )

@app.route("/admin_dashboard/<int:branch_id>")
@login_required
def admin_branch_dashboard(branch_id):
    # 특정 매장 관리자 대시보드 템플릿 렌더링
    return render_template('admin/branch_dashboard.html', branch_id=branch_id)


@app.route("/schedule", methods=["GET"])
@login_required
def schedule():
    # 백엔드 스케줄 페이지 템플릿 렌더링
    return render_template('schedule.html')


@app.route("/staff")
@login_required
def staff():
    # Next.js 프론트엔드 직원 관리 페이지로 리다이렉트
    return redirect("http://192.168.45.44:3000/staff")


@app.route("/attendance")
@login_required
def attendance():
    # Next.js 프론트엔드 근태 관리 페이지로 리다이렉트
    return redirect("http://192.168.45.44:3000/attendance")


@app.route("/orders")
@login_required
def orders():
    # Next.js 프론트엔드 주문 관리 페이지로 리다이렉트
    return redirect("http://192.168.45.44:3000/orders")


@app.route("/inventory")
@login_required
def inventory():
    # Next.js 프론트엔드 재고 관리 페이지로 리다이렉트
    return redirect("http://192.168.45.44:3000/inventory")


@app.route("/reports")
@login_required
def reports():
    # Next.js 프론트엔드 리포트 페이지로 리다이렉트
    return redirect("http://192.168.45.44:3000/reports")


@app.route("/analytics")
@login_required
def analytics():
    # Next.js 프론트엔드 분석 페이지로 리다이렉트
    return redirect("http://192.168.45.44:3000/analytics")


@app.route("/settings")
@login_required
def settings():
    # Next.js 프론트엔드 설정 페이지로 리다이렉트
    return redirect("http://192.168.45.44:3000/settings")


@app.route("/clean")
@login_required
def clean():
    # 청소 스케줄만 조회
    return render_template('clean.html')


@app.route("/clean_manage")
@login_required
def clean_manage():
    if current_user.role not in ['admin', 'brand_admin', 'manager']:
        flash('접근 권한이 없습니다.', 'error')
        return redirect(url_for('dashboard'))
    
    # 청소 관리 페이지
    return render_template('clean_manage.html')


@app.route("/notifications")
@login_required
def notifications():
    # 사용자별 알림 조회
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('notifications.html', notifications=notifications)


@app.route("/notifications/mark_read/<int:notification_id>")
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    # 본인의 알림만 수정 가능
    if notification.user_id != current_user.id:
        flash('권한이 없습니다.', 'error')
        return redirect(url_for('notifications'))
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.session.commit()
    
    flash('알림을 읽음 처리했습니다.', 'success')
    return redirect(url_for('notifications'))


@app.route("/notifications/mark_all_read")
@login_required
def mark_all_notifications_read():
    # 사용자의 모든 미읽은 알림을 읽음 처리
    Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).update({
        'is_read': True,
        'read_at': datetime.utcnow()
    })
    db.session.commit()
    
    flash('모든 알림을 읽음 처리했습니다.', 'success')
    return redirect(url_for('notifications'))


@app.route("/api/new_notifications")
@login_required
def api_new_notifications():
    """새로운 알림 API"""
    notifications = Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).order_by(Notification.created_at.desc()).limit(10).all()
    
    return jsonify([{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'created_at': n.created_at.isoformat(),
        'type': n.type
    } for n in notifications])


@app.route("/api/notifications/unread-count")
def api_notifications_unread_count():
    """미읽은 알림 개수 API"""
    try:
        if current_user.is_authenticated:
            count = Notification.query.filter_by(
                user_id=current_user.id, is_read=False
            ).count()
            return jsonify({'count': count})
        return jsonify({'count': 0})
    except Exception as e:
        return jsonify({'error': str(e), 'count': 0}), 500


@app.route("/admin/user_permissions")
@login_required
def admin_user_permissions():
    if current_user.role not in ['admin', 'brand_admin']:
        flash('접근 권한이 없습니다.', 'error')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    return render_template('admin/user_permissions.html', users=users)


@app.route("/api/user/<int:user_id>/permissions")
@login_required
def api_user_permissions(user_id):
    if current_user.role not in ['admin', 'brand_admin']:
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    user = User.query.get_or_404(user_id)
    return jsonify({
        'user_id': user.id,
        'username': user.username,
        'role': user.role,
        'permissions': user.permissions or {}
    })


@app.route("/api/user/<int:user_id>/permissions", methods=["POST"])
@login_required
def api_update_user_permissions(user_id):
    if current_user.role not in ['admin', 'brand_admin']:
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    user.permissions = data.get('permissions', {})
    db.session.commit()
    
    return jsonify({'message': '권한이 업데이트되었습니다.'})


@app.route("/api/permissions/templates")
@login_required
def api_permission_templates():
    if current_user.role not in ['admin', 'brand_admin']:
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    templates = {
        'manager': {
            'schedule_management': True,
            'staff_management': True,
            'order_management': True,
            'reports_view': True
        },
        'employee': {
            'schedule_view': True,
            'order_view': True,
            'reports_view': False
        }
    }
    
    return jsonify(templates)


@app.route("/admin/notify_send")
@login_required
def admin_notify_send():
    if current_user.role not in ['admin', 'brand_admin']:
        flash('접근 권한이 없습니다.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        message = request.form.get('message')
        target_role = request.form.get('target_role')
        target_branch = request.form.get('target_branch')
        
        if not title or not message:
            flash('제목과 내용을 입력해주세요.', 'error')
            return redirect(url_for('admin_notify_send'))
        
        # 알림 전송 로직
        if target_role == 'all':
            # 모든 사용자에게 알림
            users = User.query.filter_by(status='approved').all()
            for user in users:
                send_notification_enhanced(user.id, message, title)
        elif target_branch:
            # 특정 매장 사용자에게 알림
            users = User.query.filter_by(branch_id=target_branch, status='approved').all()
            for user in users:
                send_notification_enhanced(user.id, message, title)
        else:
            # 특정 역할 사용자에게 알림
            users = User.query.filter_by(role=target_role, status='approved').all()
            for user in users:
                send_notification_enhanced(user.id, message, title)
        
        flash('알림이 전송되었습니다.', 'success')
        return redirect(url_for('admin_notify_send'))
    
    branches = Branch.query.all()
    return render_template('admin/notify_send.html', branches=branches)


@app.route("/admin/reports")
@login_required
def admin_reports():
    if current_user.role not in ['admin', 'brand_admin']:
        flash('접근 권한이 없습니다.', 'error')
        return redirect(url_for('dashboard'))
    
    # 관리자용 리포트 페이지
    return render_template('admin/reports.html')


@app.route("/admin/statistics")
@login_required
def admin_statistics():
    if current_user.role not in ['admin', 'brand_admin']:
        flash('접근 권한이 없습니다.', 'error')
        return redirect(url_for('dashboard'))
    
    # 통계 데이터 조회
    total_users = User.query.count()
    total_orders = Order.query.count()
    total_schedules = Schedule.query.count()
    
    return render_template('admin/statistics.html', 
                         total_users=total_users,
                         total_orders=total_orders,
                         total_schedules=total_schedules)


@app.route("/admin/system_monitor")
@login_required
def admin_system_monitor():
    if current_user.role not in ['admin', 'brand_admin']:
        flash('접근 권한이 없습니다.', 'error')
        return redirect(url_for('dashboard'))
    
    # 시스템 모니터링 페이지
    return render_template('admin/system_monitor.html')


@app.route("/admin/backup_management")
@login_required
def admin_backup_management():
    if current_user.role not in ['admin', 'brand_admin']:
        flash('접근 권한이 없습니다.', 'error')
        return redirect(url_for('dashboard'))
    
    # 백업 관리 페이지
    return render_template('admin/backup_management.html')


@app.route("/admin/dashboard_mode")
@login_required
def admin_dashboard_mode():
    if current_user.role not in ['admin', 'brand_admin']:
        flash('접근 권한이 없습니다.', 'error')
        return redirect(url_for('dashboard'))
    
    # 대시보드 모드 설정 페이지
    return render_template('admin/dashboard_mode.html')


@app.route("/admin/feedback_management")
@login_required
def admin_feedback_management():
    if current_user.role not in ['admin', 'brand_admin']:
        flash('접근 권한이 없습니다.', 'error')
        return redirect(url_for('dashboard'))
    
    # 피드백 관리 페이지
    return render_template('admin/feedback_management.html')


@app.route("/api/schedule", methods=["POST"])
@login_required
def api_add_schedule():
    if current_user.role not in ['admin', 'brand_admin', 'manager']:
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    data = request.get_json()
    
    schedule = Schedule()
    schedule.user_id = data.get('user_id')
    schedule.date = date_parser.parse(data['date']).date()
    schedule.start_time = date_parser.parse(data['start_time']).time()
    schedule.end_time = date_parser.parse(data['end_time']).time()
    schedule.type = data.get('type', 'work')
    schedule.category = data.get('category', '근무')
    
    db.session.add(schedule)
    db.session.commit()
    
    return jsonify({'message': '스케줄이 추가되었습니다.', 'id': schedule.id})


@app.route("/api/schedule/<int:schedule_id>", methods=["PUT"])
@login_required
def api_update_schedule(schedule_id):
    if current_user.role not in ['admin', 'brand_admin', 'manager']:
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    schedule = Schedule.query.get_or_404(schedule_id)
    data = request.get_json()
    
    schedule.date = date_parser.parse(data['date']).date()
    schedule.start_time = date_parser.parse(data['start_time']).time()
    schedule.end_time = date_parser.parse(data['end_time']).time()
    schedule.type = data.get('type', 'work')
    schedule.category = data.get('category', '근무')
    
    db.session.commit()
    
    return jsonify({'message': '스케줄이 업데이트되었습니다.'})


@app.route("/api/schedule/<int:schedule_id>", methods=["DELETE"])
@login_required
def api_delete_schedule(schedule_id):
    if current_user.role not in ['admin', 'brand_admin', 'manager']:
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    schedule = Schedule.query.get_or_404(schedule_id)
    db.session.delete(schedule)
    db.session.commit()
    
    return jsonify({'message': '스케줄이 삭제되었습니다.'})


@app.route("/api/schedule/<int:schedule_id>", methods=["GET"])
@login_required
def api_get_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    
    return jsonify({
        'id': schedule.id,
        'user_id': schedule.user_id,
        'date': schedule.date.isoformat(),
        'start_time': schedule.start_time.isoformat(),
        'end_time': schedule.end_time.isoformat(),
        'type': schedule.type,
        'category': schedule.category
    })


@app.route("/api/users")
@login_required
def api_get_users():
    """직원 목록 API - 통합 API로 리다이렉트"""
    # 통합 API로 리다이렉트
    return redirect(url_for('api.staff.get_staff_list'))


@app.route("/api/dashboard/stats")
# @login_required  # 임시로 인증 우회 (테스트용)
def api_dashboard_stats():
    """대시보드 통계 API"""
    try:
        # 기본 통계 데이터
        total_users = User.query.count()
        total_orders = Order.query.count()
        total_schedules = Schedule.query.count()
        
        # 오늘의 통계
        today = date.today()
        today_orders = Order.query.filter(
            Order.created_at >= today
        ).count()
        
        today_schedules = Schedule.query.filter(
            Schedule.date == today
        ).count()
        
        # 주간 통계
        week_ago = today - timedelta(days=7)
        weekly_orders = Order.query.filter(
            Order.created_at >= week_ago
        ).count()
        
        # 월간 통계
        month_ago = today - timedelta(days=30)
        monthly_orders = Order.query.filter(
            Order.created_at >= month_ago
        ).count()
        
        return jsonify({
            'total_users': total_users,
            'total_orders': total_orders,
            'total_schedules': total_schedules,
            'today_orders': today_orders,
            'today_schedules': today_schedules,
            'weekly_orders': weekly_orders,
            'monthly_orders': monthly_orders,
            'last_updated': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/dashboard/realtime")
# @login_required  # 임시로 인증 우회 (테스트용)
def api_realtime_activities():
    """실시간 활동 API"""
    try:
        # 최근 활동 데이터
        recent_orders = Order.query.order_by(
            Order.created_at.desc()
        ).limit(5).all()
        
        recent_schedules = Schedule.query.order_by(
            Schedule.date.desc()
        ).limit(5).all()
        
        recent_users = User.query.order_by(
            User.created_at.desc()
        ).limit(5).all()
        
        return jsonify({
            'recent_orders': [{
                'id': order.id,
                'item': order.item,
                'created_at': order.created_at.isoformat(),
                'status': order.status
            } for order in recent_orders],
            'recent_schedules': [{
                'id': schedule.id,
                'user_id': schedule.user_id,
                'date': schedule.date.isoformat(),
                'type': schedule.type,
                'category': schedule.category
            } for schedule in recent_schedules],
            'recent_users': [{
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'created_at': user.created_at.isoformat()
            } for user in recent_users],
            'last_updated': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/dashboard/kitchen-status")
@login_required
def api_kitchen_status():
    """주방 상태 API"""
    try:
        # 주방 관련 주문 상태
        pending_orders = Order.query.filter_by(status='pending').count()
        cooking_orders = Order.query.filter_by(status='cooking').count()
        completed_orders = Order.query.filter_by(status='completed').count()
        
        total_orders = pending_orders + cooking_orders + completed_orders
        return jsonify({
            'pending_orders': pending_orders,
            'cooking_orders': cooking_orders,
            'completed_orders': completed_orders,
            'kitchen_efficiency': (completed_orders / max(total_orders, 1)) * 100,
            'last_updated': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/dashboard/sales")
@login_required
def api_sales():
    """매출 데이터 API"""
    try:
        # 매출 통계 (더미 데이터)
        today_sales = 1500000
        weekly_sales = 8500000
        monthly_sales = 35000000
        
        # 매출 트렌드 (더미 데이터)
        sales_trend = [
            {'date': '2024-01-01', 'sales': 1200000},
            {'date': '2024-01-02', 'sales': 1350000},
            {'date': '2024-01-03', 'sales': 1100000},
            {'date': '2024-01-04', 'sales': 1400000},
            {'date': '2024-01-05', 'sales': 1600000},
            {'date': '2024-01-06', 'sales': 1800000},
            {'date': '2024-01-07', 'sales': 1700000}
        ]
        
        return jsonify({
            'today_sales': today_sales,
            'weekly_sales': weekly_sales,
            'monthly_sales': monthly_sales,
            'sales_trend': sales_trend,
            'last_updated': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/monitor/real-time-data")
@login_required
def api_real_time_monitor_data():
    """실시간 모니터링 데이터 API"""
    try:
        # 실시간 시스템 상태
        system_status = {
            'cpu_usage': 45.2,
            'memory_usage': 67.8,
            'disk_usage': 23.4,
            'network_traffic': 12.5,
            'active_users': User.query.count(),
            'active_orders': Order.query.filter_by(status='pending').count(),
            'system_uptime': '15 days, 8 hours, 32 minutes',
            'last_backup': '2024-01-05 02:00:00',
            'database_status': 'healthy',
            'api_status': 'operational'
        }
        
        return jsonify({
            'system_status': system_status,
            'last_updated': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/monitor/brand-data")
@login_required
def api_brand_monitor_data():
    """브랜드별 모니터링 데이터 API"""
    try:
        # 브랜드별 통계
        branches = Branch.query.all()
        brand_data = []
        
        for branch in branches:
            branch_users = User.query.filter_by(branch_id=branch.id).count()
            branch_orders = Order.query.filter_by(store_id=branch.id).count()
            
            branch_data = {
                'branch_id': branch.id,
                'branch_name': branch.name,
                'total_users': branch_users,
                'total_orders': branch_orders,
                'status': 'active',
                'last_activity': datetime.now().isoformat()
            }
            
            brand_data.append(branch_data)
        
        return jsonify({
            'brands': brand_data,
            'total_branches': len(branches),
            'last_updated': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 매장 관리 API 엔드포인트들
@app.route("/admin/branch-management")
def admin_branch_management():
    """매장 관리 페이지"""
    return render_template('admin/branch_management.html')

@app.route("/api/admin/branch-stats")
def api_admin_branch_stats():
    """매장 통계 API - 테스트용으로 인증 우회"""
    # 테스트용으로 인증 없이 접근 가능하도록 설정
    # auth_header = request.headers.get('Authorization')
    # if not auth_header or not auth_header.startswith('Bearer '):
    #     return jsonify({"message": "인증 토큰이 필요합니다."}), 401
    
    # token = auth_header.split(' ')[1]
    
    # try:
    #     secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
    #     payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
    #     user = User.query.get(payload['user_id'])
    #     if not user or user.role != 'super_admin':
    #         return jsonify({"message": "최고 관리자 권한이 필요합니다."}), 403
        
    # 매장 통계 계산 (더미 데이터)
    stats = {
        'total_branches': 5,
        'active_branches': 4,
        'maintenance_branches': 1,
        'total_staff': 45
    }
    
    return jsonify({
        'success': True,
        'stats': stats
    })
    
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"message": "토큰이 만료되었습니다."}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"message": "유효하지 않은 토큰입니다."}), 401
    # except Exception as e:
    #     return jsonify({'error': str(e)}), 500

@app.route("/api/admin/branch-list")
def api_admin_branch_list():
    """매장 목록 API - 테스트용으로 인증 우회"""
    # 테스트용으로 인증 없이 접근 가능하도록 설정
    # auth_header = request.headers.get('Authorization')
    # if not auth_header or not auth_header.startswith('Bearer '):
    #     return jsonify({"message": "인증 토큰이 필요합니다."}), 401
    
    # token = auth_header.split(' ')[1]
    
    # try:
    #     secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
    #     payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
    #     user = User.query.get(payload['user_id'])
    #     if not user or user.role != 'super_admin':
    #         return jsonify({"message": "최고 관리자 권한이 필요합니다."}), 403
        
    # 더미 매장 데이터
    branches = [
        {
            'id': 1,
            'name': '본점',
            'address': '서울 강남구 테헤란로 123',
            'phone': '02-1234-5678',
            'status': 'active',
            'staff_count': 15,
            'sales': 3200000
        },
        {
            'id': 2,
            'name': '지점1',
            'address': '서울 서초구 서초대로 456',
            'phone': '02-2345-6789',
            'status': 'active',
            'staff_count': 12,
            'sales': 2800000
        },
        {
            'id': 3,
            'name': '지점2',
            'address': '서울 마포구 홍대로 789',
            'phone': '02-3456-7890',
            'status': 'active',
            'staff_count': 10,
            'sales': 2750000
        },
        {
            'id': 4,
            'name': '지점3',
            'address': '서울 송파구 올림픽로 321',
            'phone': '02-4567-8901',
            'status': 'active',
            'staff_count': 8,
            'sales': 2100000
        },
        {
            'id': 5,
            'name': '지점4',
            'address': '서울 영등포구 여의대로 654',
            'phone': '02-5678-9012',
            'status': 'maintenance',
            'staff_count': 0,
            'sales': 0
        }
    ]
    
    return jsonify({
        'success': True,
        'branches': branches
    })
    
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"message": "토큰이 만료되었습니다."}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"message": "유효하지 않은 토큰입니다."}), 401
    # except Exception as e:
    #     return jsonify({'error': str(e)}), 500

@app.route("/api/admin/branch-activities")
def api_admin_branch_activities():
    """매장 활동 API - 테스트용으로 인증 우회"""
    # 테스트용으로 인증 없이 접근 가능하도록 설정
    # auth_header = request.headers.get('Authorization')
    # if not auth_header or not auth_header.startswith('Bearer '):
    #     return jsonify({"message": "인증 토큰이 필요합니다."}), 401
    
    # token = auth_header.split(' ')[1]
    
    # try:
    #     secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
    #     payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
    #     user = User.query.get(payload['user_id'])
    #     if not user or user.role != 'super_admin':
    #         return jsonify({"message": "최고 관리자 권한이 필요합니다."}), 403
        
    # 더미 활동 데이터
    activities = [
        {
            'title': '본점 매출 업데이트',
            'description': '오늘 매출이 320만원으로 기록되었습니다.',
            'timestamp': '2024-01-15T14:30:00'
        },
        {
            'title': '지점1 직원 추가',
            'description': '새 직원 김철수가 지점1에 배치되었습니다.',
            'timestamp': '2024-01-15T13:15:00'
        },
        {
            'title': '지점2 재고 알림',
            'description': '지점2에서 재고 부족 알림이 발생했습니다.',
            'timestamp': '2024-01-15T12:45:00'
        },
        {
            'title': '지점3 점검 완료',
            'description': '지점3 정기 점검이 완료되었습니다.',
            'timestamp': '2024-01-15T11:20:00'
        }
    ]
    
    return jsonify({
        'success': True,
        'activities': activities
    })
    
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"message": "토큰이 만료되었습니다."}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"message": "유효하지 않은 토큰입니다."}), 401
    # except Exception as e:
    #     return jsonify({'error': str(e)}), 500

@app.route("/api/admin/branch-detail/<int:branch_id>")
def api_admin_branch_detail(branch_id):
    """매장 상세 정보 API - 테스트용으로 인증 우회"""
    # 테스트용으로 인증 없이 접근 가능하도록 설정
    # auth_header = request.headers.get('Authorization')
    # if not auth_header or not auth_header.startswith('Bearer '):
    #     return jsonify({"message": "인증 토큰이 필요합니다."}), 401
    
    # token = auth_header.split(' ')[1]
    
    # try:
    #     secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
    #     payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
    #     user = User.query.get(payload['user_id'])
    #     if not user or user.role != 'super_admin':
    #         return jsonify({"message": "최고 관리자 권한이 필요합니다."}), 403
        
    # 더미 매장 데이터 (실제로는 DB에서 조회)
    branch_data = {
        'id': branch_id,
        'name': f'매장{branch_id}',
        'address': f'서울시 강남구 테헤란로 {branch_id}00',
        'phone': f'02-1234-{branch_id:04d}',
        'status': 'active',
        'staff_count': 10 + branch_id,
        'sales': 2000000 + (branch_id * 100000)
    }
    
    return jsonify({
        'success': True,
        'branch': branch_data
    })

@app.route("/api/admin/add-branch", methods=["POST"])
def api_admin_add_branch():
    """매장 추가 API"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"message": "인증 토큰이 필요합니다."}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        user = User.query.get(payload['user_id'])
        if not user or user.role != 'super_admin':
            return jsonify({"message": "최고 관리자 권한이 필요합니다."}), 403
        
        data = request.get_json()
        
        # 실제로는 DB에 저장
        # 여기서는 성공 응답만 반환
        return jsonify({
            'success': True,
            'message': '매장이 성공적으로 추가되었습니다.'
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "토큰이 만료되었습니다."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "유효하지 않은 토큰입니다."}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/admin/update-branch/<int:branch_id>", methods=["PUT"])
def api_admin_update_branch(branch_id):
    """매장 수정 API"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"message": "인증 토큰이 필요합니다."}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        user = User.query.get(payload['user_id'])
        if not user or user.role != 'super_admin':
            return jsonify({"message": "최고 관리자 권한이 필요합니다."}), 403
        
        data = request.get_json()
        
        # 실제로는 DB에서 업데이트
        # 여기서는 성공 응답만 반환
        return jsonify({
            'success': True,
            'message': '매장 정보가 성공적으로 수정되었습니다.'
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "토큰이 만료되었습니다."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "유효하지 않은 토큰입니다."}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/admin/delete-branch/<int:branch_id>", methods=["DELETE"])
def api_admin_delete_branch(branch_id):
    """매장 삭제 API"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"message": "인증 토큰이 필요합니다."}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        user = User.query.get(payload['user_id'])
        if not user or user.role != 'super_admin':
            return jsonify({"message": "최고 관리자 권한이 필요합니다."}), 403
        
        # 실제로는 DB에서 삭제
        # 여기서는 성공 응답만 반환
        return jsonify({
            'success': True,
            'message': '매장이 성공적으로 삭제되었습니다.'
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "토큰이 만료되었습니다."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "유효하지 않은 토큰입니다."}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.cli.command("create-admin")
@click.argument("username")
@click.argument("password")
def create_admin(username, password):
    """관리자 계정 생성 CLI 명령어"""
    user = User.query.filter_by(username=username).first()
    if user:
        click.echo(f"사용자 '{username}'가 이미 존재합니다.")
        return
    
    hashed_password = generate_password_hash(password)
    admin_user = User(
        username=username,
        password_hash=hashed_password,
        role='admin',
        email=f"{username}@restaurant.com",
        name=username,
        status='approved'
    )
    
    db.session.add(admin_user)
    db.session.commit()
    
    click.echo(f"관리자 계정 '{username}'이 생성되었습니다.")


@app.cli.command("update-admin-role")
def update_admin_role():
    """admin 계정을 super_admin 권한으로 업데이트"""
    try:
        admin = User.query.filter_by(username="admin").first()
        if admin:
            admin.role = "super_admin"
            admin.status = "approved"
            db.session.commit()
            print("✅ admin 계정이 super_admin 권한으로 업데이트되었습니다.")
        else:
            print("❌ admin 계정을 찾을 수 없습니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")


# OPTIONS 요청 처리
@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


@app.route("/api/auth/profile-jwt")
def api_profile_jwt():
    """JWT 토큰 기반 사용자 프로필 정보 API"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"message": "인증 토큰이 필요합니다."}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({"message": "유효하지 않은 사용자입니다."}), 401
            
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'status': user.status,
                'branch_id': user.branch_id
            }
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "토큰이 만료되었습니다."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "유효하지 않은 토큰입니다."}), 401


@app.route("/api/dashboard/stats-jwt")
def api_dashboard_stats_jwt():
    """JWT 토큰 기반 대시보드 통계 API"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"message": "인증 토큰이 필요합니다."}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({"message": "유효하지 않은 사용자입니다."}), 401
        
        # 기본 통계 데이터
        total_users = User.query.count()
        total_orders = Order.query.count()
        total_schedules = Schedule.query.count()
        
        # 오늘의 통계
        today = date.today()
        today_orders = Order.query.filter(
            Order.created_at >= today
        ).count()
        
        today_schedules = Schedule.query.filter(
            Schedule.date == today
        ).count()
        
        # 주간 통계
        week_ago = today - timedelta(days=7)
        weekly_orders = Order.query.filter(
            Order.created_at >= week_ago
        ).count()
        
        # 월간 통계
        month_ago = today - timedelta(days=30)
        monthly_orders = Order.query.filter(
            Order.created_at >= month_ago
        ).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_orders': total_orders,
                'total_revenue': 1500000,  # 더미 데이터
                'total_staff': total_users,
                'low_stock_items': 3,  # 더미 데이터
                'today_orders': today_orders,
                'today_schedules': today_schedules,
                'weekly_orders': weekly_orders,
                'monthly_orders': monthly_orders
            },
            'last_updated': datetime.now().isoformat()
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "토큰이 만료되었습니다."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "유효하지 않은 토큰입니다."}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/super-admin-dashboard")
def super_admin_dashboard():
    """슈퍼 관리자 대시보드 - 테스트용으로 인증 우회"""
    # 테스트용으로 인증 없이 접근 가능하도록 설정
    return render_template('admin/super_admin_dashboard.html')

# 최고 관리자 API 엔드포인트들
@app.route("/api/admin/dashboard-stats")
def api_admin_dashboard_stats():
    """최고 관리자 대시보드 통계 API"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"message": "인증 토큰이 필요합니다."}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        user = User.query.get(payload['user_id'])
        if not user or user.role != 'super_admin':
            return jsonify({"message": "최고 관리자 권한이 필요합니다."}), 403
        
        # 통계 데이터 계산
        total_staff = User.query.count()
        total_branches = Branch.query.count()
        pending_approvals = User.query.filter_by(status='pending').count()
        critical_alerts = 3  # 더미 데이터
        total_orders = Order.query.count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_staff': total_staff,
                'total_branches': total_branches,
                'pending_approvals': pending_approvals,
                'critical_alerts': critical_alerts,
                'total_orders': total_orders
            }
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "토큰이 만료되었습니다."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "유효하지 않은 토큰입니다."}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route("/api/admin/system-logs")
def api_admin_system_logs():
    """시스템 로그 API"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"message": "인증 토큰이 필요합니다."}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        user = User.query.get(payload['user_id'])
        if not user or user.role != 'super_admin':
            return jsonify({"message": "최고 관리자 권한이 필요합니다."}), 403
        
        # 더미 시스템 로그 데이터
        from datetime import datetime, timedelta
        import random
        
        log_levels = ['info', 'warning', 'error']
        log_messages = [
            '사용자 로그인 성공',
            '데이터베이스 연결 확인',
            '캐시 업데이트 완료',
            '백업 작업 시작',
            '시스템 점검 완료',
            '메모리 사용량 증가 감지',
            '네트워크 연결 확인',
            '보안 스캔 완료'
        ]
        
        logs = []
        for i in range(10):
            timestamp = datetime.now() - timedelta(minutes=random.randint(0, 60))
            logs.append({
                'timestamp': timestamp.isoformat(),
                'level': random.choice(log_levels),
                'message': random.choice(log_messages)
            })
        
        # 시간순 정렬
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'success': True,
            'logs': logs
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "토큰이 만료되었습니다."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "유효하지 않은 토큰입니다."}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/admin/critical-alerts")
def api_admin_critical_alerts():
    """긴급 알림 API"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"message": "인증 토큰이 필요합니다."}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        user = User.query.get(payload['user_id'])
        if not user or user.role != 'super_admin':
            return jsonify({"message": "최고 관리자 권한이 필요합니다."}), 403
        
        # 긴급 알림 (더미 데이터)
        alerts = [
            {
                'level': 'critical',
                'title': '보건증 만료 임박',
                'description': '홍길동님의 보건증이 3일 후 만료됩니다.',
                'timestamp': datetime.now() - timedelta(hours=1)
            },
            {
                'level': 'warning',
                'title': '재고 부족',
                'description': '강남점의 김치 재고가 부족합니다.',
                'timestamp': datetime.now() - timedelta(hours=2)
            },
            {
                'level': 'info',
                'title': '시스템 업데이트',
                'description': '새로운 시스템 업데이트가 준비되었습니다.',
                'timestamp': datetime.now() - timedelta(hours=3)
            }
        ]
        
        return jsonify({
            'success': True,
            'alerts': alerts
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "토큰이 만료되었습니다."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "유효하지 않은 토큰입니다."}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/admin/pending-approvals")
def api_admin_pending_approvals():
    """승인 대기 목록 API"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"message": "인증 토큰이 필요합니다."}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        user = User.query.get(payload['user_id'])
        if not user or user.role != 'super_admin':
            return jsonify({"message": "최고 관리자 권한이 필요합니다."}), 403
        
        # 승인 대기 목록 (실제 DB에서 가져오기)
        pending_users = User.query.filter_by(status='pending').limit(5).all()
        
        approvals = [{
            'type': '직원 가입',
            'username': u.username,
            'description': f'{u.username}님의 가입 신청',
            'created_at': u.created_at
        } for u in pending_users]
        
        return jsonify({
            'success': True,
            'approvals': approvals
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "토큰이 만료되었습니다."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "유효하지 않은 토큰입니다."}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/admin/system-status")
def api_admin_system_status():
    """시스템 상태 API"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"message": "인증 토큰이 필요합니다."}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        user = User.query.get(payload['user_id'])
        if not user or user.role != 'super_admin':
            return jsonify({"message": "최고 관리자 권한이 필요합니다."}), 403
        
        # 시스템 상태 (더미 데이터)
        status = {
            'cpu_usage': 45.2,
            'memory_usage': 67.8,
            'disk_usage': 23.4,
            'database_status': '정상',
            'last_backup': datetime.now() - timedelta(hours=6)
        }
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "토큰이 만료되었습니다."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "유효하지 않은 토큰입니다."}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 직원 관리 API 엔드포인트들
@app.route("/admin/staff-management")
def admin_staff_management():
    """직원 관리 페이지"""
    return render_template('admin/staff_management.html')

@app.route("/api/admin/staff-list")
def api_admin_staff_list():
    """직원 목록 API"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"message": "인증 토큰이 필요합니다."}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        user = User.query.get(payload['user_id'])
        if not user or user.role != 'super_admin':
            return jsonify({"message": "최고 관리자 권한이 필요합니다."}), 403
        
        # 필터 파라미터 가져오기
        name_filter = request.args.get('name', '')
        role_filter = request.args.get('role', '')
        status_filter = request.args.get('status', '')
        
        # 쿼리 구성
        query = User.query
        
        if name_filter:
            query = query.filter(
                db.or_(
                    User.username.contains(name_filter),
                    User.name.contains(name_filter)
                )
            )
        
        if role_filter:
            query = query.filter(User.role == role_filter)
        
        if status_filter:
            query = query.filter(User.status == status_filter)
        
        # 정렬 및 결과 가져오기
        staff_list = query.order_by(User.created_at.desc()).all()
        
        staff_data = [{
            'id': s.id,
            'username': s.username,
            'name': s.name,
            'email': s.email,
            'role': s.role,
            'status': s.status,
            'created_at': s.created_at.isoformat() if s.created_at else None,
            'last_login': s.last_login.isoformat() if s.last_login else None
        } for s in staff_list]
        
        return jsonify({
            'success': True,
            'staff': staff_data
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "토큰이 만료되었습니다."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "유효하지 않은 토큰입니다."}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/admin/staff-detail/<int:user_id>")
def api_admin_staff_detail(user_id):
    """직원 상세 정보 API"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"message": "인증 토큰이 필요합니다."}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        user = User.query.get(payload['user_id'])
        if not user or user.role != 'super_admin':
            return jsonify({"message": "최고 관리자 권한이 필요합니다."}), 403
        
        # 대상 직원 정보 가져오기
        target_staff = User.query.get(user_id)
        if not target_staff:
            return jsonify({"message": "직원을 찾을 수 없습니다."}), 404
        
        staff_data = {
            'id': target_staff.id,
            'username': target_staff.username,
            'name': target_staff.name,
            'email': target_staff.email,
            'role': target_staff.role,
            'status': target_staff.status,
            'created_at': target_staff.created_at.isoformat() if target_staff.created_at else None,
            'last_login': target_staff.last_login.isoformat() if target_staff.last_login else None,
            'branch_id': target_staff.branch_id
        }
        
        return jsonify({
            'success': True,
            'staff': staff_data
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "토큰이 만료되었습니다."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "유효하지 않은 토큰입니다."}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/admin/update-staff-role/<int:user_id>", methods=["PUT"])
def api_admin_update_staff_role(user_id):
    """직원 권한 변경 API"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"message": "인증 토큰이 필요합니다."}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        user = User.query.get(payload['user_id'])
        if not user or user.role != 'super_admin':
            return jsonify({"message": "최고 관리자 권한이 필요합니다."}), 403
        
        data = request.get_json()
        new_role = data.get('role')
        new_status = data.get('status')
        
        if not new_role or not new_status:
            return jsonify({"message": "역할과 상태를 모두 지정해주세요."}), 400
        
        # 대상 직원 정보 가져오기
        target_staff = User.query.get(user_id)
        if not target_staff:
            return jsonify({"message": "직원을 찾을 수 없습니다."}), 404
        
        # 권한 변경
        target_staff.role = new_role
        target_staff.status = new_status
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '권한이 성공적으로 변경되었습니다.'
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "토큰이 만료되었습니다."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "유효하지 않은 토큰입니다."}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/admin/delete-staff/<int:user_id>", methods=["DELETE"])
def api_admin_delete_staff(user_id):
    """직원 삭제 API"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"message": "인증 토큰이 필요합니다."}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        user = User.query.get(payload['user_id'])
        if not user or user.role != 'super_admin':
            return jsonify({"message": "최고 관리자 권한이 필요합니다."}), 403
        
        # 대상 직원 정보 가져오기
        target_staff = User.query.get(user_id)
        if not target_staff:
            return jsonify({"message": "직원을 찾을 수 없습니다."}), 404
        
        # 자기 자신은 삭제할 수 없음
        if target_staff.id == user.id:
            return jsonify({"message": "자기 자신은 삭제할 수 없습니다."}), 400
        
        # 직원 삭제
        db.session.delete(target_staff)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '직원이 성공적으로 삭제되었습니다.'
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "토큰이 만료되었습니다."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "유효하지 않은 토큰입니다."}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 시스템 모니터링 API 엔드포인트들
@app.route("/admin/system-monitoring")
def admin_system_monitoring():
    """시스템 모니터링 페이지"""
    return render_template('admin/system_monitoring.html')

@app.route("/api/admin/system-stats")
def api_admin_system_stats():
    """시스템 통계 API"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"message": "인증 토큰이 필요합니다."}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        user = User.query.get(payload['user_id'])
        if not user or user.role != 'super_admin':
            return jsonify({"message": "최고 관리자 권한이 필요합니다."}), 403
        
        # 더미 시스템 통계 데이터
        import random
        stats = {
            'cpu_usage': random.randint(20, 80),
            'memory_usage': random.randint(30, 70),
            'disk_usage': random.randint(40, 90),
            'active_users': random.randint(10, 50)
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "토큰이 만료되었습니다."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "유효하지 않은 토큰입니다."}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/admin/service-status")
def api_admin_service_status():
    """서비스 상태 API"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"message": "인증 토큰이 필요합니다."}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        user = User.query.get(payload['user_id'])
        if not user or user.role != 'super_admin':
            return jsonify({"message": "최고 관리자 권한이 필요합니다."}), 403
        
        # 더미 서비스 상태 데이터
        import random
        services = [
            {
                'name': '웹 서버',
                'status': 'online',
                'response_time': random.randint(10, 50)
            },
            {
                'name': '데이터베이스',
                'status': 'online',
                'response_time': random.randint(5, 20)
            },
            {
                'name': 'Redis 캐시',
                'status': 'online',
                'response_time': random.randint(1, 10)
            },
            {
                'name': 'AI 서비스',
                'status': 'warning',
                'response_time': random.randint(100, 300)
            },
            {
                'name': '파일 스토리지',
                'status': 'online',
                'response_time': random.randint(20, 80)
            }
        ]
        
        return jsonify({
            'success': True,
            'services': services
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "토큰이 만료되었습니다."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "유효하지 않은 토큰입니다."}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/admin/system-alerts")
def api_admin_system_alerts():
    """시스템 알림 API"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"message": "인증 토큰이 필요합니다."}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        user = User.query.get(payload['user_id'])
        if not user or user.role != 'super_admin':
            return jsonify({"message": "최고 관리자 권한이 필요합니다."}), 403
        
        # 더미 알림 데이터
        from datetime import datetime, timedelta
        import random
        
        alerts = [
            {
                'title': '메모리 사용량 경고',
                'message': '메모리 사용량이 80%를 초과했습니다.',
                'level': 'warning',
                'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat()
            },
            {
                'title': 'AI 서비스 응답 지연',
                'message': 'AI 서비스 응답 시간이 200ms를 초과했습니다.',
                'level': 'warning',
                'timestamp': (datetime.now() - timedelta(minutes=15)).isoformat()
            },
            {
                'title': '시스템 백업 완료',
                'message': '일일 시스템 백업이 성공적으로 완료되었습니다.',
                'level': 'info',
                'timestamp': (datetime.now() - timedelta(hours=1)).isoformat()
            }
        ]
        
        return jsonify({
            'success': True,
            'alerts': alerts
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "토큰이 만료되었습니다."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "유효하지 않은 토큰입니다."}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Jinja2 comma 필터 등록
@app.template_filter('comma')
def comma_filter(value):
    try:
        return f"{int(value):,}"
    except Exception:
        return value

# Jinja2 momentjs 함수 등록 (날짜/시간 포맷팅용)
@app.template_global('momentjs')
def momentjs():
    from datetime import datetime
    return datetime.now()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
