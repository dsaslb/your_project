#!/usr/bin/env python3
"""
확장 가능한 블루프린트 구조
MVP 완성 후 모듈별로 분리 예정
"""

from flask import Blueprint

# ===== 현재 구현된 기능들 =====
# (app.py에 통합되어 있음, 나중에 블루프린트로 분리 예정)

# ===== 향후 확장 예정 블루프린트들 =====

# auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
# user_bp = Blueprint('user', __name__, url_prefix='/user')
# attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')
# admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
# notice_bp = Blueprint('notice', __name__, url_prefix='/notice')
# payroll_bp = Blueprint('payroll', __name__, url_prefix='/payroll')
# report_bp = Blueprint('report', __name__, url_prefix='/report')
# api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# 근태 관리 블루프린트
from routes.attendance import attendance_bp

def init_blueprints(app):
    """블루프린트 초기화 (v2에서 구현 예정)"""
    # TODO: 블루프린트 등록
    # app.register_blueprint(auth_bp)
    # app.register_blueprint(user_bp)
    # app.register_blueprint(attendance_bp)
    # app.register_blueprint(admin_bp)
    # app.register_blueprint(notice_bp)
    # app.register_blueprint(payroll_bp)
    # app.register_blueprint(report_bp)
    # app.register_blueprint(api_bp)
    
    # 근태 관리 블루프린트 등록
    app.register_blueprint(attendance_bp)
    pass 