from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from models import Notification, User, db
from api.gateway import token_required, role_required
from datetime import datetime, timedelta
import json

notification_system = Blueprint('notification_system', __name__)

# 알림 생성
def create_notification(user_id, title, message, type='info', data=None, priority='normal'):
    """알림 생성 헬퍼 함수"""
    try:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            data=json.dumps(data) if data else None,
            priority=priority,
            is_read=False,
            created_at=datetime.utcnow()
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return notification
    except Exception as e:
        current_app.logger.error(f"Create notification error: {str(e)}")
        db.session.rollback()
        return None

# 알림 목록 조회
@notification_system.route('/notifications', methods=['GET'])
@token_required
def get_notifications(current_user):
    """사용자 알림 목록 조회"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        is_read = request.args.get('is_read')
        type_filter = request.args.get('type')
        
        query = Notification.query.filter_by(user_id=current_user.id)
        
        # 읽음 상태 필터
        if is_read is not None:
            is_read_bool = is_read.lower() == 'true'
            query = query.filter(Notification.is_read == is_read_bool)
        
        # 타입 필터
        if type_filter:
            query = query.filter(Notification.type == type_filter)
        
        # 최신순 정렬
        query = query.order_by(Notification.created_at.desc())
        
        # 페이지네이션
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        notifications = []
        for notification in pagination.items:
            notifications.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'type': notification.type,
                'priority': notification.priority,
                'is_read': notification.is_read,
                'data': json.loads(notification.data) if notification.data else None,
                'created_at': notification.created_at.isoformat() if notification.created_at else None
            })
        
        return jsonify({
            'notifications': notifications,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get notifications error: {str(e)}")
        return jsonify({'message': '알림 목록 조회 중 오류가 발생했습니다'}), 500

# 알림 상세 조회
@notification_system.route('/notifications/<int:notification_id>', methods=['GET'])
@token_required
def get_notification(current_user, notification_id):
    """알림 상세 조회"""
    try:
        notification = Notification.query.filter_by(
            id=notification_id, 
            user_id=current_user.id
        ).first_or_404()
        
        # 읽음 처리
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            db.session.commit()
        
        return jsonify({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.type,
            'priority': notification.priority,
            'is_read': notification.is_read,
            'data': json.loads(notification.data) if notification.data else None,
            'created_at': notification.created_at.isoformat() if notification.created_at else None,
            'read_at': notification.read_at.isoformat() if notification.read_at else None
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get notification error: {str(e)}")
        return jsonify({'message': '알림 조회 중 오류가 발생했습니다'}), 500

# 알림 읽음 처리
@notification_system.route('/notifications/<int:notification_id>/read', methods=['PUT'])
@token_required
def mark_as_read(current_user, notification_id):
    """알림 읽음 처리"""
    try:
        notification = Notification.query.filter_by(
            id=notification_id, 
            user_id=current_user.id
        ).first_or_404()
        
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': '알림이 읽음 처리되었습니다'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Mark as read error: {str(e)}")
        return jsonify({'message': '알림 읽음 처리 중 오류가 발생했습니다'}), 500

# 모든 알림 읽음 처리
@notification_system.route('/notifications/read-all', methods=['PUT'])
@token_required
def mark_all_as_read(current_user):
    """모든 알림 읽음 처리"""
    try:
        unread_notifications = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).all()
        
        for notification in unread_notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(unread_notifications)}개의 알림이 읽음 처리되었습니다'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Mark all as read error: {str(e)}")
        return jsonify({'message': '알림 읽음 처리 중 오류가 발생했습니다'}), 500

# 알림 삭제
@notification_system.route('/notifications/<int:notification_id>', methods=['DELETE'])
@token_required
def delete_notification(current_user, notification_id):
    """알림 삭제"""
    try:
        notification = Notification.query.filter_by(
            id=notification_id, 
            user_id=current_user.id
        ).first_or_404()
        
        db.session.delete(notification)
        db.session.commit()
        
        return jsonify({'message': '알림이 삭제되었습니다'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Delete notification error: {str(e)}")
        return jsonify({'message': '알림 삭제 중 오류가 발생했습니다'}), 500

# 알림 통계
@notification_system.route('/notifications/stats', methods=['GET'])
@token_required
def get_notification_stats(current_user):
    """알림 통계"""
    try:
        total_notifications = Notification.query.filter_by(user_id=current_user.id).count()
        unread_notifications = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).count()
        
        # 타입별 통계
        type_stats = {}
        for notification_type in ['info', 'warning', 'error', 'success']:
            count = Notification.query.filter_by(
                user_id=current_user.id,
                type=notification_type
            ).count()
            type_stats[notification_type] = count
        
        # 우선순위별 통계
        priority_stats = {}
        for priority in ['low', 'normal', 'high', 'urgent']:
            count = Notification.query.filter_by(
                user_id=current_user.id,
                priority=priority
            ).count()
            priority_stats[priority] = count
        
        # 최근 7일 알림 수
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_notifications = Notification.query.filter(
            Notification.user_id == current_user.id,
            Notification.created_at >= week_ago
        ).count()
        
        return jsonify({
            'total_notifications': total_notifications,
            'unread_notifications': unread_notifications,
            'read_notifications': total_notifications - unread_notifications,
            'type_stats': type_stats,
            'priority_stats': priority_stats,
            'recent_notifications': recent_notifications
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get notification stats error: {str(e)}")
        return jsonify({'message': '알림 통계 조회 중 오류가 발생했습니다'}), 500

# 관리자용 알림 전송
@notification_system.route('/notifications/send', methods=['POST'])
@token_required
@role_required(['super_admin', 'brand_manager', 'store_manager'])
def send_notification(current_user):
    """관리자용 알림 전송"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['title', 'message', 'user_ids']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} 필드는 필수입니다'}), 400
        
        user_ids = data['user_ids']
        title = data['title']
        message = data['message']
        notification_type = data.get('type', 'info')
        priority = data.get('priority', 'normal')
        notification_data = data.get('data')
        
        # 권한 확인
        if current_user.role != 'super_admin':
            # 브랜드 관리자는 자신의 브랜드 사용자에게만 전송 가능
            if current_user.role == 'brand_manager':
                users = User.query.filter(
                    User.id.in_(user_ids),
                    User.brand_id == current_user.brand_id
                ).all()
            # 매장 관리자는 자신의 매장 사용자에게만 전송 가능
            elif current_user.role == 'store_manager':
                users = User.query.filter(
                    User.id.in_(user_ids),
                    User.store_id == current_user.store_id
                ).all()
        else:
            users = User.query.filter(User.id.in_(user_ids)).all()
        
        # 알림 전송
        sent_count = 0
        for user in users:
            notification = create_notification(
                user_id=user.id,
                title=title,
                message=message,
                type=notification_type,
                data=notification_data,
                priority=priority
            )
            if notification:
                sent_count += 1
        
        return jsonify({
            'message': f'{sent_count}명에게 알림이 전송되었습니다',
            'sent_count': sent_count,
            'total_users': len(users)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Send notification error: {str(e)}")
        return jsonify({'message': '알림 전송 중 오류가 발생했습니다'}), 500 