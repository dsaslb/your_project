"""
고도화된 실시간 알림 API
플러그인 모니터링과 연동된 실시간 알림 시스템
"""

from flask import Blueprint, request, jsonify, Response, current_app
from flask_socketio import emit, join_room, leave_room
from functools import wraps
from datetime import datetime, timedelta
import json
import uuid
import logging
from typing import Dict, List, Any

from core.backend.enhanced_realtime_alerts import (
    EnhancedRealtimeAlertSystem, AlertSeverity, AlertType, 
    NotificationChannel, AlertThreshold
)
from api.gateway import token_required, role_required, admin_required
from models import User, db

logger = logging.getLogger(__name__)

# Blueprint 생성
enhanced_alerts_bp = Blueprint('enhanced_alerts', __name__, url_prefix='/api/enhanced-alerts')

# 전역 알림 시스템 인스턴스
alert_system = EnhancedRealtimeAlertSystem()

# WebSocket 연결 관리
connected_clients = {}

def init_enhanced_alerts():
    """고도화된 알림 시스템 초기화"""
    try:
        alert_system.start_monitoring()
        logger.info("고도화된 실시간 알림 시스템 초기화 완료")
    except Exception as e:
        logger.error(f"고도화된 알림 시스템 초기화 실패: {e}")

# 알림 콜백 등록
def alert_callback(alert):
    """알림 발생 시 콜백"""
    try:
        # WebSocket으로 실시간 알림 전송
        alert_data = {
            'type': 'realtime_alert',
            'alert': alert.to_dict(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # 모든 연결된 클라이언트에게 전송
        for client_id, client_info in connected_clients.items():
            try:
                emit('alert', alert_data, room=client_id)
            except Exception as e:
                logger.error(f"클라이언트 {client_id}에게 알림 전송 실패: {e}")
                
    except Exception as e:
        logger.error(f"알림 콜백 실행 실패: {e}")

alert_system.add_alert_callback(alert_callback)

@enhanced_alerts_bp.route('/alerts', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin', 'manager'])
def get_alerts():
    """알림 목록 조회"""
    try:
        # 쿼리 파라미터
        severity = request.args.get('severity')
        alert_type = request.args.get('type')
        plugin_id = request.args.get('plugin_id')
        resolved = request.args.get('resolved', 'false').lower() == 'true'
        limit = int(request.args.get('limit', 50))
        
        # 알림 필터링
        alerts = []
        for alert in alert_system.alerts.values():
            # 해결 상태 필터
            if alert.resolved != resolved:
                continue
                
            # 심각도 필터
            if severity and alert.severity.value != severity:
                continue
                
            # 타입 필터
            if alert_type and alert.type.value != alert_type:
                continue
                
            # 플러그인 ID 필터
            if plugin_id and alert.plugin_id != plugin_id:
                continue
                
            alerts.append(alert.to_dict())
        
        # 시간순 정렬 및 제한
        alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        alerts = alerts[:limit]
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'total_count': len(alerts)
        })
        
    except Exception as e:
        logger.error(f"알림 목록 조회 실패: {e}")
        return jsonify({'error': '알림 목록 조회에 실패했습니다.'}), 500

@enhanced_alerts_bp.route('/alerts/<alert_id>', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin', 'manager'])
def get_alert_detail(alert_id):
    """알림 상세 조회"""
    try:
        if alert_id not in alert_system.alerts:
            return jsonify({'error': '알림을 찾을 수 없습니다.'}), 404
        
        alert = alert_system.alerts[alert_id]
        return jsonify({
            'success': True,
            'alert': alert.to_dict()
        })
        
    except Exception as e:
        logger.error(f"알림 상세 조회 실패: {e}")
        return jsonify({'error': '알림 상세 조회에 실패했습니다.'}), 500

@enhanced_alerts_bp.route('/alerts/<alert_id>/resolve', methods=['POST'])
@token_required
@role_required(['admin', 'super_admin'])
def resolve_alert(alert_id):
    """알림 해결"""
    try:
        if alert_id not in alert_system.alerts:
            return jsonify({'error': '알림을 찾을 수 없습니다.'}), 404
        
        alert_system.resolve_alert(alert_id)
        
        return jsonify({
            'success': True,
            'message': '알림이 해결되었습니다.'
        })
        
    except Exception as e:
        logger.error(f"알림 해결 실패: {e}")
        return jsonify({'error': '알림 해결에 실패했습니다.'}), 500

@enhanced_alerts_bp.route('/alerts/bulk-resolve', methods=['POST'])
@token_required
@role_required(['admin', 'super_admin'])
def bulk_resolve_alerts():
    """다중 알림 해결"""
    try:
        data = request.get_json()
        alert_ids = data.get('alert_ids', [])
        
        if not alert_ids:
            return jsonify({'error': '해결할 알림 ID가 필요합니다.'}), 400
        
        resolved_count = 0
        for alert_id in alert_ids:
            if alert_id in alert_system.alerts:
                alert_system.resolve_alert(alert_id)
                resolved_count += 1
        
        return jsonify({
            'success': True,
            'message': f'{resolved_count}개의 알림이 해결되었습니다.',
            'resolved_count': resolved_count
        })
        
    except Exception as e:
        logger.error(f"다중 알림 해결 실패: {e}")
        return jsonify({'error': '다중 알림 해결에 실패했습니다.'}), 500

@enhanced_alerts_bp.route('/alerts/statistics', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin', 'manager'])
def get_alert_statistics():
    """알림 통계 조회"""
    try:
        stats = alert_system.get_alert_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"알림 통계 조회 실패: {e}")
        return jsonify({'error': '알림 통계 조회에 실패했습니다.'}), 500

@enhanced_alerts_bp.route('/thresholds', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
def get_thresholds():
    """임계값 설정 조회"""
    try:
        thresholds = {
            'plugin_cpu_threshold': alert_system.thresholds.plugin_cpu_threshold,
            'plugin_memory_threshold': alert_system.thresholds.plugin_memory_threshold,
            'plugin_error_rate_threshold': alert_system.thresholds.plugin_error_rate_threshold,
            'plugin_response_time_threshold': alert_system.thresholds.plugin_response_time_threshold,
            'system_cpu_threshold': alert_system.thresholds.system_cpu_threshold,
            'system_memory_threshold': alert_system.thresholds.system_memory_threshold,
            'system_disk_threshold': alert_system.thresholds.system_disk_threshold
        }
        
        return jsonify({
            'success': True,
            'thresholds': thresholds
        })
        
    except Exception as e:
        logger.error(f"임계값 조회 실패: {e}")
        return jsonify({'error': '임계값 조회에 실패했습니다.'}), 500

@enhanced_alerts_bp.route('/thresholds', methods=['PUT'])
@token_required
@role_required(['admin', 'super_admin'])
def update_thresholds():
    """임계값 설정 업데이트"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '임계값 데이터가 필요합니다.'}), 400
        
        # 임계값 업데이트
        for key, value in data.items():
            if hasattr(alert_system.thresholds, key):
                setattr(alert_system.thresholds, key, float(value))
        
        return jsonify({
            'success': True,
            'message': '임계값이 업데이트되었습니다.',
            'thresholds': {
                'plugin_cpu_threshold': alert_system.thresholds.plugin_cpu_threshold,
                'plugin_memory_threshold': alert_system.thresholds.plugin_memory_threshold,
                'plugin_error_rate_threshold': alert_system.thresholds.plugin_error_rate_threshold,
                'plugin_response_time_threshold': alert_system.thresholds.plugin_response_time_threshold,
                'system_cpu_threshold': alert_system.thresholds.system_cpu_threshold,
                'system_memory_threshold': alert_system.thresholds.system_memory_threshold,
                'system_disk_threshold': alert_system.thresholds.system_disk_threshold
            }
        })
        
    except Exception as e:
        logger.error(f"임계값 업데이트 실패: {e}")
        return jsonify({'error': '임계값 업데이트에 실패했습니다.'}), 500

@enhanced_alerts_bp.route('/plugins/<plugin_id>/metrics', methods=['POST'])
@token_required
@role_required(['admin', 'super_admin'])
def update_plugin_metrics(plugin_id):
    """플러그인 메트릭 업데이트"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '메트릭 데이터가 필요합니다.'}), 400
        
        # 메트릭 업데이트
        alert_system.update_plugin_metrics(plugin_id, data)
        
        return jsonify({
            'success': True,
            'message': f'플러그인 {plugin_id} 메트릭이 업데이트되었습니다.'
        })
        
    except Exception as e:
        logger.error(f"플러그인 메트릭 업데이트 실패: {e}")
        return jsonify({'error': '플러그인 메트릭 업데이트에 실패했습니다.'}), 500

@enhanced_alerts_bp.route('/plugins/<plugin_id>/metrics', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin', 'manager'])
def get_plugin_metrics(plugin_id):
    """플러그인 메트릭 조회"""
    try:
        if plugin_id not in alert_system.plugin_metrics:
            return jsonify({'error': '플러그인 메트릭을 찾을 수 없습니다.'}), 404
        
        metrics = alert_system.plugin_metrics[plugin_id]
        
        return jsonify({
            'success': True,
            'plugin_id': plugin_id,
            'metrics': metrics
        })
        
    except Exception as e:
        logger.error(f"플러그인 메트릭 조회 실패: {e}")
        return jsonify({'error': '플러그인 메트릭 조회에 실패했습니다.'}), 500

@enhanced_alerts_bp.route('/plugins/<plugin_id>/history', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin', 'manager'])
def get_plugin_history(plugin_id):
    """플러그인 히스토리 조회"""
    try:
        range_param = request.args.get('range', '1h')
        
        # 시간 범위에 따른 데이터 포인트 수 계산
        range_map = {
            '1h': 60,    # 1분 간격으로 60개
            '6h': 72,    # 5분 간격으로 72개
            '24h': 144,  # 10분 간격으로 144개
            '7d': 168    # 1시간 간격으로 168개
        }
        
        limit = range_map.get(range_param, 60)
        
        # 실제 구현에서는 데이터베이스에서 히스토리 조회
        # 여기서는 더미 데이터 생성
        import random
        from datetime import datetime, timedelta
        
        now = datetime.utcnow()
        history_data = {
            'cpu': [],
            'memory': [],
            'error_rate': [],
            'response_time': []
        }
        
        for i in range(limit):
            timestamp = now - timedelta(minutes=i * (60 // limit))
            
            # CPU 히스토리
            history_data['cpu'].append({
                'timestamp': timestamp.isoformat(),
                'value': random.uniform(20, 90)
            })
            
            # 메모리 히스토리
            history_data['memory'].append({
                'timestamp': timestamp.isoformat(),
                'value': random.uniform(30, 85)
            })
            
            # 에러율 히스토리
            history_data['error_rate'].append({
                'timestamp': timestamp.isoformat(),
                'value': random.uniform(0, 15)
            })
            
            # 응답시간 히스토리
            history_data['response_time'].append({
                'timestamp': timestamp.isoformat(),
                'value': random.uniform(0.1, 8.0)
            })
        
        # 시간순 정렬
        for key in history_data:
            history_data[key].reverse()
        
        return jsonify({
            'success': True,
            'plugin_id': plugin_id,
            'range': range_param,
            'history': history_data
        })
        
    except Exception as e:
        logger.error(f"플러그인 히스토리 조회 실패: {e}")
        return jsonify({'error': '플러그인 히스토리 조회에 실패했습니다.'}), 500

@enhanced_alerts_bp.route('/plugins/metrics', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin', 'manager'])
def get_all_plugin_metrics():
    """모든 플러그인 메트릭 조회"""
    try:
        all_metrics = {}
        for plugin_id, metrics in alert_system.plugin_metrics.items():
            all_metrics[plugin_id] = metrics
        
        return jsonify({
            'success': True,
            'metrics': all_metrics,
            'total_plugins': len(all_metrics)
        })
        
    except Exception as e:
        logger.error(f"모든 플러그인 메트릭 조회 실패: {e}")
        return jsonify({'error': '플러그인 메트릭 조회에 실패했습니다.'}), 500

@enhanced_alerts_bp.route('/notifications/config', methods=['GET'])
@token_required
def get_notification_config():
    """사용자 알림 설정 조회"""
    try:
        user_id = str(request.user.id)  # type: ignore
        
        if user_id not in alert_system.notification_configs:
            # 기본 설정 생성
            config = {
                'user_id': user_id,
                'channels': ['web_toast', 'mobile_push'],
                'alert_types': ['plugin_cpu_high', 'plugin_memory_high', 'plugin_error_rate_high'],
                'severity_levels': ['warning', 'error', 'critical'],
                'enabled': True,
                'quiet_hours_start': None,
                'quiet_hours_end': None
            }
        else:
            config_obj = alert_system.notification_configs[user_id]
            config = {
                'user_id': config_obj.user_id,
                'channels': [c.value for c in config_obj.channels],
                'alert_types': [t.value for t in config_obj.alert_types],
                'severity_levels': [s.value for s in config_obj.severity_levels],
                'enabled': config_obj.enabled,
                'quiet_hours_start': config_obj.quiet_hours_start,
                'quiet_hours_end': config_obj.quiet_hours_end
            }
        
        return jsonify({
            'success': True,
            'config': config
        })
        
    except Exception as e:
        logger.error(f"알림 설정 조회 실패: {e}")
        return jsonify({'error': '알림 설정 조회에 실패했습니다.'}), 500

@enhanced_alerts_bp.route('/notifications/config', methods=['PUT'])
@token_required
def update_notification_config():
    """사용자 알림 설정 업데이트"""
    try:
        user_id = str(request.user.id)  # type: ignore
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '설정 데이터가 필요합니다.'}), 400
        
        # 설정 업데이트
        config = {
            'user_id': user_id,
            'channels': data.get('channels', ['web_toast']),
            'alert_types': data.get('alert_types', []),
            'severity_levels': data.get('severity_levels', ['warning', 'error', 'critical']),
            'enabled': data.get('enabled', True),
            'quiet_hours_start': data.get('quiet_hours_start'),
            'quiet_hours_end': data.get('quiet_hours_end')
        }
        
        # 데이터베이스에 저장
        conn = alert_system.db_path
        # 실제 구현에서는 데이터베이스 저장 로직 추가
        
        return jsonify({
            'success': True,
            'message': '알림 설정이 업데이트되었습니다.',
            'config': config
        })
        
    except Exception as e:
        logger.error(f"알림 설정 업데이트 실패: {e}")
        return jsonify({'error': '알림 설정 업데이트에 실패했습니다.'}), 500

@enhanced_alerts_bp.route('/stream', methods=['GET'])
@token_required
def alert_stream():
    """실시간 알림 스트림 (Server-Sent Events)"""
    def generate():
        user_id = str(request.user.id)  # type: ignore
        connection_id = str(uuid.uuid4())
        
        # 연결 등록
        connected_clients[connection_id] = {
            'user_id': user_id,
            'connected_at': datetime.utcnow()
        }
        
        try:
            # 연결 확인 메시지
            yield f"data: {json.dumps({'type': 'connected', 'connection_id': connection_id})}\n\n"
            
            # 현재 활성 알림 전송
            active_alerts = alert_system.get_active_alerts()
            if active_alerts:
                yield f"data: {json.dumps({'type': 'active_alerts', 'alerts': [a.to_dict() for a in active_alerts]})}\n\n"
            
            # 연결 유지
            while True:
                # 하트비트 전송 (30초마다)
                yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.utcnow().isoformat()})}\n\n"
                
                import time
                time.sleep(30)
                
        except GeneratorExit:
            # 연결 종료 시 정리
            if connection_id in connected_clients:
                del connected_clients[connection_id]
            logger.info(f"알림 스트림 연결 종료: {connection_id}")
    
    return Response(generate(), mimetype='text/event-stream')

@enhanced_alerts_bp.route('/test-alert', methods=['POST'])
@token_required
@role_required(['admin', 'super_admin'])
def test_alert():
    """테스트 알림 발송"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '테스트 알림 데이터가 필요합니다.'}), 400
        
        # 테스트 알림 생성
        alert = alert_system._create_alert(
            AlertType.CUSTOM_ALERT,
            AlertSeverity.INFO,
            data.get('title', '테스트 알림'),
            data.get('message', '이것은 테스트 알림입니다.'),
            plugin_id=data.get('plugin_id'),
            metadata={'test': True}
        )
        
        if alert:
            alert_system._send_alert(alert)
            
            return jsonify({
                'success': True,
                'message': '테스트 알림이 발송되었습니다.',
                'alert_id': alert.id
            })
        else:
            return jsonify({'error': '테스트 알림 생성에 실패했습니다.'}), 500
        
    except Exception as e:
        logger.error(f"테스트 알림 발송 실패: {e}")
        return jsonify({'error': '테스트 알림 발송에 실패했습니다.'}), 500

@enhanced_alerts_bp.route('/system-metrics', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin', 'manager'])
def get_system_metrics():
    """시스템 메트릭 조회"""
    try:
        import psutil
        
        # 시스템 메트릭 수집
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        metrics = {
            'cpu_usage': cpu_usage,
            'memory_usage': memory.percent,
            'disk_usage': disk.percent,
            'network_io': {
                'bytes_sent': network.bytes_sent,  # type: ignore
                'bytes_recv': network.bytes_recv   # type: ignore
            },
            'active_connections': len(psutil.net_connections()),
            'process_count': len(psutil.pids()),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'metrics': metrics
        })
        
    except Exception as e:
        logger.error(f"시스템 메트릭 조회 실패: {e}")
        return jsonify({'error': '시스템 메트릭 조회에 실패했습니다.'}), 500

# WebSocket 이벤트 핸들러
def handle_connect(sid, environ):
    """WebSocket 연결 처리"""
    try:
        # 사용자 인증 확인
        user_id = str(request.user.id) if hasattr(request, 'user') else None  # type: ignore
        
        if user_id:
            connected_clients[sid] = {
                'user_id': user_id,
                'connected_at': datetime.utcnow()
            }
            
            # 사용자별 방에 참가
            join_room(user_id)
            
            logger.info(f"WebSocket 연결: {sid} (사용자: {user_id})")
        else:
            logger.warning(f"인증되지 않은 WebSocket 연결: {sid}")
            
    except Exception as e:
        logger.error(f"WebSocket 연결 처리 실패: {e}")

def handle_disconnect(sid):
    """WebSocket 연결 해제 처리"""
    try:
        if sid in connected_clients:
            del connected_clients[sid]
            logger.info(f"WebSocket 연결 해제: {sid}")
            
    except Exception as e:
        logger.error(f"WebSocket 연결 해제 처리 실패: {e}")

def handle_join_alert_room(sid, data):
    """알림 방 참가"""
    try:
        room = data.get('room')
        if room:
            join_room(room)
            logger.info(f"클라이언트 {sid}가 방 {room}에 참가")
            
    except Exception as e:
        logger.error(f"알림 방 참가 처리 실패: {e}")

def handle_leave_alert_room(sid, data):
    """알림 방 나가기"""
    try:
        room = data.get('room')
        if room:
            leave_room(room)
            logger.info(f"클라이언트 {sid}가 방 {room}에서 나감")
            
    except Exception as e:
        logger.error(f"알림 방 나가기 처리 실패: {e}")

# 초기화 함수
def init_enhanced_alerts_api(app, socketio):
    """고도화된 알림 API 초기화"""
    try:
        # Blueprint 등록
        app.register_blueprint(enhanced_alerts_bp)
        
        # WebSocket 이벤트 등록
        socketio.on_event('connect', handle_connect)
        socketio.on_event('disconnect', handle_disconnect)
        socketio.on_event('join_alert_room', handle_join_alert_room)
        socketio.on_event('leave_alert_room', handle_leave_alert_room)
        
        # 알림 시스템 시작
        init_enhanced_alerts()
        
        logger.info("고도화된 실시간 알림 API 초기화 완료")
        
    except Exception as e:
        logger.error(f"고도화된 실시간 알림 API 초기화 실패: {e}") 