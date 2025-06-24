from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, date
from dateutil import parser as date_parser
import os
import click
from collections import defaultdict

from config import config_by_name
from extensions import db, migrate, login_manager, csrf, limiter, cache
from models import User, Schedule, CleaningPlan, Report, Notification, Notice, Order

# Import notification functions
from utils.notify import (
    send_notification_enhanced, 
    send_admin_only_notification,
    send_notification_to_role
)

# Import API Blueprints
from api.auth import api_auth_bp, auth_bp
from api.notice import api_notice_bp
from api.comment import api_comment_bp
from api.report import api_report_bp
from api.admin_report import admin_report_bp
from api.admin_log import admin_log_bp
from api.admin_report_stat import admin_report_stat_bp
from api.comment_report import comment_report_bp

# Import Route Blueprints
from routes.payroll import payroll_bp
from routes.notifications import notifications_bp

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

# Exempt all API blueprints from CSRF protection
csrf.exempt(api_auth_bp)
csrf.exempt(api_notice_bp)
csrf.exempt(api_comment_bp)
csrf.exempt(api_report_bp)
csrf.exempt(admin_report_bp)
csrf.exempt(admin_log_bp)
csrf.exempt(admin_report_stat_bp)
csrf.exempt(comment_report_bp)

# Register API Blueprints
app.register_blueprint(api_auth_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(api_notice_bp)
app.register_blueprint(api_comment_bp)
app.register_blueprint(api_report_bp)
app.register_blueprint(admin_report_bp)
app.register_blueprint(admin_log_bp)
app.register_blueprint(admin_report_stat_bp)
app.register_blueprint(comment_report_bp)

# Register Route Blueprints
app.register_blueprint(payroll_bp)
app.register_blueprint(notifications_bp)

# Login manager setup
login_manager.login_view = 'auth.login'
login_manager.login_message = '로그인이 필요합니다.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Error Handlers ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

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
    return render_template('profile.html', user=current_user)

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.')
        return redirect(url_for('dashboard'))
    
    # 기본 통계 데이터
    context = {
        'num_users': User.query.count(),
        'num_attendance': 0,
        'warn_users': [],
        'result': [],
        'branch_names': [],
        'chart_labels': [],
        'chart_data': [],
        'trend_dates': [],
        'trend_data': [],
        'dist_labels': [],
        'dist_data': [],
        'top_late': [],
        'top_absent': [],
        'recent': []
    }
    return render_template('admin_dashboard.html', **context)

# --- Schedule Routes ---
@app.route('/schedule', methods=['GET'])
@login_required
def schedule():
    from_date_str = request.args.get('from', datetime.now().strftime('%Y-%m-%d'))
    to_date_str = request.args.get('to', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        from_dt = date_parser.parse(from_date_str).date()
        to_dt = date_parser.parse(to_date_str).date()
    except ValueError:
        flash('날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)', 'error')
        from_dt = datetime.now().date()
        to_dt = datetime.now().date()
    
    if from_dt > to_dt:
        flash('시작일은 종료일보다 늦을 수 없습니다.', 'error')
        from_dt, to_dt = to_dt, from_dt
    
    days_diff = (to_dt - from_dt).days
    if days_diff > 90:
        flash('최대 90일까지 조회 가능합니다.', 'warning')
        to_dt = from_dt + timedelta(days=90)
    
    days = [(from_dt + timedelta(days=i)) for i in range(days_diff + 1)]
    schedules = {d: Schedule.query.filter_by(date=d).all() for d in days}
    cleanings = {d: CleaningPlan.query.filter_by(date=d).all() for d in days}
    
    return render_template('schedule.html',
        from_date=from_dt.strftime('%Y-%m-%d'), 
        to_date=to_dt.strftime('%Y-%m-%d'),
        dates=days, 
        schedules=schedules, 
        cleanings=cleanings
    )

@app.route('/clean')
@login_required
def clean():
    plans = CleaningPlan.query.order_by(CleaningPlan.date.desc()).all()
    return render_template('clean.html', plans=plans)

# --- Notification Routes ---
@app.route('/notifications')
@login_required
def notifications():
    """알림센터"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 권한에 따라 다른 쿼리
    if current_user.is_admin():
        query = Notification.query
    else:
        query = Notification.query.filter(
            db.or_(
                Notification.user_id == current_user.id,
                Notification.is_admin_only == False
            )
        )
    
    notifications = query.order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('notifications.html', notifications=notifications)

@app.route('/notifications/mark_read/<int:notification_id>')
@login_required
def mark_notification_read(notification_id):
    """개별 알림 읽음 처리"""
    notification = Notification.query.filter_by(
        id=notification_id, 
        user_id=current_user.id
    ).first()
    
    if notification:
        notification.is_read = True
        db.session.commit()
        flash('알림을 읽음 처리했습니다.', 'success')
    else:
        flash('알림을 찾을 수 없습니다.', 'error')
    
    return redirect(url_for('notifications'))

@app.route('/notifications/mark_all_read')
@login_required
def mark_all_notifications_read():
    """모든 알림 읽음 처리"""
    try:
        Notification.query.filter_by(
            user_id=current_user.id, 
            is_read=False
        ).update({'is_read': True})
        db.session.commit()
        flash('모든 알림을 읽음 처리했습니다.', 'success')
    except Exception as e:
        flash('알림 처리 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('notifications'))

# --- API Routes for Notifications ---
@app.route('/api/new_notifications')
@login_required
def api_new_notifications():
    """새로운 알림 수 API"""
    try:
        count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return jsonify({'count': count})
    except Exception as e:
        return jsonify({'count': 0, 'error': str(e)})

# --- CLI Commands ---
@app.cli.command('create-admin')
@click.argument('username')
@click.argument('password')
def create_admin(username, password):
    """관리자 계정 생성"""
    user = User(username=username, role='admin', status='approved')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo(f'관리자 계정 {username}이 생성되었습니다.')

if __name__ == '__main__':
    app.run(debug=True) 