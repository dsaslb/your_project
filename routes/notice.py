from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os

from models import Notice, NoticeComment, Report, db
from utils.decorators import admin_required
from utils.file_utils import save_file, delete_file
from utils.logger import log_action
from services.notice_service import update_notice

notice_bp = Blueprint('notice', __name__, url_prefix='/notice')

# 공지사항 목록
@notice_bp.route('/')
@login_required
def list_notices():
    page = request.args.get('page', 1, type=int)
    notices = Notice.query.filter_by(is_hidden=False).order_by(Notice.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('notices.html', notices=notices)

# 공지사항 상세 보기
@notice_bp.route('/<int:notice_id>')
@login_required
def view_notice(notice_id):
    notice = Notice.query.get_or_404(notice_id)
    if notice.is_hidden and not (current_user.is_admin() or current_user.is_manager()):
        flash('비공개된 공지사항입니다.', 'warning')
        return redirect(url_for('notice.list_notices'))
    return render_template('notice_view.html', notice=notice)

# 새 공지사항 작성
@notice_bp.route('/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_notice():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form['category']
        file = request.files.get('file')

        file_path, file_type = None, None
        if file and file.filename != '':
            file_path, file_type = save_file(file)

        new_notice = Notice(
            title=title,
            content=content,
            author_id=current_user.id,
            category=category,
            file_path=file_path,
            file_type=file_type
        )
        db.session.add(new_notice)
        db.session.commit()
        log_action(current_user.id, 'NOTICE_CREATE', f"New notice created: {title}")
        flash('공지사항이 성공적으로 등록되었습니다.', 'success')
        return redirect(url_for('notice.list_notices'))
    return render_template('notice_new.html')

# 공지사항 수정
@notice_bp.route('/<int:notice_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_notice(notice_id):
    notice = Notice.query.get_or_404(notice_id)
    if request.method == 'POST':
        form_data = request.form.to_dict()
        file = request.files.get('file')
        
        updated_notice = update_notice(notice_id, form_data, file, current_user.id)

        if updated_notice:
            log_action(current_user.id, 'NOTICE_EDIT', f"Notice edited: {notice.id}")
            flash('공지사항이 성공적으로 수정되었습니다.', 'success')
            return redirect(url_for('notice.view_notice', notice_id=notice.id))
        else:
            flash('공지사항을 찾을 수 없거나 수정에 실패했습니다.', 'error')
            
    return render_template('notice_edit.html', notice=notice)

# 공지사항 삭제
@notice_bp.route('/<int:notice_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_notice(notice_id):
    notice = Notice.query.get_or_404(notice_id)
    if notice.file_path:
        delete_file(notice.file_path)

    db.session.delete(notice)
    db.session.commit()
    log_action(current_user.id, 'NOTICE_DELETE', f"Notice deleted: {notice.id}")
    flash('공지사항이 삭제되었습니다.', 'success')
    return redirect(url_for('notice.list_notices'))

# 공지사항 숨김/해제
@notice_bp.route('/<int:notice_id>/hide', methods=['POST'])
@login_required
@admin_required
def hide_notice(notice_id):
    notice = Notice.query.get_or_404(notice_id)
    notice.is_hidden = not notice.is_hidden
    action = 'hide' if notice.is_hidden else 'unhide'
    db.session.commit()
    log_action(current_user.id, 'NOTICE_HIDE', f"Notice {action}: {notice.id}")
    flash(f'공지사항이 {"숨김" if notice.is_hidden else "공개"} 처리되었습니다.', 'success')
    return redirect(request.referrer or url_for('notice.list_notices'))

# 댓글 작성
@notice_bp.route('/<int:notice_id>/comment', methods=['POST'])
@login_required
def add_comment(notice_id):
    content = request.form.get('content')
    if content:
        comment = NoticeComment(
            content=content,
            user_id=current_user.id,
            notice_id=notice_id
        )
        db.session.add(comment)
        db.session.commit()
        log_action(current_user.id, 'COMMENT_CREATE', f"Comment created on notice {notice_id}")
        flash('댓글이 작성되었습니다.', 'success')
    return redirect(url_for('notice.view_notice', notice_id=notice_id))

# 댓글 삭제
@notice_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = NoticeComment.query.get_or_404(comment_id)
    if not (current_user.id == comment.user_id or current_user.is_admin()):
        flash('삭제 권한이 없습니다.', 'error')
        return redirect(url_for('notice.view_notice', notice_id=comment.notice_id))

    db.session.delete(comment)
    db.session.commit()
    log_action(current_user.id, 'COMMENT_DELETE', f"Comment deleted: {comment_id}")
    flash('댓글이 삭제되었습니다.', 'success')
    return redirect(url_for('notice.view_notice', notice_id=comment.notice_id))

# 댓글 숨김/해제
@notice_bp.route('/comment/<int:comment_id>/hide', methods=['POST'])
@login_required
@admin_required
def hide_comment(comment_id):
    comment = NoticeComment.query.get_or_404(comment_id)
    comment.is_hidden = not comment.is_hidden
    action = 'hide' if comment.is_hidden else 'unhide'
    db.session.commit()
    log_action(current_user.id, 'COMMENT_HIDE', f"Comment {action}: {comment_id}")
    flash(f'댓글이 {"숨김" if comment.is_hidden else "공개"} 처리되었습니다.', 'success')
    return redirect(url_for('notice.view_notice', notice_id=comment.notice_id))

# 공지사항/댓글 신고
@notice_bp.route('/report', methods=['POST'])
@login_required
def report():
    target_type = request.form.get('target_type')
    target_id = request.form.get('target_id', type=int)
    reason = request.form.get('reason')
    category = request.form.get('category')

    if not all([target_type, target_id, reason, category]):
        flash('잘못된 요청입니다.', 'error')
        return redirect(request.referrer)

    existing_report = Report.query.filter_by(
        target_type=target_type,
        target_id=target_id,
        user_id=current_user.id
    ).first()

    if existing_report:
        flash('이미 신고한 게시물 또는 댓글입니다.', 'warning')
        return redirect(request.referrer)

    new_report = Report(
        target_type=target_type,
        target_id=target_id,
        user_id=current_user.id,
        reason=reason,
        category=category
    )
    db.session.add(new_report)
    db.session.commit()
    log_action(current_user.id, 'REPORT_CREATE', f"Reported {target_type} {target_id}")

    flash('신고가 접수되었습니다.', 'success')
    return redirect(request.referrer) 