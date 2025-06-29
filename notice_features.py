"""
공지사항 관련 새로운 기능들
- 변경이력 관리
- 숨김 처리 (Soft Delete)
- 신고 시스템
- 관리자 검토 기능
"""

import os

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required

from extensions import db
from models import (CommentHistory, Notice, NoticeComment, NoticeHistory,
                    NoticeRead, Report, User)
from utils.decorators import (MAX_PREVIEW_SIZE, admin_required, escape_html,
                              owner_or_admin, safe_remove, sanitize_filename,
                              validate_file_size)
from utils.logger import log_action, log_action_consistency, log_error

# Blueprint 생성
notice_features = Blueprint("notice_features", __name__)


def save_notice_history(notice, editor_id, action="edit"):
    """공지사항 변경이력 저장"""
    try:
        hist = NoticeHistory(
            notice_id=notice.id,
            editor_id=editor_id,
            before_title=notice.title,
            before_content=notice.content,
            before_file_path=notice.file_path,
            before_file_type=notice.file_type,
            action=action,
            ip_address=request.remote_addr,
        )
        db.session.add(hist)
        db.session.commit()
        log_action(
            editor_id,
            "NOTICE_HISTORY_SAVED",
            f"Saved history for notice {notice.id}, action: {action}",
        )
    except Exception as e:
        log_error(e, editor_id)
        db.session.rollback()


def save_comment_history(comment, editor_id, action="edit"):
    """댓글 변경이력 저장"""
    try:
        hist = CommentHistory(
            comment_id=comment.id,
            editor_id=editor_id,
            before_content=comment.content,
            action=action,
            ip_address=request.remote_addr,
        )
        db.session.add(hist)
        db.session.commit()
        log_action(
            editor_id,
            "COMMENT_HISTORY_SAVED",
            f"Saved history for comment {comment.id}, action: {action}",
        )
    except Exception as e:
        log_error(e, editor_id)
        db.session.rollback()


# === 공지사항 수정 ===
@notice_features.route("/notice/edit/<int:notice_id>", methods=["GET", "POST"])
@login_required
@owner_or_admin(lambda notice_id: Notice.query.get_or_404(notice_id))
def notice_edit(notice_id):
    """공지사항 수정"""
    notice = Notice.query.get_or_404(notice_id)

    if request.method == "POST":
        try:
            # 변경이력 저장
            save_notice_history(notice, current_user.id, "edit")

            title = request.form.get("title", "").strip()
            content = request.form.get("content", "").strip()
            category = request.form.get("category", "").strip()

            if not title or not content:
                flash("제목과 내용을 입력해주세요.", "error")
                return render_template("notice_edit.html", notice=notice)

            # 기존 파일 정보 저장
            old_file_path = notice.file_path
            old_file_type = notice.file_type

            # 새 파일 업로드 처리
            file = request.files.get("file")
            if file and file.filename:
                try:
                    # 파일 업로드 처리 함수 필요
                    from app import save_uploaded_file

                    file_path, file_type = save_uploaded_file(file)
                    # 기존 파일 삭제
                    if old_file_path:
                        safe_remove(os.path.join("static", old_file_path))
                    notice.file_path = file_path
                    notice.file_type = file_type
                except ValueError as e:
                    flash(str(e), "error")
                    return render_template("notice_edit.html", notice=notice)

            notice.title = title
            notice.content = content
            notice.category = category
            db.session.commit()

            log_action_consistency(
                current_user.id,
                "NOTICE_EDITED",
                f"Edited notice: {title}",
                request.remote_addr,
            )
            flash("공지사항이 수정되었습니다!", "success")
            return redirect(url_for("notice_view", notice_id=notice_id))

        except Exception as e:
            log_error(e, current_user.id)
            flash("공지사항 수정 중 오류가 발생했습니다.", "error")
            return redirect(url_for("notice_edit", notice_id=notice_id))

    return render_template("notice_edit.html", notice=notice)


# === 공지사항 숨김/숨김해제 ===
@notice_features.route("/notice/hide/<int:notice_id>", methods=["POST"])
@login_required
@owner_or_admin(lambda notice_id: Notice.query.get_or_404(notice_id))
def notice_hide(notice_id):
    """공지사항 숨김 처리"""
    try:
        notice = Notice.query.get_or_404(notice_id)

        if notice.is_hidden:
            flash("이미 숨김 처리된 공지사항입니다.", "warning")
            return redirect(url_for("notice_view", notice_id=notice_id))

        # 변경이력 저장
        save_notice_history(notice, current_user.id, "hide")

        notice.is_hidden = True
        db.session.commit()

        log_action_consistency(
            current_user.id,
            "NOTICE_HIDDEN",
            f"Hidden notice: {notice.title}",
            request.remote_addr,
        )
        flash("공지사항이 숨김 처리되었습니다.", "success")
        return redirect(url_for("notices"))

    except Exception as e:
        log_error(e, current_user.id)
        flash("공지사항 숨김 처리 중 오류가 발생했습니다.", "error")
        return redirect(url_for("notice_view", notice_id=notice_id))


@notice_features.route("/notice/unhide/<int:notice_id>", methods=["POST"])
@login_required
@owner_or_admin(lambda notice_id: Notice.query.get_or_404(notice_id))
def notice_unhide(notice_id):
    """공지사항 숨김 해제"""
    try:
        notice = Notice.query.get_or_404(notice_id)

        if not notice.is_hidden:
            flash("숨김 처리되지 않은 공지사항입니다.", "warning")
            return redirect(url_for("notice_view", notice_id=notice_id))

        # 변경이력 저장
        save_notice_history(notice, current_user.id, "unhide")

        notice.is_hidden = False
        db.session.commit()

        log_action_consistency(
            current_user.id,
            "NOTICE_UNHIDDEN",
            f"Unhidden notice: {notice.title}",
            request.remote_addr,
        )
        flash("공지사항 숨김이 해제되었습니다.", "success")
        return redirect(url_for("notices"))

    except Exception as e:
        log_error(e, current_user.id)
        flash("공지사항 숨김 해제 중 오류가 발생했습니다.", "error")
        return redirect(url_for("notice_view", notice_id=notice_id))


# === 댓글 숨김/숨김해제 ===
@notice_features.route("/comment/hide/<int:comment_id>", methods=["POST"])
@login_required
@owner_or_admin(lambda comment_id: NoticeComment.query.get_or_404(comment_id))
def comment_hide(comment_id):
    """댓글 숨김 처리"""
    try:
        comment = NoticeComment.query.get_or_404(comment_id)

        if comment.is_hidden:
            flash("이미 숨김 처리된 댓글입니다.", "warning")
            return redirect(url_for("notice_view", notice_id=comment.notice_id))

        # 변경이력 저장
        save_comment_history(comment, current_user.id, "hide")

        comment.is_hidden = True
        db.session.commit()

        log_action_consistency(
            current_user.id,
            "COMMENT_HIDDEN",
            f"Hidden comment {comment_id}",
            request.remote_addr,
        )
        flash("댓글이 숨김 처리되었습니다.", "success")
        return redirect(url_for("notice_view", notice_id=comment.notice_id))

    except Exception as e:
        log_error(e, current_user.id)
        flash("댓글 숨김 처리 중 오류가 발생했습니다.", "error")
        return redirect(url_for("notices"))


@notice_features.route("/comment/unhide/<int:comment_id>", methods=["POST"])
@login_required
@owner_or_admin(lambda comment_id: NoticeComment.query.get_or_404(comment_id))
def comment_unhide(comment_id):
    """댓글 숨김 해제"""
    try:
        comment = NoticeComment.query.get_or_404(comment_id)

        if not comment.is_hidden:
            flash("숨김 처리되지 않은 댓글입니다.", "warning")
            return redirect(url_for("notice_view", notice_id=comment.notice_id))

        # 변경이력 저장
        save_comment_history(comment, current_user.id, "unhide")

        comment.is_hidden = False
        db.session.commit()

        log_action_consistency(
            current_user.id,
            "COMMENT_UNHIDDEN",
            f"Unhidden comment {comment_id}",
            request.remote_addr,
        )
        flash("댓글 숨김이 해제되었습니다.", "success")
        return redirect(url_for("notice_view", notice_id=comment.notice_id))

    except Exception as e:
        log_error(e, current_user.id)
        flash("댓글 숨김 해제 중 오류가 발생했습니다.", "error")
        return redirect(url_for("notices"))


# === 신고 시스템 ===
@notice_features.route("/report/<target_type>/<int:target_id>", methods=["POST"])
@login_required
def report(target_type, target_id):
    """신고 처리"""
    try:
        reason = request.form.get("reason", "").strip()
        detail = request.form.get("detail", "").strip()

        if not reason:
            flash("신고 사유를 입력해주세요.", "error")
            return redirect(request.referrer or url_for("notices"))

        # 중복 신고 확인
        existing_report = Report.query.filter_by(
            target_type=target_type,
            target_id=target_id,
            user_id=current_user.id,
            status="pending",
        ).first()

        if existing_report:
            flash("이미 신고한 게시물입니다.", "warning")
            return redirect(request.referrer or url_for("notices"))

        # 신고 대상 존재 확인
        if target_type == "notice":
            target = Notice.query.get(target_id)
            if not target:
                flash("존재하지 않는 공지사항입니다.", "error")
                return redirect(url_for("notices"))
        elif target_type == "comment":
            target = NoticeComment.query.get(target_id)
            if not target:
                flash("존재하지 않는 댓글입니다.", "error")
                return redirect(url_for("notices"))
        else:
            flash("잘못된 신고 대상입니다.", "error")
            return redirect(url_for("notices"))

        # 신고 등록
        report = Report(
            target_type=target_type,
            target_id=target_id,
            user_id=current_user.id,
            reason=reason,
            detail=detail,
        )
        db.session.add(report)
        db.session.commit()

        log_action(
            current_user.id, "REPORT_SUBMITTED", f"Reported {target_type} {target_id}"
        )
        flash("신고가 접수되었습니다. 관리자가 검토합니다.", "success")
        return redirect(request.referrer or url_for("notices"))

    except Exception as e:
        log_error(e, current_user.id)
        flash("신고 처리 중 오류가 발생했습니다.", "error")
        return redirect(request.referrer or url_for("notices"))


# === 관리자 기능 ===
@notice_features.route("/admin/reports")
@login_required
@admin_required
def admin_reports():
    """관리자: 신고 내역 조회"""
    try:
        reports = Report.query.order_by(Report.created_at.desc()).all()
        return render_template("admin/reports.html", reports=reports)
    except Exception as e:
        log_error(e, current_user.id)
        flash("신고 내역 조회 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_dashboard"))


@notice_features.route("/admin/report/<int:report_id>/review", methods=["POST"])
@login_required
@admin_required
def admin_report_review(report_id):
    """관리자: 신고 검토 처리"""
    try:
        report = Report.query.get_or_404(report_id)
        action = request.form.get("action")  # 'resolve' or 'dismiss'
        admin_comment = request.form.get("admin_comment", "").strip()

        if action == "resolve":
            report.status = "resolved"
            flash("신고가 해결되었습니다.", "success")
        elif action == "dismiss":
            report.status = "dismissed"
            flash("신고가 기각되었습니다.", "info")
        else:
            flash("잘못된 처리입니다.", "error")
            return redirect(url_for("admin_reports"))

        report.admin_comment = admin_comment
        report.reviewed_at = db.func.now()
        report.reviewed_by = current_user.id
        db.session.commit()

        log_action(
            current_user.id, "REPORT_REVIEWED", f"Reviewed report {report_id}: {action}"
        )
        return redirect(url_for("admin_reports"))

    except Exception as e:
        log_error(e, current_user.id)
        flash("신고 검토 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_reports"))


@notice_features.route("/admin/hidden_notices")
@login_required
@admin_required
def admin_hidden_notices():
    """관리자: 숨김 처리된 공지사항 조회"""
    try:
        notices = (
            Notice.query.filter_by(is_hidden=True)
            .order_by(Notice.created_at.desc())
            .all()
        )
        return render_template("admin/hidden_notices.html", notices=notices)
    except Exception as e:
        log_error(e, current_user.id)
        flash("숨김 공지사항 조회 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_dashboard"))


@notice_features.route("/admin/hidden_comments")
@login_required
@admin_required
def admin_hidden_comments():
    """관리자: 숨김 처리된 댓글 조회"""
    try:
        comments = (
            NoticeComment.query.filter_by(is_hidden=True)
            .order_by(NoticeComment.created_at.desc())
            .all()
        )
        return render_template("admin/hidden_comments.html", comments=comments)
    except Exception as e:
        log_error(e, current_user.id)
        flash("숨김 댓글 조회 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_dashboard"))


@notice_features.route("/admin/notice_history/<int:notice_id>")
@login_required
@admin_required
def admin_notice_history(notice_id):
    """관리자: 공지사항 변경이력 조회"""
    try:
        notice = Notice.query.get_or_404(notice_id)
        history = (
            NoticeHistory.query.filter_by(notice_id=notice_id)
            .order_by(NoticeHistory.edited_at.desc())
            .all()
        )
        return render_template(
            "admin/notice_history.html", notice=notice, history=history
        )
    except Exception as e:
        log_error(e, current_user.id)
        flash("공지사항 이력 조회 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_dashboard"))


@notice_features.route("/admin/comment_history/<int:comment_id>")
@login_required
@admin_required
def admin_comment_history(comment_id):
    """관리자: 댓글 변경이력 조회"""
    try:
        comment = NoticeComment.query.get_or_404(comment_id)
        history = (
            CommentHistory.query.filter_by(comment_id=comment_id)
            .order_by(CommentHistory.edited_at.desc())
            .all()
        )
        return render_template(
            "admin/comment_history.html", comment=comment, history=history
        )
    except Exception as e:
        log_error(e, current_user.id)
        flash("댓글 이력 조회 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_dashboard"))
