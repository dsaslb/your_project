from models.notification_models import NotificationHistory  # pyright: ignore
from typing import Optional, Any
import json
from datetime import datetime, timedelta
from api.gateway import token_required, role_required  # pyright: ignore
from models_main import Notification, User, db, Order, Schedule, Attendance
from functools import wraps
from flask_socketio import emit, join_room, leave_room
from flask import Blueprint, request, jsonify, current_app
args = None  # pyright: ignore
query = None  # pyright: ignore
form = None  # pyright: ignore

notification_system = Blueprint('notification_system', __name__)

# 알림 타입 정의
NOTIFICATION_TYPES = {
    'order_new': '새 주문',
    'order_status': '주문 상태 변경',
    'inventory_low': '재고 부족',
    'staff_attendance': '직원 출퇴근',
    'schedule_change': '스케줄 변경',
    'system_alert': '시스템 알림',
    'security_alert': '보안 알림',
    'performance_alert': '성능 알림'
}

# 알림 우선순위
PRIORITY_LEVELS = {
    'low': 1,
    'medium': 2,
    'high': 3,
    'urgent': 4
}

# 알림 저장소 (실제로는 데이터베이스 사용)
_notifications = []
_connected_users = {}


def is_duplicate_notification(type: str,  title: str, user_id=None, within_seconds=60) -> bool:
    """최근 동일한 알림이 이미 전송되었는지 확인 (중복 방지)"""
    now = datetime.utcnow()
    for n in reversed(_notifications):
        if (
            n['type'] == type and
            n['title'] == title and
            n.get('user_id') == user_id and
            (now - datetime.fromisoformat(n['created_at'])).total_seconds() < within_seconds
        ):
            return True
    return False


def create_notification(
    type: str,
    title: str,
    message: str,
    user_id: Optional[int] = None,
    priority: str = 'medium',
    data: Optional[dict[str, Any]] = None,
    expires_at=None
) -> Optional[dict[str, Any]]:
    """알림 생성 및 DB 기록, 중복 방지"""
    if is_duplicate_notification(type,  title,  user_id):
        current_app.logger.info(f"중복 알림 방지: {type}, {title}, {user_id}")
        return None
    notification = {
        'id': len(_notifications) + 1,
        'type': type,
        'title': title,
        'message': message,
        'user_id': user_id,
        'priority': priority,
        'data': data or {},
        'created_at': datetime.utcnow().isoformat(),
        'expires_at': expires_at.isoformat() if expires_at else None,
        'read': False,
        'read_at': None
    }
    _notifications.append(notification)
    try:
        # DB 기록 (NotificationHistory 모델 활용)
        db_notification = NotificationHistory(
            title=notification['title'],
            message=notification['message'],
            level=notification.get('priority', 'info'),
            channel='system',
            recipient=str(user_id) if user_id else None,
            metadata=None,
            sent_at=datetime.utcnow(),
            success=True,
            error_message=None
        )
        db.session.add(db_notification)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"알림 DB 기록 오류: {str(e)}")
    # 실시간 알림 전송
    if user_id and user_id in _connected_users:
        emit('notification', notification)  # room 파라미터 제거
    if priority in ['high', 'urgent']:
        for uid, user_data in _connected_users.items() if _connected_users is not None else []:
            if user_data.get('role') if user_data else None in ['admin', 'super_admin']:
                emit('notification', notification)  # room 파라미터 제거
    return notification


def send_system_notification(title,  message, priority='medium', data=None):
    """시스템 전체 알림"""
    notification = create_notification(
        'system_alert',
        title,
        message,
        priority=priority,
        data=data
    )

    # 모든 연결된 사용자에게 전송
    if _connected_users is not None:
        for user_id in _connected_users:
            emit('notification', notification)

    return notification

# 알림 조회 API 개선 (우선순위/타입/읽음 등 다양한 필터 지원)


@notification_system.route('/notifications', methods=['GET'])
@token_required
@role_required(['super_admin', 'brand_manager', 'store_manager', 'employee'])
def get_notifications(current_user):
    """사용자 알림 조회 (다양한 필터 지원)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        notification_type = request.args.get('type')
        priority = request.args.get('priority')
        # 사용자 알림 필터링
        user_notifications = []
        if _notifications is not None:
            for notification in _notifications:
                if (notification.get('user_id') == current_user.id or notification.get('user_id') is None):
                    if unread_only and notification.get('read'):
                        continue
                    if notification_type and notification.get('type') != notification_type:
                        continue
                    if priority and notification.get('priority') != priority:
                        continue
                    user_notifications.append(notification)
        user_notifications.sort(key=lambda x: x['created_at'], reverse=True)
        total = len(user_notifications)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_notifications = user_notifications[start_idx:end_idx] if user_notifications is not None else None
        return jsonify({
            'notifications': paginated_notifications,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            },
            'unread_count': len([n for n in user_notifications if not n.get('read')])
        }), 200
    except Exception as e:
        current_app.logger.error(f"알림 조회 오류: {str(e)}")
        return jsonify({'message': '알림 조회 중 오류가 발생했습니다'}), 500

# 알림 읽음 처리


@notification_system.route('/notifications/<int:notification_id>/read', methods=['PUT'])
@token_required
def mark_notification_read(current_user,  notification_id):
    """알림 읽음 처리 (DB 히스토리 기록 포함)"""
    try:
        notification = next((n for n in _notifications if n['id'] == notification_id), None)
        if not notification:
            return jsonify({'message': '알림을 찾을 수 없습니다'}), 404
        # 사용자 권한 확인
        if notification.get('user_id') and notification.get('user_id') != current_user.id:
            return jsonify({'message': '권한이 없습니다'}), 403
        notification['read'] = True
        notification['read_at'] = datetime.utcnow().isoformat()
        # DB 히스토리 기록
        try:
            from models.notification_models import NotificationHistory  # pyright: ignore
            from models_main import db
            # NotificationHistory 생성자 파라미터 예시 (실제 모델에 맞게 수정 필요)
            db_notification = NotificationHistory(
                title=notification['title'],
                message=notification['message'],
                level=notification.get('priority', 'info'),
                channel='system',
                recipient=str(current_user.id),
                metadata=None,
                sent_at=datetime.utcnow(),
                success=True,
                error_message=None
            )
            db.session.add(db_notification)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"알림 읽음 DB 기록 오류: {str(e)}")
        return jsonify({
            'message': '알림이 읽음 처리되었습니다',
            'notification': notification
        }), 200
    except Exception as e:
        current_app.logger.error(f"알림 읽음 처리 오류: {str(e)}")
        return jsonify({'message': '알림 읽음 처리 중 오류가 발생했습니다'}), 500

# 모든 알림 읽음 처리


@notification_system.route('/notifications/read-all', methods=['PUT'])
@token_required
def mark_all_notifications_read(current_user):
    """모든 알림 읽음 처리"""
    try:
        count = 0
        if _notifications is not None:
            for notification in _notifications:
                if (notification.get('user_id') == current_user.id or notification.get('user_id') is None) and not notification.get('read'):
                    notification['read'] = True
                    notification['read_at'] = datetime.utcnow().isoformat()
                    count += 1

        return jsonify({
            'message': f'{count}개의 알림이 읽음 처리되었습니다',
            'count': count
        }), 200

    except Exception as e:
        current_app.logger.error(f"모든 알림 읽음 처리 오류: {str(e)}")
        return jsonify({'message': '알림 읽음 처리 중 오류가 발생했습니다'}), 500

# 알림 삭제


@notification_system.route('/notifications/<int:notification_id>', methods=['DELETE'])
@token_required
def delete_notification(current_user,  notification_id):
    """알림 삭제"""
    try:
        notification = next(
            (n for n in _notifications if n['id'] == notification_id),
            None
        )

        if not notification:
            return jsonify({'message': '알림을 찾을 수 없습니다'}), 404

        # 사용자 권한 확인
        if notification.get('user_id') and notification.get('user_id') != current_user.id:
            return jsonify({'message': '권한이 없습니다'}), 403

        _notifications.remove(notification)

        return jsonify({'message': '알림이 삭제되었습니다'}), 200

    except Exception as e:
        current_app.logger.error(f"알림 삭제 오류: {str(e)}")
        return jsonify({'message': '알림 삭제 중 오류가 발생했습니다'}), 500

# 알림 설정 조회


@notification_system.route('/settings', methods=['GET'])
@token_required
def get_notification_settings(current_user):
    """알림 설정 조회"""
    try:
        # 실제로는 데이터베이스에서 사용자별 설정 조회
        settings = {
            'email_notifications': True,
            'push_notifications': True,
            'sound_enabled': True,
            'notification_types': {
                'order_new': True,
                'order_status': True,
                'inventory_low': True,
                'staff_attendance': False,
                'schedule_change': True,
                'system_alert': True,
                'security_alert': True,
                'performance_alert': False
            },
            'quiet_hours': {
                'enabled': False,
                'start': '22:00',
                'end': '08:00'
            }
        }

        return jsonify(settings), 200

    except Exception as e:
        current_app.logger.error(f"알림 설정 조회 오류: {str(e)}")
        return jsonify({'message': '알림 설정 조회 중 오류가 발생했습니다'}), 500

# 알림 설정 업데이트


@notification_system.route('/settings', methods=['PUT'])
@token_required
def update_notification_settings(current_user):
    """알림 설정 업데이트"""
    try:
        data = request.get_json() or {}

        # 실제로는 데이터베이스에 설정 저장
        updated_settings = {
            'email_notifications': data.get('email_notifications', True),
            'push_notifications': data.get('push_notifications', True),
            'sound_enabled': data.get('sound_enabled', True),
            'notification_types': data.get('notification_types', {}),
            'quiet_hours': data.get('quiet_hours', {})
        }

        return jsonify({
            'message': '알림 설정이 업데이트되었습니다',
            'settings': updated_settings
        }), 200

    except Exception as e:
        current_app.logger.error(f"알림 설정 업데이트 오류: {str(e)}")
        return jsonify({'message': '알림 설정 업데이트 중 오류가 발생했습니다'}), 500

# 테스트 알림 전송


@notification_system.route('/test', methods=['POST'])
@token_required
@role_required(['admin', 'super_admin'])
def send_test_notification(current_user):
    """테스트 알림 전송"""
    try:
        data = request.get_json() or {}
        notification_type = data.get('type', 'system_alert')
        message = data.get('message', '테스트 알림입니다')

        notification = create_notification(
            notification_type,
            '테스트 알림',
            message,
            current_user.id,
            'medium',
            {'test': True}
        )

        return jsonify({
            'message': '테스트 알림이 전송되었습니다',
            'notification': notification
        }), 200

    except Exception as e:
        current_app.logger.error(f"테스트 알림 전송 오류: {str(e)}")
        return jsonify({'message': '테스트 알림 전송 중 오류가 발생했습니다'}), 500

# 알림 통계


@notification_system.route('/stats', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
def get_notification_stats(current_user):
    """알림 통계 조회"""
    try:
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())

        # 오늘 생성된 알림
        today_notifications = [
            n for n in _notifications
            if today_start <= datetime.fromisoformat(n['created_at']) <= today_end
        ]

        # 타입별 통계
        type_stats = {}
        if today_notifications is not None:
            for notification in today_notifications:
                notification_type = notification.get('type', 'unknown')
                if notification_type not in type_stats:
                    type_stats[notification_type] = 0
                type_stats[notification_type] += 1

        # 우선순위별 통계
        priority_stats = {}
        if today_notifications is not None:
            for notification in today_notifications:
                priority = notification.get('priority', 'medium')
                if priority not in priority_stats:
                    priority_stats[priority] = 0
                priority_stats[priority] += 1

        return jsonify({
            'today_total': len(today_notifications),
            'today_unread': len([n for n in today_notifications if not n.get('read')]),
            'type_stats': type_stats,
            'priority_stats': priority_stats,
            'total_notifications': len(_notifications)
        }), 200

    except Exception as e:
        current_app.logger.error(f"알림 통계 조회 오류: {str(e)}")
        return jsonify({'message': '알림 통계 조회 중 오류가 발생했습니다'}), 500
