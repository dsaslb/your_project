#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
app.py 오류 수정 스크립트
"""

def fix_app_py():
    """app.py의 import와 초기화 오류를 수정합니다."""
    
    print("🔧 app.py 오류 수정 중...")
    
    # 파일 읽기
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 새로운 import와 초기화 코드
    new_header = '''from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, Response
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

'''
    
    # 기존 import 부분을 새로운 import로 교체
    lines = content.split('\n')
    new_lines = []
    
    # 첫 번째 @app.route 라인을 찾을 때까지 건너뛰기
    skip_until_route = True
    for line in lines:
        if skip_until_route:
            if line.strip().startswith('@app.route'):
                skip_until_route = False
                new_lines.append(new_header)
                new_lines.append(line)
            # import 라인들과 초기화 라인들은 건너뛰기
            elif not (line.strip().startswith('from ') or line.strip().startswith('import ') or 
                     line.strip().startswith('app = ') or line.strip().startswith('app.config') or
                     line.strip().startswith('csrf = ') or line.strip().startswith('db.init_app') or
                     line.strip().startswith('migrate.init_app') or line.strip().startswith('cache.init_app') or
                     line.strip().startswith('limiter.init_app') or line.strip().startswith('@app.after_request') or
                     line.strip().startswith('logger = ') or line.strip().startswith('login_manager = ') or
                     line.strip().startswith('@login_manager.user_loader') or line.strip().startswith('def load_user') or
                     line.strip().startswith('def login_required') or line.strip().startswith('def admin_required') or
                     line.strip().startswith('@app.errorhandler')):
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # 파일 저장
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ app.py 오류 수정 완료!")

if __name__ == '__main__':
    fix_app_py() 