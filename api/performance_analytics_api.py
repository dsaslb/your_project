#!/usr/bin/env python3
"""
성능 분석 API 엔드포인트
운영 데이터 기반 성능 분석 및 튜닝을 위한 REST API
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, Optional

# 성능 분석 시스템 import
try:
    from core.backend.performance_analytics import PerformanceAnalytics
except ImportError:
    PerformanceAnalytics = None

logger = logging.getLogger(__name__)

# Blueprint 생성
performance_analytics_bp = Blueprint('performance_analytics', __name__, url_prefix='/api/performance')

# 성능 분석 시스템 인스턴스
performance_analytics = PerformanceAnalytics() if PerformanceAnalytics else None

@performance_analytics_bp.route('/start', methods=['POST'])
def start_analytics():
    """성능 분석 시스템 시작"""
    try:
        if not performance_analytics:
            return jsonify({
                'success': False,
                'error': '성능 분석 시스템을 사용할 수 없습니다'
            }), 500
        
        result = performance_analytics.start_analytics()
        
        return jsonify({
            'success': result['status'] == 'success',
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"성능 분석 시스템 시작 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@performance_analytics_bp.route('/stop', methods=['POST'])
def stop_analytics():
    """성능 분석 시스템 중지"""
    try:
        if not performance_analytics:
            return jsonify({
                'success': False,
                'error': '성능 분석 시스템을 사용할 수 없습니다'
            }), 500
        
        result = performance_analytics.stop_analytics()
        
        return jsonify({
            'success': result['status'] == 'success',
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"성능 분석 시스템 중지 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@performance_analytics_bp.route('/collect', methods=['POST'])
def collect_metric():
    """성능 메트릭 수집"""
    try:
        if not performance_analytics:
            return jsonify({
                'success': False,
                'error': '성능 분석 시스템을 사용할 수 없습니다'
            }), 500
        
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['metric_type', 'value']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'필수 필드가 누락되었습니다: {field}'
                }), 400
        
        # 메트릭 수집
        performance_analytics.collect_metric(
            metric_type=data['metric_type'],
            value=float(data['value']),
            plugin_id=data.get('plugin_id'),
            component=data.get('component'),
            metadata=data.get('metadata')
        )
        
        return jsonify({
            'success': True,
            'message': '메트릭이 성공적으로 수집되었습니다',
            'timestamp': datetime.now().isoformat()
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'잘못된 값 형식: {e}'
        }), 400
    except Exception as e:
        logger.error(f"메트릭 수집 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@performance_analytics_bp.route('/analyze', methods=['POST'])
def analyze_performance():
    """성능 분석 수행"""
    try:
        if not performance_analytics:
            return jsonify({
                'success': False,
                'error': '성능 분석 시스템을 사용할 수 없습니다'
            }), 500
        
        data = request.get_json() or {}
        period_hours = data.get('period_hours', 24)
        
        # 분석 수행
        analysis = performance_analytics.analyze_performance(period_hours)
        
        return jsonify({
            'success': True,
            'data': {
                'analysis_id': analysis.analysis_id,
                'timestamp': analysis.timestamp.isoformat(),
                'period': analysis.period,
                'health_score': analysis.health_score,
                'metrics_summary': analysis.metrics_summary,
                'bottlenecks': analysis.bottlenecks,
                'recommendations': analysis.recommendations,
                'trends': analysis.trends
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"성능 분석 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@performance_analytics_bp.route('/report', methods=['GET'])
def get_performance_report():
    """성능 리포트 조회"""
    try:
        if not performance_analytics:
            return jsonify({
                'success': False,
                'error': '성능 분석 시스템을 사용할 수 없습니다'
            }), 500
        
        analysis_id = request.args.get('analysis_id')
        
        # 리포트 조회
        report = performance_analytics.get_performance_report(analysis_id)
        
        if 'error' in report:
            return jsonify({
                'success': False,
                'error': report['error'],
                'timestamp': datetime.now().isoformat()
            }), 404
        
        return jsonify({
            'success': True,
            'data': report,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"성능 리포트 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@performance_analytics_bp.route('/suggestions', methods=['GET'])
def get_optimization_suggestions():
    """최적화 제안사항 조회"""
    try:
        if not performance_analytics:
            return jsonify({
                'success': False,
                'error': '성능 분석 시스템을 사용할 수 없습니다'
            }), 500
        
        # 제안사항 조회
        suggestions = performance_analytics.get_optimization_suggestions()
        
        return jsonify({
            'success': True,
            'data': {
                'suggestions': suggestions,
                'total_count': len(suggestions),
                'high_priority': len([s for s in suggestions if s.get('priority') == 'high']),
                'critical_priority': len([s for s in suggestions if s.get('priority') == 'critical'])
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"최적화 제안사항 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@performance_analytics_bp.route('/metrics', methods=['GET'])
def get_metrics_summary():
    """메트릭 요약 조회"""
    try:
        if not performance_analytics:
            return jsonify({
                'success': False,
                'error': '성능 분석 시스템을 사용할 수 없습니다'
            }), 500
        
        # 최신 분석 결과에서 메트릭 요약 조회
        report = performance_analytics.get_performance_report()
        
        if 'error' in report:
            return jsonify({
                'success': False,
                'error': report['error'],
                'timestamp': datetime.now().isoformat()
            }), 404
        
        metrics_summary = report.get('metrics_summary', {})
        
        return jsonify({
            'success': True,
            'data': {
                'metrics_summary': metrics_summary,
                'key_metrics': {
                    'avg_response_time': metrics_summary.get('avg_response_time', 0),
                    'avg_memory_usage': metrics_summary.get('avg_memory_usage', 0),
                    'avg_cpu_usage': metrics_summary.get('avg_cpu_usage', 0),
                    'avg_error_rate': metrics_summary.get('avg_error_rate', 0)
                },
                'health_score': report.get('health_score', 0),
                'overall_status': report.get('summary', {}).get('overall_status', 'unknown')
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"메트릭 요약 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@performance_analytics_bp.route('/bottlenecks', methods=['GET'])
def get_bottlenecks():
    """병목 지점 조회"""
    try:
        if not performance_analytics:
            return jsonify({
                'success': False,
                'error': '성능 분석 시스템을 사용할 수 없습니다'
            }), 500
        
        # 최신 분석 결과에서 병목 지점 조회
        report = performance_analytics.get_performance_report()
        
        if 'error' in report:
            return jsonify({
                'success': False,
                'error': report['error'],
                'timestamp': datetime.now().isoformat()
            }), 404
        
        bottlenecks = report.get('bottlenecks', [])
        
        return jsonify({
            'success': True,
            'data': {
                'bottlenecks': bottlenecks,
                'total_count': len(bottlenecks),
                'critical_count': len([b for b in bottlenecks if b.get('severity') == 'critical']),
                'warning_count': len([b for b in bottlenecks if b.get('severity') == 'warning'])
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"병목 지점 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@performance_analytics_bp.route('/trends', methods=['GET'])
def get_trends():
    """트렌드 분석 조회"""
    try:
        if not performance_analytics:
            return jsonify({
                'success': False,
                'error': '성능 분석 시스템을 사용할 수 없습니다'
            }), 500
        
        # 최신 분석 결과에서 트렌드 조회
        report = performance_analytics.get_performance_report()
        
        if 'error' in report:
            return jsonify({
                'success': False,
                'error': report['error'],
                'timestamp': datetime.now().isoformat()
            }), 404
        
        trends = report.get('trends', {})
        
        return jsonify({
            'success': True,
            'data': {
                'trends': trends,
                'trend_summary': {
                    'increasing_metrics': [k for k, v in trends.items() if v.get('trend') == 'increasing'],
                    'decreasing_metrics': [k for k, v in trends.items() if v.get('trend') == 'decreasing'],
                    'stable_metrics': [k for k, v in trends.items() if v.get('trend') == 'stable']
                }
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"트렌드 분석 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@performance_analytics_bp.route('/status', methods=['GET'])
def get_analytics_status():
    """성능 분석 시스템 상태 조회"""
    try:
        if not performance_analytics:
            return jsonify({
                'success': False,
                'error': '성능 분석 시스템을 사용할 수 없습니다'
            }), 500
        
        # 시스템 상태 정보
        status = {
            'running': performance_analytics.running,
            'analysis_count': len(performance_analytics.analysis_results),
            'metrics_storage': {
                'response_times': len(performance_analytics.metrics_storage['response_times']),
                'memory_usage': len(performance_analytics.metrics_storage['memory_usage']),
                'cpu_usage': len(performance_analytics.metrics_storage['cpu_usage']),
                'error_rates': len(performance_analytics.metrics_storage['error_rates']),
                'plugin_metrics': len(performance_analytics.metrics_storage['plugin_metrics'])
            },
            'config': performance_analytics.analysis_config,
            'thresholds': performance_analytics.thresholds
        }
        
        return jsonify({
            'success': True,
            'data': status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"성능 분석 시스템 상태 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500 