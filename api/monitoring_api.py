from flask import Blueprint, jsonify, request, current_app
from flask_cors import CORS
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

# 모니터링 모듈 임포트
from monitoring.real_time_monitor import monitor, SystemMetrics, UserActivity, PerformanceAlert
from monitoring.advanced_analytics import analytics, TrendAnalysis, AnomalyDetection, UserBehaviorAnalysis, PerformancePrediction

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint 생성
monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/api/monitoring')
CORS(monitoring_bp)

@monitoring_bp.route('/status', methods=['GET'])
def get_monitoring_status():
    """모니터링 시스템 상태 조회"""
    try:
        status = {
            'monitoring_active': monitor.running,
            'current_time': time.time(),
            'uptime': time.time() - monitor.start_time if hasattr(monitor, 'start_time') else 0,
            'metrics_collected': len(monitor.get_recent_metrics(1)),  # 최근 1분
            'alerts_count': len(monitor.get_recent_alerts(1)),  # 최근 1시간
            'thresholds': monitor.thresholds
        }
        return jsonify({'success': True, 'data': status})
    except Exception as e:
        logger.error(f"모니터링 상태 조회 실패: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_bp.route('/start', methods=['POST'])
def start_monitoring():
    """모니터링 시작"""
    try:
        if not monitor.running:
            monitor.start_monitoring()
            return jsonify({'success': True, 'message': '모니터링이 시작되었습니다'})
        else:
            return jsonify({'success': False, 'message': '모니터링이 이미 실행 중입니다'})
    except Exception as e:
        logger.error(f"모니터링 시작 실패: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_bp.route('/stop', methods=['POST'])
def stop_monitoring():
    """모니터링 중지"""
    try:
        if monitor.running:
            monitor.stop_monitoring()
            return jsonify({'success': True, 'message': '모니터링이 중지되었습니다'})
        else:
            return jsonify({'success': False, 'message': '모니터링이 실행 중이 아닙니다'})
    except Exception as e:
        logger.error(f"모니터링 중지 실패: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """시스템 메트릭 조회"""
    try:
        minutes = request.args.get('minutes', 60, type=int)
        metrics = monitor.get_recent_metrics(minutes)
        
        # 데이터 직렬화
        metrics_data = []
        for metric in metrics:
            metrics_data.append({
                'timestamp': metric.timestamp,
                'datetime': datetime.fromtimestamp(metric.timestamp).isoformat(),
                'cpu_percent': metric.cpu_percent,
                'memory_percent': metric.memory_percent,
                'disk_usage_percent': metric.disk_usage_percent,
                'network_sent': metric.network_sent,
                'network_recv': metric.network_recv,
                'active_connections': metric.active_connections,
                'active_users': metric.active_users,
                'request_count': metric.request_count,
                'error_count': metric.error_count,
                'response_time_avg': metric.response_time_avg
            })
        
        return jsonify({
            'success': True, 
            'data': metrics_data,
            'count': len(metrics_data)
        })
    except Exception as e:
        logger.error(f"메트릭 조회 실패: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_bp.route('/metrics/current', methods=['GET'])
def get_current_metrics():
    """현재 시스템 메트릭 조회"""
    try:
        import psutil
        
        # 현재 시스템 상태
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network_stats = psutil.net_io_counters()
        connections = len(psutil.net_connections())
        
        current_metrics = {
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available': memory.available,
            'memory_total': memory.total,
            'disk_usage_percent': disk.percent,
            'disk_free': disk.free,
            'disk_total': disk.total,
            'network_sent': network_stats.bytes_sent,
            'network_recv': network_stats.bytes_recv,
            'active_connections': connections,
            'active_users': len(monitor.stats['active_users']),
            'active_sessions': len(monitor.stats['active_sessions']),
            'request_count': monitor.stats['request_count'],
            'error_count': monitor.stats['error_count'],
            'response_time_avg': sum(monitor.stats['response_times']) / len(monitor.stats['response_times']) if monitor.stats['response_times'] else 0
        }
        
        return jsonify({'success': True, 'data': current_metrics})
    except Exception as e:
        logger.error(f"현재 메트릭 조회 실패: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """성능 알림 조회"""
    try:
        hours = request.args.get('hours', 24, type=int)
        resolved = request.args.get('resolved', 'false').lower() == 'true'
        
        alerts = monitor.get_recent_alerts(hours)
        
        # 해결 상태 필터링
        if not resolved:
            alerts = [alert for alert in alerts if not alert.resolved]
        
        # 데이터 직렬화
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'alert_id': alert.alert_id,
                'alert_type': alert.alert_type,
                'severity': alert.severity,
                'message': alert.message,
                'timestamp': alert.timestamp,
                'datetime': datetime.fromtimestamp(alert.timestamp).isoformat(),
                'metrics': alert.metrics,
                'resolved': alert.resolved,
                'resolved_at': alert.resolved_at,
                'resolved_datetime': datetime.fromtimestamp(alert.resolved_at).isoformat() if alert.resolved_at else None
            })
        
        return jsonify({
            'success': True,
            'data': alerts_data,
            'count': len(alerts_data)
        })
    except Exception as e:
        logger.error(f"알림 조회 실패: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_bp.route('/alerts/<alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    """알림 해결"""
    try:
        monitor.resolve_alert(alert_id)
        return jsonify({'success': True, 'message': '알림이 해결되었습니다'})
    except Exception as e:
        logger.error(f"알림 해결 실패: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_bp.route('/thresholds', methods=['GET', 'PUT'])
def manage_thresholds():
    """임계값 관리"""
    try:
        if request.method == 'GET':
            return jsonify({
                'success': True,
                'data': monitor.thresholds
            })
        else:  # PUT
            new_thresholds = request.get_json()
            if not new_thresholds:
                return jsonify({'success': False, 'error': '임계값 데이터가 필요합니다'}), 400
            
            monitor.update_thresholds(new_thresholds)
            return jsonify({'success': True, 'message': '임계값이 업데이트되었습니다'})
    except Exception as e:
        logger.error(f"임계값 관리 실패: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_bp.route('/activity', methods=['GET', 'POST'])
def manage_user_activity():
    """사용자 활동 관리"""
    try:
        if request.method == 'GET':
            hours = request.args.get('hours', 24, type=int)
            user_id = request.args.get('user_id')
            
            # 사용자 활동 요약 조회
            summary = monitor.get_user_activity_summary(hours)
            
            if user_id:
                # 특정 사용자 활동을 조회하는 로직 필요
                pass
            
            return jsonify({
                'success': True,
                'data': summary
            })
        else:  # POST
            # 사용자 활동 기록
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': '활동 데이터가 필요합니다'}), 400
            
            activity = UserActivity(
                user_id=data.get('user_id'),
                session_id=data.get('session_id'),
                action=data.get('action'),
                page=data.get('page'),
                timestamp=data.get('timestamp', time.time()),
                duration=data.get('duration', 0.0),
                ip_address=data.get('ip_address'),
                user_agent=data.get('user_agent'),
                success=data.get('success', True),
                error_message=data.get('error_message')
            )
            
            monitor.record_user_activity(activity)
            return jsonify({'success': True, 'message': '사용자 활동이 기록되었습니다'})
    except Exception as e:
        logger.error(f"사용자 활동 관리 실패: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_bp.route('/analytics/trends', methods=['GET'])
def get_trend_analysis():
    """트렌드 분석 결과 조회"""
    try:
        hours = request.args.get('hours', 168, type=int)  # 기본값: 7일
        
        # 데이터 로드
        df = analytics.load_metrics_data(hours)
        if df.empty:
            return jsonify({'success': False, 'error': '분석할 데이터가 없습니다'}), 404
        
        # 트렌드 분석
        trends = analytics.analyze_trends(df)
        
        # 데이터 직렬화
        trends_data = []
        for trend in trends:
            trends_data.append({
                'metric': trend.metric,
                'trend': trend.trend,
                'slope': trend.slope,
                'confidence': trend.confidence,
                'prediction_next_hour': trend.prediction_next_hour,
                'prediction_next_day': trend.prediction_next_day
            })
        
        return jsonify({
            'success': True,
            'data': trends_data,
            'analysis_period_hours': hours
        })
    except Exception as e:
        logger.error(f"트렌드 분석 실패: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_bp.route('/analytics/anomalies', methods=['GET'])
def get_anomaly_detection():
    """이상 탐지 결과 조회"""
    try:
        hours = request.args.get('hours', 168, type=int)
        severity = request.args.get('severity')  # 'low', 'medium', 'high'
        
        # 데이터 로드
        df = analytics.load_metrics_data(hours)
        if df.empty:
            return jsonify({'success': False, 'error': '분석할 데이터가 없습니다'}), 404
        
        # 이상 탐지
        anomalies = analytics.detect_anomalies(df)
        
        # 심각도 필터링
        if severity:
            anomalies = [a for a in anomalies if a.severity == severity]
        
        # 데이터 직렬화
        anomalies_data = []
        for anomaly in anomalies:
            anomalies_data.append({
                'metric': anomaly.metric,
                'timestamp': anomaly.timestamp,
                'datetime': datetime.fromtimestamp(anomaly.timestamp).isoformat(),
                'value': anomaly.value,
                'threshold': anomaly.threshold,
                'severity': anomaly.severity,
                'description': anomaly.description
            })
        
        return jsonify({
            'success': True,
            'data': anomalies_data,
            'count': len(anomalies_data)
        })
    except Exception as e:
        logger.error(f"이상 탐지 실패: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_bp.route('/analytics/user-behavior', methods=['GET'])
def get_user_behavior_analysis():
    """사용자 행동 분석 결과 조회"""
    try:
        hours = request.args.get('hours', 168, type=int)
        user_id = request.args.get('user_id')
        
        # 데이터 로드
        df = analytics.load_user_activity_data(hours)
        if df.empty:
            return jsonify({'success': False, 'error': '분석할 데이터가 없습니다'}), 404
        
        # 사용자 행동 분석
        behaviors = analytics.analyze_user_behavior(df)
        
        # 특정 사용자 필터링
        if user_id:
            behaviors = [b for b in behaviors if b.user_id == user_id]
        
        # 데이터 직렬화
        behaviors_data = []
        for behavior in behaviors:
            behaviors_data.append({
                'user_id': behavior.user_id,
                'session_count': behavior.session_count,
                'avg_session_duration': behavior.avg_session_duration,
                'favorite_pages': behavior.favorite_pages,
                'peak_activity_hours': behavior.peak_activity_hours,
                'error_rate': behavior.error_rate,
                'engagement_score': behavior.engagement_score
            })
        
        return jsonify({
            'success': True,
            'data': behaviors_data,
            'count': len(behaviors_data)
        })
    except Exception as e:
        logger.error(f"사용자 행동 분석 실패: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_bp.route('/analytics/predictions', methods=['GET'])
def get_performance_predictions():
    """성능 예측 결과 조회"""
    try:
        hours = request.args.get('hours', 168, type=int)
        metric = request.args.get('metric', 'cpu_percent')
        hours_ahead = request.args.get('hours_ahead', 24, type=int)
        
        # 데이터 로드
        df = analytics.load_metrics_data(hours)
        if df.empty:
            return jsonify({'success': False, 'error': '분석할 데이터가 없습니다'}), 404
        
        # 성능 예측
        prediction = analytics.predict_performance(df, metric, hours_ahead)
        
        if not prediction:
            return jsonify({'success': False, 'error': '예측을 수행할 수 없습니다'}), 400
        
        # 데이터 직렬화
        prediction_data = {
            'metric': prediction.metric,
            'prediction_time': prediction.prediction_time,
            'prediction_datetime': datetime.fromtimestamp(prediction.prediction_time).isoformat(),
            'predicted_value': prediction.predicted_value,
            'confidence_interval': prediction.confidence_interval,
            'factors': prediction.factors
        }
        
        return jsonify({
            'success': True,
            'data': prediction_data
        })
    except Exception as e:
        logger.error(f"성능 예측 실패: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_bp.route('/reports/performance', methods=['GET'])
def get_performance_report():
    """성능 보고서 생성"""
    try:
        hours = request.args.get('hours', 24, type=int)
        
        # 성능 보고서 생성
        report = analytics.generate_performance_report(hours)
        
        if 'error' in report:
            return jsonify({'success': False, 'error': report['error']}), 404
        
        return jsonify({
            'success': True,
            'data': report
        })
    except Exception as e:
        logger.error(f"성능 보고서 생성 실패: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_bp.route('/reports/visualizations', methods=['POST'])
def create_visualizations():
    """시각화 생성"""
    try:
        data = request.get_json() or {}
        hours = data.get('hours', 24)
        save_path = data.get('save_path', 'static/reports/')
        
        # 시각화 생성
        result = analytics.create_visualizations(hours, save_path)
        
        if 'error' in result:
            return jsonify({'success': False, 'error': result['error']}), 404
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        logger.error(f"시각화 생성 실패: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_bp.route('/reports/recommendations', methods=['GET'])
def get_recommendations():
    """성능 최적화 권장사항 조회"""
    try:
        hours = request.args.get('hours', 24, type=int)
        
        # 성능 보고서 생성
        report = analytics.generate_performance_report(hours)
        
        if 'error' in report:
            return jsonify({'success': False, 'error': report['error']}), 404
        
        # 권장사항 생성
        recommendations = analytics.get_recommendations(report)
        
        return jsonify({
            'success': True,
            'data': {
                'recommendations': recommendations,
                'count': len(recommendations)
            }
        })
    except Exception as e:
        logger.error(f"권장사항 생성 실패: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_bp.route('/dashboard/summary', methods=['GET'])
def get_dashboard_summary():
    """대시보드 요약 정보 조회"""
    try:
        # 현재 메트릭
        current_metrics = monitor.get_recent_metrics(1)
        current_metric = current_metrics[-1] if current_metrics else None
        
        # 최근 알림
        recent_alerts = monitor.get_recent_alerts(1)
        unresolved_alerts = [a for a in recent_alerts if not a.resolved]
        
        # 사용자 활동 요약
        activity_summary = monitor.get_user_activity_summary(1)
        
        # 트렌드 분석 (최근 24시간)
        df = analytics.load_metrics_data(24)
        trends = analytics.analyze_trends(df) if not df.empty else []
        
        summary = {
            'current_metrics': {
                'cpu_percent': current_metric.cpu_percent if current_metric else 0,
                'memory_percent': current_metric.memory_percent if current_metric else 0,
                'active_users': current_metric.active_users if current_metric else 0,
                'response_time_avg': current_metric.response_time_avg if current_metric else 0
            },
            'alerts': {
                'total_recent': len(recent_alerts),
                'unresolved': len(unresolved_alerts),
                'critical': len([a for a in unresolved_alerts if a.severity == 'critical'])
            },
            'user_activity': activity_summary,
            'trends': [{'metric': t.metric, 'trend': t.trend} for t in trends[:5]]
        }
        
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        logger.error(f"대시보드 요약 조회 실패: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 에러 핸들러
@monitoring_bp.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': '리소스를 찾을 수 없습니다'}), 404

@monitoring_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': '내부 서버 오류가 발생했습니다'}), 500 