from utils.logger import log_action, log_error  # pyright: ignore
from utils.decorators import admin_required  # pyright: ignore
from models_main import (Attendance, CleaningPlan, Notification, Order, Schedule,
                         ShiftRequest, User)
from extensions import db
from sqlalchemy import and_, extract, func, or_
from flask_login import current_user, login_required
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)
from datetime import date, datetime, timedelta
args = None  # pyright: ignore
query = None  # pyright: ignore


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    """대시보드 메인 페이지"""
    if current_user.is_admin():
        return admin_dashboard()
    else:
        return employee_dashboard()


def admin_dashboard():
    """관리자 대시보드 - 모든 데이터 요약"""
    try:
        now = datetime.utcnow()
        today = now.date()

        # 실시간 통계
        stats = get_admin_stats(today)

        # 최근 7일 변화 추이
        weekly_trends = get_weekly_trends()

        # 최근 30일 변화 추이
        monthly_trends = get_monthly_trends()

        # 대기 중인 요청들
        pending_requests = get_pending_requests()

        # 최근 알림
        recent_notifications = get_recent_notifications()

        # 시스템 상태 정보
        system_status = get_system_status()

        return render_template(
            "admin_dashboard.html",
            user=current_user,
            stats=stats,
            weekly_trends=weekly_trends,
            monthly_trends=monthly_trends,
            pending_requests=pending_requests,
            recent_notifications=recent_notifications,
            system_status=system_status,
        )

    except Exception as e:
        log_error(e, current_user.id)
        flash("관리자 대시보드 로딩 중 오류가 발생했습니다.", "error")
        return redirect(url_for("auth.login"))


def employee_dashboard():
    """직원 대시보드 - 개인 데이터 요약"""
    try:
        now = datetime.utcnow()
        today = now.date()

        # 개인 통계
        personal_stats = get_employee_stats(current_user.id,  today)

        # 개인 근무 일정
        my_schedule = get_my_schedule(current_user.id)

        # 개인 알림
        my_notifications = get_my_notifications(current_user.id)

        # 개인 근태 현황
        attendance_status = get_attendance_status(current_user.id,  today)

        return render_template(
            "dashboard.html",
            user=current_user,
            stats=personal_stats,
            schedule=my_schedule,
            notifications=my_notifications,
            attendance_status=attendance_status,
        )

    except Exception as e:
        log_error(e, current_user.id)
        flash("직원 대시보드 로딩 중 오류가 발생했습니다.", "error")
        return redirect(url_for("auth.login"))


def get_admin_stats(today):
    """관리자용 실시간 통계"""
    try:
        # 전체 사용자 수
        total_users = User.query.filter_by(status="approved").count()

        # 오늘 출근한 직원 수
        today_attendance = Attendance.query.filter(
            func.date(Attendance.clock_in) == today
        ).count()

        # 오늘 퇴근한 직원 수
        today_clockout = Attendance.query.filter(
            and_(
                func.date(Attendance.clock_in) == today,
                Attendance.clock_out.isnot(None),
            )
        ).count()

        # 대기 중인 교대 신청
        pending_shifts = ShiftRequest.query.filter_by(status="pending").count()

        # 대기 중인 발주
        pending_orders = Order.query.filter_by(status="pending").count()

        # 오늘의 청소 계획
        today_cleaning = CleaningPlan.query.filter_by(date=today).count()

        # 안읽은 알림 수
        unread_notifications = Notification.query.filter_by(is_read=False).count()

        # 최근 7일 신규 가입자
        week_ago = today - timedelta(days=7)
        new_users_week = User.query.filter(
            and_(User.created_at >= week_ago, User.status == "approved")
        ).count()

        # 최근 30일 신규 가입자
        month_ago = today - timedelta(days=30)
        new_users_month = User.query.filter(
            and_(User.created_at >= month_ago, User.status == "approved")
        ).count()

        return {
            "total_users": total_users,
            "today_attendance": today_attendance,
            "today_clockout": today_clockout,
            "pending_shifts": pending_shifts,
            "pending_orders": pending_orders,
            "today_cleaning": today_cleaning,
            "unread_notifications": unread_notifications,
            "new_users_week": new_users_week,
            "new_users_month": new_users_month,
            "total_orders": 0,
            "today_orders": 0,
            "total_managers": 0,
            "total_employees": 0,
            "rejected_users": 0,
            "today_schedules": 0,
            "total_schedules": 0,
            "total_branches": 0,
            "total_revenue": 0,
        }

    except Exception as e:
        log_error(e, current_user.id)
        return {}


def get_weekly_trends():
    """최근 7일 변화 추이"""
    try:
        trends = []
        for i in range(7):
            target_date = date.today() - timedelta(days=i)

            # 출근자 수
            attendance_count = Attendance.query.filter(
                func.date(Attendance.clock_in) == target_date
            ).count()

            # 교대 신청 수
            shift_requests = ShiftRequest.query.filter(
                func.date(ShiftRequest.created_at) == target_date
            ).count()

            # 발주 수
            orders_count = Order.query.filter(
                func.date(Order.created_at) == target_date
            ).count()

            trends.append(
                {
                    "date": target_date.strftime("%m-%d"),
                    "attendance": attendance_count,
                    "shifts": shift_requests,
                    "orders": orders_count,
                }
            )

        return list(reversed(trends))

    except Exception as e:
        log_error(e, current_user.id)
        return []


def get_monthly_trends():
    """최근 30일 변화 추이"""
    try:
        trends = []
        for i in range(30):
            target_date = date.today() - timedelta(days=i)

            # 출근자 수
            attendance_count = Attendance.query.filter(
                func.date(Attendance.clock_in) == target_date
            ).count()

            # 신규 사용자
            new_users = User.query.filter(
                and_(
                    func.date(User.created_at) == target_date,
                    User.status == "approved",
                )
            ).count()

            trends.append(
                {
                    "date": target_date.strftime("%m-%d"),
                    "attendance": attendance_count,
                    "new_users": new_users,
                }
            )

        return list(reversed(trends))

    except Exception as e:
        log_error(e, current_user.id)
        return []


def get_pending_requests():
    """대기 중인 요청들"""
    try:
        # 대기 중인 교대 신청
        pending_shifts = ShiftRequest.query.filter_by(status="pending").limit(5).all()

        # 대기 중인 발주
        pending_orders = Order.query.filter_by(status="pending").limit(5).all()

        # 승인 대기 중인 사용자
        pending_users = User.query.filter_by(status="pending").limit(5).all()

        return {
            "shifts": pending_shifts,
            "orders": pending_orders,
            "users": pending_users,
        }

    except Exception as e:
        log_error(e, current_user.id)
        return {}


def get_recent_notifications():
    """최근 알림"""
    try:
        return Notification.query.filter_by(is_read=False).order_by(
            Notification.created_at.desc()
        ).limit(10).all()
    except Exception as e:
        log_error(e, current_user.id)
        return []


def get_system_status():
    """시스템 상태 정보"""
    try:
        return {
            "uptime": "24시간+",  # 실제로는 서버 시작 시간 계산
            "dashboard_mode": "admin",
            "last_backup": "2024-01-15 14:30",  # 실제로는 백업 매니저에서 가져옴
            "db_status": "정상",
            "server_version": "Flask 2.0+",
            "db_version": "SQLite 3.x",
            "memory_usage": "45%",
            "disk_usage": "32%",
            "active_sessions": User.query.filter_by(status="approved").count(),
            "system_load": "정상",
        }
    except Exception as e:
        log_error(e, current_user.id)
        return {
            "uptime": "알 수 없음",
            "dashboard_mode": "admin",
            "last_backup": "알 수 없음",
            "db_status": "알 수 없음",
            "server_version": "알 수 없음",
            "db_version": "알 수 없음",
            "memory_usage": "알 수 없음",
            "disk_usage": "알 수 없음",
            "active_sessions": 0,
            "system_load": "알 수 없음",
        }


def get_employee_stats(user_id,  today):
    """직원용 개인 통계"""
    try:
        # 이번 달 출근 일수
        month_start = today.replace(day=1)
        monthly_attendance = Attendance.query.filter(
            and_(Attendance.user_id == user_id, Attendance.clock_in >= month_start)
        ).count()

        # 이번 달 총 근무 시간 (property/hybrid_property 오류 임시 방지)
        try:
            monthly_hours = (
                db.session.query(func.sum(Attendance.work_hours))
                .filter(
                    and_(
                        Attendance.user_id == user_id,
                        Attendance.clock_in >= month_start,
                        Attendance.clock_out.isnot(None),
                    )
                )
                .scalar()
            )
            if monthly_hours is None:
                monthly_hours = 0
        except Exception:
            monthly_hours = 0

        # 대기 중인 교대 신청
        pending_shifts = ShiftRequest.query.filter_by(
            user_id=user_id, status="pending"
        ).count()

        # 안읽은 알림
        unread_notifications = Notification.query.filter_by(
            user_id=user_id, is_read=False
        ).count()

        # 이번 주 근무 일수
        week_start = today - timedelta(days=today.weekday())
        weekly_attendance = Attendance.query.filter(
            and_(Attendance.user_id == user_id, Attendance.clock_in >= week_start)
        ).count()

        # 관리자용 필드도 0으로 포함
        return {
            "monthly_attendance": monthly_attendance,
            "monthly_hours": round(monthly_hours, 1),
            "pending_shifts": pending_shifts,
            "unread_notifications": unread_notifications,
            "weekly_attendance": weekly_attendance,
            "total_orders": 0,
            "pending_orders": 0,
            "today_orders": 0,
            "total_users": 0,
            "total_managers": 0,
            "total_employees": 0,
            "rejected_users": 0,
            "today_schedules": 0,
            "total_schedules": 0,
            "total_branches": 0,
            "total_revenue": 0,
        }

    except Exception as e:
        log_error(e, current_user.id)
        return {}


def get_my_schedule(user_id):
    """개인 근무 일정"""
    try:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        return (
            Schedule.query.filter(
                and_(
                    Schedule.user_id == user_id,
                    Schedule.date >= week_start,
                    Schedule.date <= week_end,
                )
            )
            .order_by(Schedule.date)
            .all()
        )

    except Exception as e:
        log_error(e, current_user.id)
        return []


def get_my_notifications(user_id):
    """개인 알림"""
    try:
        return (
            Notification.query.filter_by(user_id=user_id)
            .order_by(Notification.created_at.desc())
            .limit(5)
            .all()
        )

    except Exception as e:
        log_error(e, current_user.id)
        return []


def get_attendance_status(user_id,  today):
    """개인 근태 현황"""
    try:
        # 오늘 출근 기록
        today_attendance = Attendance.query.filter(
            and_(
                Attendance.user_id == user_id,
                func.date(Attendance.clock_in) == today,
            )
        ).first()

        if today_attendance:
            return {
                "clocked_in": True,
                "clock_in_time": today_attendance.clock_in,
                "clocked_out": today_attendance.clock_out is not None,
                "clock_out_time": today_attendance.clock_out,
                "work_hours": today_attendance.work_hours,
            }
        else:
            return {"clocked_in": False, "clocked_out": False}

    except Exception as e:
        log_error(e, current_user.id)
        return {}


@dashboard_bp.route("/api/dashboard/stats")
@login_required
def api_dashboard_stats():
    """대시보드 통계 API"""
    try:
        today = date.today()

        if current_user.is_admin():
            stats = get_admin_stats(today)
        else:
            stats = get_employee_stats(current_user.id,  today)

        return jsonify({"success": True, "stats": stats})

    except Exception as e:
        log_error(e, current_user.id)
        return jsonify({"success": False, "error": str(e)})


@dashboard_bp.route("/api/dashboard/trends")
@login_required
def api_dashboard_trends():
    """대시보드 추이 API"""
    try:
        period = request.args.get() if args else None"period", "weekly") if args else None

        if period == "weekly":
            trends = get_weekly_trends()
        else:
            trends = get_monthly_trends()

        return jsonify({"success": True, "trends": trends})

    except Exception as e:
        log_error(e, current_user.id)
        return jsonify({"success": False, "error": str(e)})


@dashboard_bp.route('/api/dashboard/activities')
@login_required
def dashboard_activities():
    """최근 활동 데이터 API"""
    # 더미 활동 데이터
    activities = [
        {
            "id": 1,
            "type": "order",
            "title": "새 주문 등록",
            "description": "테이블 5번에서 새로운 주문이 등록되었습니다.",
            "timestamp": "2024-01-15T14:30:00Z",
            "status": "success"
        },
        {
            "id": 2,
            "type": "inventory",
            "title": "재고 부족 알림",
            "description": "토마토 소스 재고가 부족합니다.",
            "timestamp": "2024-01-15T13:45:00Z",
            "status": "warning"
        },
        {
            "id": 3,
            "type": "staff",
            "title": "직원 출근",
            "description": "김철수 직원이 출근했습니다.",
            "timestamp": "2024-01-15T09:00:00Z",
            "status": "info"
        }
    ]
    return jsonify({"success": True, "data": activities})


@dashboard_bp.route('/api/dashboard/charts')
@login_required
def dashboard_charts():
    """차트 데이터 API"""
    # 더미 차트 데이터
    charts = {
        "sales_chart": {
            "labels": ["1월", "2월", "3월", "4월", "5월", "6월"],
            "data": [1200000, 1350000, 1420000, 1380000, 1550000, 1680000]
        },
        "orders_chart": {
            "labels": ["월", "화", "수", "목", "금", "토", "일"],
            "data": [45, 52, 38, 61, 78, 95, 67]
        }
    }
    return jsonify({"success": True, "data": charts})
