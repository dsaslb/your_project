from flask import Blueprint, jsonify, request
from monitoring.monitoring_manager import MonitoringManager, MonitoringConfig
from .utils import APIResponse, api_error_handler, log_api_request, validate_json_input
import os
import logging

# 로거 설정
logger = logging.getLogger(__name__)

# 모니터링 Blueprint 생성
monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/api/monitoring')

# 모니터링 관리자 초기화
config = MonitoringConfig(
    data_dir="./monitoring/data",
    collection_interval=60,
    retention_days=30,
    alert_enabled=True,
    email_enabled=False,
    webhook_enabled=False
)

monitoring_manager = MonitoringManager(config)

@monitoring_bp.route('/health', methods=['GET'])
@api_error_handler
@log_api_request
def health_check():
    """모니터링 시스템 상태 확인"""
    return APIResponse.success(
        data={
            'is_running': monitoring_manager.is_running,
            'message': '모니터링 시스템이 정상적으로 작동 중입니다'
        },
        message='모니터링 시스템 상태 확인 완료'
    )

@monitoring_bp.route('/stats/system', methods=['GET'])
@api_error_handler
@log_api_request
def get_system_stats():
    """시스템 통계 조회"""
    stats = monitoring_manager.get_system_stats()
    return APIResponse.success(data=stats, message='시스템 통계 조회 완료')

@monitoring_bp.route('/stats/application', methods=['GET'])
def get_application_stats():
    """애플리케이션 통계 조회"""
    try:
        stats = monitoring_manager.get_application_stats()
        return jsonify({
            'status': 'success',
            'data': stats
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'애플리케이션 통계 조회 오류: {str(e)}'
        }), 500

@monitoring_bp.route('/metrics/history', methods=['GET'])
def get_metric_history():
    """메트릭 히스토리 조회"""
    try:
        metric_name = request.args.get('metric', 'cpu_percent')
        hours = int(request.args.get('hours', 24))
        
        history = monitoring_manager.get_metric_history(metric_name, hours)
        return jsonify({
            'status': 'success',
            'data': {
                'metric_name': metric_name,
                'hours': hours,
                'history': history
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'메트릭 히스토리 조회 오류: {str(e)}'
        }), 500

@monitoring_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """알림 목록 조회"""
    try:
        status = request.args.get('status')
        limit = int(request.args.get('limit', 100))
        
        alerts = monitoring_manager.get_alerts(status, limit)
        
        # Alert 객체를 딕셔너리로 변환
        alert_list = []
        for alert in alerts:
            alert_dict = {
                'alert_id': alert.alert_id,
                'rule_id': alert.rule_id,
                'metric_type': alert.metric_type,
                'metric_name': alert.metric_name,
                'current_value': alert.current_value,
                'threshold': alert.threshold,
                'severity': alert.severity,
                'message': alert.message,
                'timestamp': alert.timestamp.isoformat(),
                'status': alert.status,
                'acknowledged_by': alert.acknowledged_by,
                'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None
            }
            alert_list.append(alert_dict)
        
        return jsonify({
            'status': 'success',
            'data': alert_list
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'알림 조회 오류: {str(e)}'
        }), 500

@monitoring_bp.route('/alerts/<alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """알림 승인"""
    try:
        data = request.get_json()
        user = data.get('user', 'admin')
        
        monitoring_manager.acknowledge_alert(alert_id, user)
        
        return jsonify({
            'status': 'success',
            'message': f'알림 {alert_id}가 승인되었습니다'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'알림 승인 오류: {str(e)}'
        }), 500

@monitoring_bp.route('/rules', methods=['GET'])
def get_alert_rules():
    """알림 규칙 목록 조회"""
    try:
        rules = []
        for rule in monitoring_manager.alert_rules.values():
            rule_dict = {
                'rule_id': rule.rule_id,
                'name': rule.name,
                'metric_type': rule.metric_type,
                'metric_name': rule.metric_name,
                'operator': rule.operator,
                'threshold': rule.threshold,
                'duration': rule.duration,
                'severity': rule.severity,
                'enabled': rule.enabled,
                'created_at': rule.created_at.isoformat() if rule.created_at else None
            }
            rules.append(rule_dict)
        
        return jsonify({
            'status': 'success',
            'data': rules
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'알림 규칙 조회 오류: {str(e)}'
        }), 500

@monitoring_bp.route('/rules', methods=['POST'])
def create_alert_rule():
    """알림 규칙 생성"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'metric_type', 'metric_name', 'operator', 'threshold', 'duration', 'severity']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'필수 필드가 누락되었습니다: {field}'
                }), 400
        
        rule_id = monitoring_manager.create_alert_rule(
            name=data['name'],
            metric_type=data['metric_type'],
            metric_name=data['metric_name'],
            operator=data['operator'],
            threshold=float(data['threshold']),
            duration=int(data['duration']),
            severity=data['severity']
        )
        
        return jsonify({
            'status': 'success',
            'message': '알림 규칙이 생성되었습니다',
            'data': {'rule_id': rule_id}
        }), 201
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'알림 규칙 생성 오류: {str(e)}'
        }), 500

@monitoring_bp.route('/rules/<rule_id>', methods=['PUT'])
def update_alert_rule(rule_id):
    """알림 규칙 수정"""
    try:
        data = request.get_json()
        
        if rule_id not in monitoring_manager.alert_rules:
            return jsonify({
                'status': 'error',
                'message': '알림 규칙을 찾을 수 없습니다'
            }), 404
        
        rule = monitoring_manager.alert_rules[rule_id]
        
        # 업데이트 가능한 필드들
        if 'name' in data:
            rule.name = data['name']
        if 'threshold' in data:
            rule.threshold = float(data['threshold'])
        if 'duration' in data:
            rule.duration = int(data['duration'])
        if 'severity' in data:
            rule.severity = data['severity']
        if 'enabled' in data:
            rule.enabled = bool(data['enabled'])
        
        # 데이터베이스에 저장
        monitoring_manager._save_alert_rule(rule)
        
        return jsonify({
            'status': 'success',
            'message': '알림 규칙이 수정되었습니다'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'알림 규칙 수정 오류: {str(e)}'
        }), 500

@monitoring_bp.route('/rules/<rule_id>', methods=['DELETE'])
def delete_alert_rule(rule_id):
    """알림 규칙 삭제"""
    try:
        if rule_id not in monitoring_manager.alert_rules:
            return jsonify({
                'status': 'error',
                'message': '알림 규칙을 찾을 수 없습니다'
            }), 404
        
        # 데이터베이스에서 삭제
        db_path = os.path.join(monitoring_manager.config.data_dir, 'monitoring.db')
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM alert_rules WHERE rule_id = ?', (rule_id,))
        cursor.execute('DELETE FROM alerts WHERE rule_id = ?', (rule_id,))
        
        conn.commit()
        conn.close()
        
        # 메모리에서 삭제
        del monitoring_manager.alert_rules[rule_id]
        
        return jsonify({
            'status': 'success',
            'message': '알림 규칙이 삭제되었습니다'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'알림 규칙 삭제 오류: {str(e)}'
        }), 500

@monitoring_bp.route('/control/start', methods=['POST'])
def start_monitoring():
    """모니터링 시작"""
    try:
        monitoring_manager.start_monitoring()
        
        return jsonify({
            'status': 'success',
            'message': '모니터링이 시작되었습니다'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'모니터링 시작 오류: {str(e)}'
        }), 500

@monitoring_bp.route('/control/stop', methods=['POST'])
def stop_monitoring():
    """모니터링 중지"""
    try:
        monitoring_manager.stop_monitoring()
        
        return jsonify({
            'status': 'success',
            'message': '모니터링이 중지되었습니다'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'모니터링 중지 오류: {str(e)}'
        }), 500

@monitoring_bp.route('/control/status', methods=['GET'])
def get_monitoring_status():
    """모니터링 상태 조회"""
    try:
        return jsonify({
            'status': 'success',
            'data': {
                'is_running': monitoring_manager.is_running,
                'collection_interval': monitoring_manager.config.collection_interval,
                'retention_days': monitoring_manager.config.retention_days,
                'alert_enabled': monitoring_manager.config.alert_enabled,
                'email_enabled': monitoring_manager.config.email_enabled,
                'webhook_enabled': monitoring_manager.config.webhook_enabled
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'모니터링 상태 조회 오류: {str(e)}'
        }), 500

@monitoring_bp.route('/metrics/collect', methods=['POST'])
def collect_metrics():
    """수동 메트릭 수집"""
    try:
        data = request.get_json()
        metric_type = data.get('type', 'all')  # system, application, all
        
        if metric_type in ['system', 'all']:
            system_metrics = monitoring_manager.collect_system_metrics()
        
        if metric_type in ['application', 'all']:
            endpoint = data.get('endpoint', '/api/health')
            app_metrics = monitoring_manager.collect_application_metrics(endpoint)
        
        return jsonify({
            'status': 'success',
            'message': '메트릭 수집이 완료되었습니다'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'메트릭 수집 오류: {str(e)}'
        }), 500

@monitoring_bp.route('/cleanup', methods=['POST'])
def cleanup_old_data():
    """오래된 데이터 정리"""
    try:
        monitoring_manager._cleanup_old_data()
        
        return jsonify({
            'status': 'success',
            'message': '오래된 데이터 정리가 완료되었습니다'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'데이터 정리 오류: {str(e)}'
        }), 500 