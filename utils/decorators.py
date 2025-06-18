from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not getattr(current_user, 'is_admin', False):
            flash("관리자만 접근할 수 있습니다.", "danger")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function
