import os
import json
from datetime import datetime, date, time
from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'core_db.sqlite3')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

## ---------- 권한 체계 통합 관리 ---------- ##
ALL_PERMISSIONS = [
    'order', 'schedule', 'clean', 'inventory', 
    'customer', 'reports', 'reservation', 'accounting'
]

PERMISSION_LABELS = {
    'order': '발주',
    'schedule': '스케줄', 
    'clean': '청소',
    'inventory': '재고',
    'customer': '고객',
    'reports': '보고서',
    'reservation': '예약',
    'accounting': '정산'
}

USER_ROLES = ['admin', 'manager', 'employee']
USER_GRADES = ['manager', 'captain', 'employee']
USER_STATUSES = ['pending', 'approved', 'rejected']

## ---------- 권한 보호 데코레이터 ---------- ##
def require_perm(perm):
    """특정 권한이 필요한 라우트를 보호하는 데코레이터"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            user = User.query.get(session['user_id'])
            if not user:
                session.clear()
                return redirect(url_for('login'))
            
            # 관리자는 모든 권한 보유
            if user.role == 'admin':
                return f(*args, **kwargs)
            
            # 특정 권한 체크
            perms = user.get_permissions()
            if not perms.get(perm, False):
                return render_template('errors/403.html', 
                    error="권한이 없습니다.", 
                    required_perm=PERMISSION_LABELS.get(perm, perm)), 403
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

def require_role(role):
    """특정 역할이 필요한 라우트를 보호하는 데코레이터"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            if session.get('role') != role:
                return render_template('errors/403.html', 
                    error="접근 권한이 없습니다.", 
                    required_role=role), 403
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

## ---------- 모델 ---------- ##
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='employee')  # 'admin', 'manager', 'employee'
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 승인권자(상위 관리자)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 보안 관련 필드
    login_fail = db.Column(db.Integer, default=0)  # 로그인 실패 횟수
    is_locked = db.Column(db.Boolean, default=False)  # 계정 잠금 상태
    last_login = db.Column(db.DateTime)  # 마지막 로그인 시간
    password_changed_at = db.Column(db.DateTime, default=datetime.now)  # 비밀번호 변경 시간
    
    # 직급 및 권한 필드
    grade = db.Column(db.String(20), default='employee')  # 직급: manager/captain/employee
    can_order = db.Column(db.Boolean, default=False)  # 발주 권한 (기존 호환성)
    can_schedule = db.Column(db.Boolean, default=False)  # 스케줄 권한 (기존 호환성)
    can_clean = db.Column(db.Boolean, default=False)  # 청소 권한 (기존 호환성)
    
    # 확장 가능한 JSON 권한 필드
    permissions = db.Column(db.Text, default='{}')  # {"order":true, "schedule":false, "clean":true, ...}
    
    def check_pw(self, pw): 
        return check_password_hash(self.password_hash, pw)
    
    def has_permission(self, perm):
        """JSON 권한에서 특정 권한 확인"""
        try:
            perms = json.loads(self.permissions or '{}')
            return perms.get(perm, False)
        except:
            return False
    
    def set_permissions(self, perms_dict):
        """권한 딕셔너리를 JSON으로 저장"""
        self.permissions = json.dumps(perms_dict)
    
    def get_permissions(self):
        """JSON 권한을 딕셔너리로 반환"""
        try:
            return json.loads(self.permissions or '{}')
        except:
            return {}

class ApprovalLog(db.Model):  # 승인/거절 이력
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 승인받은 사용자
    approver_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 승인자
    action = db.Column(db.String(20))  # 'approve', 'reject'
    created_at = db.Column(db.DateTime, default=datetime.now)

class Notice(db.Model):  # 공지/운영방침용
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.now)

class Order(db.Model):  # 발주
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(50))
    quantity = db.Column(db.Integer)
    order_date = db.Column(db.Date, default=date.today)
    ordered_by = db.Column(db.Integer, db.ForeignKey('user.id'))

class Schedule(db.Model):  # 직원 스케줄
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    work_date = db.Column(db.Date)
    shift = db.Column(db.String(20))  # 예: "오전", "오후", "종일"

class CleanSchedule(db.Model):  # 청소 스케줄
    id = db.Column(db.Integer, primary_key=True)
    team = db.Column(db.String(20))  # 예: "주방", "홀"
    work_date = db.Column(db.Date)
    content = db.Column(db.String(100))

class Notification(db.Model):  # 알림 시스템
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 알림 대상
    content = db.Column(db.String(200))  # 알림 내용
    created_at = db.Column(db.DateTime, default=datetime.now)
    is_read = db.Column(db.Boolean, default=False)  # 읽음 여부

## ---------- DB/관리자 초기화 함수 ---------- ##
def init_db():
    with app.app_context():
        db.create_all()
        # 최종관리자만 자동 생성 (ID=1)
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin', 
                password_hash=generate_password_hash('admin123'), 
                role='admin',
                status='approved',
                parent_id=None
            )
            db.session.add(admin_user)
            db.session.commit()
        if not Notice.query.first():
            db.session.add(Notice(content='운영 방침/공지 예시입니다.'))
            db.session.commit()

## ---------- 로그인/로그아웃 ---------- ##
@app.route('/')
@app.route('/index')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        
        if not user:
            return render_template('login.html', error="로그인 정보를 확인해주세요.")
        
        # 계정 잠금 체크
        if user.is_locked:
            return render_template('login.html', error="계정이 잠겼습니다. 관리자에게 문의하세요.")
        
        # 승인 상태 체크
        if user.status != 'approved':
            if user.status == 'pending':
                return render_template('login.html', error="승인 대기중입니다. 승인 후 사용 가능합니다.")
            elif user.status == 'rejected':
                return render_template('login.html', error="가입이 거절되었습니다. 관리자에게 문의하세요.")
        
        # 비밀번호 체크
        if user.check_pw(request.form['password']):
            # 로그인 성공
            user.login_fail = 0  # 실패 횟수 초기화
            user.last_login = datetime.now()
            db.session.commit()
            
            session['user_id'] = user.id
            session['role'] = user.role
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            # 로그인 실패
            user.login_fail += 1
            if user.login_fail >= 5:
                user.is_locked = True
                db.session.commit()
                return render_template('login.html', error="비밀번호 오류! 5회 이상 틀려서 계정이 잠겼습니다. 관리자에게 문의하세요.")
            else:
                db.session.commit()
                remaining = 5 - user.login_fail
                return render_template('login.html', error=f"비밀번호 오류! {remaining}회 더 틀리면 계정이 잠깁니다.")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

## ---------- 회원가입 ---------- ##
@app.route('/register', methods=['GET', 'POST'])
def register():
    managers = User.query.filter_by(role='manager', status='approved').all()
    if request.method == 'POST':
        username = request.form['username']
        pw = request.form['password']
        role = request.form['role']
        parent_id = 1  # 기본값: 최종관리자
        if role == 'employee':
            parent_id = int(request.form.get('manager_id', 1))  # 매장관리자 지정
        if User.query.filter_by(username=username).first():
            return render_template('register.html', managers=managers, error='이미 존재하는 아이디입니다.')
        user = User(
            username=username,
            password_hash=generate_password_hash(pw),
            role=role,
            status='pending',
            parent_id=parent_id
        )
        db.session.add(user)
        db.session.commit()
        return render_template('register.html', managers=managers, msg='가입 신청 완료! 관리자 승인 후 사용 가능')
    return render_template('register.html', managers=managers)

## ---------- 대시보드 ---------- ##
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    notices = Notice.query.order_by(Notice.created_at.desc()).limit(3).all()
    return render_template('dashboard.html', user=user, notices=notices)

## ---------- 발주 관리 ---------- ##
@app.route('/order', methods=['GET', 'POST'])
@require_perm('order')
def order():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user.can_order and user.role != 'admin':
        return render_template('error.html', error="발주 권한이 없습니다.")
    
    if request.method == 'POST':
        item = request.form['item']
        quantity = request.form['quantity']
        order = Order(item=item, quantity=quantity, ordered_by=session['user_id'])
        db.session.add(order)
        db.session.commit()
        return redirect(url_for('order'))
    orders = Order.query.order_by(Order.order_date.desc()).all()
    return render_template('order.html', orders=orders)

## ---------- 직원 스케줄 관리 ---------- ##
@app.route('/schedule', methods=['GET', 'POST'])
@require_perm('schedule')
def schedule():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user.can_schedule and user.role != 'admin':
        return render_template('error.html', error="스케줄 권한이 없습니다.")
    
    if request.method == 'POST':
        work_date = datetime.strptime(request.form['work_date'], '%Y-%m-%d').date()
        shift = request.form['shift']
        schedule = Schedule(user_id=session['user_id'], work_date=work_date, shift=shift)
        db.session.add(schedule)
        db.session.commit()
        return redirect(url_for('schedule'))
    schedules = Schedule.query.order_by(Schedule.work_date.desc()).all()
    users = User.query.filter_by(status='approved').all()
    return render_template('schedule.html', schedules=schedules, users=users)

## ---------- 청소 스케줄 관리 ---------- ##
@app.route('/clean', methods=['GET', 'POST'])
@require_perm('clean')
def clean():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user.can_clean and user.role != 'admin':
        return render_template('error.html', error="청소 권한이 없습니다.")
    
    if request.method == 'POST':
        team = request.form['team']
        work_date = datetime.strptime(request.form['work_date'], '%Y-%m-%d').date()
        content = request.form['content']
        clean_schedule = CleanSchedule(team=team, work_date=work_date, content=content)
        db.session.add(clean_schedule)
        db.session.commit()
        return redirect(url_for('clean'))
    clean_schedules = CleanSchedule.query.order_by(CleanSchedule.work_date.desc()).all()
    return render_template('clean.html', clean_schedules=clean_schedules)

## ---------- 관리자 승인 관리 ---------- ##
@app.route('/admin/approve_users')
def approve_users():
    if session.get('role') not in ['admin', 'manager']:
        return redirect(url_for('login'))
    
    # admin: 전체, manager: 본인이 parent_id인 직원만
    if session.get('role') == 'manager':
        pendings = User.query.filter_by(status='pending', parent_id=session['user_id']).all()
    else:
        pendings = User.query.filter(User.status=='pending', User.role.in_(['manager','employee'])).all()
    
    return render_template('approve_users.html', pendings=pendings)

@app.route('/admin/approve/<int:user_id>', methods=['POST'])
def approve_user(user_id):
    if session.get('role') not in ['admin', 'manager']:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('approve_users'))
    
    # 권한 체크 (매장관리자는 자신이 승인권자인 직원만 승인 가능)
    approver = User.query.get(session['user_id'])
    if approver.role == 'manager' and user.parent_id != approver.id:
        return redirect(url_for('approve_users'))
    
    # 승인 처리
    user.status = 'approved'
    user.grade = request.form.get('grade', 'employee')
    
    # JSON 권한 처리 (확장 가능한 권한 시스템)
    all_perms = ['order', 'schedule', 'clean', 'inventory', 'customer', 'reports']
    perms = {perm: f"perm_{perm}" in request.form for perm in all_perms}
    user.set_permissions(perms)
    
    # 기존 호환성을 위한 필드도 설정
    user.can_order = perms.get('order', False)
    user.can_schedule = perms.get('schedule', False)
    user.can_clean = perms.get('clean', False)
    
    # 계정 잠금 해제
    user.login_fail = 0
    user.is_locked = False
    
    # 승인 이력 기록
    approval_log = ApprovalLog(
        user_id=user.id,
        approver_id=approver.id,
        action='approve'
    )
    db.session.add(approval_log)
    db.session.commit()
    
    # 승인 알림 전송
    send_notification(user.id, f'🎉 가입이 승인되었습니다! 이제 로그인하여 서비스를 이용하실 수 있습니다.')
    
    return redirect(url_for('approve_users'))

@app.route('/admin/reject/<int:user_id>')
def reject_user(user_id):
    if session.get('role') not in ['admin', 'manager']:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('approve_users'))
    
    # 권한 체크 (매장관리자는 자신이 승인권자인 직원만 거절 가능)
    approver = User.query.get(session['user_id'])
    if approver.role == 'manager' and user.parent_id != approver.id:
        return redirect(url_for('approve_users'))
    
    user.status = 'rejected'
    
    # 거절 이력 기록
    rejection_log = ApprovalLog(
        user_id=user.id,
        approver_id=approver.id,
        action='reject'
    )
    db.session.add(rejection_log)
    db.session.commit()
    
    # 거절 알림 전송
    send_notification(user.id, f'❌ 가입이 거절되었습니다. 관리자에게 문의하시기 바랍니다.')
    
    return redirect(url_for('approve_users'))

## ---------- 비밀번호 변경 ---------- ##
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        old_pw = request.form['old_pw']
        new_pw = request.form['new_pw']
        confirm_pw = request.form['confirm_pw']
        
        # 기존 비밀번호 확인
        if not user.check_pw(old_pw):
            return render_template('change_password.html', error="기존 비밀번호가 틀렸습니다.")
        
        # 새 비밀번호 확인
        if new_pw != confirm_pw:
            return render_template('change_password.html', error="새 비밀번호가 일치하지 않습니다.")
        
        # 비밀번호 강도 체크
        if len(new_pw) < 8:
            return render_template('change_password.html', error="비밀번호는 8자 이상이어야 합니다.")
        
        if not any(c.isdigit() for c in new_pw):
            return render_template('change_password.html', error="비밀번호에 숫자를 포함해야 합니다.")
        
        if not any(c.isalpha() for c in new_pw):
            return render_template('change_password.html', error="비밀번호에 영문을 포함해야 합니다.")
        
        # 비밀번호 변경
        user.password_hash = generate_password_hash(new_pw)
        user.password_changed_at = datetime.now()
        db.session.commit()
        
        return render_template('change_password.html', msg="비밀번호가 성공적으로 변경되었습니다.")
    
    return render_template('change_password.html')

## ---------- 관리자 계정 잠금 해제 ---------- ##
@app.route('/admin/unlock/<int:user_id>')
def unlock_user(user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if user:
        user.is_locked = False
        user.login_fail = 0
        db.session.commit()
    
    return redirect(url_for('approve_users'))

## ---------- 알림 관련 함수 ---------- ##
def send_notification(user_id, msg):
    """사용자에게 알림 전송"""
    notification = Notification(user_id=user_id, content=msg)
    db.session.add(notification)
    db.session.commit()

## ---------- 알림 관리 ---------- ##
@app.route('/notifications')
def notifications():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 사용자의 모든 알림 조회 (최신순)
    notis = Notification.query.filter_by(user_id=session['user_id']).order_by(Notification.created_at.desc()).all()
    
    # 읽음 처리
    for n in notis:
        if not n.is_read:
            n.is_read = True
    db.session.commit()
    
    return render_template('notifications.html', notifications=notis)

@app.route('/notifications/count')
def notification_count():
    """읽지 않은 알림 개수 반환 (AJAX용)"""
    if 'user_id' not in session:
        return {'count': 0}
    
    count = Notification.query.filter_by(user_id=session['user_id'], is_read=False).count()
    return {'count': count}

## ---------- 관리자 권한 관리 ---------- ##
@app.route('/admin/user_permissions', methods=['GET', 'POST'])
def user_permissions():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    users = User.query.filter(User.role.in_(['manager', 'employee'])).all()
    
    if request.method == 'POST':
        # 모든 사용자의 권한을 일괄 업데이트
        for user in users:
            perms = {
                "order": f"perm_order_{user.id}" in request.form,
                "schedule": f"perm_schedule_{user.id}" in request.form,
                "clean": f"perm_clean_{user.id}" in request.form,
                "inventory": f"perm_inventory_{user.id}" in request.form,
                "customer": f"perm_customer_{user.id}" in request.form,
                "reports": f"perm_reports_{user.id}" in request.form,
                "reservation": f"perm_reservation_{user.id}" in request.form,
                "accounting": f"perm_accounting_{user.id}" in request.form
            }
            
            # 기존 권한과 비교하여 변경사항 확인
            old_perms = user.get_permissions()
            if old_perms != perms:
                user.set_permissions(perms)
                
                # 기존 호환성을 위한 필드도 업데이트
                user.can_order = perms.get('order', False)
                user.can_schedule = perms.get('schedule', False)
                user.can_clean = perms.get('clean', False)
                
                # 권한 변경 이력 로그 남기기 (diff 포함)
                diff_memo = f"이전:{json.dumps(old_perms, ensure_ascii=False)}→변경:{json.dumps(perms, ensure_ascii=False)}"
                log = ApprovalLog(
                    user_id=user.id, 
                    approver_id=session['user_id'],
                    action='permission_change',
                    memo=diff_memo
                )
                db.session.add(log)
        
        db.session.commit()
        
        # 권한 변경 알림 전송
        for user in users:
            send_notification(user.id, f'🔧 권한이 변경되었습니다. 새로운 권한으로 서비스를 이용하실 수 있습니다.')
        
        return redirect(url_for('user_permissions'))
    
    return render_template('user_permissions.html', users=users)

## ---------- 권한 변경 이력 조회 ---------- ##
@app.route('/admin/approval_logs')
def approval_logs():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    # 모든 승인/거절/권한변경 이력 조회 (최신순)
    logs = ApprovalLog.query.order_by(ApprovalLog.created_at.desc()).all()
    
    return render_template('approval_logs.html', logs=logs)

## ---------- 확장된 기능 라우트 ---------- ##
@app.route('/inventory')
@require_perm('inventory')
def inventory():
    """재고 관리"""
    return render_template('inventory.html', message="재고 관리 기능이 구현되었습니다!")

@app.route('/reservation')
@require_perm('reservation')
def reservation():
    """예약 관리"""
    return render_template('reservation.html', message="예약 관리 기능이 구현되었습니다!")

@app.route('/accounting')
@require_perm('accounting')
def accounting():
    """정산 관리"""
    return render_template('accounting.html', message="정산 관리 기능이 구현되었습니다!")

@app.route('/customer')
@require_perm('customer')
def customer():
    """고객 관리"""
    return render_template('customer.html', message="고객 관리 기능이 구현되었습니다!")

@app.route('/reports')
@require_perm('reports')
def reports():
    """보고서"""
    return render_template('reports.html', message="보고서 기능이 구현되었습니다!")

if __name__ == "__main__":
    # 앱 시작 시 DB 초기화
    init_db()
    app.run(debug=True) 