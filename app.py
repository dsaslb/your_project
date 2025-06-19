from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import DevConfig
from extensions import db, migrate
from utils.logger import log_action
from werkzeug.exceptions import NotFound, InternalServerError
from datetime import datetime, date, timedelta
import pandas as pd
from flask import send_file
from io import BytesIO

app = Flask(__name__)
app.config.from_object(DevConfig)

db.init_app(app)
migrate.init_app(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# --- 인증/회원가입/로그인 ---
@app.route('/', methods=['GET'])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if current_user.is_admin():
        return redirect(url_for('admin_dashboard'))
    elif current_user.is_manager():
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    from models import User
    if request.method == 'POST':
        username = request.form.get('username')
        pw = request.form.get('password')
        user = User.query.filter_by(username=username, deleted_at=None).first()
        if user and user.check_password(pw) and user.status == 'approved':
            login_user(user)
            log_action(user, "login", "로그인 성공")
            flash("로그인 성공!", "success")
            return redirect(url_for('index'))
        else:
            flash("로그인 실패", "danger")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    log_action(current_user, "logout", "로그아웃")
    logout_user()
    flash("로그아웃 완료", "success")
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    from models import User
    if request.method == 'POST':
        username = request.form.get('username')
        pw = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash("이미 존재하는 아이디입니다.", "danger")
        else:
            user = User(username=username, role='employee', status='pending')
            user.set_password(pw)
            db.session.add(user)
            db.session.commit()
            log_action(user, "register", "회원가입 요청")
            flash("회원가입 요청 완료(승인 후 사용 가능)", "success")
            return redirect(url_for('login'))
    return render_template('register.html')

# --- 직원 출퇴근 CRUD ---
@app.route('/dashboard')
@login_required
def dashboard():
    from models import Attendance
    records = Attendance.query.filter_by(user_id=current_user.id).order_by(Attendance.clock_in.desc()).all()
    return render_template('dashboard.html', records=records)

@app.route('/clockin', methods=['POST'])
@login_required
def clock_in():
    from models import Attendance
    today = datetime.now().date()
    exist = Attendance.query.filter(
        Attendance.user_id==current_user.id,
        Attendance.clock_in >= datetime(today.year, today.month, today.day)
    ).first()
    if exist:
        flash("이미 출근기록이 있습니다.", "danger")
        return redirect(url_for('dashboard'))
    now = datetime.now()
    att = Attendance(user_id=current_user.id, clock_in=now)
    db.session.add(att)
    log_action(current_user, "clockin", f"출근 {now}")
    db.session.commit()
    flash("출근 완료", "success")
    return redirect(url_for('dashboard'))

@app.route('/clockout/<int:att_id>', methods=['POST'])
@login_required
def clock_out(att_id):
    from models import Attendance
    att = Attendance.query.get_or_404(att_id)
    if att.user_id != current_user.id or att.clock_out:
        flash("퇴근 기록 오류", "danger")
        return redirect(url_for('dashboard'))
    now = datetime.now()
    att.clock_out = now
    log_action(current_user, "clockout", f"퇴근 {now}")
    db.session.commit()
    flash("퇴근 완료", "success")
    return redirect(url_for('dashboard'))

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

@app.route('/admin/users/approve/<int:user_id>', methods=['POST'])
@login_required
def approve_user(user_id):
    from models import User, ApproveLog
    if not (current_user.is_admin() or current_user.is_manager()):
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    reason = request.form.get('reason', '')
    
    user.status = 'approved'
    db.session.commit()
    
    # 승인 로그 기록
    approve_log = ApproveLog(
        user_id=user.id,
        approver_id=current_user.id,
        action='approved',
        reason=reason
    )
    db.session.add(approve_log)
    db.session.commit()
    
    log_action(current_user, "approve_user", f"사용자 승인: {user.username}")
    flash(f"{user.username} 사용자 승인 완료", "success")
    return redirect(url_for('admin_users'))

@app.route('/admin/users/reject/<int:user_id>', methods=['POST'])
@login_required
def reject_user(user_id):
    from models import User, ApproveLog
    if not (current_user.is_admin() or current_user.is_manager()):
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    reason = request.form.get('reason', '')
    
    user.status = 'rejected'
    db.session.commit()
    
    # 거절 로그 기록
    approve_log = ApproveLog(
        user_id=user.id,
        approver_id=current_user.id,
        action='rejected',
        reason=reason
    )
    db.session.add(approve_log)
    db.session.commit()
    
    log_action(current_user, "reject_user", f"사용자 거절: {user.username}")
    flash(f"{user.username} 사용자 거절 완료", "success")
    return redirect(url_for('admin_users'))

@app.route('/admin/attendance', methods=['GET', 'POST'])
@login_required
def admin_attendance():
    from models import User, Attendance
    if not (current_user.is_admin() or current_user.is_manager()):
        return redirect(url_for('dashboard'))
    
    # 필터링
    user_id = request.args.get('user_id', type=int)
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    query = Attendance.query.join(User).filter(User.deleted_at == None)
    
    if user_id:
        query = query.filter(Attendance.user_id == user_id)
    if from_date:
        query = query.filter(Attendance.clock_in >= datetime.strptime(from_date, '%Y-%m-%d'))
    if to_date:
        query = query.filter(Attendance.clock_in <= datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1))
    
    attendances = query.order_by(Attendance.clock_in.desc()).all()
    users = User.query.filter_by(deleted_at=None, status='approved').all()
    
    return render_template('admin_attendance.html', attendances=attendances, users=users)

@app.route('/admin/attendance/download')
@login_required
def admin_attendance_download():
    from models import User, Attendance
    if not (current_user.is_admin() or current_user.is_manager()):
        return redirect(url_for('dashboard'))
    
    # 필터링
    user_id = request.args.get('user_id', type=int)
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    query = Attendance.query.join(User).filter(User.deleted_at == None)
    
    if user_id:
        query = query.filter(Attendance.user_id == user_id)
    if from_date:
        query = query.filter(Attendance.clock_in >= datetime.strptime(from_date, '%Y-%m-%d'))
    if to_date:
        query = query.filter(Attendance.clock_in <= datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1))
    
    attendances = query.order_by(Attendance.clock_in.desc()).all()
    
    # CSV 생성
    data = []
    for att in attendances:
        user = User.query.get(att.user_id)
        data.append({
            '사용자': user.username if user else '탈퇴',
            '출근시간': att.clock_in.strftime('%Y-%m-%d %H:%M:%S') if att.clock_in else '',
            '퇴근시간': att.clock_out.strftime('%Y-%m-%d %H:%M:%S') if att.clock_out else '',
            '근무시간(분)': att.work_minutes,
            '상태': att.status,
            '등록일': att.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')
    output.seek(0)
    
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'attendance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
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

@app.route('/admin/approve_logs')
@login_required
def approve_logs():
    from models import User, ApproveLog
    if not (current_user.is_admin() or current_user.is_manager()):
        return redirect(url_for('dashboard'))
    
    # 필터링
    user_id = request.args.get('user_id', type=int)
    approver_id = request.args.get('approver_id', type=int)
    action = request.args.get('action')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    query = ApproveLog.query
    
    if user_id:
        query = query.filter(ApproveLog.user_id == user_id)
    if approver_id:
        query = query.filter(ApproveLog.approver_id == approver_id)
    if action:
        query = query.filter(ApproveLog.action == action)
    if from_date:
        query = query.filter(ApproveLog.timestamp >= datetime.strptime(from_date, '%Y-%m-%d'))
    if to_date:
        query = query.filter(ApproveLog.timestamp <= datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1))
    
    logs = query.order_by(ApproveLog.timestamp.desc()).all()
    users = User.query.filter_by(deleted_at=None).all()
    
    return render_template('approve_logs.html', logs=logs, users=users)

@app.route('/admin/approve_logs/download')
@login_required
def approve_logs_download():
    from models import User, ApproveLog
    if not (current_user.is_admin() or current_user.is_manager()):
        return redirect(url_for('dashboard'))
    
    # 필터링
    user_id = request.args.get('user_id', type=int)
    approver_id = request.args.get('approver_id', type=int)
    action = request.args.get('action')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    query = ApproveLog.query
    
    if user_id:
        query = query.filter(ApproveLog.user_id == user_id)
    if approver_id:
        query = query.filter(ApproveLog.approver_id == approver_id)
    if action:
        query = query.filter(ApproveLog.action == action)
    if from_date:
        query = query.filter(ApproveLog.timestamp >= datetime.strptime(from_date, '%Y-%m-%d'))
    if to_date:
        query = query.filter(ApproveLog.timestamp <= datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1))
    
    logs = query.order_by(ApproveLog.timestamp.desc()).all()
    
    # CSV 생성
    data = []
    for log in logs:
        user = User.query.get(log.user_id)
        approver = User.query.get(log.approver_id)
        data.append({
            '사용자': user.username if user else '탈퇴',
            '담당자': approver.username if approver else '탈퇴',
            '액션': '승인' if log.action == 'approved' else '거절',
            '사유': log.reason or '',
            '일시': log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')
    output.seek(0)
    
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'approve_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

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
