from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, make_response
from flask_login import UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, date, time
from dateutil import parser as date_parser
import os
import click
from collections import defaultdict
import io
import pandas as pd
import pdfkit
from sqlalchemy import func, case, extract, and_
from calendar import monthrange
import base64
import json

from config import config_by_name, COOKIE_SECURE
from extensions import db, migrate, login_manager, csrf, limiter, cache
from models import User, Schedule, CleaningPlan, Report, Notification, Notice, Order, Attendance, AttendanceEvaluation, AttendanceReport, ReasonTemplate, ShiftRequest, ReasonEditLog, PermissionChangeLog, UserPermission, PermissionTemplate, Team

# Import notification functions
from utils.notify import (
    send_notification_enhanced, 
    send_admin_only_notification,
    send_notification_to_role,
    send_kakao,
    send_email
)

# Import utility functions
from utils.report import generate_attendance_report_pdf
from utils.pay_transfer import transfer_salary
from utils.security import (
    password_strong, log_security_event, check_account_lockout,
    handle_failed_login, reset_login_attempts, sanitize_input,
    validate_email, validate_phone, get_client_ip, is_suspicious_request,
    admin_required
)
from utils.file_utils import cleanup_old_backups, compress_backup_files, send_backup_notification
from utils.logger import log_action, log_error

# AttendanceDispute 모델 정의
class AttendanceDispute(db.Model):
    """근태 신고/이의제기 모델"""
    __tablename__ = 'attendance_disputes'
    
    id = db.Column(db.Integer, primary_key=True)
    attendance_id = db.Column(db.Integer, db.ForeignKey('attendances.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    dispute_type = db.Column(db.String(20), nullable=False, index=True)  # 'report' (신고) or 'dispute' (이의제기)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending', index=True)  # 'pending', 'processing', 'resolved', 'rejected'
    admin_reply = db.Column(db.Text)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    attendance = db.relationship('Attendance', backref='disputes')
    user = db.relationship('User', foreign_keys=[user_id], backref='attendance_disputes')
    admin = db.relationship('User', foreign_keys=[admin_id], backref='processed_disputes')
    
    def __repr__(self):
        return f'<AttendanceDispute {self.id} - {self.dispute_type}>'

config_name = os.getenv('FLASK_ENV', 'default')

app = Flask(__name__)
app.config.from_object(config_by_name[config_name])

# Initialize extensions
csrf.init_app(app)
db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
limiter.init_app(app)
cache.init_app(app)

# Login manager setup
login_manager.login_view = 'auth.login'
login_manager.login_message = '로그인이 필요합니다.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Error Handlers ---
@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(413)
def request_entity_too_large(e):
    return render_template('errors/413.html'), 413

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

# --- Context Processor ---
@app.context_processor
def inject_notifications():
    """템플릿에서 사용할 전역 변수 주입"""
    if current_user.is_authenticated:
        unread_count = Notification.query.filter_by(
            user_id=current_user.id, 
            is_read=False
        ).count()
        return {'unread_notification_count': unread_count}
    return {'unread_notification_count': 0}

# --- Basic Routes ---
@app.route('/')
@login_required
def index():
    if current_user.is_admin():
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    from datetime import datetime, time
    import calendar

    now = datetime.utcnow()
    monthly_stats = []
    lateness_list = []
    early_leave_list = []

    STANDARD_CLOCKIN = time(9, 0, 0)
    STANDARD_CLOCKOUT = time(18, 0, 0)

    for i in range(6):
        year = (now.year if now.month - i > 0 else now.year-1)
        month = (now.month - i) if now.month - i > 0 else 12 + (now.month - i)
        # 해당 월 출근/퇴근 기록
        records = Attendance.query.filter(
            Attendance.user_id == user.id,
            db.extract('year', Attendance.clock_in) == year,
            db.extract('month', Attendance.clock_in) == month,
            Attendance.clock_out.isnot(None)
        ).all()
        work_days = len(records)
        total_seconds = sum([
            (r.clock_out - r.clock_in).total_seconds() for r in records if r.clock_out
        ])
        total_hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        wage = total_hours * 12000  # 시급 예시
        # 지각/조퇴
        lateness = sum([1 for r in records if r.clock_in and r.clock_in.time() > STANDARD_CLOCKIN])
        early_leave = sum([1 for r in records if r.clock_out and r.clock_out.time() < STANDARD_CLOCKOUT])
        lateness_list.append(lateness)
        early_leave_list.append(early_leave)
        monthly_stats.append({
            "year": year,
            "month": month,
            "work_days": work_days,
            "total_hours": total_hours,
            "minutes": minutes,
            "wage": wage,
            "lateness": lateness,
            "early_leave": early_leave,
        })
    labels = [f"{row['year']}-{row['month']:02d}" for row in monthly_stats]
    hours_list = [row['total_hours'] for row in monthly_stats]

    # 최신순 정렬
    monthly_stats = sorted(monthly_stats, key=lambda x: (x['year'], x['month']), reverse=True)

    # 최근 알림 5개
    notifications = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).limit(5).all()

    return render_template('profile.html', 
                         user=user, 
                         monthly_stats=monthly_stats,
                         labels=labels,
                         hours_list=hours_list,
                         notifications=notifications)

# --- Admin Dashboard ---
@app.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_dashboard():
    """관리자 대시보드 - 필터링 및 내보내기 기능 포함"""
    try:
        # 필터 파라미터 처리
        date_from = request.args.get('date_from', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        date_to = request.args.get('date_to', datetime.now().strftime('%Y-%m-%d'))
        team_filter = request.args.get('team', '')
        user_filter = request.args.get('user', '')
        
        # 날짜 변환
        try:
            start_date = datetime.strptime(date_from, '%Y-%m-%d')
            end_date = datetime.strptime(date_to, '%Y-%m-%d')
        except ValueError:
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now()
        
        # 기본 쿼리
        query = Attendance.query.filter(
            Attendance.clock_in >= start_date,
            Attendance.clock_in <= end_date + timedelta(days=1)
        )
        
        # 팀 필터
        if team_filter:
            query = query.join(User).filter(User.team_id == team_filter)
        
        # 사용자 필터
        if user_filter:
            query = query.filter(Attendance.user_id == user_filter)
        
        # 출결 데이터 조회
        attendances = query.order_by(Attendance.clock_in.desc()).all()
        
        # 통계 계산
        total_records = len(attendances)
        on_time_count = sum(1 for a in attendances if a.clock_in and a.clock_in.time() <= time(9, 0))
        late_count = sum(1 for a in attendances if a.clock_in and a.clock_in.time() > time(9, 0))
        absent_count = total_records - on_time_count - late_count
        
        # 팀별 통계
        team_stats = db.session.query(
            User.team_id,
            func.count(Attendance.id).label('total'),
            func.sum(case([(Attendance.clock_in <= time(9, 0), 1)], else_=0)).label('on_time'),
            func.sum(case([(Attendance.clock_in > time(9, 0), 1)], else_=0)).label('late')
        ).join(User).filter(
            Attendance.clock_in >= start_date,
            Attendance.clock_in <= end_date + timedelta(days=1)
        ).group_by(User.team_id).all()
        
        # 사용자 목록 (필터용)
        users = User.query.filter_by(status='approved').order_by(User.name).all()
        teams = Team.query.filter_by(is_active=True).order_by(Team.name).all()
        
        # 알림 통계
        notification_stats = db.session.query(
            func.date(Notification.created_at).label('date'),
            func.count(Notification.id).label('count')
        ).filter(
            Notification.created_at >= start_date,
            Notification.created_at <= end_date + timedelta(days=1)
        ).group_by(func.date(Notification.created_at)).all()
        
        return render_template('admin/admin_dashboard.html',
                             attendances=attendances,
                             total_records=total_records,
                             on_time_count=on_time_count,
                             late_count=late_count,
                             absent_count=absent_count,
                             team_stats=team_stats,
                             notification_stats=notification_stats,
                             users=users,
                             teams=teams,
                             date_from=date_from,
                             date_to=date_to,
                             team_filter=team_filter,
                             user_filter=user_filter)
    
    except Exception as e:
        flash(f'대시보드 로딩 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('index'))

# --- Chart API Routes ---
@app.route('/admin_dashboard/stats_data')
@login_required
@admin_required
def admin_dashboard_stats_data():
    """차트용 통계 데이터 API"""
    try:
        date_from = request.args.get('date_from', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        date_to = request.args.get('date_to', datetime.now().strftime('%Y-%m-%d'))
        team_filter = request.args.get('team', '')
        
        start_date = datetime.strptime(date_from, '%Y-%m-%d')
        end_date = datetime.strptime(date_to, '%Y-%m-%d')
        
        # 출결 통계
        attendance_stats = db.session.query(
            func.date(Attendance.clock_in).label('date'),
            func.count(Attendance.id).label('total'),
            func.sum(case([(Attendance.clock_in <= time(9, 0), 1)], else_=0)).label('on_time'),
            func.sum(case([(Attendance.clock_in > time(9, 0), 1)], else_=0)).label('late')
        ).filter(
            Attendance.clock_in >= start_date,
            Attendance.clock_in <= end_date + timedelta(days=1)
        ).group_by(func.date(Attendance.clock_in)).all()
        
        # 팀별 통계
        team_stats = db.session.query(
            Team.name.label('team_name'),
            func.count(Attendance.id).label('total'),
            func.sum(case([(Attendance.clock_in <= time(9, 0), 1)], else_=0)).label('on_time'),
            func.sum(case([(Attendance.clock_in > time(9, 0), 1)], else_=0)).label('late')
        ).join(User).join(Team).filter(
            Attendance.clock_in >= start_date,
            Attendance.clock_in <= end_date + timedelta(days=1)
        ).group_by(Team.name).all()
        
        # 사유별 통계
        reason_stats = db.session.query(
            Attendance.reason,
            func.count(Attendance.id).label('count')
        ).filter(
            Attendance.clock_in >= start_date,
            Attendance.clock_in <= end_date + timedelta(days=1),
            Attendance.reason.isnot(None)
        ).group_by(Attendance.reason).order_by(func.count(Attendance.id).desc()).limit(10).all()
        
        return jsonify({
            'attendance_stats': [
                {
                    'date': str(stat.date),
                    'total': stat.total,
                    'on_time': stat.on_time,
                    'late': stat.late
                } for stat in attendance_stats
            ],
            'team_stats': [
                {
                    'team_name': stat.team_name,
                    'total': stat.total,
                    'on_time': stat.on_time,
                    'late': stat.late
                } for stat in team_stats
            ],
            'reason_stats': [
                {
                    'reason': stat.reason,
                    'count': stat.count
                } for stat in reason_stats
            ]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Export Routes ---
@app.route('/admin_dashboard/excel')
@login_required
@admin_required
def admin_dashboard_excel():
    """관리자 대시보드 엑셀 내보내기"""
    try:
        date_from = request.args.get('date_from', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        date_to = request.args.get('date_to', datetime.now().strftime('%Y-%m-%d'))
        team_filter = request.args.get('team', '')
        user_filter = request.args.get('user', '')
        
        start_date = datetime.strptime(date_from, '%Y-%m-%d')
        end_date = datetime.strptime(date_to, '%Y-%m-%d')
        
        query = Attendance.query.filter(
            Attendance.clock_in >= start_date,
            Attendance.clock_in <= end_date + timedelta(days=1)
        )
        
        if team_filter:
            query = query.join(User).filter(User.team_id == team_filter)
        if user_filter:
            query = query.filter(Attendance.user_id == user_filter)
        
        attendances = query.join(User).order_by(Attendance.clock_in.desc()).all()
        
        # 엑셀 데이터 생성
        data = []
        for att in attendances:
            data.append({
                '직원명': att.user.name,
                '팀': att.user.team.name if att.user.team else '',
                '출근일': att.clock_in.strftime('%Y-%m-%d') if att.clock_in else '',
                '출근시간': att.clock_in.strftime('%H:%M:%S') if att.clock_in else '',
                '퇴근시간': att.clock_out.strftime('%H:%M:%S') if att.clock_out else '',
                '사유': att.reason or '',
                '상태': '정시' if att.clock_in and att.clock_in.time() <= time(9, 0) else '지각'
            })
        
        df = pd.DataFrame(data)
        
        # 엑셀 파일 생성
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='출결현황', index=False)
        
        output.seek(0)
        
        filename = f'admin_dashboard_{date_from}_{date_to}.xlsx'
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        flash(f'엑셀 내보내기 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin_dashboard/pdf')
@login_required
@admin_required
def admin_dashboard_pdf():
    """관리자 대시보드 PDF 내보내기"""
    try:
        date_from = request.args.get('date_from', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        date_to = request.args.get('date_to', datetime.now().strftime('%Y-%m-%d'))
        
        start_date = datetime.strptime(date_from, '%Y-%m-%d')
        end_date = datetime.strptime(date_to, '%Y-%m-%d')
        
        # 통계 데이터 조회
        total_records = Attendance.query.filter(
            Attendance.clock_in >= start_date,
            Attendance.clock_in <= end_date + timedelta(days=1)
        ).count()
        
        on_time_count = Attendance.query.filter(
            Attendance.clock_in >= start_date,
            Attendance.clock_in <= end_date + timedelta(days=1),
            Attendance.clock_in <= time(9, 0)
        ).count()
        
        late_count = Attendance.query.filter(
            Attendance.clock_in >= start_date,
            Attendance.clock_in <= end_date + timedelta(days=1),
            Attendance.clock_in > time(9, 0)
        ).count()
        
        # PDF 생성
        html_content = render_template('admin/admin_dashboard_pdf.html',
                                     date_from=date_from,
                                     date_to=date_to,
                                     total_records=total_records,
                                     on_time_count=on_time_count,
                                     late_count=late_count)
        
        pdf = pdfkit.from_string(html_content, False)
        
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=admin_dashboard_{date_from}_{date_to}.pdf'
        
        return response
    
    except Exception as e:
        flash(f'PDF 내보내기 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

# --- Other Routes ---
@app.route('/schedule', methods=['GET'])
@login_required
def schedule():
    return render_template('schedule.html')

@app.route('/clean')
@login_required
def clean():
    return render_template('clean.html')

@app.route('/notifications')
@login_required
def notifications():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('notifications.html', notifications=notifications)

@app.route('/notifications/mark_read/<int:notification_id>')
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id == current_user.id:
        notification.is_read = True
        db.session.commit()
        flash('알림을 읽음 처리했습니다.', 'success')
    return redirect(url_for('notifications'))

@app.route('/notifications/mark_all_read')
@login_required
def mark_all_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    flash('모든 알림을 읽음 처리했습니다.', 'success')
    return redirect(url_for('notifications'))

# --- CLI Commands ---
@app.cli.command('create-admin')
@click.argument('username')
@click.argument('password')
def create_admin(username, password):
    """관리자 계정 생성"""
    user = User(username=username, role='admin', status='approved')
    user.password_hash = generate_password_hash(password)
    db.session.add(user)
    db.session.commit()
    click.echo(f'관리자 계정 {username}이 생성되었습니다.')

# --- Mobile Routes ---
@app.route('/m')
@login_required
def m_dashboard():
    """모바일 대시보드"""
    try:
        # 오늘 출결 정보
        today = datetime.now().date()
        today_attendance = Attendance.query.filter(
            Attendance.user_id == current_user.id,
            func.date(Attendance.clock_in) == today
        ).first()
        
        # 최근 출결 기록 (최근 7일)
        recent_attendances = Attendance.query.filter(
            Attendance.user_id == current_user.id,
            Attendance.clock_in >= datetime.now() - timedelta(days=7)
        ).order_by(Attendance.clock_in.desc()).all()
        
        # 미읽 알림 수
        unread_count = Notification.query.filter_by(
            user_id=current_user.id, 
            is_read=False
        ).count()
        
        return render_template('mobile/m_dashboard.html',
                             today_attendance=today_attendance,
                             recent_attendances=recent_attendances,
                             unread_count=unread_count)
    
    except Exception as e:
        flash(f'모바일 대시보드 로딩 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/m/attendance', methods=['GET', 'POST'])
@login_required
def m_attendance():
    """모바일 출결 입력"""
    if request.method == 'POST':
        try:
            action = request.form.get('action')
            today = datetime.now().date()
            
            # 오늘 출결 기록 확인
            existing = Attendance.query.filter(
                Attendance.user_id == current_user.id,
                func.date(Attendance.clock_in) == today
            ).first()
            
            if action == 'clock_in':
                if existing and existing.clock_in:
                    flash('이미 출근 처리되었습니다.', 'warning')
                else:
                    if not existing:
                        existing = Attendance(user_id=current_user.id)
                        db.session.add(existing)
                    
                    existing.clock_in = datetime.now()
                    db.session.commit()
                    flash('출근이 기록되었습니다.', 'success')
            
            elif action == 'clock_out':
                if not existing or not existing.clock_in:
                    flash('먼저 출근을 기록해주세요.', 'warning')
                elif existing.clock_out:
                    flash('이미 퇴근 처리되었습니다.', 'warning')
                else:
                    existing.clock_out = datetime.now()
                    db.session.commit()
                    flash('퇴근이 기록되었습니다.', 'success')
            
            return redirect(url_for('m_attendance'))
        
        except Exception as e:
            flash(f'출결 처리 중 오류가 발생했습니다: {str(e)}', 'error')
            return redirect(url_for('m_attendance'))
    
    # GET 요청 - 출결 현황 표시
    try:
        today = datetime.now().date()
        today_attendance = Attendance.query.filter(
            Attendance.user_id == current_user.id,
            func.date(Attendance.clock_in) == today
        ).first()
        
        return render_template('mobile/m_attendance.html',
                             today_attendance=today_attendance)
    
    except Exception as e:
        flash(f'출결 정보 로딩 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('m_dashboard'))

@app.route('/m/notifications')
@login_required
def m_notifications():
    """모바일 알림 목록"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        notifications = Notification.query.filter_by(user_id=current_user.id)\
            .order_by(Notification.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return render_template('mobile/m_notifications.html',
                             notifications=notifications)
    
    except Exception as e:
        flash(f'알림 목록 로딩 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('m_dashboard'))

@app.route('/m/notification/<int:noti_id>')
@login_required
def m_notification_detail(noti_id):
    """모바일 알림 상세"""
    try:
        notification = Notification.query.get_or_404(noti_id)
        
        if notification.user_id != current_user.id:
            flash('접근 권한이 없습니다.', 'error')
            return redirect(url_for('m_notifications'))
        
        # 읽음 처리
        if not notification.is_read:
            notification.is_read = True
            db.session.commit()
        
        return render_template('mobile/m_notification_detail.html',
                             notification=notification)
    
    except Exception as e:
        flash(f'알림 상세 로딩 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('m_notifications'))

@app.route('/m/notifications/mark_read/<int:notification_id>')
@login_required
def m_mark_notification_read(notification_id):
    """모바일 알림 읽음 처리"""
    try:
        notification = Notification.query.get_or_404(notification_id)
        if notification.user_id == current_user.id:
            notification.is_read = True
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': '권한 없음'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/m/notifications/mark_all_read')
@login_required
def m_mark_all_notifications_read():
    """모바일 모든 알림 읽음 처리"""
    try:
        Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
        db.session.commit()
        flash('모든 알림을 읽음 처리했습니다.', 'success')
    except Exception as e:
        flash(f'알림 처리 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('m_notifications'))

@app.route('/m/profile')
@login_required
def m_profile():
    """모바일 프로필"""
    try:
        user = current_user
        
        # 최근 6개월 통계
        now = datetime.utcnow()
        monthly_stats = []
        
        for i in range(6):
            year = (now.year if now.month - i > 0 else now.year-1)
            month = (now.month - i) if now.month - i > 0 else 12 + (now.month - i)
            
            records = Attendance.query.filter(
                Attendance.user_id == user.id,
                db.extract('year', Attendance.clock_in) == year,
                db.extract('month', Attendance.clock_in) == month,
                Attendance.clock_out.isnot(None)
            ).all()
            
            work_days = len(records)
            total_seconds = sum([
                (r.clock_out - r.clock_in).total_seconds() for r in records if r.clock_out
            ])
            total_hours = int(total_seconds // 3600)
            
            monthly_stats.append({
                "year": year,
                "month": month,
                "work_days": work_days,
                "total_hours": total_hours
            })
        
        return render_template('mobile/m_profile.html',
                             user=user,
                             monthly_stats=monthly_stats)
    
    except Exception as e:
        flash(f'프로필 로딩 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('m_dashboard'))

@app.route('/m/stats')
@login_required
def m_stats():
    """모바일 통계"""
    try:
        # 최근 30일 통계
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        attendances = Attendance.query.filter(
            Attendance.user_id == current_user.id,
            Attendance.clock_in >= start_date,
            Attendance.clock_in <= end_date
        ).all()
        
        total_days = len(attendances)
        on_time_days = sum(1 for a in attendances if a.clock_in and a.clock_in.time() <= time(9, 0))
        late_days = sum(1 for a in attendances if a.clock_in and a.clock_in.time() > time(9, 0))
        
        # 총 근무 시간
        total_hours = 0
        for att in attendances:
            if att.clock_in and att.clock_out:
                duration = att.clock_out - att.clock_in
                total_hours += duration.total_seconds() / 3600
        
        return render_template('mobile/m_stats.html',
                             total_days=total_days,
                             on_time_days=on_time_days,
                             late_days=late_days,
                             total_hours=int(total_hours))
    
    except Exception as e:
        flash(f'통계 로딩 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('m_dashboard'))

# --- Mobile Detection ---
@app.before_request
def detect_mobile():
    """모바일 디바이스 감지"""
    user_agent = request.headers.get('User-Agent', '').lower()
    mobile_keywords = ['mobile', 'android', 'iphone', 'ipad', 'tablet']
    
    if any(keyword in user_agent for keyword in mobile_keywords):
        request.is_mobile = True
    else:
        request.is_mobile = False

# --- Utility Functions ---
def get_pending_disputes_count():
    """대기 중인 이의제기 수 조회"""
    try:
        return AttendanceDispute.query.filter_by(status='pending').count()
    except:
        return 0

@app.route('/attendance_stats')
@login_required
def attendance_stats():
    """출결 통계 페이지"""
    try:
        # 월별 통계
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        monthly_stats = db.session.query(
            func.extract('month', Attendance.clock_in).label('month'),
            func.count(Attendance.id).label('total'),
            func.sum(case([(Attendance.clock_in <= time(9, 0), 1)], else_=0)).label('on_time'),
            func.sum(case([(Attendance.clock_in > time(9, 0), 1)], else_=0)).label('late')
        ).filter(
            func.extract('year', Attendance.clock_in) == current_year
        ).group_by(func.extract('month', Attendance.clock_in)).all()
        
        return render_template('attendance_stats.html',
                             monthly_stats=monthly_stats)
    
    except Exception as e:
        flash(f'통계 로딩 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    # 개발 모드에서 실행
    app.run(debug=True, host='0.0.0.0', port=5000) 