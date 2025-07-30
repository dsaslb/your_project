"""
고급 플러그인 API
엔터프라이즈급 플러그인 관리 및 확장 API
"""

from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import traceback
import os
import sys

# 플러그인 시스템 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from plugins.advanced_plugin_system import AdvancedPluginManager

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint 생성
advanced_plugin_bp = Blueprint('advanced_plugin', __name__, url_prefix='/api/v2/plugins')

# 플러그인 매니저 인스턴스
plugin_manager = AdvancedPluginManager()

@advanced_plugin_bp.route('/health', methods=['GET'])
@cross_origin()
def plugin_health_check():
    """플러그인 시스템 상태 확인"""
    try:
        plugins = plugin_manager.list_plugins()
        active_plugins = [p for p in plugins if p['metadata']['status'] == 'active']
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'total_plugins': len(plugins),
            'active_plugins': len(active_plugins),
            'system_version': '2.0.0'
        }), 200
    except Exception as e:
        logger.error(f"플러그인 헬스체크 오류: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_plugin_bp.route('/list', methods=['GET'])
@cross_origin()
def list_plugins():
    """플러그인 목록 조회"""
    try:
        plugins = plugin_manager.list_plugins()
        
        return jsonify({
            'status': 'success',
            'plugins': plugins,
            'total_count': len(plugins),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"플러그인 목록 조회 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '플러그인 목록 조회 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_plugin_bp.route('/info/<plugin_name>', methods=['GET'])
@cross_origin()
def get_plugin_info(plugin_name: str):
    """플러그인 정보 조회"""
    try:
        plugin_info = plugin_manager.get_plugin_info(plugin_name)
        
        if not plugin_info:
            return jsonify({
                'error': f'플러그인 {plugin_name}을 찾을 수 없습니다',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        return jsonify({
            'status': 'success',
            'plugin': plugin_info,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"플러그인 정보 조회 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '플러그인 정보 조회 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_plugin_bp.route('/install', methods=['POST'])
@cross_origin()
def install_plugin():
    """플러그인 설치"""
    try:
        data = request.get_json()
        
        if not data or 'plugin_path' not in data:
            return jsonify({
                'error': '플러그인 경로가 필요합니다',
                'required_fields': ['plugin_path']
            }), 400
        
        plugin_path = data['plugin_path']
        source = data.get('source', 'local')
        
        success = plugin_manager.install_plugin(plugin_path, source)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'플러그인 설치 완료: {plugin_path}',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'error': '플러그인 설치에 실패했습니다',
                'timestamp': datetime.now().isoformat()
            }), 500
        
    except Exception as e:
        logger.error(f"플러그인 설치 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '플러그인 설치 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_plugin_bp.route('/uninstall/<plugin_name>', methods=['DELETE'])
@cross_origin()
def uninstall_plugin(plugin_name: str):
    """플러그인 제거"""
    try:
        success = plugin_manager.uninstall_plugin(plugin_name)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'플러그인 제거 완료: {plugin_name}',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'error': '플러그인 제거에 실패했습니다',
                'timestamp': datetime.now().isoformat()
            }), 500
        
    except Exception as e:
        logger.error(f"플러그인 제거 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '플러그인 제거 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_plugin_bp.route('/enable/<plugin_name>', methods=['POST'])
@cross_origin()
def enable_plugin(plugin_name: str):
    """플러그인 활성화"""
    try:
        success = plugin_manager.enable_plugin(plugin_name)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'플러그인 활성화 완료: {plugin_name}',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'error': '플러그인 활성화에 실패했습니다',
                'timestamp': datetime.now().isoformat()
            }), 500
        
    except Exception as e:
        logger.error(f"플러그인 활성화 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '플러그인 활성화 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_plugin_bp.route('/disable/<plugin_name>', methods=['POST'])
@cross_origin()
def disable_plugin(plugin_name: str):
    """플러그인 비활성화"""
    try:
        success = plugin_manager.disable_plugin(plugin_name)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'플러그인 비활성화 완료: {plugin_name}',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'error': '플러그인 비활성화에 실패했습니다',
                'timestamp': datetime.now().isoformat()
            }), 500
        
    except Exception as e:
        logger.error(f"플러그인 비활성화 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '플러그인 비활성화 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_plugin_bp.route('/config/<plugin_name>', methods=['GET'])
@cross_origin()
def get_plugin_config(plugin_name: str):
    """플러그인 설정 조회"""
    try:
        plugin_info = plugin_manager.get_plugin_info(plugin_name)
        
        if not plugin_info:
            return jsonify({
                'error': f'플러그인 {plugin_name}을 찾을 수 없습니다',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        return jsonify({
            'status': 'success',
            'config': plugin_info['config'],
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"플러그인 설정 조회 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '플러그인 설정 조회 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_plugin_bp.route('/config/<plugin_name>', methods=['PUT'])
@cross_origin()
def update_plugin_config(plugin_name: str):
    """플러그인 설정 업데이트"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': '설정 데이터가 필요합니다',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # 설정 업데이트
        plugin_info = plugin_manager.get_plugin_info(plugin_name)
        if not plugin_info:
            return jsonify({
                'error': f'플러그인 {plugin_name}을 찾을 수 없습니다',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        # 플러그인 인스턴스에 설정 전달
        if plugin_name in plugin_manager.instances:
            instance = plugin_manager.instances[plugin_name]
            if hasattr(instance, 'set_config'):
                instance.set_config(data)
        
        return jsonify({
            'status': 'success',
            'message': f'플러그인 설정 업데이트 완료: {plugin_name}',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"플러그인 설정 업데이트 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '플러그인 설정 업데이트 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_plugin_bp.route('/update/<plugin_name>', methods=['POST'])
@cross_origin()
def update_plugin(plugin_name: str):
    """플러그인 업데이트"""
    try:
        success = plugin_manager.update_plugin(plugin_name)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'플러그인 업데이트 완료: {plugin_name}',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'error': '플러그인 업데이트에 실패했습니다',
                'timestamp': datetime.now().isoformat()
            }), 500
        
    except Exception as e:
        logger.error(f"플러그인 업데이트 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '플러그인 업데이트 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_plugin_bp.route('/backup/<plugin_name>', methods=['POST'])
@cross_origin()
def backup_plugin(plugin_name: str):
    """플러그인 백업"""
    try:
        backup_path = plugin_manager.backup_plugin(plugin_name)
        
        if backup_path:
            return jsonify({
                'status': 'success',
                'message': f'플러그인 백업 완료: {plugin_name}',
                'backup_path': backup_path,
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'error': '플러그인 백업에 실패했습니다',
                'timestamp': datetime.now().isoformat()
            }), 500
        
    except Exception as e:
        logger.error(f"플러그인 백업 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '플러그인 백업 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_plugin_bp.route('/restore', methods=['POST'])
@cross_origin()
def restore_plugin():
    """플러그인 복원"""
    try:
        data = request.get_json()
        
        if not data or 'backup_path' not in data:
            return jsonify({
                'error': '백업 파일 경로가 필요합니다',
                'required_fields': ['backup_path']
            }), 400
        
        backup_path = data['backup_path']
        success = plugin_manager.restore_plugin(backup_path)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': '플러그인 복원 완료',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'error': '플러그인 복원에 실패했습니다',
                'timestamp': datetime.now().isoformat()
            }), 500
        
    except Exception as e:
        logger.error(f"플러그인 복원 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '플러그인 복원 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_plugin_bp.route('/execute/<plugin_name>/<command>', methods=['POST'])
@cross_origin()
def execute_plugin_command(plugin_name: str, command: str):
    """플러그인 명령어 실행"""
    try:
        data = request.get_json() or {}
        args = data.get('args', [])
        kwargs = data.get('kwargs', {})
        
        full_command = f"{plugin_name}:{command}"
        result = plugin_manager.execute_command(full_command, *args, **kwargs)
        
        return jsonify({
            'status': 'success',
            'command': full_command,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except ValueError as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 404
    except Exception as e:
        logger.error(f"플러그인 명령어 실행 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '플러그인 명령어 실행 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_plugin_bp.route('/hooks/<hook_name>', methods=['POST'])
@cross_origin()
def execute_hook(hook_name: str):
    """훅 실행"""
    try:
        data = request.get_json() or {}
        args = data.get('args', [])
        kwargs = data.get('kwargs', {})
        
        results = plugin_manager.execute_hook(hook_name, *args, **kwargs)
        
        return jsonify({
            'status': 'success',
            'hook': hook_name,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"훅 실행 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '훅 실행 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_plugin_bp.route('/events/<event_name>', methods=['POST'])
@cross_origin()
def trigger_event(event_name: str):
    """이벤트 트리거"""
    try:
        data = request.get_json() or {}
        args = data.get('args', [])
        kwargs = data.get('kwargs', {})
        
        plugin_manager.trigger_event(event_name, *args, **kwargs)
        
        return jsonify({
            'status': 'success',
            'event': event_name,
            'message': '이벤트가 성공적으로 트리거되었습니다',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"이벤트 트리거 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '이벤트 트리거 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_plugin_bp.route('/marketplace', methods=['GET'])
@cross_origin()
def get_marketplace():
    """플러그인 마켓플레이스 정보"""
    try:
        # 실제 구현에서는 외부 API에서 플러그인 목록을 가져옴
        marketplace_plugins = [
            {
                'name': 'advanced-analytics',
                'version': '1.0.0',
                'description': '고급 분석 플러그인',
                'author': 'Your Program Team',
                'category': 'analytics',
                'downloads': 1250,
                'rating': 4.8,
                'price': 0,
                'tags': ['analytics', 'ai', 'machine-learning']
            },
            {
                'name': 'workflow-automation',
                'version': '1.2.0',
                'description': '워크플로우 자동화 플러그인',
                'author': 'Automation Labs',
                'category': 'automation',
                'downloads': 890,
                'rating': 4.6,
                'price': 29.99,
                'tags': ['automation', 'workflow', 'productivity']
            },
            {
                'name': 'security-monitor',
                'version': '2.1.0',
                'description': '보안 모니터링 플러그인',
                'author': 'Security Pro',
                'category': 'security',
                'downloads': 2100,
                'rating': 4.9,
                'price': 49.99,
                'tags': ['security', 'monitoring', 'compliance']
            }
        ]
        
        return jsonify({
            'status': 'success',
            'plugins': marketplace_plugins,
            'total_count': len(marketplace_plugins),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"마켓플레이스 조회 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '마켓플레이스 조회 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_plugin_bp.route('/dependencies/<plugin_name>', methods=['GET'])
@cross_origin()
def check_dependencies(plugin_name: str):
    """의존성 확인"""
    try:
        dependencies_met = plugin_manager.check_dependencies(plugin_name)
        
        plugin_info = plugin_manager.get_plugin_info(plugin_name)
        if not plugin_info:
            return jsonify({
                'error': f'플러그인 {plugin_name}을 찾을 수 없습니다',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        dependencies = plugin_info['metadata']['dependencies']
        dependency_status = {}
        
        for dep in dependencies:
            dep_info = plugin_manager.get_plugin_info(dep)
            dependency_status[dep] = {
                'installed': dep_info is not None,
                'active': dep_info['metadata']['status'] == 'active' if dep_info else False,
                'version': dep_info['metadata']['version'] if dep_info else None
            }
        
        return jsonify({
            'status': 'success',
            'plugin_name': plugin_name,
            'dependencies_met': dependencies_met,
            'dependencies': dependency_status,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"의존성 확인 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '의존성 확인 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_plugin_bp.route('/stats', methods=['GET'])
@cross_origin()
def get_plugin_stats():
    """플러그인 통계"""
    try:
        plugins = plugin_manager.list_plugins()
        
        # 카테고리별 통계
        categories = {}
        statuses = {}
        
        for plugin in plugins:
            category = plugin['metadata']['category']
            status = plugin['metadata']['status']
            
            categories[category] = categories.get(category, 0) + 1
            statuses[status] = statuses.get(status, 0) + 1
        
        # 활성 플러그인 수
        active_count = statuses.get('active', 0)
        total_count = len(plugins)
        
        return jsonify({
            'status': 'success',
            'stats': {
                'total_plugins': total_count,
                'active_plugins': active_count,
                'inactive_plugins': statuses.get('inactive', 0),
                'error_plugins': statuses.get('error', 0),
                'categories': categories,
                'statuses': statuses,
                'activation_rate': (active_count / total_count * 100) if total_count > 0 else 0
            },
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"플러그인 통계 조회 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '플러그인 통계 조회 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# 에러 핸들러
@advanced_plugin_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'API 엔드포인트를 찾을 수 없습니다',
        'timestamp': datetime.now().isoformat()
    }), 404

@advanced_plugin_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': '서버 내부 오류가 발생했습니다',
        'timestamp': datetime.now().isoformat()
    }), 500 