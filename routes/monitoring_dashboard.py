from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
import logging
from datetime import datetime, timedelta
import time

# 모니터링 모듈 임포트
from monitoring.real_time_monitor import monitor
from monitoring.advanced_analytics import analytics

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint 생성
monitoring_dashboard_bp = Blueprint('monitoring_dashboard', __name__, url_prefix='/admin/monitoring')

@monitoring_dashboard_bp.route('/')
@login_required
def dashboard():
    """모니터링 대시보드 메인 페이지"""
    try:
        return render_template('admin/monitoring_dashboard.html')
    except Exception as e:
        logger.error(f"모니터링 대시보드 로드 실패: {e}")
        flash('대시보드를 로드하는 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin.dashboard'))

@monitoring_dashboard_bp.route('/alerts')
@login_required
def alerts_page():
    """알림 관리 페이지"""
    try:
        # 필터 파라미터
        hours = request.args.get('hours', 24, type=int)
        severity = request.args.get('severity', '')
        resolved = request.args.get('resolved', 'false').lower() == 'true'
        
        # 알림 데이터 조회
        alerts = monitor.get_recent_alerts(hours)
        
        # 필터링
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        if not resolved:
            alerts = [a for a in alerts if not a.resolved]
        
        # 데이터 직렬화
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'alert_id': alert.alert_id,
                'alert_type': alert.alert_type,
                'severity': alert.severity,
                'message': alert.message,
                'timestamp': alert.timestamp,
                'datetime': datetime.fromtimestamp(alert.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                'metrics': alert.metrics,
                'resolved': alert.resolved,
                'resolved_at': alert.resolved_at,
                'resolved_datetime': datetime.fromtimestamp(alert.resolved_at).strftime('%Y-%m-%d %H:%M:%S') if alert.resolved_at else None
            })
        
        return render_template('admin/monitoring_alerts.html', alerts=alerts_data)
    except Exception as e:
        logger.error(f"알림 페이지 로드 실패: {e}")
        flash('알림 페이지를 로드하는 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('monitoring_dashboard.dashboard'))

@monitoring_dashboard_bp.route('/metrics')
@login_required
def metrics_page():
    """메트릭 상세 페이지"""
    try:
        # 필터 파라미터
        hours = request.args.get('hours', 24, type=int)
        metric_type = request.args.get('type', 'all')
        
        # 메트릭 데이터 조회
        metrics = monitor.get_recent_metrics(hours * 60)  # 시간을 분으로 변환
        
        # 메트릭 타입별 필터링
        if metric_type != 'all':
            # 특정 메트릭 타입에 대한 필터링 로직
            pass
        
        # 데이터 직렬화
        metrics_data = []
        for metric in metrics:
            metrics_data.append({
                'timestamp': metric.timestamp,
                'datetime': datetime.fromtimestamp(metric.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
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
        
        return render_template('admin/monitoring_metrics.html', metrics=metrics_data)
    except Exception as e:
        logger.error(f"메트릭 페이지 로드 실패: {e}")
        flash('메트릭 페이지를 로드하는 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('monitoring_dashboard.dashboard'))

@monitoring_dashboard_bp.route('/analytics')
@login_required
def analytics_page():
    """분석 결과 페이지"""
    try:
        # 필터 파라미터
        hours = request.args.get('hours', 168, type=int)  # 기본값: 7일
        
        # 분석 데이터 조회
        report = analytics.generate_performance_report(hours)
        
        if 'error' in report:
            flash(report['error'], 'error')
            return redirect(url_for('monitoring_dashboard.dashboard'))
        
        return render_template('admin/monitoring_analytics.html', report=report)
    except Exception as e:
        logger.error(f"분석 페이지 로드 실패: {e}")
        flash('분석 페이지를 로드하는 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('monitoring_dashboard.dashboard'))

@monitoring_dashboard_bp.route('/reports')
@login_required
def reports_page():
    """보고서 페이지"""
    try:
        # 필터 파라미터
        hours = request.args.get('hours', 24, type=int)
        report_type = request.args.get('type', 'performance')
        
        if report_type == 'performance':
            # 성능 보고서
            report = analytics.generate_performance_report(hours)
            recommendations = analytics.get_recommendations(report)
            
            return render_template('admin/monitoring_reports.html', 
                                report=report, 
                                recommendations=recommendations,
                                report_type=report_type)
        else:
            flash('지원하지 않는 보고서 타입입니다.', 'error')
            return redirect(url_for('monitoring_dashboard.dashboard'))
            
    except Exception as e:
        logger.error(f"보고서 페이지 로드 실패: {e}")
        flash('보고서 페이지를 로드하는 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('monitoring_dashboard.dashboard'))

@monitoring_dashboard_bp.route('/settings')
@login_required
def settings_page():
    """모니터링 설정 페이지"""
    try:
        # 현재 설정 조회
        current_thresholds = monitor.thresholds
        monitoring_status = {
            'active': monitor.running,
            'uptime': time.time() - getattr(monitor, 'start_time', time.time()) if monitor.running else 0
        }
        
        return render_template('admin/monitoring_settings.html', 
                             thresholds=current_thresholds,
                             status=monitoring_status)
    except Exception as e:
        logger.error(f"설정 페이지 로드 실패: {e}")
        flash('설정 페이지를 로드하는 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('monitoring_dashboard.dashboard'))

@monitoring_dashboard_bp.route('/settings/thresholds', methods=['POST'])
@login_required
def update_thresholds():
    """임계값 업데이트"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '데이터가 필요합니다'}), 400
        
        # 임계값 검증
        required_fields = ['cpu_percent', 'memory_percent', 'disk_usage_percent', 'response_time_avg', 'error_rate']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} 필드가 필요합니다'}), 400
            
            value = float(data[field])
            if value < 0 or value > 100:
                return jsonify({'success': False, 'error': f'{field} 값은 0-100 사이여야 합니다'}), 400
        
        # 임계값 업데이트
        monitor.update_thresholds(data)
        
        flash('임계값이 성공적으로 업데이트되었습니다.', 'success')
        return jsonify({'success': True, 'message': '임계값이 업데이트되었습니다'})
        
    except Exception as e:
        logger.error(f"임계값 업데이트 실패: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_dashboard_bp.route('/settings/monitoring', methods=['POST'])
@login_required
def toggle_monitoring():
    """모니터링 시작/중지"""
    try:
        data = request.get_json()
        action = data.get('action')
        
        if action == 'start':
            if not monitor.running:
                monitor.start_monitoring()
                flash('모니터링이 시작되었습니다.', 'success')
                return jsonify({'success': True, 'message': '모니터링이 시작되었습니다'})
            else:
                return jsonify({'success': False, 'message': '모니터링이 이미 실행 중입니다'})
        
        elif action == 'stop':
            if monitor.running:
                monitor.stop_monitoring()
                flash('모니터링이 중지되었습니다.', 'success')
                return jsonify({'success': True, 'message': '모니터링이 중지되었습니다'})
            else:
                return jsonify({'success': False, 'message': '모니터링이 실행 중이 아닙니다'})
        
        else:
            return jsonify({'success': False, 'error': '잘못된 액션입니다'}), 400
            
    except Exception as e:
        logger.error(f"모니터링 토글 실패: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_dashboard_bp.route('/visualizations')
@login_required
def visualizations_page():
    """시각화 페이지"""
    try:
        # 시각화 생성
        hours = request.args.get('hours', 24, type=int)
        result = analytics.create_visualizations(hours)
        
        if 'error' in result:
            flash(result['error'], 'error')
            return redirect(url_for('monitoring_dashboard.dashboard'))
        
        return render_template('admin/monitoring_visualizations.html', 
                             visualizations=result['visualizations_created'],
                             save_path=result['save_path'])
    except Exception as e:
        logger.error(f"시각화 페이지 로드 실패: {e}")
        flash('시각화 페이지를 로드하는 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('monitoring_dashboard.dashboard'))

@monitoring_dashboard_bp.route('/export')
@login_required
def export_data():
    """데이터 내보내기"""
    try:
        # 내보내기 파라미터
        data_type = request.args.get('type', 'metrics')  # metrics, alerts, analytics
        hours = request.args.get('hours', 24, type=int)
        format_type = request.args.get('format', 'json')  # json, csv
        
        if data_type == 'metrics':
            data = monitor.get_recent_metrics(hours * 60)
        elif data_type == 'alerts':
            data = monitor.get_recent_alerts(hours)
        elif data_type == 'analytics':
            data = analytics.generate_performance_report(hours)
        else:
            flash('지원하지 않는 데이터 타입입니다.', 'error')
            return redirect(url_for('monitoring_dashboard.dashboard'))
        
        # 데이터 직렬화
        if format_type == 'json':
            from flask import Response
            import json
            return Response(
                json.dumps(data, default=str, indent=2, ensure_ascii=False),
                mimetype='application/json',
                headers={'Content-Disposition': f'attachment; filename=monitoring_{data_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'}
            )
        elif format_type == 'csv':
            import csv
            from io import StringIO
            
            output = StringIO()
            if data_type == 'metrics':
                fieldnames = ['timestamp', 'datetime', 'cpu_percent', 'memory_percent', 'disk_usage_percent', 
                             'network_sent', 'network_recv', 'active_connections', 'active_users', 
                             'request_count', 'error_count', 'response_time_avg']
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for metric in data:
                    writer.writerow({
                        'timestamp': metric.timestamp,
                        'datetime': datetime.fromtimestamp(metric.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
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
            
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename=monitoring_{data_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
            )
        else:
            flash('지원하지 않는 형식입니다.', 'error')
            return redirect(url_for('monitoring_dashboard.dashboard'))
            
    except Exception as e:
        logger.error(f"데이터 내보내기 실패: {e}")
        flash('데이터 내보내기 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('monitoring_dashboard.dashboard'))

@monitoring_dashboard_bp.route('/health')
@login_required
def health_check():
    """모니터링 시스템 상태 확인"""
    try:
        import psutil
        
        # 시스템 상태
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 모니터링 시스템 상태
        monitoring_status = {
            'active': monitor.running,
            'uptime': time.time() - getattr(monitor, 'start_time', time.time()) if monitor.running else 0,
            'metrics_collected': len(monitor.get_recent_metrics(1)),
            'alerts_count': len(monitor.get_recent_alerts(1))
        }
        
        health_data = {
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_usage_percent': disk.percent,
                'timestamp': time.time()
            },
            'monitoring': monitoring_status,
            'status': 'healthy' if monitoring_status['active'] else 'inactive'
        }
        
        return jsonify({'success': True, 'data': health_data})
        
    except Exception as e:
        logger.error(f"상태 확인 실패: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 에러 핸들러
@monitoring_dashboard_bp.errorhandler(404)
def not_found(error):
    flash('요청한 페이지를 찾을 수 없습니다.', 'error')
    return redirect(url_for('monitoring_dashboard.dashboard'))

@monitoring_dashboard_bp.errorhandler(500)
def internal_error(error):
    flash('내부 서버 오류가 발생했습니다.', 'error')
    return redirect(url_for('monitoring_dashboard.dashboard')) 