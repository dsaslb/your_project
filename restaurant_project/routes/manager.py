from flask import Blueprint

manager_bp = Blueprint('manager', __name__)

# 여기에 라우트 핸들러 추가
# 예시:
@manager_bp.route('/manager')
def manager_home():
    return "Manager Home"

# 예시 라우트
@manager_bp.route('/manager/dashboard')
def dashboard():
    return "Manager Dashboard"