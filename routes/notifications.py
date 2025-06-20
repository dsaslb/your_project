from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from datetime import datetime

from extensions import db
from models import User, ApproveLog, Attendance
from utils.decorators import admin_required
from utils.notify import send_notification, notify_approval_result, notify_attendance_issue
from utils.logger import log_action, log_error

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/admin/send_notification', methods=['GET', 'POST'])
@login_required
@admin_required
def send_notification_page():
    """관리자 알림 발송"""
    if request.method == 'POST':
        try:
            notification_type = request.form.get('notification_type', 'email')
            message = request.form.get('message', '')
            user_ids = request.form.getlist('user_ids')
            
            if not message:
                flash('알림 내용을 입력해주세요.', 'error')
                return redirect(url_for('notifications.send_notification_page'))
            
            users = []
            if user_ids:
                users = User.query.filter(User.id.in_(user_ids)).all()
            else:
                users = User.query.filter_by(status='approved').all()
            
            success_count = 0
            for user in users:
                success, _ = send_notification(user, message, notification_type)
                if success:
                    success_count += 1
            
            log_action(current_user.id, 'NOTIFICATION_SENT', f'Sent {notification_type} to {success_count} users')
            flash(f'알림 발송 완료! 성공: {success_count}명', 'success')
            
            return redirect(url_for('admin_dashboard'))
            
        except Exception as e:
            log_error(e, current_user.id)
            flash('알림 발송 중 오류가 발생했습니다.', 'error')
            return redirect(url_for('notifications.send_notification_page'))
    
    # GET 요청: 알림 발송 페이지
    users = User.query.filter_by(status='approved').all()
    return render_template('admin/send_notification.html', users=users)

@notifications_bp.route('/admin/approve_user/<int:user_id>/<action>')
@login_required
@admin_required
def approve_user_with_notification(user_id, action):
    """승인/거절 처리 (알림 포함)"""
    try:
        user = User.query.get_or_404(user_id)
        reason = request.args.get('reason', '')
        
        if action == 'approve':
            user.status = 'approved'
            message = f'사용자 {user.username} 승인됨'
            log_action(current_user.id, 'USER_APPROVED', f'Approved user {user.username}')
            
            # 승인 알림 발송
            notify_approval_result(user, True)
            
        elif action == 'reject':
            user.status = 'rejected'
            message = f'사용자 {user.username} 거절됨'
            log_action(current_user.id, 'USER_REJECTED', f'Rejected user {user.username}')
            
            # 거절 알림 발송
            notify_approval_result(user, False)
        
        # 승인 로그 기록
        approve_log = ApproveLog(
            user_id=user_id,
            action=action,
            admin_id=current_user.id,
            reason=reason
        )
        db.session.add(approve_log)
        db.session.commit()
        
        flash(message, 'success')
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('사용자 처리 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('approve_users'))

@notifications_bp.route('/admin/attendance_notification/<int:user_id>')
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
            extract('year', Attendance.clock_in) == year,
            extract('month', Attendance.clock_in) == month,
            Attendance.clock_out.isnot(None)
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
            notify_attendance_issue(user, year, month, lateness, early_leave, night_work)
            flash(f'{user.name or user.username}님에게 근태 알림을 발송했습니다.', 'success')
        else:
            flash(f'{user.name or user.username}님은 근태 이상이 없습니다.', 'info')
        
        log_action(current_user.id, 'ATTENDANCE_NOTIFICATION_SENT', f'Sent attendance notification to {user.username}')
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('근태 알림 발송 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('admin_users'))

@notifications_bp.route('/admin/bulk_attendance_notification')
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

        users = User.query.filter_by(status='approved').all()
        notification_count = 0

        for user in users:
            attendances = Attendance.query.filter(
                Attendance.user_id == user.id,
                extract('year', Attendance.clock_in) == year,
                extract('month', Attendance.clock_in) == month,
                Attendance.clock_out.isnot(None)
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
                notify_attendance_issue(user, year, month, lateness, early_leave, night_work)
                notification_count += 1

        log_action(current_user.id, 'BULK_ATTENDANCE_NOTIFICATION', f'Sent attendance notifications to {notification_count} users')
        flash(f'근태 알림 발송 완료! {notification_count}명에게 발송', 'success')
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('근태 알림 발송 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('admin_dashboard')) 