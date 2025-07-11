#!/usr/bin/env python3
"""
플러그인 운영 및 모니터링 API
실제 운영 환경에서 플러그인 시스템의 안정성과 성능을 관리하는 API
"""

import logging
from flask import Blueprint, jsonify, request

# 동적 import로 안전하게 처리
try:
    import importlib
    operations_module = importlib.import_module('core.backend.plugin_operations_manager')
    plugin_operations_manager = operations_module.plugin_operations_manager
except ImportError as e:
    logging.warning(f"plugin_operations_manager 모듈을 import할 수 없습니다: {e}")
    plugin_operations_manager = None

logger = logging.getLogger(__name__)

# 블루프린트 생성
plugin_operations_bp = Blueprint('plugin_operations', __name__, url_prefix='/api/plugin-operations')

@plugin_operations_bp.route('/status', methods=['GET'])
def get_operations_status():
    """운영 상태 조회"""
    try:
        if plugin_operations_manager is None:
            return jsonify({
                'status': 'error',
                'message': '플러그인 운영 관리자가 초기화되지 않았습니다'
            }), 500
        
        status = plugin_operations_manager.get_operations_status()
        return jsonify({
            'status': 'success',
            'data': status
        })
        
    except Exception as e:
        logger.error(f"운영 상태 조회 실패: {e}")
        return jsonify({
            'status': 'error',
            'message': f'운영 상태 조회 실패: {e}'
        }), 500

@plugin_operations_bp.route('/start', methods=['POST'])
def start_operations():
    """운영 모니터링 시작"""
    try:
        if plugin_operations_manager is None:
            return jsonify({
                'status': 'error',
                'message': '플러그인 운영 관리자가 초기화되지 않았습니다'
            }), 500
        
        result = plugin_operations_manager.start_operations()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"운영 모니터링 시작 실패: {e}")
        return jsonify({
            'status': 'error',
            'message': f'운영 모니터링 시작 실패: {e}'
        }), 500

@plugin_operations_bp.route('/stop', methods=['POST'])
def stop_operations():
    """운영 모니터링 중지"""
    try:
        if plugin_operations_manager is None:
            return jsonify({
                'status': 'error',
                'message': '플러그인 운영 관리자가 초기화되지 않았습니다'
            }), 500
        
        result = plugin_operations_manager.stop_operations()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"운영 모니터링 중지 실패: {e}")
        return jsonify({
            'status': 'error',
            'message': f'운영 모니터링 중지 실패: {e}'
        }), 500

@plugin_operations_bp.route('/metrics', methods=['GET'])
def get_performance_metrics():
    """성능 메트릭 조회"""
    try:
        if plugin_operations_manager is None:
            return jsonify({
                'status': 'error',
                'message': '플러그인 운영 관리자가 초기화되지 않았습니다'
            }), 500
        
        metric_type = request.args.get('type', 'all')
        metrics = plugin_operations_manager.get_performance_metrics(metric_type)
        
        return jsonify({
            'status': 'success',
            'data': metrics
        })
        
    except Exception as e:
        logger.error(f"성능 메트릭 조회 실패: {e}")
        return jsonify({
            'status': 'error',
            'message': f'성능 메트릭 조회 실패: {e}'
        }), 500

@plugin_operations_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """알림 조회"""
    try:
        if plugin_operations_manager is None:
            return jsonify({
                'status': 'error',
                'message': '플러그인 운영 관리자가 초기화되지 않았습니다'
            }), 500
        
        alert_level = request.args.get('level', 'all')
        alerts = plugin_operations_manager.get_alerts(alert_level)
        
        return jsonify({
            'status': 'success',
            'data': alerts
        })
        
    except Exception as e:
        logger.error(f"알림 조회 실패: {e}")
        return jsonify({
            'status': 'error',
            'message': f'알림 조회 실패: {e}'
        }), 500

@plugin_operations_bp.route('/alerts/clear', methods=['POST'])
def clear_alerts():
    """알림 정리"""
    try:
        if plugin_operations_manager is None:
            return jsonify({
                'status': 'error',
                'message': '플러그인 운영 관리자가 초기화되지 않았습니다'
            }), 500
        
        data = request.get_json() or {}
        alert_level = data.get('level', 'all')
        
        plugin_operations_manager.clear_alerts(alert_level)
        
        return jsonify({
            'status': 'success',
            'message': f'{alert_level} 레벨 알림이 정리되었습니다'
        })
        
    except Exception as e:
        logger.error(f"알림 정리 실패: {e}")
        return jsonify({
            'status': 'error',
            'message': f'알림 정리 실패: {e}'
        }), 500

@plugin_operations_bp.route('/thresholds', methods=['GET'])
def get_thresholds():
    """임계값 조회"""
    try:
        if plugin_operations_manager is None:
            return jsonify({
                'status': 'error',
                'message': '플러그인 운영 관리자가 초기화되지 않았습니다'
            }), 500
        
        thresholds = plugin_operations_manager.get_thresholds()
        
        return jsonify({
            'status': 'success',
            'data': thresholds
        })
        
    except Exception as e:
        logger.error(f"임계값 조회 실패: {e}")
        return jsonify({
            'status': 'error',
            'message': f'임계값 조회 실패: {e}'
        }), 500

@plugin_operations_bp.route('/thresholds', methods=['POST'])
def set_threshold():
    """임계값 설정"""
    try:
        if plugin_operations_manager is None:
            return jsonify({
                'status': 'error',
                'message': '플러그인 운영 관리자가 초기화되지 않았습니다'
            }), 500
        
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': '요청 데이터가 없습니다'
            }), 400
        
        threshold_name = data.get('name')
        value = data.get('value')
        
        if threshold_name is None or value is None:
            return jsonify({
                'status': 'error',
                'message': '임계값 이름과 값이 필요합니다'
            }), 400
        
        success = plugin_operations_manager.set_threshold(threshold_name, float(value))
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'임계값 설정 완료: {threshold_name} = {value}'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'알 수 없는 임계값: {threshold_name}'
            }), 400
        
    except ValueError:
        return jsonify({
            'status': 'error',
            'message': '임계값은 숫자여야 합니다'
        }), 400
    except Exception as e:
        logger.error(f"임계값 설정 실패: {e}")
        return jsonify({
            'status': 'error',
            'message': f'임계값 설정 실패: {e}'
        }), 500

@plugin_operations_bp.route('/health', methods=['GET'])
def get_health_status():
    """헬스 상태 조회"""
    try:
        if plugin_operations_manager is None:
            return jsonify({
                'status': 'error',
                'message': '플러그인 운영 관리자가 초기화되지 않았습니다'
            }), 500
        
        health_status = plugin_operations_manager._perform_health_check()
        
        return jsonify({
            'status': 'success',
            'data': health_status
        })
        
    except Exception as e:
        logger.error(f"헬스 상태 조회 실패: {e}")
        return jsonify({
            'status': 'error',
            'message': f'헬스 상태 조회 실패: {e}'
        }), 500

@plugin_operations_bp.route('/logs', methods=['GET'])
def get_operation_logs():
    """운영 로그 조회"""
    try:
        if plugin_operations_manager is None:
            return jsonify({
                'status': 'error',
                'message': '플러그인 운영 관리자가 초기화되지 않았습니다'
            }), 500
        
        limit = request.args.get('limit', 100, type=int)
        operation_type = request.args.get('type')
        
        logs = list(plugin_operations_manager.operation_logs)
        
        # 필터링
        if operation_type:
            logs = [log for log in logs if log.get('operation_type') == operation_type]
        
        # 최신 순으로 정렬
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # 제한
        logs = logs[:limit]
        
        return jsonify({
            'status': 'success',
            'data': {
                'logs': logs,
                'total_count': len(logs)
            }
        })
        
    except Exception as e:
        logger.error(f"운영 로그 조회 실패: {e}")
        return jsonify({
            'status': 'error',
            'message': f'운영 로그 조회 실패: {e}'
        }), 500

@plugin_operations_bp.route('/record', methods=['POST'])
def record_operation():
    """운영 로그 기록"""
    try:
        if plugin_operations_manager is None:
            return jsonify({
                'status': 'error',
                'message': '플러그인 운영 관리자가 초기화되지 않았습니다'
            }), 500
        
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': '요청 데이터가 없습니다'
            }), 400
        
        operation_type = data.get('operation_type')
        success = data.get('success', True)
        response_time = data.get('response_time', 0.0)
        details = data.get('details', {})
        
        if operation_type is None:
            return jsonify({
                'status': 'error',
                'message': '운영 타입이 필요합니다'
            }), 400
        
        plugin_operations_manager.record_operation(
            operation_type=operation_type,
            success=success,
            response_time=response_time,
            details=details
        )
        
        return jsonify({
            'status': 'success',
            'message': '운영 로그가 기록되었습니다'
        })
        
    except Exception as e:
        logger.error(f"운영 로그 기록 실패: {e}")
        return jsonify({
            'status': 'error',
            'message': f'운영 로그 기록 실패: {e}'
        }), 500

@plugin_operations_bp.route('/<plugin_name>/status', methods=['GET'])
def get_plugin_status(plugin_name):
    """특정 플러그인 상태 조회"""
    try:
        if plugin_operations_manager is None:
            return jsonify({
                'status': 'error',
                'message': '플러그인 운영 관리자가 초기화되지 않았습니다'
            }), 500
        
        # 플러그인 이름 검증
        if not plugin_name or not isinstance(plugin_name, str):
            return jsonify({
                'status': 'error',
                'message': '유효하지 않은 플러그인 이름입니다'
            }), 400
        
        # 플러그인 존재 여부 확인
        from core.backend.plugin_loader import plugin_loader
        if plugin_name not in plugin_loader.loaded_plugins:
            return jsonify({
                'status': 'error',
                'message': f'플러그인 "{plugin_name}"을 찾을 수 없습니다'
            }), 404
        
        # 플러그인 상태 조회
        status = plugin_operations_manager.get_plugin_status(plugin_name)
        
        return jsonify({
            'status': 'success',
            'data': {
                'plugin_name': plugin_name,
                'status': status,
                'last_updated': plugin_operations_manager.get_last_update_time(plugin_name)
            }
        })
        
    except Exception as e:
        logger.error(f"플러그인 {plugin_name} 상태 조회 실패: {e}")
        return jsonify({
            'status': 'error',
            'message': f'플러그인 상태 조회 실패: {e}'
        }), 500

@plugin_operations_bp.route('/<plugin_name>/metrics', methods=['GET'])
def get_plugin_metrics(plugin_name):
    """특정 플러그인 성능 메트릭 조회"""
    try:
        if plugin_operations_manager is None:
            return jsonify({
                'status': 'error',
                'message': '플러그인 운영 관리자가 초기화되지 않았습니다'
            }), 500
        
        # 플러그인 이름 검증
        if not plugin_name or not isinstance(plugin_name, str):
            return jsonify({
                'status': 'error',
                'message': '유효하지 않은 플러그인 이름입니다'
            }), 400
        
        # 플러그인 존재 여부 확인
        from core.backend.plugin_loader import plugin_loader
        if plugin_name not in plugin_loader.loaded_plugins:
            return jsonify({
                'status': 'error',
                'message': f'플러그인 "{plugin_name}"을 찾을 수 없습니다'
            }), 404
        
        # 메트릭 타입 필터링
        metric_type = request.args.get('type', 'all')
        
        # 플러그인 메트릭 조회
        metrics = plugin_operations_manager.get_plugin_metrics(plugin_name, metric_type)
        
        return jsonify({
            'status': 'success',
            'data': {
                'plugin_name': plugin_name,
                'metrics': metrics,
                'last_updated': plugin_operations_manager.get_last_update_time(plugin_name)
            }
        })
        
    except Exception as e:
        logger.error(f"플러그인 {plugin_name} 메트릭 조회 실패: {e}")
        return jsonify({
            'status': 'error',
            'message': f'플러그인 메트릭 조회 실패: {e}'
        }), 500

@plugin_operations_bp.route('/<plugin_name>/restart', methods=['POST'])
def restart_plugin(plugin_name):
    """특정 플러그인 재시작"""
    try:
        if plugin_operations_manager is None:
            return jsonify({
                'status': 'error',
                'message': '플러그인 운영 관리자가 초기화되지 않았습니다'
            }), 500
        
        # 플러그인 이름 검증
        if not plugin_name or not isinstance(plugin_name, str):
            return jsonify({
                'status': 'error',
                'message': '유효하지 않은 플러그인 이름입니다'
            }), 400
        
        # 플러그인 존재 여부 확인
        from core.backend.plugin_loader import plugin_loader
        if plugin_name not in plugin_loader.loaded_plugins:
            return jsonify({
                'status': 'error',
                'message': f'플러그인 "{plugin_name}"을 찾을 수 없습니다'
            }), 404
        
        # 플러그인 재시작
        result = plugin_operations_manager.restart_plugin(plugin_name)
        
        return jsonify({
            'status': 'success',
            'message': f'플러그인 "{plugin_name}"이 재시작되었습니다',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"플러그인 {plugin_name} 재시작 실패: {e}")
        return jsonify({
            'status': 'error',
            'message': f'플러그인 재시작 실패: {e}'
        }), 500 