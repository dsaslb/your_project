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
from api.comment import api_comment_bp
from api.comment_report import comment_report_bp
from api.contracts import contracts_bp
from api.notice import api_notice_bp
from api.report import api_report_bp
from api.staff import staff_bp as api_staff_bp
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

config_name = os.getenv("FLASK_ENV", "default")

app = Flask(__name__)
app.config.from_object(config_by_name[config_name])

# Initialize CORS
CORS(app, supports_credentials=True, origins=['http://localhost:3000', 'http://localhost:3001', 'http://localhost:3002', 'http://localhost:3003', 'http://192.168.45.44:3003'])

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
app.register_blueprint(api_staff_bp)
app.register_blueprint(contracts_bp)

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
    return render_template("dashboard.html", user=current_user)


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)


@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    if not current_user.is_admin():
        flash("관리자 권한이 필요합니다.")
        return redirect(url_for("dashboard"))

    # 대시보드 모드 설정 전달
    dashboard_mode = current_app.config.get("DASHBOARD_MODE", "solo")

    # 최고관리자 전용 통계 데이터
    stats = {
        "pending_users": User.query.filter_by(status="pending").count(),
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


# --- Admin Routes ---
@app.route("/admin/users")
@login_required
def admin_users():
    if not current_user.is_admin():
        return redirect(url_for("index"))
    users = User.query.all()
    return render_template("admin_users.html", users=users)


@app.route("/admin/user_permissions")
@login_required
def admin_user_permissions():
    """권한 관리 페이지"""
    if not current_user.is_admin():
        flash("관리자 권한이 필요합니다.", "error")
        return redirect(url_for("index"))

    users = User.query.filter_by(status="approved").all()
    return render_template("admin/user_permissions.html", users=users)


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
    """전체 알림 발송 페이지"""
    if not current_user.is_admin():
        flash("관리자 권한이 필요합니다.", "error")
        return redirect(url_for("index"))

    return render_template("admin/notify_send.html")


@app.route("/admin/reports")
@login_required
def admin_reports():
    """관리자 보고서 페이지"""
    if not current_user.is_admin():
        flash("관리자 권한이 필요합니다.", "error")
        return redirect(url_for("index"))

    # 더미 통계 데이터
    total_stats = {
        "total_users": 25,
        "approved_users": 20,
        "pending_users": 5,
        "total_orders": 150
    }
    
    branch_stats = [
        {
            "branch": {"id": 1, "name": "본점"},
            "users": 12,
            "orders": 80,
            "schedules": 45
        },
        {
            "branch": {"id": 2, "name": "지점1"},
            "users": 8,
            "orders": 45,
            "schedules": 30
        },
        {
            "branch": {"id": 3, "name": "지점2"},
            "users": 5,
            "orders": 25,
            "schedules": 20
        }
    ]

    reports = Report.query.order_by(Report.created_at.desc()).all()
    return render_template("admin/reports.html", reports=reports, total_stats=total_stats, branch_stats=branch_stats)


@app.route("/admin/system_monitor")
@login_required
def admin_system_monitor():
    """시스템 모니터링 페이지"""
    if not current_user.is_admin():
        flash("관리자 권한이 필요합니다.", "error")
        return redirect(url_for("index"))

    return render_template("admin/system_monitor.html")


@app.route("/admin/backup_management")
@login_required
def admin_backup_management():
    """백업 관리 페이지"""
    if not current_user.is_admin():
        flash("관리자 권한이 필요합니다.", "error")
        return redirect(url_for("index"))

    return render_template("admin/backup_management.html")


@app.route("/admin/swap_requests", methods=["GET"])
@login_required
def admin_swap_requests():
    if not current_user.is_admin():
        return redirect(url_for("index"))
    # '대기' 상태인 '교대' 카테고리의 스케줄만 조회
    reqs = (
        Schedule.query.filter_by(category="교대", status="대기")
        .order_by(Schedule.date.asc())
        .all()
    )
    return render_template("admin/swap_requests.html", swap_requests=reqs)


@app.route("/admin/statistics")
@login_required
def admin_statistics():
    if not current_user.is_admin():
        return redirect(url_for("index"))
    return render_template("admin/statistics.html")


@app.route("/admin/all_notifications")
@login_required
def all_notifications():
    """관리자용 전체 알림 조회"""
    if not current_user.is_admin():
        flash("관리자 권한이 필요합니다.", "error")
        return redirect(url_for("index"))

    page = request.args.get("page", 1, type=int)
    per_page = 50

    notifications = Notification.query.order_by(
        Notification.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template("admin/all_notifications.html", notifications=notifications)


@app.route("/schedule_fc")
@login_required
def schedule_fc():
    return render_template("schedule_fc.html")


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
    """사용자 목록 API (스케줄 배정용)"""
    try:
        users = User.query.filter_by(status='approved').all()
        return jsonify([{
            "id": user.id,
            "username": user.username,
            "role": user.role
        } for user in users])
    except Exception as e:
        return jsonify({"success": False, "message": f"오류가 발생했습니다: {str(e)}"}), 400


@app.route("/api/dashboard/stats")
@login_required
def api_dashboard_stats():
    """대시보드 통계 데이터 API"""
    try:
        # 오늘 날짜
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # 주문 통계
        today_orders = Order.query.filter(
            Order.created_at >= today
        ).count()
        yesterday_orders = Order.query.filter(
            Order.created_at >= yesterday,
            Order.created_at < today
        ).count()
        
        # 매출 통계 (더미 데이터)
        today_revenue = 2350000
        yesterday_revenue = 2180000
        
        # 직원 통계
        total_staff = User.query.filter_by(role="employee").count()
        online_staff = User.query.filter_by(role="employee", status="approved").count()
        
        # 테이블 통계 (더미 데이터)
        total_tables = 20
        occupied_tables = 12
        available_tables = total_tables - occupied_tables
        
        # 재고 통계 (더미 데이터)
        total_items = 156
        low_stock_items = 12
        critical_stock_items = 3
        
        stats = {
            "orders": {
                "today": today_orders,
                "yesterday": yesterday_orders,
                "change": round(((today_orders - yesterday_orders) / yesterday_orders * 100) if yesterday_orders > 0 else 0, 1),
                "pending": 8,
                "completed": 35,
                "cancelled": 2
            },
            "revenue": {
                "today": today_revenue,
                "yesterday": yesterday_revenue,
                "change": round(((today_revenue - yesterday_revenue) / yesterday_revenue * 100) if yesterday_revenue > 0 else 0, 1),
                "average": 52222
            },
            "tables": {
                "total": total_tables,
                "occupied": occupied_tables,
                "available": available_tables,
                "reservation": 5
            },
            "staff": {
                "total": total_staff,
                "online": online_staff,
                "onBreak": 2,
                "offDuty": total_staff - online_staff - 2
            },
            "inventory": {
                "totalItems": total_items,
                "lowStock": low_stock_items,
                "criticalStock": critical_stock_items,
                "value": 8500000
            },
            "performance": {
                "satisfaction": 4.8,
                "efficiency": 92.5,
                "attendance": 96.8
            }
        }
        
        return jsonify({"success": True, "data": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/dashboard/recent-activity")
@login_required
def api_recent_activity():
    """최근 활동 로그 API"""
    try:
        # 실제 활동 데이터 (더미)
        activities = [
            {
                "id": 1,
                "type": "order",
                "title": "새 주문 접수",
                "description": "테이블 5 - 김치찌개 외 3개",
                "time": "2분 전",
                "status": "success",
                "amount": 45500,
                "table": 5
            },
            {
                "id": 2,
                "type": "reservation",
                "title": "예약 확인",
                "description": "4명 - 오후 7:30",
                "time": "5분 전",
                "status": "info"
            },
            {
                "id": 3,
                "type": "inventory",
                "title": "재고 부족 알림",
                "description": "연어 - 3인분 남음",
                "time": "10분 전",
                "status": "warning"
            },
            {
                "id": 4,
                "type": "staff",
                "title": "직원 출근",
                "description": "김철수 - 주방",
                "time": "15분 전",
                "status": "success"
            },
            {
                "id": 5,
                "type": "order",
                "title": "주문 완료",
                "description": "테이블 3 - 비빔밥 외 2개",
                "time": "20분 전",
                "status": "success",
                "amount": 32000,
                "table": 3
            }
        ]
        
        return jsonify({"success": True, "data": activities})
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


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
