from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required, logout_user, current_user
from datetime import datetime
import os
import click
from collections import defaultdict

from config import config_by_name
from extensions import db, migrate, login_manager, csrf, limiter, cache
from models import User, Schedule, CleaningPlan, Report

# Import API Blueprints
from api.auth import api_auth_bp, auth_bp
from api.notice import api_notice_bp
from api.comment import api_comment_bp
from api.report import api_report_bp
from api.admin_report import admin_report_bp
from api.admin_log import admin_log_bp


def create_app(config_name=None):
    if config_name is None:
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

    # Register API Blueprints
    app.register_blueprint(api_auth_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_notice_bp)
    app.register_blueprint(api_comment_bp)
    app.register_blueprint(api_report_bp)
    app.register_blueprint(admin_report_bp)
    app.register_blueprint(admin_log_bp)

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

    # --- Routes ---
    @app.route('/')
    @login_required
    def index():
        if hasattr(current_user, 'role') and current_user.role == 'admin':
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
        if not (hasattr(current_user, 'role') and current_user.role == 'admin'):
            flash('관리자 권한이 필요합니다.')
            return redirect(url_for('dashboard'))
        
        context = {
            'num_users': User.query.count(),
            'num_attendance': 0,
            'warn_users': [], 'result': [], 'branch_names': [], 'chart_labels': [],
            'chart_data': [], 'trend_dates': [], 'trend_data': [], 'dist_labels': [],
            'dist_data': [], 'top_late': [], 'top_absent': [], 'recent': []
        }
        return render_template('admin_dashboard.html', **context)

    @app.route('/admin/attendance-stats')
    @login_required
    def attendance_stats():
        if not (hasattr(current_user, 'role') and current_user.role == 'admin'):
            flash('관리자 권한이 필요합니다.', 'error')
            return redirect(url_for('index'))
        return render_template('admin/attendance_stats.html')

    @app.route('/admin/attendance')
    @login_required
    def admin_attendance():
        if not (hasattr(current_user, 'role') and current_user.role == 'admin'):
            return redirect(url_for('index'))
        users = User.query.all()
        return render_template('admin/attendances.html', users=users)

    @app.route('/admin/reports')
    @login_required
    def admin_reports():
        if not (hasattr(current_user, 'role') and current_user.role == 'admin'):
            flash('관리자 권한이 필요합니다.', 'error')
            return redirect(url_for('index'))
        reports = Report.query.order_by(Report.created_at.desc()).all()
        return render_template('admin/reports.html', reports=reports)

    # CLI command
    @app.cli.command('create-admin')
    @click.argument('username')
    @click.argument('password')
    def create_admin_command(username, password):
        """새로운 관리자 계정을 생성합니다."""
        if User.query.filter_by(username=username).first():
            print(f"사용자 '{username}'가 이미 존재합니다.")
            return
        user = User(username=username, role='admin', status='approved')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"관리자 '{username}'가 성공적으로 생성되었습니다.")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) 