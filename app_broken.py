from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json
import csv
import io
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import logging
from logging.handlers import RotatingFileHandler
import traceback
from werkzeug.utils import secure_filename
import zipfile
import shutil
from flask_wtf.csrf import CSRFProtect
import re
import click

from config import config_by_name
from extensions import db, migrate, login_manager, csrf, limiter, cache, init_extensions
from utils.logger import setup_logger, log_error, log_action, log_security_event, send_slack_alert_if_prod
from utils.security import check_account_lockout, increment_failed_attempts, reset_failed_attempts
from utils.decorators import owner_or_admin
from utils.slack_alert import test_slack_connection, send_event_alert
from models import User, Notice, NoticeComment, Attendance, ShiftRequest, Feedback, Suggestion, SystemLog, Schedule, CleaningPlan, Report

config_name = os.getenv('FLASK_ENV', 'default')

app = Flask(__name__)
app.config.from_object(config_by_name[config_name])

csrf.init_app(app)
init_extensions(app)
setup_logging(app)


@app.after_request
def add_security_headers(response):
    for header, value in app.config.get('SECURITY_HEADERS', {}).items():
        response.headers[header] = value
    return response

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        log_error(e)
        return None

# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    log_error(e)
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    log_error(e)
    if app.config.get('SLACK_WEBHOOK_URL'):
        send_event_alert(f"🚨 서버 500 에러 발생!\n에러: {str(e)}", "ERROR")
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden(e):
    log_error(e)
    return render_template('errors/403.html'), 403

@app.errorhandler(413)
def too_large(e):
    log_error(e)
    return render_template("errors/413.html", message="파일 용량이 너무 큽니다! (최대 10MB)"), 413

# --- Routes ---
@app.route('/', methods=['GET'])
@login_required
def index():
    if current_user.is_admin() or current_user.is_manager():
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('아이디와 비밀번호를 입력해주세요.', 'error')
            return redirect(url_for('login'))
        try:
            user = User.query.filter_by(username=username).first()
            if not user or not user.check_password(password):
                flash('아이디 또는 비밀번호가 잘못되었습니다.', 'error')
                return redirect(url_for('login'))
            if user.status != 'approved':
                flash('승인 대기 중인 계정입니다.', 'warning')
                return redirect(url_for('login'))
            login_user(user)
            flash('로그인 성공!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            log_error(e)
            flash('로그인 중 오류가 발생했습니다.', 'error')
            return redirect(url_for('login'))
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("3 per hour")
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not password:
            flash('모든 필드를 입력해주세요.', 'error')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('비밀번호가 일치하지 않습니다.', 'error')
            return redirect(url_for('register'))
        
        try:
            if User.query.filter_by(username=username).first():
                flash('이미 존재하는 아이디입니다.', 'error')
                return redirect(url_for('register'))
            
            new_user = User(username=username)
            new_user.set_password(password)
            new_user.status = 'pending'
            new_user.role = 'employee'
            
            db.session.add(new_user)
            db.session.commit()
            
            log_action(new_user.id, 'USER_REGISTERED', f'New user registration from {request.remote_addr}')
            flash('가입 신청 완료! 관리자의 승인을 기다려주세요.', 'success')
            return redirect(url_for('login'))
            
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('register'))
        except Exception as e:
            log_error(e)
            flash('회원가입 중 오류가 발생했습니다.', 'error')
            return redirect(url_for('register'))
    
    return render_template('auth/register.html')

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_password or not new_password or not confirm_password:
            flash('모든 필드를 입력해주세요.', 'error')
            return redirect(url_for('change_password'))
        
        if new_password != confirm_password:
            flash('새 비밀번호가 일치하지 않습니다.', 'error')
            return redirect(url_for('change_password'))
        
        try:
            if not current_user.check_password(current_password):
                flash("현재 비밀번호가 틀렸습니다.", 'error')
                return redirect(url_for('change_password'))
            
            current_user.set_password(new_password)
            db.session.commit()
            
            log_action(current_user.id, 'PASSWORD_CHANGED')
            flash("비밀번호가 성공적으로 변경되었습니다.", 'success')
            return redirect(url_for('dashboard'))
            
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('change_password'))
        except Exception as e:
            log_error(e)
            flash("비밀번호 변경 중 오류가 발생했습니다.", 'error')
            return redirect(url_for('change_password'))
    
    return render_template('change_password.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])
    from datetime import datetime, time
    now = datetime.utcnow()

    monthly_stats = []
    lateness_list = []
    early_leave_list = []

    STANDARD_CLOCKIN = time(9, 0, 0)
    STANDARD_CLOCKOUT = time(18, 0, 0)

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
        total_seconds = sum([(r.clock_out - r.clock_in).total_seconds() for r in records if r.clock_out])
        total_hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        wage = total_hours * 12000
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

    # 최근 알림 5개 (알림 DB가 있다면)
    # notifications = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).limit(5).all()
    notifications = []  # 예시

    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        
        try:
            current_user.name = name
            current_user.phone = phone
            current_user.email = email
            db.session.commit()
            
            log_action(current_user.id, 'PROFILE_UPDATED')
            flash("회원정보가 저장되었습니다.", 'success')
            return redirect(url_for('profile'))
            
        except Exception as e:
            log_error(e)
            flash("회원정보 저장 중 오류가 발생했습니다.", 'error')
            return redirect(url_for('profile'))

    return render_template(
        'profile.html',
        user=user,
        monthly_stats=monthly_stats,
        labels=labels,
        hours_list=hours_list,
        lateness_list=lateness_list,
        early_leave_list=early_leave_list,
        notifications=notifications
    )

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/schedule', methods=['GET'])
@login_required
def schedule():
    from_date_str = request.args.get('from', datetime.now().strftime('%Y-%m-%d'))
    to_date_str = request.args.get('to', datetime.now().strftime('%Y-%m-%d'))
    try:
        from_dt = datetime.strptime(from_date_str, '%Y-%m-%d')
        to_dt = datetime.strptime(to_date_str, '%Y-%m-%d')
    except ValueError:
        flash('날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)', 'error')
        from_dt = datetime.now()
        to_dt = datetime.now()
    if from_dt > to_dt:
        flash('시작일은 종료일보다 늦을 수 없습니다.', 'error')
        from_dt, to_dt = to_dt, from_dt
    days_diff = (to_dt - from_dt).days
    if days_diff > 90:
        flash('최대 90일까지 조회 가능합니다.', 'warning')
        to_dt = from_dt + timedelta(days=90)
    days = [(from_dt + timedelta(days=i)).date() for i in range(days_diff + 1)]
    schedules = {d: Schedule.query.filter_by(date=d).all() for d in days}
    cleanings = {d: CleaningPlan.query.filter_by(date=d).all() for d in days}
    return render_template('schedule.html',
        from_date=from_dt.strftime('%Y-%m-%d'), 
        to_date=to_dt.strftime('%Y-%m-%d'),
        dates=days, 
        schedules=schedules, 
        cleanings=cleanings
    )

@app.route('/clock_in')
@login_required
def clock_in():
    try:
        today = Attendance.query.filter_by(user_id=current_user.id)\
                               .filter(func.date(Attendance.clock_in) == date.today())\
                               .first()
        
        if today and today.clock_out is None:
            flash("이미 출근 처리되었습니다. 퇴근 버튼을 눌러주세요.", 'warning')
            return redirect(url_for('dashboard'))
        
        attendance = Attendance(user_id=current_user.id)
        db.session.add(attendance)
        db.session.commit()
        
        log_action(current_user.id, 'CLOCK_IN', f'Clock in at {attendance.clock_in}')
        flash("출근 처리 완료!", 'success')
        
    except Exception as e:
        log_error(e, current_user.id)
        flash("출근 처리 중 오류가 발생했습니다.", 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/clock_out')
@login_required
def clock_out():
    try:
        today = Attendance.query.filter_by(user_id=current_user.id)\
                               .filter(func.date(Attendance.clock_in) == date.today())\
                               .first()
        
        if not today:
            flash("출근 기록이 없습니다.", 'error')
            return redirect(url_for('dashboard'))
        
        if today.clock_out is not None:
            flash("이미 퇴근 처리되었습니다.", 'warning')
            return redirect(url_for('dashboard'))
        
        today.clock_out = datetime.utcnow()
        db.session.commit()
        
        log_action(current_user.id, 'CLOCK_OUT', f'Clock out at {today.clock_out}')
        flash("퇴근 처리 완료!", 'success')
        
    except Exception as e:
        log_error(e, current_user.id)
        flash("퇴근 처리 중 오류가 발생했습니다.", 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/attendance')
@login_required
def attendance():
    try:
        page = request.args.get('page', 1, type=int)
        records = Attendance.query.filter_by(user_id=current_user.id)\
                                 .order_by(Attendance.clock_in.desc())\
                                 .paginate(page=page, per_page=20, error_out=False)
        return render_template('attendance/my_attendance.html', records=records)
    except Exception as e:
        log_error(e, current_user.id)
        flash('출근 기록 조회 중 오류가 발생했습니다.', 'error')
        return render_template('attendance/my_attendance.html', records=None)

@app.route('/admin')
@login_required
@admin_required
@cache.cached(timeout=300)  # 5분 캐시
def admin_dashboard():
    try:
        # 기간 필터 (기본: 이번 달)
        from_dt = request.args.get("from")
        to_dt = request.args.get("to")
        today = date.today()
        
        if not from_dt:
            first = datetime(today.year, today.month, 1)
        else:
            first = datetime.strptime(from_dt, "%Y-%m-%d")
        
        if not to_dt:
            # pandas 대신 표준 라이브러리 사용
            if first.month == 12:
                last = datetime(first.year + 1, 1, 1)
            else:
                last = datetime(first.year, first.month + 1, 1)
        else:
            last = datetime.strptime(to_dt, "%Y-%m-%d") + timedelta(days=1)

        # 통계 데이터 조회
        users = User.query.filter(User.deleted_at == None, User.status == "approved").all()
        
        # 출근 통계
        attendance_stats = db.session.query(
            func.count(Attendance.id).label('total_attendance'),
            func.count(Attendance.clock_out).label('completed_attendance')
        ).filter(
            Attendance.clock_in >= first,
            Attendance.clock_in < last
        ).first()
        
        context = {
            'users': users,
            'attendance_stats': attendance_stats,
            'from_dt': from_dt,
            'to_dt': to_dt
        }
        
        return render_template('admin/dashboard.html', **context)
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('관리자 대시보드 로딩 중 오류가 발생했습니다.', 'error')
        return render_template('admin/dashboard.html')

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    from models import User
    if not (current_user.is_admin() or current_user.is_manager()):
        return redirect(url_for('dashboard'))
    users = User.query.filter_by(deleted_at=None).order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=users)

@app.route('/approve_users')
@login_required
@admin_required
def approve_users():
    users = User.query.filter(User.status != 'approved').all()
    return render_template('approve_users.html', users=users)

@app.route('/approve_user/<int:user_id>/<action>')
@login_required
@admin_required
def approve_user(user_id, action):
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

@app.route('/approve_logs')
@login_required
@admin_required
def approve_logs():
    logs = ApproveLog.query.order_by(ApproveLog.timestamp.desc()).all()
    return render_template('approve_logs.html', logs=logs)

@app.route('/admin/attendance', methods=['GET'])
@login_required
@admin_required
def admin_attendance():
    # 필터 값 읽기
    user_filter = request.args.get('user', '')
    date_filter = request.args.get('date', '')
    status_filter = request.args.get('status', '')
    
    # 페이지네이션
    page = request.args.get('page', 1, type=int)
    per_page = 30  # 페이지당 30개 레코드
    
    # 기본 쿼리
    query = Attendance.query.join(User)
    
    # 필터 적용
    if user_filter:
        query = query.filter(User.username.contains(user_filter) | User.name.contains(user_filter))
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Attendance.clock_in) == filter_date)
        except ValueError:
            pass
    
    if status_filter:
        if status_filter == 'late':
            query = query.filter(Attendance.clock_in >= datetime.combine(date.today(), time(9, 0)))
        elif status_filter == 'early_leave':
            query = query.filter(Attendance.clock_out <= datetime.combine(date.today(), time(18, 0)))
        elif status_filter == 'absent':
            query = query.filter(Attendance.clock_in.is_(None))
    
    # 정렬 및 페이지네이션
    query = query.order_by(Attendance.clock_in.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    records = pagination.items
    
    # 사용자 목록 (필터용)
    users = User.query.filter_by(status='approved').all()
    
    return render_template('admin/attendances.html', 
                         records=records, 
                         users=users,
                         pagination=pagination,
                         user_filter=user_filter,
                         date_filter=date_filter,
                         status_filter=status_filter)

@app.route('/admin/attendance/csv', methods=['GET'])
@login_required
@admin_required
def admin_attendance_csv():
    user_id = request.args.get('user_id', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    query = db.session.query(Attendance, User).join(User, Attendance.user_id == User.id)
    if user_id:
        query = query.filter(Attendance.user_id == user_id)
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d")
            query = query.filter(Attendance.clock_in >= date_from_obj)
        except:
            pass
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d")
            query = query.filter(Attendance.clock_in <= date_to_obj)
        except:
            pass

    records = query.order_by(Attendance.clock_in.desc()).all()

    def generate():
        output = StringIO()
        writer = csv.writer(output)
        
        # 헤더 작성
        writer.writerow(['직원명', '출근시간', '퇴근시간', '근무시간(분)', '상태', '위치'])
        
        # 데이터 작성
        for att, user in records:
            mins = 0
            if att.clock_in and att.clock_out:
                mins = int((att.clock_out - att.clock_in).total_seconds() // 60)
            
            row = [
                str(user.name or user.username),
                att.clock_in.strftime('%Y-%m-%d %H:%M') if att.clock_in else '-',
                att.clock_out.strftime('%Y-%m-%d %H:%M') if att.clock_out else '-',
                str(mins),
                att.status,
                att.location_in or '-'
            ]
            writer.writerow(row)
        
        output.seek(0)
        return output.getvalue()

    return Response(
        generate(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=attendance.csv"}
    )

@app.route('/admin/actionlog')
@login_required
def admin_actionlog():
    from models import User, ActionLog
    if not (current_user.is_admin() or current_user.is_manager()):
        return redirect(url_for('dashboard'))
    
    # 필터링
    user_id = request.args.get('user_id', type=int)
    action = request.args.get('action')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    query = ActionLog.query
    
    if user_id:
        query = query.filter(ActionLog.user_id == user_id)
    if action:
        query = query.filter(ActionLog.action == action)
    if from_date:
        query = query.filter(ActionLog.created_at >= datetime.strptime(from_date, '%Y-%m-%d'))
    if to_date:
        query = query.filter(ActionLog.created_at <= datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1))
    
    logs = query.order_by(ActionLog.created_at.desc()).all()
    users = User.query.filter_by(deleted_at=None).all()
    
    return render_template('admin_actionlog.html', logs=logs, users=users)

@app.route('/admin/approve_stats')
@login_required
def approve_stats():
    from models import User, ApproveLog
    if not (current_user.is_admin() or current_user.is_manager()):
        return redirect(url_for('dashboard'))
    
    # 승인/거절 통계
    total_approved = ApproveLog.query.filter_by(action='approved').count()
    total_rejected = ApproveLog.query.filter_by(action='rejected').count()
    
    # 담당자별 통계
    approver_stats = db.session.query(
        User.username,
        db.func.count(ApproveLog.id).label('total_count'),
        db.func.sum(db.case([(ApproveLog.action == 'approved', 1)], else_=0)).label('approved_count'),
        db.func.sum(db.case([(ApproveLog.action == 'rejected', 1)], else_=0)).label('rejected_count')
    ).join(ApproveLog, User.id == ApproveLog.approver_id).group_by(User.id, User.username).all()
    
    # 월별 통계
    monthly_stats = db.session.query(
        db.func.strftime('%Y-%m', ApproveLog.timestamp).label('month'),
        db.func.count(ApproveLog.id).label('total_count'),
        db.func.sum(db.case([(ApproveLog.action == 'approved', 1)], else_=0)).label('approved_count'),
        db.func.sum(db.case([(ApproveLog.action == 'rejected', 1)], else_=0)).label('rejected_count')
    ).group_by(db.func.strftime('%Y-%m', ApproveLog.timestamp)).order_by('month').all()
    
    return render_template('approve_stats.html', 
                         total_approved=total_approved,
                         total_rejected=total_rejected,
                         approver_stats=approver_stats,
                         monthly_stats=monthly_stats)

@app.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    from models import Feedback
    if request.method == 'POST':
        satisfaction = request.form.get('satisfaction', type=int)
        health = request.form.get('health', type=int)
        comment = request.form.get('comment', '')
        
        feedback = Feedback(user_id=current_user.id, satisfaction=satisfaction, health=health, comment=comment)
        db.session.add(feedback)
        db.session.commit()
        
        flash("피드백 제출 완료", "success")
        return redirect(url_for('dashboard'))
    
    return render_template('feedback.html')

@app.route('/admin/feedback')
@login_required
def admin_feedback():
    from models import User, Feedback
    if not (current_user.is_admin() or current_user.is_manager()):
        return redirect(url_for('dashboard'))
    
    feedbacks = Feedback.query.join(User).filter(User.deleted_at == None).order_by(Feedback.created_at.desc()).all()
    return render_template('admin_feedback.html', feedbacks=feedbacks)

@app.route('/api/my/attendances')
@login_required
def api_my_attendances():
    from models import Attendance
    attendances = Attendance.query.filter_by(user_id=current_user.id).order_by(Attendance.clock_in.desc()).limit(10).all()
    data = []
    for att in attendances:
        data.append({
            'id': att.id,
            'clock_in': att.clock_in.strftime('%Y-%m-%d %H:%M:%S') if att.clock_in else None,
            'clock_out': att.clock_out.strftime('%Y-%m-%d %H:%M:%S') if att.clock_out else None,
            'work_minutes': att.work_minutes,
            'status': att.status
        })
    return jsonify(data)

@app.route('/admin/attendance/stats/csv', methods=['GET'])
@login_required
@admin_required
def admin_attendance_stats_csv():
    year = request.args.get('year', type=int) or datetime.utcnow().year
    month = request.args.get('month', type=int)
    user_id = request.args.get('user_id', type=int)
    wage_per_hour = request.args.get('wage', type=int) or 12000  # 기본 시급

    # 집계 쿼리 (집계와 동일)
    base_query = db.session.query(
        Attendance.user_id,
        func.count(Attendance.id).label('days'),
        func.sum(
            func.strftime('%s', Attendance.clock_out) - func.strftime('%s', Attendance.clock_in)
        ).label('total_seconds')
    ).group_by(Attendance.user_id)

    if month:
        base_query = base_query.filter(extract('year', Attendance.clock_in) == year)
        base_query = base_query.filter(extract('month', Attendance.clock_in) == month)
    else:
        base_query = base_query.filter(extract('year', Attendance.clock_in) == year)
    if user_id:
        base_query = base_query.filter(Attendance.user_id == user_id)

    stats = base_query.all()

    def generate():
        header = '직원,근무일수,총근무시간(시간),총급여(원)\n'
        yield header
        for user_id, days, total_seconds in stats:
            user = User.query.get(user_id)
            total_hours = int((total_seconds or 0) // 3600)
            minutes = int(((total_seconds or 0) % 3600) // 60)
            work_time = total_hours + minutes/60
            wage = int(work_time * wage_per_hour)
            row = [
                str(user.name or user.username),
                str(days),
                f"{total_hours}시간 {minutes}분",
                str(wage)
            ]
            yield ','.join(row) + '\n'
    return Response(
        generate(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=attendance_stats.csv"}
    )

@app.route('/admin/attendance/stats', methods=['GET'])
@login_required
@admin_required
def attendance_stats():
    from sqlalchemy import extract, func
    
    year = request.args.get('year', type=int) or datetime.utcnow().year
    month = request.args.get('month', type=int)
    user_id = request.args.get('user_id', type=int)
    
    # 집계 쿼리
    base_query = db.session.query(
        Attendance.user_id,
        func.count(Attendance.id).label('days'),
        func.sum(
            func.strftime('%s', Attendance.clock_out) - func.strftime('%s', Attendance.clock_in)
        ).label('total_seconds')
    ).group_by(Attendance.user_id)

    if month:
        base_query = base_query.filter(extract('year', Attendance.clock_in) == year)
        base_query = base_query.filter(extract('month', Attendance.clock_in) == month)
    else:
        base_query = base_query.filter(extract('year', Attendance.clock_in) == year)
    if user_id:
        base_query = base_query.filter(Attendance.user_id == user_id)

    stats = base_query.all()
    
    # 통계 데이터 가공
    stats_data = []
    for user_id, days, total_seconds in stats:
        user = User.query.get(user_id)
        if user:
            total_hours = int((total_seconds or 0) // 3600)
            minutes = int(((total_seconds or 0) % 3600) // 60)
            work_time = total_hours + minutes/60
            
            stats_data.append({
                'user': user,
                'days': days,
                'total_hours': total_hours,
                'total_minutes': minutes,
                'work_time': work_time,
                'work_time_formatted': f"{total_hours}시간 {minutes}분"
            })
    
    # 직원 목록 (필터용)
    employees = User.query.filter(User.deleted_at == None, User.status == "approved").order_by(User.username).all()
    
    return render_template(
        'admin/attendance_stats.html',
        stats_data=stats_data,
        employees=employees,
        year=year,
        month=month,
        user_id=user_id
    )

@app.route('/admin/payroll_pdf/<int:user_id>')
@login_required
@admin_required
def payroll_pdf(user_id):
    user = User.query.get_or_404(user_id)
    
    # 현재 월 정보 (실제로는 쿼리스트링으로 월/년도 지정 가능)
    now = datetime.utcnow()
    month = request.args.get('month', type=int) or now.month
    year = request.args.get('year', type=int) or now.year
    
    # 근무 통계 조회
    work_days = Attendance.query.filter(
        Attendance.user_id == user_id,
        extract('year', Attendance.clock_in) == year,
        extract('month', Attendance.clock_in) == month,
        Attendance.clock_out.isnot(None)
    ).count()
    
    total_seconds = db.session.query(
        func.sum(func.strftime('%s', Attendance.clock_out) - func.strftime('%s', Attendance.clock_in))
    ).filter(
        Attendance.user_id == user_id,
        extract('year', Attendance.clock_in) == year,
        extract('month', Attendance.clock_in) == month,
        Attendance.clock_out.isnot(None)
    ).scalar() or 0
    
    total_hours = int(total_seconds // 3600)
    wage = total_hours * 12000  # 기본 시급
    
    # 지각/조퇴/야근 통계
    attendances = Attendance.query.filter(
        Attendance.user_id == user_id,
        extract('year', Attendance.clock_in) == year,
        extract('month', Attendance.clock_in) == month
    ).all()
    
    late_count = 0
    early_leave_count = 0
    overtime_hours = 0
    
    for att in attendances:
        if att.clock_in and att.clock_out:
            if att.clock_in.time() > time(9, 0):
                late_count += 1
            if att.clock_out.time() < time(18, 0):
                early_leave_count += 1
            if att.clock_out.time() > time(18, 0):
                overtime_hours += (att.clock_out - att.clock_in).total_seconds() / 3600 - 8
    
    # static 폴더가 없으면 생성
    if not os.path.exists('static'):
        os.makedirs('static')
    
    filename = f"payroll_{user.username}_{year}_{month:02d}.pdf"
    filepath = os.path.join('static', filename)
    
    generate_payroll_pdf(filepath, user, month, year, work_days, total_hours, wage, 
                        late_count, early_leave_count, overtime_hours)
    
    return redirect(url_for('static', filename=filename))

@app.route('/admin/user_stats/<int:user_id>')
@login_required
@admin_required
def user_stats(user_id):
    user = User.query.get_or_404(user_id)
    year = request.args.get('year', type=int) or datetime.utcnow().year
    
    labels, monthly_hours = get_user_monthly_trend(user_id, year, db.session)
    
    return render_template('admin/user_stats.html', 
                         user=user, 
                         labels=labels, 
                         monthly_hours=monthly_hours,
                         year=year)

@app.route('/admin/bulk_payroll')
@login_required
@admin_required
def bulk_payroll():
    now = datetime.utcnow()
    year = request.args.get('year', type=int) or now.year
    month = request.args.get('month', type=int) or now.month
    
    users = User.query.filter(User.deleted_at == None, User.status == "approved").all()
    pdf_links = []
    
    # static 폴더가 없으면 생성
    if not os.path.exists('static'):
        os.makedirs('static')
    
    for user in users:
        # 근무 통계 조회
        work_days = Attendance.query.filter(
            Attendance.user_id == user.id,
            extract('year', Attendance.clock_in) == year,
            extract('month', Attendance.clock_in) == month,
            Attendance.clock_out.isnot(None)
        ).count()
        
        total_seconds = db.session.query(
            func.sum(func.strftime('%s', Attendance.clock_out) - func.strftime('%s', Attendance.clock_in))
        ).filter(
            Attendance.user_id == user.id,
            extract('year', Attendance.clock_in) == year,
            extract('month', Attendance.clock_in) == month,
            Attendance.clock_out.isnot(None)
        ).scalar() or 0
        
        total_hours = int(total_seconds // 3600)
        wage = total_hours * 12000
        
        # 지각/조퇴/야근 통계
        attendances = Attendance.query.filter(
            Attendance.user_id == user.id,
            extract('year', Attendance.clock_in) == year,
            extract('month', Attendance.clock_in) == month
        ).all()
        
        late_count = 0
        early_leave_count = 0
        overtime_hours = 0
        
        for att in attendances:
            if att.clock_in and att.clock_out:
                if att.clock_in.time() > time(9, 0):
                    late_count += 1
                if att.clock_out.time() < time(18, 0):
                    early_leave_count += 1
                if att.clock_out.time() > time(18, 0):
                    overtime_hours += (att.clock_out - att.clock_in).total_seconds() / 3600 - 8
        
        filename = f"payroll_{user.username}_{year}_{month:02d}.pdf"
        filepath = os.path.join('static', filename)
        
        generate_payroll_pdf(filepath, user, month, year, work_days, total_hours, wage,
                            late_count, early_leave_count, overtime_hours)
        
        pdf_links.append({
            'filename': filename,
            'username': user.name or user.username,
            'work_days': work_days,
            'total_hours': total_hours,
            'wage': wage
        })
    
    return render_template('admin/bulk_payroll.html', 
                         pdf_links=pdf_links, 
                         year=year, 
                         month=month)

@app.cli.command('create-sample-data')
def create_sample_data():
    """샘플 데이터 생성"""
    from utils.sample_data import create_sample_data
    create_sample_data()
    print("샘플 데이터가 생성되었습니다.")

@app.cli.command('cleanup-logs')
def cleanup_logs():
    """오래된 로그 파일 정리"""
    from utils.logger import cleanup_logs_command
    cleanup_logs_command()

@app.cli.command('show-log-stats')
def show_log_stats():
    """로그 파일 통계 보기"""
    from utils.logger import show_log_stats_command
    show_log_stats_command()

@app.cli.command('rotate-logs')
def rotate_logs():
    """로그 파일 수동 로테이션"""
    from utils.logger import rotate_logs_manually
    if rotate_logs_manually():
        print("로그 로테이션이 완료되었습니다.")
    else:
        print("로그 로테이션에 실패했습니다.")

@app.cli.command('security-check')
def security_check():
    """보안 설정 점검"""
    from utils.security import validate_password_strength
    import secrets
    
    print("=== 보안 설정 점검 ===")
    
    # 비밀번호 강도 테스트
    test_passwords = [
        "weak",
        "password123",
        "StrongPass1!",
        "VeryStrongPassword123!@#"
    ]
    
    print("\n1. 비밀번호 강도 검증:")
    for pwd in test_passwords:
        is_valid, message = validate_password_strength(pwd)
        status = "✅" if is_valid else "❌"
        print(f"   {status} '{pwd}': {message}")
    
    # 환경변수 점검
    print("\n2. 환경변수 점검:")
    required_vars = ['SECRET_KEY', 'CSRF_SECRET_KEY']
    for var in required_vars:
        value = os.environ.get(var)
        if value and value != 'your-super-secret-key-here-change-this':
            print(f"   ✅ {var}: 설정됨")
        else:
            print(f"   ❌ {var}: 설정되지 않음 또는 기본값")
    
    # 데이터베이스 연결 점검
    print("\n3. 데이터베이스 연결:")
    try:
        with app.app_context():
            db.engine.execute("SELECT 1")
            print("   ✅ 데이터베이스 연결 성공")
    except Exception as e:
        print(f"   ❌ 데이터베이스 연결 실패: {e}")
    
    print("\n보안 점검이 완료되었습니다.")

@app.cli.command('test-slack')
def test_slack():
    """Slack 연결 테스트"""
    if test_slack_connection():
        print("Slack 연결 성공!")
        send_event_alert("Slack 연결 테스트 메시지입니다.")
    else:
        print("Slack 연결 실패. 설정을 확인하세요.")

@app.cli.command('create-admin')
@click.argument('username')
@click.argument('password')
def create_admin(username, password):
    """Provides a password argument to create an admin user."""
    if User.query.filter_by(username=username).first():
        print(f"User {username} already exists.")
        return
    
    user = User(username=username, email=f'{username}@example.com', is_admin=True, status='approved')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print(f"Admin user {username} created successfully.")

@app.cli.command('reset-password')
@click.argument('username')
def reset_password():
    """사용자 비밀번호 재설정"""
    username = input("사용자명: ").strip()
    if not username:
        print("사용자명을 입력해주세요.")
        return
    
    user = User.query.filter_by(username=username).first()
    if not user:
        print("존재하지 않는 사용자입니다.")
        return
    
    new_password = input("새 비밀번호: ").strip()
    if not new_password:
        print("새 비밀번호를 입력해주세요.")
        return
    
    # 비밀번호 강도 검증
    from utils.security import validate_password_strength
    is_valid, message = validate_password_strength(new_password)
    if not is_valid:
        print(f"비밀번호 오류: {message}")
        return
    
    try:
        user.set_password(new_password)
        user.login_attempts = 0
        user.locked_until = None
        db.session.commit()
        
        print(f"✅ 사용자 '{username}'의 비밀번호가 성공적으로 재설정되었습니다.")
        
    except Exception as e:
        print(f"❌ 비밀번호 재설정 실패: {e}")
        db.session.rollback()

@app.cli.command('lock-user')
def lock_user():
    """사용자 계정 잠금"""
    username = input("사용자명: ").strip()
    if not username:
        print("사용자명을 입력해주세요.")
        return
    
    user = User.query.filter_by(username=username).first()
    if not user:
        print("존재하지 않는 사용자입니다.")
        return
    
    try:
        from datetime import timedelta
        user.locked_until = datetime.utcnow() + timedelta(days=30)  # 30일 잠금
        db.session.commit()
        
        print(f"✅ 사용자 '{username}'의 계정이 30일간 잠겼습니다.")
        
    except Exception as e:
        print(f"❌ 계정 잠금 실패: {e}")
        db.session.rollback()

@app.cli.command('unlock-user')
def unlock_user():
    """사용자 계정 잠금 해제"""
    username = input("사용자명: ").strip()
    if not username:
        print("사용자명을 입력해주세요.")
        return
    
    user = User.query.filter_by(username=username).first()
    if not user:
        print("존재하지 않는 사용자입니다.")
        return
    
    try:
        user.locked_until = None
        user.login_attempts = 0
        db.session.commit()
        
        print(f"✅ 사용자 '{username}'의 계정 잠금이 해제되었습니다.")
        
    except Exception as e:
        print(f"❌ 계정 잠금 해제 실패: {e}")
        db.session.rollback()

@app.route('/admin/attendance_report_pdf/<int:user_id>')
@login_required
@admin_required
def attendance_report_pdf(user_id):
    """개별 직원 근태 리포트 PDF 생성"""
    try:
        import os
        from datetime import datetime, time
        from utils.report import generate_attendance_report_pdf
        
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
        ).order_by(Attendance.clock_in).all()

        # 통계 계산
        lateness = early_leave = night_work = 0
        for att in attendances:
            if att.clock_in and att.clock_in.time() > STANDARD_CLOCKIN:
                lateness += 1
            if att.clock_out and att.clock_out.time() < STANDARD_CLOCKOUT:
                early_leave += 1
            if att.clock_out and att.clock_out.time() > NIGHT_WORK_START:
                night_work += 1

        # PDF 파일 생성
        filename = f"attendance_report_{user.username}_{year}_{month}.pdf"
        filepath = os.path.join('static', 'reports', filename)
        
        # reports 디렉토리 생성
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        generate_attendance_report_pdf(filepath, user, month, year, lateness, early_leave, night_work, attendances)
        
        log_action(current_user.id, 'PDF_REPORT_GENERATED', f'Generated attendance report for {user.username}')
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('PDF 생성 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/monthly_summary_pdf')
@login_required
@admin_required
def monthly_summary_pdf():
    """월별 전체 직원 근태 요약 PDF"""
    try:
        import os
        from datetime import datetime, time
        from utils.report import generate_monthly_summary_pdf
        
        now = datetime.utcnow()
        year, month = now.year, now.month

        STANDARD_CLOCKIN = time(9, 0, 0)
        STANDARD_CLOCKOUT = time(18, 0, 0)
        NIGHT_WORK_START = time(21, 0, 0)

        users_data = []
        users = User.query.filter_by(status='approved').all()

        for user in users:
            attendances = Attendance.query.filter(
                Attendance.user_id == user.id,
                extract('year', Attendance.clock_in) == year,
                extract('month', Attendance.clock_in) == month,
                Attendance.clock_out.isnot(None)
            ).all()

            lateness = early_leave = night_work = 0
            total_hours = 0

            for att in attendances:
                if att.clock_in and att.clock_in.time() > STANDARD_CLOCKIN:
                    lateness += 1
                if att.clock_out and att.clock_out.time() < STANDARD_CLOCKOUT:
                    early_leave += 1
                if att.clock_out and att.clock_out.time() > NIGHT_WORK_START:
                    night_work += 1
                total_hours += att.work_hours

            users_data.append({
                'user': user,
                'lateness': lateness,
                'early_leave': early_leave,
                'night_work': night_work,
                'total_hours': total_hours
            })

        # PDF 파일 생성
        filename = f"monthly_summary_{year}_{month}.pdf"
        filepath = os.path.join('static', 'reports', filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        generate_monthly_summary_pdf(filepath, users_data, month, year)
        
        log_action(current_user.id, 'PDF_SUMMARY_GENERATED', f'Generated monthly summary for {year}/{month}')
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('PDF 생성 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/individual_transfer/<int:user_id>')
@login_required
@admin_required
def individual_transfer(user_id):
    """개별 급여 이체"""
    try:
        from utils.pay_transfer import transfer_salary, validate_bank_account
        from utils.notify import notify_salary_payment
        
        user = User.query.get_or_404(user_id)
        year, month = datetime.utcnow().year, datetime.utcnow().month
        
        # 해당 월 근무시간 계산
        total_seconds = db.session.query(
            func.sum(func.strftime('%s', Attendance.clock_out) - func.strftime('%s', Attendance.clock_in))
        ).filter(
            Attendance.user_id == user.id,
            extract('year', Attendance.clock_in) == year,
            extract('month', Attendance.clock_in) == month,
            Attendance.clock_out.isnot(None)
        ).scalar() or 0
        
        total_hours = int(total_seconds // 3600)
        wage = total_hours * 12000
        
        # 계좌 정보 검증
        is_valid, error_msg = validate_bank_account(user)
        if not is_valid:
            flash(f'계좌 정보 오류: {error_msg}', 'error')
            return redirect(url_for('admin_users'))
        
        # 급여 이체 실행
        success, message = transfer_salary(user, wage, f"{year}년 {month}월 급여")
        
        if success:
            notify_salary_payment(user, wage, year, month)
            flash(f'{user.name or user.username}님 급여 {wage:,}원 이체 완료!', 'success')
        else:
            flash(f'급여 이체 실패: {message}', 'error')
        
        log_action(current_user.id, 'INDIVIDUAL_TRANSFER', f'Transferred {wage:,} won to {user.username}')
        
        return redirect(url_for('admin_users'))
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('급여 이체 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_users'))

@app.route('/admin/bulk_transfer')
@login_required
@admin_required
def bulk_transfer():
    """일괄 급여 이체 실행"""
    try:
        year, month = datetime.utcnow().year, datetime.utcnow().month
        users = User.query.filter_by(status='approved').all()
        
        transfer_results = []
        
        for user in users:
            # 해당 월 근무시간 계산
            total_seconds = db.session.query(
                func.sum(func.strftime('%s', Attendance.clock_out) - func.strftime('%s', Attendance.clock_in))
            ).filter(
                Attendance.user_id == user.id,
                extract('year', Attendance.clock_in) == year,
                extract('month', Attendance.clock_in) == month,
                Attendance.clock_out.isnot(None)
            ).scalar() or 0
            
            total_hours = int(total_seconds // 3600)
            wage = total_hours * 12000  # 시간당 12,000원
            
            # 계좌 정보 검증
            is_valid, error_msg = validate_bank_account(user)
            if not is_valid:
                transfer_results.append({
                    'user_id': user.id,
                    'user_name': user.name or user.username,
                    'amount': wage,
                    'success': False,
                    'message': error_msg
                })
                continue
            
            # 급여 이체 실행
            success, message = transfer_salary(user, wage, f"{year}년 {month}월 급여")
            
            transfer_results.append({
                'user_id': user.id,
                'user_name': user.name or user.username,
                'amount': wage,
                'success': success,
                'message': message
            })
            
            # 성공 시 알림 발송
            if success:
                notify_salary_payment(user, wage, year, month)
        
        # 결과 요약
        success_count = sum(1 for r in transfer_results if r['success'])
        total_count = len(transfer_results)
        
        log_action(current_user.id, 'BULK_TRANSFER_EXECUTED', f'Transferred salary for {success_count}/{total_count} users')
        
        flash(f'일괄 급여 이체 완료! 성공: {success_count}명, 실패: {total_count - success_count}명', 'success')
        
        return redirect(url_for('admin_dashboard'))
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('급여 이체 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/transfer_history')
@login_required
@admin_required
def transfer_history():
    """이체 이력 조회"""
    try:
        from utils.pay_transfer import get_transfer_history
        
        # 최근 이체 이력 조회
        recent_transfers = ActionLog.query.filter(
            ActionLog.action.like('SALARY_TRANSFER_%')
        ).order_by(ActionLog.created_at.desc()).limit(50).all()
        
        return render_template('admin/transfer_history.html', transfers=recent_transfers)
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('이체 이력 조회 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/send_notification', methods=['GET', 'POST'])
@login_required
@admin_required
def send_notification():
    """관리자 알림 발송"""
    if request.method == 'POST':
        try:
            notification_type = request.form.get('notification_type', 'email')
            message = request.form.get('message', '')
            user_ids = request.form.getlist('user_ids')
            
            if not message:
                flash('알림 내용을 입력해주세요.', 'error')
                return redirect(url_for('send_notification'))
            
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
            return redirect(url_for('send_notification'))
    
    # GET 요청: 알림 발송 페이지
    users = User.query.filter_by(status='approved').all()
    return render_template('admin/send_notification.html', users=users)

@app.route('/shift_request', methods=['GET', 'POST'])
@login_required
def shift_request():
    from datetime import datetime
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        desired_date = request.form['desired_date']
        reason = request.form['reason']
        new_req = ShiftRequest(
            user_id=user.id,
            request_date=datetime.utcnow().date(),
            desired_date=desired_date,
            reason=reason,
            status='pending'
        )
        db.session.add(new_req)
        
        # 신청 접수 알림 저장
        notification = Notification(
            user_id=user.id,
            message=f"{desired_date} 근무 변경 신청이 접수되었습니다."
        )
        db.session.add(notification)
        
        db.session.commit()
        
        # 관리자에게 알림 전송 (관리자 계정이 있다면)
        from utils.notify import send_notification
        admin_users = User.query.filter_by(role='admin').all()
        for admin in admin_users:
            send_notification(admin, f"{user.name or user.username}님이 {desired_date} 근무 변경을 신청했습니다.")
        
        flash("교대/근무 변경 신청이 접수되었습니다!")
        return redirect(url_for('shift_request'))
    requests = ShiftRequest.query.filter_by(user_id=user.id).order_by(ShiftRequest.created_at.desc()).all()
    return render_template('shift_request.html', requests=requests)

@app.route('/admin/shift_requests')
@login_required
@admin_required
def admin_shift_requests():
    """관리자: 근무 변경 신청 관리"""
    try:
        requests = ShiftRequest.query.order_by(ShiftRequest.created_at.desc()).all()
        return render_template('admin/shift_requests.html', requests=requests)
    except Exception as e:
        log_error(e, current_user.id)
        flash('근무 변경 신청 조회 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/shift_request_action/<int:request_id>/<action>')
@login_required
@admin_required
def shift_request_action(request_id, action):
    """관리자: 근무 변경 신청 승인/거절"""
    try:
        req = ShiftRequest.query.get_or_404(request_id)
        
        if action == 'approve':
            req.status = 'approved'
            message = f"{req.desired_date.strftime('%Y-%m-%d')} 근무 변경이 승인되었습니다."
            log_action(current_user.id, 'SHIFT_REQUEST_APPROVED', f'Approved shift request {request_id}')
            
        elif action == 'reject':
            req.status = 'rejected'
            message = f"{req.desired_date.strftime('%Y-%m-%d')} 근무 변경이 거절되었습니다."
            log_action(current_user.id, 'SHIFT_REQUEST_REJECTED', f'Rejected shift request {request_id}')
        
        else:
            flash('잘못된 요청입니다.', 'error')
            return redirect(url_for('admin_shift_requests'))
        
        # 알림 전송
        from utils.notify import send_notification
        send_notification(req.user, message)
        
        # 알림 DB 저장
        notification = Notification(
            user_id=req.user_id,
            message=message
        )
        db.session.add(notification)
        db.session.commit()
        
        flash("처리가 완료되었습니다.", 'success')
        return redirect(url_for('admin_shift_requests'))
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('처리 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_shift_requests'))

@app.route('/calendar')
@login_required
def calendar():
    """내 근무 스케줄 캘린더"""
    try:
        user = User.query.get(session['user_id'])
        
        # 출근 기록
        records = Attendance.query.filter_by(user_id=user.id).all()
        # 승인된 근무 변경 신청
        shift_reqs = ShiftRequest.query.filter_by(user_id=user.id, status='approved').all()
        
        events = []
        
        # 출근 일정 추가
        for rec in records:
            events.append({
                "title": "출근",
                "start": rec.clock_in.strftime('%Y-%m-%d'),
                "color": "#00aaff"
            })
        
        # 승인된 근무 변경 일정 추가
        for req in shift_reqs:
            events.append({
                "title": "근무변경(승인)",
                "start": req.desired_date.strftime('%Y-%m-%d'),
                "color": "#ffbb00"
            })
        
        return render_template('calendar.html', events=events)
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('캘린더 로딩 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/admin/notifications')
@login_required
@admin_required
def admin_notifications():
    """관리자: 알림센터"""
    try:
        notis = Notification.query.order_by(Notification.created_at.desc()).limit(100).all()
        return render_template('admin/notifications.html', notis=notis)
    except Exception as e:
        log_error(e, current_user.id)
        flash('알림 조회 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_dashboard'))

def save_notice_history(notice, editor_id, action='edit'):
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
            ip_address=request.remote_addr
        )
        db.session.add(hist)
        db.session.commit()
        log_action(editor_id, 'NOTICE_HISTORY_SAVED', f'Saved history for notice {notice.id}, action: {action}')
    except Exception as e:
        log_error(e, editor_id)
        db.session.rollback()

def save_comment_history(comment, editor_id, action='edit'):
    """댓글 변경이력 저장"""
    try:
        hist = CommentHistory(
            comment_id=comment.id,
            editor_id=editor_id,
            before_content=comment.content,
            action=action,
            ip_address=request.remote_addr
        )
        db.session.add(hist)
        db.session.commit()
        log_action(editor_id, 'COMMENT_HISTORY_SAVED', f'Saved history for comment {comment.id}, action: {action}')
    except Exception as e:
        log_error(e, editor_id)
        db.session.rollback()

@app.route('/notice/new', methods=['GET', 'POST'])
@login_required
@admin_required
def notice_new():
    """공지사항 등록 (개선된 파일 업로드)"""
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            category = request.form.get('category', '').strip()
            
            if not title or not content:
                flash('제목과 내용을 입력해주세요.', 'error')
                return render_template('notice_new.html')
            
            file_path = None
            file_type = None
            
            # 파일 업로드 처리
            file = request.files.get('file')
            if file and file.filename:
                try:
                    file_path, file_type = save_uploaded_file(file)
                except ValueError as e:
                    flash(str(e), 'error')
                    return render_template('notice_new.html')
            
            notice = Notice(
                title=title, 
                content=content, 
                file_path=file_path, 
                file_type=file_type,
                category=category, 
                author_id=current_user.id
            )
            db.session.add(notice)
            db.session.commit()
            
            save_notice_history(notice, current_user.id, 'create')
            log_action_consistency(current_user.id, 'NOTICE_CREATED', 
                                 f'Created notice: {title}', 
                                 request.remote_addr)
            flash("공지사항이 등록되었습니다!", 'success')
            return redirect(url_for('notices'))
            
        except Exception as e:
            log_error(e, current_user.id)
            flash("공지사항 등록 중 오류가 발생했습니다.", 'error')
            return redirect(url_for('notice_new'))
    
    return render_template('notice_new.html')

@app.route('/notice/edit/<int:notice_id>', methods=['GET', 'POST'])
@owner_or_admin(lambda notice_id: Notice.query.get_or_404(notice_id))
def notice_edit(notice_id):
    """공지사항 수정"""
    notice = Notice.query.get_or_404(notice_id)
    
    if request.method == 'POST':
        try:
            # 변경이력 저장
            save_notice_history(notice, current_user.id, 'edit')
            
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            category = request.form.get('category', '').strip()
            
            if not title or not content:
                flash('제목과 내용을 입력해주세요.', 'error')
                return render_template('notice_edit.html', notice=notice)
            
            # 기존 파일 정보 저장
            old_file_path = notice.file_path
            old_file_type = notice.file_type
            
            # 새 파일 업로드 처리
            file = request.files.get('file')
            if file and file.filename:
                try:
                    file_path, file_type = save_uploaded_file(file)
                    # 기존 파일 삭제
                    if old_file_path:
                        safe_remove(os.path.join('static', old_file_path))
                    notice.file_path = file_path
                    notice.file_type = file_type
                except ValueError as e:
                    flash(str(e), 'error')
                    return render_template('notice_edit.html', notice=notice)
            
            notice.title = title
            notice.content = content
            notice.category = category
            db.session.commit()
            
            log_action_consistency(current_user.id, 'NOTICE_EDITED', 
                                 f'Edited notice: {title}', 
                                 request.remote_addr)
            flash("공지사항이 수정되었습니다!", 'success')
            return redirect(url_for('notice_view', notice_id=notice_id))
            
        except Exception as e:
            log_error(e, current_user.id)
            flash("공지사항 수정 중 오류가 발생했습니다.", 'error')
            return redirect(url_for('notice_edit', notice_id=notice_id))
    
    return render_template('notice_edit.html', notice=notice)

@app.route('/notice/hide/<int:notice_id>', methods=['POST'])
@owner_or_admin(lambda notice_id: Notice.query.get_or_404(notice_id))
def notice_hide(notice_id):
    """공지사항 숨김 처리"""
    try:
        notice = Notice.query.get_or_404(notice_id)
        
        if notice.is_hidden:
            flash("이미 숨김 처리된 공지사항입니다.", 'warning')
            return redirect(url_for('notice_view', notice_id=notice_id))
        
        # 변경이력 저장
        save_notice_history(notice, current_user.id, 'hide')
        
        notice.is_hidden = True
        db.session.commit()
        
        log_action_consistency(current_user.id, 'NOTICE_HIDDEN', 
                             f'Hidden notice: {notice.title}', 
                             request.remote_addr)
        flash("공지사항이 숨김 처리되었습니다.", 'success')
        return redirect(url_for('notices'))
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('공지사항 숨김 처리 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('notice_view', notice_id=notice_id))

@app.route('/notice/unhide/<int:notice_id>', methods=['POST'])
@login_required
@admin_required
def notice_unhide(notice_id):
    """공지사항 숨김 해제"""
    try:
        notice = Notice.query.get_or_404(notice_id)
        
        if not notice.is_hidden:
            flash("숨김 처리되지 않은 공지사항입니다.", 'warning')
            return redirect(url_for('notice_view', notice_id=notice_id))
        
        # 변경이력 저장
        save_notice_history(notice, current_user.id, 'unhide')
        
        notice.is_hidden = False
        db.session.commit()
        
        log_action_consistency(current_user.id, 'NOTICE_UNHIDDEN', 
                             f'Unhidden notice: {notice.title}', 
                             request.remote_addr)
        flash("숨김 해제 완료", 'success')
        return redirect(url_for('admin_hidden_notices'))
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('공지사항 숨김 해제 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('notice_view', notice_id=notice_id))

@app.route('/notice/comment/delete/<int:comment_id>', methods=['POST'])
@owner_or_admin(lambda comment_id: NoticeComment.query.get_or_404(comment_id))
def comment_delete(comment_id):
    """댓글 삭제"""
    try:
        comment = NoticeComment.query.get_or_404(comment_id)
        notice_id = comment.notice_id
        
        db.session.delete(comment)
        db.session.commit()
        
        save_comment_history(comment, current_user.id, 'delete')
        log_action_consistency(current_user.id, 'COMMENT_DELETED', f'Deleted comment {comment_id}', request.remote_addr)
        flash("댓글이 삭제되었습니다.", 'success')
        return redirect(url_for('notice_view', notice_id=notice_id))
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('댓글 삭제 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('notices'))

@app.route('/notices')
@login_required
def notices():
    """공지사항 목록 (검색/필터 기능 포함)"""
    try:
        q = request.args.get('q', '')
        cat = request.args.get('cat', '')
        query = Notice.query.filter_by(is_hidden=False)  # 숨김 처리된 공지사항 제외
        
        if q:
            query = query.filter(
                (Notice.title.contains(q)) | (Notice.content.contains(q))
            )
        if cat:
            query = query.filter(Notice.category == cat)
        
        notices = query.order_by(Notice.created_at.desc()).all()
        
        # 현재 사용자가 읽지 않은 공지사항 체크
        unread_notices = set()
        if notices:
            read_notices = NoticeRead.query.filter_by(user_id=current_user.id).all()
            read_notice_ids = {r.notice_id for r in read_notices}
            unread_notices = {n.id for n in notices if n.id not in read_notice_ids}
        
        # 카테고리 목록 조회
        categories = db.session.query(Notice.category).distinct().all()
        categories = [c[0] for c in categories if c[0]]
        
        return render_template('notices.html', 
                             notices=notices, 
                             unread_notices=unread_notices,
                             categories=categories,
                             q=q, 
                             cat=cat)
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('공지사항 목록 조회 중 오류가 발생했습니다.', 'error')
        return render_template('notices.html', 
                             notices=[], 
                             unread_notices=set(),
                             categories=[],
                             q='', 
                             cat='')

@app.route('/notice/<int:notice_id>')
@login_required
def notice_view(notice_id):
    """공지사항 상세보기"""
    try:
        notice = Notice.query.get_or_404(notice_id)
        
        # 읽음 체크(이미 읽지 않았다면)
        read = NoticeRead.query.filter_by(notice_id=notice_id, user_id=current_user.id).first()
        if not read:
            read_record = NoticeRead(notice_id=notice_id, user_id=current_user.id)
            db.session.add(read_record)
            db.session.commit()
            
            log_action_consistency(current_user.id, 'NOTICE_READ', f'Read notice: {notice.title}', request.remote_addr)
        
        # 첨부파일 미리보기 생성
        preview = None
        if notice.file_path and notice.file_type:
            file_path = os.path.join('static', notice.file_path)
            if os.path.exists(file_path):
                if notice.file_type in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                    # 이미지는 미리보기 없이 다운로드 링크만 제공
                    preview = "이미지 파일"
                elif notice.file_type in ['txt', 'md', 'log', 'csv']:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            content = f.read(MAX_PREVIEW_SIZE)
                            # XSS 방어
                            preview = escape_html(content)
                            if len(content) >= MAX_PREVIEW_SIZE:
                                preview += "\n\n... (파일이 너무 커서 일부만 표시됩니다)"
                    except Exception as e:
                        preview = "미리보기에 실패했습니다."
                else:
                    preview = "다운로드 가능한 파일"
        
        return render_template('notice_view.html', notice=notice, preview=preview)
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('공지사항 조회 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('notices'))

@app.route('/admin/notice_stats')
@login_required
@admin_required
def notice_stats():
    """관리자: 공지사항 읽음 통계"""
    try:
        notices = Notice.query.order_by(Notice.created_at.desc()).all()
        users = User.query.filter_by(status='approved').all()
        
        stats = []
        for notice in notices:
            read_count = NoticeRead.query.filter_by(notice_id=notice.id).count()
            total_users = len(users)
            read_rate = (read_count / total_users * 100) if total_users > 0 else 0
            
            stats.append({
                'notice': notice,
                'read_count': read_count,
                'total_users': total_users,
                'read_rate': round(read_rate, 1)
            })
        
        return render_template('admin/notice_stats.html', stats=stats)
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('공지사항 통계 조회 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/suggestion', methods=['GET', 'POST'])
@login_required
def suggestion():
    """익명 건의함"""
    if request.method == 'POST':
        try:
            content = request.form['content']
            if not content.strip():
                flash('건의 내용을 입력해주세요.', 'error')
                return redirect(url_for('suggestion'))
            
            sug = Suggestion(content=content, is_anonymous=True)
            db.session.add(sug)
            db.session.commit()
            
            log_action(current_user.id, 'SUGGESTION_SUBMITTED', 'Anonymous suggestion submitted')
            flash("건의가 익명으로 접수되었습니다!", 'success')
            return redirect(url_for('suggestion'))
            
        except Exception as e:
            log_error(e, current_user.id)
            flash('건의 제출 중 오류가 발생했습니다.', 'error')
            return redirect(url_for('suggestion'))
    
    try:
        sugs = Suggestion.query.order_by(Suggestion.created_at.desc()).all()
        return render_template('suggestion.html', sugs=sugs)
    except Exception as e:
        log_error(e, current_user.id)
        flash('건의 목록 조회 중 오류가 발생했습니다.', 'error')
        return render_template('suggestion.html', sugs=[])

@app.route('/admin/suggestion_answer/<int:sug_id>', methods=['POST'])
@login_required
@admin_required
def suggestion_answer(sug_id):
    """관리자: 건의 답변 등록"""
    try:
        sug = Suggestion.query.get_or_404(sug_id)
        answer = request.form['answer']
        
        if not answer.strip():
            flash('답변 내용을 입력해주세요.', 'error')
            return redirect(url_for('suggestion'))
        
        sug.answer = answer
        sug.answered_at = db.func.now()
        db.session.commit()
        
        log_action(current_user.id, 'SUGGESTION_ANSWERED', f'Answered suggestion {sug_id}')
        flash("답변 등록 완료", 'success')
        return redirect(url_for('suggestion'))
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('답변 등록 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('suggestion'))

@app.route('/faq', methods=['GET', 'POST'])
@login_required
def faq():
    """AI FAQ/가이드 챗봇"""
    answer = None
    if request.method == 'POST':
        try:
            question = request.form['question']
            if not question.strip():
                flash('질문을 입력해주세요.', 'error')
                return redirect(url_for('faq'))
            
            # 간단 키워드 기반 답변 시스템
            question_lower = question.lower()
            
            if '급여' in question_lower or '월급' in question_lower or '봉급' in question_lower:
                answer = "급여는 근무시간 × 시급으로 자동 계산됩니다. 마이페이지에서 상세 내역을 확인할 수 있습니다."
            elif '지각' in question_lower or '조퇴' in question_lower or '출근' in question_lower:
                answer = "지각/조퇴 기록은 관리자 및 본인 마이페이지에서 확인할 수 있습니다. 출근/퇴근 버튼으로 정확한 시간을 기록하세요."
            elif 'pdf' in question_lower or '명세서' in question_lower or '영수증' in question_lower:
                answer = "마이페이지에서 PDF 버튼을 클릭해 급여명세서를 받을 수 있습니다. 관리자에게 문의하시면 상세한 내역을 제공해드립니다."
            elif '근무' in question_lower and ('변경' in question_lower or '교대' in question_lower):
                answer = "근무 변경은 '근무 변경 신청' 메뉴에서 신청할 수 있습니다. 관리자 승인 후 변경됩니다."
            elif '건의' in question_lower or '제안' in question_lower:
                answer = "익명 건의함을 통해 건의사항을 제출할 수 있습니다. 관리자가 답변을 제공합니다."
            elif '공지' in question_lower or '알림' in question_lower:
                answer = "공지사항 메뉴에서 최신 공지사항을 확인할 수 있습니다. 읽지 않은 공지사항은 표시됩니다."
            elif '비밀번호' in question_lower or '패스워드' in question_lower:
                answer = "비밀번호 변경은 '비밀번호 변경' 메뉴에서 할 수 있습니다. 보안을 위해 정기적으로 변경하시기 바랍니다."
            elif '계정' in question_lower or '로그인' in question_lower:
                answer = "계정 관련 문제는 관리자에게 문의하세요. 계정 잠금, 승인 대기 등의 문제를 해결해드립니다."
            else:
                answer = "죄송합니다. 해당 질문에 대한 답변을 찾을 수 없습니다. 관리자에게 직접 문의해 주세요."
            
            log_action(current_user.id, 'FAQ_QUESTION', f'Asked: {question[:50]}...')
            
        except Exception as e:
            log_error(e, current_user.id)
            flash('질문 처리 중 오류가 발생했습니다.', 'error')
            return redirect(url_for('faq'))
    
    return render_template('faq.html', answer=answer)

@app.route('/admin/backup', methods=['GET'])
@login_required
@admin_required
def admin_backup():
    """DB 백업 다운로드"""
    try:
        # SQLite DB 경로 추출
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
        else:
            db_path = db_uri.replace('sqlite:///', '')
        
        # 백업 파일명 생성 (날짜 포함)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"restaurant_backup_{timestamp}.sqlite3"
        backup_path = os.path.join('backups', backup_filename)
        
        # backups 폴더 생성
        os.makedirs('backups', exist_ok=True)
        
        # DB 파일 복사
        shutil.copy2(db_path, backup_path)
        
        log_action(current_user.id, 'DB_BACKUP', f'Database backup created: {backup_filename}')
        
        return send_file(backup_path, 
                        as_attachment=True, 
                        download_name=backup_filename,
                        mimetype='application/octet-stream')
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('DB 백업 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/restore', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_restore():
    """DB 복원"""
    if request.method == 'POST':
        try:
            # SQLite DB 경로 추출
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
            else:
                db_path = db_uri.replace('sqlite:///', '')
            
            file = request.files['file']
            if not file or not file.filename:
                flash('파일을 선택해주세요.', 'error')
                return redirect(url_for('admin_restore'))
            
            # 파일 확장자 검증
            if not file.filename.endswith('.sqlite3'):
                flash('SQLite 데이터베이스 파일(.sqlite3)만 업로드 가능합니다.', 'error')
                return redirect(url_for('admin_restore'))
            
            # 기존 DB 백업 생성
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            current_backup = f"restaurant_current_{timestamp}.sqlite3"
            current_backup_path = os.path.join('backups', current_backup)
            
            os.makedirs('backups', exist_ok=True)
            shutil.copy2(db_path, current_backup_path)
            
            # 새 DB 파일 저장
            file.save(db_path)
            
            log_action(current_user.id, 'DB_RESTORE', f'Database restored from: {file.filename}')
            flash('DB 복원이 완료되었습니다. 프로그램을 재시작해주세요.', 'success')
            return redirect(url_for('admin_dashboard'))
            
        except Exception as e:
            log_error(e, current_user.id)
            flash('DB 복원 중 오류가 발생했습니다.', 'error')
            return redirect(url_for('admin_restore'))
    
    return render_template('admin/restore.html')

@app.route('/admin/file_backup', methods=['GET'])
@login_required
@admin_required
def admin_file_backup():
    """첨부파일 백업 다운로드"""
    try:
        uploads_dir = os.path.join('static', 'uploads')
        
        # uploads 폴더가 없으면 빈 ZIP 생성
        if not os.path.exists(uploads_dir):
            flash('백업할 첨부파일이 없습니다.', 'info')
            return redirect(url_for('admin_dashboard'))
        
        # ZIP 파일 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f"uploads_backup_{timestamp}.zip"
        zip_path = os.path.join('backups', zip_filename)
        
        os.makedirs('backups', exist_ok=True)
        
        with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for foldername, subfolders, filenames in os.walk(uploads_dir):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    arcname = os.path.relpath(file_path, uploads_dir)
                    zf.write(file_path, arcname)
        
        log_action(current_user.id, 'FILE_BACKUP', f'File backup created: {zip_filename}')
        
        return send_file(zip_path, 
                        as_attachment=True, 
                        download_name=zip_filename,
                        mimetype='application/zip')
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('첨부파일 백업 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/file_restore', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_file_restore():
    """첨부파일 복원"""
    if request.method == 'POST':
        try:
            file = request.files['file']
            if not file or not file.filename:
                flash('파일을 선택해주세요.', 'error')
                return redirect(url_for('admin_file_restore'))
            
            # ZIP 파일 검증
            if not file.filename.endswith('.zip'):
                flash('ZIP 파일만 업로드 가능합니다.', 'error')
                return redirect(url_for('admin_file_restore'))
            
            uploads_dir = os.path.join('static', 'uploads')
            
            # 기존 uploads 폴더 백업
            if os.path.exists(uploads_dir):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                current_backup = f"uploads_current_{timestamp}.zip"
                current_backup_path = os.path.join('backups', current_backup)
                
                os.makedirs('backups', exist_ok=True)
                
                with zipfile.ZipFile(current_backup_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
                    for foldername, subfolders, filenames in os.walk(uploads_dir):
                        for filename in filenames:
                            file_path = os.path.join(foldername, filename)
                            arcname = os.path.relpath(file_path, uploads_dir)
                            zf.write(file_path, arcname)
            
            # uploads 폴더 생성 및 파일 복원
            os.makedirs(uploads_dir, exist_ok=True)
            
            with zipfile.ZipFile(file) as zf:
                zf.extractall(uploads_dir)
            
            log_action(current_user.id, 'FILE_RESTORE', f'Files restored from: {file.filename}')
            flash('첨부파일 복원이 완료되었습니다!', 'success')
            return redirect(url_for('admin_dashboard'))
            
        except Exception as e:
            log_error(e, current_user.id)
            flash('첨부파일 복원 중 오류가 발생했습니다.', 'error')
            return redirect(url_for('admin_file_restore'))
    
    return render_template('admin/file_restore.html')

@app.route('/notice/delete/<int:notice_id>', methods=['POST'])
@owner_or_admin(lambda notice_id: Notice.query.get_or_404(notice_id))
def notice_delete(notice_id):
    """공지사항 삭제 (트랜잭션 및 롤백 처리)"""
    try:
        from sqlalchemy.exc import SQLAlchemyError
        
        notice = Notice.query.get_or_404(notice_id)
        title = notice.title
        
        # 첨부파일 안전 삭제
        if notice.file_path:
            file_path = os.path.join('static', notice.file_path)
            safe_remove(file_path)
        
        # 댓글 삭제
        comments_count = NoticeComment.query.filter_by(notice_id=notice_id).count()
        NoticeComment.query.filter_by(notice_id=notice_id).delete()
        
        # 공지사항 삭제
        db.session.delete(notice)
        db.session.commit()
        
        save_notice_history(notice, current_user.id, 'delete')
        log_action_consistency(current_user.id, 'NOTICE_DELETED', 
                             f'Deleted notice: {title} (comments: {comments_count})', 
                             request.remote_addr)
        flash("공지 삭제 완료", 'success')
        return redirect(url_for('notices'))
        
    except SQLAlchemyError as e:
        db.session.rollback()
        log_error(e, current_user.id)
        flash('삭제 중 오류가 발생했습니다. 다시 시도해주세요.', 'error')
        return redirect(url_for('notices'))
    except Exception as e:
        log_error(e, current_user.id)
        flash('공지사항 삭제 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('notices'))

@app.route('/notice/<int:notice_id>/comment', methods=['POST'])
@login_required
def comment_new(notice_id):
    """댓글 등록"""
    try:
        content = request.form.get('content', '').strip()
        if not content:
            flash('댓글 내용을 입력해주세요.', 'error')
            return redirect(url_for('notice_view', notice_id=notice_id))
        
        # XSS 방어
        content = escape_html(content)
        
        comment = NoticeComment(
            notice_id=notice_id, 
            user_id=current_user.id, 
            content=content
        )
        db.session.add(comment)
        db.session.commit()
        
        save_comment_history(comment, current_user.id, 'create')
        log_action_consistency(current_user.id, 'COMMENT_CREATED', f'Added comment to notice {notice_id}', request.remote_addr)
        flash("댓글이 등록되었습니다.", 'success')
        return redirect(url_for('notice_view', notice_id=notice_id))
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('댓글 등록 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('notice_view', notice_id=notice_id))

def highlight(text, keyword):
    """검색어 하이라이트 기능"""
    if not keyword or not text:
        return text
    return re.sub(f"({re.escape(keyword)})", r'<mark>\1</mark>', text, flags=re.IGNORECASE)

@app.template_filter('highlight')
def highlight_filter(text, keyword):
    """템플릿 필터로 사용할 하이라이트 함수"""
    return highlight(text, keyword)

@app.route('/admin/notice_history/<int:notice_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_notice_history(notice_id):
    """관리자: 공지사항 변경이력 조회 및 복원"""
    try:
        notice = Notice.query.get_or_404(notice_id)
        history = NoticeHistory.query.filter_by(notice_id=notice_id).order_by(NoticeHistory.edited_at.desc()).all()
        
        # 복원 요청 처리
        if request.method == 'POST':
            hist_id = int(request.form.get('history_id'))
            hist = NoticeHistory.query.get_or_404(hist_id)
            
            # 복원 전 현재 상태를 이력으로 저장
            save_notice_history(notice, current_user.id, 'restore')
            
            # 이전 버전으로 복원
            notice.title = hist.before_title
            notice.content = hist.before_content
            notice.file_path = hist.before_file_path
            notice.file_type = hist.before_file_type
            db.session.commit()
            
            log_action_consistency(current_user.id, 'NOTICE_RESTORED', 
                                 f'Restored notice {notice_id} to version {hist_id}', 
                                 request.remote_addr)
            flash("이전 버전으로 복원되었습니다.", 'success')
            return redirect(url_for('admin_notice_history', notice_id=notice_id))
        
        return render_template('admin/notice_history.html', notice=notice, history=history)
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('공지사항 이력 조회 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/hidden_notices')
@login_required
@admin_required
def admin_hidden_notices():
    """관리자: 숨김 처리된 공지사항 조회"""
    try:
        notices = Notice.query.filter_by(is_hidden=True).order_by(Notice.created_at.desc()).all()
        return render_template('admin/hidden_notices.html', notices=notices)
    except Exception as e:
        log_error(e, current_user.id)
        flash('숨김 공지사항 조회 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/report/<target_type>/<int:target_id>', methods=['POST'])
@login_required
def report(target_type, target_id):
    """신고 처리 (개선된 버전)"""
    try:
        reason = request.form.get('reason', '').strip()
        category = request.form.get('category', '').strip()
        detail = request.form.get('detail', '').strip()
        
        if not reason or not category:
            flash('신고 사유와 카테고리를 선택해주세요.', 'error')
            return redirect(request.referrer or url_for('notices'))
        
        # 동일 대상 1인 1회만 허용
        existing_report = Report.query.filter_by(
            target_type=target_type,
            target_id=target_id,
            user_id=current_user.id
        ).first()
        
        if existing_report:
            flash("이미 신고하셨습니다!", 'warning')
            return redirect(request.referrer or url_for('notices'))
        
        # 신고 대상 존재 확인
        if target_type == 'notice':
            target = Notice.query.get(target_id)
            if not target:
                flash('존재하지 않는 공지사항입니다.', 'error')
                return redirect(url_for('notices'))
        elif target_type == 'comment':
            target = NoticeComment.query.get(target_id)
            if not target:
                flash('존재하지 않는 댓글입니다.', 'error')
                return redirect(url_for('notices'))
        else:
            flash('잘못된 신고 대상입니다.', 'error')
            return redirect(url_for('notices'))
        
        # 신고 등록
        report = Report(
            target_type=target_type,
            target_id=target_id,
            user_id=current_user.id,
            reason=reason,
            category=category,
            detail=detail
        )
        db.session.add(report)
        db.session.commit()
        
        log_action(current_user.id, 'REPORT_SUBMITTED', f'Reported {target_type} {target_id}: {category}')
        flash("신고가 접수되었습니다. 관리자가 검토합니다.", 'success')
        return redirect(request.referrer or url_for('notices'))
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('신고 처리 중 오류가 발생했습니다.', 'error')
        return redirect(request.referrer or url_for('notices'))

@app.route('/admin/reports')
@login_required
@admin_required
def admin_reports():
    """관리자: 신고 내역 조회"""
    try:
        reports = Report.query.order_by(Report.created_at.desc()).all()
        return render_template('admin/reports.html', reports=reports)
    except Exception as e:
        log_error(e, current_user.id)
        flash('신고 내역 조회 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/moderation')
@login_required
@admin_required
def admin_moderation():
    reports = Report.query.filter_by(status='pending').order_by(Report.created_at.desc()).all()
    return render_template('admin/moderation.html', reports=reports)

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    init_extensions(app)
    setup_logging(app)
    
    # 여기서 블루프린트 등록
    # from .routes import main as main_blueprint
    # app.register_blueprint(main_blueprint)

    return app

if __name__ == '__main__':
    app.run(debug=True)
