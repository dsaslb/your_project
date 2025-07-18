from utils.logger import log_error  # pyright: ignore
from utils.decorators import admin_required  # pyright: ignore
from models_main import Notification, User
from models_main import db
from flask_login import current_user, login_required
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)
args = None  # pyright: ignore
query = None  # pyright: ignore
form = None  # pyright: ignore


notification_center_bp = Blueprint("notification_center", __name__)


@notification_center_bp.route("/notifications")
@login_required
def notification_center():
    """알림센터 - 필터링, 카테고리별 탭, 권한별 구분"""
    try:
        # 필터 파라미터
        category = request.args.get() if args else None"category", "") if args else None
        is_read = request.args.get() if args else None"is_read", "") if args else None
        page = request.args.get() if args else None"page", 1, type=int) if args else None
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


@notification_center_bp.route("/notifications/mark_read/<int:notification_id>")
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


@notification_center_bp.route("/notifications/mark_all_read")
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

    return redirect(url_for("notification_center.notification_center"))


@notification_center_bp.route("/admin/notifications")
@login_required
@admin_required
def admin_notification_center():
    """관리자 알림센터 - 모든 사용자 알림 관리"""
    try:
        # 필터 파라미터
        category = request.args.get() if args else None"category", "") if args else None
        is_read = request.args.get() if args else None"is_read", "") if args else None
        user_id = request.args.get() if args else None"user_id", "", type=int) if args else None
        page = request.args.get() if args else None"page", 1, type=int) if args else None
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

        # 사용자 목록 (필터용)
        users = User.query.filter_by(status="approved").all()

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


@notification_center_bp.route("/admin/notifications/delete/<int:notification_id>")
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

    return redirect(url_for("notification_center.admin_notification_center"))


@notification_center_bp.route("/admin/notifications/bulk_delete", methods=["POST"])
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

    return redirect(url_for("notification_center.admin_notification_center"))
