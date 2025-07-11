"""
플러그인 시스템 통합 매니저 API
플러그인 시스템 전체를 관리하는 API 엔드포인트
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
import logging

from .plugin_system_manager import plugin_system_manager

logger = logging.getLogger(__name__)

# 블루프린트 생성
plugin_system_manager_bp = Blueprint('plugin_system_manager', __name__, url_prefix='/api/plugin-system')

@plugin_system_manager_bp.route('/status', methods=['GET'])
def get_system_status():
    """플러그인 시스템 상태 조회"""
    try:
        status = plugin_system_manager.get_system_status()
        return jsonify({
            'success': True,
            'data': status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"시스템 상태 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@plugin_system_manager_bp.route('/info', methods=['GET'])
def get_system_info():
    """플러그인 시스템 정보 조회"""
    try:
        info = plugin_system_manager.get_system_info()
        return jsonify({
            'success': True,
            'data': info,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"시스템 정보 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@plugin_system_manager_bp.route('/initialize', methods=['POST'])
def initialize_system():
    """플러그인 시스템 초기화"""
    try:
        result = plugin_system_manager.initialize_system()
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"시스템 초기화 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@plugin_system_manager_bp.route('/start', methods=['POST'])
def start_system():
    """플러그인 시스템 시작"""
    try:
        result = plugin_system_manager.start_system()
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"시스템 시작 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@plugin_system_manager_bp.route('/stop', methods=['POST'])
def stop_system():
    """플러그인 시스템 중지"""
    try:
        result = plugin_system_manager.stop_system()
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"시스템 중지 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@plugin_system_manager_bp.route('/health-check', methods=['POST'])
def run_health_check():
    """헬스 체크 실행"""
    try:
        result = plugin_system_manager.run_health_check()
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"헬스 체크 실행 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@plugin_system_manager_bp.route('/restart', methods=['POST'])
def restart_system():
    """플러그인 시스템 재시작"""
    try:
        # 시스템 중지
        stop_result = plugin_system_manager.stop_system()
        
        # 잠시 대기
        import time
        time.sleep(2)
        
        # 시스템 재시작
        start_result = plugin_system_manager.start_system()
        
        return jsonify({
            'success': True,
            'data': {
                'stop_result': stop_result,
                'start_result': start_result,
                'restart_timestamp': datetime.now().isoformat()
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"시스템 재시작 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@plugin_system_manager_bp.route('/logs', methods=['GET'])
def get_system_logs():
    """시스템 로그 조회"""
    try:
        # 간단한 로그 조회 (실제로는 로그 파일에서 읽어와야 함)
        logs = {
            'recent_logs': [
                {
                    'timestamp': datetime.now().isoformat(),
                    'level': 'INFO',
                    'message': '플러그인 시스템 로그 조회'
                }
            ],
            'log_levels': ['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            'log_file_path': 'logs/plugin_system.log'
        }
        
        return jsonify({
            'success': True,
            'data': logs,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"시스템 로그 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@plugin_system_manager_bp.route('/metrics', methods=['GET'])
def get_system_metrics():
    """시스템 메트릭 조회"""
    try:
        # 시스템 메트릭 수집
        metrics = {
            'performance': {
                'cpu_usage': 0,
                'memory_usage': 0,
                'active_plugins': plugin_system_manager.system_status['active_plugins'],
                'total_plugins': plugin_system_manager.system_status['total_plugins']
            },
            'health': {
                'status': plugin_system_manager.system_status['health_status'],
                'last_check': plugin_system_manager.system_status['last_check'].isoformat() if plugin_system_manager.system_status['last_check'] else None
            },
            'components': {}
        }
        
        # 컴포넌트별 메트릭
        for name, component in plugin_system_manager.components.items():
            if component:
                try:
                    if hasattr(component, 'get_metrics'):
                        metrics['components'][name] = component.get_metrics()
                    else:
                        metrics['components'][name] = {'status': 'available'}
                except Exception:
                    metrics['components'][name] = {'status': 'error'}
            else:
                metrics['components'][name] = {'status': 'unavailable'}
        
        return jsonify({
            'success': True,
            'data': metrics,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"시스템 메트릭 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@plugin_system_manager_bp.route('/config', methods=['GET'])
def get_system_config():
    """시스템 설정 조회"""
    try:
        # 시스템 설정 조회
        config = {
            'health_check_interval': plugin_system_manager.health_check_interval,
            'auto_optimization': True,
            'log_level': 'INFO',
            'max_plugins': 100,
            'plugin_timeout': 30
        }
        
        return jsonify({
            'success': True,
            'data': config,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"시스템 설정 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@plugin_system_manager_bp.route('/config', methods=['PUT'])
def update_system_config():
    """시스템 설정 업데이트"""
    try:
        data = request.get_json()
        
        # 설정 업데이트
        if 'health_check_interval' in data:
            plugin_system_manager.health_check_interval = data['health_check_interval']
        
        return jsonify({
            'success': True,
            'message': '시스템 설정이 업데이트되었습니다',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"시스템 설정 업데이트 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500 