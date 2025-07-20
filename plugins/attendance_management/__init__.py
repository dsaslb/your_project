"""
출근관리 플러그인
직원 출근/퇴근 기록, 근무시간 관리, 출근 통계 기능을 제공합니다.
"""

from flask import Blueprint

# 플러그인 블루프린트 생성
attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')

# 플러그인 메타데이터
PLUGIN_INFO = {
    'name': 'attendance_management',
    'version': '1.0.0',
    'description': '직원 출근/퇴근 관리 및 근무시간 통계',
    'author': 'Your Program',
    'category': 'HR',
    'required_permissions': ['attendance_view', 'attendance_manage'],
    'dependencies': [],
    'settings': {
        'work_start_time': '09:00',
        'work_end_time': '18:00',
        'break_time': 60,  # 분
        'overtime_threshold': 8  # 시간
    }
}

from . import routes, models 