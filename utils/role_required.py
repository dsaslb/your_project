from flask_login import current_user
from flask import abort
from functools import wraps

args = None  # pyright: ignore

# 세분화된 권한 체크 데코레이터
# 사용 예시: @role_required('admin',  'super_admin')


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 로그인 여부 및 권한 체크
            if not current_user.is_authenticated or current_user.role not in roles:
                abort(403)  # 접근 거부
            return f(*args, **kwargs)

        return decorated_function

    return decorator
