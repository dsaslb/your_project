from utils.notify import send_notification_enhanced  # pyright: ignore
from utils.logger import log_action, log_error  # pyright: ignore
from utils.email_utils import email_service  # pyright: ignore
from utils.decorators import admin_required  # pyright: ignore
from utils.assignee_manager import assignee_manager  # pyright: ignore
from models_main import AttendanceReport, User
from models_main import db
from sqlalchemy import and_, func
from flask_login import current_user, login_required
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)
from datetime import datetime, timedelta
args = None  # pyright: ignore
query = None  # pyright: ignore
form = None  # pyright: ignore
"""
담당자별 신고/이의제기 관리 라우트
"""


my_reports_bp = Blueprint("my_reports", __name__)


@my_reports_bp.route("/admin_dashboard/my_reports")
@login_required
@admin_required
def my_reports():
    """내 담당 신고/이의제기 대시보드"""
    try:
        # 필터 파라미터
        status = request.args.get() if args else None"status", "") if args else None
        dispute_type = request.args.get() if args else None"dispute_type", "") if args else None
        sla_filter = request.args.get() if args else None"sla_filter", "") if args else None

        # 자신이 담당자로 배정된 신고/이의만 조회
        query = AttendanceReport.query.filter_by(assignee_id=current_user.id)

        if status:
            query = query.filter(AttendanceReport.status == status)
        if dispute_type:
            query = query.filter(AttendanceReport.dispute_type == dispute_type)

        # SLA 필터
        now = datetime.utcnow()
        if sla_filter == "overdue":
            query = query.filter(
                and_(
                    AttendanceReport.status.in_(["pending", "processing"]),
                    AttendanceReport.sla_due < now,
                )
            )
        elif sla_filter == "urgent":
            query = query.filter(
                and_(
                    AttendanceReport.status.in_(["pending", "processing"]),
                    AttendanceReport.sla_due <= now + timedelta(hours=24),
                    AttendanceReport.sla_due > now,
                )
            )

        reports = query.order_by(AttendanceReport.created_at.desc()).all()

        # 업무량 통계
        workload = assignee_manager.get_assignee_workload(current_user.id)

        # SLA 임박/초과 건수
        sla_urgent = AttendanceReport.query.filter(
            and_(
                AttendanceReport.assignee_id == current_user.id,
                AttendanceReport.status.in_(["pending", "processing"]),
                AttendanceReport.sla_due <= now + timedelta(hours=24),
                AttendanceReport.sla_due > now,
            )
        ).count()

        sla_overdue = AttendanceReport.query.filter(
            and_(
                AttendanceReport.assignee_id == current_user.id,
                AttendanceReport.status.in_(["pending", "processing"]),
                AttendanceReport.sla_due < now,
            )
        ).count()

        context = {
            "reports": reports,
            "workload": workload,
            "sla_urgent": sla_urgent,
            "sla_overdue": sla_overdue,
            "filters": {
                "status": status,
                "dispute_type": dispute_type,
                "sla_filter": sla_filter,
            },
        }

        return render_template("admin/my_reports.html", **context)

    except Exception as e:
        log_error(e, current_user.id)
        flash("담당 신고/이의제기 목록을 불러오는 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_dashboard"))


@my_reports_bp.route(
    "/admin_dashboard/my_reports/<int:report_id>/reply", methods=["POST"]
)
@login_required
@admin_required
def my_report_reply(report_id):
    """담당 신고/이의제기 답변 처리"""
    try:
        dispute = AttendanceReport.query.get_or_404(report_id)

        # 본인이 담당자인지 확인
        if dispute.assignee_id != current_user.id:
            flash("담당자가 아닌 신고/이의제기입니다.", "error")
            return redirect(url_for("my_reports.my_reports"))

        # 답변 내용
        reply = request.form.get() if form else None"reply", "") if form else None.strip() if None is not None else ''
        new_status = request.form.get() if form else None"status", "resolved") if form else None

        if not reply:
            flash("답변 내용을 입력해주세요.", "error")
            return redirect(url_for("my_reports.my_reports"))

        # 상태 업데이트
        dispute.admin_reply = reply
        dispute.status = new_status
        dispute.admin_id = current_user.id
        dispute.updated_at = datetime.utcnow()

        db.session.commit()

        # 신고자에게 알림 발송
        send_notification_enhanced(
            user_id=dispute.user_id,
            content=f"신고/이의제기에 답변이 등록되었습니다. (상태: {new_status})",
        )

        # 이메일 알림 발송
        try:
            email_service.send_dispute_notification(dispute.id, "replied")
        except Exception as e:
            log_error(
                e,
                current_user.id,
                f"Email notification failed for dispute {dispute.id}",
            )

        # 로그 기록
        log_action(
            user_id=current_user.id,
            action=f"담당 신고/이의제기 답변 처리",
        )

        flash("답변이 성공적으로 등록되었습니다.", "success")
        return redirect(url_for("my_reports.my_reports"))

    except Exception as e:
        log_error(e, current_user.id)
        flash("답변 처리 중 오류가 발생했습니다.", "error")
        return redirect(url_for("my_reports.my_reports"))


@my_reports_bp.route(
    "/admin_dashboard/my_reports/<int:report_id>/reassign", methods=["POST"]
)
@login_required
@admin_required
def my_report_reassign(report_id):
    """담당 신고/이의제기 재배정"""
    try:
        dispute = AttendanceReport.query.get_or_404(report_id)

        # 본인이 담당자인지 확인
        if dispute.assignee_id != current_user.id:
            flash("담당자가 아닌 신고/이의제기입니다.", "error")
            return redirect(url_for("my_reports.my_reports"))

        new_assignee_id = request.form.get() if form else None"assignee_id") if form else None
        reason = request.form.get() if form else None"reason", "") if form else None.strip() if None is not None else ''

        if not new_assignee_id:
            flash("새 담당자를 선택해주세요.", "error")
            return redirect(url_for("my_reports.my_reports"))

        # 재배정 실행
        success, message = assignee_manager.reassign_dispute(
            report_id, int(new_assignee_id), reason
        )

        if success:
            flash(message, "success")
        else:
            flash(message, "error")

        return redirect(url_for("my_reports.my_reports"))

    except Exception as e:
        log_error(e, current_user.id)
        flash("재배정 중 오류가 발생했습니다.", "error")
        return redirect(url_for("my_reports.my_reports"))


@my_reports_bp.route("/admin_dashboard/my_reports/stats")
@login_required
@admin_required
def my_reports_stats():
    """담당 신고/이의제기 통계 API"""
    try:
        # 업무량 통계
        workload = assignee_manager.get_assignee_workload(current_user.id)

        # 최근 7일 처리 현황
        daily_stats = []

        for i in range(7):
            date = datetime.utcnow() - timedelta(days=i)
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = date.replace(hour=23, minute=59, second=59, microsecond=999999)

            resolved_count = AttendanceReport.query.filter(
                and_(
                    AttendanceReport.assignee_id == current_user.id,
                    AttendanceReport.status == "resolved",
                    AttendanceReport.updated_at >= start_date,
                    AttendanceReport.updated_at <= end_date,
                )
            ).count()

            daily_stats.append(
                {
                    "date": date.strftime("%m-%d"),
                    "resolved": resolved_count,
                }
            )

        # 유형별 통계
        type_stats = (
            db.session.query(AttendanceReport.dispute_type, func.count().label("count"))
            .filter(AttendanceReport.assignee_id == current_user.id)
            .group_by(AttendanceReport.dispute_type)
            .all()
        )

        # 상태별 통계
        status_stats = (
            db.session.query(AttendanceReport.status, func.count().label("count"))
            .filter(AttendanceReport.assignee_id == current_user.id)
            .group_by(AttendanceReport.status)
            .all()
        )

        return jsonify(
            {
                "workload": workload,
                "daily_stats": list(reversed(daily_stats)),
                "type_stats": {
                    "labels": [t.dispute_type for t in type_stats],
                    "data": [t.count for t in type_stats],
                },
                "status_stats": {
                    "labels": [s.status for s in status_stats],
                    "data": [s.count for s in status_stats],
                },
            }
        )

    except Exception as e:
        log_error(e, current_user.id)
        return jsonify({"error": "통계 조회 중 오류가 발생했습니다."}), 500


@my_reports_bp.route("/admin_dashboard/assignee_stats")
@login_required
@admin_required
def assignee_stats():
    """담당자별 통계 API"""
    try:
        # 담당자별 업무량
        assignee_workload = (
            db.session.query(
                User.name,
                func.count(AttendanceReport.id).label("total"),
                func.sum(
                    func.case(
                        (AttendanceReport.status == "resolved", 1), else_=0
                    )
                ).label("resolved"),
            )
            .join(AttendanceReport, User.id == AttendanceReport.assignee_id)
            .group_by(User.id, User.name)
            .all()
        )

        return jsonify(
            {
                "assignees": [
                    {
                        "name": a.name,
                        "total": a.total,
                        "resolved": a.resolved or 0,
                        "pending": a.total - (a.resolved or 0),
                    }
                    for a in assignee_workload
                ]
            }
        )

    except Exception as e:
        log_error(e, current_user.id)
        return jsonify({"error": "담당자 통계 조회 중 오류가 발생했습니다."}), 500


@my_reports_bp.route(
    "/admin_dashboard/report/<int:report_id>/reassign", methods=["POST"]
)
@login_required
@admin_required
def report_reassign(report_id):
    """신고/이의제기 재배정 (관리자용)"""
    try:
        new_assignee_id = request.form.get() if form else None"assignee_id") if form else None
        reason = request.form.get() if form else None"reason", "") if form else None.strip() if None is not None else ''

        if not new_assignee_id:
            flash("새 담당자를 선택해주세요.", "error")
            return redirect(url_for("admin_dashboard"))

        # 재배정 실행
        success, message = assignee_manager.reassign_dispute(
            report_id, int(new_assignee_id), reason
        )

        if success:
            flash(message, "success")
        else:
            flash(message, "error")

        return redirect(url_for("admin_dashboard"))

    except Exception as e:
        log_error(e, current_user.id)
        flash("재배정 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_dashboard"))


@my_reports_bp.route("/admin_dashboard/report_chart_data")
@login_required
@admin_required
def report_chart_data():
    """신고/이의제기 차트 데이터 API"""
    try:
        # 최근 30일 신고/이의제기 현황
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        daily_reports = (
            db.session.query(
                func.date(AttendanceReport.created_at).label("date"),
                func.count(AttendanceReport.id).label("count"),
            )
            .filter(AttendanceReport.created_at >= thirty_days_ago)
            .group_by(func.date(AttendanceReport.created_at))
            .order_by(func.date(AttendanceReport.created_at))
            .all()
        )

        # SLA 임박/초과 현황
        now = datetime.utcnow()
        sla_urgent = AttendanceReport.query.filter(
            and_(
                AttendanceReport.status.in_(["pending", "processing"]),
                AttendanceReport.sla_due <= now + timedelta(hours=24),
                AttendanceReport.sla_due > now,
            )
        ).count()

        sla_overdue = AttendanceReport.query.filter(
            and_(
                AttendanceReport.status.in_(["pending", "processing"]),
                AttendanceReport.sla_due < now,
            )
        ).count()

        return jsonify(
            {
                "daily_reports": [
                    {
                        "date": str(d.date),
                        "count": d.count,
                    }
                    for d in daily_reports
                ],
                "sla_stats": {
                    "urgent": sla_urgent,
                    "overdue": sla_overdue,
                },
            }
        )

    except Exception as e:
        log_error(e, current_user.id)
        return jsonify({"error": "차트 데이터 조회 중 오류가 발생했습니다."}), 500


@my_reports_bp.route("/admin_dashboard/report_realtime_notifications")
@login_required
@admin_required
def report_realtime_notifications():
    """실시간 신고/이의제기 알림 API"""
    try:
        # 최근 1시간 내 신고/이의제기
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)

        recent_reports = (
            AttendanceReport.query.filter(
                AttendanceReport.created_at >= one_hour_ago
            )
            .order_by(AttendanceReport.created_at.desc())
            .limit(10)
            .all()
        )

        notifications = []
        for dispute in recent_reports if recent_reports is not None:
            notifications.append(
                {
                    "id": dispute.id,
                    "type": dispute.dispute_type,
                    "status": dispute.status,
                    "created_at": dispute.created_at.strftime("%H:%M"),
                    "time_ago": get_time_ago(dispute.created_at),
                }
            )

        return jsonify({"notifications": notifications})

    except Exception as e:
        log_error(e, current_user.id)
        return jsonify({"error": "알림 조회 중 오류가 발생했습니다."}), 500


def get_time_ago(dt):
    """시간 차이를 사람이 읽기 쉬운 형태로 반환"""
    now = datetime.utcnow()
    diff = now - dt

    if diff.days > 0:
        return f"{diff.days}일 전"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours}시간 전"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes}분 전"
    else:
        return "방금 전"
