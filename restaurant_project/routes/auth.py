from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from restaurant_project.models import db, User, UserLog, ActionLog, ApprovalLog
from flask_bcrypt import Bcrypt
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from utils import sample_data
from utils.decorators import admin_required
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

# Bcrypt 인스턴스는 app.py에서 생성되므로 current_app에서 가져옴
def get_bcrypt():
    return current_app.extensions['bcrypt']

def require_role(role):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator

def log_action(user, action, actor, detail=None):
    log = ActionLog(user_id=user.id, actor_id=actor.id if actor else None, action=action, detail=detail)
    db.session.add(log)
    db.session.commit()

@auth_bp.route("/")
def home():
    return redirect(url_for("auth.login"))

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password, deleted_at=None).first()
        if user and user.status == 'approved':
            login_user(user)
            flash("로그인 성공!", "success")
            return redirect(url_for('index'))
        else:
            flash("로그인 실패!", "danger")
    return '''
        <form method="post">
            <input name="username" placeholder="아이디"><br>
            <input name="password" type="password" placeholder="비밀번호"><br>
            <button type="submit">로그인</button>
        </form>
    '''

@auth_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html')

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']
        # parent_id 자동 할당
        if role == 'manager':
            admin = User.query.filter_by(role='admin', status='approved', deleted=False).first()
            parent_id = admin.id if admin else None
        elif role == 'employee':
            if not current_user.is_authenticated or current_user.role != 'manager':
                abort(403)
            parent_id = current_user.id
        else:
            parent_id = None
        user = User(username=username, password=password, role=role, status='pending', parent_id=parent_id)
        db.session.add(user)
        db.session.commit()
        log_action(user, 'register', current_user if current_user.is_authenticated else None, '회원가입 신청')
        flash('회원가입 요청이 접수되었습니다. 승인 후 이용 가능합니다.', 'info')
        return redirect(url_for('auth.login'))
    # GET: 상위 관리자 목록 전달
    parent_admins = User.query.filter_by(role='admin', status='approved', deleted=False).all()
    parent_managers = User.query.filter_by(role='manager', status='approved', deleted=False).all()
    return render_template('register.html', parent_admins=parent_admins, parent_managers=parent_managers)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("로그아웃 되었습니다.", "success")
    return redirect(url_for('auth.login'))

@auth_bp.route("/users")
def user_list():
    users = User.query.all()
    return render_template("user_list.html", users=users)

@auth_bp.route('/admin/only')
@login_required
def admin_only():
    if current_user.role != 'admin':
        abort(403)
    return '이 페이지는 관리자만 볼 수 있습니다.'

@auth_bp.route('/admin_approval_list')
@login_required
def admin_approval_list():
    if current_user.role != 'superadmin':
        abort(403)
    admins = User.query.filter_by(role='admin', status='pending').all()
    return render_template('admin_approval_list.html', admins=admins)

@auth_bp.route('/employee_approval_list')
@login_required
def employee_approval_list():
    if current_user.role != 'admin':
        abort(403)
    employees = User.query.filter_by(role='employee', status='pending').all()
    return render_template('employee_approval_list.html', employees=employees)

@auth_bp.route('/approve_admin/<int:user_id>')
@login_required
def approve_admin(user_id):
    if current_user.role != 'superadmin':
        abort(403)
    user = User.query.get(user_id)
    if user and user.role == 'admin':
        user.status = 'active'
        db.session.commit()
    return redirect(url_for('auth.admin_approval_list'))

@auth_bp.route('/approve_employee/<int:user_id>')
@login_required
def approve_employee_admin(user_id):
    if current_user.role != 'admin':
        abort(403)
    user = User.query.get(user_id)
    if user and user.role == 'employee':
        user.status = 'active'
        db.session.commit()
    return redirect(url_for('auth.employee_approval_list'))

@auth_bp.route('/reject_user/<int:user_id>')
@login_required
def reject_user(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(404)
    if (current_user.role == 'superadmin' and user.role == 'admin') or (current_user.role == 'admin' and user.role == 'employee'):
        user.status = 'rejected'
        db.session.commit()
    else:
        abort(403)
    return redirect(request.referrer or url_for('auth.dashboard'))

# 최고관리자: 매장관리자 승인 대기 목록
@auth_bp.route('/admin/approve_managers')
@login_required
@require_role('admin')
def approve_managers():
    pending = User.query.filter_by(role='manager', status='pending', deleted=False).all()
    approved = User.query.filter_by(role='manager', status='approved', deleted=False).all()
    rejected = User.query.filter_by(role='manager', status='rejected', deleted=False).all()
    return render_template('approve_managers.html', users=pending, approved=approved, rejected=rejected)

@auth_bp.route('/admin/approve_manager/<int:user_id>')
@login_required
@require_role('admin')
def approve_manager(user_id):
    user = User.query.get(user_id)
    user.status = 'approved'
    db.session.commit()
    log_action(user, 'approve', current_user, '매장관리자 승인')
    flash(f"{user.username} 님이 승인되었습니다.", 'success')
    return redirect(url_for('auth.approve_managers'))

@auth_bp.route('/admin/reject_manager/<int:user_id>')
@login_required
@require_role('admin')
def reject_manager(user_id):
    user = User.query.get(user_id)
    user.status = 'rejected'
    db.session.commit()
    log_action(user, 'reject', current_user, '매장관리자 거절')
    flash(f"{user.username} 님이 거절되었습니다.", 'danger')
    return redirect(url_for('auth.approve_managers'))

# 매장관리자: 직원 승인 대기 목록
@auth_bp.route('/manager/approve_employees')
@login_required
@require_role('manager')
def approve_employees():
    pending = User.query.filter_by(role='employee', status='pending', parent_id=current_user.id, deleted=False).all()
    approved = User.query.filter_by(role='employee', status='approved', parent_id=current_user.id, deleted=False).all()
    rejected = User.query.filter_by(role='employee', status='rejected', parent_id=current_user.id, deleted=False).all()
    return render_template('approve_employees.html', users=pending, approved=approved, rejected=rejected)

@auth_bp.route('/manager/approve_employee/<int:user_id>')
@login_required
@require_role('manager')
def approve_employee_manager(user_id):
    user = User.query.get(user_id)
    user.status = 'approved'
    db.session.commit()
    log_action(user, 'approve', current_user, '직원 승인')
    flash(f"{user.username} 님이 승인되었습니다.", 'success')
    return redirect(url_for('auth.approve_employees'))

@auth_bp.route('/manager/reject_employee/<int:user_id>')
@login_required
@require_role('manager')
def reject_employee(user_id):
    user = User.query.get(user_id)
    user.status = 'rejected'
    db.session.commit()
    log_action(user, 'reject', current_user, '직원 거절')
    flash(f"{user.username} 님이 거절되었습니다.", 'danger')
    return redirect(url_for('auth.approve_employees'))

@auth_bp.route('/delete_account/<int:user_id>')
@login_required
def delete_account(user_id):
    user = User.query.get(user_id)
    if not user or user.deleted:
        abort(404)
    if current_user.id != user.id and current_user.role not in ['admin', 'manager']:
        abort(403)
    user.deleted = True
    user.deleted_at = datetime.utcnow()
    db.session.commit()
    log_action(user, 'delete', current_user, '계정 소프트 삭제')
    flash('계정이 탈퇴(삭제) 처리되었습니다.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/some_route')
def some_func():
    # ...

user = User.query.filter_by(username='admin').first()  # 본인 아이디로 변경
user.status = 'approved'
db.session.commit() 