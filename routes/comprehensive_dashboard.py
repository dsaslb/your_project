from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
import logging
from datetime import datetime, timedelta
import time
import json
from typing import Dict, List, Any

# 모니터링 모듈 임포트
from monitoring.real_time_monitor import monitor
from monitoring.advanced_analytics import analytics
from utils.alert_notifier import AlertNotifier
from utils.advanced_caching import AdvancedCache

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint 생성
comprehensive_dashboard_bp = Blueprint('comprehensive_dashboard', __name__, url_prefix='/admin/comprehensive')

# 캐시 인스턴스 생성
cache = AdvancedCache()

@comprehensive_dashboard_bp.route('/')
@login_required
def dashboard():
    """합 대시보드 메인 페이지 - 모든 모니터링 데이터 통합 뷰"""
    try:
        # 사용자 권한 확인
        if not current_user.has_role('admin') and not current_user.has_role('monitor'):
            flash('접근 권한이 없습니다.', 'error')
            return redirect(url_for('admin.dashboard'))
        
        return render_template('admin/comprehensive_dashboard.html')
    except Exception as e:
        logger.error(f"합 대시보드 로드 실패: {e}")
        flash('대시보드를 로드하는 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin.dashboard'))

@comprehensive_dashboard_bp.route('/api/overview')
@login_required
def get_overview_data():
    """전체 시스템 개요 데이터 API"""
    try:
        # 캐시된 데이터 확인
        cache_key = f"comprehensive_overview_{int(time.time() / 300)}"  # 5분 캐시
        cached_data = cache.get(cache_key)
        if cached_data:
            return jsonify(cached_data)
        
        # 실시간 메트릭 수집
        current_metrics = monitor.get_current_metrics()
        
        # 알림 상태 확인
        recent_alerts = monitor.get_recent_alerts(24)  # 최근 24시간
        critical_alerts = [a for a in recent_alerts if a.severity == 'critical' and not a.resolved]
        warning_alerts = [a for a in recent_alerts if a.severity == 'warning' and not a.resolved]
        
        # 시스템 상태 계산
        system_health = calculate_system_health(current_metrics, recent_alerts)
        
        # 성능 지표 계산
        performance_metrics = calculate_performance_metrics(current_metrics)
        
        # 사용자 활동 분석
        user_activity = analytics.get_user_activity_summary()
        
        # 데이터베이스 상태
        db_status = monitor.get_database_status()
        
        # 네트워크 상태
        network_status = monitor.get_network_status()
        
        overview_data = {
            'timestamp': datetime.now().isoformat(),
            'system_health': system_health,
            'current_metrics': {
                'cpu_percent': current_metrics.cpu_percent,
                'memory_percent': current_metrics.memory_percent,
                'disk_usage_percent': current_metrics.disk_usage_percent,
                'active_connections': current_metrics.active_connections,
                'active_users': current_metrics.active_users,
                'response_time': current_metrics.response_time
            },
            'alerts': {
                'critical_count': len(critical_alerts),
                'warning_count': len(warning_alerts),
                'total_count': len(recent_alerts),
                'recent_alerts': [
                    {
                        'id': alert.alert_id,
                        'type': alert.alert_type,
                        'severity': alert.severity,
                        'message': alert.message,
                        'timestamp': alert.timestamp,
                        'resolved': alert.resolved
                    } for alert in recent_alerts[:10]  # 최근 10개만
                ]
            },
            'performance': performance_metrics,
            'user_activity': user_activity,
            'database': db_status,
            'network': network_status
        }
        
        # 캐시에 저장
        cache.set(cache_key, overview_data, 300)  # 5분 캐시
        
        return jsonify(overview_data)
    except Exception as e:
        logger.error(f"개요 데이터 조회 실패: {e}")
        return jsonify({'error': '데이터를 조회하는 중 오류가 발생했습니다.'}), 500

@comprehensive_dashboard_bp.route('/api/trends')
@login_required
def get_trends_data():
    """트렌드 분석 데이터 API"""
    try:
        hours = request.args.get('hours', 24, type=int)
        
        # 시간별 메트릭 데이터
        hourly_metrics = monitor.get_metrics_by_hour(hours)
        
        # 사용자 활동 트렌드
        user_trends = analytics.get_user_activity_trends(hours)
        
        # 알림 트렌드
        alert_trends = analytics.get_alert_trends(hours)
        
        # 성능 트렌드
        performance_trends = analytics.get_performance_trends(hours)
        
        trends_data = {
            'hourly_metrics': hourly_metrics,
            'user_trends': user_trends,
            'alert_trends': alert_trends,
            'performance_trends': performance_trends
        }
        
        return jsonify(trends_data)
    except Exception as e:
        logger.error(f"트렌드 데이터 조회 실패: {e}")
        return jsonify({'error': '트렌드 데이터를 조회하는 중 오류가 발생했습니다.'}), 500

@comprehensive_dashboard_bp.route('/api/real-time')
@login_required
def get_real_time_data():
    """실시간 데이터 스트림 API"""
    try:
        # 실시간 메트릭
        real_time_metrics = monitor.get_real_time_metrics()
        
        # 실시간 알림
        real_time_alerts = monitor.get_real_time_alerts()
        
        # 실시간 사용자 활동
        real_time_users = analytics.get_real_time_user_activity()
        
        real_time_data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': real_time_metrics,
            'alerts': real_time_alerts,
            'users': real_time_users
        }
        
        return jsonify(real_time_data)
    except Exception as e:
        logger.error(f"실시간 데이터 조회 실패: {e}")
        return jsonify({'error': '실시간 데이터를 조회하는 중 오류가 발생했습니다.'}), 500

@comprehensive_dashboard_bp.route('/api/analytics')
@login_required
def get_analytics_data():
    """고급 분석 데이터 API"""
    try:
        days = request.args.get('days', 7, type=int)
        
        # 시스템 사용 패턴 분석
        usage_patterns = analytics.get_usage_patterns(days)
        
        # 성능 병목 분석
        performance_bottlenecks = analytics.get_performance_bottlenecks(days)
        
        # 사용자 행동 분석
        user_behavior = analytics.get_user_behavior_analysis(days)
        
        # 예측 분석
        predictions = analytics.get_system_predictions(days)
        
        analytics_data = {
            'usage_patterns': usage_patterns,
            'performance_bottlenecks': performance_bottlenecks,
            'user_behavior': user_behavior,
            'predictions': predictions
        }
        
        return jsonify(analytics_data)
    except Exception as e:
        logger.error(f"분석 데이터 조회 실패: {e}")
        return jsonify({'error': '분석 데이터를 조회하는 중 오류가 발생했습니다.'}), 500

@comprehensive_dashboard_bp.route('/api/notifications')
@login_required
def get_notifications_data():
    """알림 설정 및 상태 API"""
    try:
        # 알림 설정 조회
        notification_settings = AlertNotifier.get_settings()
        
        # 알림 채널 상태
        channel_status = AlertNotifier.get_channel_status()
        
        # 알림 통계
        notification_stats = AlertNotifier.get_notification_stats()
        
        notifications_data = {
            'settings': notification_settings,
            'channel_status': channel_status,
            'stats': notification_stats
        }
        
        return jsonify(notifications_data)
    except Exception as e:
        logger.error(f"알림 데이터 조회 실패: {e}")
        return jsonify({'error': '알림 데이터를 조회하는 중 오류가 발생했습니다.'}), 500

@comprehensive_dashboard_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """합 대시보드 설정 페이지"""
    try:
        if request.method == 'POST':
            # 설정 업데이트 로직
            settings_data = request.get_json()
            
            # 알림 설정 업데이트
            if 'notifications' in settings_data:
                AlertNotifier.update_settings(settings_data['notifications'])
            
            # 모니터링 설정 업데이트
            if 'monitoring' in settings_data:
                monitor.update_settings(settings_data['monitoring'])
            
            # 캐시 설정 업데이트
            if 'cache' in settings_data:
                cache.update_settings(settings_data['cache'])
            
            flash('설정이 성공적으로 업데이트되었습니다.', 'success')
            return jsonify({'success': True})
        
        # 현재 설정 조회
        current_settings = {
            'notifications': AlertNotifier.get_settings(),
            'monitoring': monitor.get_settings(),
            'cache': cache.get_settings()
        }
        
        return render_template('admin/comprehensive_settings.html', settings=current_settings)
    except Exception as e:
        logger.error(f"설정 페이지 처리 실패: {e}")
        flash('설정을 처리하는 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('comprehensive_dashboard.dashboard'))

@comprehensive_dashboard_bp.route('/export')
@login_required
def export_data():
    """데이터 내보내기"""
    try:
        format_type = request.args.get('format', 'json')
        data_type = request.args.get('type', 'all')
        days = request.args.get('days', 7, type=int)
        
        if format_type == 'json':
            # JSON 형식으로 내보내기
            export_data = generate_export_data(data_type, days)
            return jsonify(export_data)
        elif format_type == 'csv':
            # CSV 형식으로 내보내기
            csv_data = generate_csv_data(data_type, days)
            return csv_data, 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': f'attachment; filename=comprehensive_dashboard_{datetime.now().strftime("%Y%m%d")}.csv'
            }
        else:
            flash('지원하지 않는 형식입니다.', 'error')
            return redirect(url_for('comprehensive_dashboard.dashboard'))
    except Exception as e:
        logger.error(f"데이터 내보내기 실패: {e}")
        flash('데이터를 내보내는 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('comprehensive_dashboard.dashboard'))

def calculate_system_health(metrics, alerts) -> Dict[str, Any]:
    """시스템 건강도 계산"""
    health_score = 100
    
    # CPU 사용률에 따른 점수 감점
    if metrics.cpu_percent > 90:
        health_score -= 30
    elif metrics.cpu_percent > 80:
        health_score -= 20
    elif metrics.cpu_percent > 70:
        health_score -= 10
    
    # 메모리 사용률에 따른 점수 감점
    if metrics.memory_percent > 90:
        health_score -= 30
    elif metrics.memory_percent > 80:
        health_score -= 20
    elif metrics.memory_percent > 70:
        health_score -= 10
    
    # 알림에 따른 점수 감점
    critical_alerts = [a for a in alerts if a.severity == 'critical' and not a.resolved]
    warning_alerts = [a for a in alerts if a.severity == 'warning' and not a.resolved]
    
    health_score -= len(critical_alerts) * 15
    health_score -= len(warning_alerts) * 5
    
    # 최소 점수 보장
    health_score = max(health_score, 0)
    
    # 상태 레벨 결정
    if health_score >= 80:
        status = 'excellent'
    elif health_score >= 60:
        status = 'good'
    elif health_score >= 40:
        status = 'warning'
    else:
        status = 'critical'
    
    return {
        'score': health_score,
        'status': status,
        'factors': {
            'cpu_usage': metrics.cpu_percent,
            'memory_usage': metrics.memory_percent,
            'critical_alerts': len(critical_alerts),
            'warning_alerts': len(warning_alerts)
        }
    }

def calculate_performance_metrics(metrics) -> Dict[str, Any]:
    """성능 지표 계산"""
    return {
        'response_time': {
            'current': metrics.response_time,
            'average': metrics.avg_response_time,
            'trend': 'stable'  # 실제로는 트렌드 계산 로직 필요
        },
        'throughput': {
            'requests_per_second': metrics.request_count / 60 if metrics.request_count else 0,
            'active_connections': metrics.active_connections
        },
        'availability': {
            'uptime_percentage': 99.9,  # 실제로는 업타임 계산 로직 필요
            'last_downtime': None
        }
    }

def generate_export_data(data_type: str, days: int) -> Dict[str, Any]:
    """내보내기용 데이터 생성"""
    if data_type == 'all':
        return {
            'overview': get_overview_data().get_json(),
            'trends': get_trends_data().get_json(),
            'analytics': get_analytics_data().get_json(),
            'exported_at': datetime.now().isoformat()
        }
    else:
        # 특정 데이터 타입만 내보내기
        return {
            'data_type': data_type,
            'data': {},  # 실제 데이터 로직 구현 필요
            'exported_at': datetime.now().isoformat()
        }

def generate_csv_data(data_type: str, days: int) -> str:
    """CSV 형식 데이터 생성"""
    # CSV 헤더
    csv_content = "Timestamp,CPU%,Memory%,Disk%,Active Users,Response Time,Alerts\n"
    
    # 실제 데이터 로직 구현 필요
    # 여기서는 예시 데이터만 반환
    csv_content += f"{datetime.now().isoformat()},50,60,70,100,200,5\n"
    
    return csv_content

@comprehensive_dashboard_bp.errorhandler(404)
def not_found(error):
    """404 에러 핸들러"""
    return render_template('errors/404.html'), 404

@comprehensive_dashboard_bp.errorhandler(500)
def internal_error(error):
    """500 에러 핸들러"""
    logger.error(f"합 대시보드 내부 오류: {error}")
    return render_template('errors/500.html'), 500 