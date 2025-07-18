from core.backend.realtime_notifications import (  # pyright: ignore
    notification_manager, Notification, NotificationType, NotificationPriority
)
from typing import Optional
from datetime import datetime, timedelta
import logging
import uuid
import json
from functools import wraps
from flask_login import login_required, current_user
from flask import Blueprint, jsonify, request, Response
args = None  # pyright: ignore
form = None  # pyright: ignore
"""
실시간 알림 API
WebSocket 및 REST API를 통한 실시간 알림 관리
"""


logger = logging.getLogger(__name__)

realtime_notifications_bp = Blueprint('realtime_notifications', __name__)


def admin_required(f):
    """관리자 권한 확인 데코레이터"""
    @wraps(f)
    def decorated_function(*args,  **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': '로그인이 필요합니다.'}), 401

        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({'error': '관리자 권한이 필요합니다.'}), 403

        return f(*args, **kwargs)
    return decorated_function


def is_duplicate_notification(type: str,  title: str, user_id=None, within_seconds=60) -> bool:
    """최근 동일한 알림이 이미 전송되었는지 확인 (중복 방지)"""
    now = datetime.utcnow()
    for n in notification_manager.get_recent_notifications(user_id=user_id, limit=10):
        if (
            n.type == type and
            n.title == title and
            n.user_id == user_id and
            (now - n.created_at).total_seconds() < within_seconds
        ):
            return True
    return False


@realtime_notifications_bp.route('/api/notifications/channels', methods=['GET'])
@login_required
@admin_required
def get_channels():
    """채널 목록 조회"""
    try:
        channels = []
        for channel_id, channel in notification_manager.channels.items():
            channels.append({
                'id': channel_id,
                'name': channel.name,
                'description': channel.description,
                'subscriber_count': len(channel.subscribers),
                'notification_count': len(channel.notifications)
            })

        return jsonify({
            'success': True,
            'channels': channels
        })

    except Exception as e:
        logger.error(f"채널 목록 조회 실패: {e}")
        return jsonify({'error': '채널 목록 조회에 실패했습니다.'}), 500


@realtime_notifications_bp.route('/api/notifications/channels', methods=['POST'])
@login_required
@admin_required
def create_channel():
    """채널 생성"""
    try:
        data = request.get_json()

        if not data or 'channel_id' not in data or 'name' not in data:
            return jsonify({'error': '채널 ID와 이름이 필요합니다.'}), 400

        channel = notification_manager.create_channel(
            channel_id=data['channel_id'],
            name=data['name'],
            description=data.get('description', '')
        )

        return jsonify({
            'success': True,
            'message': '채널이 생성되었습니다.',
            'channel': {
                'id': channel.channel_id,
                'name': channel.name,
                'description': channel.description
            }
        })

    except Exception as e:
        logger.error(f"채널 생성 실패: {e}")
        return jsonify({'error': '채널 생성에 실패했습니다.'}), 500


@realtime_notifications_bp.route('/api/notifications/subscribe', methods=['POST'])
@login_required
def subscribe_channel():
    """채널 구독"""
    try:
        data = request.get_json()

        if not data or 'channel_id' not in data:
            return jsonify({'error': '채널 ID가 필요합니다.'}), 400

        channel_id = data['channel_id']
        user_id = str(current_user.id)

        if notification_manager.subscribe_user(user_id, channel_id):
            return jsonify({
                'success': True,
                'message': f'채널 {channel_id}에 구독되었습니다.'
            })
        else:
            return jsonify({'error': '채널 구독에 실패했습니다.'}), 400

    except Exception as e:
        logger.error(f"채널 구독 실패: {e}")
        return jsonify({'error': '채널 구독에 실패했습니다.'}), 500


@realtime_notifications_bp.route('/api/notifications/unsubscribe', methods=['POST'])
@login_required
def unsubscribe_channel():
    """채널 구독 해제"""
    try:
        data = request.get_json()
        if not data or 'channel_id' not in data:
            return jsonify({'error': '채널 ID가 필요합니다.'}), 400
        channel_id = data['channel_id']
        user_id = str(current_user.id)
        if notification_manager.unsubscribe_user(user_id, channel_id):
            return jsonify({
                'success': True,
                'message': f'채널 {channel_id} 구독이 해제되었습니다.'
            })
        else:
            return jsonify({'error': '채널 구독 해제에 실패했습니다.'}), 400
    except Exception as e:
        logger.error(f"채널 구독 해제 실패: {e}")
        return jsonify({'error': '채널 구독 해제에 실패했습니다.'}), 500


@realtime_notifications_bp.route('/api/notifications/send', methods=['POST'])
@login_required
@admin_required
def send_notification():
    """알림 전송 (중복 방지 및 DB 기록 보장)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '알림 데이터가 필요합니다.'}), 400
        required_fields = ['channel_id', 'title', 'message', 'type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'필수 필드 {field}가 누락되었습니다.'}), 400
        notification_type = NotificationType(data['type'])
        priority = NotificationPriority(data.get('priority', 'normal'))
        user_id = data.get('user_id')
        if is_duplicate_notification(data['type'], data['title'], user_id):
            logger.info(f"중복 알림 방지: {data['type']}, {data['title']}, {user_id}")
            return jsonify({'error': '동일 알림이 최근에 이미 전송되었습니다.'}), 200
        notification = Notification(
            id=str(uuid.uuid4()),
            type=notification_type,
            title=data['title'],
            message=data['message'],
            priority=priority,
            user_id=user_id,
            group_id=data.get('group_id'),
            data=data.get('data'),
            expires_at=datetime.utcnow() + timedelta(days=7) if data.get('expires_in_days') else None
        )
        try:
            notification_manager.save_to_db(notification)
        except Exception as e:
            logger.error(f"알림 DB 기록 오류: {e}")
        target_users = data.get('target_users')
        if notification_manager.send_notification(data['channel_id'], notification, target_users):
            return jsonify({
                'success': True,
                'message': '알림이 전송되었습니다.',
                'notification_id': notification.id
            })
        else:
            return jsonify({'error': '알림 전송에 실패했습니다.'}), 400
    except Exception as e:
        logger.error(f"알림 전송 실패: {e}")
        return jsonify({'error': '알림 전송에 실패했습니다.'}), 500


@realtime_notifications_bp.route('/api/notifications/user', methods=['GET'])
@login_required
def get_user_notifications():
    """사용자 알림 조회"""
    try:
        user_id = str(current_user.id)
        channel_id = request.args.get('channel_id')
        limit = int(request.args.get('limit', 50))

        notifications = notification_manager.get_user_notifications(user_id, channel_id, limit)

        return jsonify({
            'success': True,
            'notifications': [n.to_dict() for n in notifications],
            'total': len(notifications)
        })

    except Exception as e:
        logger.error(f"사용자 알림 조회 실패: {e}")
        return jsonify({'error': '알림 조회에 실패했습니다.'}), 500


@realtime_notifications_bp.route('/api/notifications/read/<notification_id>', methods=['PUT'])
@login_required
def mark_notification_read(notification_id):
    """알림 읽음 표시 (개선된 응답 포맷)"""
    try:
        user_id = str(current_user.id)

        if notification_manager.mark_as_read(notification_id, user_id):
            return jsonify({
                'success': True,
                'message': '알림이 읽음 처리되었습니다.',
                'notification_id': notification_id,
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': '알림을 찾을 수 없습니다.',
                'notification_id': notification_id
            }), 404

    except Exception as e:
        logger.error(f"알림 읽음 표시 실패: {e}")
        return jsonify({
            'success': False,
            'error': '알림 읽음 표시에 실패했습니다.',
            'details': str(e)
        }), 500


@realtime_notifications_bp.route('/api/notifications/sse')
@login_required
def notification_sse():
    """Server-Sent Events를 통한 실시간 알림 스트림 (개선된 포맷)"""
    def generate():
        user_id = str(current_user.id)
        connection_id = str(uuid.uuid4())

        # 연결 등록
        notification_manager.register_connection(connection_id, user_id)

        # 기본 채널 구독
        default_channels = ['system', 'user']
        if current_user.role in ['admin', 'super_admin']:
            default_channels.append('admin')

        for channel_id in default_channels:
            notification_manager.subscribe_user(user_id, channel_id)

        try:
            # SSE 헤더 전송 (개선된 포맷)
            yield f"data: {json.dumps({'type': 'connected', 'connection_id': connection_id, 'success': True})}\n\n"

            # 연결 유지
            while True:
                # 하트비트 전송 (30초마다)
                yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.utcnow().isoformat(), 'success': True})}\n\n"

                # 실제 구현에서는 WebSocket이나 더 효율적인 방법 사용
                import time
                time.sleep(30)

        except GeneratorExit:
            # 연결 종료 시 정리
            notification_manager.unregister_connection(connection_id)
            for channel_id in default_channels:
                notification_manager.unsubscribe_user(user_id, channel_id)
            logger.info(f"SSE 연결 종료: {connection_id}")

    return Response(generate(), mimetype='text/event-stream')


@realtime_notifications_bp.route('/api/notifications/stats', methods=['GET'])
@login_required
@admin_required
def get_notification_stats():
    """알림 통계 조회"""
    try:
        stats = {
            'total_channels': len(notification_manager.channels),
            'total_connections': len(notification_manager.connection_users),
            'total_users': len(notification_manager.user_connections),
            'channels': {}
        }

        for channel_id, channel in notification_manager.channels.items():
            if isinstance(stats['channels'], dict):
                stats['channels'][channel_id] = {
                    'name': channel.name,
                    'subscriber_count': len(channel.subscribers),
                    'notification_count': len(channel.notifications),
                    'unread_count': len([n for n in channel.notifications if not n.read])
                }

        return jsonify({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        logger.error(f"알림 통계 조회 실패: {e}")
        return jsonify({'error': '알림 통계 조회에 실패했습니다.'}), 500


@realtime_notifications_bp.route('/api/notifications/cleanup', methods=['POST'])
@login_required
@admin_required
def cleanup_notifications():
    """만료된 알림 정리"""
    try:
        notification_manager.cleanup_expired_notifications()

        return jsonify({
            'success': True,
            'message': '만료된 알림이 정리되었습니다.'
        })

    except Exception as e:
        logger.error(f"알림 정리 실패: {e}")
        return jsonify({'error': '알림 정리에 실패했습니다.'}), 500
