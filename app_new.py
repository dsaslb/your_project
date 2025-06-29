import base64
import io
import json
import os
from calendar import monthrange
from collections import defaultdict
from datetime import date, datetime, time, timedelta

import click
import pandas as pd
import pdfkit
from dateutil import parser as date_parser
from flask import (Flask, flash, jsonify, make_response, redirect,
                   render_template, request, send_file, session, url_for)
from flask_login import (UserMixin, current_user, login_required, login_user,
                         logout_user)
from sqlalchemy import and_, case, extract, func
from werkzeug.security import check_password_hash, generate_password_hash

from api.admin_log import admin_log_bp
from api.admin_report import admin_report_bp
from api.admin_report_stat import admin_report_stat_bp
# Import API Blueprints
from api.auth import api_auth_bp, auth_bp
from api.comment import api_comment_bp
from api.comment_report import comment_report_bp
from api.notice import api_notice_bp
from api.report import api_report_bp
from config import COOKIE_SECURE, config_by_name
from extensions import cache, csrf, db, limiter, login_manager, migrate
from models import (Attendance, AttendanceEvaluation, AttendanceReport,
                    CleaningPlan, Notice, Notification, Order,
                    PermissionChangeLog, PermissionTemplate, ReasonEditLog,
                    ReasonTemplate, Report, Schedule, ShiftRequest, Team, User,
                    UserPermission)
from routes.notifications import notifications_bp
# Import Route Blueprints
from routes.payroll import payroll_bp
# Import file utility functions
from utils.file_utils import (cleanup_old_backups, compress_backup_files,
                              send_backup_notification)
# Import logging functions
from utils.logger import log_action, log_error
# Import notification functions
from utils.notify import (send_admin_only_notification, send_email, send_kakao,
                          send_notification_enhanced,
                          send_notification_to_role)
from utils.pay_transfer import transfer_salary
# Import new utility functions
from utils.report import generate_attendance_report_pdf
# Import security functions
from utils.security import (admin_required, check_account_lockout,
                            get_client_ip, handle_failed_login,
                            is_suspicious_request, log_security_event,
                            password_strong, reset_login_attempts,
                            sanitize_input, validate_email, validate_phone)


# AttendanceDispute 모델 정의
class AttendanceDispute(db.Model):
    """근태 신고/이의제기 모델"""

    __tablename__ = "attendance_disputes"

    id = db.Column(db.Integer, primary_key=True)
    attendance_id = db.Column(
        db.Integer, db.ForeignKey("attendances.id"), nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    dispute_type = db.Column(db.String(20), nullable=False)  # 'report', 'dispute'
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(
        db.String(20), default="pending"
    )  # 'pending', 'processing', 'resolved', 'rejected'
    admin_reply = db.Column(db.Text)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 관계
    attendance = db.relationship("Attendance", backref="disputes")
    user = db.relationship("User", foreign_keys=[user_id], backref="disputes")
    admin = db.relationship("User", foreign_keys=[admin_id], backref="admin_disputes")


config_name = os.getenv("FLASK_ENV", "default")

app = Flask(__name__)
app.config.from_object(config_by_name[config_name])

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

# Register Route Blueprints
app.register_blueprint(payroll_bp)
app.register_blueprint(notifications_bp)

# Login manager setup
login_manager.login_view = "auth.login"
login_manager.login_message = "로그인이 필요합니다."
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- Error Handlers ---
@app.errorhandler(403)
def forbidden(e):
    return render_template("errors/403.html"), 403


@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404


@app.errorhandler(413)
def request_entity_too_large(e):
    return render_template("errors/413.html"), 413


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

    # 기본 통계 데이터
    context = {
        "num_users": User.query.count(),
        "num_attendance": 0,
        "warn_users": [],
        "result": [],
        "branch_names": [],
        "chart_labels": [],
        "chart_data": [],
        "trend_dates": [],
        "trend_data": [],
        "dist_labels": [],
        "dist_data": [],
        "top_late": [],
        "top_absent": [],
        "recent": [],
    }
    return render_template("admin_dashboard.html", **context)


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
    schedules = {d: Schedule.query.filter_by(date=d).all() for d in days}
    cleanings = {d: CleaningPlan.query.filter_by(date=d).all() for d in days}

    return render_template(
        "schedule.html",
        from_date=from_dt.strftime("%Y-%m-%d"),
        to_date=to_dt.strftime("%Y-%m-%d"),
        dates=days,
        schedules=schedules,
        cleanings=cleanings,
    )


@app.route("/clean")
@login_required
def clean():
    plans = CleaningPlan.query.order_by(CleaningPlan.date.desc()).all()
    return render_template("clean.html", plans=plans)


@app.route("/schedule_management", methods=["GET"])
@login_required
def schedule_management():
    # 관리자 또는 매니저만 접근 가능
    if not current_user.is_admin() and current_user.role != "manager":
        flash("권한이 없습니다.", "error")
        return redirect(url_for("index"))

    schedules = Schedule.query.order_by(Schedule.date.desc()).all()
    return render_template("schedule_management.html", schedules=schedules)


@app.route("/schedule/add", methods=["GET", "POST"])
@login_required
def add_schedule():
    if request.method == "POST":
        try:
            user_id = int(request.form["user_id"])
            date_str = request.form["date"]
            start_time_str = request.form["start_time"]
            end_time_str = request.form["end_time"]
            category = request.form.get("category", "근무")
            memo = request.form.get("memo", "")

            # 날짜와 시간 파싱
            schedule_date = date_parser.parse(date_str).date()
            start_time = date_parser.parse(start_time_str).time()
            end_time = date_parser.parse(end_time_str).time()

            # 기본값 설정
            status = request.form.get("status", "대기")

            schedule = Schedule(
                user_id=user_id,
                date=schedule_date,
                start_time=start_time,
                end_time=end_time,
                category=category,
                status=status,
                memo=memo,
            )

            db.session.add(schedule)
            db.session.commit()

            flash("일정이 추가되었습니다.", "success")
            return redirect(url_for("schedule_management"))

        except (ValueError, TypeError) as e:
            flash(f"입력 데이터 오류: {e}", "error")
        except Exception as e:
            flash(f"일정 추가 중 오류가 발생했습니다: {e}", "error")

    users = User.query.all()
    return render_template("add_schedule.html", users=users)


@app.route("/schedule_fc")
@login_required
def schedule_fc():
    return render_template("schedule_fc.html")


@app.route("/schedule/approve/<int:schedule_id>", methods=["POST"])
@login_required
def approve_schedule(schedule_id):
    if not current_user.is_admin() and current_user.role != "manager":
        flash("권한이 없습니다.", "error")
        return redirect(url_for("schedule_management"))

    schedule = Schedule.query.get_or_404(schedule_id)
    action = request.form.get("action")

    if action == "approve":
        schedule.status = "승인"
        flash("일정이 승인되었습니다.", "success")
    elif action == "reject":
        schedule.status = "거절"
        flash("일정이 거절되었습니다.", "success")
    else:
        flash("잘못된 요청입니다.", "error")
        return redirect(url_for("schedule_management"))

    db.session.commit()
    return redirect(url_for("schedule_management"))


@app.route("/schedule/edit/<int:sid>", methods=["GET", "POST"])
@login_required
def edit_schedule(sid):
    schedule = Schedule.query.get_or_404(sid)

    if request.method == "POST":
        try:
            schedule.user_id = int(request.form["user_id"])
            schedule.date = date_parser.parse(request.form["date"]).date()
            schedule.start_time = date_parser.parse(request.form["start_time"]).time()
            schedule.end_time = date_parser.parse(request.form["end_time"]).time()
            schedule.category = request.form.get("category", "근무")
            schedule.status = request.form.get("status", "대기")
            schedule.memo = request.form.get("memo", "")

            db.session.commit()
            flash("일정이 수정되었습니다.", "success")
            return redirect(url_for("schedule_management"))

        except Exception as e:
            flash(f"일정 수정 중 오류가 발생했습니다: {e}", "error")

    users = User.query.all()
    return render_template("edit_schedule.html", schedule=schedule, users=users)


@app.route("/schedule/delete/<int:sid>")
@login_required
def delete_schedule(sid):
    if not current_user.is_admin() and current_user.role != "manager":
        flash("권한이 없습니다.", "error")
        return redirect(url_for("schedule_management"))

    schedule = Schedule.query.get_or_404(sid)
    db.session.delete(schedule)
    db.session.commit()
    flash("일정이 삭제되었습니다.", "success")
    return redirect(url_for("schedule_management"))


@app.route("/clean/edit/<int:cid>", methods=["GET", "POST"])
@login_required
def edit_clean(cid):
    if not current_user.is_admin():
        flash("권한이 없습니다.", "error")
        return redirect(url_for("clean"))

    plan = CleaningPlan.query.get_or_404(cid)

    if request.method == "POST":
        try:
            plan.date = date_parser.parse(request.form["date"]).date()
            plan.plan = request.form["plan"]
            plan.team = request.form.get("team", "")
            plan.manager_id = (
                int(request.form["manager_id"]) if request.form["manager_id"] else None
            )
            plan.user_id = (
                int(request.form["user_id"]) if request.form["user_id"] else None
            )

            db.session.commit()
            flash("청소 계획이 수정되었습니다.", "success")
            return redirect(url_for("clean"))

        except Exception as e:
            flash(f"청소 계획 수정 중 오류가 발생했습니다: {e}", "error")

    users = User.query.all()
    return render_template("edit_clean.html", plan=plan, users=users)


@app.route("/clean/delete/<int:cid>")
@login_required
def delete_clean(cid):
    if not current_user.is_admin():
        flash("권한이 없습니다.", "error")
        return redirect(url_for("clean"))

    plan = CleaningPlan.query.get_or_404(cid)
    db.session.delete(plan)
    db.session.commit()
    flash("청소 계획이 삭제되었습니다.", "success")
    return redirect(url_for("clean"))


# --- API Routes ---
@app.route("/api/schedule")
@login_required
def api_schedule():
    """FullCalendar용 스케줄 API"""
    start = request.args.get("start")
    end = request.args.get("end")

    try:
        start_date = date_parser.parse(start).date() if start else datetime.now().date()
        end_date = date_parser.parse(end).date() if end else datetime.now().date()
    except:
        start_date = datetime.now().date()
        end_date = datetime.now().date()

    schedules = Schedule.query.filter(
        Schedule.date >= start_date, Schedule.date <= end_date
    ).all()

    def get_user_color(user_id):
        # 유저별로 고정된 색상을 반환 (간단한 예시)
        colors = ["#007bff", "#28a745", "#dc3545", "#ffc107", "#17a2b8", "#6f42c1"]
        return colors[user_id % len(colors)]

    events = []
    for schedule in schedules:
        user = User.query.get(schedule.user_id)
        events.append(
            {
                "id": schedule.id,
                "title": f"{user.username if user else 'Unknown'} - {schedule.category}",
                "start": f"{schedule.date.isoformat()}T{schedule.start_time.isoformat()}",
                "end": f"{schedule.date.isoformat()}T{schedule.end_time.isoformat()}",
                "backgroundColor": get_user_color(schedule.user_id),
                "borderColor": get_user_color(schedule.user_id),
                "extendedProps": {
                    "category": schedule.category,
                    "status": schedule.status,
                    "memo": schedule.memo,
                },
            }
        )

    return jsonify(events)


@app.route("/api/schedule", methods=["POST"])
@login_required
def api_add_schedule():
    """API를 통한 스케줄 추가"""
    data = request.json

    try:
        schedule = Schedule(
            user_id=int(data["user_id"]),
            date=date_parser.parse(data["date"]).date(),
            start_time=date_parser.parse(data["start_time"]).time(),
            end_time=date_parser.parse(data["end_time"]).time(),
            category=data.get("category", "근무"),
            status=data.get("status", "대기"),
            memo=data.get("memo", ""),
        )

        db.session.add(schedule)
        db.session.commit()

        return jsonify({"success": True, "id": schedule.id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/schedule/<int:sid>", methods=["PUT"])
@login_required
def api_edit_schedule(sid):
    """API를 통한 스케줄 수정"""
    schedule = Schedule.query.get_or_404(sid)
    data = request.json

    try:
        schedule.user_id = int(data["user_id"])
        schedule.date = date_parser.parse(data["date"]).date()
        schedule.start_time = date_parser.parse(data["start_time"]).time()
        schedule.end_time = date_parser.parse(data["end_time"]).time()
        schedule.category = data.get("category", "근무")
        schedule.status = data.get("status", "대기")
        schedule.memo = data.get("memo", "")

        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/schedule/<int:sid>", methods=["DELETE"])
@login_required
def api_delete_schedule(sid):
    """API를 통한 스케줄 삭제"""
    schedule = Schedule.query.get_or_404(sid)

    try:
        db.session.delete(schedule)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


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


# --- Order Routes ---
@app.route("/order_detail/<int:oid>", methods=["GET", "POST"])
@login_required
def order_detail(oid):
    order = Order.query.get_or_404(oid)

    if request.method == "POST" and current_user.role in ["admin", "manager"]:
        old_status = order.status
        order.status = request.form["status"]
        order.detail = request.form.get("detail", order.detail)
        db.session.commit()

        # 상태 변경 시 알림 발송
        if old_status != order.status:
            if order.status == "approved":
                send_order_approval_notification(order)
            elif order.status == "rejected":
                content = f"발주 '{order.item}' ({order.quantity}개)가 거절되었습니다."
                link = f"/order_detail/{order.id}"
                send_notification_enhanced(order.ordered_by, content, "발주", link)
            elif order.status == "delivered":
                content = f"발주 '{order.item}' ({order.quantity}개)가 배송되었습니다."
                link = f"/order_detail/{order.id}"
                send_notification_enhanced(order.ordered_by, content, "발주", link)

        flash("발주 상태가 업데이트되었습니다.", "success")
        return redirect(url_for("order_detail", oid=oid))

    return render_template("order_detail.html", order=order)


def send_order_approval_notification(order):
    """발주 승인 시 담당 매니저와 발주자 모두에게 알림"""
    try:
        # 발주자에게 알림
        send_notification_enhanced(
            order.ordered_by,
            f"발주 '{order.item}' ({order.quantity}개)가 승인되었습니다.",
            "발주",
            f"/order_detail/{order.id}",
        )

        # 매니저(관리자) 전체에게도 알림
        managers = User.query.filter(User.role.in_(["admin", "manager"])).all()
        for manager in managers:
            if manager.id != order.ordered_by:  # 발주자와 다른 경우만
                # 발주자 정보 조회
                order_user = User.query.get(order.ordered_by)
                username = order_user.username if order_user else "알 수 없음"
                send_notification_enhanced(
                    manager.id,
                    f"발주 '{order.item}' ({order.quantity}개)가 승인 처리되었습니다. (발주자: {username})",
                    "발주",
                    f"/order_detail/{order.id}",
                )

        return True
    except Exception as e:
        print(f"발주 승인 알림 발송 실패: {e}")
        return False


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


@app.route("/notifications/mark_read", methods=["POST"])
@login_required
def mark_read():
    """선택한 알림 읽음 처리"""
    try:
        ids = request.form.getlist("noti_ids")
        for nid in ids:
            notification = Notification.query.filter_by(
                id=int(nid), user_id=current_user.id
            ).first()
            if notification:
                notification.is_read = True

        db.session.commit()
        flash(f"{len(ids)}개의 알림을 읽음 처리했습니다.", "success")

    except Exception as e:
        flash("알림 처리 중 오류가 발생했습니다.", "error")

    return redirect(url_for("notifications"))


# --- Statistics Routes ---
@app.route("/stat_report")
@login_required
def stat_report():
    from sqlalchemy import func

    # 직원별 근무일수
    workdays = (
        db.session.query(Schedule.user_id, func.count(Schedule.id))
        .filter(Schedule.category == "근무")
        .group_by(Schedule.user_id)
        .all()
    )
    # 직원별 발주건수
    orders = (
        db.session.query(Order.ordered_by, func.count(Order.id))
        .group_by(Order.ordered_by)
        .all()
    )
    # 청소 담당별
    cleans = (
        db.session.query(CleaningPlan.manager_id, func.count(CleaningPlan.id))
        .group_by(CleaningPlan.manager_id)
        .all()
    )
    users = {u.id: u.username for u in User.query.all()}
    return render_template(
        "stat_report.html", workdays=workdays, orders=orders, cleans=cleans, users=users
    )


# 대시보드에 미처리 신고/이의제기 건수 표시
def get_pending_disputes_count():
    """미처리 신고/이의제기 건수 조회"""
    try:
        return AttendanceDispute.query.filter_by(status="pending").count()
    except:
        return 0


if __name__ == "__main__":
    app.run(debug=True)
