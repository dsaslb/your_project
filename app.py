from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import click
from collections import defaultdict

from config import config_by_name
from extensions import db, migrate, login_manager, csrf, limiter, cache
from models import User, Schedule, CleaningPlan, Report, Notification, Notice

# Import API Blueprints
from api.auth import api_auth_bp, auth_bp
from api.notice import api_notice_bp
from api.comment import api_comment_bp
from api.report import api_report_bp
from api.admin_report import admin_report_bp
from api.admin_log import admin_log_bp
from api.admin_report_stat import admin_report_stat_bp
from api.comment_report import comment_report_bp

# from utils.decorators import require_perm, admin_required
# from utils.notify import send_notification, notify_admins

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

# Login manager setup
login_manager.login_view = 'login'
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
    # In a real app, you'd log the error
    return render_template('errors/500.html'), 500

# --- Routes ---
@app.route('/')
@login_required
def index():
    if current_user.is_admin():
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

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
    
    # Pass empty/default data to prevent template errors
    context = {
        'num_users': User.query.count(),
        'num_attendance': 0, # Replace with actual query later
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

@app.route('/admin/attendance-stats')
@login_required
def attendance_stats():
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('index'))
    # In a real application, you would fetch data here
    return render_template('admin/attendance_stats.html')

# --- Placeholders for admin dashboard links ---
@app.route('/admin/attendance')
@login_required
def admin_attendance():
    if not current_user.is_admin(): return redirect(url_for('index'))
    users = User.query.all()
    return render_template('admin/attendances.html', users=users)

@app.route('/admin/payroll/bulk')
@login_required
def bulk_payroll():
    if not current_user.is_admin(): return redirect(url_for('index'))
    return "준비중인 페이지입니다. (급여명세서 일괄생성)"

@app.route('/admin/users')
@login_required
def admin_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/approve')
@login_required
def approve_users():
    if not current_user.is_admin(): return redirect(url_for('index'))
    pending_users = User.query.filter_by(status='pending').all()
    return render_template('approve_users.html', users=pending_users)

@app.route('/admin/swap_requests', methods=['GET'])
@login_required
def admin_swap_requests():
    # '대기' 상태인 '교대' 카테고리의 스케줄만 조회
    reqs = Schedule.query.filter_by(category='교대', status='대기').order_by(Schedule.date.asc()).all()
    return render_template('admin/swap_requests.html', swap_requests=reqs)

@app.route('/admin/notifications')
@login_required
def admin_notifications():
    if not current_user.is_admin(): return redirect(url_for('index'))
    return "준비중인 페이지입니다. (알림센터)"

@app.route('/admin/notice/stats')
@login_required
def notice_stats():
    if not current_user.is_admin(): return redirect(url_for('index'))
    return "준비중인 페이지입니다. (공지사항 통계)"

@app.route('/admin/reports/monthly-summary-pdf')
@login_required
def monthly_summary_pdf():
    if not current_user.is_admin(): return redirect(url_for('index'))
    return "준비중인 페이지입니다. (월별 근태 요약 PDF)"

@app.route('/admin/payroll/bulk-transfer')
@login_required
def bulk_transfer():
    if not current_user.is_admin(): return redirect(url_for('index'))
    return "준비중인 페이지입니다. (급여 자동이체)"

@app.route('/admin/notifications/send')
@login_required
def send_notification_page():
    if not current_user.is_admin(): return redirect(url_for('index'))
    return "준비중인 페이지입니다. (알림 발송)"

@app.route('/admin/backup/db')
@login_required
def admin_backup():
    if not current_user.is_admin(): return redirect(url_for('index'))
    return "준비중인 페이지입니다. (DB 백업)"

@app.route('/admin/restore/db')
@login_required
def admin_restore():
    if not current_user.is_admin(): return redirect(url_for('index'))
    return "준비중인 페이지입니다. (DB 복원)"

@app.route('/admin/backup/files')
@login_required
def admin_file_backup():
    if not current_user.is_admin(): return redirect(url_for('index'))
    return "준비중인 페이지입니다. (첨부파일 백업)"

@app.route('/admin/restore/files')
@login_required
def admin_file_restore():
    if not current_user.is_admin(): return redirect(url_for('index'))
    return "준비중인 페이지입니다. (첨부파일 복원)"

@app.route('/admin/logs/action')
@login_required
def admin_actionlog():
    if not current_user.is_admin(): return redirect(url_for('index'))
    return "준비중인 페이지입니다. (작업 로그)"

@app.route('/admin/logs/sys')
@login_required
def admin_syslog():
    if not current_user.is_admin(): return redirect(url_for('index'))
    return "준비중인 페이지입니다. (시스템 로그)"

@app.route('/schedule', methods=['GET'])
@login_required
def schedule():
    schedules = Schedule.query.filter(Schedule.user_id.in_([current_user.id])).order_by(Schedule.date).all()
    
    events = []
    for s in schedules:
        events.append({
            'title': s.category,
            'start': f"{s.date.isoformat()}T{s.start_time.isoformat()}",
            'end': f"{s.date.isoformat()}T{s.end_time.isoformat()}",
            'description': s.memo or '',
            'id': s.id
        })
    
    return render_template('schedule_fc.html', events=events)


@app.route('/clean')
@login_required
def clean():
    plans = CleaningPlan.query.order_by(CleaningPlan.date.desc()).all()
    return render_template('clean.html', plans=plans)


@app.route('/schedule_management', methods=['GET'])
@login_required
def schedule_management():
    # 관리자 또는 매니저만 접근 가능
    if not (current_user.is_admin() or current_user.is_manager()):
        flash('권한이 없습니다.', 'error')
        return redirect(url_for('index'))
    
    # 해당 지점의 모든 스케줄을 가져옴
    schedules = Schedule.query.filter_by(user_id=current_user.id).order_by(Schedule.date.desc()).all()
    return render_template('schedule_management.html', schedules=schedules)


@app.route('/schedule/add', methods=['GET', 'POST'])
@login_required
def add_schedule():
    if request.method == 'POST':
        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        category = request.form.get('category')
        memo = request.form.get('memo')
        user_id = current_user.id

        if not all([date, start_time, end_time, category]):
            flash('모든 필수 항목을 입력해주세요.', 'error')
            return redirect(url_for('add_schedule'))

        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()

            new_schedule = Schedule(
                user_id=user_id,
                date=date_obj,
                start_time=start_time_obj,
                end_time=end_time_obj,
                category=category,
                memo=memo
            )
            db.session.add(new_schedule)
            db.session.commit()
            flash('새로운 스케줄이 추가되었습니다.', 'success')
            return redirect(url_for('schedule_management'))
        except Exception as e:
            db.session.rollback()
            flash(f'오류가 발생했습니다: {e}', 'error')
            
    return render_template('add_schedule.html')


@app.route('/schedule_fc')
@login_required
def schedule_fc():
    schedules = Schedule.query.filter_by(user_id=current_user.id).all()
    events = []
    for s in schedules:
        events.append({
            'title': s.category,
            'start': f"{s.date.isoformat()}T{s.start_time.isoformat()}",
            'end': f"{s.date.isoformat()}T{s.end_time.isoformat()}",
            'description': s.memo,
            'id': s.id
        })
    return render_template('schedule_fc.html', events=events)


@app.route('/schedule/approve/<int:schedule_id>', methods=['POST'])
@login_required
def approve_schedule(schedule_id):
    if not (current_user.is_admin() or current_user.is_manager()):
        flash('권한이 없습니다.', 'error')
        return redirect(url_for('schedule_management'))
    
    schedule = Schedule.query.get_or_404(schedule_id)
    action = request.form.get('action') # 'approve' or 'reject'
    
    if action in ['승인', '거절']:
        schedule.status = action
        db.session.commit()
        flash(f'스케줄이 {action}되었습니다.', 'success')
    else:
        flash('잘못된 요청입니다.', 'error')
        
    return redirect(url_for('schedule_management'))


@app.route('/schedule/edit/<int:sid>', methods=['GET', 'POST'])
@login_required
def edit_schedule(sid):
    schedule = Schedule.query.get_or_404(sid)
    if schedule.user_id != current_user.id:
        flash("수정 권한이 없습니다.", 'error')
        return redirect(url_for('schedule_fc'))

    if request.method == 'POST':
        schedule.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        schedule.start_time = datetime.strptime(request.form['start_time'], '%H:%M').time()
        schedule.end_time = datetime.strptime(request.form['end_time'], '%H:%M').time()
        schedule.category = request.form['category']
        schedule.memo = request.form['memo']
        db.session.commit()
        flash("스케줄이 수정되었습니다.", 'success')
        return redirect(url_for('schedule_fc'))
    
    return render_template('edit_schedule.html', schedule=schedule)

@app.route('/schedule/delete/<int:sid>')
@login_required
def delete_schedule(sid):
    schedule = Schedule.query.get_or_404(sid)
    if schedule.user_id != current_user.id:
        flash("삭제 권한이 없습니다.", 'error')
        return redirect(url_for('schedule_fc'))
    
    db.session.delete(schedule)
    db.session.commit()
    flash("스케줄이 삭제되었습니다.", 'success')
    return redirect(url_for('schedule_fc'))


@app.route('/clean/edit/<int:cid>', methods=['GET', 'POST'])
@login_required
def edit_clean(cid):
    plan = CleaningPlan.query.get_or_404(cid)
    if not current_user.is_admin() and plan.user_id != current_user.id:
        flash("수정 권한이 없습니다.", 'error')
        return redirect(url_for('clean'))

    if request.method == 'POST':
        plan.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        plan.plan = request.form['plan']
        plan.team = request.form['team']
        db.session.commit()
        flash("청소 계획이 수정되었습니다.", 'success')
        return redirect(url_for('clean'))
    
    return render_template('edit_clean.html', plan=plan)

@app.route('/clean/delete/<int:cid>')
@login_required
def delete_clean(cid):
    plan = CleaningPlan.query.get_or_404(cid)
    if not current_user.is_admin() and plan.user_id != current_user.id:
        flash("삭제 권한이 없습니다.", 'error')
        return redirect(url_for('clean'))
    
    db.session.delete(plan)
    db.session.commit()
    flash("청소 계획이 삭제되었습니다.", 'success')
    return redirect(url_for('clean'))


@app.route('/api/schedule')
@login_required
def api_schedule():
    start = request.args.get('start')
    end = request.args.get('end')
    
    schedules = Schedule.query.filter(Schedule.date.between(start, end)).all()
    
    user_colors = {}
    
    def get_user_color(user_id):
        # 유저별로 고정된 색상을 반환 (간단한 예시)
        if user_id not in user_colors:
            # 해시를 이용해 유저별 색상 생성
            hue = (hash(str(user_id)) % 360)
            user_colors[user_id] = f'hsl({hue}, 70%, 50%)'
        return user_colors[user_id]

    events = []
    for s in schedules:
        events.append({
            'title': f"{s.user.username} - {s.category}",
            'start': f"{s.date.isoformat()}T{s.start_time.isoformat()}",
            'end': f"{s.date.isoformat()}T{s.end_time.isoformat()}",
            'description': s.memo or '',
            'id': s.id,
            'color': get_user_color(s.user_id)
        })
    return jsonify(events)

@app.route('/api/schedule', methods=['POST'])
@login_required
def api_add_schedule():
    data = request.json
    try:
        new_schedule = Schedule(
            user_id=current_user.id, # 본인 스케줄만 추가
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            start_time=datetime.strptime(data['start_time'], '%H:%M').time(),
            end_time=datetime.strptime(data['end_time'], '%H:%M').time(),
            category=data['category'],
            memo=data.get('memo')
        )
        db.session.add(new_schedule)
        db.session.commit()
        return jsonify({'message': '스케줄 추가 성공', 'id': new_schedule.id}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@app.route('/api/schedule/<int:sid>', methods=['PUT'])
@login_required
def api_edit_schedule(sid):
    schedule = Schedule.query.get_or_404(sid)
    if schedule.user_id != current_user.id:
        return jsonify({'message': '권한 없음'}), 403
    
    data = request.json
    try:
        schedule.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        schedule.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        schedule.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        schedule.category = data['category']
        schedule.memo = data.get('memo')
        db.session.commit()
        return jsonify({'message': '스케줄 수정 성공'})
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@app.route('/api/schedule/<int:sid>', methods=['DELETE'])
@login_required
def api_delete_schedule(sid):
    schedule = Schedule.query.get_or_404(sid)
    if schedule.user_id != current_user.id:
        return jsonify({'message': '권한 없음'}), 403
    
    db.session.delete(schedule)
    db.session.commit()
    return jsonify({'message': '스케줄 삭제 성공'})


@app.cli.command('create-admin')
@click.argument('username')
@click.argument('password')
def create_admin(username, password):
    """Creates a new admin user."""
    user = User(username=username, status='approved', role='admin')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print(f'Admin user {username} created successfully.')


@app.context_processor
def inject_notifications():
    if current_user.is_authenticated:
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return dict(unread_notification_count=unread_count)
    return dict(unread_notification_count=0)

@app.route('/notifications')
@login_required
def notifications():
    # 현재 로그인한 사용자의 모든 알림을 최신순으로 가져옵니다.
    user_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    
    # 읽지 않은 알림을 읽음 처리합니다.
    unread_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False)
    for notif in unread_notifications:
        notif.is_read = True
    db.session.commit()
    
    return render_template('notifications.html', notifications=user_notifications)


@app.route('/notifications/count')
@login_required
def unread_notification_count():
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})


@app.route('/admin/statistics')
@login_required
def admin_statistics():
    return render_template('admin_statistics.html')

@app.route('/admin/reports')
@login_required
def admin_reports():
    page = request.args.get('page', 1, type=int)
    reports = Report.query.order_by(Report.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('admin/reports.html', reports=reports)


@app.route('/admin/reports/review/<int:report_id>', methods=['POST'])
@login_required
def admin_report_review(report_id):
    if not current_user.is_admin():
        return jsonify({'error': '관리자 권한이 필요합니다.'}), 403
        
    report = Report.query.get_or_404(report_id)
    data = request.get_json()
    
    report.status = data.get('status', report.status)
    report.admin_comment = data.get('admin_comment', report.admin_comment)
    report.reviewed_at = datetime.utcnow()
    report.reviewed_by = current_user.id
    
    db.session.commit()
    
    return jsonify({'message': '신고가 성공적으로 처리되었습니다.'})

if __name__ == '__main__':
    app.run(debug=True) 