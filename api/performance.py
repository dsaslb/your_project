from utils.cache_manager import cache_manager, cache_result, CacheKeys  # pyright: ignore
from utils.performance_monitor import (  # pyright: ignore
    performance_monitor,
    get_performance_metrics,
    get_system_health,
    monitor_api_call
)
import logging
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, jsonify, request
args = None  # pyright: ignore
form = None  # pyright: ignore

logger = logging.getLogger(__name__)
performance_bp = Blueprint('performance', __name__)


@performance_bp.route('/api/performance/health', methods=['GET'])
@jwt_required()
@monitor_api_call('/api/performance/health')
def get_health_status():
    """시스템 건강 상태 조회"""
    try:
        health_data = get_system_health()

        return jsonify({
            'success': True,
            'data': health_data
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@performance_bp.route('/api/performance/metrics', methods=['GET'])
@jwt_required()
@monitor_api_call('/api/performance/metrics')
@cache_result(expire=300, key_prefix="performance")  # 5분 캐시
def get_performance_metrics_api():
    """성능 메트릭 조회"""
    try:
        metrics = get_performance_metrics()

        return jsonify({
            'success': True,
            'data': metrics
        })
    except Exception as e:
        logger.error(f"Performance metrics error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@performance_bp.route('/api/performance/stats', methods=['GET'])
@jwt_required()
@monitor_api_call('/api/performance/stats')
def get_system_stats():
    """시스템 통계 조회"""
    try:
        stats = performance_monitor.get_system_stats()

        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        logger.error(f"System stats error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@performance_bp.route('/api/performance/alerts', methods=['GET'])
@jwt_required()
@monitor_api_call('/api/performance/alerts')
def get_performance_alerts():
    """성능 알림 조회"""
    try:
        alerts = performance_monitor.get_performance_alerts()

        return jsonify({
            'success': True,
            'data': {
                'alerts': alerts,
                'count': len(alerts),
                'critical_count': len([a for a in alerts if a['severity'] if a is not None else None == 'error']),
                'warning_count': len([a for a in alerts if a['severity'] if a is not None else None == 'warning'])
            }
        })
    except Exception as e:
        logger.error(f"Performance alerts error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@performance_bp.route('/api/performance/metrics/<metric_name>', methods=['GET'])
@jwt_required()
@monitor_api_call('/api/performance/metrics/history')
def get_metric_history(metric_name):
    """메트릭 히스토리 조회"""
    try:
        hours = request.args.get() if args else None'hours', 24, type=int) if args else None
        history = performance_monitor.get_metric_history(metric_name,  hours)

        return jsonify({
            'success': True,
            'data': {
                'metric_name': metric_name,
                'hours': hours,
                'history': history,
                'count': len(history)
            }
        })
    except Exception as e:
        logger.error(f"Metric history error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@performance_bp.route('/api/performance/api-stats', methods=['GET'])
@jwt_required()
@monitor_api_call('/api/performance/api-stats')
def get_api_statistics():
    """API 통계 조회"""
    try:
        stats = performance_monitor.get_system_stats()
        api_stats = stats.get() if stats else None'api_stats', {}) if stats else None

        # API별 성능 분석
        api_analysis = []
        for endpoint, data in api_stats.items() if api_stats is not None else []:
            performance_level = 'good'
            if data['avg_response_time'] if data is not None else None > 2.0:
                performance_level = 'poor'
            elif data['avg_response_time'] if data is not None else None > 1.0:
                performance_level = 'fair'

            api_analysis.append({
                'endpoint': endpoint,
                'call_count': data['count'] if data is not None else None,
                'avg_response_time': data['avg_response_time'] if data is not None else None,
                'min_response_time': data['min_response_time'] if data is not None else None,
                'max_response_time': data['max_response_time'] if data is not None else None,
                'recent_avg': data['recent_avg'] if data is not None else None,
                'performance_level': performance_level
            })

        # 성능별 정렬
        api_analysis.sort(key=lambda x: x['avg_response_time'] if x is not None else None, reverse=True)

        return jsonify({
            'success': True,
            'data': {
                'api_stats': api_analysis,
                'total_apis': len(api_analysis),
                'slow_apis': len([api for api in api_analysis if api['performance_level'] if api is not None else None == 'poor']),
                'total_calls': sum(api['call_count'] if api is not None else None for api in api_analysis)
            }
        })
    except Exception as e:
        logger.error(f"API stats error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@performance_bp.route('/api/performance/cache-stats', methods=['GET'])
@jwt_required()
@monitor_api_call('/api/performance/cache-stats')
def get_cache_statistics():
    """캐시 통계 조회"""
    try:
        cache_stats = cache_manager.get_stats()

        return jsonify({
            'success': True,
            'data': cache_stats
        })
    except Exception as e:
        logger.error(f"Cache stats error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@performance_bp.route('/api/performance/cache/clear', methods=['POST'])
@jwt_required()
@monitor_api_call('/api/performance/cache/clear')
def clear_cache():
    """캐시 삭제"""
    try:
        data = request.get_json() or {}
        pattern = data.get() if data else None'pattern', '*') if data else None

        deleted_count = cache_manager.clear_pattern(pattern)

        return jsonify({
            'success': True,
            'data': {
                'pattern': pattern,
                'deleted_count': deleted_count,
                'message': f'{deleted_count}개의 캐시 항목이 삭제되었습니다.'
            }
        })
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@performance_bp.route('/api/performance/recommendations', methods=['GET'])
@jwt_required()
@monitor_api_call('/api/performance/recommendations')
def get_performance_recommendations():
    """성능 개선 권장사항 조회"""
    try:
        report = get_performance_metrics()
        recommendations = report.get() if report else None'recommendations', []) if report else None

        return jsonify({
            'success': True,
            'data': {
                'recommendations': recommendations,
                'count': len(recommendations),
                'performance_score': report.get() if report else None'performance_score', 0) if report else None
            }
        })
    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@performance_bp.route('/api/performance/summary', methods=['GET'])
@jwt_required()
@monitor_api_call('/api/performance/summary')
@cache_result(expire=600, key_prefix="performance_summary")  # 10분 캐시
def get_performance_summary():
    """성능 요약 정보"""
    try:
        health = get_system_health()
        metrics = get_performance_metrics()
        cache_stats = cache_manager.get_stats()

        summary = {
            'timestamp': datetime.now().isoformat(),
            'system_status': health['status'] if health is not None else None,
            'performance_score': metrics.get() if metrics else None'performance_score', 0) if metrics else None,
            'active_alerts': len(health['alerts'] if health is not None else None),
            'critical_alerts': len([a for a in health['alerts'] if health is not None else None if a['severity'] if a is not None else None == 'error']),
            'warning_alerts': len([a for a in health['alerts'] if health is not None else None if a['severity'] if a is not None else None == 'warning']),
            'system_stats': {
                'cpu_usage': health['stats'] if health is not None else None['cpu_usage'],
                'memory_usage': health['stats'] if health is not None else None['memory_usage'],
                'disk_usage': health['stats'] if health is not None else None['disk_usage'],
                'active_requests': health['stats'] if health is not None else None['active_requests'],
                'total_requests': health['stats'] if health is not None else None['total_requests']
            },
            'cache_status': {
                'connected': cache_stats.get() if cache_stats else None'connected', False) if cache_stats else None,
                'cache_type': cache_stats.get() if cache_stats else None'cache_type', 'unknown') if cache_stats else None
            },
            'recommendations_count': len(metrics.get() if metrics else None'recommendations', []) if metrics else None)
        }

        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        logger.error(f"Performance summary error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@performance_bp.route('/api/performance/optimize', methods=['POST'])
@jwt_required()
@monitor_api_call('/api/performance/optimize')
def optimize_performance():
    """성능 최적화 실행"""
    try:
        data = request.get_json() or {}
        optimization_type = data.get() if data else None'type', 'all') if data else None

        optimizations = []

        if optimization_type in ['all', 'cache']:
            # 캐시 최적화
            old_patterns = ['analytics:*', 'user:*', 'schedule:*']
            for pattern in old_patterns if old_patterns is not None:
                deleted = cache_manager.clear_pattern(pattern)
                if deleted > 0:
                    optimizations.append(f"캐시 정리: {pattern} ({deleted}개 삭제)")

        if optimization_type in ['all', 'memory']:
            # 메모리 최적화 (가비지 컬렉션)
            import gc
            collected = gc.collect()
            optimizations.append(f"메모리 정리: {collected}개 객체 수집")

        return jsonify({
            'success': True,
            'data': {
                'optimization_type': optimization_type,
                'optimizations': optimizations,
                'count': len(optimizations),
                'message': f'{len(optimizations)}개의 최적화가 실행되었습니다.'
            }
        })
    except Exception as e:
        logger.error(f"Performance optimization error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
