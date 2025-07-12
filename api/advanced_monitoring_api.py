"""
고도화된 플러그인 모니터링 API
실시간 그래프/차트, 상세 로그/이벤트 추적, 드릴다운 보기
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any, Optional

# 고도화된 모니터링 시스템 import
try:
    from core.backend.advanced_plugin_monitoring import (
        advanced_plugin_monitor,
        MetricType,
        LogLevel,
        DetailedMetric,
        PluginLog,
        PluginEvent,
        PerformanceSnapshot
    )
except ImportError:
    advanced_plugin_monitor = None

logger = logging.getLogger(__name__)

# 블루프린트 생성
advanced_monitoring_bp = Blueprint('advanced_monitoring', __name__, url_prefix='/api/advanced-monitoring')

@advanced_monitoring_bp.route('/status', methods=['GET'])
@login_required
def get_monitoring_status():
    """모니터링 시스템 상태 조회"""
    if not advanced_plugin_monitor:
        return jsonify({
            'success': False,
            'message': '고도화된 모니터링 시스템이 사용할 수 없습니다.'
        }), 503
    
    try:
        real_time_stats = advanced_plugin_monitor.get_real_time_stats()
        all_summaries = advanced_plugin_monitor.get_all_plugins_summary()
        
        return jsonify({
            'success': True,
            'data': {
                'monitoring_active': advanced_plugin_monitor.monitoring_active,
                'total_plugins': len(real_time_stats),
                'active_plugins': len([s for s in all_summaries if s['status'] == 'active']),
                'inactive_plugins': len([s for s in all_summaries if s['status'] == 'inactive']),
                'total_metrics': sum(len(advanced_plugin_monitor.metrics_cache) for _ in advanced_plugin_monitor.metrics_cache),
                'total_logs': sum(len(advanced_plugin_monitor.logs_cache) for _ in advanced_plugin_monitor.logs_cache),
                'total_events': sum(len(advanced_plugin_monitor.events_cache) for _ in advanced_plugin_monitor.events_cache)
            }
        })
    except Exception as e:
        logger.error(f"모니터링 상태 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'상태 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500

@advanced_monitoring_bp.route('/plugins', methods=['GET'])
@login_required
def get_all_plugins():
    """모든 플러그인 요약 정보 조회"""
    if not advanced_plugin_monitor:
        return jsonify({
            'success': False,
            'message': '고도화된 모니터링 시스템이 사용할 수 없습니다.'
        }), 503
    
    try:
        summaries = advanced_plugin_monitor.get_all_plugins_summary()
        
        # JSON 직렬화를 위해 datetime 객체 변환
        for summary in summaries:
            if summary.get('last_update'):
                summary['last_update'] = summary['last_update'].isoformat()
        
        return jsonify({
            'success': True,
            'data': summaries
        })
    except Exception as e:
        logger.error(f"플러그인 목록 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'플러그인 목록 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500

@advanced_monitoring_bp.route('/plugins/<plugin_id>/summary', methods=['GET'])
@login_required
def get_plugin_summary(plugin_id: str):
    """특정 플러그인 요약 정보 조회"""
    if not advanced_plugin_monitor:
        return jsonify({
            'success': False,
            'message': '고도화된 모니터링 시스템이 사용할 수 없습니다.'
        }), 503
    
    try:
        summary = advanced_plugin_monitor.get_plugin_summary(plugin_id)
        
        if not summary:
            return jsonify({
                'success': False,
                'message': '플러그인을 찾을 수 없습니다.'
            }), 404
        
        # JSON 직렬화를 위해 datetime 객체 변환
        if summary.get('last_update'):
            summary['last_update'] = summary['last_update'].isoformat()
        
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        logger.error(f"플러그인 요약 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'플러그인 요약 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500

@advanced_monitoring_bp.route('/plugins/<plugin_id>/metrics', methods=['GET'])
@login_required
def get_plugin_metrics(plugin_id: str):
    """플러그인 메트릭 조회"""
    if not advanced_plugin_monitor:
        return jsonify({
            'success': False,
            'message': '고도화된 모니터링 시스템이 사용할 수 없습니다.'
        }), 503
    
    try:
        # 쿼리 파라미터
        metric_type = request.args.get('metric_type')
        hours = request.args.get('hours', 24, type=int)
        
        # 메트릭 타입 변환
        metric_enum = None
        if metric_type:
            try:
                metric_enum = MetricType(metric_type)
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': f'유효하지 않은 메트릭 타입입니다: {metric_type}'
                }), 400

        # metric_enum이 None일 경우 기본값을 지정 (예: MetricType.CPU 등)
        if metric_enum is None:
            # MetricType의 기본값을 지정하세요. 예시로 CPU로 설정 (실제 프로젝트에 맞게 수정)
            metric_enum = MetricType.CPU  # pyright: ignore

        metrics = advanced_plugin_monitor.get_plugin_metrics(plugin_id, metric_enum, hours)  # pyright: ignore
        
        # JSON 직렬화를 위해 데이터 변환
        metrics_data = []
        for metric in metrics:
            metrics_data.append({
                'plugin_id': metric.plugin_id,
                'metric_type': metric.metric_type.value,
                'value': metric.value,
                'timestamp': metric.timestamp.isoformat(),
                'metadata': metric.metadata
            })
        
        return jsonify({
            'success': True,
            'data': metrics_data
        })
    except Exception as e:
        logger.error(f"플러그인 메트릭 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'메트릭 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500

@advanced_monitoring_bp.route('/plugins/<plugin_id>/logs', methods=['GET'])
@login_required
def get_plugin_logs(plugin_id: str):
    """플러그인 로그 조회"""
    if not advanced_plugin_monitor:
        return jsonify({
            'success': False,
            'message': '고도화된 모니터링 시스템이 사용할 수 없습니다.'
        }), 503
    
    try:
        # 쿼리 파라미터
        level = request.args.get('level')
        hours = request.args.get('hours', 24, type=int)
        
        # 로그 레벨 변환
        log_level = None
        if level:
            try:
                log_level = LogLevel(level)
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': f'유효하지 않은 로그 레벨입니다: {level}'
                }), 400

        # log_level이 None인 경우 기본값을 설정 (예: LogLevel.INFO)
        if log_level is None:
            log_level = LogLevel.INFO  # pyright: ignore

        logs = advanced_plugin_monitor.get_plugin_logs(plugin_id, log_level, hours)  # pyright: ignore
        
        # JSON 직렬화를 위해 데이터 변환
        logs_data = []
        for log in logs:
            logs_data.append({
                'plugin_id': log.plugin_id,
                'level': log.level.value,
                'message': log.message,
                'timestamp': log.timestamp.isoformat(),
                'context': log.context,
                'traceback': log.traceback
            })
        
        return jsonify({
            'success': True,
            'data': logs_data
        })
    except Exception as e:
        logger.error(f"플러그인 로그 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'로그 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500

@advanced_monitoring_bp.route('/plugins/<plugin_id>/events', methods=['GET'])
@login_required
def get_plugin_events(plugin_id: str):
    """플러그인 이벤트 조회"""
    if not advanced_plugin_monitor:
        return jsonify({
            'success': False,
            'message': '고도화된 모니터링 시스템이 사용할 수 없습니다.'
        }), 503
    
    try:
        # 쿼리 파라미터
        event_type = request.args.get('event_type')
        hours = request.args.get('hours', 24, type=int)
        
        # event_type이 None일 경우 빈 문자열로 대체하여 타입 오류 방지
        safe_event_type = event_type if event_type is not None else ""
        events = advanced_plugin_monitor.get_plugin_events(plugin_id, safe_event_type, hours)  # pyright: ignore
        
        # JSON 직렬화를 위해 데이터 변환
        events_data = []
        for event in events:
            events_data.append({
                'plugin_id': event.plugin_id,
                'event_type': event.event_type,
                'description': event.description,
                'timestamp': event.timestamp.isoformat(),
                'severity': event.severity,
                'data': event.data
            })
        
        return jsonify({
            'success': True,
            'data': events_data
        })
    except Exception as e:
        logger.error(f"플러그인 이벤트 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'이벤트 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500

@advanced_monitoring_bp.route('/plugins/<plugin_id>/snapshots', methods=['GET'])
@login_required
def get_plugin_snapshots(plugin_id: str):
    """플러그인 성능 스냅샷 조회"""
    if not advanced_plugin_monitor:
        return jsonify({
            'success': False,
            'message': '고도화된 모니터링 시스템이 사용할 수 없습니다.'
        }), 503
    
    try:
        # 쿼리 파라미터
        hours = request.args.get('hours', 24, type=int)
        
        snapshots = advanced_plugin_monitor.get_performance_snapshots(plugin_id, hours)
        
        # JSON 직렬화를 위해 데이터 변환
        snapshots_data = []
        for snapshot in snapshots:
            snapshots_data.append({
                'plugin_id': snapshot.plugin_id,
                'timestamp': snapshot.timestamp.isoformat(),
                'cpu_usage': snapshot.cpu_usage,
                'memory_usage': snapshot.memory_usage,
                'response_time': snapshot.response_time,
                'error_rate': snapshot.error_rate,
                'request_count': snapshot.request_count,
                'throughput': snapshot.throughput,
                'disk_io': snapshot.disk_io,
                'network_io': snapshot.network_io,
                'custom_metrics': snapshot.custom_metrics
            })
        
        return jsonify({
            'success': True,
            'data': snapshots_data
        })
    except Exception as e:
        logger.error(f"플러그인 스냅샷 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'스냅샷 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500

@advanced_monitoring_bp.route('/plugins/<plugin_id>/real-time', methods=['GET'])
@login_required
def get_plugin_real_time(plugin_id: str):
    """플러그인 실시간 통계 조회"""
    if not advanced_plugin_monitor:
        return jsonify({
            'success': False,
            'message': '고도화된 모니터링 시스템이 사용할 수 없습니다.'
        }), 503
    
    try:
        stats = advanced_plugin_monitor.get_real_time_stats(plugin_id)
        
        if not stats:
            return jsonify({
                'success': False,
                'message': '플러그인을 찾을 수 없습니다.'
            }), 404
        
        # JSON 직렬화를 위해 datetime 객체 변환
        if stats.get('last_update'):
            stats['last_update'] = stats['last_update'].isoformat()
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        logger.error(f"실시간 통계 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'실시간 통계 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500

@advanced_monitoring_bp.route('/plugins/<plugin_id>/metrics', methods=['POST'])
@login_required
def record_plugin_metric(plugin_id: str):
    """플러그인 메트릭 기록"""
    if not advanced_plugin_monitor:
        return jsonify({
            'success': False,
            'message': '고도화된 모니터링 시스템이 사용할 수 없습니다.'
        }), 503
    
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        if 'metric_type' not in data or 'value' not in data:
            return jsonify({
                'success': False,
                'message': '필수 필드가 누락되었습니다: metric_type, value'
            }), 400
        
        # 메트릭 타입 검증
        try:
            metric_type = MetricType(data['metric_type'])
        except ValueError:
            return jsonify({
                'success': False,
                'message': f'유효하지 않은 메트릭 타입입니다: {data["metric_type"]}'
            }), 400
        
        # 메트릭 기록
        advanced_plugin_monitor.record_metric(
            plugin_id=plugin_id,
            metric_type=metric_type,
            value=float(data['value']),
            metadata=data.get('metadata', {})
        )
        
        return jsonify({
            'success': True,
            'message': '메트릭이 기록되었습니다.'
        })
    except Exception as e:
        logger.error(f"메트릭 기록 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'메트릭 기록 중 오류가 발생했습니다: {str(e)}'
        }), 500

@advanced_monitoring_bp.route('/plugins/<plugin_id>/logs', methods=['POST'])
@login_required
def record_plugin_log(plugin_id: str):
    """플러그인 로그 기록"""
    if not advanced_plugin_monitor:
        return jsonify({
            'success': False,
            'message': '고도화된 모니터링 시스템이 사용할 수 없습니다.'
        }), 503
    
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        if 'level' not in data or 'message' not in data:
            return jsonify({
                'success': False,
                'message': '필수 필드가 누락되었습니다: level, message'
            }), 400
        
        # 로그 레벨 검증
        try:
            level = LogLevel(data['level'])
        except ValueError:
            return jsonify({
                'success': False,
                'message': f'유효하지 않은 로그 레벨입니다: {data["level"]}'
            }), 400
        
        # 로그 기록
        advanced_plugin_monitor.record_log(
            plugin_id=plugin_id,
            level=level,
            message=data['message'],
            context=data.get('context', {}),
            traceback=data.get('traceback')
        )
        
        return jsonify({
            'success': True,
            'message': '로그가 기록되었습니다.'
        })
    except Exception as e:
        logger.error(f"로그 기록 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'로그 기록 중 오류가 발생했습니다: {str(e)}'
        }), 500

@advanced_monitoring_bp.route('/plugins/<plugin_id>/events', methods=['POST'])
@login_required
def record_plugin_event(plugin_id: str):
    """플러그인 이벤트 기록"""
    if not advanced_plugin_monitor:
        return jsonify({
            'success': False,
            'message': '고도화된 모니터링 시스템이 사용할 수 없습니다.'
        }), 503
    
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['event_type', 'description', 'severity']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'필수 필드가 누락되었습니다: {field}'
                }), 400
        
        # 이벤트 기록
        advanced_plugin_monitor.record_event(
            plugin_id=plugin_id,
            event_type=data['event_type'],
            description=data['description'],
            severity=data['severity'],
            data=data.get('data', {})
        )
        
        return jsonify({
            'success': True,
            'message': '이벤트가 기록되었습니다.'
        })
    except Exception as e:
        logger.error(f"이벤트 기록 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'이벤트 기록 중 오류가 발생했습니다: {str(e)}'
        }), 500

@advanced_monitoring_bp.route('/plugins/<plugin_id>/snapshots', methods=['POST'])
@login_required
def create_plugin_snapshot(plugin_id: str):
    """플러그인 성능 스냅샷 생성"""
    if not advanced_plugin_monitor:
        return jsonify({
            'success': False,
            'message': '고도화된 모니터링 시스템이 사용할 수 없습니다.'
        }), 503
    
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['cpu_usage', 'memory_usage', 'response_time', 'error_rate', 'request_count', 'throughput']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'필수 필드가 누락되었습니다: {field}'
                }), 400
        
        # 스냅샷 데이터 준비
        snapshot_data = {
            'cpu_usage': float(data['cpu_usage']),
            'memory_usage': float(data['memory_usage']),
            'response_time': float(data['response_time']),
            'error_rate': float(data['error_rate']),
            'request_count': int(data['request_count']),
            'throughput': float(data['throughput']),
            'disk_io': data.get('disk_io', {}),
            'network_io': data.get('network_io', {}),
            'custom_metrics': data.get('custom_metrics', {})
        }
        
        # 스냅샷 생성
        advanced_plugin_monitor.create_snapshot(plugin_id, snapshot_data)
        
        return jsonify({
            'success': True,
            'message': '성능 스냅샷이 생성되었습니다.'
        })
    except Exception as e:
        logger.error(f"스냅샷 생성 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'스냅샷 생성 중 오류가 발생했습니다: {str(e)}'
        }), 500

@advanced_monitoring_bp.route('/analytics/trends', methods=['GET'])
@login_required
def get_analytics_trends():
    """분석 트렌드 조회"""
    if not advanced_plugin_monitor:
        return jsonify({
            'success': False,
            'message': '고도화된 모니터링 시스템이 사용할 수 없습니다.'
        }), 503
    
    try:
        # 쿼리 파라미터
        hours = request.args.get('hours', 24, type=int)
        metric_type = request.args.get('metric_type', 'cpu_usage')
        
        # 모든 플러그인의 메트릭 수집
        all_metrics = []
        for plugin_id in advanced_plugin_monitor.real_time_stats.keys():
            try:
                metric_enum = MetricType(metric_type)
                metrics = advanced_plugin_monitor.get_plugin_metrics(plugin_id, metric_enum, hours)
                all_metrics.extend(metrics)
            except ValueError:
                continue
        
        # 시간별 평균 계산
        hourly_averages = {}
        for metric in all_metrics:
            hour_key = metric.timestamp.strftime('%Y-%m-%d %H:00')
            if hour_key not in hourly_averages:
                hourly_averages[hour_key] = {'sum': 0, 'count': 0}
            hourly_averages[hour_key]['sum'] += metric.value
            hourly_averages[hour_key]['count'] += 1
        
        # 평균 계산
        trends = []
        for hour_key, data in sorted(hourly_averages.items()):
            trends.append({
                'timestamp': hour_key,
                'average_value': data['sum'] / data['count'],
                'data_points': data['count']
            })
        
        return jsonify({
            'success': True,
            'data': {
                'metric_type': metric_type,
                'hours': hours,
                'trends': trends
            }
        })
    except Exception as e:
        logger.error(f"분석 트렌드 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'분석 트렌드 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500

@advanced_monitoring_bp.route('/analytics/performance', methods=['GET'])
@login_required
def get_performance_analytics():
    """성능 분석 조회"""
    if not advanced_plugin_monitor:
        return jsonify({
            'success': False,
            'message': '고도화된 모니터링 시스템이 사용할 수 없습니다.'
        }), 503
    
    try:
        # 쿼리 파라미터
        hours = request.args.get('hours', 24, type=int)
        
        # 모든 플러그인의 스냅샷 수집
        all_snapshots = []
        for plugin_id in advanced_plugin_monitor.real_time_stats.keys():
            snapshots = advanced_plugin_monitor.get_performance_snapshots(plugin_id, hours)
            all_snapshots.extend(snapshots)
        
        if not all_snapshots:
            return jsonify({
                'success': True,
                'data': {
                    'total_snapshots': 0,
                    'average_cpu': 0,
                    'average_memory': 0,
                    'average_response_time': 0,
                    'average_error_rate': 0,
                    'total_requests': 0,
                    'average_throughput': 0
                }
            })
        
        # 통계 계산
        total_snapshots = len(all_snapshots)
        total_cpu = sum(s.cpu_usage for s in all_snapshots)
        total_memory = sum(s.memory_usage for s in all_snapshots)
        total_response_time = sum(s.response_time for s in all_snapshots)
        total_error_rate = sum(s.error_rate for s in all_snapshots)
        total_requests = sum(s.request_count for s in all_snapshots)
        total_throughput = sum(s.throughput for s in all_snapshots)
        
        analytics = {
            'total_snapshots': total_snapshots,
            'average_cpu': total_cpu / total_snapshots,
            'average_memory': total_memory / total_snapshots,
            'average_response_time': total_response_time / total_snapshots,
            'average_error_rate': total_error_rate / total_snapshots,
            'total_requests': total_requests,
            'average_throughput': total_throughput / total_snapshots
        }
        
        return jsonify({
            'success': True,
            'data': analytics
        })
    except Exception as e:
        logger.error(f"성능 분석 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'성능 분석 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500 