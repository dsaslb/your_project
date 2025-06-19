from functools import wraps
from flask import redirect, url_for, flash, request
from flask_login import current_user

def role_required(role):
    """역할별 권한 데코레이터 팩토리"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("로그인이 필요합니다.", "danger")
                return redirect(url_for('auth.login'))
            
            if current_user.role != role:
                flash(f"{role} 권한이 필요합니다.", "danger")
                return redirect(url_for('auth.login'))
            
            return f(*args, **kwargs)
        return decorated
    return decorator

def admin_required(f):
    """관리자 권한 데코레이터"""
    return role_required('admin')(f)

def manager_required(f):
    """매니저 권한 데코레이터"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("로그인이 필요합니다.", "danger")
            return redirect(url_for('auth.login'))
        
        if not current_user.is_manager():
            flash("매니저 이상 권한이 필요합니다.", "danger")
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated

def employee_required(f):
    """직원 권한 데코레이터"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("로그인이 필요합니다.", "danger")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def approved_user_required(f):
    """승인된 사용자만 접근 가능한 데코레이터"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("로그인이 필요합니다.", "danger")
            return redirect(url_for('auth.login'))
        
        if not current_user.is_active():
            flash("승인 대기 중입니다. 관리자에게 문의하세요.", "warning")
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated

def log_action(action_name):
    """액션 로깅 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            from models.action_log import ActionLog
            
            result = f(*args, **kwargs)
            
            # 액션 로그 기록
            if current_user.is_authenticated:
                ActionLog.log_action(
                    user_id=current_user.id,
                    action=action_name,
                    detail=f"{f.__name__} 실행",
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string
                )
            
            return result
        return decorated
    return decorator 