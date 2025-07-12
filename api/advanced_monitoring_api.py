"""
고급 플러그인 모니터링 API
"""

from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from functools import wraps
from datetime import datetime, timedelta
import json
import logging

from core.backend.advanced_plugin_monitoring import advanced_monitor
from api.gateway import token_required, role_required

logger = logging.getLogger(__name__)

advanced_monitoring_bp = Blueprint('advanced_monitoring', __name__)

def log_request(f):
    """요청 로깅 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(f"API 요청: {request.method} {request.path}")
        return f(*args, **kwargs)
    return decorated_function

@advanced_monitoring_bp.route('/api/advanced-monitoring/start', methods=['POST'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
@cross_origin()
def start_advanced_monitoring():
    """고급 모니터링 시작"""
    try:
        advanced_monitor.start_monitoring()
        
        return jsonify({
            'success': True,
            'message': '고급 플러그인 모니터링이 시작되었습니다.',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"고급 모니터링 시작 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_monitoring_bp.route('/api/advanced-monitoring/stop', methods=['POST'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
@cross_origin()
def stop_advanced_monitoring():
    """고급 모니터링 중지"""
    try:
        advanced_monitor.stop_monitoring()
        
        return jsonify({
            'success': True,
            'message': '고급 플러그인 모니터링이 중지되었습니다.',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"고급 모니터링 중지 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_monitoring_bp.route('/api/advanced-monitoring/register-plugin', methods=['POST'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
@cross_origin()
def register_plugin():
    """플러그인 등록"""
    try:
        data = request.get_json()
        
        if not data or 'plugin_id' not in data or 'plugin_name' not in data:
            return jsonify({
                'success': False,
                'error': 'plugin_id와 plugin_name이 필요합니다.'
            }), 400
            
        plugin_id = data['plugin_id']
        plugin_name = data['plugin_name']
        
        advanced_monitor.register_plugin(plugin_id, plugin_name)
        
        return jsonify({
            'success': True,
            'message': f'플러그인 {plugin_name}이 등록되었습니다.',
            'plugin_id': plugin_id,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"플러그인 등록 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_monitoring_bp.route('/api/advanced-monitoring/update-metrics', methods=['POST'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
@cross_origin()
def update_metrics():
    """상세 메트릭 업데이트"""
    try:
        data = request.get_json()
        
        if not data or 'plugin_id' not in data or 'metrics' not in data:
            return jsonify({
                'success': False,
                'error': 'plugin_id와 metrics가 필요합니다.'
            }), 400
            
        plugin_id = data['plugin_id']
        metrics = data['metrics']
        
        advanced_monitor.update_detailed_metrics(plugin_id, metrics)
        
        return jsonify({
            'success': True,
            'message': '메트릭이 업데이트되었습니다.',
            'plugin_id': plugin_id,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"메트릭 업데이트 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_monitoring_bp.route('/api/advanced-monitoring/metrics/<plugin_id>', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
@cross_origin()
def get_detailed_metrics(plugin_id):
    """상세 메트릭 조회"""
    try:
        hours = request.args.get('hours', 24, type=int)
        
        metrics = advanced_monitor.get_detailed_metrics(plugin_id, hours)
        
        # JSON 직렬화 가능한 형태로 변환
        serialized_metrics = []
        for metric in metrics:
            serialized_metric = {
                'plugin_id': metric.plugin_id,
                'timestamp': metric.timestamp.isoformat(),
                'cpu_usage': metric.cpu_usage,
                'memory_usage': metric.memory_usage,
                'memory_rss': metric.memory_rss,
                'memory_vms': metric.memory_vms,
                'response_time_p50': metric.response_time_p50,
                'response_time_p95': metric.response_time_p95,
                'response_time_p99': metric.response_time_p99,
                'error_rate': metric.error_rate,
                'throughput': metric.throughput,
                'active_connections': metric.active_connections,
                'total_connections': metric.total_connections,
                'disk_read_bytes': metric.disk_read_bytes,
                'disk_write_bytes': metric.disk_write_bytes,
                'network_rx_bytes': metric.network_rx_bytes,
                'network_tx_bytes': metric.network_tx_bytes,
                'custom_metrics': metric.custom_metrics
            }
            serialized_metrics.append(serialized_metric)
        
        return jsonify({
            'success': True,
            'plugin_id': plugin_id,
            'metrics': serialized_metrics,
            'count': len(serialized_metrics),
            'hours': hours,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"상세 메트릭 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_monitoring_bp.route('/api/advanced-monitoring/trends/<plugin_id>', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
@cross_origin()
def get_performance_trends(plugin_id):
    """성능 트렌드 조회"""
    try:
        trends = advanced_monitor.get_performance_trends(plugin_id)
        
        # JSON 직렬화 가능한 형태로 변환
        serialized_trends = {}
        for metric_type, trend in trends.items():
            serialized_trends[metric_type.value] = {
                'plugin_id': trend.plugin_id,
                'metric_type': trend.metric_type.value,
                'current_value': trend.current_value,
                'previous_value': trend.previous_value,
                'change_percent': trend.change_percent,
                'trend_direction': trend.trend_direction,
                'trend_strength': trend.trend_strength
            }
        
        return jsonify({
            'success': True,
            'plugin_id': plugin_id,
            'trends': serialized_trends,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"성능 트렌드 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_monitoring_bp.route('/api/advanced-monitoring/usage-patterns/<plugin_id>', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
@cross_origin()
def get_usage_patterns(plugin_id):
    """사용량 패턴 조회"""
    try:
        patterns = advanced_monitor.get_usage_patterns(plugin_id)
        
        if not patterns:
            return jsonify({
                'success': False,
                'error': '사용량 패턴 데이터가 없습니다.'
            }), 404
        
        # JSON 직렬화 가능한 형태로 변환
        serialized_patterns = {
            'plugin_id': patterns.plugin_id,
            'peak_hours': patterns.peak_hours,
            'low_usage_hours': patterns.low_usage_hours,
            'daily_usage_pattern': patterns.daily_usage_pattern,
            'weekly_usage_pattern': patterns.weekly_usage_pattern,
            'monthly_usage_pattern': patterns.monthly_usage_pattern
        }
        
        return jsonify({
            'success': True,
            'plugin_id': plugin_id,
            'patterns': serialized_patterns,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"사용량 패턴 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_monitoring_bp.route('/api/advanced-monitoring/analytics/<plugin_id>', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
@cross_origin()
def get_analytics(plugin_id):
    """종합 분석 데이터 조회"""
    try:
        # 시간 범위 파라미터
        hours = request.args.get('hours', 24, type=int)
        
        # 상세 메트릭
        metrics = advanced_monitor.get_detailed_metrics(plugin_id, hours)
        
        # 성능 트렌드
        trends = advanced_monitor.get_performance_trends(plugin_id)
        
        # 사용량 패턴
        patterns = advanced_monitor.get_usage_patterns(plugin_id)
        
        # 통계 계산
        if metrics:
            cpu_values = [m.cpu_usage for m in metrics]
            memory_values = [m.memory_usage for m in metrics]
            response_times = [m.response_time_p95 for m in metrics]
            error_rates = [m.error_rate for m in metrics]
            
            stats = {
                'cpu': {
                    'average': sum(cpu_values) / len(cpu_values),
                    'max': max(cpu_values),
                    'min': min(cpu_values),
                    'current': cpu_values[-1] if cpu_values else 0
                },
                'memory': {
                    'average': sum(memory_values) / len(memory_values),
                    'max': max(memory_values),
                    'min': min(memory_values),
                    'current': memory_values[-1] if memory_values else 0
                },
                'response_time': {
                    'average': sum(response_times) / len(response_times),
                    'max': max(response_times),
                    'min': min(response_times),
                    'current': response_times[-1] if response_times else 0
                },
                'error_rate': {
                    'average': sum(error_rates) / len(error_rates),
                    'max': max(error_rates),
                    'min': min(error_rates),
                    'current': error_rates[-1] if error_rates else 0
                }
            }
        else:
            stats = {}
        
        # JSON 직렬화
        serialized_metrics = []
        for metric in metrics:
            serialized_metrics.append({
                'timestamp': metric.timestamp.isoformat(),
                'cpu_usage': metric.cpu_usage,
                'memory_usage': metric.memory_usage,
                'response_time_p95': metric.response_time_p95,
                'error_rate': metric.error_rate,
                'throughput': metric.throughput
            })
        
        serialized_trends = {}
        for metric_type, trend in trends.items():
            serialized_trends[metric_type.value] = {
                'current_value': trend.current_value,
                'change_percent': trend.change_percent,
                'trend_direction': trend.trend_direction,
                'trend_strength': trend.trend_strength
            }
        
        serialized_patterns = None
        if patterns:
            serialized_patterns = {
                'peak_hours': patterns.peak_hours,
                'low_usage_hours': patterns.low_usage_hours,
                'daily_usage_pattern': patterns.daily_usage_pattern
            }
        
        return jsonify({
            'success': True,
            'plugin_id': plugin_id,
            'analytics': {
                'metrics': serialized_metrics,
                'trends': serialized_trends,
                'patterns': serialized_patterns,
                'statistics': stats
            },
            'hours': hours,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"분석 데이터 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_monitoring_bp.route('/api/advanced-monitoring/status', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
@cross_origin()
def get_monitoring_status():
    """모니터링 상태 조회"""
    try:
        # 모니터링 중인 플러그인 수
        plugin_count = len(advanced_monitor.metrics_buffer)
        
        # 최근 알림 수 (기본 모니터에서 가져오기)
        from core.backend.plugin_monitoring import plugin_monitor
        active_alerts = plugin_monitor.get_active_alerts()
        
        status = {
            'monitoring_active': advanced_monitor.monitoring_active,
            'plugin_count': plugin_count,
            'active_alerts': len(active_alerts),
            'database_path': advanced_monitor.db_path,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        logger.error(f"모니터링 상태 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_monitoring_bp.route('/api/advanced-monitoring/export/<plugin_id>', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
@cross_origin()
def export_plugin_data(plugin_id):
    """플러그인 데이터 내보내기"""
    try:
        # 시간 범위 파라미터
        hours = request.args.get('hours', 24, type=int)
        format_type = request.args.get('format', 'json')
        
        # 데이터 수집
        metrics = advanced_monitor.get_detailed_metrics(plugin_id, hours)
        trends = advanced_monitor.get_performance_trends(plugin_id)
        patterns = advanced_monitor.get_usage_patterns(plugin_id)
        
        # JSON 직렬화
        export_data = {
            'plugin_id': plugin_id,
            'export_timestamp': datetime.utcnow().isoformat(),
            'time_range_hours': hours,
            'metrics': [],
            'trends': {},
            'patterns': None
        }
        
        # 메트릭 데이터
        for metric in metrics:
            export_data['metrics'].append({
                'timestamp': metric.timestamp.isoformat(),
                'cpu_usage': metric.cpu_usage,
                'memory_usage': metric.memory_usage,
                'response_time_p95': metric.response_time_p95,
                'error_rate': metric.error_rate,
                'throughput': metric.throughput,
                'active_connections': metric.active_connections,
                'disk_read_bytes': metric.disk_read_bytes,
                'disk_write_bytes': metric.disk_write_bytes,
                'network_rx_bytes': metric.network_rx_bytes,
                'network_tx_bytes': metric.network_tx_bytes
            })
        
        # 트렌드 데이터
        for metric_type, trend in trends.items():
            export_data['trends'][metric_type.value] = {
                'current_value': trend.current_value,
                'change_percent': trend.change_percent,
                'trend_direction': trend.trend_direction,
                'trend_strength': trend.trend_strength
            }
        
        # 패턴 데이터
        if patterns:
            export_data['patterns'] = {
                'peak_hours': patterns.peak_hours,
                'low_usage_hours': patterns.low_usage_hours,
                'daily_usage_pattern': patterns.daily_usage_pattern
            }
        
        if format_type == 'csv':
            # CSV 형식으로 변환 (간단한 구현)
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 헤더
            writer.writerow(['timestamp', 'cpu_usage', 'memory_usage', 'response_time_p95', 'error_rate', 'throughput'])
            
            # 데이터
            for metric in metrics:
                writer.writerow([
                    metric.timestamp.isoformat(),
                    metric.cpu_usage,
                    metric.memory_usage,
                    metric.response_time_p95,
                    metric.error_rate,
                    metric.throughput
                ])
            
            from flask import Response
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename={plugin_id}_metrics.csv'}
            )
        else:
            # JSON 형식
            return jsonify({
                'success': True,
                'data': export_data
            })
            
    except Exception as e:
        logger.error(f"데이터 내보내기 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 