from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, make_response
from flask_login import UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, date
from dateutil import parser as date_parser
import os
import click
from collections import defaultdict
import io
import pandas as pd
import pdfkit
from sqlalchemy import func, case

from config import config_by_name
from extensions import db, migrate, login_manager, csrf, limiter, cache
from models import User, Schedule, CleaningPlan, Report, Notification, Notice, Order, Attendance, AttendanceEvaluation, AttendanceReport

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
        return redirect(url_for('index'))
    
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    # 기존 통계 데이터
    num_users = User.query.count()
    num_attendance = Attendance.query.count()
    
    # 경고 사용자 (이번 달 지각 2회 이상/결근 발생)
    current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    warn_users = []
    
    # 지점별 비교 데이터
    result = db.session.query(
        User.branch,
        func.count(User.id).label('user_count'),
        func.sum(Attendance.work_minutes).label('total_work'),
        func.sum(case([(Attendance.status == 'late', 1)], else_=0)).label('total_late'),
        func.sum(case([(Attendance.status == 'absent', 1)], else_=0)).label('total_absent')
    ).join(Attendance, User.id == Attendance.user_id, isouter=True).group_by(User.branch).all()
    
    # 월별 통계 데이터 추가
    # 알림 통계
    noti_stats = db.session.query(
        func.strftime('%Y-%m', Notification.created_at).label('month'),
        func.count().label('count')
    ).group_by(func.strftime('%Y-%m', Notification.created_at)).order_by('month').all()
    
    # 근무 스케줄 통계
    work_stats = db.session.query(
        func.strftime('%Y-%m', Schedule.date).label('month'),
        func.count().label('count')
    ).group_by(func.strftime('%Y-%m', Schedule.date)).order_by('month').all()
    
    # 발주 통계 (Order 모델이 있다면)
    order_stats = []
    try:
        order_stats = db.session.query(
            func.strftime('%Y-%m', Order.order_date).label('month'),
            func.count().label('count')
        ).group_by(func.strftime('%Y-%m', Order.order_date)).order_by('month').all()
    except:
        pass
    
    # 청소 계획 통계 (CleaningPlan 모델이 있다면)
    clean_stats = []
    try:
        clean_stats = db.session.query(
            func.strftime('%Y-%m', CleaningPlan.date).label('month'),
            func.count().label('count')
        ).group_by(func.strftime('%Y-%m', CleaningPlan.date)).order_by('month').all()
    except:
        pass
    
    # 알림 카테고리별 통계
    noti_category_stats = db.session.query(
        Notification.category,
        func.count().label('count')
    ).group_by(Notification.category).all()
    
    # 차트 데이터 준비
    chart_labels = [r.month for r in noti_stats]
    noti_data = [r.count for r in noti_stats]
    work_data = [r.count for r in work_stats]
    order_data = [r.count for r in order_stats]
    clean_data = [r.count for r in clean_stats]
    
    # 카테고리별 데이터
    category_labels = [r.category for r in noti_category_stats]
    category_data = [r.count for r in noti_category_stats]
    
    # 기존 차트 데이터들
    branch_names = [r.branch for r in result]
    trend_dates = []
    trend_data = []
    dist_labels = ['8시간 미만', '8-9시간', '9-10시간', '10시간 이상']
    dist_data = [0, 0, 0, 0]
    
    # 최근 출퇴근 이력
    recent = db.session.query(
        User.username.label('user'),
        Attendance.clock_in,
        Attendance.clock_out,
        Attendance.work_minutes,
        Attendance.status
    ).join(User).order_by(Attendance.clock_in.desc()).limit(10).all()
    
    # 지각/결근 랭킹
    top_late = db.session.query(
        User.username.label('user'),
        func.count().label('late_count')
    ).join(Attendance).filter(Attendance.status == 'late').group_by(User.id).order_by(func.count().desc()).limit(5).all()
    
    top_absent = db.session.query(
        User.username.label('user'),
        func.count().label('absent_count')
    ).join(Attendance).filter(Attendance.status == 'absent').group_by(User.id).order_by(func.count().desc()).limit(5).all()
    
    context = {
        'num_users': num_users,
        'num_attendance': num_attendance,
        'warn_users': warn_users,
        'result': result,
        'branch_names': branch_names,
        'trend_dates': trend_dates,
        'trend_data': trend_data,
        'dist_labels': dist_labels,
        'dist_data': dist_data,
        'recent': recent,
        'top_late': top_late,
        'top_absent': top_absent,
        'chart_labels': chart_labels,
        'chart_data': noti_data,  # 기존 차트용
        # 새로운 월별 통계 데이터
        'noti_stats': noti_stats,
        'work_stats': work_stats,
        'order_stats': order_stats,
        'clean_stats': clean_stats,
        'noti_data': noti_data,
        'work_data': work_data,
        'order_data': order_data,
        'clean_data': clean_data,
        # 카테고리별 통계
        'noti_category_stats': noti_category_stats,
        'category_labels': category_labels,
        'category_data': category_data
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
        query = Notification.query.filter_by(user_id=current_user.id)
    
    # 필터링
    category = request.args.get('category', '')
    current_is_read = request.args.get('is_read', '')
    
    if category:
        query = query.filter_by(category=category)
    if current_is_read in ['0', '1']:
        query = query.filter_by(is_read=bool(int(current_is_read)))
    
    # 정렬 및 페이징
    notifications = query.order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # 통계
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    # 카테고리별 통계
    stats = {}
    if current_user.is_admin():
        stats['unread'] = Notification.query.filter_by(is_read=False).count()
        stats['total'] = Notification.query.count()
    else:
        stats['unread'] = unread_count
        stats['total'] = Notification.query.filter_by(user_id=current_user.id).count()
    
    return render_template('notifications.html',
        notifications=notifications,
        unread_count=unread_count,
        current_category=category,
        current_is_read=current_is_read,
        stat=stats
    )

@app.route('/notifications/advanced')
@login_required
def notifications_advanced():
    """알림센터 상세 필터"""
    q = Notification.query.filter_by(user_id=current_user.id)
    
    # 필터링 파라미터
    category = request.args.get('category')
    is_read = request.args.get('is_read')
    keyword = request.args.get('kw')
    date_from = request.args.get('from')
    date_to = request.args.get('to')
    
    # 필터 적용
    if category:
        q = q.filter_by(category=category)
    if is_read in ['0', '1']:
        q = q.filter_by(is_read=bool(int(is_read)))
    if keyword:
        q = q.filter(Notification.content.contains(keyword))
    if date_from:
        q = q.filter(Notification.created_at >= date_from)
    if date_to:
        q = q.filter(Notification.created_at <= date_to)
    
    notis = q.order_by(Notification.created_at.desc()).all()
    
    return render_template('notifications_advanced.html', 
        notis=notis, 
        category=category,
        is_read=is_read,
        kw=keyword,
        from_date=date_from,
        to_date=date_to
    )

@app.route('/notifications/mark_read/<int:notification_id>')
@login_required
def mark_notification_read(notification_id):
    """알림 읽음 처리"""
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id == current_user.id:
        notification.is_read = True
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 403

@app.route('/notifications/mark_all_read')
@login_required
def mark_all_notifications_read():
    """모든 알림 읽음 처리"""
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    flash('모든 알림을 읽음 처리했습니다.', 'success')
    return redirect(url_for('notifications'))

@app.route('/api/new_notifications')
@login_required
def api_new_notifications():
    """실시간 알림 개수 API"""
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})

@app.route('/api/latest_notifications')
@login_required
def api_latest_notifications():
    """최신 알림 목록 API"""
    notis = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(6).all()
    icons = {'발주':'📦','청소':'🧹','근무':'👤','교대':'🔁','공지':'🔔'}
    
    out = []
    for n in notis:
        out.append({
            'content': n.content,
            'icon': icons.get(n.category, '🔔'),
            'time': n.created_at.strftime('%m-%d %H:%M'),
            'is_read': n.is_read
        })
    
    return jsonify({'list': out})

@app.route('/notification/<int:nid>')
@login_required
def notification_jump(nid):
    """알림 클릭 시 자동 읽음 처리 및 상세페이지 이동"""
    n = Notification.query.get_or_404(nid)
    
    # 본인만 확인(혹은 관리자는 전체)
    if n.user_id != current_user.id and not current_user.is_admin():
        flash('권한이 없습니다.', 'error')
        return redirect(url_for('notifications'))
    
    # 자동 읽음 처리
    n.is_read = True
    db.session.commit()
    
    # 링크가 있으면 해당 페이지로 이동
    if n.link:
        return redirect(n.link)
    
    # 링크가 없으면 상세페이지로 이동
    return render_template('notification_detail.html', n=n)

# --- Admin Routes ---
@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin():
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/swap_requests', methods=['GET'])
@login_required
def admin_swap_requests():
    if not current_user.is_admin():
        return redirect(url_for('index'))
    # '대기' 상태인 '교대' 카테고리의 스케줄만 조회
    reqs = Schedule.query.filter_by(category='교대', status='대기').order_by(Schedule.date.asc()).all()
    return render_template('admin/swap_requests.html', swap_requests=reqs)

@app.route('/admin/reports')
@login_required
def admin_reports():
    if not current_user.is_admin():
        return redirect(url_for('index'))
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return render_template('admin/reports.html', reports=reports)

@app.route('/admin/statistics')
@login_required
def admin_statistics():
    if not current_user.is_admin():
        return redirect(url_for('index'))
    
    # 기본 변수들 추가
    users = User.query.all()
    swap_count = {'대기': 0, '승인': 0, '거절': 0}  # 기본값
    off_count = {}  # 기본값
    
    return render_template('admin/statistics.html', 
                         users=users, 
                         swap_count=swap_count, 
                         off_count=off_count)

@app.route('/admin/all_notifications')
@login_required
def admin_all_notifications():
    """관리자용 알림센터 - 필터링 기능"""
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('index'))
    
    # 필터링 파라미터
    user_id = request.args.get('user_id')
    category = request.args.get('category')
    date_from = request.args.get('from')
    date_to = request.args.get('to')
    
    # 쿼리 구성
    q = Notification.query
    if user_id:
        q = q.filter_by(user_id=int(user_id))
    if category:
        q = q.filter_by(category=category)
    if date_from:
        try:
            from_dt = datetime.strptime(date_from, '%Y-%m-%d')
            q = q.filter(Notification.created_at >= from_dt)
        except ValueError:
            pass
    if date_to:
        try:
            to_dt = datetime.strptime(date_to, '%Y-%m-%d')
            # 종료일은 23:59:59까지 포함
            to_dt = to_dt.replace(hour=23, minute=59, second=59)
            q = q.filter(Notification.created_at <= to_dt)
        except ValueError:
            pass
    
    # 결과 조회 (최대 500개)
    notis = q.order_by(Notification.created_at.desc()).limit(500).all()
    
    # 사용자 목록 (필터용)
    users = User.query.all()
    
    return render_template('admin/all_notifications.html', 
        notis=notis, 
        users=users, 
        user_id=user_id, 
        category=category
    )

@app.route('/admin/notification/delete/<int:nid>', methods=['POST'])
@login_required
def admin_delete_notification(nid):
    """관리자용 알림 삭제"""
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('index'))
    
    n = Notification.query.get_or_404(nid)
    db.session.delete(n)
    db.session.commit()
    
    flash('알림이 삭제되었습니다.', 'success')
    return redirect(request.referrer or url_for('admin_all_notifications'))

@app.route('/admin/notification/<int:nid>')
@login_required
def admin_notification_detail(nid):
    """관리자용 알림 상세 조회"""
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('index'))
    
    n = Notification.query.get_or_404(nid)
    return render_template('admin/notification_detail.html', n=n)

@app.route('/notifications/bulk', methods=['POST'])
@login_required
def notifications_bulk_action():
    """알림 일괄 처리 (읽음/삭제/엑셀 다운로드)"""
    nids = request.form.getlist('nids')
    action = request.form.get('action')
    
    if not nids:
        flash('처리할 알림을 선택해주세요.', 'warning')
        return redirect(request.referrer or url_for('notifications'))
    
    # 쿼리 구성 (본인 알림만 또는 관리자는 전체)
    if current_user.is_admin():
        qs = Notification.query.filter(Notification.id.in_(nids))
    else:
        qs = Notification.query.filter(
            Notification.id.in_(nids),
            Notification.user_id == current_user.id
        )
    
    notifications = qs.all()
    
    if action == 'read':
        # 일괄 읽음 처리
        for n in notifications:
            n.is_read = True
        db.session.commit()
        flash(f'{len(notifications)}개의 알림을 읽음 처리했습니다.', 'success')
        return redirect(request.referrer or url_for('notifications'))
        
    elif action == 'delete':
        # 일괄 삭제
        for n in notifications:
            db.session.delete(n)
        db.session.commit()
        flash(f'{len(notifications)}개의 알림을 삭제했습니다.', 'success')
        return redirect(request.referrer or url_for('notifications'))
        
    elif action == 'excel':
        # 엑셀 다운로드
        df = pd.DataFrame([{
            "직원": n.user.username if n.user else "",
            "카테고리": n.category,
            "내용": n.content,
            "시각": n.created_at.strftime("%Y-%m-%d %H:%M"),
            "읽음": "O" if n.is_read else "X"
        } for n in notifications])
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='알림목록')
        output.seek(0)
        
        filename = f"notifications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return send_file(output, download_name=filename, as_attachment=True)
    
    return redirect(request.referrer or url_for('notifications'))

@app.route('/notifications/excel')
@login_required
def notifications_excel():
    """일반 사용자용 알림 엑셀 다운로드 (검색/필터 적용)"""
    # 기본 쿼리 (본인 알림만)
    q = Notification.query.filter_by(user_id=current_user.id)
    
    # 검색/필터 파라미터 적용
    category = request.args.get('category')
    is_read = request.args.get('is_read')
    kw = request.args.get('kw')
    date_from = request.args.get('from')
    date_to = request.args.get('to')
    
    if category:
        q = q.filter_by(category=category)
    if is_read in ['0', '1']:
        q = q.filter_by(is_read=bool(int(is_read)))
    if kw:
        q = q.filter(Notification.content.contains(kw))
    if date_from:
        try:
            from_dt = datetime.strptime(date_from, '%Y-%m-%d')
            q = q.filter(Notification.created_at >= from_dt)
        except ValueError:
            pass
    if date_to:
        try:
            to_dt = datetime.strptime(date_to, '%Y-%m-%d')
            # 종료일은 23:59:59까지 포함
            to_dt = to_dt.replace(hour=23, minute=59, second=59)
            q = q.filter(Notification.created_at <= to_dt)
        except ValueError:
            pass
    
    # 결과 조회
    notis = q.order_by(Notification.created_at.desc()).all()
    
    # DataFrame 변환
    df = pd.DataFrame([{
        "카테고리": n.category,
        "내용": n.content,
        "시각": n.created_at.strftime("%Y-%m-%d %H:%M"),
        "읽음": "O" if n.is_read else "X"
    } for n in notis])
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='알림목록')
    output.seek(0)
    
    filename = f"my_notifications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(output, download_name=filename, as_attachment=True)

@app.route('/admin/all_notifications/excel')
@login_required
def admin_all_notifications_excel():
    """관리자용 전체 알림 엑셀 다운로드 (필터 적용)"""
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('index'))
    
    # 기본 쿼리
    q = Notification.query
    
    # 필터 파라미터 적용
    user_id = request.args.get('user_id')
    category = request.args.get('category')
    date_from = request.args.get('from')
    date_to = request.args.get('to')
    
    if user_id:
        q = q.filter_by(user_id=int(user_id))
    if category:
        q = q.filter_by(category=category)
    if date_from:
        try:
            from_dt = datetime.strptime(date_from, '%Y-%m-%d')
            q = q.filter(Notification.created_at >= from_dt)
        except ValueError:
            pass
    if date_to:
        try:
            to_dt = datetime.strptime(date_to, '%Y-%m-%d')
            # 종료일은 23:59:59까지 포함
            to_dt = to_dt.replace(hour=23, minute=59, second=59)
            q = q.filter(Notification.created_at <= to_dt)
        except ValueError:
            pass
    
    # 결과 조회 (최대 1000개)
    notis = q.order_by(Notification.created_at.desc()).limit(1000).all()
    
    # DataFrame 변환
    df = pd.DataFrame([{
        "직원": n.user.username if n.user else "",
        "카테고리": n.category,
        "내용": n.content,
        "시각": n.created_at.strftime("%Y-%m-%d %H:%M"),
        "읽음": "O" if n.is_read else "X"
    } for n in notis])
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='전체알림목록')
    output.seek(0)
    
    filename = f"all_notifications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(output, download_name=filename, as_attachment=True)

@app.route('/notifications/pdf')
@login_required
def notifications_pdf():
    """일반 사용자용 알림 PDF 다운로드 (검색/필터 적용)"""
    # 기본 쿼리 (본인 알림만)
    q = Notification.query.filter_by(user_id=current_user.id)
    
    # 검색/필터 파라미터 적용
    category = request.args.get('category')
    is_read = request.args.get('is_read')
    kw = request.args.get('kw')
    from_date = request.args.get('from')
    to_date = request.args.get('to')
    
    if category:
        q = q.filter_by(category=category)
    if is_read in ['0', '1']:
        q = q.filter_by(is_read=bool(int(is_read)))
    if kw:
        q = q.filter(Notification.content.contains(kw))
    if from_date:
        try:
            from_dt = datetime.strptime(from_date, '%Y-%m-%d')
            q = q.filter(Notification.created_at >= from_dt)
        except ValueError:
            pass
    if to_date:
        try:
            to_dt = datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1)
            q = q.filter(Notification.created_at < to_dt)
        except ValueError:
            pass
    
    # 결과 조회
    notis = q.order_by(Notification.created_at.desc()).limit(100).all()
    
    # HTML 템플릿 렌더링
    html = render_template('notifications_pdf.html', 
                         notis=notis, 
                         user=current_user,
                         category=category,
                         is_read=is_read,
                         kw=kw,
                         from_date=from_date,
                         to_date=to_date)
    
    try:
        # PDF 생성
        pdf = pdfkit.from_string(html, False)
        output = io.BytesIO(pdf)
        output.seek(0)
        
        filename = f"my_notifications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return send_file(output, download_name=filename, as_attachment=True)
    except Exception as e:
        flash(f'PDF 생성 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(request.referrer or url_for('notifications'))

@app.route('/admin/all_notifications/pdf')
@login_required
def admin_all_notifications_pdf():
    """관리자용 전체 알림 PDF 다운로드 (필터 적용)"""
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('index'))
    
    # 기본 쿼리
    q = Notification.query
    
    # 필터 파라미터 적용
    user_id = request.args.get('user_id')
    category = request.args.get('category')
    
    if user_id:
        q = q.filter_by(user_id=int(user_id))
    if category:
        q = q.filter_by(category=category)
    
    # 결과 조회 (최대 100개)
    notis = q.order_by(Notification.created_at.desc()).limit(100).all()
    
    # HTML 템플릿 렌더링
    html = render_template('admin/all_notifications_pdf.html', 
                         notis=notis,
                         user_id=user_id,
                         category=category)
    
    try:
        # PDF 생성
        pdf = pdfkit.from_string(html, False)
        output = io.BytesIO(pdf)
        output.seek(0)
        
        filename = f"all_notifications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return send_file(output, download_name=filename, as_attachment=True)
    except Exception as e:
        flash(f'PDF 생성 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(request.referrer or url_for('admin_all_notifications'))

@app.route('/schedule_fc')
@login_required
def schedule_fc():
    return render_template('schedule_fc.html')

@app.route('/admin/data_backup')
@login_required
def admin_data_backup():
    """관리자용 전체 데이터 통합 백업 (ZIP + CSV)"""
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('index'))
    
    import zipfile
    import tempfile
    import os
    
    try:
        # 임시 디렉토리 생성
        temp_dir = tempfile.mkdtemp()
        
        # 각 테이블의 데이터를 DataFrame으로 변환
        dataframes = {}
        
        # 사용자 데이터
        users_data = []
        for u in User.query.all():
            user_dict = {
                'id': u.id,
                'username': u.username,
                'role': u.role,
                'status': u.status,
                'created_at': u.created_at.strftime('%Y-%m-%d %H:%M:%S') if u.created_at else '',
                'last_login': u.last_login.strftime('%Y-%m-%d %H:%M:%S') if u.last_login else ''
            }
            users_data.append(user_dict)
        dataframes['users'] = pd.DataFrame(users_data)
        
        # 알림 데이터
        notifications_data = []
        for n in Notification.query.all():
            notif_dict = {
                'id': n.id,
                'user_id': n.user_id,
                'username': n.user.username if n.user else '',
                'category': n.category,
                'content': n.content,
                'is_read': n.is_read,
                'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S') if n.created_at else '',
                'link': n.link or '',
                'memo': n.memo or ''
            }
            notifications_data.append(notif_dict)
        dataframes['notifications'] = pd.DataFrame(notifications_data)
        
        # 스케줄 데이터
        schedules_data = []
        for s in Schedule.query.all():
            schedule_dict = {
                'id': s.id,
                'user_id': s.user_id,
                'username': s.user.username if s.user else '',
                'date': s.date.strftime('%Y-%m-%d') if s.date else '',
                'start_time': s.start_time.strftime('%H:%M') if s.start_time else '',
                'end_time': s.end_time.strftime('%H:%M') if s.end_time else '',
                'category': s.category or '',
                'status': s.status or '',
                'memo': s.memo or '',
                'created_at': s.created_at.strftime('%Y-%m-%d %H:%M:%S') if s.created_at else ''
            }
            schedules_data.append(schedule_dict)
        dataframes['schedules'] = pd.DataFrame(schedules_data)
        
        # 청소 계획 데이터
        cleanings_data = []
        for c in CleaningPlan.query.all():
            cleaning_dict = {
                'id': c.id,
                'user_id': c.user_id,
                'username': c.user.username if c.user else '',
                'date': c.date.strftime('%Y-%m-%d') if c.date else '',
                'team': c.team or '',
                'plan': c.plan or '',
                'memo': c.memo or '',
                'created_at': c.created_at.strftime('%Y-%m-%d %H:%M:%S') if c.created_at else ''
            }
            cleanings_data.append(cleaning_dict)
        dataframes['cleanings'] = pd.DataFrame(cleanings_data)
        
        # 발주 데이터
        orders_data = []
        for o in Order.query.all():
            order_dict = {
                'id': o.id,
                'user_id': o.user_id,
                'username': o.user.username if o.user else '',
                'item_name': o.item_name or '',
                'quantity': o.quantity or 0,
                'status': o.status or '',
                'memo': o.memo or '',
                'created_at': o.created_at.strftime('%Y-%m-%d %H:%M:%S') if o.created_at else ''
            }
            orders_data.append(order_dict)
        dataframes['orders'] = pd.DataFrame(orders_data)
        
        # 공지사항 데이터
        notices_data = []
        for n in Notice.query.all():
            notice_dict = {
                'id': n.id,
                'title': n.title or '',
                'content': n.content or '',
                'author_id': n.author_id,
                'author_name': n.author.username if n.author else '',
                'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S') if n.created_at else '',
                'updated_at': n.updated_at.strftime('%Y-%m-%d %H:%M:%S') if n.updated_at else ''
            }
            notices_data.append(notice_dict)
        dataframes['notices'] = pd.DataFrame(notices_data)
        
        # 보고서 데이터
        reports_data = []
        for r in Report.query.all():
            report_dict = {
                'id': r.id,
                'user_id': r.user_id,
                'username': r.user.username if r.user else '',
                'title': r.title or '',
                'content': r.content or '',
                'category': r.category or '',
                'status': r.status or '',
                'created_at': r.created_at.strftime('%Y-%m-%d %H:%M:%S') if r.created_at else ''
            }
            reports_data.append(report_dict)
        dataframes['reports'] = pd.DataFrame(reports_data)
        
        # ZIP 파일 생성
        zip_filename = f"restaurant_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 각 DataFrame을 CSV로 저장하고 ZIP에 추가
            for table_name, df in dataframes.items():
                if not df.empty:
                    csv_filename = f"{table_name}.csv"
                    csv_path = os.path.join(temp_dir, csv_filename)
                    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                    zipf.write(csv_path, csv_filename)
        
        # 백업 정보 파일 추가
        backup_info = f"""레스토랑 관리 시스템 데이터 백업
생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
생성자: {current_user.username}

포함된 테이블:
- users: {len(users_data)}개 사용자
- notifications: {len(notifications_data)}개 알림
- schedules: {len(schedules_data)}개 스케줄
- cleanings: {len(cleanings_data)}개 청소계획
- orders: {len(orders_data)}개 발주
- notices: {len(notices_data)}개 공지사항
- reports: {len(reports_data)}개 보고서

총 {sum(len(data) for data in [users_data, notifications_data, schedules_data, cleanings_data, orders_data, notices_data, reports_data])}개 레코드
"""
        
        info_path = os.path.join(temp_dir, 'backup_info.txt')
        with open(info_path, 'w', encoding='utf-8') as f:
            f.write(backup_info)
        zipf.write(info_path, 'backup_info.txt')
        
        # ZIP 파일 전송
        return send_file(
            zip_path,
            download_name=zip_filename,
            as_attachment=True,
            mimetype='application/zip'
        )
        
    except Exception as e:
        flash(f'백업 생성 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))
    
    finally:
        # 임시 파일 정리
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except:
            pass

@app.route('/admin/notification_stats')
@login_required
def admin_notification_stats():
    """알림 카테고리별 통계 페이지"""
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('index'))
    
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    # 카테고리별 통계
    category_stats = db.session.query(
        Notification.category,
        func.count().label('count')
    ).group_by(Notification.category).order_by(func.count().desc()).all()
    
    # 월별 알림 통계
    monthly_stats = db.session.query(
        func.strftime('%Y-%m', Notification.created_at).label('month'),
        func.count().label('count')
    ).group_by(func.strftime('%Y-%m', Notification.created_at)).order_by('month').all()
    
    # 사용자별 알림 통계
    user_stats = db.session.query(
        User.username,
        func.count(Notification.id).label('count')
    ).join(Notification, User.id == Notification.user_id).group_by(User.id).order_by(func.count(Notification.id).desc()).limit(10).all()
    
    # 읽음/안읽음 통계
    read_stats = db.session.query(
        Notification.is_read,
        func.count().label('count')
    ).group_by(Notification.is_read).all()
    
    # 최근 7일 알림 통계
    recent_7days = db.session.query(
        func.date(Notification.created_at).label('date'),
        func.count().label('count')
    ).filter(
        Notification.created_at >= datetime.now() - timedelta(days=7)
    ).group_by(func.date(Notification.created_at)).order_by('date').all()
    
    return render_template('admin/notification_stats.html',
                         category_stats=category_stats,
                         monthly_stats=monthly_stats,
                         user_stats=user_stats,
                         read_stats=read_stats,
                         recent_7days=recent_7days)

@app.route('/staff_stats', methods=['GET'])
@login_required
def staff_stats():
    """직원별 통계 페이지"""
    from datetime import date, timedelta
    import json
    
    # 사용자 목록 (관리자는 모든 사용자, 일반 사용자는 본인만)
    if current_user.is_admin():
        users = User.query.filter_by(status='approved').all()
    else:
        users = [current_user]
    
    # 선택된 사용자 (기본값: 첫 번째 사용자 또는 본인)
    user_id = int(request.args.get('user_id', 0)) or (users[0].id if users else current_user.id)
    
    # 권한 확인 (관리자가 아니면 본인만 조회 가능)
    if not current_user.is_admin() and user_id != current_user.id:
        flash('본인의 통계만 조회할 수 있습니다.', 'error')
        return redirect(url_for('staff_stats', user_id=current_user.id))
    
    # 기간 지정 (기본 최근 30일)
    date_from = request.args.get('from', (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'))
    date_to = request.args.get('to', date.today().strftime('%Y-%m-%d'))
    
    # 근무, 청소, 발주, 알림 건수
    work_cnt = Schedule.query.filter(
        Schedule.user_id == user_id,
        Schedule.category == '근무',
        Schedule.date >= date_from,
        Schedule.date <= date_to
    ).count()
    
    clean_cnt = Schedule.query.filter(
        Schedule.user_id == user_id,
        Schedule.category == '청소',
        Schedule.date >= date_from,
        Schedule.date <= date_to
    ).count()
    
    order_cnt = Order.query.filter(
        Order.ordered_by == user_id,
        Order.order_date >= date_from,
        Order.order_date <= date_to
    ).count()
    
    noti_cnt = Notification.query.filter(
        Notification.user_id == user_id,
        Notification.created_at >= date_from,
        Notification.created_at <= date_to
    ).count()
    
    # 출근 통계
    attendance_cnt = Attendance.query.filter(
        Attendance.user_id == user_id,
        Attendance.clock_in >= date_from,
        Attendance.clock_in <= date_to + ' 23:59:59'
    ).count()
    
    # 일별/카테고리별 히스토리 (차트용)
    days = []
    work_hist = []
    clean_hist = []
    order_hist = []
    attendance_hist = []
    
    if date_from and date_to:
        start_date = date.fromisoformat(date_from)
        end_date = date.fromisoformat(date_to)
        days = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d')
                for i in range((end_date - start_date).days + 1)]
        
        for d in days:
            work_hist.append(Schedule.query.filter(
                Schedule.user_id == user_id, 
                Schedule.category == '근무', 
                Schedule.date == d
            ).count())
            
            clean_hist.append(Schedule.query.filter(
                Schedule.user_id == user_id, 
                Schedule.category == '청소', 
                Schedule.date == d
            ).count())
            
            order_hist.append(Order.query.filter(
                Order.ordered_by == user_id, 
                Order.order_date == d
            ).count())
            
            attendance_hist.append(Attendance.query.filter(
                Attendance.user_id == user_id,
                func.date(Attendance.clock_in) == d
            ).count())
    
    # 선택된 사용자 정보
    selected_user = User.query.get(user_id)
    
    return render_template('staff_stats.html',
        users=users, 
        user_id=user_id, 
        selected_user=selected_user,
        date_from=date_from, 
        date_to=date_to,
        work_cnt=work_cnt, 
        clean_cnt=clean_cnt, 
        order_cnt=order_cnt, 
        noti_cnt=noti_cnt,
        attendance_cnt=attendance_cnt,
        days=json.dumps(days), 
        work_hist=json.dumps(work_hist), 
        clean_hist=json.dumps(clean_hist), 
        order_hist=json.dumps(order_hist),
        attendance_hist=json.dumps(attendance_hist)
    )

@app.route('/staff_attendance', methods=['GET'])
@login_required
def staff_attendance():
    """직원별 근무/지각/조퇴/야근 이력 조회"""
    from datetime import date, timedelta
    
    # 사용자 목록 (관리자는 모든 사용자, 일반 사용자는 본인만)
    if current_user.is_admin():
        users = User.query.filter_by(status='approved').all()
    else:
        users = [current_user]
    
    # 선택된 사용자 (기본값: 첫 번째 사용자 또는 본인)
    user_id = int(request.args.get('user_id', 0)) or (users[0].id if users else current_user.id)
    
    # 권한 확인 (관리자가 아니면 본인만 조회 가능)
    if not current_user.is_admin() and user_id != current_user.id:
        flash('본인의 근태만 조회할 수 있습니다.', 'error')
        return redirect(url_for('staff_attendance', user_id=current_user.id))
    
    # 기간 지정 (기본 최근 30일)
    date_from = request.args.get('from_', (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'))
    date_to = request.args.get('to', date.today().strftime('%Y-%m-%d'))
    
    # 근태 기록 조회
    records = Attendance.query.filter(
        Attendance.user_id == user_id,
        Attendance.clock_in >= date_from,
        Attendance.clock_in <= date_to + ' 23:59:59'
    ).order_by(Attendance.clock_in.desc()).all()
    
    # 선택된 사용자 정보
    selected_user = User.query.get(user_id)
    
    # 통계 계산
    total_days = len(records)
    late_count = sum(1 for r in records if r.status and '지각' in r.status)
    early_leave_count = sum(1 for r in records if r.status and '조퇴' in r.status)
    overtime_count = sum(1 for r in records if r.clock_out and r.clock_out.time() > timedelta(hours=18).total_seconds())
    normal_count = sum(1 for r in records if r.status == '정상')
    
    return render_template('staff_attendance.html',
        users=users, 
        user_id=user_id, 
        selected_user=selected_user,
        date_from=date_from, 
        date_to=date_to, 
        records=records,
        total_days=total_days,
        late_count=late_count,
        early_leave_count=early_leave_count,
        overtime_count=overtime_count,
        normal_count=normal_count
    )

@app.route('/staff_attendance/pdf')
@login_required
def staff_attendance_pdf():
    """직원별 근태 이력 PDF 다운로드"""
    from datetime import date, timedelta
    
    user_id = int(request.args.get('user_id', 0))
    date_from = request.args.get('from_', (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'))
    date_to = request.args.get('to', date.today().strftime('%Y-%m-%d'))
    
    # 권한 확인
    if not current_user.is_admin() and user_id != current_user.id:
        flash('본인의 근태만 다운로드할 수 있습니다.', 'error')
        return redirect(url_for('staff_attendance', user_id=current_user.id))
    
    user = User.query.get(user_id)
    if not user:
        flash('사용자를 찾을 수 없습니다.', 'error')
        return redirect(url_for('staff_attendance'))
    
    # 근태 기록 조회
    records = Attendance.query.filter(
        Attendance.user_id == user_id,
        Attendance.clock_in >= date_from,
        Attendance.clock_in <= date_to + ' 23:59:59'
    ).order_by(Attendance.clock_in.desc()).all()
    
    # 통계 계산
    total_days = len(records)
    late_count = sum(1 for r in records if r.status and '지각' in r.status)
    early_leave_count = sum(1 for r in records if r.status and '조퇴' in r.status)
    overtime_count = sum(1 for r in records if r.clock_out and r.clock_out.time() > timedelta(hours=18).total_seconds())
    normal_count = sum(1 for r in records if r.status == '정상')
    
    # HTML 템플릿 렌더링
    html = render_template('staff_attendance_pdf.html', 
                         user=user, 
                         records=records, 
                         date_from=date_from, 
                         date_to=date_to,
                         total_days=total_days,
                         late_count=late_count,
                         early_leave_count=early_leave_count,
                         overtime_count=overtime_count,
                         normal_count=normal_count)
    
    try:
        # PDF 생성
        pdf = pdfkit.from_string(html, False)
        output = io.BytesIO(pdf)
        output.seek(0)
        
        filename = f"{user.username}_근태이력_{date_from}_{date_to}.pdf"
        return send_file(output, download_name=filename, as_attachment=True)
    except Exception as e:
        flash(f'PDF 생성 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('staff_attendance', user_id=user_id, from_=date_from, to=date_to))

@app.route('/staff_attendance_report', methods=['GET', 'POST'])
@login_required
def staff_attendance_report():
    """직원 근태 리포트/평가"""
    from datetime import date, timedelta
    
    # 사용자 목록 (관리자는 모든 사용자, 일반 사용자는 본인만)
    if current_user.is_admin():
        users = User.query.filter_by(status='approved').all()
    else:
        users = [current_user]
    
    # 선택된 사용자 (기본값: 첫 번째 사용자 또는 본인)
    user_id = int(request.args.get('user_id', 0)) or (users[0].id if users else current_user.id)
    
    # 권한 확인 (관리자가 아니면 본인만 조회 가능)
    if not current_user.is_admin() and user_id != current_user.id:
        flash('본인의 근태만 조회할 수 있습니다.', 'error')
        return redirect(url_for('staff_attendance_report', user_id=current_user.id))
    
    # 기간 지정 (기본 최근 30일)
    date_from = request.args.get('from_', (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'))
    date_to = request.args.get('to', date.today().strftime('%Y-%m-%d'))
    
    # 근태 기록 조회
    records = Attendance.query.filter(
        Attendance.user_id == user_id,
        Attendance.clock_in >= date_from,
        Attendance.clock_in <= date_to + ' 23:59:59'
    ).order_by(Attendance.clock_in.desc()).all()
    
    # 선택된 사용자 정보
    selected_user = User.query.get(user_id)
    
    # 통계 계산
    total_days = len(records)
    late_count = sum(1 for r in records if r.status and '지각' in r.status)
    early_leave_count = sum(1 for r in records if r.status and '조퇴' in r.status)
    overtime_count = sum(1 for r in records if r.clock_out and r.clock_out.time() > timedelta(hours=18).total_seconds())
    normal_count = sum(1 for r in records if r.status == '정상')
    
    # 근태 점수 계산 (100점 만점)
    score = 100
    if total_days > 0:
        # 지각: -5점씩
        score -= late_count * 5
        # 조퇴: -3점씩
        score -= early_leave_count * 3
        # 야근: +2점씩 (최대 10점)
        overtime_bonus = min(overtime_count * 2, 10)
        score += overtime_bonus
        # 정상 출근: +1점씩 (최대 20점)
        normal_bonus = min(normal_count * 1, 20)
        score += normal_bonus
    
    # 점수 범위 제한
    score = max(0, min(100, score))
    
    # 등급 부여
    if score >= 90:
        grade = "A+"
    elif score >= 80:
        grade = "A"
    elif score >= 70:
        grade = "B+"
    elif score >= 60:
        grade = "B"
    elif score >= 50:
        grade = "C+"
    elif score >= 40:
        grade = "C"
    else:
        grade = "D"
    
    # 기존 평가 코멘트 조회
    comment = ""
    evaluation = AttendanceReport.query.filter_by(
        user_id=user_id,
        period_from=date_from,
        period_to=date_to
    ).first()
    
    if evaluation:
        comment = evaluation.comment
    
    # 평가 이력 조회
    history = AttendanceReport.query.filter_by(user_id=user_id).order_by(AttendanceReport.created_at.desc()).limit(10).all()
    
    # POST 요청 처리 (평가 저장)
    if request.method == 'POST' and current_user.is_admin():
        comment = request.form.get('comment', '').strip()
        
        # 평가 저장/업데이트
        if evaluation:
            evaluation.comment = comment
            evaluation.score = score
            evaluation.grade = grade
            evaluation.total = total_days
            evaluation.late = late_count
            evaluation.early = early_leave_count
            evaluation.ot = overtime_count
            evaluation.ontime = normal_count
        else:
            evaluation = AttendanceReport(
                user_id=user_id,
                period_from=date_from,
                period_to=date_to,
                total=total_days,
                late=late_count,
                early=early_leave_count,
                ot=overtime_count,
                ontime=normal_count,
                score=score,
                grade=grade,
                comment=comment
            )
            db.session.add(evaluation)
        
        db.session.commit()
        flash('평가가 저장되었습니다.', 'success')
    
    return render_template('staff_attendance_report.html',
        users=users,
        user_id=user_id,
        selected_user=selected_user,
        date_from=date_from,
        date_to=date_to,
        total=total_days,
        late=late_count,
        early=early_leave_count,
        ot=overtime_count,
        ontime=normal_count,
        score=score,
        grade=grade,
        comment=comment,
        history=history,
        is_admin=current_user.is_admin()
    )

@app.route('/staff_attendance_report_excel')
@login_required
def staff_attendance_report_excel():
    """직원 근태 리포트 Excel 다운로드"""
    import pandas as pd
    import io
    
    # 사용자 목록 (관리자는 모든 사용자, 일반 사용자는 본인만)
    if current_user.is_admin():
        users = User.query.filter_by(status='approved').all()
    else:
        users = [current_user]
    
    # 선택된 사용자 (기본값: 첫 번째 사용자 또는 본인)
    user_id = int(request.args.get('user_id', 0)) or (users[0].id if users else current_user.id)
    
    # 권한 확인 (관리자가 아니면 본인만 조회 가능)
    if not current_user.is_admin() and user_id != current_user.id:
        flash('본인의 근태만 조회할 수 있습니다.', 'error')
        return redirect(url_for('staff_attendance_report', user_id=current_user.id))
    
    # 평가 이력 조회
    history = AttendanceReport.query.filter_by(user_id=user_id).order_by(AttendanceReport.created_at.desc()).all()
    
    # 선택된 사용자 정보
    selected_user = User.query.get(user_id)
    
    # DataFrame 생성
    data = []
    for h in history:
        data.append({
            "기간": f"{h.period_from}~{h.period_to}",
            "점수": h.score,
            "등급": h.grade,
            "지각": h.late,
            "조퇴": h.early,
            "야근": h.ot,
            "정상출근": h.ontime,
            "총근무일": h.total,
            "코멘트": h.comment or "",
            "작성시각": h.created_at.strftime("%Y-%m-%d %H:%M")
        })
    
    df = pd.DataFrame(data)
    
    # Excel 파일 생성
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='근태평가이력', index=False)
        
        # 워크시트 가져오기
        worksheet = writer.sheets['근태평가이력']
        
        # 열 너비 자동 조정
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).apply(len).max(), len(col)) + 2
            worksheet.set_column(i, i, max_len)
    
    output.seek(0)
    
    # 파일명 생성
    filename = f"근태평가이력_{selected_user.username}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    
    return send_file(
        output,
        download_name=filename,
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/staff_attendance_report_pdf')
@login_required
def staff_attendance_report_pdf():
    """직원 근태 리포트 PDF 다운로드"""
    import pdfkit
    import io
    from datetime import date, timedelta
    
    # 사용자 목록 (관리자는 모든 사용자, 일반 사용자는 본인만)
    if current_user.is_admin():
        users = User.query.filter_by(status='approved').all()
    else:
        users = [current_user]
    
    # 선택된 사용자 (기본값: 첫 번째 사용자 또는 본인)
    user_id = int(request.args.get('user_id', 0)) or (users[0].id if users else current_user.id)
    
    # 권한 확인 (관리자가 아니면 본인만 조회 가능)
    if not current_user.is_admin() and user_id != current_user.id:
        flash('본인의 근태만 조회할 수 있습니다.', 'error')
        return redirect(url_for('staff_attendance_report', user_id=current_user.id))
    
    # 기간 지정 (기본 최근 30일)
    date_from = request.args.get('from_', (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'))
    date_to = request.args.get('to', date.today().strftime('%Y-%m-%d'))
    
    # 근태 기록 조회
    records = Attendance.query.filter(
        Attendance.user_id == user_id,
        Attendance.clock_in >= date_from,
        Attendance.clock_in <= date_to + ' 23:59:59'
    ).order_by(Attendance.clock_in.desc()).all()
    
    # 선택된 사용자 정보
    selected_user = User.query.get(user_id)
    
    # 통계 계산
    total_days = len(records)
    late_count = sum(1 for r in records if r.status and '지각' in r.status)
    early_leave_count = sum(1 for r in records if r.status and '조퇴' in r.status)
    overtime_count = sum(1 for r in records if r.clock_out and r.clock_out.time() > timedelta(hours=18).total_seconds())
    normal_count = sum(1 for r in records if r.status == '정상')
    
    # 근태 점수 계산 (100점 만점)
    score = 100
    if total_days > 0:
        # 지각: -5점씩
        score -= late_count * 5
        # 조퇴: -3점씩
        score -= early_leave_count * 3
        # 야근: +2점씩 (최대 10점)
        overtime_bonus = min(overtime_count * 2, 10)
        score += overtime_bonus
        # 정상 출근: +1점씩 (최대 20점)
        normal_bonus = min(normal_count * 1, 20)
        score += normal_bonus
    
    # 점수 범위 제한
    score = max(0, min(100, score))
    
    # 등급 부여
    if score >= 90:
        grade = "A+"
    elif score >= 80:
        grade = "A"
    elif score >= 70:
        grade = "B+"
    elif score >= 60:
        grade = "B"
    elif score >= 50:
        grade = "C+"
    elif score >= 40:
        grade = "C"
    else:
        grade = "D"
    
    # 기존 평가 코멘트 조회
    comment = ""
    evaluation = AttendanceReport.query.filter_by(
        user_id=user_id,
        period_from=date_from,
        period_to=date_to
    ).first()
    
    if evaluation:
        comment = evaluation.comment
    
    # HTML 렌더링
    html_content = render_template('staff_attendance_report_pdf.html',
        selected_user=selected_user,
        date_from=date_from,
        date_to=date_to,
        total=total_days,
        late=late_count,
        early=early_leave_count,
        ot=overtime_count,
        ontime=normal_count,
        score=score,
        grade=grade,
        comment=comment,
        current_user=current_user,
        now=datetime.utcnow()
    )
    
    # PDF 생성
    try:
        pdf = pdfkit.from_string(html_content, False)
        
        # 파일명 생성
        filename = f"근태리포트_{selected_user.username}_{date_from}_{date_to}.pdf"
        
        # 응답 생성
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        flash(f'PDF 생성 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('staff_attendance_report', user_id=user_id, from_=date_from, to=date_to))

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