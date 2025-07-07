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

from api.admin_log import admin_log_bp
from api.admin_report import admin_report_bp
from api.admin_report_stat import admin_report_stat_bp
# Import API Blueprints
from api.auth import api_auth_bp, auth_bp
from api.health import health_bp
from api.comment import api_comment_bp
from api.comment_report import comment_report_bp
from api.contracts import contracts_bp
from api.notice import api_notice_bp
from api.report import api_report_bp
from api.staff import staff_bp as api_staff_bp
from api.role_based_routes import role_routes
from config import config_by_name
from extensions import cache, csrf, db, limiter, login_manager, migrate
from models import (Branch, CleaningPlan, FeedbackIssue, Notice, Notification,
                    Order, Report, Schedule, SystemLog, User)
from routes.notifications import notifications_bp
from routes.dashboard import dashboard_bp
from routes.schedule import schedule_bp
from routes.staff import staff_bp as routes_staff_bp
from routes.staff_management import staff_bp as staff_management_bp
from routes.orders import orders_bp
from routes.inventory import inventory_bp
from routes.notice_api import notice_api_bp
from routes.attendance import attendance_bp
# Import Route Blueprints
from routes.payroll import payroll_bp
from routes.notice import notice_bp
# Import notification functions
from utils.notify import (send_admin_only_notification,
                          send_notification_enhanced,
                          send_notification_to_role)
from routes.admin_dashboard_api import admin_dashboard_api
from api.gateway import gateway

# 새로운 모듈들
from api.modules.user_management import user_management
from api.modules.notification_system import notification_system
from api.modules.schedule_management import schedule_management
from api.modules.restaurant.qsc_system import qsc_system
from api.modules.optimization import optimization
from api.modules.security import security
from api.modules.monitoring import monitoring
from api.modules.automation import automation
from api.modules.analytics import analytics
from api.modules.chat_system import chat_bp, register_chat_events
from api.modules.reporting_system import reporting_bp
from api.modules.visualization import visualization_bp

config_name = os.getenv("FLASK_ENV", "default")

app = Flask(__name__)
app.config.from_object(config_by_name[config_name])

# Initialize CORS
CORS(app, origins=[
    'http://localhost:3000',
    'http://localhost:3001',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:3001',
    'http://192.168.45.44:3000',
    'http://192.168.45.44:3001'
], supports_credentials=True)

# Initialize extensions
csrf.init_app(app)
db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
limiter.init_app(app)
cache.init_app(app)

# Exempt all API blueprints from CSRF protection
csrf.exempt(api_auth_bp)
csrf.exempt(api_notice_bp)
csrf.exempt(api_comment_bp)
csrf.exempt(api_report_bp)
csrf.exempt(admin_report_bp)
csrf.exempt(admin_log_bp)
csrf.exempt(admin_report_stat_bp)
csrf.exempt(comment_report_bp)
csrf.exempt(api_staff_bp)
csrf.exempt(contracts_bp)
csrf.exempt(health_bp)
csrf.exempt(role_routes)

# Exempt optimization modules from CSRF protection
csrf.exempt(optimization)
csrf.exempt(security)
csrf.exempt(monitoring)
csrf.exempt(notification_system)
csrf.exempt(automation)
csrf.exempt(analytics)
csrf.exempt(user_management)
csrf.exempt(schedule_management)
csrf.exempt(qsc_system)
csrf.exempt(monitoring)
csrf.exempt(security)
csrf.exempt(visualization_bp)

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
app.register_blueprint(role_routes)

# Register optimization modules
app.register_blueprint(optimization, url_prefix='/api/optimization')
app.register_blueprint(security, url_prefix='/api/security')
app.register_blueprint(monitoring, url_prefix='/api/monitoring')
app.register_blueprint(notification_system, url_prefix='/api/notification-system')
app.register_blueprint(automation, url_prefix='/api/automation')
app.register_blueprint(analytics, url_prefix='/api/analytics')
app.register_blueprint(user_management, url_prefix='/api/user-management')
app.register_blueprint(schedule_management, url_prefix='/api/schedule-management')
app.register_blueprint(qsc_system, url_prefix='/api/qsc-system')
app.register_blueprint(monitoring, url_prefix='/api/monitoring')
app.register_blueprint(security, url_prefix='/api/security')
app.register_blueprint(visualization_bp, url_prefix='/api/visualization')

# Register Route Blueprints
app.register_blueprint(payroll_bp)
app.register_blueprint(notifications_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(schedule_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(notice_api_bp)
app.register_blueprint(notice_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(admin_dashboard_api)

# Login manager setup
login_manager.login_view = "auth.login"
login_manager.login_message = "로그인이 필요합니다."
login_manager.login_message_category = "info"
login_manager.anonymous_user = AnonymousUserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- Error Handlers ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("errors/500.html"), 500


# --- Favicon 처리 ---
@app.route('/favicon.ico')
def favicon():
    """Favicon 요청 처리"""
    return '', 204  # No Content 응답


# --- Context Processor ---
@app.context_processor
def inject_notifications():
    """템플릿에서 사용할 전역 변수 주입"""
    if current_user.is_authenticated:
        unread_count = Notification.query.filter_by(
            user_id=current_user.id, is_read=False
        ).count()
        return {"unread_notification_count": unread_count}
    return {"unread_notification_count": 0}


# --- Basic Routes ---
@app.route("/")
@login_required
def index():
    if current_user.is_admin():
        return redirect(url_for("admin_dashboard"))
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
@login_required
def dashboard():
    # Next.js 프론트엔드 대시보드로 리다이렉트
    return redirect("http://localhost:3000/dashboard")


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)


@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    # 브랜드 관리자인 경우 브랜드 관리자 대시보드로 리다이렉트
    if current_user.role == "brand_admin":
        return redirect(url_for("admin_branch_dashboard", branch_id=current_user.branch_id))
    
    # 최고관리자가 아닌 경우 접근 거부
    if not current_user.is_admin():
        flash("관리자 권한이 필요합니다.")
        return redirect(url_for("dashboard"))

    # 대시보드 모드 설정 전달
    dashboard_mode = current_app.config.get("DASHBOARD_MODE", "solo")

    # 최고관리자 전용 통계 데이터
    stats = {
        "unread_notifications": Notification.query.filter_by(is_read=False).count(),
        "pending_feedback": FeedbackIssue.query.filter_by(status="pending").count(),
        "total_branches": Branch.query.count(),
        "total_users": User.query.count(),
        "active_users": User.query.filter_by(status="approved").count(),
        "total_orders": Order.query.count(),
        "total_schedules": Schedule.query.count(),
        # 추가 통계 데이터
        "total_managers": User.query.filter_by(role="manager").count(),
        "total_employees": User.query.filter_by(role="employee").count(),
        "rejected_users": User.query.filter_by(status="rejected").count(),
        "today_orders": Order.query.filter(
            Order.created_at >= datetime.now().date()
        ).count(),
        "today_schedules": Schedule.query.filter(
            Schedule.date >= datetime.now().date()
        ).count(),
    }

    # 시스템 상태 정보
    system_status = {
        "uptime": "24시간+",  # 실제로는 서버 시작 시간 계산
        "dashboard_mode": dashboard_mode,
        "last_backup": "2024-01-15 14:30",  # 실제로는 백업 매니저에서 가져옴
        "db_status": "정상",
        "server_version": "Flask 2.0+",
        "db_version": "SQLite 3.x",
        # 추가 시스템 정보
        "memory_usage": "45%",
        "disk_usage": "32%",
        "active_sessions": len(
            [u for u in User.query.filter_by(status="approved").all()]
        ),
        "system_load": "정상",
    }

    # 매장 목록 데이터 생성 (실제로는 DB에서 불러옴)
    branch_list = []
    try:
        # 모든 사용자 중 매장 관리자와 직원들을 매장별로 그룹화
        managers = User.query.filter_by(role="manager").all()
        employees = User.query.filter_by(role="employee").all()

        # 임시 매장 데이터 (실제로는 Branch 모델에서 가져와야 함)
        branch_list = [
            {
                "id": 1,
                "name": "본점",
                "manager": managers[0] if managers else None,
                "employees": employees[:5] if employees else [],
                "status": "운영중",
            },
            {
                "id": 2,
                "name": "지점1",
                "manager": managers[1] if len(managers) > 1 else None,
                "employees": employees[5:10] if len(employees) > 5 else [],
                "status": "운영중",
            },
        ]
    except Exception as e:
        print(f"매장 데이터 생성 오류: {e}")

    # 차트 데이터 (실제로는 DB에서 계산)
    chart_data = {
        "attendance": {
            "labels": ["월", "화", "수", "목", "금", "토", "일"],
            "data": [85, 88, 92, 87, 90, 95, 82],
        },
        "orders": {
            "labels": ["1월", "2월", "3월", "4월", "5월", "6월"],
            "data": [120, 135, 142, 138, 156, 168],
        },
    }

    # 최근 활동 데이터
    recent_activities = [
        {"type": "user_join", "message": "새 직원 가입", "time": "5분 전"},
        {"type": "order", "message": "발주 승인", "time": "10분 전"},
        {"type": "schedule", "message": "근무표 수정", "time": "15분 전"},
        {"type": "notification", "message": "전체 알림 발송", "time": "30분 전"},
    ]

    # 알림 데이터
    alerts = {
        "critical": [
            {"type": "system", "message": "백업 필요", "time": "1시간 전"},
            {"type": "user", "message": "승인 대기 사용자 3명", "time": "2시간 전"},
        ],
        "warning": [
            {"type": "performance", "message": "서버 부하 증가", "time": "3시간 전"}
        ],
    }

    # 권한별 접근 통계
    permission_stats = {
        "admin_count": User.query.filter_by(role="admin").count(),
        "manager_count": User.query.filter_by(role="manager").count(),
        "employee_count": User.query.filter_by(role="employee").count(),
        "pending_count": User.query.filter_by(status="pending").count(),
    }

    # 실시간 모니터링 데이터
    realtime_data = {
        "active_users": User.query.filter_by(status="approved").count(),
        "online_users": 12,  # 실제로는 세션 관리에서 가져옴
        "system_uptime": "24시간 15분",
        "last_backup": "2024-01-15 14:30",
        "db_connections": 5,
        "memory_usage": "45%",
        "cpu_usage": "32%",
    }

    # 권한 관리 데이터
    permission_data = {
        "total_permissions": 8,  # 모듈 수
        "active_permissions": 6,
        "pending_changes": 2,
        "recent_updates": [
            {"user": "test_manager1", "action": "권한 수정", "time": "1시간 전"},
            {"user": "test_employee5", "action": "권한 부여", "time": "2시간 전"},
        ],
    }

    # 보고서 데이터
    report_data = {
        "total_reports": Report.query.count(),
        "pending_reports": Report.query.filter_by(status="pending").count(),
        "resolved_reports": Report.query.filter_by(status="resolved").count(),
        "recent_reports": Report.query.order_by(Report.created_at.desc())
        .limit(5)
        .all(),
    }

    # 시스템 로그 데이터
    log_data = {
        "total_logs": SystemLog.query.count(),
        "error_logs": SystemLog.query.filter(SystemLog.action.like("%error%")).count(),
        "warning_logs": SystemLog.query.filter(
            SystemLog.action.like("%warning%")
        ).count(),
        "recent_logs": SystemLog.query.order_by(SystemLog.created_at.desc())
        .limit(10)
        .all(),
    }

    # 백업 데이터
    backup_data = {
        "last_backup": "2024-01-15 14:30",
        "backup_size": "45.2 MB",
        "backup_status": "성공",
        "next_backup": "2024-01-16 14:30",
        "backup_count": 30,
    }

    # 성능 데이터
    performance_data = {
        "response_time": "0.15초",
        "requests_per_minute": 45,
        "error_rate": "0.02%",
        "uptime": "99.8%",
    }

    # 사용자 활동 데이터
    user_activity = {
        "login_today": 25,
        "active_sessions": 12,
        "new_users_week": 3,
        "top_late": [],
        "top_absent": [],
        "recent": [],
    }

    context = {
        "user": current_user,
        "stats": stats,
        "system_status": system_status,
        "branch_list": branch_list,
        "chart_data": chart_data,
        "recent_activities": recent_activities,
        "alerts": alerts,
        "permission_stats": permission_stats,
        "realtime_data": realtime_data,
        "permission_data": permission_data,
        "report_data": report_data,
        "log_data": log_data,
        "backup_data": backup_data,
        "performance_data": performance_data,
        "user_activity": user_activity,
    }

    return render_template("admin_dashboard.html", **context)


@app.route("/admin_dashboard/<int:branch_id>")
@login_required
def admin_branch_dashboard(branch_id):
    if not current_user.is_admin():
        flash("관리자 권한이 필요합니다.")
        return redirect(url_for("dashboard"))
    
    # 매장 정보 조회 (실제로는 Branch 모델에서 가져와야 함)
    branch = {
        "id": branch_id,
        "name": f"매장 {branch_id}",
        "status": "운영중"
    }
    
    # 매장별 통계 데이터
    stats = {
        "total_users": User.query.filter_by(branch_id=branch_id).count() if hasattr(User, 'branch_id') else 0,
        "active_users": User.query.filter_by(branch_id=branch_id, status="approved").count() if hasattr(User, 'branch_id') else 0,
        "pending_users": User.query.filter_by(branch_id=branch_id, status="pending").count() if hasattr(User, 'branch_id') else 0,
        "total_orders": Order.query.filter_by(branch_id=branch_id).count() if hasattr(Order, 'branch_id') else 0,
        "total_schedules": Schedule.query.filter_by(branch_id=branch_id).count() if hasattr(Schedule, 'branch_id') else 0,
    }
    
    context = {
        "user": current_user,
        "branch": branch,
        "stats": stats,
    }
    
    return render_template("admin_branch_dashboard.html", **context)


# --- Schedule Routes ---
@app.route("/schedule", methods=["GET"])
@login_required
def schedule():
    from_date_str = request.args.get("from", datetime.now().strftime("%Y-%m-%d"))
    to_date_str = request.args.get("to", datetime.now().strftime("%Y-%m-%d"))

    try:
        from_dt = date_parser.parse(from_date_str).date()
        to_dt = date_parser.parse(to_date_str).date()
    except ValueError:
        flash("날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)", "error")
        from_dt = datetime.now().date()
        to_dt = datetime.now().date()

    if from_dt > to_dt:
        flash("시작일은 종료일보다 늦을 수 없습니다.", "error")
        from_dt, to_dt = to_dt, from_dt

    days_diff = (to_dt - from_dt).days
    if days_diff > 90:
        flash("최대 90일까지 조회 가능합니다.", "warning")
        to_dt = from_dt + timedelta(days=90)

    days = [(from_dt + timedelta(days=i)) for i in range(days_diff + 1)]
    
    # 통합된 Schedule 모델에서 근무와 청소 스케줄 분리
    all_schedules = Schedule.query.filter(
        Schedule.date >= from_dt,
        Schedule.date <= to_dt
    ).all()
    
    work_schedules = [s for s in all_schedules if s.type == 'work']
    clean_schedules = [s for s in all_schedules if s.type == 'clean']

    return render_template(
        "schedule.html",
        from_date=from_dt.strftime("%Y-%m-%d"),
        to_date=to_dt.strftime("%Y-%m-%d"),
        dates=days,
        work_schedules=work_schedules,
        clean_schedules=clean_schedules,
    )


@app.route("/clean")
@login_required
def clean():
    # 청소 스케줄만 조회
    plans = Schedule.query.filter_by(type='clean').order_by(Schedule.date.desc()).all()
    return render_template("clean.html", plans=plans)

@app.route("/clean_manage")
@login_required
def clean_manage():
    """청소 관리 페이지"""
    try:
        # 승인된 직원 목록 조회
        employees = User.query.filter(
            User.role.in_(['employee', 'manager']),
            User.status.in_(['approved', 'active'])
        ).order_by(User.name).all()
        
        # 청소 스케줄 조회
        cleanings = Schedule.query.filter_by(type='clean').order_by(Schedule.date.desc()).all()
        
        return render_template("clean_manage.html", employees=employees, cleanings=cleanings)
        
    except Exception as e:
        flash("청소 관리 페이지 로딩 중 오류가 발생했습니다.", "error")
        return redirect(url_for("dashboard"))


# --- Notification Routes ---
@app.route("/notifications")
@login_required
def notifications():
    """알림센터"""
    page = request.args.get("page", 1, type=int)
    per_page = 20

    # 권한에 따라 다른 쿼리
    if current_user.is_admin():
        query = Notification.query
    else:
        query = Notification.query.filter(
            db.or_(
                Notification.user_id == current_user.id,
                Notification.is_admin_only == False,
            )
        )

    notifications = query.order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template("notifications.html", notifications=notifications)


@app.route("/notifications/mark_read/<int:notification_id>")
@login_required
def mark_notification_read(notification_id):
    """개별 알림 읽음 처리"""
    notification = Notification.query.filter_by(
        id=notification_id, user_id=current_user.id
    ).first()

    if notification:
        notification.is_read = True
        db.session.commit()
        flash("알림을 읽음 처리했습니다.", "success")
    else:
        flash("알림을 찾을 수 없습니다.", "error")

    return redirect(url_for("notifications"))


@app.route("/notifications/mark_all_read")
@login_required
def mark_all_notifications_read():
    """모든 알림 읽음 처리"""
    try:
        Notification.query.filter_by(user_id=current_user.id, is_read=False).update(
            {"is_read": True}
        )
        db.session.commit()
        flash("모든 알림을 읽음 처리했습니다.", "success")
    except Exception as e:
        flash("알림 처리 중 오류가 발생했습니다.", "error")

    return redirect(url_for("notifications"))


# --- API Routes for Notifications ---
@app.route("/api/new_notifications")
@login_required
def api_new_notifications():
    """새로운 알림 수 API"""
    try:
        count = Notification.query.filter_by(
            user_id=current_user.id, is_read=False
        ).count()
        return jsonify({"count": count})
    except Exception as e:
        return jsonify({"count": 0, "error": str(e)})


@app.route("/notifications/count")
def notifications_count():
    # 실제 구현에서는 로그인 사용자별 미읽은 알림 개수 반환
    # 여기서는 더미 데이터로 3을 반환
    return jsonify({"count": 3})


# --- Admin Routes ---
# @app.route("/admin/users")
# @login_required
# def admin_users():
#     return render_template("admin_users.html", user=current_user)


@app.route("/admin/user_permissions")
@login_required
def admin_user_permissions():
    """권한 관리 페이지"""
    if not current_user.is_admin():
        flash("최고관리자 권한이 필요합니다.")
        return redirect(url_for("dashboard"))
    
    users = User.query.all()
    return render_template("admin/user_permissions.html", users=users, user=current_user)


@app.route("/api/user/<int:user_id>/permissions")
@login_required
def api_user_permissions(user_id):
    """사용자 권한 조회 API"""
    if not current_user.is_admin():
        return jsonify({"error": "권한이 없습니다."}), 403

    user = User.query.get_or_404(user_id)
    return jsonify(user.permissions or {})


@app.route("/api/user/<int:user_id>/permissions", methods=["POST"])
@login_required
def api_update_user_permissions(user_id):
    """사용자 권한 업데이트 API"""
    if not current_user.is_admin():
        return jsonify({"error": "권한이 없습니다."}), 403

    user = User.query.get_or_404(user_id)
    permissions = request.json

    user.permissions = permissions
    db.session.commit()

    return jsonify({"success": True, "message": "권한이 업데이트되었습니다."})


@app.route("/api/permissions/templates")
@login_required
def api_permission_templates():
    """권한 템플릿 목록 API"""
    if not current_user.has_permission("employee_management", "assign_roles"):
        return jsonify({"error": "권한이 없습니다."}), 403

    try:
        from models import PermissionTemplate
        templates = PermissionTemplate.query.filter_by(is_active=True).all()
        
        template_list = []
        for template in templates:
            template_list.append({
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'role_type': template.role_type,
                'permissions': template.permissions,
                'created_at': template.created_at.strftime('%Y-%m-%d %H:%M:%S') if template.created_at else None
            })
        
        return jsonify({
            "success": True,
            "templates": template_list
        })
    except Exception as e:
        return jsonify({"error": f"템플릿 조회 중 오류가 발생했습니다: {str(e)}"}), 500


@app.route("/admin/notify_send")
@login_required
def admin_notify_send():
    """알림 발송 관리 페이지"""
    if not current_user.is_admin():
        flash("최고관리자 권한이 필요합니다.")
        return redirect(url_for("dashboard"))
    
    # 더미 알림 데이터 (실제로는 데이터베이스에서 가져옴)
    notifications = [
        {
            "id": 1,
            "title": "월간 매출 보고서 발송 안내",
            "message": "2024년 1월 매출 보고서가 발송되었습니다. 각 매장별로 확인해주세요.",
            "created_at": datetime.now() - timedelta(days=1),
            "is_read": True
        },
        {
            "id": 2,
            "title": "새로운 메뉴 출시 안내",
            "message": "다음 주부터 새로운 시즌 메뉴가 출시됩니다. 사전 교육을 받아주세요.",
            "created_at": datetime.now() - timedelta(hours=3),
            "is_read": False
        },
        {
            "id": 3,
            "title": "시스템 점검 안내",
            "message": "오늘 밤 12시부터 2시간 동안 시스템 점검이 있을 예정입니다.",
            "created_at": datetime.now() - timedelta(hours=6),
            "is_read": True
        }
    ]
    
    return render_template("admin/notify_send.html", notifications=notifications, user=current_user)


@app.route("/admin/reports")
@login_required
def admin_reports():
    """통합 보고서 페이지"""
    if not current_user.is_admin():
        flash("최고관리자 권한이 필요합니다.")
        return redirect(url_for("dashboard"))
    
    # 매장별 통계 데이터
    branches = Branch.query.all()
    total_orders = Order.query.count()
    total_users = User.query.count()
    
    return render_template("admin/reports.html", 
                         branches=branches, 
                         total_orders=total_orders, 
                         total_users=total_users,
                         user=current_user)


@app.route("/admin/statistics")
@login_required
def admin_statistics():
    """통계 페이지"""
    if not current_user.is_admin():
        flash("최고관리자 권한이 필요합니다.")
        return redirect(url_for("dashboard"))
    
    # 더미 통계 데이터 (실제로는 데이터베이스에서 계산)
    stats_data = {
        "total_users": User.query.count(),
        "total_orders": Order.query.count(),
        "total_sales": 10850000,  # 5개 매장 총 매출
        "total_branches": 5,
        "active_branches": 4,
        "error_count": 12,  # 더미 데이터
        "warning_count": 8,  # 더미 데이터
        "info_count": 45,    # 더미 데이터
        "system_uptime": "24시간+",
        "database_size": "2.3GB",
        "api_requests": 1250,
        "success_rate": 98.5
    }
    
    return render_template("admin/statistics.html", stats_data=stats_data, user=current_user)


@app.route("/admin/system_monitor")
@login_required
def admin_system_monitor():
    """실시간 매장 모니터링 페이지"""
    if not current_user.is_admin():
        flash("최고관리자 권한이 필요합니다.")
        return redirect(url_for("dashboard"))
    
    # 매장별 실시간 데이터
    branches = Branch.query.all()
    
    # 발주 현황 데이터
    today_orders = Order.query.filter(
        Order.created_at >= datetime.now().date()
    ).all()
    
    orders_data = {
        "total_count": len(today_orders),
        "pending_count": len([o for o in today_orders if o.status == "pending"]),
        "approved_count": len([o for o in today_orders if o.status == "approved"]),
        "rejected_count": len([o for o in today_orders if o.status == "rejected"]),
        "total_amount": sum([o.total_amount for o in today_orders if o.total_amount])
    }
    
    # 재고 현황 데이터 (더미 데이터)
    inventory_data = {
        "total_items": 156,
        "low_stock": 8,
        "adequate_stock": 142,
        "excess_stock": 6
    }
    
    # 직원 현황 데이터
    total_staff = User.query.filter_by(role="employee").count()
    managers = User.query.filter_by(role="manager").count()
    
    staff_data = {
        "total_staff": total_staff + managers,
        "working": 22,  # 실제로는 출근 기록에서 계산
        "on_leave": 3,  # 실제로는 휴가/병가 기록에서 계산
        "absent": 3     # 실제로는 미출근 기록에서 계산
    }
    
    # 매출 현황 데이터 (더미 데이터)
    sales_data = {
        "today_sales": 8750000,
        "week_sales": 52300000,
        "month_sales": 198450000,
        "growth_rate": 12.5
    }
    
    # 매장별 알림 데이터
    alerts = [
        {"branch": "본점", "type": "warning", "message": "밀가루 재고 부족 (2일 후 소진 예상)"},
        {"branch": "지점1", "type": "danger", "message": "김철수 직원 미출근 (연락 필요)"},
        {"branch": "지점2", "type": "info", "message": "오늘 발주 승인 완료 (3건)"},
        {"branch": "본점", "type": "warning", "message": "냉장고 온도 이상 (점검 필요)"}
    ]
    
    # 시스템 상태 정보
    import psutil
    import platform
    
    system_info = {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "uptime": "24시간+",
        "active_connections": 28
    }
    
    return render_template("admin/system_monitor.html", 
                         branches=branches,
                         orders_data=orders_data,
                         inventory_data=inventory_data,
                         staff_data=staff_data,
                         sales_data=sales_data,
                         alerts=alerts,
                         system_info=system_info,
                         user=current_user)


@app.route("/admin/backup_management")
@login_required
def admin_backup_management():
    """백업 관리 페이지"""
    if not current_user.is_admin():
        flash("최고관리자 권한이 필요합니다.")
        return redirect(url_for("dashboard"))
    
    # 백업 파일 목록 (실제로는 백업 디렉토리에서 가져옴)
    backup_files = [
        {"name": "backup_2024_01_15_1430.db", "size": "2.5MB", "date": "2024-01-15 14:30"},
        {"name": "backup_2024_01_14_1430.db", "size": "2.4MB", "date": "2024-01-14 14:30"},
        {"name": "backup_2024_01_13_1430.db", "size": "2.3MB", "date": "2024-01-13 14:30"},
    ]
    
    return render_template("admin/backup_management.html", 
                         backup_files=backup_files,
                         user=current_user)


@app.route("/admin/dashboard_mode")
@login_required
def admin_dashboard_mode():
    """대시보드 모드 설정 페이지"""
    if not current_user.is_admin():
        flash("최고관리자 권한이 필요합니다.")
        return redirect(url_for("dashboard"))
    
    current_mode = current_app.config.get("DASHBOARD_MODE", "solo")
    
    return render_template("admin/dashboard_mode.html", 
                         current_mode=current_mode,
                         user=current_user)


@app.route("/admin/feedback_management")
@login_required
def admin_feedback_management():
    """피드백 관리 페이지"""
    if not current_user.is_admin():
        flash("최고관리자 권한이 필요합니다.")
        return redirect(url_for("dashboard"))
    
    feedback_issues = FeedbackIssue.query.order_by(FeedbackIssue.created_at.desc()).all()
    
    return render_template("admin/feedback_management.html", 
                         feedback_issues=feedback_issues,
                         user=current_user)


# --- Schedule API Routes ---
@app.route("/api/schedule", methods=["POST"])
@login_required
def api_add_schedule():
    """스케줄 추가 API"""
    try:
        data = request.json
        schedule = Schedule(
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            start_time=datetime.strptime(data['start_time'], '%H:%M').time(),
            end_time=datetime.strptime(data['end_time'], '%H:%M').time(),
            type=data['type'],  # 'work' 또는 'clean'
            user_id=data.get('user_id'),
            team=data.get('team'),  # 청소 스케줄용
            status='pending'
        )
        db.session.add(schedule)
        db.session.commit()
        return jsonify({"success": True, "message": "스케줄이 추가되었습니다.", "id": schedule.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"오류가 발생했습니다: {str(e)}"}), 400


@app.route("/api/schedule/<int:schedule_id>", methods=["PUT"])
@login_required
def api_update_schedule(schedule_id):
    """스케줄 수정 API"""
    try:
        schedule = Schedule.query.get_or_404(schedule_id)
        data = request.json
        
        schedule.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        schedule.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        schedule.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        schedule.user_id = data.get('user_id')
        schedule.team = data.get('team')
        schedule.status = data.get('status', schedule.status)
        
        db.session.commit()
        return jsonify({"success": True, "message": "스케줄이 수정되었습니다."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"오류가 발생했습니다: {str(e)}"}), 400


@app.route("/api/schedule/<int:schedule_id>", methods=["DELETE"])
@login_required
def api_delete_schedule(schedule_id):
    """스케줄 삭제 API"""
    try:
        schedule = Schedule.query.get_or_404(schedule_id)
        db.session.delete(schedule)
        db.session.commit()
        return jsonify({"success": True, "message": "스케줄이 삭제되었습니다."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"오류가 발생했습니다: {str(e)}"}), 400


@app.route("/api/schedule/<int:schedule_id>", methods=["GET"])
@login_required
def api_get_schedule(schedule_id):
    """스케줄 조회 API"""
    try:
        schedule = Schedule.query.get_or_404(schedule_id)
        return jsonify({
            "id": schedule.id,
            "date": schedule.date.strftime('%Y-%m-%d') if schedule.date else None,
            "start_time": schedule.start_time.strftime('%H:%M') if schedule.start_time else None,
            "end_time": schedule.end_time.strftime('%H:%M') if schedule.end_time else None,
            "type": schedule.type,
            "user_id": schedule.user_id,
            "team": schedule.team,
            "status": schedule.status
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"오류가 발생했습니다: {str(e)}"}), 400


@app.route("/api/users")
@login_required
def api_get_users():
    """사용자 목록 API (스케줄 배정용) - 통합 API 사용"""
    try:
        # 통합 API로 리다이렉트
        from api.staff import get_staff_list
        return get_staff_list()
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/dashboard/stats")
# @login_required  # 임시로 인증 우회 (테스트용)
def api_dashboard_stats():
    """대시보드 통계 데이터 API"""
    try:
        # period 파라미터 가져오기
        period = request.args.get('period', 7, type=int)
        
        # 차트용 데이터 생성
        from datetime import datetime, timedelta
        import random
        
        # 날짜 라벨 생성
        labels = []
        for i in range(period, 0, -1):
            date = datetime.now() - timedelta(days=i-1)
            labels.append(date.strftime('%Y-%m-%d'))
        
        # 더미 차트 데이터 생성
        datasets = {
            'attendance': [random.randint(8, 12) for _ in range(period)],
            'notifications': [random.randint(5, 20) for _ in range(period)],
            'orders': [random.randint(15, 35) for _ in range(period)],
            'system_logs': [random.randint(10, 30) for _ in range(period)]
        }
        
        # 실시간 통계 데이터
        current_stats = {
            'active_users': random.randint(5, 15),
            'unread_notifications': random.randint(0, 8),
            'pending_orders': random.randint(2, 10),
            'today_attendance': random.randint(8, 12),
            'system_errors': random.randint(0, 3)
        }
        
        return jsonify({
            "success": True,
            "labels": labels,
            "datasets": datasets,
            "current_stats": current_stats
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/dashboard/realtime")
# @login_required  # 임시로 인증 우회 (테스트용)
def api_realtime_activities():
    """실시간 활동 로그 API"""
    try:
        import random
        
        # 더미 실시간 활동 데이터
        activities = [
            {
                "username": "김철수",
                "action": "로그인",
                "type": "system_log",
                "time_ago": "1분 전",
                "detail": "관리자 패널 접속"
            },
            {
                "username": "시스템",
                "action": "알림 전송",
                "type": "notification",
                "time_ago": "3분 전",
                "detail": "새 주문 접수됨"
            },
            {
                "username": "이영희",
                "action": "출근 체크",
                "type": "system_log",
                "time_ago": "5분 전",
                "detail": "정시 출근"
            },
            {
                "username": "박민수",
                "action": "발주 신청",
                "type": "system_log",
                "time_ago": "8분 전",
                "detail": "식재료 5종 발주"
            },
            {
                "username": "시스템",
                "action": "오류 발생",
                "type": "system_log",
                "time_ago": "12분 전",
                "detail": "프린터 연결 실패"
            }
        ]
        
        return jsonify({"success": True, "activities": activities})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/dashboard/orders")
@login_required
def api_orders():
    """주문 활동 API"""
    try:
        # 실제 주문 데이터
        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
        
        orders_data = []
        for order in recent_orders:
            orders_data.append({
                "time": order.created_at.strftime("%H:%M"),
                "order": f"#{order.id}",
                "action": "완료" if order.status == "completed" else "조리 중" if order.status == "cooking" else "대기 중",
                "items": "주문 상품",
                "status": order.status
            })
        
        # 더미 데이터 추가
        orders_data.extend([
            {"time": "14:29", "order": "#2025-001", "action": "완료", "items": "스테이크, 파스타", "status": "completed"},
            {"time": "14:12", "order": "#2025-002", "action": "조리 중", "items": "피자, 샐러드", "status": "cooking"},
            {"time": "13:55", "order": "#2025-003", "action": "대기 중", "items": "스시, 미소국", "status": "waiting"},
            {"time": "13:33", "order": "#2025-004", "action": "접수됨", "items": "파스타, 와인", "status": "received"},
            {"time": "13:15", "order": "#2025-005", "action": "배달 완료", "items": "치킨, 콜라", "status": "delivered"}
        ])
        
        return jsonify({"success": True, "data": orders_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/dashboard/kitchen-status")
@login_required
def api_kitchen_status():
    """주방 상태 API"""
    try:
        kitchen_data = {
            "timestamp": datetime.now().strftime("# %Y-%m-%d %H:%M KST"),
            "status": "모든 시스템 정상",
            "temperature": "180°C - 220°C... 정상",
            "ventilation": "ON",
            "message": "...주문 #2025-002 조리 시작... 예상 완료 15분"
        }
        
        return jsonify({"success": True, "data": kitchen_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/dashboard/sales")
@login_required
def api_sales():
    """매출 데이터 API"""
    try:
        sales_data = {
            "today": {
                "cash": 1800000,
                "card": 4260000,
                "total": 6060000
            },
            "orders": {
                "waiting": 8,
                "cooking": 12,
                "completed": 45
            },
            "alerts": {
                "urgent": 3,
                "low_stock": 7,
                "satisfaction": 4.8,
                "reservations": 15
            }
        }
        
        return jsonify({"success": True, "data": sales_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/monitor/real-time-data")
@login_required
def api_real_time_monitor_data():
    """실시간 모니터링 데이터 API"""
    if not current_user.is_admin():
        return jsonify({"error": "권한이 없습니다."}), 403
    
    try:
        # 발주 현황 데이터
        today_orders = Order.query.filter(
            Order.created_at >= datetime.now().date()
        ).all()
        
        orders_data = {
            "total_count": len(today_orders),
            "pending_count": len([o for o in today_orders if o.status == "pending"]),
            "approved_count": len([o for o in today_orders if o.status == "approved"]),
            "rejected_count": len([o for o in today_orders if o.status == "rejected"]),
            "total_amount": sum([o.total_amount for o in today_orders if o.total_amount])
        }
        
        # 직원 현황 데이터
        total_staff = User.query.filter_by(role="employee").count()
        managers = User.query.filter_by(role="manager").count()
        
        staff_data = {
            "total_staff": total_staff + managers,
            "working": 22,  # 실제로는 출근 기록에서 계산
            "on_leave": 3,  # 실제로는 휴가/병가 기록에서 계산
            "absent": 3     # 실제로는 미출근 기록에서 계산
        }
        
        # 매장별 알림 데이터
        alerts = [
            {"branch": "본점", "type": "warning", "message": "밀가루 재고 부족 (2일 후 소진 예상)"},
            {"branch": "지점1", "type": "danger", "message": "김철수 직원 미출근 (연락 필요)"},
            {"branch": "지점2", "type": "info", "message": "오늘 발주 승인 완료 (3건)"},
            {"branch": "본점", "type": "warning", "message": "냉장고 온도 이상 (점검 필요)"}
        ]
        
        return jsonify({
            "orders_data": orders_data,
            "staff_data": staff_data,
            "alerts": alerts,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/monitor/brand-data")
@login_required
def api_brand_monitor_data():
    """브랜드별 모니터링 데이터 API"""
    if not current_user.is_admin():
        return jsonify({"error": "권한이 없습니다."}), 403
    
    try:
        # 브랜드 정보 (실제로는 브랜드 테이블에서 가져옴)
        brand_info = {
            "name": "맛있는 레스토랑",
            "total_branches": 5,
            "branches": [
                {"id": "main", "name": "본점", "status": "active"},
                {"id": "branch1", "name": "지점1", "status": "active"},
                {"id": "branch2", "name": "지점2", "status": "active"},
                {"id": "branch3", "name": "지점3", "status": "active"},
                {"id": "branch4", "name": "지점4", "status": "preparing"}
            ]
        }
        
        # 브랜드 전체 통계
        total_staff = User.query.filter_by(role="employee").count()
        managers = User.query.filter_by(role="manager").count()
        
        brand_stats = {
            "total_staff": total_staff + managers,
            "total_orders": Order.query.filter(
                Order.created_at >= datetime.now().date()
            ).count(),
            "total_sales": 10850000,  # 5개 매장 총 매출
            "active_branches": 4
        }
        
        # 매장별 상세 데이터
        branch_details = {
            "main": {
                "name": "본점",
                "staff_count": 15,
                "orders_today": 5,
                "sales_today": 3200000,
                "alerts": [
                    {"type": "warning", "message": "밀가루 재고 부족 (2일 후 소진 예상)"},
                    {"type": "warning", "message": "냉장고 온도 이상 (점검 필요)"}
                ]
            },
            "branch1": {
                "name": "지점1",
                "staff_count": 12,
                "orders_today": 3,
                "sales_today": 2800000,
                "alerts": [
                    {"type": "danger", "message": "김철수 직원 미출근 (연락 필요)"}
                ]
            },
            "branch2": {
                "name": "지점2",
                "staff_count": 10,
                "orders_today": 7,
                "sales_today": 2750000,
                "alerts": [
                    {"type": "info", "message": "오늘 발주 승인 완료 (3건)"}
                ]
            },
            "branch3": {
                "name": "지점3",
                "staff_count": 8,
                "orders_today": 4,
                "sales_today": 2100000,
                "alerts": [
                    {"type": "warning", "message": "오늘 고객 불만 접수 (1건)"}
                ]
            },
            "branch4": {
                "name": "지점4",
                "staff_count": 0,
                "orders_today": 0,
                "sales_today": 0,
                "alerts": [
                    {"type": "info", "message": "인테리어 공사 진행 중 (70% 완료)"}
                ]
            }
        }
        
        return jsonify({
            "brand_info": brand_info,
            "brand_stats": brand_stats,
            "branch_details": branch_details,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/branch_management")
@login_required
def admin_branch_management():
    """매장 관리 페이지"""
    if not current_user.is_admin():
        flash("최고관리자 권한이 필요합니다.")
        return redirect(url_for("dashboard"))
    
    # 매장 데이터 (실제로는 데이터베이스에서 가져옴)
    branches = [
        {
            "id": "BR001",
            "name": "본점",
            "status": "active",
            "staff_count": 15,
            "today_sales": 3200000,
            "today_orders": 5,
            "location": "서울 강남구",
            "phone": "02-1234-5678"
        },
        {
            "id": "BR002", 
            "name": "지점1",
            "status": "active",
            "staff_count": 12,
            "today_sales": 2800000,
            "today_orders": 3,
            "location": "서울 서초구",
            "phone": "02-2345-6789"
        },
        {
            "id": "BR003",
            "name": "지점2", 
            "status": "active",
            "staff_count": 10,
            "today_sales": 2750000,
            "today_orders": 7,
            "location": "서울 마포구",
            "phone": "02-3456-7890"
        },
        {
            "id": "BR004",
            "name": "지점3",
            "status": "active", 
            "staff_count": 8,
            "today_sales": 2100000,
            "today_orders": 4,
            "location": "서울 송파구",
            "phone": "02-4567-8901"
        },
        {
            "id": "BR005",
            "name": "지점4",
            "status": "preparing",
            "staff_count": 0,
            "open_date": "2024년 3월",
            "preparation_status": "인테리어 중",
            "location": "서울 영등포구",
            "phone": "02-5678-9012"
        }
    ]
    
    # 브랜드 통계
    brand_stats = {
        "total_branches": len(branches),
        "active_branches": len([b for b in branches if b["status"] == "active"]),
        "preparing_branches": len([b for b in branches if b["status"] == "preparing"]),
        "total_staff": sum([b["staff_count"] for b in branches if b["status"] == "active"])
    }
    
    return render_template("admin/branch_management.html", 
                         branches=branches,
                         brand_stats=brand_stats,
                         user=current_user)


# --- CLI Commands ---
@app.cli.command("create-admin")
@click.argument("username")
@click.argument("password")
def create_admin(username, password):
    """관리자 계정 생성"""
    user = User(username=username, role="admin", status="approved")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo(f"관리자 계정 {username}이 생성되었습니다.")


# API Gateway 등록
app.register_blueprint(gateway, url_prefix='/api')

# 기존 API 블루프린트들 등록
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(staff_bp, url_prefix='/api/staff')
app.register_blueprint(schedule_bp, url_prefix='/api/schedule')
app.register_blueprint(orders_bp, url_prefix='/api/orders')
app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

# 새로운 모듈들 등록
app.register_blueprint(user_management, url_prefix='/api/modules/user')
app.register_blueprint(notification_system, url_prefix='/api/modules/notification')
app.register_blueprint(schedule_management, url_prefix='/api/modules/schedule')
app.register_blueprint(qsc_system, url_prefix='/api/modules/restaurant/qsc')
app.register_blueprint(optimization, url_prefix='/api/modules/optimization')
app.register_blueprint(monitoring, url_prefix='/api/modules/monitoring')
app.register_blueprint(security, url_prefix='/api/modules/security')

# 채팅 시스템 등록
app.register_blueprint(chat_bp, url_prefix='/api/chat')

# 보고서 시스템 등록
app.register_blueprint(reporting_bp, url_prefix='/api/reporting')

# WebSocket 이벤트 등록
register_chat_events(socketio)

# 임시로 analytics 비활성화
# app.register_blueprint(analytics_bp, url_prefix='/api/analytics')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
