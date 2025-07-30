"""
WebSocket 관련 REST API
실시간 알림 시스템을 위한 HTTP 엔드포인트
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from websocket.websocket_server import get_notification_manager

logger = logging.getLogger(__name__)

websocket_api = Blueprint('websocket_api', __name__)

@websocket_api.route('/api/websocket/status', methods=['GET'])
def get_websocket_status():
    """WebSocket 서버 상태 조회"""
    try:
        notification_manager = get_notification_manager()
        
        if not notification_manager:
            return jsonify({
                'success': False,
                'error': 'WebSocket 서버가 초기화되지 않았습니다.'
            }), 503
        
        status = notification_manager.get_connected_clients_info()
        
        return jsonify({
            'success': True,
            'data': status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"WebSocket 상태 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@websocket_api.route('/api/websocket/notifications/send', methods=['POST'])
def send_notification():
    """알림 전송"""
    try:
        data = request.get_json()
        
        notification_type = data.get('type')
        message = data.get('message')
        notification_data = data.get('data', {})
        target_rooms = data.get('target_rooms')
        target_users = data.get('target_users')
        
        if not notification_type or not message:
            return jsonify({
                'success': False,
                'error': '알림 타입과 메시지가 필요합니다.'
            }), 400
        
        notification_manager = get_notification_manager()
        
        if not notification_manager:
            return jsonify({
                'success': False,
                'error': 'WebSocket 서버가 초기화되지 않았습니다.'
            }), 503
        
        notification = notification_manager.send_notification(
            notification_type=notification_type,
            message=message,
            data=notification_data,
            target_rooms=target_rooms,
            target_users=target_users
        )
        
        if notification:
            return jsonify({
                'success': True,
                'data': notification,
                'message': '알림이 성공적으로 전송되었습니다.'
            })
        else:
            return jsonify({
                'success': False,
                'error': '알림 전송에 실패했습니다.'
            }), 500
            
    except Exception as e:
        logger.error(f"알림 전송 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@websocket_api.route('/api/websocket/notifications/history', methods=['GET'])
def get_notification_history():
    """알림 히스토리 조회"""
    try:
        notification_manager = get_notification_manager()
        
        if not notification_manager:
            return jsonify({
                'success': False,
                'error': 'WebSocket 서버가 초기화되지 않았습니다.'
            }), 503
        
        # 쿼리 파라미터
        limit = request.args.get('limit', 50, type=int)
        notification_type = request.args.get('type')
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        history = notification_manager.notification_history.copy()
        
        # 타입 필터링
        if notification_type:
            history = [n for n in history if n.get('type') == notification_type]
        
        # 읽지 않은 알림만 필터링
        if unread_only:
            history = [n for n in history if not n.get('read', False)]
        
        # 최신순으로 정렬하고 제한
        history.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        history = history[:limit]
        
        return jsonify({
            'success': True,
            'data': {
                'notifications': history,
                'total_count': len(history),
                'filters': {
                    'type': notification_type,
                    'unread_only': unread_only,
                    'limit': limit
                }
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"알림 히스토리 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@websocket_api.route('/api/websocket/notifications/clear', methods=['POST'])
def clear_notification_history():
    """알림 히스토리 정리"""
    try:
        data = request.get_json() or {}
        
        notification_type = data.get('type')
        older_than_hours = data.get('older_than_hours', 24)
        
        notification_manager = get_notification_manager()
        
        if not notification_manager:
            return jsonify({
                'success': False,
                'error': 'WebSocket 서버가 초기화되지 않았습니다.'
            }), 503
        
        # 정리할 알림 수 계산
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        original_count = len(notification_manager.notification_history)
        
        # 조건에 맞는 알림 제거
        if notification_type:
            notification_manager.notification_history = [
                n for n in notification_manager.notification_history
                if n.get('type') != notification_type or 
                datetime.fromisoformat(n.get('created_at', '1970-01-01')) > cutoff_time
            ]
        else:
            notification_manager.notification_history = [
                n for n in notification_manager.notification_history
                if datetime.fromisoformat(n.get('created_at', '1970-01-01')) > cutoff_time
            ]
        
        cleared_count = original_count - len(notification_manager.notification_history)
        
        return jsonify({
            'success': True,
            'data': {
                'cleared_count': cleared_count,
                'remaining_count': len(notification_manager.notification_history),
                'filters': {
                    'type': notification_type,
                    'older_than_hours': older_than_hours
                }
            },
            'message': f'{cleared_count}개의 알림이 정리되었습니다.'
        })
        
    except Exception as e:
        logger.error(f"알림 히스토리 정리 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@websocket_api.route('/api/websocket/notifications/mark-read', methods=['POST'])
def mark_notifications_read():
    """알림 읽음 처리"""
    try:
        data = request.get_json()
        
        notification_ids = data.get('notification_ids', [])
        mark_all = data.get('mark_all', False)
        
        if not notification_ids and not mark_all:
            return jsonify({
                'success': False,
                'error': '알림 ID 목록 또는 mark_all 플래그가 필요합니다.'
            }), 400
        
        notification_manager = get_notification_manager()
        
        if not notification_manager:
            return jsonify({
                'success': False,
                'error': 'WebSocket 서버가 초기화되지 않았습니다.'
            }), 503
        
        marked_count = 0
        
        if mark_all:
            # 모든 알림을 읽음 처리
            for notification in notification_manager.notification_history:
                if not notification.get('read', False):
                    notification['read'] = True
                    notification['read_at'] = datetime.now().isoformat()
                    marked_count += 1
        else:
            # 지정된 알림만 읽음 처리
            for notification in notification_manager.notification_history:
                if notification.get('id') in notification_ids and not notification.get('read', False):
                    notification['read'] = True
                    notification['read_at'] = datetime.now().isoformat()
                    marked_count += 1
        
        return jsonify({
            'success': True,
            'data': {
                'marked_count': marked_count,
                'total_notifications': len(notification_manager.notification_history)
            },
            'message': f'{marked_count}개의 알림이 읽음 처리되었습니다.'
        })
        
    except Exception as e:
        logger.error(f"알림 읽음 처리 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@websocket_api.route('/api/websocket/notifications/stats', methods=['GET'])
def get_notification_stats():
    """알림 통계 조회"""
    try:
        notification_manager = get_notification_manager()
        
        if not notification_manager:
            return jsonify({
                'success': False,
                'error': 'WebSocket 서버가 초기화되지 않았습니다.'
            }), 503
        
        # 통계 계산
        total_notifications = len(notification_manager.notification_history)
        unread_count = sum(1 for n in notification_manager.notification_history if not n.get('read', False))
        
        # 타입별 통계
        type_stats = {}
        for notification in notification_manager.notification_history:
            notification_type = notification.get('type', 'unknown')
            if notification_type not in type_stats:
                type_stats[notification_type] = {'total': 0, 'unread': 0}
            
            type_stats[notification_type]['total'] += 1
            if not notification.get('read', False):
                type_stats[notification_type]['unread'] += 1
        
        # 우선순위별 통계
        priority_stats = {'high': 0, 'medium': 0, 'low': 0}
        for notification in notification_manager.notification_history:
            priority = notification.get('priority', 'medium')
            priority_stats[priority] = priority_stats.get(priority, 0) + 1
        
        return jsonify({
            'success': True,
            'data': {
                'total_notifications': total_notifications,
                'unread_count': unread_count,
                'read_count': total_notifications - unread_count,
                'type_stats': type_stats,
                'priority_stats': priority_stats,
                'connected_clients': len(notification_manager.connected_clients)
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"알림 통계 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 