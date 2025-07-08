import os
from collections import defaultdict
from datetime import date, datetime, timedelta

import click
from dateutil import parser as date_parser
from flask import (Flask, current_app, flash, jsonify, redirect,
                   render_template, request, session, url_for)
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

CORS(app,
     origins=[
         "http://localhost:3000",
         "http://127.0.0.1:3000",
         "http://192.168.45.44:3000",
         "http://localhost:3001",
         "http://127.0.0.1:3001",
         "http://192.168.45.44:3001"
     ],
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"])

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
    comment_report_bp, api_staff_bp, contracts_bp, health_bp
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

# Register Route Blueprints
app.register_blueprint(payroll_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(notice_api_bp)

# Login manager setup
login_manager.login_view = "auth.login"
login_manager.login_message = "로그인이 필요합니다."
login_manager.login_message_category = "info"
login_manager.anonymous_user = AnonymousUserMixin


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
    return app.send_static_file('favicon.ico')


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
@login_required
def index():
    return redirect(url_for('dashboard'))


@app.route("/dashboard")
@login_required
def dashboard():
    # Next.js 프론트엔드 대시보드로 리다이렉트
    return redirect("http://localhost:3000/dashboard")


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


@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    # 브랜드 관리자인 경우 브랜드 관리자 대시보드로 리다이렉트
    if current_user.role == 'brand_admin':
        return redirect("http://localhost:3000/brand-dashboard")
    # 일반 관리자인 경우 관리자 대시보드로 리다이렉트
    return redirect("http://localhost:3000/admin-dashboard")


@app.route("/admin_dashboard/<int:branch_id>")
@login_required
def admin_branch_dashboard(branch_id):
    # 특정 매장 관리자 대시보드로 리다이렉트
    return redirect(f"http://localhost:3000/brand-dashboard/branches/{branch_id}")


@app.route("/schedule", methods=["GET"])
@login_required
def schedule():
    # Next.js 프론트엔드 스케줄 페이지로 리다이렉트
    return redirect("http://localhost:3000/schedule")


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
@login_required
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
            send_notification_enhanced(title, message, role=target_role)
        elif target_branch:
            send_notification_enhanced(title, message, branch_id=target_branch)
        else:
            send_notification_enhanced(title, message, role=target_role)
        
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
    
    schedule = Schedule(
        user_id=data['user_id'],
        date=date_parser.parse(data['date']).date(),
        start_time=date_parser.parse(data['start_time']).time(),
        end_time=date_parser.parse(data['end_time']).time(),
        role=data['role']
    )
    
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
    schedule.role = data['role']
    
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
        'role': schedule.role
    })


@app.route("/api/users")
@login_required
def api_get_users():
    if current_user.role not in ['admin', 'brand_admin']:
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'role': user.role,
        'branch_id': user.branch_id
    } for user in users])


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
                'title': order.title,
                'created_at': order.created_at.isoformat(),
                'status': order.status
            } for order in recent_orders],
            'recent_schedules': [{
                'id': schedule.id,
                'user_id': schedule.user_id,
                'date': schedule.date.isoformat(),
                'role': schedule.role
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
            branch_orders = Order.query.filter_by(branch_id=branch.id).count()
            
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


@app.route("/admin/branch_management")
@login_required
def admin_branch_management():
    if current_user.role not in ['admin', 'brand_admin']:
        flash('접근 권한이 없습니다.', 'error')
        return redirect(url_for('dashboard'))
    
    # 매장 관리 페이지
    branches = Branch.query.all()
    return render_template('admin/branch_management.html', branches=branches)


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
        email=f"{username}@restaurant.com"
    )
    
    db.session.add(admin_user)
    db.session.commit()
    
    click.echo(f"관리자 계정 '{username}'이 생성되었습니다.")


# OPTIONS 요청 처리
@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
