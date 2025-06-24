from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
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
    # In a real app, you'd log the error
    return render_template('errors/500.html'), 500

# --- Routes ---
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
    
    # 기본값 설정
    selected_user_id = request.args.get('user_id', type=int)
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    page = request.args.get('page', 1, type=int)
    
    # 사용자 목록
    users = User.query.all()
    
    # 출근 기록 조회 (간단한 예시)
    attendances = []
    total_work_hours = 0.0
    
    # 페이지네이션 객체 생성 (간단한 예시)
    class Pagination:
        def __init__(self, page, per_page, total, items):
            self.page = page
            self.per_page = per_page
            self.total = total
            self.items = items
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1 if page > 1 else None
            self.next_num = page + 1 if page < self.pages else None
        
        def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
            last = 0
            for num in range(1, self.pages + 1):
                if (num <= left_edge or 
                    (num > self.page - left_current - 1 and 
                     num < self.page + right_current) or 
                    num > self.pages - right_edge):
                    if last + 1 != num:
                        yield None
                    yield num
                    last = num
    
    pagination = Pagination(page, 20, len(attendances), attendances)
    
    return render_template('admin/attendances.html', 
                         users=users, 
                         attendances=attendances,
                         total_work_hours=total_work_hours,
                         selected_user_id=selected_user_id,
                         start_date=start_date,
                         end_date=end_date,
                         pagination=pagination)

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

@app.route('/admin/users/approve/<int:user_id>', methods=['POST'])
@login_required
def approve_user(user_id):
    if not current_user.is_admin(): return redirect(url_for('index'))
    
    user = User.query.get(user_id)
    if user:
        user.status = 'approved'
        db.session.commit()
        flash(f'{user.username} 사용자가 승인되었습니다.', 'success')
    else:
        flash('사용자를 찾을 수 없습니다.', 'error')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/users/reject/<int:user_id>', methods=['POST'])
@login_required
def reject_user(user_id):
    if not current_user.is_admin(): return redirect(url_for('index'))
    
    user = User.query.get(user_id)
    if user:
        user.status = 'rejected'
        db.session.commit()
        flash(f'{user.username} 사용자가 거절되었습니다.', 'success')
    else:
        flash('사용자를 찾을 수 없습니다.', 'error')
    
    return redirect(url_for('admin_users'))

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
    reason = request.form.get('reason', '')  # 거절 사유
    
    if action in ['승인', '거절']:
        schedule.status = action
        db.session.commit()
        
        # 알림 발송
        if action == '승인':
            content = f"{schedule.date.strftime('%m월 %d일')} 교대 신청이 승인되었습니다."
            link = "/swap_manage"
            send_notification_enhanced(schedule.user_id, content, "교대", link)
        else:
            content = f"{schedule.date.strftime('%m월 %d일')} 교대 신청이 거절되었습니다."
            if reason:
                content += f" 사유: {reason}"
            link = "/swap_manage"
            send_notification_enhanced(schedule.user_id, content, "교대", link)
        
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
    # 제안해주신 내용에 맞춰 개선된 알림센터
    try:
        # 필터 처리
        category = request.args.get('category', '')
        is_read = request.args.get('is_read', '')
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # 기본 쿼리
        query = Notification.query.filter_by(user_id=current_user.id)
        
        # 카테고리 필터
        if category:
            query = query.filter_by(category=category)
        
        # 읽음/안읽음 필터
        if is_read == '0':
            query = query.filter_by(is_read=False)
        elif is_read == '1':
            query = query.filter_by(is_read=True)
        
        # 정렬 (최신순)
        query = query.order_by(Notification.created_at.desc())
        
        # 페이징
        notifications = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 카테고리별 통계
        category_stats = db.session.query(
            Notification.category,
            db.func.count(Notification.id).label('total'),
            db.func.sum(db.case((Notification.is_read == False, 1), else_=0)).label('unread')
        ).filter_by(user_id=current_user.id).group_by(Notification.category).all()
        
        # 전체 통계
        total_notifications = Notification.query.filter_by(user_id=current_user.id).count()
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        
        return render_template('notifications.html', 
                             notifications=notifications,
                             category_stats=category_stats,
                             total_notifications=total_notifications,
                             unread_count=unread_count,
                             current_category=category,
                             current_is_read=is_read)
                             
    except Exception as e:
        flash('알림센터 로딩 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/notifications/mark_read/<int:notification_id>')
@login_required
def mark_notification_read(notification_id):
    """알림 읽음 처리"""
    try:
        notification = Notification.query.filter_by(
            id=notification_id, user_id=current_user.id
        ).first_or_404()
        
        notification.is_read = True
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/notifications/mark_all_read')
@login_required
def mark_all_notifications_read():
    """모든 알림 읽음 처리"""
    try:
        Notification.query.filter_by(
            user_id=current_user.id, is_read=False
        ).update({'is_read': True})
        db.session.commit()
        
        flash('모든 알림을 읽음 처리했습니다.', 'success')
        
    except Exception as e:
        flash('알림 처리 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('notifications'))

@app.route('/admin/notifications/center')
@login_required
def admin_notification_center():
    """관리자 알림센터 - 모든 사용자 알림 관리"""
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('dashboard'))
        
    try:
        # 필터 파라미터
        category = request.args.get('category', '')
        is_read = request.args.get('is_read', '')
        user_id = request.args.get('user_id', '', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = 30
        
        # 기본 쿼리 (관리자는 모든 알림 조회 가능)
        query = Notification.query.join(User)
        
        # 카테고리 필터
        if category:
            query = query.filter_by(category=category)
        
        # 읽음/안읽음 필터
        if is_read == '0':
            query = query.filter_by(is_read=False)
        elif is_read == '1':
            query = query.filter_by(is_read=True)
        
        # 사용자 필터
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        # 정렬 (최신순)
        query = query.order_by(Notification.created_at.desc())
        
        # 페이징
        notifications = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 카테고리별 통계
        category_stats = db.session.query(
            Notification.category,
            db.func.count(Notification.id).label('total'),
            db.func.sum(db.case((Notification.is_read == False, 1), else_=0)).label('unread')
        ).group_by(Notification.category).all()
        
        # 사용자별 통계
        user_stats = db.session.query(
            User.username,
            User.name,
            db.func.count(Notification.id).label('total'),
            db.func.sum(db.case((Notification.is_read == False, 1), else_=0)).label('unread')
        ).join(Notification).group_by(User.id, User.username, User.name).all()
        
        # 전체 통계
        total_notifications = Notification.query.count()
        unread_count = Notification.query.filter_by(is_read=False).count()
        
        # 사용자 목록 (필터용)
        users = User.query.filter_by(status='approved').all()
        
        return render_template('admin/notifications.html', 
                             notifications=notifications,
                             category_stats=category_stats,
                             user_stats=user_stats,
                             total_notifications=total_notifications,
                             unread_count=unread_count,
                             users=users,
                             current_category=category,
                             current_is_read=is_read,
                             current_user_id=user_id)
                             
    except Exception as e:
        flash('관리자 알림센터 로딩 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/notifications/delete/<int:notification_id>')
@login_required
def delete_notification(notification_id):
    """알림 삭제 (관리자만)"""
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('dashboard'))
        
    try:
        notification = Notification.query.get_or_404(notification_id)
        db.session.delete(notification)
        db.session.commit()
        
        flash('알림이 삭제되었습니다.', 'success')
        
    except Exception as e:
        flash('알림 삭제 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('admin_notification_center'))

@app.route('/admin/notifications/bulk_delete', methods=['POST'])
@login_required
def bulk_delete_notifications():
    """알림 일괄 삭제 (관리자만)"""
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('dashboard'))
        
    try:
        notification_ids = request.form.getlist('notification_ids')
        
        if notification_ids:
            Notification.query.filter(Notification.id.in_(notification_ids)).delete(synchronize_session=False)
            db.session.commit()
            flash(f'{len(notification_ids)}개의 알림이 삭제되었습니다.', 'success')
        else:
            flash('삭제할 알림을 선택해주세요.', 'error')
        
    except Exception as e:
        flash('알림 일괄 삭제 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('admin_notification_center'))

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
    if not current_user.is_admin(): return redirect(url_for('index'))
    return "준비중인 페이지입니다. (신고 처리)"

# === 새로운 관리 기능들 ===

@app.route('/user_manage', methods=['GET', 'POST'])
@login_required
def user_manage():
    if not current_user.is_admin(): 
        flash('관리자만 접근할 수 있습니다.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        role = request.form['role']
        
        # 중복 사용자명 확인
        if User.query.filter_by(username=username).first():
            flash('이미 존재하는 사용자명입니다.', 'error')
        else:
            # 임시 비밀번호 생성 (실제로는 이메일로 전송)
            temp_password = 'temp123456'
            user = User(username=username, role=role, status='approved')
            user.set_password(temp_password)
            db.session.add(user)
            db.session.commit()
            flash(f'{username} 직원이 등록되었습니다. 임시 비밀번호: {temp_password}', 'success')
    
    users = User.query.all()
    return render_template('user_manage.html', users=users)

@app.route('/schedule_manage', methods=['GET', 'POST'])
@login_required
def schedule_manage():
    if not (current_user.is_admin() or current_user.is_manager()):
        flash('권한이 없습니다.', 'error')
        return redirect(url_for('index'))
    
    employees = User.query.filter(User.role=='employee').all()
    
    if request.method == 'POST':
        user_id = int(request.form['user_id'])
        date_str = request.form['date']
        start_time_str = request.form['start_time']
        end_time_str = request.form['end_time']
        category = request.form['category']
        memo = request.form['memo']
        
        try:
            date_obj = date.fromisoformat(date_str)
            start_time_obj = datetime.strptime(start_time_str, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time_str, '%H:%M').time()
            
            schedule = Schedule(
                user_id=user_id,
                date=date_obj,
                start_time=start_time_obj,
                end_time=end_time_obj,
                category=category,
                memo=memo,
                status='승인'
            )
            db.session.add(schedule)
            db.session.commit()
            flash('스케줄이 등록되었습니다.', 'success')
        except Exception as e:
            flash(f'오류가 발생했습니다: {e}', 'error')
    
    schedules = Schedule.query.order_by(Schedule.date.desc()).all()
    return render_template('schedule_manage.html', schedules=schedules, employees=employees)

@app.route('/order_manage', methods=['GET', 'POST'])
@login_required
def order_manage():
    if not (current_user.is_admin() or current_user.is_manager()):
        flash('권한이 없습니다.', 'error')
        return redirect(url_for('index'))
    
    users = User.query.all()
    
    if request.method == 'POST':
        item = request.form['item']
        quantity = int(request.form['quantity'])
        order_date_str = request.form['order_date']
        ordered_by = int(request.form['ordered_by'])
        
        try:
            order_date_obj = date.fromisoformat(order_date_str)
            order = Order(
                item=item,
                quantity=quantity,
                order_date=order_date_obj,
                ordered_by=ordered_by
            )
            db.session.add(order)
            db.session.commit()
            flash('발주가 등록되었습니다.', 'success')
        except Exception as e:
            flash(f'오류가 발생했습니다: {e}', 'error')
    
    orders = Order.query.order_by(Order.order_date.desc()).all()
    return render_template('order_manage.html', orders=orders, users=users)

@app.route('/clean_manage', methods=['GET', 'POST'])
@login_required
def clean_manage():
    if not (current_user.is_admin() or current_user.is_manager()):
        flash('권한이 없습니다.', 'error')
        return redirect(url_for('index'))
    
    employees = User.query.filter(User.role=='employee').all()
    
    if request.method == 'POST':
        date_str = request.form['date']
        plan = request.form['plan']
        team = request.form['team']
        manager_id = int(request.form['manager_id'])
        
        try:
            date_obj = date.fromisoformat(date_str)
            cleaning = CleaningPlan(
                date=date_obj,
                plan=plan,
                team=team,
                manager_id=manager_id
            )
            db.session.add(cleaning)
            db.session.commit()
            flash('청소 계획이 등록되었습니다.', 'success')
        except Exception as e:
            flash(f'오류가 발생했습니다: {e}', 'error')
    
    cleanings = CleaningPlan.query.order_by(CleaningPlan.date.desc()).all()
    return render_template('clean_manage.html', cleanings=cleanings, employees=employees)

@app.route('/swap_manage', methods=['GET', 'POST'])
@login_required
def swap_manage():
    swaps = Schedule.query.filter_by(category='교대').order_by(Schedule.date.desc()).all()
    employees = User.query.filter_by(role='employee').all()
    if request.method == 'POST' and current_user.role in ['admin', 'manager']:
        sid = int(request.form['sid'])
        status = request.form['status']
        sch = Schedule.query.get(sid)
        sch.status = status
        db.session.commit()
    return render_template('swap_manage.html', swaps=swaps, employees=employees)

@app.route('/clean_report')
@login_required
def clean_report():
    from sqlalchemy import func
    counts = db.session.query(
        CleaningPlan.team,
        CleaningPlan.date,
        func.count(CleaningPlan.id)
    ).group_by(CleaningPlan.team, CleaningPlan.date).all()
    return render_template('clean_report.html', counts=counts)

@app.route('/stat_report')
@login_required
def stat_report():
    from sqlalchemy import func
    # 직원별 근무일수
    workdays = db.session.query(
        Schedule.user_id,
        func.count(Schedule.id)
    ).filter(Schedule.category=='근무').group_by(Schedule.user_id).all()
    # 직원별 발주건수
    orders = db.session.query(
        Order.ordered_by,
        func.count(Order.id)
    ).group_by(Order.ordered_by).all()
    # 청소 담당별
    cleans = db.session.query(
        CleaningPlan.manager_id,
        func.count(CleaningPlan.id)
    ).group_by(CleaningPlan.manager_id).all()
    users = {u.id:u.username for u in User.query.all()}
    return render_template('stat_report.html', workdays=workdays, orders=orders, cleans=cleans, users=users)

@app.route('/order_detail/<int:oid>', methods=['GET', 'POST'])
@login_required
def order_detail(oid):
    order = Order.query.get_or_404(oid)
    
    if request.method == 'POST' and current_user.role in ['admin', 'manager']:
        old_status = order.status
        order.status = request.form['status']
        order.detail = request.form.get('detail', order.detail)
        db.session.commit()
        
        # 상태 변경 시 알림 발송
        if old_status != order.status:
            if order.status == 'approved':
                # 발주 승인 시 알림 발송
                send_order_approval_notification(order)
            elif order.status == 'rejected':
                from utils.notify import send_notification_enhanced
                content = f"발주 '{order.item}' ({order.quantity}개)가 거절되었습니다."
                link = f"/order_detail/{order.id}"
                send_notification_enhanced(order.ordered_by, content, "발주", link)
            elif order.status == 'delivered':
                from utils.notify import send_notification_enhanced
                content = f"발주 '{order.item}' ({order.quantity}개)가 배송되었습니다."
                link = f"/order_detail/{order.id}"
                send_notification_enhanced(order.ordered_by, content, "발주", link)
        
        flash('발주 상태가 업데이트되었습니다.', 'success')
        return redirect(url_for('order_detail', oid=oid))
    
    return render_template('order_detail.html', order=order)

def send_order_approval_notification(order):
    """발주 승인 시 담당 매니저와 발주자 모두에게 알림"""
    try:
        from utils.notify import send_notification_enhanced
        
        # 발주자에게 알림
        send_notification_enhanced(
            order.ordered_by, 
            f"발주 '{order.item}' ({order.quantity}개)가 승인되었습니다.", 
            "발주", 
            f"/order_detail/{order.id}"
        )
        
        # 매니저(관리자) 전체에게도 알림
        managers = User.query.filter(User.role.in_(['admin', 'manager'])).all()
        for manager in managers:
            if manager.id != order.ordered_by:  # 발주자와 다른 경우만
                # 발주자 정보 조회
                order_user = User.query.get(order.ordered_by)
                username = order_user.username if order_user else "알 수 없음"
                send_notification_enhanced(
                    manager.id,
                    f"발주 '{order.item}' ({order.quantity}개)가 승인 처리되었습니다. (발주자: {username})",
                    "발주",
                    f"/order_detail/{order.id}"
                )
        
        return True
    except Exception as e:
        print(f"발주 승인 알림 발송 실패: {e}")
        return False

@app.route('/api/new_notifications')
@login_required
def api_new_notifications():
    """새로운 알림 수 API"""
    try:
        count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return jsonify({'count': count})
    except Exception as e:
        return jsonify({'count': 0, 'error': str(e)})

@app.route('/notifications/mark_read', methods=['POST'])
@login_required
def mark_read():
    """선택한 알림 읽음 처리"""
    try:
        ids = request.form.getlist('noti_ids')
        for nid in ids:
            notification = Notification.query.filter_by(
                id=int(nid), user_id=current_user.id
            ).first()
            if notification:
                notification.is_read = True
        
        db.session.commit()
        flash(f'{len(ids)}개의 알림을 읽음 처리했습니다.', 'success')
        
    except Exception as e:
        flash('알림 처리 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('notifications'))

@app.route('/admin/all_notifications')
@login_required
def all_notifications():
    """관리자용 전체 알림 조회"""
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('index'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    notifications = Notification.query.order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/all_notifications.html', notifications=notifications)

@app.route('/admin/send_notification', methods=['GET', 'POST'])
@login_required
def admin_send_notification():
    """관리자용 알림 발송"""
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('index'))
    
    users = User.query.filter_by(role='employee').all()
    
    if request.method == 'POST':
        try:
            user_id = int(request.form['user_id'])
            content = request.form['content'].strip()
            category = request.form['category']
            
            if not content:
                flash('알림 내용을 입력해주세요.', 'error')
            else:
                send_notification_enhanced(user_id, content, category)
                flash('알림이 성공적으로 발송되었습니다.', 'success')
                return redirect(url_for('admin_send_notification'))
                
        except Exception as e:
            flash(f'알림 발송 중 오류가 발생했습니다: {e}', 'error')
    
    return render_template('admin/send_notification.html', users=users)

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
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
    # In a real app, you'd log the error
    return render_template('errors/500.html'), 500

# --- Routes ---
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
    
    # 기본값 설정
    selected_user_id = request.args.get('user_id', type=int)
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    page = request.args.get('page', 1, type=int)
    
    # 사용자 목록
    users = User.query.all()
    
    # 출근 기록 조회 (간단한 예시)
    attendances = []
    total_work_hours = 0.0
    
    # 페이지네이션 객체 생성 (간단한 예시)
    class Pagination:
        def __init__(self, page, per_page, total, items):
            self.page = page
            self.per_page = per_page
            self.total = total
            self.items = items
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1 if page > 1 else None
            self.next_num = page + 1 if page < self.pages else None
        
        def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
            last = 0
            for num in range(1, self.pages + 1):
                if (num <= left_edge or 
                    (num > self.page - left_current - 1 and 
                     num < self.page + right_current) or 
                    num > self.pages - right_edge):
                    if last + 1 != num:
                        yield None
                    yield num
                    last = num
    
    pagination = Pagination(page, 20, len(attendances), attendances)
    
    return render_template('admin/attendances.html', 
                         users=users, 
                         attendances=attendances,
                         total_work_hours=total_work_hours,
                         selected_user_id=selected_user_id,
                         start_date=start_date,
                         end_date=end_date,
                         pagination=pagination)

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

@app.route('/admin/users/approve/<int:user_id>', methods=['POST'])
@login_required
def approve_user(user_id):
    if not current_user.is_admin(): return redirect(url_for('index'))
    
    user = User.query.get(user_id)
    if user:
        user.status = 'approved'
        db.session.commit()
        flash(f'{user.username} 사용자가 승인되었습니다.', 'success')
    else:
        flash('사용자를 찾을 수 없습니다.', 'error')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/users/reject/<int:user_id>', methods=['POST'])
@login_required
def reject_user(user_id):
    if not current_user.is_admin(): return redirect(url_for('index'))
    
    user = User.query.get(user_id)
    if user:
        user.status = 'rejected'
        db.session.commit()
        flash(f'{user.username} 사용자가 거절되었습니다.', 'success')
    else:
        flash('사용자를 찾을 수 없습니다.', 'error')
    
    return redirect(url_for('admin_users'))

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
    reason = request.form.get('reason', '')  # 거절 사유
    
    if action in ['승인', '거절']:
        schedule.status = action
        db.session.commit()
        
        # 알림 발송
        if action == '승인':
            content = f"{schedule.date.strftime('%m월 %d일')} 교대 신청이 승인되었습니다."
            link = "/swap_manage"
            send_notification_enhanced(schedule.user_id, content, "교대", link)
        else:
            content = f"{schedule.date.strftime('%m월 %d일')} 교대 신청이 거절되었습니다."
            if reason:
                content += f" 사유: {reason}"
            link = "/swap_manage"
            send_notification_enhanced(schedule.user_id, content, "교대", link)
        
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
    # 제안해주신 내용에 맞춰 개선된 알림센터
    try:
        # 필터 처리
        category = request.args.get('category', '')
        is_read = request.args.get('is_read', '')
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # 기본 쿼리
        query = Notification.query.filter_by(user_id=current_user.id)
        
        # 카테고리 필터
        if category:
            query = query.filter_by(category=category)
        
        # 읽음/안읽음 필터
        if is_read == '0':
            query = query.filter_by(is_read=False)
        elif is_read == '1':
            query = query.filter_by(is_read=True)
        
        # 정렬 (최신순)
        query = query.order_by(Notification.created_at.desc())
        
        # 페이징
        notifications = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 카테고리별 통계
        category_stats = db.session.query(
            Notification.category,
            db.func.count(Notification.id).label('total'),
            db.func.sum(db.case((Notification.is_read == False, 1), else_=0)).label('unread')
        ).filter_by(user_id=current_user.id).group_by(Notification.category).all()
        
        # 전체 통계
        total_notifications = Notification.query.filter_by(user_id=current_user.id).count()
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        
        return render_template('notifications.html', 
                             notifications=notifications,
                             category_stats=category_stats,
                             total_notifications=total_notifications,
                             unread_count=unread_count,
                             current_category=category,
                             current_is_read=is_read)
                             
    except Exception as e:
        flash('알림센터 로딩 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/notifications/mark_read/<int:notification_id>')
@login_required
def mark_notification_read(notification_id):
    """알림 읽음 처리"""
    try:
        notification = Notification.query.filter_by(
            id=notification_id, user_id=current_user.id
        ).first_or_404()
        
        notification.is_read = True
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/notifications/mark_all_read')
@login_required
def mark_all_notifications_read():
    """모든 알림 읽음 처리"""
    try:
        Notification.query.filter_by(
            user_id=current_user.id, is_read=False
        ).update({'is_read': True})
        db.session.commit()
        
        flash('모든 알림을 읽음 처리했습니다.', 'success')
        
    except Exception as e:
        flash('알림 처리 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('notifications'))

@app.route('/admin/notifications/center')
@login_required
def admin_notification_center():
    """관리자 알림센터 - 모든 사용자 알림 관리"""
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('dashboard'))
        
    try:
        # 필터 파라미터
        category = request.args.get('category', '')
        is_read = request.args.get('is_read', '')
        user_id = request.args.get('user_id', '', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = 30
        
        # 기본 쿼리 (관리자는 모든 알림 조회 가능)
        query = Notification.query.join(User)
        
        # 카테고리 필터
        if category:
            query = query.filter_by(category=category)
        
        # 읽음/안읽음 필터
        if is_read == '0':
            query = query.filter_by(is_read=False)
        elif is_read == '1':
            query = query.filter_by(is_read=True)
        
        # 사용자 필터
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        # 정렬 (최신순)
        query = query.order_by(Notification.created_at.desc())
        
        # 페이징
        notifications = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 카테고리별 통계
        category_stats = db.session.query(
            Notification.category,
            db.func.count(Notification.id).label('total'),
            db.func.sum(db.case((Notification.is_read == False, 1), else_=0)).label('unread')
        ).group_by(Notification.category).all()
        
        # 사용자별 통계
        user_stats = db.session.query(
            User.username,
            User.name,
            db.func.count(Notification.id).label('total'),
            db.func.sum(db.case((Notification.is_read == False, 1), else_=0)).label('unread')
        ).join(Notification).group_by(User.id, User.username, User.name).all()
        
        # 전체 통계
        total_notifications = Notification.query.count()
        unread_count = Notification.query.filter_by(is_read=False).count()
        
        # 사용자 목록 (필터용)
        users = User.query.filter_by(status='approved').all()
        
        return render_template('admin/notifications.html', 
                             notifications=notifications,
                             category_stats=category_stats,
                             user_stats=user_stats,
                             total_notifications=total_notifications,
                             unread_count=unread_count,
                             users=users,
                             current_category=category,
                             current_is_read=is_read,
                             current_user_id=user_id)
                             
    except Exception as e:
        flash('관리자 알림센터 로딩 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/notifications/delete/<int:notification_id>')
@login_required
def delete_notification(notification_id):
    """알림 삭제 (관리자만)"""
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('dashboard'))
        
    try:
        notification = Notification.query.get_or_404(notification_id)
        db.session.delete(notification)
        db.session.commit()
        
        flash('알림이 삭제되었습니다.', 'success')
        
    except Exception as e:
        flash('알림 삭제 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('admin_notification_center'))

@app.route('/admin/notifications/bulk_delete', methods=['POST'])
@login_required
def bulk_delete_notifications():
    """알림 일괄 삭제 (관리자만)"""
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('dashboard'))
        
    try:
        notification_ids = request.form.getlist('notification_ids')
        
        if notification_ids:
            Notification.query.filter(Notification.id.in_(notification_ids)).delete(synchronize_session=False)
            db.session.commit()
            flash(f'{len(notification_ids)}개의 알림이 삭제되었습니다.', 'success')
        else:
            flash('삭제할 알림을 선택해주세요.', 'error')
        
    except Exception as e:
        flash('알림 일괄 삭제 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('admin_notification_center'))

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
    if not current_user.is_admin(): return redirect(url_for('index'))
    return "준비중인 페이지입니다. (신고 처리)"

# === 새로운 관리 기능들 ===

@app.route('/user_manage', methods=['GET', 'POST'])
@login_required
def user_manage():
    if not current_user.is_admin(): 
        flash('관리자만 접근할 수 있습니다.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        role = request.form['role']
        
        # 중복 사용자명 확인
        if User.query.filter_by(username=username).first():
            flash('이미 존재하는 사용자명입니다.', 'error')
        else:
            # 임시 비밀번호 생성 (실제로는 이메일로 전송)
            temp_password = 'temp123456'
            user = User(username=username, role=role, status='approved')
            user.set_password(temp_password)
            db.session.add(user)
            db.session.commit()
            flash(f'{username} 직원이 등록되었습니다. 임시 비밀번호: {temp_password}', 'success')
    
    users = User.query.all()
    return render_template('user_manage.html', users=users)

@app.route('/schedule_manage', methods=['GET', 'POST'])
@login_required
def schedule_manage():
    if not (current_user.is_admin() or current_user.is_manager()):
        flash('권한이 없습니다.', 'error')
        return redirect(url_for('index'))
    
    employees = User.query.filter(User.role=='employee').all()
    
    if request.method == 'POST':
        user_id = int(request.form['user_id'])
        date_str = request.form['date']
        start_time_str = request.form['start_time']
        end_time_str = request.form['end_time']
        category = request.form['category']
        memo = request.form['memo']
        
        try:
            date_obj = date.fromisoformat(date_str)
            start_time_obj = datetime.strptime(start_time_str, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time_str, '%H:%M').time()
            
            schedule = Schedule(
                user_id=user_id,
                date=date_obj,
                start_time=start_time_obj,
                end_time=end_time_obj,
                category=category,
                memo=memo,
                status='승인'
            )
            db.session.add(schedule)
            db.session.commit()
            flash('스케줄이 등록되었습니다.', 'success')
        except Exception as e:
            flash(f'오류가 발생했습니다: {e}', 'error')
    
    schedules = Schedule.query.order_by(Schedule.date.desc()).all()
    return render_template('schedule_manage.html', schedules=schedules, employees=employees)

@app.route('/order_manage', methods=['GET', 'POST'])
@login_required
def order_manage():
    if not (current_user.is_admin() or current_user.is_manager()):
        flash('권한이 없습니다.', 'error')
        return redirect(url_for('index'))
    
    users = User.query.all()
    
    if request.method == 'POST':
        item = request.form['item']
        quantity = int(request.form['quantity'])
        order_date_str = request.form['order_date']
        ordered_by = int(request.form['ordered_by'])
        
        try:
            order_date_obj = date.fromisoformat(order_date_str)
            order = Order(
                item=item,
                quantity=quantity,
                order_date=order_date_obj,
                ordered_by=ordered_by
            )
            db.session.add(order)
            db.session.commit()
            flash('발주가 등록되었습니다.', 'success')
        except Exception as e:
            flash(f'오류가 발생했습니다: {e}', 'error')
    
    orders = Order.query.order_by(Order.order_date.desc()).all()
    return render_template('order_manage.html', orders=orders, users=users)

@app.route('/clean_manage', methods=['GET', 'POST'])
@login_required
def clean_manage():
    if not (current_user.is_admin() or current_user.is_manager()):
        flash('권한이 없습니다.', 'error')
        return redirect(url_for('index'))
    
    employees = User.query.filter(User.role=='employee').all()
    
    if request.method == 'POST':
        date_str = request.form['date']
        plan = request.form['plan']
        team = request.form['team']
        manager_id = int(request.form['manager_id'])
        
        try:
            date_obj = date.fromisoformat(date_str)
            cleaning = CleaningPlan(
                date=date_obj,
                plan=plan,
                team=team,
                manager_id=manager_id
            )
            db.session.add(cleaning)
            db.session.commit()
            flash('청소 계획이 등록되었습니다.', 'success')
        except Exception as e:
            flash(f'오류가 발생했습니다: {e}', 'error')
    
    cleanings = CleaningPlan.query.order_by(CleaningPlan.date.desc()).all()
    return render_template('clean_manage.html', cleanings=cleanings, employees=employees)

@app.route('/swap_manage', methods=['GET', 'POST'])
@login_required
def swap_manage():
    swaps = Schedule.query.filter_by(category='교대').order_by(Schedule.date.desc()).all()
    employees = User.query.filter_by(role='employee').all()
    if request.method == 'POST' and current_user.role in ['admin', 'manager']:
        sid = int(request.form['sid'])
        status = request.form['status']
        sch = Schedule.query.get(sid)
        sch.status = status
        db.session.commit()
    return render_template('swap_manage.html', swaps=swaps, employees=employees)

@app.route('/clean_report')
@login_required
def clean_report():
    from sqlalchemy import func
    counts = db.session.query(
        CleaningPlan.team,
        CleaningPlan.date,
        func.count(CleaningPlan.id)
    ).group_by(CleaningPlan.team, CleaningPlan.date).all()
    return render_template('clean_report.html', counts=counts)

@app.route('/stat_report')
@login_required
def stat_report():
    from sqlalchemy import func
    # 직원별 근무일수
    workdays = db.session.query(
        Schedule.user_id,
        func.count(Schedule.id)
    ).filter(Schedule.category=='근무').group_by(Schedule.user_id).all()
    # 직원별 발주건수
    orders = db.session.query(
        Order.ordered_by,
        func.count(Order.id)
    ).group_by(Order.ordered_by).all()
    # 청소 담당별
    cleans = db.session.query(
        CleaningPlan.manager_id,
        func.count(CleaningPlan.id)
    ).group_by(CleaningPlan.manager_id).all()
    users = {u.id:u.username for u in User.query.all()}
    return render_template('stat_report.html', workdays=workdays, orders=orders, cleans=cleans, users=users)

@app.route('/order_detail/<int:oid>', methods=['GET', 'POST'])
@login_required
def order_detail(oid):
    order = Order.query.get_or_404(oid)
    
    if request.method == 'POST' and current_user.role in ['admin', 'manager']:
        old_status = order.status
        order.status = request.form['status']
        order.detail = request.form.get('detail', order.detail)
        db.session.commit()
        
        # 상태 변경 시 알림 발송
        if old_status != order.status:
            if order.status == 'approved':
                # 발주 승인 시 알림 발송
                send_order_approval_notification(order)
            elif order.status == 'rejected':
                from utils.notify import send_notification_enhanced
                content = f"발주 '{order.item}' ({order.quantity}개)가 거절되었습니다."
                link = f"/order_detail/{order.id}"
                send_notification_enhanced(order.ordered_by, content, "발주", link)
            elif order.status == 'delivered':
                from utils.notify import send_notification_enhanced
                content = f"발주 '{order.item}' ({order.quantity}개)가 배송되었습니다."
                link = f"/order_detail/{order.id}"
                send_notification_enhanced(order.ordered_by, content, "발주", link)
        
        flash('발주 상태가 업데이트되었습니다.', 'success')
        return redirect(url_for('order_detail', oid=oid))
    
    return render_template('order_detail.html', order=order)

def send_order_approval_notification(order):
    """발주 승인 시 담당 매니저와 발주자 모두에게 알림"""
    try:
        from utils.notify import send_notification_enhanced
        
        # 발주자에게 알림
        send_notification_enhanced(
            order.ordered_by, 
            f"발주 '{order.item}' ({order.quantity}개)가 승인되었습니다.", 
            "발주", 
            f"/order_detail/{order.id}"
        )
        
        # 매니저(관리자) 전체에게도 알림
        managers = User.query.filter(User.role.in_(['admin', 'manager'])).all()
        for manager in managers:
            if manager.id != order.ordered_by:  # 발주자와 다른 경우만
                send_notification_enhanced(
                    manager.id,
                    f"발주 '{order.item}' ({order.quantity}개)가 승인 처리되었습니다. (발주자: {order.user.username})",
                    "발주",
                    f"/order_detail/{order.id}"
                )
        
        return True
    except Exception as e:
        print(f"발주 승인 알림 발송 실패: {e}")
        return False

@app.route('/api/new_notifications')
@login_required
def api_new_notifications():
    """새로운 알림 수 API"""
    try:
        count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return jsonify({'count': count})
    except Exception as e:
        return jsonify({'count': 0, 'error': str(e)})

@app.route('/notifications/mark_read', methods=['POST'])
@login_required
def mark_read():
    """선택한 알림 읽음 처리"""
    try:
        ids = request.form.getlist('noti_ids')
        for nid in ids:
            notification = Notification.query.filter_by(
                id=int(nid), user_id=current_user.id
            ).first()
            if notification:
                notification.is_read = True
        
        db.session.commit()
        flash(f'{len(ids)}개의 알림을 읽음 처리했습니다.', 'success')
        
    except Exception as e:
        flash('알림 처리 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('notifications'))

@app.route('/admin/all_notifications')
@login_required
def all_notifications():
    """관리자용 전체 알림 조회"""
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('index'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    notifications = Notification.query.order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/all_notifications.html', notifications=notifications)

@app.route('/admin/send_notification', methods=['GET', 'POST'])
@login_required
def admin_send_notification():
    """관리자용 알림 발송"""
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('index'))
    
    users = User.query.filter_by(role='employee').all()
    
    if request.method == 'POST':
        try:
            user_id = int(request.form['user_id'])
            content = request.form['content'].strip()
            category = request.form['category']
            
            if not content:
                flash('알림 내용을 입력해주세요.', 'error')
            else:
                send_notification_enhanced(user_id, content, category)
                flash('알림이 성공적으로 발송되었습니다.', 'success')
                return redirect(url_for('admin_send_notification'))
                
        except Exception as e:
            flash(f'알림 발송 중 오류가 발생했습니다: {e}', 'error')
    
    return render_template('admin/send_notification.html', users=users)

@app.route('/notifications/filtered')
@login_required
def notifications_filtered():
    """고급 필터링 알림 조회"""
    category = request.args.get('category', '')
    keyword = request.args.get('keyword', '')
    is_read = request.args.get('is_read', '')
    is_admin_only = request.args.get('is_admin_only', 'false')
    
    # 기본 쿼리 (권한에 따라)
    if current_user.is_admin():
        query = Notification.query
    else:
        query = Notification.query.filter(
            db.or_(
                Notification.user_id == current_user.id,
                Notification.is_admin_only == False
            )
        )
    
    # 카테고리 필터
    if category:
        query = query.filter(Notification.category == category)
    
    # 키워드 검색
    if keyword:
        query = query.filter(Notification.content.contains(keyword))
    
    # 읽음 상태 필터
    if is_read == 'true':
        query = query.filter(Notification.is_read == True)
    elif is_read == 'false':
        query = query.filter(Notification.is_read == False)
    
    # 관리자 전용 필터
    if is_admin_only == 'true' and current_user.is_admin():
        query = query.filter(Notification.is_admin_only == True)
    elif is_admin_only == 'false':
        query = query.filter(Notification.is_admin_only == False)
    
    notifications = query.order_by(Notification.created_at.desc()).all()
    
    return render_template('notifications_filtered.html', 
                         notifications=notifications,
                         category=category,
                         keyword=keyword,
                         is_read=is_read,
                         is_admin_only=is_admin_only)

@app.route('/notifications/advanced_search')
@login_required
def notifications_advanced_search():
    """고급 검색 페이지"""
    return render_template('notifications_advanced_search.html')

@app.route('/notifications/orders/approved')
@login_required
def order_approved_notifications():
    """발주 승인 알림만 필터링"""
    notis = Notification.query.filter_by(
        user_id=current_user.id,
        category='발주',
        is_read=False
    ).filter(Notification.content.contains('승인')).order_by(Notification.created_at.desc()).all()
    
    return render_template('noti_orders_approved.html', notis=notis)

@app.route('/admin/system_notifications')
@login_required
def admin_system_notifications():
    """관리자만 보는 시스템 알림"""
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('index'))
    
    notis = Notification.query.filter_by(is_admin_only=True).order_by(Notification.created_at.desc()).all()
    return render_template('admin/noti_system.html', notis=notis)

if __name__ == '__main__':
    app.run(debug=True) 