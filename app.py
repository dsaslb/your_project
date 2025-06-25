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
from sqlalchemy import func, case, extract
from calendar import monthrange

from config import config_by_name
from extensions import db, migrate, login_manager, csrf, limiter, cache
from models import User, Schedule, CleaningPlan, Report, Notification, Notice, Order, Attendance, AttendanceEvaluation, AttendanceReport, ReasonTemplate

# Import notification functions
from utils.notify import (
    send_notification_enhanced, 
    send_admin_only_notification,
    send_notification_to_role,
    send_kakao,
    send_email
)

# Import new utility functions
from utils.report import generate_attendance_report_pdf
from utils.pay_transfer import transfer_salary

# Import security functions
from utils.security import (
    password_strong, log_security_event, check_account_lockout,
    handle_failed_login, reset_login_attempts, sanitize_input,
    validate_email, validate_phone, get_client_ip, is_suspicious_request
)

# Import file utility functions
from utils.file_utils import cleanup_old_backups, compress_backup_files, send_backup_notification

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

# Register Route Blueprints
# Blueprint registration will be added when needed

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
        func.sum(case((Attendance.status == 'late', 1), else_=0)).label('total_late'),
        func.sum(case((Attendance.status == 'absent', 1), else_=0)).label('total_absent')
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
        days = [(start_date + timedelta(days=i)) for i in range((end_date - start_date).days + 1)]
        
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
        selected_user=user,
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
        filename = f"근태리포트_{user.username}_{date_from}_{date_to}.pdf"
        
        # 응답 생성
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        flash(f'PDF 생성 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('staff_attendance_report', user_id=user_id, from_=date_from, to=date_to))

@app.route('/staff_attendance_report', methods=['GET', 'POST'])
@login_required
def staff_attendance_report():
    """직원 근태 리포트/평가"""
    from datetime import date, timedelta
    from utils.notify import send_notification_enhanced, send_notification_to_role
    
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

        # --- 근태 리포트 알림 자동 발송 ---
        pdf_link = url_for('staff_attendance_report_pdf') + f'?user_id={user_id}'
        noti_content = f"{date_from}~{date_to} 근태 평가 리포트가 등록되었습니다."
        send_notification_enhanced(
            user_id=user_id,
            content=noti_content,
            category="근무",
            link=pdf_link
        )
        send_notification_to_role(
            role='admin',
            content=f"[{selected_user.username}] {noti_content}",
            category="근무",
            link=pdf_link
        )

        # --- 카카오톡/이메일 자동 전송 ---
        kakao_msg = f"{selected_user.username}님, {date_from}~{date_to} 근태 평가 리포트가 등록되었습니다.\n결과 확인: {pdf_link}"
        send_kakao(selected_user, kakao_msg)
        # 이메일(PDF 첨부)
        subject = "근태 평가 리포트"
        body = f"{selected_user.username}님, {date_from}~{date_to} 근태 평가 리포트가 등록되었습니다.\n결과 확인: {pdf_link}"
        try:
            # PDF 생성 로직 제거 (html_content 변수 오류 해결)
            send_email(selected_user, subject, body)
        except Exception as e:
            print(f"이메일 전송 오류: {e}")
    
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
        for i, col in enumerate(df.columns.values):
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

@app.route('/admin/bulk_send_report', methods=['POST'])
@login_required
def bulk_send_report():
    if not current_user.is_admin():
        return "권한없음", 403
    from datetime import timedelta
    from utils.notify import send_notification_enhanced, send_notification_to_role, send_kakao, send_email
    import pdfkit
    date_from = request.form.get('from')
    date_to = request.form.get('to')
    users = User.query.filter_by(role='employee', status='approved').all()
    for user in users:
        # 근태 기록 조회
        records = Attendance.query.filter(
            Attendance.user_id == user.id,
            Attendance.clock_in >= date_from,
            Attendance.clock_in <= date_to + ' 23:59:59'
        ).order_by(Attendance.clock_in.desc()).all()
        total_days = len(records)
        late_count = sum(1 for r in records if r.status and '지각' in r.status)
        early_leave_count = sum(1 for r in records if r.status and '조퇴' in r.status)
        overtime_count = sum(1 for r in records if r.clock_out and r.clock_out.time() > timedelta(hours=18).total_seconds())
        normal_count = sum(1 for r in records if r.status == '정상')
        # 점수/등급 계산
        score = 100
        if total_days > 0:
            score -= late_count * 5
            score -= early_leave_count * 3
            overtime_bonus = min(overtime_count * 2, 10)
            score += overtime_bonus
            normal_bonus = min(normal_count * 1, 20)
            score += normal_bonus
        score = max(0, min(100, score))
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
        # 코멘트(기존 평가 있으면 유지)
        evaluation = AttendanceReport.query.filter_by(
            user_id=user.id,
            period_from=date_from,
            period_to=date_to
        ).first()
        comment = evaluation.comment if evaluation else ''
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
                user_id=user.id,
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
        # 알림/카톡/메일
        pdf_link = url_for('staff_attendance_report_pdf') + f'?user_id={user.id}'
        noti_content = f"{date_from}~{date_to} 근태 평가 리포트가 등록되었습니다."
        send_notification_enhanced(
            user_id=user.id,
            content=noti_content,
            category="근무",
            link=pdf_link
        )
        send_notification_to_role(
            role='admin',
            content=f"[{user.username}] {noti_content}",
            category="근무",
            link=pdf_link
        )
        kakao_msg = f"{user.username}님, {date_from}~{date_to} 근태 평가 리포트가 등록되었습니다.\n결과 확인: {pdf_link}"
        send_kakao(user, kakao_msg)
        subject = "근태 평가 리포트"
        body = f"{user.username}님, {date_from}~{date_to} 근태 평가 리포트가 등록되었습니다.\n결과 확인: {pdf_link}"
        try:
            # PDF 생성 로직 제거 (html_content 변수 오류 해결)
            send_email(user, subject, body)
        except Exception as e:
            print(f"이메일 전송 오류: {e}")
    return "일괄 발송 완료"

@app.route('/attendance_dashboard', methods=['GET'])
def attendance_dashboard():
    from datetime import date
    from calendar import monthrange
    
    users = User.query.all()
    user_id = int(request.args.get('user_id', 0)) or users[0].id
    today = date.today()
    y, m = today.year, today.month
    date_from = request.args.get('from', f"{y}-{m:02d}-01")
    date_to = request.args.get('to', f"{y}-{m:02d}-{monthrange(y,m)[1]:02d}")
    
    records = Attendance.query.filter(
        Attendance.user_id==user_id,
        Attendance.clock_in >= date_from,
        Attendance.clock_in <= date_to + ' 23:59:59'
    ).order_by(Attendance.clock_in).all()
    
    total = len(records)
    late = sum(r.is_late for r in records)
    early = sum(r.is_early_leave for r in records)
    ot = sum(r.is_overtime for r in records)
    normal = total - late - early
    
    daily = {r.clock_in.date().strftime('%Y-%m-%d'): {
        'late': r.is_late, 'early': r.is_early_leave, 'ot': r.is_overtime
    } for r in records if r.clock_in}
    
    summary = {
        '총근무일': total,
        '정상출근': normal,
        '지각': late,
        '조퇴': early,
        '야근': ot
    }
    
    # 사유 템플릿 조회
    reason_templates = ReasonTemplate.query.filter_by(is_active=True).order_by(ReasonTemplate.text).all()
    
    # 선택된 사용자 정보
    user = User.query.get(user_id)
    
    return render_template('attendance_dashboard.html',
        users=users, user_id=user_id, date_from=date_from, date_to=date_to,
        summary=summary, records=records, daily=daily,
        reason_templates=reason_templates, user=user)

@app.route('/staff/<int:user_id>/attendance_report/pdf')
@login_required
def staff_attendance_report_pdf_individual(user_id):
    """직원별 개별 근태 리포트 PDF 다운로드"""
    from datetime import date
    from calendar import monthrange
    
    # 권한 확인 (관리자만 가능)
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('staff_attendance_report'))
    
    # 날짜 범위 설정
    y, m = date.today().year, date.today().month
    date_from = request.args.get('from', f"{y}-{m:02d}-01")
    date_to = request.args.get('to', f"{y}-{m:02d}-{monthrange(y,m)[1]:02d}")
    
    # 근태 기록 조회
    records = Attendance.query.filter(
        Attendance.user_id == user_id,
        Attendance.clock_in >= date_from,
        Attendance.clock_in <= date_to + ' 23:59:59'
    ).order_by(Attendance.clock_in).all()
    
    user = User.query.get(user_id)
    if not user:
        flash('사용자를 찾을 수 없습니다.', 'error')
        return redirect(url_for('staff_attendance_report'))
    
    # HTML 렌더링
    html = render_template('staff/attendance_report_pdf.html', 
                          user=user, records=records, date_from=date_from, date_to=date_to)
    
    # PDF 생성
    import pdfkit, io
    pdf = pdfkit.from_string(html, False)
    
    return send_file(io.BytesIO(pdf), 
                    download_name=f"{user.username}_근태리포트.pdf", 
                    as_attachment=True)

@app.route('/staff/<int:user_id>/attendance_report/excel')
@login_required
def staff_attendance_report_excel_individual(user_id):
    """직원별 개별 근태 리포트 Excel 다운로드"""
    from datetime import date
    from calendar import monthrange
    import pandas as pd, io
    
    # 권한 확인 (관리자만 가능)
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('staff_attendance_report'))
    
    # 날짜 범위 설정
    y, m = date.today().year, date.today().month
    date_from = request.args.get('from', f"{y}-{m:02d}-01")
    date_to = request.args.get('to', f"{y}-{m:02d}-{monthrange(y,m)[1]:02d}")
    
    # 근태 기록 조회
    records = Attendance.query.filter(
        Attendance.user_id == user_id,
        Attendance.clock_in >= date_from,
        Attendance.clock_in <= date_to + ' 23:59:59'
    ).order_by(Attendance.clock_in).all()
    
    user = User.query.get(user_id)
    if not user:
        flash('사용자를 찾을 수 없습니다.', 'error')
        return redirect(url_for('staff_attendance_report'))
    
    # DataFrame 생성
    df = pd.DataFrame([{
        '날짜': r.clock_in.date() if r.clock_in else None,
        '출근': r.clock_in.strftime('%H:%M') if r.clock_in else '',
        '퇴근': r.clock_out.strftime('%H:%M') if r.clock_out else '',
        '지각': 'O' if r.is_late else '',
        '조퇴': 'O' if r.is_early_leave else '',
        '야근': 'O' if r.is_overtime else '',
        '사유': r.reason or ''
    } for r in records])
    
    # Excel 파일 생성
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    
    return send_file(output, 
                    download_name=f"{user.username}_근태리포트.xlsx", 
                    as_attachment=True)

@app.route('/attendance/<int:rid>/reason', methods=['POST'])
@login_required
def update_attendance_reason(rid):
    """근태 사유 수정"""
    from datetime import date, timedelta
    
    # 권한 확인 (관리자/매니저만 가능)
    if session.get('role') not in ('admin', 'manager'):
        flash('권한이 없습니다.', 'error')
        return redirect(request.referrer or url_for('attendance_dashboard'))
    
    # 근태 기록 조회
    attendance = Attendance.query.get_or_404(rid)
    old_reason = attendance.reason
    new_reason = request.form.get('reason', '').strip()
    
    attendance.reason = new_reason
    db.session.commit()
    
    # 사유 템플릿 자동 저장 (새로운 사유인 경우)
    if new_reason and not ReasonTemplate.query.filter_by(text=new_reason).first():
        template = ReasonTemplate(
            text=new_reason,
            created_by=current_user.id
        )
        db.session.add(template)
        db.session.commit()
    
    # 사유별 누적 카운트 체크 (예: '지각' 3회 이상)
    if new_reason and "지각" in new_reason:
        cnt = Attendance.query.filter(
            Attendance.user_id == attendance.user_id,
            Attendance.reason.like('%지각%'),
            Attendance.clock_in >= (date.today() - timedelta(days=30))
        ).count()
        
        if cnt >= 3:
            # 알림 생성
            notification = Notification(
                user_id=attendance.user_id,
                content=f"최근 한 달간 '지각' 사유가 {cnt}회 발생했습니다. 주의하세요!",
                category="근무",
                link="/attendance_dashboard"
            )
            db.session.add(notification)
            db.session.commit()
    
    flash('사유가 업데이트되었습니다.', 'success')
    return redirect(request.referrer or url_for('attendance_dashboard'))

@app.route('/attendance_dashboard/excel')
def attendance_dashboard_excel():
    user_id = int(request.args['user_id'])
    date_from = request.args['from']
    date_to = request.args['to']
    records = Attendance.query.filter(
        Attendance.user_id==user_id,
        Attendance.clock_in >= date_from,
        Attendance.clock_in <= date_to + ' 23:59:59'
    ).order_by(Attendance.clock_in).all()
    import pandas as pd, io
    df = pd.DataFrame([{
        '날짜': r.clock_in.date() if r.clock_in else None,
        '출근': r.clock_in.strftime('%H:%M') if r.clock_in else '',
        '퇴근': r.clock_out.strftime('%H:%M') if r.clock_out else '',
        '지각': 'O' if r.is_late else '',
        '조퇴': 'O' if r.is_early_leave else '',
        '야근': 'O' if r.is_overtime else '',
        '사유': r.reason or ''
    } for r in records])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, download_name="attendance_dashboard.xlsx", as_attachment=True)

@app.route('/attendance_dashboard/pdf')
def attendance_dashboard_pdf():
    user_id = int(request.args['user_id'])
    date_from = request.args['from']
    date_to = request.args['to']
    records = Attendance.query.filter(
        Attendance.user_id==user_id,
        Attendance.clock_in >= date_from,
        Attendance.clock_in <= date_to + ' 23:59:59'
    ).order_by(Attendance.clock_in).all()
    html = render_template('attendance_dashboard_pdf.html', records=records)
    import pdfkit
    pdf = pdfkit.from_string(html, False)
    import io
    return send_file(io.BytesIO(pdf), download_name="attendance_dashboard.pdf", as_attachment=True)

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

@app.route('/admin/attendance_monthly_stats')
def admin_attendance_monthly_stats():
    from datetime import date
    from calendar import monthrange
    today = date.today()
    y, m = today.year, today.month
    date_from = f"{y}-{m:02d}-01"
    date_to = f"{y}-{m:02d}-{monthrange(y,m)[1]:02d}"
    users = User.query.all()
    stats = []
    for u in users:
        records = Attendance.query.filter(
            Attendance.user_id==u.id,
            Attendance.clock_in >= date_from,
            Attendance.clock_in <= date_to + ' 23:59:59'
        ).all()
        total = len(records)
        late = sum(r.is_late for r in records)
        early = sum(r.is_early_leave for r in records)
        ot = sum(r.is_overtime for r in records)
        normal = total - late - early
        late_rate = round(100 * late / total, 1) if total else 0
        attend_rate = round(100 * normal / total, 1) if total else 0
        early_rate = round(100 * early / total, 1) if total else 0
        ot_rate = round(100 * ot / total, 1) if total else 0
        stats.append({
            "username": u.username,
            "total": total,
            "normal": normal,
            "late": late,
            "early": early,
            "ot": ot,
            "late_rate": late_rate,
            "attend_rate": attend_rate,
            "early_rate": early_rate,
            "ot_rate": ot_rate,
        })
    return render_template('admin/attendance_monthly_stats.html', stats=stats, date_from=date_from, date_to=date_to)

@app.route('/admin/attendance_monthly_stats/excel')
def admin_attendance_monthly_stats_excel():
    from datetime import date
    from calendar import monthrange
    import pandas as pd, io
    today = date.today()
    y, m = today.year, today.month
    date_from = f"{y}-{m:02d}-01"
    date_to = f"{y}-{m:02d}-{monthrange(y,m)[1]:02d}"
    users = User.query.all()
    rows = []
    for u in users:
        records = Attendance.query.filter(
            Attendance.user_id==u.id,
            Attendance.clock_in >= date_from,
            Attendance.clock_in <= date_to + ' 23:59:59'
        ).all()
        total = len(records)
        late = sum(r.is_late for r in records)
        early = sum(r.is_early_leave for r in records)
        ot = sum(r.is_overtime for r in records)
        normal = total - late - early
        late_rate = round(100 * late / total, 1) if total else 0
        attend_rate = round(100 * normal / total, 1) if total else 0
        early_rate = round(100 * early / total, 1) if total else 0
        ot_rate = round(100 * ot / total, 1) if total else 0
        rows.append({
            "직원명": u.username,
            "총근무": total,
            "정상출근": normal,
            "지각": late,
            "조퇴": early,
            "야근": ot,
            "지각률(%)": late_rate,
            "출근률(%)": attend_rate,
            "조퇴률(%)": early_rate,
            "야근률(%)": ot_rate,
        })
    df = pd.DataFrame(rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, download_name="attendance_monthly_report.xlsx", as_attachment=True)

@app.route('/admin/attendance_monthly_stats/pdf')
def admin_attendance_monthly_stats_pdf():
    from datetime import date
    from calendar import monthrange
    today = date.today()
    y, m = today.year, today.month
    date_from = f"{y}-{m:02d}-01"
    date_to = f"{y}-{m:02d}-{monthrange(y,m)[1]:02d}"
    users = User.query.all()
    stats = []
    for u in users:
        records = Attendance.query.filter(
            Attendance.user_id==u.id,
            Attendance.clock_in >= date_from,
            Attendance.clock_in <= date_to + ' 23:59:59'
        ).all()
        total = len(records)
        late = sum(r.is_late for r in records)
        early = sum(r.is_early_leave for r in records)
        ot = sum(r.is_overtime for r in records)
        normal = total - late - early
        late_rate = round(100 * late / total, 1) if total else 0
        attend_rate = round(100 * normal / total, 1) if total else 0
        early_rate = round(100 * early / total, 1) if total else 0
        ot_rate = round(100 * ot / total, 1) if total else 0
        stats.append({
            "username": u.username,
            "total": total,
            "normal": normal,
            "late": late,
            "early": early,
            "ot": ot,
            "late_rate": late_rate,
            "attend_rate": attend_rate,
            "early_rate": early_rate,
            "ot_rate": ot_rate,
        })
    html = render_template('admin/attendance_monthly_stats_pdf.html', stats=stats, date_from=date_from, date_to=date_to)
    import pdfkit, io
    pdf = pdfkit.from_string(html, False)
    return send_file(io.BytesIO(pdf), download_name="attendance_monthly_report.pdf", as_attachment=True)

@app.route('/admin/attendance_reason_stats')
@login_required
def admin_attendance_reason_stats():
    """근태 사유별 통계"""
    from datetime import date
    from calendar import monthrange
    from sqlalchemy import func
    
    # 권한 확인
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # 이번달 기본
    today = date.today()
    y, m = today.year, today.month
    date_from = request.args.get('from', f"{y}-{m:02d}-01")
    date_to = request.args.get('to', f"{y}-{m:02d}-{monthrange(y,m)[1]:02d}")
    
    # 사유별 집계
    reasons = db.session.query(
        Attendance.reason, func.count().label('count')
    ).filter(
        Attendance.clock_in >= date_from,
        Attendance.clock_in <= date_to + ' 23:59:59',
        Attendance.reason != None,
        Attendance.reason != ""
    ).group_by(Attendance.reason).order_by(func.count().desc()).all()
    
    # 직원별 사유 리스트
    staff_reasons = db.session.query(
        User.username, Attendance.clock_in, Attendance.reason
    ).join(User, User.id == Attendance.user_id).filter(
        Attendance.clock_in >= date_from,
        Attendance.clock_in <= date_to + ' 23:59:59',
        Attendance.reason != None,
        Attendance.reason != ""
    ).order_by(Attendance.clock_in.desc()).all()
    
    return render_template('admin/attendance_reason_stats.html',
        reasons=reasons, staff_reasons=staff_reasons, date_from=date_from, date_to=date_to)

@app.route('/admin/attendance_reason_stats/excel')
@login_required
def admin_attendance_reason_stats_excel():
    """사유별 통계 Excel 다운로드"""
    from datetime import date
    from calendar import monthrange
    from sqlalchemy import func
    import pandas as pd, io
    
    # 권한 확인
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # 이번달 기본
    today = date.today()
    y, m = today.year, today.month
    date_from = request.args.get('from', f"{y}-{m:02d}-01")
    date_to = request.args.get('to', f"{y}-{m:02d}-{monthrange(y,m)[1]:02d}")
    
    # 사유별 집계
    reasons = db.session.query(
        Attendance.reason, func.count().label('count')
    ).filter(
        Attendance.clock_in >= date_from,
        Attendance.clock_in <= date_to + ' 23:59:59',
        Attendance.reason != None,
        Attendance.reason != ""
    ).group_by(Attendance.reason).order_by(func.count().desc()).all()
    
    # 직원별 사유 리스트
    staff_reasons = db.session.query(
        User.username, Attendance.clock_in, Attendance.reason
    ).join(User, User.id == Attendance.user_id).filter(
        Attendance.clock_in >= date_from,
        Attendance.clock_in <= date_to + ' 23:59:59',
        Attendance.reason != None,
        Attendance.reason != ""
    ).order_by(Attendance.clock_in.desc()).all()
    
    # Excel 생성
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # 1. 사유별 집계 시트
        reason_rows = []
        total_count = sum(count for _, count in reasons)
        
        for reason, count in reasons:
            percentage = round(count / total_count * 100, 1) if total_count > 0 else 0
            reason_rows.append({
                "사유": reason,
                "건수": count,
                "비율(%)": percentage
            })
        
        df_reasons = pd.DataFrame(reason_rows)
        df_reasons.to_excel(writer, index=False, sheet_name='사유별집계')
        
        # 2. 직원별 상세 시트
        staff_rows = []
        for username, clock_in, reason in staff_reasons:
            staff_rows.append({
                "직원명": username,
                "날짜": clock_in.strftime('%Y-%m-%d') if clock_in else '-',
                "시간": clock_in.strftime('%H:%M') if clock_in else '-',
                "사유": reason
            })
        
        df_staff = pd.DataFrame(staff_rows)
        df_staff.to_excel(writer, index=False, sheet_name='직원별상세')
        
        # 워크북 및 워크시트 가져오기
        workbook = writer.book
        
        # 스타일 설정
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        # 사유별 집계 시트 스타일링
        worksheet1 = writer.sheets['사유별집계']
        for col_num, value in enumerate(df_reasons.columns.values):
            worksheet1.write(0, col_num, value, header_format)
        
        # 열 너비 자동 조정
        for i, col in enumerate(df_reasons.columns):
            max_len = max(df_reasons[col].astype(str).apply(len).max(), len(col)) + 2
            worksheet1.set_column(i, i, max_len)
        
        # 직원별 상세 시트 스타일링
        worksheet2 = writer.sheets['직원별상세']
        for col_num, value in enumerate(df_staff.columns.values):
            worksheet2.write(0, col_num, value, header_format)
        
        # 열 너비 자동 조정
        for i, col in enumerate(df_staff.columns):
            max_len = max(df_staff[col].astype(str).apply(len).max(), len(col)) + 2
            worksheet2.set_column(i, i, max_len)
    
    output.seek(0)
    return send_file(output, download_name=f"attendance_reason_stats_{date_from}_{date_to}.xlsx", as_attachment=True)

@app.route('/admin/attendance_reason_stats/pdf')
@login_required
def admin_attendance_reason_stats_pdf():
    """사유별 통계 PDF 다운로드"""
    from datetime import date
    from calendar import monthrange
    from sqlalchemy import func
    import pdfkit, io
    
    # 권한 확인
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # 이번달 기본
    today = date.today()
    y, m = today.year, today.month
    date_from = request.args.get('from', f"{y}-{m:02d}-01")
    date_to = request.args.get('to', f"{y}-{m:02d}-{monthrange(y,m)[1]:02d}")
    
    # 사유별 집계
    reasons = db.session.query(
        Attendance.reason, func.count().label('count')
    ).filter(
        Attendance.clock_in >= date_from,
        Attendance.clock_in <= date_to + ' 23:59:59',
        Attendance.reason != None,
        Attendance.reason != ""
    ).group_by(Attendance.reason).order_by(func.count().desc()).all()
    
    # 직원별 사유 리스트
    staff_reasons = db.session.query(
        User.username, Attendance.clock_in, Attendance.reason
    ).join(User, User.id == Attendance.user_id).filter(
        Attendance.clock_in >= date_from,
        Attendance.clock_in <= date_to + ' 23:59:59',
        Attendance.reason != None,
        Attendance.reason != ""
    ).order_by(Attendance.clock_in.desc()).all()
    
    html = render_template('admin/attendance_reason_stats_pdf.html',
        reasons=reasons, staff_reasons=staff_reasons, date_from=date_from, date_to=date_to)
    
    pdf = pdfkit.from_string(html, False)
    return send_file(io.BytesIO(pdf), download_name=f"attendance_reason_stats_{date_from}_{date_to}.pdf", as_attachment=True)

# 사유 템플릿 관리 (관리자만)
@app.route('/admin/reason_templates', methods=['GET', 'POST'])
@login_required
def admin_reason_templates():
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        text = request.form['text'].strip()
        team = request.form.get('team', '').strip()
        
        if text and not ReasonTemplate.query.filter_by(text=text, team=team or None).first():
            template = ReasonTemplate(
                text=text,
                team=team or None,
                created_by=current_user.id
            )
            db.session.add(template)
            db.session.commit()
            flash('사유 템플릿이 추가되었습니다.', 'success')
            return redirect(url_for('admin_reason_templates'))
        else:
            flash('이미 존재하는 템플릿입니다.', 'error')
    
    templates = ReasonTemplate.query.filter_by(is_active=True).order_by(ReasonTemplate.text).all()
    return render_template('admin/reason_templates.html', templates=templates)

@app.route('/admin/reason_templates/delete/<int:tid>', methods=['POST'])
@login_required
def delete_reason_template(tid):
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    template = ReasonTemplate.query.get_or_404(tid)
    db.session.delete(template)
    db.session.commit()
    flash('사유 템플릿이 삭제되었습니다.', 'success')
    return redirect(url_for('admin_reason_templates'))

# AI 사유 추천 함수 (정교화)
def ai_recommend_reason(user, date_):
    """AI 사유 추천 (정교화된 패턴 분석)"""
    import calendar
    from collections import Counter
    
    if not user:
        return ""
    
    dow = calendar.day_name[date_.weekday()]
    
    # 1. 최근 10회 입력한 사유 중 최빈값
    last_reasons = []
    recent_attendances = Attendance.query.filter_by(user_id=user.id)\
        .order_by(Attendance.clock_in.desc()).limit(10).all()
    
    for att in recent_attendances:
        if att.reason and att.reason.strip():
            last_reasons.append(att.reason.strip())
    
    if last_reasons:
        counter = Counter(last_reasons)
        most_common = counter.most_common(1)
        if most_common and most_common[0][1] >= 2:  # 2회 이상 사용된 사유
            return most_common[0][0]
    
    # 2. 요일 기반 추천
    if dow == 'Monday':
        return "월요일 컨디션 저하"
    elif dow == 'Friday':
        return "금요일 야근"
    elif dow == 'Wednesday':
        return "수요일 중간점검"
    elif dow == 'Tuesday':
        return "화요일 업무 집중"
    elif dow == 'Thursday':
        return "목요일 업무 마무리"
    
    # 3. 계절/월별 패턴 (예시)
    month = date_.month
    if month in [12, 1, 2]:  # 겨울
        return "겨울철 교통 지연"
    elif month in [6, 7, 8]:  # 여름
        return "여름철 컨디션 저하"
    
    return ""

# 모바일 API - 사유 템플릿 제공
@app.route('/api/mobile/reason_templates')
def api_mobile_reason_templates():
    team = request.args.get('team')
    q = ReasonTemplate.query.filter_by(is_active=True)
    if team:
        q = q.filter_by(team=team)
    templates = q.all()
    return jsonify([t.text for t in templates])

# 모바일 API - 사유 업데이트
@app.route('/api/mobile/attendance_reason', methods=['POST'])
def api_mobile_attendance_reason():
    data = request.json
    rid = data.get('rid')
    reason = data.get('reason', '').strip()
    
    # 모바일 인증 체크 (실제 구현시 토큰 검증 추가)
    attendance = Attendance.query.get(rid)
    if not attendance:
        return jsonify({'result': 'error', 'message': '근태 기록을 찾을 수 없습니다.'}), 404
    
    attendance.reason = reason
    db.session.commit()
    
    return jsonify({'result': 'ok', 'message': '사유가 업데이트되었습니다.'})

# AJAX 실시간 사유 편집 API
@app.route('/api/attendance/<int:rid>/reason', methods=['POST'])
def api_attendance_reason_edit(rid):
    """AJAX 실시간 사유 편집"""
    from datetime import date, timedelta
    
    # 권한 확인
    if session.get('role') not in ('admin', 'manager', 'teamlead'):
        return jsonify({'result': 'fail', 'msg': '권한없음'})
    
    # 근태 기록 조회
    attendance = Attendance.query.get_or_404(rid)
    data = request.get_json()
    new_reason = data.get('reason', '').strip()
    
    # 사유 업데이트
    attendance.reason = new_reason
    db.session.commit()
    
    # 사유 템플릿 자동 저장 (새로운 사유인 경우)
    if new_reason and not ReasonTemplate.query.filter_by(text=new_reason).first():
        template = ReasonTemplate(
            text=new_reason,
            created_by=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(template)
        db.session.commit()
    
    # 사유별 누적 카운트 체크 (예: '지각' 3회 이상)
    if new_reason and "지각" in new_reason:
        cnt = Attendance.query.filter(
            Attendance.user_id == attendance.user_id,
            Attendance.reason.like('%지각%'),
            Attendance.clock_in >= (date.today() - timedelta(days=30))
        ).count()
        
        if cnt >= 3:
            # 알림 생성
            notification = Notification(
                user_id=attendance.user_id,
                content=f"최근 한 달간 '지각' 사유가 {cnt}회 발생했습니다. 주의하세요!",
                category="근무",
                link="/attendance_dashboard"
            )
            db.session.add(notification)
            db.session.commit()
    
    return jsonify({'result': 'ok', 'msg': '사유가 업데이트되었습니다.'})

# 팀장용 사유 템플릿 관리 (팀별 권한)
@app.route('/teamlead/reason_templates', methods=['GET', 'POST'])
@login_required
def teamlead_reason_templates():
    """팀장용 사유 템플릿 관리"""
    if session.get('role') != 'teamlead':
        flash('팀장 권한이 필요합니다.', 'error')
        return redirect(url_for('dashboard'))
    
    team = session.get('team')
    if not team:
        flash('팀 정보가 없습니다.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        text = request.form['text'].strip()
        
        if text and not ReasonTemplate.query.filter_by(text=text, team=team).first():
            template = ReasonTemplate(
                text=text,
                team=team,
                created_by=current_user.id
            )
            db.session.add(template)
            db.session.commit()
            flash('사유 템플릿이 추가되었습니다.', 'success')
            return redirect(url_for('teamlead_reason_templates'))
        else:
            flash('이미 존재하는 템플릿입니다.', 'error')
    
    # 해당 팀의 템플릿만 조회
    templates = ReasonTemplate.query.filter_by(team=team, is_active=True).order_by(ReasonTemplate.text).all()
    return render_template('teamlead/reason_templates.html', templates=templates, team=team)

@app.route('/teamlead/reason_templates/delete/<int:tid>', methods=['POST'])
@login_required
def teamlead_delete_reason_template(tid):
    """팀장용 템플릿 삭제"""
    if session.get('role') != 'teamlead':
        flash('팀장 권한이 필요합니다.', 'error')
        return redirect(url_for('dashboard'))
    
    template = ReasonTemplate.query.get_or_404(tid)
    
    # 본인 팀의 템플릿만 삭제 가능
    if template.team != session.get('team'):
        flash('다른 팀의 템플릿은 삭제할 수 없습니다.', 'error')
        return redirect(url_for('teamlead_reason_templates'))
    
    db.session.delete(template)
    db.session.commit()
    flash('사유 템플릿이 삭제되었습니다.', 'success')
    return redirect(url_for('teamlead_reason_templates'))

# 템플릿별 사용 빈도 통계 (차트 포함)
@app.route('/admin/reason_template_stats')
@login_required
def admin_reason_template_stats():
    """사유 템플릿별 사용 빈도 통계 (차트 포함)"""
    from sqlalchemy import func
    
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # 팀별 필터링
    team = request.args.get('team')
    
    # 사유별 빈도 집계
    q = db.session.query(
        ReasonTemplate.text, 
        ReasonTemplate.team,
        func.count(Attendance.id).label('usage_count')
    ).outerjoin(
        Attendance, 
        Attendance.reason == ReasonTemplate.text
    ).filter(
        ReasonTemplate.is_active == True
    )
    
    if team:
        q = q.filter(ReasonTemplate.team == team)
    
    stats = q.group_by(ReasonTemplate.text, ReasonTemplate.team)\
        .order_by(func.count(Attendance.id).desc()).all()
    
    # 팀 목록 (필터용)
    teams = db.session.query(ReasonTemplate.team)\
        .filter(ReasonTemplate.team.isnot(None))\
        .distinct().all()
    teams = [t[0] for t in teams]
    
    return render_template('admin/reason_template_stats.html', 
                         stats=stats, teams=teams, current_team=team)

# 최다 사유 TOP5, 팀별 인기 사유
@app.route('/admin/reason_top5')
@login_required
def admin_reason_top5():
    """최다 사유 TOP5, 팀별 인기 사유"""
    from sqlalchemy import func
    
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    team = request.args.get('team')
    
    # 전체 최다 사유 TOP5
    q = db.session.query(
        Attendance.reason, 
        func.count().label('count')
    ).filter(
        Attendance.reason != None, 
        Attendance.reason != ""
    )
    
    if team:
        q = q.join(User, User.id == Attendance.user_id).filter(User.team == team)
    
    top5 = q.group_by(Attendance.reason)\
        .order_by(func.count().desc()).limit(5).all()
    
    # 팀별 인기 사유 (전체)
    team_stats = db.session.query(
        User.team,
        Attendance.reason,
        func.count().label('count')
    ).join(
        User, User.id == Attendance.user_id
    ).filter(
        Attendance.reason != None,
        Attendance.reason != "",
        User.team.isnot(None)
    ).group_by(
        User.team, Attendance.reason
    ).order_by(
        User.team, func.count().desc()
    ).all()
    
    # 팀별로 TOP3 정리
    team_top3 = {}
    for t, r, c in team_stats:
        if t not in team_top3:
            team_top3[t] = []
        if len(team_top3[t]) < 3:
            team_top3[t].append((r, c))
    
    return render_template('admin/reason_top5.html', 
                         top5=top5, team=team, team_top3=team_top3)

# AI 기반 템플릿 자동 추천 (정교화)
def ai_recommend_reason_template(user, date_):
    """AI 기반 템플릿 자동 추천 (빈도+팀별+요일)"""
    from collections import Counter
    import calendar
    
    if not user:
        return ""
    
    # 1. 최근 본인 사용 최빈 사유
    last_personal = []
    recent_attendances = Attendance.query.filter_by(user_id=user.id)\
        .order_by(Attendance.clock_in.desc()).limit(10).all()
    
    for att in recent_attendances:
        if att.reason and att.reason.strip():
            last_personal.append(att.reason.strip())
    
    if last_personal:
        counter = Counter(last_personal)
        most_common = counter.most_common(1)
        if most_common and most_common[0][1] >= 2:  # 2회 이상 사용
            return most_common[0][0]
    
    # 2. 같은 팀 최빈 사유
    if hasattr(user, 'team') and user.team:
        team = user.team
        team_attendances = db.session.query(Attendance.reason)\
            .join(User, User.id == Attendance.user_id)\
            .filter(User.team == team)\
            .order_by(Attendance.clock_in.desc()).limit(20).all()
        
        team_reasons = [r[0] for r in team_attendances if r[0] and r[0].strip()]
        if team_reasons:
            counter = Counter(team_reasons)
            most_common = counter.most_common(1)
            if most_common:
                return most_common[0][0]
    
    # 3. 요일별 사유
    dow = calendar.day_name[date_.weekday()]
    if dow == 'Monday':
        return "월요일 컨디션 저하"
    elif dow == 'Friday':
        return "금요일 야근"
    elif dow == 'Wednesday':
        return "수요일 중간점검"
    elif dow == 'Tuesday':
        return "화요일 업무 집중"
    elif dow == 'Thursday':
        return "목요일 업무 마무리"
    
    return ""

# 모바일 인기 사유 API
@app.route('/api/mobile/reason_top', methods=['GET'])
def api_mobile_reason_top():
    """모바일 인기 사유 TOP5 API"""
    from sqlalchemy import func
    
    team = request.args.get('team')
    
    q = db.session.query(
        Attendance.reason, 
        func.count().label('count')
    ).filter(
        Attendance.reason != None, 
        Attendance.reason != ""
    )
    
    if team:
        q = q.join(User, User.id == Attendance.user_id).filter(User.team == team)
    
    top = q.group_by(Attendance.reason)\
        .order_by(func.count().desc()).limit(5).all()
    
    return jsonify([{'reason': r, 'count': c} for r, c in top])

# --- 새로운 기능: PDF 리포트 생성 ---
@app.route('/admin/attendance_report_pdf/<int:user_id>')
@login_required
def attendance_report_pdf(user_id):
    """지각/조퇴/야근 리포트 PDF 자동 생성"""
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    import os
    from datetime import datetime, time
    
    user = User.query.get(user_id)
    if not user:
        flash('사용자를 찾을 수 없습니다.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    now = datetime.utcnow()
    year, month = now.year, now.month

    STANDARD_CLOCKIN = time(9, 0, 0)
    STANDARD_CLOCKOUT = time(18, 0, 0)

    attendances = Attendance.query.filter(
        Attendance.user_id == user_id,
        extract('year', Attendance.clock_in) == year,
        extract('month', Attendance.clock_in) == month,
        Attendance.clock_out.isnot(None)
    ).all()
    
    lateness = early_leave = night_work = 0
    for att in attendances:
        if att.clock_in and att.clock_in.time() > STANDARD_CLOCKIN:
            lateness += 1
        if att.clock_out and att.clock_out.time() < STANDARD_CLOCKOUT:
            early_leave += 1
        if att.clock_out and att.clock_out.time() > time(21, 0, 0):
            night_work += 1

    filename = f"attendance_report_{user.username}_{year}_{month}.pdf"
    filepath = os.path.join('static', 'reports', filename)
    
    # static/reports 디렉토리가 없으면 생성
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    generate_attendance_report_pdf(filepath, user, month, year, lateness, early_leave, night_work)
    return redirect(url_for('static', filename=f'reports/{filename}'))

# --- 새로운 기능: 급여 자동이체 ---
@app.route('/admin/bulk_transfer')
@login_required
def bulk_transfer():
    """일괄 급여 이체 실행"""
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    year, month = datetime.utcnow().year, datetime.utcnow().month
    users = User.query.filter_by(status='approved').all()
    
    transfer_count = 0
    for user in users:
        # 해당 월 급여 계산
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
        
        # 자동이체(가상)
        if transfer_salary(user, wage):
            transfer_count += 1
            
            # 급여 지급 알림
            from utils.notify import send_notification_enhanced
            send_notification_enhanced(
                user_id=user.id,
                content=f"{year}년 {month}월 급여 {wage:,}원이 입금되었습니다.",
                category="급여",
                link=url_for('staff_attendance_report', user_id=user.id)
            )
    
    flash(f"일괄 급여 이체(가상) 실행 완료! {transfer_count}명에게 이체되었습니다.")
    return redirect(url_for('admin_dashboard'))

# --- 새로운 기능: 근태 이상 자동 알림 ---
@app.route('/admin/attendance_warnings')
@login_required
def attendance_warnings():
    """근태 이상 자동 알림 관리"""
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    from datetime import datetime, time
    
    now = datetime.utcnow()
    year, month = now.year, now.month
    
    STANDARD_CLOCKIN = time(9, 0, 0)
    STANDARD_CLOCKOUT = time(18, 0, 0)
    
    users = User.query.filter_by(status='approved').all()
    warning_users = []
    
    for user in users:
        attendances = Attendance.query.filter(
            Attendance.user_id == user.id,
            extract('year', Attendance.clock_in) == year,
            extract('month', Attendance.clock_in) == month,
            Attendance.clock_out.isnot(None)
        ).all()
        
        lateness = early_leave = night_work = 0
        for att in attendances:
            if att.clock_in and att.clock_in.time() > STANDARD_CLOCKIN:
                lateness += 1
            if att.clock_out and att.clock_out.time() < STANDARD_CLOCKOUT:
                early_leave += 1
            if att.clock_out and att.clock_out.time() > time(21, 0, 0):
                night_work += 1
        
        # 근태 이상 감지 (지각 2회 이상 또는 조퇴 3회 이상)
        if lateness >= 2 or early_leave >= 3:
            warning_users.append({
                'user': user,
                'lateness': lateness,
                'early_leave': early_leave,
                'night_work': night_work
            })
            
            # 자동 알림 발송
            from utils.notify import send_notification_enhanced
            warning_message = f"{year}년 {month}월 근태: 지각 {lateness}회, 조퇴 {early_leave}회, 야근 {night_work}회 발생."
            send_notification_enhanced(
                user_id=user.id,
                content=warning_message,
                category="근태",
                link=url_for('staff_attendance_report', user_id=user.id)
            )
    
    return render_template('admin/attendance_warnings.html', 
                         warning_users=warning_users,
                         year=year, month=month)



# --- Payroll Routes ---
@app.route('/payroll_pdf/<int:year>/<int:month>')
@login_required
def payroll_pdf(year, month):
    from utils.payroll import generate_payroll_pdf
    import os
    user = User.query.get(session['user_id'])
    records = Attendance.query.filter(
        Attendance.user_id == user.id,
        db.extract('year', Attendance.clock_in) == year,
        db.extract('month', Attendance.clock_in) == month,
        Attendance.clock_out.isnot(None)
    ).all()
    work_days = len(records)
    total_seconds = sum([(r.clock_out - r.clock_in).total_seconds() for r in records if r.clock_out])
    total_hours = int(total_seconds // 3600)
    wage = total_hours * 12000
    filename = f"payroll_{user.username}_{year}_{month}.pdf"
    filepath = os.path.join('static', filename)
    generate_payroll_pdf(filepath, user, month, year, work_days, total_hours, wage)
    return redirect(url_for('static', filename=filename))

# --- Shift Request Routes ---
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
        db.session.commit()
        flash("교대/근무 변경 신청이 접수되었습니다!")
        return redirect(url_for('shift_request'))
    requests = ShiftRequest.query.filter_by(user_id=user.id).order_by(ShiftRequest.created_at.desc()).all()
    return render_template('shift_request.html', requests=requests)

@app.route('/admin/shift_requests')
@login_required
def admin_shift_requests():
    if not current_user.is_admin():
        return redirect(url_for('index'))
    requests = ShiftRequest.query.order_by(ShiftRequest.created_at.desc()).all()
    return render_template('admin/shift_requests.html', requests=requests)

@app.route('/admin/shift_request_action/<int:request_id>/<action>')
@login_required
def shift_request_action(request_id, action):
    if not current_user.is_admin():
        return redirect(url_for('index'))
    req = ShiftRequest.query.get_or_404(request_id)
    if action == 'approve':
        req.status = 'approved'
        # 알림 전송
        send_notification_enhanced(req.user, f"{req.desired_date} 근무 변경이 승인되었습니다.", category='근무')
    elif action == 'reject':
        req.status = 'rejected'
        send_notification_enhanced(req.user, f"{req.desired_date} 근무 변경이 거절되었습니다.", category='근무')
    db.session.commit()
    flash("처리가 완료되었습니다.")
    return redirect(url_for('admin_shift_requests'))

# --- Calendar Route ---
@app.route('/calendar')
@login_required
def calendar():
    user = User.query.get(session['user_id'])
    # 출근/근무 변경 등 일정을 FullCalendar로 변환
    records = Attendance.query.filter_by(user_id=user.id).all()
    shift_reqs = ShiftRequest.query.filter_by(user_id=user.id, status='approved').all()
    events = []
    for rec in records:
        events.append({
            "title": "출근",
            "start": rec.clock_in.strftime('%Y-%m-%d'),
            "color": "#00aaff"
        })
    for req in shift_reqs:
        events.append({
            "title": "근무변경(승인)",
            "start": req.desired_date.strftime('%Y-%m-%d'),
            "color": "#ffbb00"
        })
    return render_template('calendar.html', events=events)

# 관리자 이메일 환경변수 또는 config에서 불러오기
ADMIN_EMAIL = getattr(app.config, 'ADMIN_EMAIL', 'admin@example.com')

@app.route('/admin/backup', methods=['GET'])
@login_required
@admin_required
def admin_backup():
    try:
        # ... 기존 백업 코드 ...
        # 백업 파일 생성 후 자동 정리/압축
        backup_dir = 'backups'
        cleanup_old_backups(backup_dir, days=30)
        compress_backup_files(backup_dir, compress_after_days=3)
        send_backup_notification(True, ADMIN_EMAIL, 'DB 백업이 성공적으로 완료되었습니다.')
        # (샘플) 클라우드 업로드: upload_backup_to_cloud(backup_path, 'mybucket', backup_filename)
        return send_file(backup_path, as_attachment=True, download_name=backup_filename, mimetype='application/octet-stream')
    except Exception as e:
        send_backup_notification(False, ADMIN_EMAIL, f'DB 백업 실패: {e}')
        # ... 기존 에러 처리 ...

@app.route('/admin/restore', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_restore():
    if request.method == 'POST':
        try:
            # ... 기존 복원 코드 ...
            # 복원 전 자동 백업, 정리/압축
            backup_dir = 'backups'
            cleanup_old_backups(backup_dir, days=30)
            compress_backup_files(backup_dir, compress_after_days=3)
            send_backup_notification(True, ADMIN_EMAIL, 'DB 복원이 성공적으로 완료되었습니다.')
            # (샘플) 클라우드 업로드: upload_backup_to_cloud(current_backup_path, 'mybucket', current_backup)
            # ...
        except Exception as e:
            send_backup_notification(False, ADMIN_EMAIL, f'DB 복원 실패: {e}')
            # ...

@app.route('/admin/file_backup', methods=['GET'])
@login_required
@admin_required
def admin_file_backup():
    try:
        # ... 기존 첨부파일 백업 코드 ...
        backup_dir = 'backups'
        cleanup_old_backups(backup_dir, days=30)
        compress_backup_files(backup_dir, compress_after_days=3)
        send_backup_notification(True, ADMIN_EMAIL, '첨부파일 백업이 성공적으로 완료되었습니다.')
        # (샘플) 클라우드 업로드: upload_backup_to_cloud(zip_path, 'mybucket', zip_filename)
        return send_file(zip_path, as_attachment=True, download_name=zip_filename, mimetype='application/zip')
    except Exception as e:
        send_backup_notification(False, ADMIN_EMAIL, f'첨부파일 백업 실패: {e}')
        # ...

@app.route('/admin/file_restore', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_file_restore():
    if request.method == 'POST':
        try:
            # ... 기존 첨부파일 복원 코드 ...
            backup_dir = 'backups'
            cleanup_old_backups(backup_dir, days=30)
            compress_backup_files(backup_dir, compress_after_days=3)
            send_backup_notification(True, ADMIN_EMAIL, '첨부파일 복원이 성공적으로 완료되었습니다.')
            # (샘플) 클라우드 업로드: upload_backup_to_cloud(current_backup_path, 'mybucket', current_backup)
            # ...
        except Exception as e:
            send_backup_notification(False, ADMIN_EMAIL, f'첨부파일 복원 실패: {e}')
            # ...

# --- 주기적 자동 백업용 Flask CLI 커맨드 ---
import click
@app.cli.command('auto-backup')
@click.option('--type', default='db', help='db/file/all')
def auto_backup(type):
    """주기적 자동 백업 실행 (crontab/스케줄러에서 호출)"""
    backup_dir = 'backups'
    try:
        if type in ('db', 'all'):
            # DB 백업 함수 호출 (기존 코드 재사용)
            # ...
            cleanup_old_backups(backup_dir, days=30)
            compress_backup_files(backup_dir, compress_after_days=3)
            send_backup_notification(True, ADMIN_EMAIL, '자동 DB 백업 성공')
        if type in ('file', 'all'):
            # 첨부파일 백업 함수 호출 (기존 코드 재사용)
            # ...
            cleanup_old_backups(backup_dir, days=30)
            compress_backup_files(backup_dir, compress_after_days=3)
            send_backup_notification(True, ADMIN_EMAIL, '자동 첨부파일 백업 성공')
    except Exception as e:
        send_backup_notification(False, ADMIN_EMAIL, f'자동 백업 실패: {e}')

if __name__ == '__main__':
    app.run(debug=True) 
 