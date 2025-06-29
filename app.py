from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, date
from dateutil import parser as date_parser
import os
import click
from collections import defaultdict
from flask_migrate import Migrate
from sqlalchemy import func

from config import config_by_name
from extensions import db, migrate, login_manager, csrf, limiter, cache
from models import User, Schedule, CleaningPlan, Report, Notification, Notice, Order, FeedbackIssue, Branch

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
migrate = Migrate(app, db)
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
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
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
    
    # 매장 목록 데이터 생성 (실제로는 DB에서 불러옴)
    branch_list = []
    try:
        # 모든 사용자 중 매장 관리자와 직원들을 매장별로 그룹화
        managers = User.query.filter_by(role='manager').all()
        employees = User.query.filter_by(role='employee').all()
        
        # 임시 매장 데이터 (실제로는 Branch 모델에서 가져와야 함)
        temp_branches = [
            {'id': 1, 'name': '본점', 'manager_id': None},
            {'id': 2, 'name': '강남점', 'manager_id': None},
            {'id': 3, 'name': '홍대점', 'manager_id': None}
        ]
        
        for branch in temp_branches:
            # 해당 매장의 관리자 찾기
            manager = next((m for m in managers if m.branch_id == branch['id']), None)
            # 해당 매장의 직원들 찾기
            branch_employees = [e for e in employees if e.branch_id == branch['id']]
            
            branch_list.append({
                'id': branch['id'],
                'name': branch['name'],
                'manager_name': manager.username if manager else "-",
                'num_employees': len(branch_employees),
                'employees': branch_employees
            })
    except Exception as e:
        # 오류 발생 시 빈 리스트로 설정
        branch_list = []
    
    # 기본 통계 데이터
    avg_processing = db.session.query(func.avg(Order.processing_minutes)).scalar()
    exceed_count = db.session.query(Order).join(Branch).filter(
        Order.processing_minutes > Branch.processing_time_standard
    ).count()
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
        'recent': [],
        'branch_list': branch_list,
        'avg_processing': avg_processing or 0,
        'exceed_count': exceed_count,
    }
    return render_template('admin_dashboard.html', **context)

@app.route('/manager_dashboard/<int:branch_id>')
@login_required
def manager_dashboard(branch_id):
    """매장 관리자 전용 대시보드"""
    if not current_user.is_admin():
        flash('매장 관리자 권한이 필요합니다.')
        return redirect(url_for('dashboard'))
    
    # 실제 매장 정보, 직원 리스트 등 context에 추가
    try:
        # 해당 매장의 직원들 찾기
        employees = User.query.filter_by(branch_id=branch_id, role='employee').all()
        manager = User.query.filter_by(branch_id=branch_id, role='manager').first()
        
        context = {
            'branch_id': branch_id,
            'branch_name': f'매장 {branch_id}',
            'manager': manager,
            'employees': employees,
            'num_employees': len(employees)
        }
    except Exception as e:
        flash('매장 정보를 불러오는 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('manager_dashboard.html', **context)

@app.route('/employee_dashboard/<int:employee_id>')
@login_required
def employee_dashboard(employee_id):
    """직원 전용 업무 페이지"""
    try:
        emp = User.query.get_or_404(employee_id)
        
        # 권한 체크: 관리자 or 자기 자신만 접근
        if not (current_user.is_admin() or current_user.id == emp.id):
            flash('해당 직원 업무 접근 권한이 없습니다.')
            return redirect(url_for('dashboard'))
        
        context = {
            'employee': emp,
            'branch_name': f'매장 {emp.branch_id}' if emp.branch_id else '미지정'
        }
    except Exception as e:
        flash('직원 정보를 불러오는 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('employee_dashboard.html', **context)

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

@app.route('/notifications/count')
@login_required
def notifications_count():
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})

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

@app.route('/m/notifications')
def m_notifications():
    return render_template('mobile/m_notifications.html')

@app.route('/m/profile')
@login_required
def m_profile():
    return render_template('mobile/m_profile.html', user=current_user)

@app.route('/feedback/new', methods=['GET', 'POST'])
@login_required
def new_feedback():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        fb = FeedbackIssue(
            title=title,
            content=content,
            user_id=current_user.id,
            branch_id=getattr(current_user, 'branch_id', None)
        )
        db.session.add(fb)
        db.session.commit()
        # 관리자에게 알림 전송
        try:
            send_admin_only_notification("새로운 개선/문의사항 등록", content)
        except Exception:
            pass
        flash('개선/문의사항이 등록되었습니다.')
        return redirect(url_for('dashboard'))
    return render_template('feedback_new.html')

@app.route('/admin/feedback')
@login_required
def admin_feedback():
    if not current_user.is_admin():
        flash('관리자만 접근할 수 있습니다.')
        return redirect(url_for('dashboard'))
    feedbacks = FeedbackIssue.query.order_by(FeedbackIssue.created_at.desc()).all()
    return render_template('admin/feedback.html', feedbacks=feedbacks)

@app.route('/admin/feedback/<int:feedback_id>/resolve')
@login_required
def resolve_feedback(feedback_id):
    if not current_user.is_admin():
        flash('관리자만 접근할 수 있습니다.')
        return redirect(url_for('dashboard'))
    fb = FeedbackIssue.query.get_or_404(feedback_id)
    fb.status = 'resolved'
    db.session.commit()
    flash('해당 문의가 처리되었습니다.')
    return redirect(url_for('admin_feedback'))

@app.route('/admin/notify_send', methods=['GET', 'POST'])
@login_required
def admin_notify_send():
    """관리자 전용 알림 발송 페이지"""
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.')
        return redirect(url_for('dashboard'))

    # 지점과 직원 목록 가져오기
    branches = Branch.query.all()
    employees = User.query.filter_by(status='approved').all()

    if request.method == 'POST':
        target_type = request.form['target_type']
        title = request.form['title']
        content = request.form['content']
        category = request.form['category']
        priority = request.form['priority']
        is_admin_only = request.form.get('is_admin_only') == '1'
        
        if not target_type or not title or not content:
            flash('필수 항목을 모두 입력해주세요.', 'error')
            return render_template('admin/notify_send.html', 
                                 branches=branches, 
                                 employees=employees,
                                 recent_history=[])
        
        try:
            if target_type == 'all':
                # 전체 알림: 모든 승인된 직원에게 발송
                users = User.query.filter_by(status='approved').all()
                for user in users:
                    notification = Notification(
                        user_id=user.id, 
                        content=content,
                        category=category,
                        priority=priority,
                        is_admin_only=is_admin_only
                    )
                    db.session.add(notification)
                db.session.commit()
                flash(f'전체 알림이 {len(users)}명에게 발송되었습니다.', 'success')
                
            elif target_type == 'branch':
                branch_id = request.form['branch_id']
                if not branch_id:
                    flash('지점을 선택해주세요.', 'error')
                    return render_template('admin/notify_send.html', 
                                         branches=branches, 
                                         employees=employees,
                                         recent_history=[])
                
                # 해당 지점의 승인된 직원들에게 발송
                users = User.query.filter_by(branch_id=branch_id, status='approved').all()
                for user in users:
                    notification = Notification(
                        user_id=user.id, 
                        content=content,
                        category=category,
                        priority=priority,
                        is_admin_only=is_admin_only
                    )
                    db.session.add(notification)
                db.session.commit()
                flash(f'지점별 알림이 {len(users)}명에게 발송되었습니다.', 'success')
                
            elif target_type == 'user':
                user_id = request.form['user_id']
                if not user_id:
                    flash('직원을 선택해주세요.', 'error')
                    return render_template('admin/notify_send.html', 
                                         branches=branches, 
                                         employees=employees,
                                         recent_history=[])
                
                # 개별 직원에게 발송
                notification = Notification(
                    user_id=user_id, 
                    content=content,
                    category=category,
                    priority=priority,
                    is_admin_only=is_admin_only
                )
                db.session.add(notification)
                db.session.commit()
                flash('직원 개별 알림이 발송되었습니다.', 'success')
            else:
                flash('대상을 선택해주세요.', 'error')
                return render_template('admin/notify_send.html', 
                                     branches=branches, 
                                     employees=employees,
                                     recent_history=[])
                
        except Exception as e:
            db.session.rollback()
            flash(f'알림 발송 중 오류가 발생했습니다: {str(e)}', 'error')
            return render_template('admin/notify_send.html', 
                                 branches=branches, 
                                 employees=employees,
                                 recent_history=[])
        
        return redirect(url_for('admin_notify_send'))

    # 최근 발송 이력 (최근 10개)
    recent_history = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).limit(10).all()

    return render_template('admin/notify_send.html', 
                         branches=branches, 
                         employees=employees,
                         recent_history=recent_history)

@app.route('/api/order/new', methods=['POST'])
@login_required
def create_order():
    data = request.json or request.form
    order = Order(
        employee_id=current_user.id,  # 또는 data['employee_id']
        store_id=current_user.branch_id,  # 또는 data['store_id']
        created_at=datetime.utcnow()
    )
    db.session.add(order)
    db.session.commit()
    return jsonify({'result': 'ok', 'order_id': order.id})

@app.route('/api/order/complete/<int:order_id>', methods=['POST'])
@login_required
def complete_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.completed_at:
        return jsonify({'error': '이미 완료된 주문입니다.'}), 400
    order.completed_at = datetime.utcnow()
    diff = order.completed_at - order.created_at
    order.processing_minutes = int(diff.total_seconds() // 60)
    db.session.commit()

    # 기준 초과 알림
    branch = Branch.query.get(order.store_id)
    standard = branch.processing_time_standard if branch else 15
    if order.processing_minutes > standard:
        send_notification_enhanced(
            user_id=order.employee_id,
            title="주문 처리 시간이 기준을 초과했습니다.",
            content=f"기준: {standard}분 / 실제: {order.processing_minutes}분",
        )
    return jsonify({'result': 'ok'})

@app.route('/admin/order_setting', methods=['GET', 'POST'])
@login_required
def admin_order_setting():
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.')
        return redirect(url_for('dashboard'))
    branches = Branch.query.all()
    if request.method == 'POST':
        for branch in branches:
            field_name = f'standard_{branch.id}'
            if field_name in request.form:
                try:
                    new_val = int(request.form[field_name])
                    if new_val != branch.processing_time_standard:
                        branch.processing_time_standard = new_val
                        db.session.commit()
                        # 모든 직원에게 알림
                        send_notification_to_role(
                            role='employee',
                            title="주문 처리 기준 시간이 변경되었습니다.",
                            content=f"{branch.name} 기준 시간: {new_val}분"
                        )
                except Exception as e:
                    flash(f"{branch.name} 기준 시간 변경 실패: {e}")
        flash('기준 시간이 저장되었습니다.')
        return redirect(url_for('admin_order_setting'))
    return render_template('admin/order_setting.html', branches=branches)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

