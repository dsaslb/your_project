"""
담당자별 신고/이의제기 관리 라우트
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func

from extensions import db
from models import User, Attendance, AttendanceDispute
from utils.decorators import admin_required, team_lead_required
from utils.logger import log_action, log_error
from utils.notification_automation import send_notification
from utils.assignee_manager import assignee_manager
from utils.email_utils import email_service

my_reports_bp = Blueprint('my_reports', __name__)

@my_reports_bp.route('/admin_dashboard/my_reports')
@login_required
@admin_required
def my_reports():
    """내 담당 신고/이의제기 대시보드"""
    try:
        # 필터 파라미터
        status = request.args.get('status', '')
        dispute_type = request.args.get('dispute_type', '')
        sla_filter = request.args.get('sla_filter', '')
        
        # 자신이 담당자로 배정된 신고/이의만 조회
        query = AttendanceDispute.query.filter_by(assignee_id=current_user.id)
        
        if status:
            query = query.filter(AttendanceDispute.status == status)
        if dispute_type:
            query = query.filter(AttendanceDispute.dispute_type == dispute_type)
        
        # SLA 필터
        now = datetime.utcnow()
        if sla_filter == 'overdue':
            query = query.filter(
                and_(
                    AttendanceDispute.status.in_(['pending', 'processing']),
                    AttendanceDispute.sla_due < now
                )
            )
        elif sla_filter == 'urgent':
            query = query.filter(
                and_(
                    AttendanceDispute.status.in_(['pending', 'processing']),
                    AttendanceDispute.sla_due <= now + timedelta(hours=24),
                    AttendanceDispute.sla_due > now
                )
            )
        
        reports = query.order_by(AttendanceDispute.created_at.desc()).all()
        
        # 업무량 통계
        workload = assignee_manager.get_assignee_workload(current_user.id)
        
        # SLA 임박/초과 건수
        sla_urgent = AttendanceDispute.query.filter(
            and_(
                AttendanceDispute.assignee_id == current_user.id,
                AttendanceDispute.status.in_(['pending', 'processing']),
                AttendanceDispute.sla_due <= now + timedelta(hours=24),
                AttendanceDispute.sla_due > now
            )
        ).count()
        
        sla_overdue = AttendanceDispute.query.filter(
            and_(
                AttendanceDispute.assignee_id == current_user.id,
                AttendanceDispute.status.in_(['pending', 'processing']),
                AttendanceDispute.sla_due < now
            )
        ).count()
        
        context = {
            'reports': reports,
            'workload': workload,
            'sla_urgent': sla_urgent,
            'sla_overdue': sla_overdue,
            'filters': {
                'status': status,
                'dispute_type': dispute_type,
                'sla_filter': sla_filter
            }
        }
        
        return render_template('admin/my_reports.html', **context)
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('담당 신고/이의제기 목록을 불러오는 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_dashboard'))

@my_reports_bp.route('/admin_dashboard/my_reports/<int:report_id>/reply', methods=['POST'])
@login_required
@admin_required
def my_report_reply(report_id):
    """담당 신고/이의제기 답변 처리"""
    try:
        dispute = AttendanceDispute.query.get_or_404(report_id)
        
        # 본인이 담당자인지 확인
        if dispute.assignee_id != current_user.id:
            flash('담당자가 아닌 신고/이의제기입니다.', 'error')
            return redirect(url_for('my_reports.my_reports'))
        
        # 답변 내용
        reply = request.form.get('reply', '').strip()
        new_status = request.form.get('status', 'resolved')
        
        if not reply:
            flash('답변 내용을 입력해주세요.', 'error')
            return redirect(url_for('my_reports.my_reports'))
        
        # 상태 업데이트
        dispute.admin_reply = reply
        dispute.status = new_status
        dispute.admin_id = current_user.id
        dispute.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # 신고자에게 알림 발송
        send_notification(
            user_id=dispute.user_id,
            content=f"신고/이의제기에 답변이 등록되었습니다. (상태: {new_status})",
            category="신고/이의제기",
            link=f"/attendance/dispute/{dispute.id}"
        )
        
        # 이메일 알림 발송
        try:
            email_service.send_dispute_notification(dispute.id, 'replied')
        except Exception as e:
            log_error(e, current_user.id, f'Email notification failed for dispute {dispute.id}')
        
        # 로그 기록
        log_action(
            user_id=current_user.id,
            action=f"담당 신고/이의제기 답변 처리",
            details=f"신고ID: {dispute.id}, 상태: {new_status}, 답변: {reply[:50]}..."
        )
        
        flash('답변이 성공적으로 등록되었습니다.', 'success')
        return redirect(url_for('my_reports.my_reports'))
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('답변 처리 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('my_reports.my_reports'))

@my_reports_bp.route('/admin_dashboard/my_reports/<int:report_id>/reassign', methods=['POST'])
@login_required
@admin_required
def my_report_reassign(report_id):
    """담당 신고/이의제기 재배정"""
    try:
        dispute = AttendanceDispute.query.get_or_404(report_id)
        
        # 본인이 담당자인지 확인
        if dispute.assignee_id != current_user.id:
            flash('담당자가 아닌 신고/이의제기입니다.', 'error')
            return redirect(url_for('my_reports.my_reports'))
        
        new_assignee_id = request.form.get('assignee_id')
        reason = request.form.get('reason', '').strip()
        
        if not new_assignee_id:
            flash('새 담당자를 선택해주세요.', 'error')
            return redirect(url_for('my_reports.my_reports'))
        
        # 재배정 실행
        success, message = assignee_manager.reassign_dispute(
            report_id, 
            int(new_assignee_id), 
            reason
        )
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
        
        return redirect(url_for('my_reports.my_reports'))
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('재배정 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('my_reports.my_reports'))

@my_reports_bp.route('/admin_dashboard/my_reports/stats')
@login_required
@admin_required
def my_reports_stats():
    """담당 신고/이의제기 통계 API"""
    try:
        # 업무량 통계
        workload = assignee_manager.get_assignee_workload(current_user.id)
        
        # 최근 7일 처리 현황
        week_ago = datetime.utcnow() - timedelta(days=7)
        daily_stats = []
        
        for i in range(7):
            date = datetime.utcnow() - timedelta(days=i)
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            resolved_count = AttendanceDispute.query.filter(
                and_(
                    AttendanceDispute.assignee_id == current_user.id,
                    AttendanceDispute.status == 'resolved',
                    AttendanceDispute.updated_at >= start_date,
                    AttendanceDispute.updated_at <= end_date
                )
            ).count()
            
            daily_stats.append({
                'date': date.strftime('%m-%d'),
                'resolved': resolved_count
            })
        
        daily_stats.reverse()
        
        # SLA 통계
        now = datetime.utcnow()
        sla_urgent = AttendanceDispute.query.filter(
            and_(
                AttendanceDispute.assignee_id == current_user.id,
                AttendanceDispute.status.in_(['pending', 'processing']),
                AttendanceDispute.sla_due <= now + timedelta(hours=24),
                AttendanceDispute.sla_due > now
            )
        ).count()
        
        sla_overdue = AttendanceDispute.query.filter(
            and_(
                AttendanceDispute.assignee_id == current_user.id,
                AttendanceDispute.status.in_(['pending', 'processing']),
                AttendanceDispute.sla_due < now
            )
        ).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'workload': workload,
                'daily_stats': daily_stats,
                'sla_urgent': sla_urgent,
                'sla_overdue': sla_overdue
            }
        })
        
    except Exception as e:
        log_error(e, current_user.id)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@my_reports_bp.route('/admin_dashboard/assignee_stats')
@login_required
@admin_required
def assignee_stats():
    """전체 담당자 통계 (관리자용)"""
    try:
        stats = assignee_manager.get_assignee_stats()
        
        # 담당자 목록 (재배정용)
        assignees = User.query.filter(
            User.role.in_(['admin', 'manager', 'teamlead'])
        ).order_by(User.name).all()
        
        context = {
            'assignee_stats': stats['assignee_stats'],
            'sla_overdue': stats['sla_overdue'],
            'sla_urgent': stats['sla_urgent'],
            'assignees': assignees
        }
        
        return render_template('admin/assignee_stats.html', **context)
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('담당자 통계를 불러오는 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_dashboard'))

@my_reports_bp.route('/admin_dashboard/report/<int:report_id>/reassign', methods=['POST'])
@login_required
@admin_required
def report_reassign(report_id):
    """신고/이의제기 재배정 (관리자용)"""
    try:
        dispute = AttendanceDispute.query.get_or_404(report_id)
        
        new_assignee_id = request.form.get('assignee_id')
        reason = request.form.get('reason', '').strip()
        
        if not new_assignee_id:
            flash('새 담당자를 선택해주세요.', 'error')
            return redirect(url_for('admin_reports.admin_reports'))
        
        # 재배정 실행
        success, message = assignee_manager.reassign_dispute(
            report_id, 
            int(new_assignee_id), 
            reason
        )
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
        
        return redirect(url_for('admin_reports.admin_reports'))
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('재배정 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_reports.admin_reports'))

@my_reports_bp.route('/admin_dashboard/report_chart_data')
@login_required
@admin_required
def report_chart_data():
    """신고/이의제기 차트 데이터 API"""
    try:
        from sqlalchemy import func
        
        # 날짜별 신고/이의제기 통계
        data = db.session.query(
            func.strftime('%Y-%m-%d', AttendanceDispute.created_at).label('date'),
            func.count().label('count')
        ).group_by(
            func.strftime('%Y-%m-%d', AttendanceDispute.created_at)
        ).order_by('date').all()
        
        # 상태별 통계
        status_stats = db.session.query(
            AttendanceDispute.status,
            func.count().label('count')
        ).group_by(AttendanceDispute.status).all()
        
        # 유형별 통계
        type_stats = db.session.query(
            AttendanceDispute.dispute_type,
            func.count().label('count')
        ).group_by(AttendanceDispute.dispute_type).all()
        
        return jsonify({
            'success': True,
            'daily_data': {
                'labels': [d.date for d in data],
                'counts': [d.count for d in data]
            },
            'status_stats': {
                'labels': [s.status for s in status_stats],
                'counts': [s.count for s in status_stats]
            },
            'type_stats': {
                'labels': [t.dispute_type for t in type_stats],
                'counts': [t.count for t in type_stats]
            }
        })
        
    except Exception as e:
        log_error(e, current_user.id)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@my_reports_bp.route('/admin_dashboard/report_realtime_notifications')
@login_required
@admin_required
def report_realtime_notifications():
    """실시간 신고/이의제기 알림 API"""
    try:
        # 최근 1시간 내 신고/이의제기 조회
        from datetime import datetime, timedelta
        
        recent_time = datetime.utcnow() - timedelta(hours=1)
        recent_disputes = AttendanceDispute.query.filter(
            AttendanceDispute.created_at >= recent_time
        ).order_by(AttendanceDispute.created_at.desc()).limit(10).all()
        
        notifications = []
        for dispute in recent_disputes:
            notifications.append({
                'id': dispute.id,
                'type': dispute.dispute_type,
                'user_name': dispute.user.name or dispute.user.username,
                'reason': dispute.reason[:50] + '...' if len(dispute.reason) > 50 else dispute.reason,
                'status': dispute.status,
                'created_at': dispute.created_at.strftime('%H:%M'),
                'time_ago': get_time_ago(dispute.created_at)
            })
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'count': len(notifications)
        })
        
    except Exception as e:
        log_error(e, current_user.id)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_time_ago(dt):
    """시간 경과 계산"""
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