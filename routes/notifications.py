from datetime import datetime, timedelta

from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required
from sqlalchemy import and_, or_

from extensions import db
from models import ApproveLog, Attendance, Notification, User
from utils.decorators import admin_required
from utils.logger import log_action, log_error
from utils.notify import (notify_approval_result, notify_attendance_issue,
                          send_notification)

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("/notifications")
@login_required
def notification_center():
    """알림센터 - 필터링, 카테고리별 탭, 권한별 구분"""
    try:
        # 필터 파라미터
        category = request.args.get("category", "")
        is_read = request.args.get("is_read", "")
        page = request.args.get("page", 1, type=int)
        per_page = 20

        # 기본 쿼리
        query = Notification.query.filter_by(user_id=current_user.id)

        # 카테고리 필터
        if category:
            query = query.filter_by(category=category)

        # 읽음/안읽음 필터
        if is_read == "0":
            query = query.filter_by(is_read=False)
        elif is_read == "1":
            query = query.filter_by(is_read=True)

        # 정렬 (최신순)
        query = query.order_by(Notification.created_at.desc())

        # 페이징
        notifications = query.paginate(page=page, per_page=per_page, error_out=False)

        # 카테고리별 통계
        category_stats = (
            db.session.query(
                Notification.category,
                db.func.count(Notification.id).label("total"),
                db.func.sum(db.case((Notification.is_read == False, 1), else_=0)).label(
                    "unread"
                ),
            )
            .filter_by(user_id=current_user.id)
            .group_by(Notification.category)
            .all()
        )

        # 전체 통계
        total_notifications = Notification.query.filter_by(
            user_id=current_user.id
        ).count()
        unread_count = Notification.query.filter_by(
            user_id=current_user.id, is_read=False
        ).count()

        return render_template(
            "notifications.html",
            notifications=notifications,
            category_stats=category_stats,
            total_notifications=total_notifications,
            unread_count=unread_count,
            current_category=category,
            current_is_read=is_read,
        )

    except Exception as e:
        log_error(e, current_user.id)
        flash("알림센터 로딩 중 오류가 발생했습니다.", "error")
        return redirect(url_for("dashboard"))


@notifications_bp.route("/notifications/mark_read/<int:notification_id>")
@login_required
def mark_notification_read(notification_id):
    """알림 읽음 처리"""
    try:
        notification = Notification.query.filter_by(
            id=notification_id, user_id=current_user.id
        ).first_or_404()

        notification.is_read = True
        db.session.commit()

        return jsonify({"success": True})

    except Exception as e:
        log_error(e, current_user.id)
        return jsonify({"success": False, "error": str(e)})


@notifications_bp.route("/notifications/mark_all_read")
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
        log_error(e, current_user.id)
        flash("알림 처리 중 오류가 발생했습니다.", "error")

    return redirect(url_for("notifications.notification_center"))


@notifications_bp.route("/admin/notifications")
@login_required
@admin_required
def admin_notification_center():
    """관리자 알림센터 - 모든 사용자 알림 관리"""
    try:
        # 필터 파라미터
        category = request.args.get("category", "")
        is_read = request.args.get("is_read", "")
        user_id = request.args.get("user_id", "", type=int)
        page = request.args.get("page", 1, type=int)
        per_page = 30

        # 기본 쿼리 (관리자는 모든 알림 조회 가능)
        query = Notification.query.join(User)

        # 카테고리 필터
        if category:
            query = query.filter_by(category=category)

        # 읽음/안읽음 필터
        if is_read == "0":
            query = query.filter_by(is_read=False)
        elif is_read == "1":
            query = query.filter_by(is_read=True)

        # 사용자 필터
        if user_id:
            query = query.filter_by(user_id=user_id)

        # 정렬 (최신순)
        query = query.order_by(Notification.created_at.desc())

        # 페이징
        notifications = query.paginate(page=page, per_page=per_page, error_out=False)

        # 카테고리별 통계
        category_stats = (
            db.session.query(
                Notification.category,
                db.func.count(Notification.id).label("total"),
                db.func.sum(db.case((Notification.is_read == False, 1), else_=0)).label(
                    "unread"
                ),
            )
            .group_by(Notification.category)
            .all()
        )

        # 사용자별 통계
        user_stats = (
            db.session.query(
                User.username,
                User.name,
                db.func.count(Notification.id).label("total"),
                db.func.sum(db.case((Notification.is_read == False, 1), else_=0)).label(
                    "unread"
                ),
            )
            .join(Notification)
            .group_by(User.id, User.username, User.name)
            .all()
        )

        # 전체 통계
        total_notifications = Notification.query.count()
        unread_count = Notification.query.filter_by(is_read=False).count()

        # 사용자 목록 (필터용) - 통합 API와 동일한 로직
        users = User.query.filter(
            User.role.in_(['employee', 'manager']),
            User.status.in_(['approved', 'active'])
        ).order_by(User.name).all()

        return render_template(
            "admin/notifications.html",
            notifications=notifications,
            category_stats=category_stats,
            user_stats=user_stats,
            total_notifications=total_notifications,
            unread_count=unread_count,
            users=users,
            current_category=category,
            current_is_read=is_read,
            current_user_id=user_id,
        )

    except Exception as e:
        log_error(e, current_user.id)
        flash("관리자 알림센터 로딩 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_dashboard"))


@notifications_bp.route("/admin/notifications/delete/<int:notification_id>")
@login_required
@admin_required
def delete_notification(notification_id):
    """알림 삭제 (관리자만)"""
    try:
        notification = Notification.query.get_or_404(notification_id)
        db.session.delete(notification)
        db.session.commit()

        flash("알림이 삭제되었습니다.", "success")

    except Exception as e:
        log_error(e, current_user.id)
        flash("알림 삭제 중 오류가 발생했습니다.", "error")

    return redirect(url_for("notifications.admin_notification_center"))


@notifications_bp.route("/admin/notifications/bulk_delete", methods=["POST"])
@login_required
@admin_required
def bulk_delete_notifications():
    """알림 일괄 삭제 (관리자만)"""
    try:
        notification_ids = request.form.getlist("notification_ids")

        if notification_ids:
            Notification.query.filter(Notification.id.in_(notification_ids)).delete(
                synchronize_session=False
            )
            db.session.commit()
            flash(f"{len(notification_ids)}개의 알림이 삭제되었습니다.", "success")
        else:
            flash("삭제할 알림을 선택해주세요.", "error")

    except Exception as e:
        log_error(e, current_user.id)
        flash("알림 일괄 삭제 중 오류가 발생했습니다.", "error")

    return redirect(url_for("notifications.admin_notification_center"))


@notifications_bp.route("/admin/send_notification", methods=["GET", "POST"])
@login_required
@admin_required
def send_notification_page():
    """관리자 알림 발송"""
    if request.method == "POST":
        try:
            notification_type = request.form.get("notification_type", "email")
            message = request.form.get("message", "")
            user_ids = request.form.getlist("user_ids")

            if not message:
                flash("알림 내용을 입력해주세요.", "error")
                return redirect(url_for("notifications.send_notification_page"))

            users = []
            if user_ids:
                users = User.query.filter(User.id.in_(user_ids)).all()
            else:
                users = User.query.filter(
                User.role.in_(['employee', 'manager']),
                User.status.in_(['approved', 'active'])
            ).order_by(User.name).all()

            success_count = 0
            for user in users:
                success, _ = send_notification(user, message, notification_type)
                if success:
                    success_count += 1

            log_action(
                current_user.id,
                "NOTIFICATION_SENT",
                f"Sent {notification_type} to {success_count} users",
            )
            flash(f"알림 발송 완료! 성공: {success_count}명", "success")

            return redirect(url_for("admin_dashboard"))

        except Exception as e:
            log_error(e, current_user.id)
            flash("알림 발송 중 오류가 발생했습니다.", "error")
            return redirect(url_for("notifications.send_notification_page"))

    # GET 요청: 알림 발송 페이지 - 통합 API와 동일한 로직
    users = User.query.filter(
        User.role.in_(['employee', 'manager']),
        User.status.in_(['approved', 'active'])
    ).order_by(User.name).all()
    return render_template("admin/send_notification.html", users=users)


@notifications_bp.route("/admin/approve_user/<int:user_id>/<action>")
@login_required
@admin_required
def approve_user_with_notification(user_id, action):
    """승인/거절 처리 (알림 포함)"""
    try:
        user = User.query.get_or_404(user_id)
        reason = request.args.get("reason", "")

        if action == "approve":
            user.status = "approved"
            message = f"사용자 {user.username} 승인됨"
            log_action(
                current_user.id, "USER_APPROVED", f"Approved user {user.username}"
            )

            # 승인 알림 발송
            notify_approval_result(user, True)

        elif action == "reject":
            user.status = "rejected"
            message = f"사용자 {user.username} 거절됨"
            log_action(
                current_user.id, "USER_REJECTED", f"Rejected user {user.username}"
            )

            # 거절 알림 발송
            notify_approval_result(user, False)

        # 승인 로그 기록
        approve_log = ApproveLog(
            user_id=user_id, action=action, admin_id=current_user.id, reason=reason
        )
        db.session.add(approve_log)
        db.session.commit()

        flash(message, "success")

    except Exception as e:
        log_error(e, current_user.id)
        flash("사용자 처리 중 오류가 발생했습니다.", "error")

    return redirect(url_for("approve_users"))


@notifications_bp.route("/admin/attendance_notification/<int:user_id>")
@login_required
@admin_required
def send_attendance_notification(user_id):
    """근태 이상 알림 발송"""
    try:
        from datetime import time

        from sqlalchemy import extract

        user = User.query.get_or_404(user_id)
        now = datetime.utcnow()
        year, month = now.year, now.month

        STANDARD_CLOCKIN = time(9, 0, 0)
        STANDARD_CLOCKOUT = time(18, 0, 0)
        NIGHT_WORK_START = time(21, 0, 0)

        # 해당 월 출근 기록 조회
        attendances = Attendance.query.filter(
            Attendance.user_id == user_id,
            extract("year", Attendance.clock_in) == year,
            extract("month", Attendance.clock_in) == month,
            Attendance.clock_out.isnot(None),
        ).all()

        # 통계 계산
        lateness = early_leave = night_work = 0
        for att in attendances:
            if att.clock_in and att.clock_in.time() > STANDARD_CLOCKIN:
                lateness += 1
            if att.clock_out and att.clock_out.time() < STANDARD_CLOCKOUT:
                early_leave += 1
            if att.clock_out and att.clock_out.time() > NIGHT_WORK_START:
                night_work += 1

        # 근태 이상이 있는 경우에만 알림 발송
        if lateness > 0 or early_leave > 0 or night_work > 0:
            notify_attendance_issue(
                user, year, month, lateness, early_leave, night_work
            )
            flash(
                f"{user.name or user.username}님에게 근태 알림을 발송했습니다.",
                "success",
            )
        else:
            flash(f"{user.name or user.username}님은 근태 이상이 없습니다.", "info")

        log_action(
            current_user.id,
            "ATTENDANCE_NOTIFICATION_SENT",
            f"Sent attendance notification to {user.username}",
        )

    except Exception as e:
        log_error(e, current_user.id)
        flash("근태 알림 발송 중 오류가 발생했습니다.", "error")

    return redirect(url_for("admin_users"))


@notifications_bp.route("/admin/bulk_attendance_notification")
@login_required
@admin_required
def bulk_attendance_notification():
    """전체 직원 근태 알림 발송"""
    try:
        from datetime import time

        from sqlalchemy import extract

        now = datetime.utcnow()
        year, month = now.year, now.month

        STANDARD_CLOCKIN = time(9, 0, 0)
        STANDARD_CLOCKOUT = time(18, 0, 0)
        NIGHT_WORK_START = time(21, 0, 0)

        users = User.query.filter_by(status="approved").all()
        notification_count = 0

        for user in users:
            attendances = Attendance.query.filter(
                Attendance.user_id == user.id,
                extract("year", Attendance.clock_in) == year,
                extract("month", Attendance.clock_in) == month,
                Attendance.clock_out.isnot(None),
            ).all()

            lateness = early_leave = night_work = 0
            for att in attendances:
                if att.clock_in and att.clock_in.time() > STANDARD_CLOCKIN:
                    lateness += 1
                if att.clock_out and att.clock_out.time() < STANDARD_CLOCKOUT:
                    early_leave += 1
                if att.clock_out and att.clock_out.time() > NIGHT_WORK_START:
                    night_work += 1

            # 근태 이상이 있는 경우에만 알림 발송
            if lateness > 0 or early_leave > 0 or night_work > 0:
                notify_attendance_issue(
                    user, year, month, lateness, early_leave, night_work
                )
                notification_count += 1

        log_action(
            current_user.id,
            "BULK_ATTENDANCE_NOTIFICATION",
            f"Sent attendance notifications to {notification_count} users",
        )
        flash(f"근태 알림 발송 완료! {notification_count}명에게 발송", "success")

    except Exception as e:
        log_error(e, current_user.id)
        flash("근태 알림 발송 중 오류가 발생했습니다.", "error")

    return redirect(url_for("admin_dashboard"))


@notifications_bp.route("/unread-count")
def api_unread_count():
    """미확인 알림 개수 API"""
    try:
        # JWT 토큰에서 사용자 ID 추출 (실제 구현에서는 토큰 검증 필요)
        # 임시로 더미 데이터 반환
        unread_count = 3  # 실제로는 current_user.id로 조회
        
        return jsonify({"unread_count": unread_count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
