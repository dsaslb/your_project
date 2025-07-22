"""
운영자/관리자 대시보드용 상태/로그/알림 API
- /api/admin/ops/status : 전체 서비스/컨테이너 상태
- /api/admin/ops/logs : 최근 장애/복구 로그
- /api/admin/ops/alerts : 최근 장애 알림
"""
from flask import Blueprint, jsonify
import subprocess
import os

bp = Blueprint('admin_ops_api', __name__, url_prefix='/api/admin/ops')

LOG_FILE = os.path.join('logs', 'auto_recover.log')

@bp.route('/status', methods=['GET'])
def get_status():
    """전체 서비스/컨테이너 상태 반환"""
    try:
        result = subprocess.check_output(['docker-compose', 'ps'], stderr=subprocess.STDOUT)
        return jsonify({
            'status': 'ok',
            'output': result.decode('utf-8')
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

@bp.route('/logs', methods=['GET'])
def get_logs():
    """최근 장애/복구 로그 반환"""
    try:
        if not os.path.exists(LOG_FILE):
            return jsonify({'logs': []})
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()[-30:]
        return jsonify({'logs': lines})
    except Exception as e:
        return jsonify({'error': str(e)})

@bp.route('/alerts', methods=['GET'])
def get_alerts():
    """최근 장애 알림 반환 (로그에서 ALERT 라인 추출)"""
    try:
        if not os.path.exists(LOG_FILE):
            return jsonify({'alerts': []})
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            alerts = [line for line in f if '[ALERT]' in line][-20:]
        return jsonify({'alerts': alerts})
    except Exception as e:
        return jsonify({'error': str(e)}) 