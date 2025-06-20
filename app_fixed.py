from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, date, time
from sqlalchemy import func, extract
from sqlalchemy.sql import text
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
from io import StringIO
from markupsafe import escape as escape_html

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant_dev.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# 확장 기능 초기화
db = SQLAlchemy()
migrate = None
cache = Cache()
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# CSRF 보호 설정
csrf = CSRFProtect(app)

# 임시로 CSRF 보호 비활성화 (개발 중)
app.config['WTF_CSRF_ENABLED'] = False

# 확장 기능 초기화
db.init_app(app)
cache.init_app(app)

# 모델 import (순환 import 방지)
from models import User, Attendance, Notice, NoticeComment, NoticeHistory, CommentHistory, Report, NoticeRead, ApproveLog, ShiftRequest, Notification, Suggestion, Feedback, ActionLog

# 유틸리티 함수들 import
try:
    from utils.logger import setup_logger, log_error, log_action, log_action_consistency, log_security_event
    from utils.attendance import check_account_lockout, increment_failed_attempts, reset_failed_attempts
    from utils.notify import notify_approval_result, send_notification
    from utils.report import generate_attendance_report_pdf, generate_monthly_summary_pdf
    from utils.pay_transfer import transfer_salary, validate_bank_account
    from utils.payroll import generate_payroll_pdf
    from utils.dashboard import get_user_monthly_trend
    from utils.security import owner_or_admin
    from utils.file_utils import save_uploaded_file, safe_remove, MAX_PREVIEW_SIZE
except ImportError:
    # 유틸리티 함수들이 없으면 더미 함수로 대체
    def setup_logger(app): return None
    def log_error(e): print(f"Error: {e}")
    def log_action(user_id, action, message=""): pass
    def log_action_consistency(user_id, action, message=""): pass
    def log_security_event(user_id, action, message=""): pass
    def check_account_lockout(user): return False, ""
    def increment_failed_attempts(user): pass
    def reset_failed_attempts(user): pass
    def notify_approval_result(user_id, result): pass
    def send_notification(user_id, message): pass
    def generate_attendance_report_pdf(user_id): return None
    def generate_monthly_summary_pdf(): return None
    def transfer_salary(user_id, amount): return True
    def validate_bank_account(account): return True
    def generate_payroll_pdf(user_id): return None
    def get_user_monthly_trend(user_id): return []
    def owner_or_admin(getter_func): 
        def decorator(f):
            return f
        return decorator
    def save_uploaded_file(file): return ""
    def safe_remove(path): pass
    MAX_PREVIEW_SIZE = 1024 * 1024

# 보안 헤더 미들웨어
@app.after_request
def add_security_headers(response):
    """보안 헤더 추가"""
    for header, value in app.config.get('SECURITY_HEADERS', {}).items():
        response.headers[header] = value
    return response

# 로거 설정
logger = setup_logger(app)

# 로그인 매니저 설정
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '로그인이 필요합니다.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        log_error(e)
        return None

# 보안 강화된 데코레이터들
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('로그인이 필요합니다.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('로그인이 필요합니다.', 'warning')
            return redirect(url_for('login'))
        if not (current_user.is_admin() or current_user.is_manager()):
            log_security_event(current_user.id, 'UNAUTHORIZED_ACCESS', f'Attempted to access {request.endpoint}')
            flash("관리자 권한이 필요합니다.", 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# 에러 핸들러
@app.errorhandler(404)
def page_not_found(e):
    log_error(e)
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    log_error(e)
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden(e):
    log_error(e)
    return render_template('errors/403.html'), 403

@app.errorhandler(413)
def too_large(e):
    """파일 크기 초과 오류 핸들러"""
    log_error(e)
    return render_template("errors/413.html", message="파일 용량이 너무 큽니다! (최대 10MB)"), 413

# --- 인증/회원가입/로그인 ---
@app.route('/', methods=['GET'])
@login_required
def index():
    if current_user.is_admin() or current_user.is_manager():
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('아이디와 비밀번호를 입력해주세요.', 'error')
            return redirect(url_for('login'))
        
        try:
            user = User.query.filter_by(username=username).first()
            
            if not user:
                flash('아이디 또는 비밀번호가 잘못되었습니다.', 'error')
                return redirect(url_for('login'))
            
            # 계정 잠금 확인
            is_locked, lock_message = check_account_lockout(user)
            if is_locked:
                flash(lock_message, 'error')
                return redirect(url_for('login'))
            
            if not user.check_password(password):
                # 로그인 실패 횟수 증가
                increment_failed_attempts(user)
                log_security_event(user.id, 'LOGIN_FAILED', f'Failed login attempt from {request.remote_addr}')
                flash('아이디 또는 비밀번호가 잘못되었습니다.', 'error')
                return redirect(url_for('login'))
            
            if user.status != 'approved':
                flash('승인 대기 중인 계정입니다. 관리자에게 문의하세요.', 'warning')
                return redirect(url_for('login'))
            
            # 로그인 성공
            reset_failed_attempts(user)
            login_user(user)
            log_action(user.id, 'LOGIN_SUCCESS', f'Login from {request.remote_addr}')
            flash('로그인 성공!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            log_error(e)
            flash('로그인 중 오류가 발생했습니다.', 'error')
            return redirect(url_for('login'))
    
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    try:
        user_id = current_user.id
        logout_user()
        session.clear()
        log_action(user_id, 'LOGOUT')
        flash('로그아웃되었습니다.', 'info')
    except Exception as e:
        log_error(e)
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

@app.route('/dashboard')
@login_required
@cache.cached(timeout=60)  # 1분 캐시
def dashboard():
    try:
        # 최근 출근 기록
        recent_records = Attendance.query.filter_by(user_id=current_user.id)\
                                        .order_by(Attendance.clock_in.desc())\
                                        .limit(5).all()
        
        # 이번 달 통계
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_records = Attendance.query.filter(
            Attendance.user_id == current_user.id,
            Attendance.clock_in >= current_month
        ).all()
        
        total_hours = sum(record.work_hours for record in monthly_records if record.clock_out)
        total_days = len(monthly_records)
        
        return render_template('dashboard.html', 
                             recent_records=recent_records,
                             total_hours=total_hours,
                             total_days=total_days)
    except Exception as e:
        log_error(e)
        flash('대시보드 로딩 중 오류가 발생했습니다.', 'error')
        return render_template('dashboard.html', recent_records=[], total_hours=0, total_days=0)

@app.route('/clock_in')
@login_required
def clock_in():
    try:
        today = Attendance.query.filter_by(user_id=current_user.id)\
                               .filter(db.func.date(Attendance.clock_in) == datetime.utcnow().date())\
                               .first()
        
        if today and today.clock_out is None:
            flash("이미 출근 처리되었습니다.", 'warning')
            return redirect(url_for('dashboard'))
        
        attendance = Attendance(user_id=current_user.id)
        db.session.add(attendance)
        db.session.commit()
        
        log_action(current_user.id, 'CLOCK_IN', f'Clock in at {attendance.clock_in}')
        flash("출근 처리 완료!", 'success')
        
    except Exception as e:
        log_error(e)
        flash("출근 처리 중 오류가 발생했습니다.", 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/clock_out')
@login_required
def clock_out():
    try:
        today = Attendance.query.filter_by(user_id=current_user.id)\
                               .filter(db.func.date(Attendance.clock_in) == datetime.utcnow().date())\
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
        log_error(e)
        flash("퇴근 처리 중 오류가 발생했습니다.", 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/attendance')
@login_required
def attendance():
    try:
        records = Attendance.query.filter_by(user_id=current_user.id)\
                                 .order_by(Attendance.clock_in.desc()).all()
        return render_template('attendance/my_attendance.html', records=records)
    except Exception as e:
        log_error(e)
        flash('출근 기록 조회 중 오류가 발생했습니다.', 'error')
        return render_template('attendance/my_attendance.html', records=[])

@app.route('/admin')
@login_required
@admin_required
@cache.cached(timeout=300)  # 5분 캐시
def admin_dashboard():
    try:
        # 사용자 통계
        total_users = User.query.filter_by(status='approved').count()
        pending_users = User.query.filter_by(status='pending').count()
        
        # 출근 통계
        today = datetime.utcnow().date()
        today_attendance = Attendance.query.filter(
            db.func.date(Attendance.clock_in) == today
        ).count()
        
        # 최근 활동
        recent_actions = ActionLog.query.order_by(ActionLog.created_at.desc()).limit(10).all()
        
        return render_template('admin/dashboard.html',
                             total_users=total_users,
                             pending_users=pending_users,
                             today_attendance=today_attendance,
                             recent_actions=recent_actions)
    except Exception as e:
        log_error(e)
        flash('관리자 대시보드 로딩 중 오류가 발생했습니다.', 'error')
        return render_template('admin/dashboard.html',
                             total_users=0,
                             pending_users=0,
                             today_attendance=0,
                             recent_actions=[])

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    try:
        users = User.query.all()
        return render_template('admin_users.html', users=users)
    except Exception as e:
        log_error(e)
        flash('사용자 목록 조회 중 오류가 발생했습니다.', 'error')
        return render_template('admin_users.html', users=[])

@app.route('/notices')
@login_required
def notices():
    try:
        notices = Notice.query.filter_by(is_hidden=False)\
                             .order_by(Notice.created_at.desc()).all()
        return render_template('notices.html', notices=notices)
    except Exception as e:
        log_error(e)
        flash('공지사항 조회 중 오류가 발생했습니다.', 'error')
        return render_template('notices.html', notices=[])

@app.route('/faq')
@login_required
def faq():
    return render_template('faq.html')

@app.route('/suggestion', methods=['GET', 'POST'])
@login_required
def suggestion():
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            try:
                suggestion = Suggestion(content=content)
                db.session.add(suggestion)
                db.session.commit()
                flash("건의가 접수되었습니다!", 'success')
            except Exception as e:
                log_error(e)
                flash("건의 접수 중 오류가 발생했습니다.", 'error')
        return redirect(url_for('suggestion'))
    
    try:
        sugs = Suggestion.query.order_by(Suggestion.created_at.desc()).all()
        return render_template('suggestion.html', sugs=sugs)
    except Exception as e:
        log_error(e)
        return render_template('suggestion.html', sugs=[])

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/calendar')
@login_required
def calendar():
    return render_template('calendar.html', events=[])

@app.route('/shift_request', methods=['GET', 'POST'])
@login_required
def shift_request():
    if request.method == 'POST':
        try:
            request_date = datetime.strptime(request.form.get('request_date'), '%Y-%m-%d').date()
            desired_date = datetime.strptime(request.form.get('desired_date'), '%Y-%m-%d').date()
            reason = request.form.get('reason')
            
            shift_request = ShiftRequest(
                user_id=current_user.id,
                request_date=request_date,
                desired_date=desired_date,
                reason=reason
            )
            db.session.add(shift_request)
            db.session.commit()
            
            flash("근무 변경 신청이 접수되었습니다!", 'success')
        except Exception as e:
            log_error(e)
            flash("근무 변경 신청 중 오류가 발생했습니다.", 'error')
        return redirect(url_for('shift_request'))
    
    try:
        requests = ShiftRequest.query.filter_by(user_id=current_user.id)\
                                   .order_by(ShiftRequest.created_at.desc()).all()
        return render_template('shift_request.html', requests=requests)
    except Exception as e:
        log_error(e)
        return render_template('shift_request.html', requests=[])

@app.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    if request.method == 'POST':
        try:
            satisfaction = int(request.form.get('satisfaction', 0))
            health = int(request.form.get('health', 0))
            comment = request.form.get('comment', '')
            category = request.form.get('category', '일반')
            
            feedback = Feedback(
                user_id=current_user.id,
                satisfaction=satisfaction,
                health=health,
                comment=comment,
                category=category
            )
            db.session.add(feedback)
            db.session.commit()
            
            flash("피드백 제출 완료", 'success')
        except Exception as e:
            log_error(e)
            flash("피드백 제출 중 오류가 발생했습니다.", 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('feedback.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # 관리자 계정이 없으면 생성
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(username='admin', role='admin', status='approved')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("관리자 계정이 생성되었습니다. (username: admin, password: admin123)")
    
    app.run(debug=True) 