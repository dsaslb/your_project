"""
스케줄관리 플러그인
직원 근무 스케줄 관리, 근무 시간표, 스케줄 변경 요청 기능을 제공합니다.
"""

from flask import Blueprint

# 플러그인 블루프린트 생성
schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')

# 플러그인 메타데이터
PLUGIN_INFO = {
    'name': 'schedule_management',
    'version': '1.0.0',
    'description': '직원 근무 스케줄 관리 및 시간표 시스템',
    'author': 'Your Program',
    'category': 'HR',
    'required_permissions': ['schedule_view', 'schedule_manage'],
    'dependencies': ['attendance_management'],
    'settings': {
        'default_shift_hours': 8,
        'break_time_minutes': 60,
        'overtime_threshold': 8,
        'auto_schedule_enabled': False
    }
}

from . import routes, models 