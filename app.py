from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session, Response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import DevConfig
from extensions import db, migrate
from utils.logger import log_action
from werkzeug.exceptions import NotFound, InternalServerError
from datetime import datetime, date, timedelta
import pandas as pd
from flask import send_file
from io import BytesIO
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, ApproveLog, Attendance
from sqlalchemy import extract, func
from sqlalchemy.sql import func

app = Flask(__name__)
app.config.from_object(DevConfig)

db.init_app(app)
migrate.init_app(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 로그인 required 데코레이터 (간단 버전)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = User.query.get(session.get('user_id'))
        if not user or user.role != 'admin':
            flash("관리자 권한이 필요합니다.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- 인증/회원가입/로그인 ---
@app.route('/', methods=['GET'])
@login_required
def index():
    if current_user.is_admin():
        return redirect(url_for('admin_dashboard'))
    elif current_user.is_manager():
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password) and user.status == 'approved':
            session['user_id'] = user.id
            flash('로그인 성공!')
            return redirect(url_for('dashboard'))
        flash('로그인 실패! (아이디/비밀번호/승인상태 확인)')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('로그아웃되었습니다.')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('이미 존재하는 아이디입니다.')
            return redirect(url_for('register'))
        new_user = User(
            username=username,
            password=generate_password_hash(password),
            status='pending',
            role='employee'
        )
        db.session.add(new_user)
        db.session.commit()
        flash('가입 신청 완료! 관리자의 승인을 기다려주세요.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        current = request.form['current_password']
        new = request.form['new_password']
        if not check_password_hash(user.password, current):
            flash("현재 비밀번호가 틀렸습니다.")
            return redirect(url_for('change_password'))
        user.password = generate_password_hash(new)
        db.session.commit()
        flash("비밀번호가 성공적으로 변경되었습니다.")
        return redirect(url_for('dashboard'))
    return render_template('change_password.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.name = request.form['name']
        user.phone = request.form['phone']
        db.session.commit()
        flash("회원정보가 저장되었습니다.")
        return redirect(url_for('dashboard'))
    return render_template('profile.html', user=user)

# --- 직원 출퇴근 CRUD ---
@app.route('/dashboard')
@login_required
def dashboard():
    from models import Attendance
    records = Attendance.query.filter_by(user_id=current_user.id).order_by(Attendance.clock_in.desc()).all()
    return render_template('dashboard.html', records=records)

@app.route('/clock_in')
@login_required
def clock_in():
    user_id = session['user_id']
    today = Attendance.query.filter_by(user_id=user_id).order_by(Attendance.id.desc()).first()
    if today and today.clock_out is None:
        flash("이미 출근 처리되었습니다. 퇴근 버튼을 눌러주세요.")
        return redirect(url_for('dashboard'))
    attendance = Attendance(user_id=user_id)
    db.session.add(attendance)
    db.session.commit()
    flash("출근 처리 완료!")
    return redirect(url_for('dashboard'))

@app.route('/clock_out')
@login_required
def clock_out():
    user_id = session['user_id']
    today = Attendance.query.filter_by(user_id=user_id).order_by(Attendance.id.desc()).first()
    if not today or today.clock_out is not None:
        flash("출근 기록이 없거나 이미 퇴근 처리되었습니다.")
        return redirect(url_for('dashboard'))
    today.clock_out = datetime.utcnow()
    db.session.commit()
    flash("퇴근 처리 완료!")
    return redirect(url_for('dashboard'))

@app.route('/attendance')
@login_required
def attendance():
    user_id = session['user_id']
    records = Attendance.query.filter_by(user_id=user_id).order_by(Attendance.clock_in.desc()).all()
    return render_template('attendance.html', records=records)

# --- 관리자 대시보드/사용자 관리/승인/거절/액션로그 ---
@app.route('/admin')
@login_required
def admin_dashboard():
    from models import User, Attendance, Branch
    if not (current_user.is_admin() or current_user.is_manager()):
        return redirect(url_for('dashboard'))

    # 기간 필터 (기본: 이번 달)
    from_dt = request.args.get("from")
    to_dt = request.args.get("to")
    today = date.today()
    if not from_dt:
        first = datetime(today.year, today.month, 1)
    else:
        first = datetime.strptime(from_dt, "%Y-%m-%d")
    if not to_dt:
        last = (first + pd.offsets.MonthEnd()).to_pydatetime() + timedelta(days=1)
    else:
        last = datetime.strptime(to_dt, "%Y-%m-%d") + timedelta(days=1)

    # 전체/지점별 통계
    branches = Branch.query.all()
    users = User.query.filter(User.deleted_at == None, User.status == "approved").all()
    branch_names = [b.name for b in branches]

    # 1. 각 지점별 월별 근무시간
    result = []
    for branch in branches:
        branch_users = [u.id for u in users if u.branch_id == branch.id]
        attendances = Attendance.query.filter(
            Attendance.user_id.in_(branch_users),
            Attendance.clock_in >= first, Attendance.clock_in < last
        ).all()
        total_work = sum(a.work_minutes for a in attendances)
        total_late = sum(1 for a in attendances if a.status == "지각")
        total_absent = sum(1 for a in attendances if a.status == "결근")
        result.append({
            "branch": branch.name,
            "total_work": total_work,
            "total_late": total_late,
            "total_absent": total_absent,
            "user_count": len(branch_users)
        })

    # --- 기본 통계 ---
    num_users = User.query.filter(User.deleted_at == None, User.status == "approved").count()
    num_attendance = Attendance.query.count()
    
    # 월별 기록
    month_attendance = Attendance.query.filter(Attendance.clock_in >= first, Attendance.clock_in < last).all()
    users_dict = {u.id: u.username for u in User.query.filter(User.deleted_at == None)}

    # --- DataFrame 통계 ---
    data = []
    for a in month_attendance:
        data.append({
            "user": users_dict.get(a.user_id, '탈퇴'),
            "clock_in": a.clock_in,
            "clock_out": a.clock_out,
            "work_minutes": a.work_minutes,
            "status": a.status
        })
    df = pd.DataFrame(data)

    # --- 1. 월별 직원 근무시간 합계 ---
    if not df.empty:
        summary = df.groupby("user").agg(
            work_minutes_sum=("work_minutes", "sum"),
            late_count=("status", lambda x: (x=="지각").sum()),
            absent_count=("status", lambda x: (x=="결근").sum())
        ).reset_index()
        chart_labels = summary["user"].tolist()
        chart_data = summary["work_minutes_sum"].tolist()
    else:
        summary = pd.DataFrame()
        chart_labels = []
        chart_data = []

    # --- 2. 지각/결근 Top 3 랭킹 ---
    top_late = summary.sort_values('late_count', ascending=False).head(3) if not summary.empty else pd.DataFrame()
    top_absent = summary.sort_values('absent_count', ascending=False).head(3) if not summary.empty else pd.DataFrame()

    # --- 3. 트렌드 데이터 (일자별 근무시간) ---
    if not df.empty:
        df['date'] = pd.to_datetime(df['clock_in']).dt.date
        daily_work = df.groupby('date')['work_minutes'].sum().reset_index()
        trend_dates = [str(d) for d in daily_work['date']]
        trend_data = daily_work['work_minutes'].tolist()
    else:
        trend_dates = []
        trend_data = []

    # --- 4. 근무시간 분포 데이터 ---
    if not df.empty:
        dist_labels = ['8시간 미만', '8-9시간', '9-10시간', '10시간 이상']
        dist_data = [0, 0, 0, 0]
        for minutes in df['work_minutes']:
            hours = minutes / 60
            if hours < 8:
                dist_data[0] += 1
            elif hours < 9:
                dist_data[1] += 1
            elif hours < 10:
                dist_data[2] += 1
            else:
                dist_data[3] += 1
    else:
        dist_labels = ['8시간 미만', '8-9시간', '9-10시간', '10시간 이상']
        dist_data = [0, 0, 0, 0]

    # --- 5. 최근 출퇴근 이력 ---
    recent_attendances = Attendance.query.join(User).filter(
        User.deleted_at == None
    ).order_by(Attendance.clock_in.desc()).limit(10).all()
    
    recent = []
    for att in recent_attendances:
        user = User.query.get(att.user_id)
        recent.append({
            'user': user.username if user else '탈퇴',
            'clock_in': att.clock_in.strftime('%Y-%m-%d %H:%M') if att.clock_in else '',
            'clock_out': att.clock_out.strftime('%Y-%m-%d %H:%M') if att.clock_out else '',
            'work_minutes': att.work_minutes,
            'status': att.status
        })

    # --- 6. 경고 사용자 (지각 2회 이상/결근 발생) ---
    warn_users = []
    if not summary.empty:
        for _, row in summary.iterrows():
            if row['late_count'] >= 2 or row['absent_count'] > 0:
                warn_users.append(row['user'])

    return render_template('admin_dashboard.html', 
                         num_users=num_users, 
                         num_attendance=num_attendance,
                         chart_labels=chart_labels,
                         chart_data=chart_data,
                         top_late=top_late,
                         top_absent=top_absent,
                         result=result,
                         branch_names=branch_names,
                         trend_dates=trend_dates,
                         trend_data=trend_data,
                         dist_labels=dist_labels,
                         dist_data=dist_data,
                         recent=recent,
                         warn_users=warn_users,
                         from_dt=from_dt or first.strftime("%Y-%m-%d"),
                         to_dt=to_dt or (last - timedelta(days=1)).strftime("%Y-%m-%d"))

@app.route('/admin/users')
@login_required
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
    user = User.query.get_or_404(user_id)
    admin_id = session['user_id']
    if action == 'approve':
        user.status = 'approved'
        flash(f"{user.username} 승인 완료!")
    elif action == 'reject':
        user.status = 'rejected'
        flash(f"{user.username} 거절 처리됨.")
    db.session.commit()
    # 승인/거절 로그 기록
    log = ApproveLog(user_id=user.id, action=action, admin_id=admin_id)
    db.session.add(log)
    db.session.commit()
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
    user_id = request.args.get('user_id', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    query = db.session.query(Attendance, User).join(User, Attendance.user_id == User.id)

    # 직원 필터
    if user_id:
        query = query.filter(Attendance.user_id == user_id)

    # 날짜 필터
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

    # 직원 목록(셀렉트박스용)
    employees = User.query.filter(User.deleted_at == None, User.status == "approved").order_by(User.username).all()

    # 간단 통계: 출근 건수/총근무시간
    total_days = len(records)
    total_minutes = 0
    for att, user in records:
        if att.clock_in and att.clock_out:
            total_minutes += int((att.clock_out - att.clock_in).total_seconds() // 60)
    total_hours = total_minutes // 60

    return render_template(
        'admin/attendances.html',
        records=records,
        employees=employees,
        total_days=total_days,
        total_hours=total_hours,
        request=request,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to
    )

# CSV 다운로드 라우트
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
        header = '직원,출근,퇴근,근무시간(분)\n'
        yield header
        for att, user in records:
            mins = 0
            if att.clock_in and att.clock_out:
                mins = int((att.clock_out - att.clock_in).total_seconds() // 60)
            row = [
                str(user.name or user.username),
                att.clock_in.strftime('%Y-%m-%d %H:%M') if att.clock_in else '-',
                att.clock_out.strftime('%Y-%m-%d %H:%M') if att.clock_out else '-',
                str(mins)
            ]
            yield ','.join(row) + '\n'

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

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

@app.cli.command('create-sample-data')
def create_sample_data():
    """샘플 데이터 생성"""
    from utils.sample_data import create_sample_data
    create_sample_data()
    print("샘플 데이터 생성 완료!")

if __name__ == '__main__':
    app.run(debug=True)
