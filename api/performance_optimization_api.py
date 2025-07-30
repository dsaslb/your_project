"""
성능 최적화 API
시스템 성능 최적화 및 모니터링 엔드포인트
"""

from flask import Blueprint, jsonify, request
from utils.query_optimizer import query_optimizer
from utils.api_cache import api_cache
from utils.async_processor import async_processor
from utils.memory_optimizer import memory_optimizer
import logging

performance_optimization_bp = Blueprint('performance_optimization', __name__)
logger = logging.getLogger(__name__)

@performance_optimization_bp.route('/stats', methods=['GET'])
def get_performance_stats():
    """전체 성능 통계 조회"""
    try:
        stats = {
            'query_optimization': query_optimizer.get_performance_report(),
            'cache_stats': api_cache.get_cache_stats(),
            'async_tasks': async_processor.get_all_tasks(),
            'memory_optimization': memory_optimizer.get_optimization_stats()
        }
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        logger.error(f"성능 통계 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@performance_optimization_bp.route('/optimize/memory', methods=['POST'])
def optimize_memory():
    """메모리 최적화 실행"""
    try:
        result = memory_optimizer.optimize_memory()
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"메모리 최적화 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@performance_optimization_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """캐시 초기화"""
    try:
        pattern = request.json.get('pattern', '*') if request.json else '*'
        api_cache.invalidate_cache(pattern)
        query_optimizer.clear_cache()
        
        return jsonify({
            'success': True,
            'message': f'캐시 초기화 완료 (패턴: {pattern})'
        }), 200
        
    except Exception as e:
        logger.error(f"캐시 초기화 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@performance_optimization_bp.route('/tasks/cleanup', methods=['POST'])
def cleanup_tasks():
    """완료된 작업 정리"""
    try:
        max_age = request.json.get('max_age', 3600) if request.json else 3600
        async_processor.cleanup_completed_tasks(max_age)
        
        return jsonify({
            'success': True,
            'message': f'작업 정리 완료 (최대 나이: {max_age}초)'
        }), 200
        
    except Exception as e:
        logger.error(f"작업 정리 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@performance_optimization_bp.route('/health', methods=['GET'])
def get_health_status():
    """성능 상태 점검"""
    try:
        health_status = {
            'memory': memory_optimizer.check_memory_health(),
            'cache': api_cache.get_cache_stats(),
            'tasks': {
                'queue_size': async_processor.task_queue.qsize(),
                'running_tasks': len([t for t in async_processor.running_tasks.values() if t['status'] == 'running'])
            }
        }
        
        # 전체 상태 결정
        overall_status = 'healthy'
        if health_status['memory']['status'] in ['warning', 'critical']:
            overall_status = health_status['memory']['status']
        
        return jsonify({
            'success': True,
            'data': {
                'status': overall_status,
                'details': health_status
            }
        }), 200
        
    except Exception as e:
        logger.error(f"상태 점검 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 