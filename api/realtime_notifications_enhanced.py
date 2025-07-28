# -*- coding: utf-8 -*-
"""
향상된 실시간 알림/이력/모니터링 API
최근 작업, 승인/거절, 실패/오류, 장애/배포 등 이벤트 기록
실시간 알림(운영자/관리자), 장애/이슈 히스토리 시각화
"""

import logging
import json
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import and_, or_, func, desc, case
from collections import defaultdict
import threading
import time

from extensions import db, csrf
from models_main import (
    Notification, SystemLog, ActionLog, User, IndustryAdmin,
    PluginDeployment, Brand, Branch
)
from models.plugin_models import PluginInstallation as PluginInstall

# 로깅 설정
logger = logging.getLogger(__name__)

# Blueprint 생성
realtime_notifications_bp = Blueprint('realtime_notifications_enhanced', __name__)

class NotificationManager:
    """알림 관리자 클래스"""
    
    def __init__(self):
        self.notification_types = {
            'system_alert': {
                'title_template': '시스템 알림: {title}',
                'priority': 'high',
                'auto_expire': False
            },
            'security_alert': {
                'title_template': '보안 알림: {title}',
                'priority': 'critical',
                'auto_expire': False
            },
            'approval_request': {
                'title_template': '승인 요청: {title}',
                'priority': 'medium',
                'auto_expire': True,
                'expire_hours': 72
            },
            'approval_result': {
                'title_template': '승인 결과: {title}',
                'priority': 'medium',
                'auto_expire': True,
                'expire_hours': 48
            },
            'plugin_event': {
                'title_template': '플러그인 이벤트: {title}',
                'priority': 'medium',
                'auto_expire': True,
                'expire_hours': 24
            },
            'user_activity': {
                'title_template': '사용자 활동: {title}',
                'priority': 'low',
                'auto_expire': True,
                'expire_hours': 12
            },
            'error_notification': {
                'title_template': '오류 알림: {title}',
                'priority': 'high',
                'auto_expire': False
            },
            'deployment_notification': {
                'title_template': '배포 알림: {title}',
                'priority': 'medium',
                'auto_expire': True,
                'expire_hours': 24
            }
        }
    
    def create_notification(self, notification_type, title, content, target_users=None, metadata=None):
        """알림 생성"""
        try:
            if notification_type not in self.notification_types:
                raise ValueError(f"알 수 없는 알림 타입: {notification_type}")
            
            notification_config = self.notification_types[notification_type]
            
            # 제목 템플릿 적용
            formatted_title = notification_config['title_template'].format(title=title)
            
            # 알림 생성
            notification = Notification(
                title=formatted_title,
                content=content,
                type=notification_type,
                severity=notification_config['priority'],
                metadata=json.dumps(metadata) if metadata else None,
                created_at=datetime.utcnow()
            )
            
            db.session.add(notification)
            db.session.flush()  # ID 생성
            
            # 대상 사용자에게 알림 전송
            if target_users:
                self._send_to_users(notification, target_users)
            else:
                # 기본적으로 관리자들에게 전송
                self._send_to_admins(notification)
            
            db.session.commit()
            
            logger.info(f"알림 생성 완료: {notification_type} - {title}")
            
            return notification
            
        except Exception as e:
            logger.error(f"알림 생성 실패: {e}")
            db.session.rollback()
            raise
    
    def _send_to_users(self, notification, user_ids):
        """특정 사용자들에게 알림 전송"""
        for user_id in user_ids:
            user_notification = Notification(
                title=notification.title,
                content=notification.content,
                type=notification.type,
                severity=notification.severity,
                metadata=notification.metadata,
                user_id=user_id,
                created_at=datetime.utcnow()
            )
            db.session.add(user_notification)
    
    def _send_to_admins(self, notification):
        """관리자들에게 알림 전송"""
        admin_users = User.query.filter(
            User.role.in_(['admin', 'industry_admin'])
        ).all()
        
        for admin in admin_users:
            admin_notification = Notification(
                title=notification.title,
                content=notification.content,
                type=notification.type,
                severity=notification.severity,
                metadata=notification.metadata,
                user_id=admin.id,
                created_at=datetime.utcnow()
            )
            db.session.add(admin_notification)
    
    def mark_as_read(self, notification_id, user_id):
        """알림 읽음 처리"""
        try:
            notification = Notification.query.filter_by(
                id=notification_id,
                user_id=user_id
            ).first()
            
            if notification:
                notification.is_read = True
                notification.read_at = datetime.utcnow()
                db.session.commit()
                
                logger.info(f"알림 읽음 처리: {notification_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"알림 읽음 처리 실패: {e}")
            db.session.rollback()
            return False
    
    def delete_notification(self, notification_id, user_id):
        """알림 삭제"""
        try:
            notification = Notification.query.filter_by(
                id=notification_id,
                user_id=user_id
            ).first()
            
            if notification:
                db.session.delete(notification)
                db.session.commit()
                
                logger.info(f"알림 삭제: {notification_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"알림 삭제 실패: {e}")
            db.session.rollback()
            return False
    
    def cleanup_expired_notifications(self):
        """만료된 알림 정리"""
        try:
            now = datetime.utcnow()
            deleted_count = 0
            
            for notification_type, config in self.notification_types.items():
                if config.get('auto_expire'):
                    expire_hours = config.get('expire_hours', 24)
                    expire_time = now - timedelta(hours=expire_hours)
                    
                    expired_notifications = Notification.query.filter(
                        and_(
                            Notification.type == notification_type,
                            Notification.created_at < expire_time,
                            Notification.is_read == True
                        )
                    ).all()
                    
                    for notification in expired_notifications:
                        db.session.delete(notification)
                        deleted_count += 1
            
            db.session.commit()
            
            if deleted_count > 0:
                logger.info(f"만료된 알림 {deleted_count}개 정리 완료")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"만료된 알림 정리 실패: {e}")
            db.session.rollback()
            return 0

class EventTracker:
    """이벤트 추적 클래스"""
    
    def __init__(self):
        self.event_types = {
            'user_login': '사용자 로그인',
            'user_logout': '사용자 로그아웃',
            'user_creation': '사용자 생성',
            'user_update': '사용자 정보 수정',
            'user_deletion': '사용자 삭제',
            'approval_request': '승인 요청',
            'approval_approve': '승인 완료',
            'approval_reject': '승인 거절',
            'plugin_install': '플러그인 설치',
            'plugin_uninstall': '플러그인 제거',
            'plugin_update': '플러그인 업데이트',
            'plugin_error': '플러그인 오류',
            'system_error': '시스템 오류',
            'security_violation': '보안 위반',
            'data_backup': '데이터 백업',
            'data_restore': '데이터 복원',
            'deployment_start': '배포 시작',
            'deployment_complete': '배포 완료',
            'deployment_failed': '배포 실패'
        }
    
    def track_event(self, event_type, user_id, details=None, metadata=None):
        """이벤트 추적"""
        try:
            if event_type not in self.event_types:
                logger.warning(f"알 수 없는 이벤트 타입: {event_type}")
            
            event_description = self.event_types.get(event_type, event_type)
            
            # 활동 로그 기록
            action_log = ActionLog(
                user_id=user_id,
                action=event_type,
                message=f"{event_description}: {details}" if details else event_description,
                metadata=json.dumps(metadata) if metadata else None,
                ip_address=request.remote_addr if request else None,
                user_agent=request.headers.get('User-Agent') if request else None,
                created_at=datetime.utcnow()
            )
            
            db.session.add(action_log)
            db.session.commit()
            
            logger.info(f"이벤트 추적: {event_type} - {event_description}")
            
            return action_log
            
        except Exception as e:
            logger.error(f"이벤트 추적 실패: {e}")
            db.session.rollback()
            raise
    
    def get_event_summary(self, days=7):
        """이벤트 요약 조회"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # 이벤트 타입별 통계
            event_stats = db.session.query(
                ActionLog.action,
                func.count(ActionLog.id).label('count')
            ).filter(
                ActionLog.created_at >= start_date
            ).group_by(ActionLog.action).all()
            
            # 일별 이벤트 통계
            daily_stats = db.session.query(
                func.date(ActionLog.created_at).label('date'),
                func.count(ActionLog.id).label('count')
            ).filter(
                ActionLog.created_at >= start_date
            ).group_by(func.date(ActionLog.created_at)).order_by(
                func.date(ActionLog.created_at)
            ).all()
            
            # 사용자별 활동 통계
            user_stats = db.session.query(
                ActionLog.user_id,
                User.username,
                func.count(ActionLog.id).label('count')
            ).join(User).filter(
                ActionLog.created_at >= start_date
            ).group_by(ActionLog.user_id, User.username).order_by(
                func.count(ActionLog.id).desc()
            ).limit(10).all()
            
            summary = {
                'period_days': days,
                'total_events': sum(stat.count for stat in event_stats),
                'event_types': [
                    {
                        'type': stat.action,
                        'description': self.event_types.get(stat.action, stat.action),
                        'count': stat.count
                    } for stat in event_stats
                ],
                'daily_stats': [
                    {
                        'date': stat.date.isoformat(),
                        'count': stat.count
                    } for stat in daily_stats
                ],
                'top_users': [
                    {
                        'user_id': stat.user_id,
                        'username': stat.username,
                        'count': stat.count
                    } for stat in user_stats
                ]
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"이벤트 요약 조회 실패: {e}")
            return None

# 인스턴스 생성
notification_manager = NotificationManager()
event_tracker = EventTracker()

@realtime_notifications_bp.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    """사용자 알림 목록 조회"""
    try:
        # 쿼리 파라미터
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        notification_type = request.args.get('type')
        is_read = request.args.get('is_read')
        
        # 기본 쿼리 (사용자별 알림)
        query = Notification.query.filter(
            or_(
                Notification.user_id == current_user.id,
                Notification.user_id.is_(None)  # 전체 알림
            )
        )
        
        # 필터링
        if notification_type:
            query = query.filter(Notification.type == notification_type)
        if is_read is not None:
            is_read_bool = is_read.lower() == 'true'
            query = query.filter(Notification.is_read == is_read_bool)
        
        # 정렬 (최신순)
        query = query.order_by(Notification.created_at.desc())
        
        # 페이징
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 결과 데이터 구성
        notifications = []
        for notification in pagination.items:
            notification_data = {
                'id': notification.id,
                'title': notification.title,
                'content': notification.content,
                'type': notification.type,
                'severity': notification.severity,
                'is_read': notification.is_read,
                'read_at': notification.read_at.isoformat() if notification.read_at else None,
                'metadata': json.loads(notification.metadata) if notification.metadata else None,
                'created_at': notification.created_at.isoformat()
            }
            notifications.append(notification_data)
        
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
        })
        
    except Exception as e:
        logger.error(f"알림 목록 조회 실패: {e}")
        return jsonify({'error': '알림 목록 조회에 실패했습니다.'}), 500

@realtime_notifications_bp.route('/api/notifications/unread', methods=['GET'])
@login_required
def get_unread_notifications():
    """읽지 않은 알림 조회"""
    try:
        # 읽지 않은 알림만 조회
        unread_notifications = Notification.query.filter(
            and_(
                or_(
                    Notification.user_id == current_user.id,
                    Notification.user_id.is_(None)
                ),
                Notification.is_read == False
            )
        ).order_by(Notification.created_at.desc()).limit(50).all()
        
        notifications = []
        for notification in unread_notifications:
            notification_data = {
                'id': notification.id,
                'title': notification.title,
                'content': notification.content,
                'type': notification.type,
                'severity': notification.severity,
                'metadata': json.loads(notification.metadata) if notification.metadata else None,
                'created_at': notification.created_at.isoformat()
            }
            notifications.append(notification_data)
        
        return jsonify({
            'unread_count': len(notifications),
            'notifications': notifications
        })
        
    except Exception as e:
        logger.error(f"읽지 않은 알림 조회 실패: {e}")
        return jsonify({'error': '읽지 않은 알림 조회에 실패했습니다.'}), 500

@realtime_notifications_bp.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
@csrf.exempt
def mark_notification_read(notification_id):
    """알림 읽음 처리"""
    try:
        success = notification_manager.mark_as_read(notification_id, current_user.id)
        
        if success:
            return jsonify({'message': '알림이 읽음 처리되었습니다.'})
        else:
            return jsonify({'error': '알림을 찾을 수 없습니다.'}), 404
        
    except Exception as e:
        logger.error(f"알림 읽음 처리 실패: {e}")
        return jsonify({'error': '알림 읽음 처리에 실패했습니다.'}), 500

@realtime_notifications_bp.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
@login_required
@csrf.exempt
def delete_notification(notification_id):
    """알림 삭제"""
    try:
        success = notification_manager.delete_notification(notification_id, current_user.id)
        
        if success:
            return jsonify({'message': '알림이 삭제되었습니다.'})
        else:
            return jsonify({'error': '알림을 찾을 수 없습니다.'}), 404
        
    except Exception as e:
        logger.error(f"알림 삭제 실패: {e}")
        return jsonify({'error': '알림 삭제에 실패했습니다.'}), 500

@realtime_notifications_bp.route('/api/notifications/create', methods=['POST'])
@login_required
@csrf.exempt
def create_notification():
    """알림 생성"""
    try:
        # 권한 확인
        if not current_user.has_permission('notification_management', 'send'):
            return jsonify({'error': '알림 생성 권한이 없습니다.'}), 403
        
        data = request.get_json()
        notification_type = data.get('type')
        title = data.get('title')
        content = data.get('content')
        target_users = data.get('target_users')
        metadata = data.get('metadata')
        
        if not all([notification_type, title, content]):
            return jsonify({'error': '알림 타입, 제목, 내용은 필수입니다.'}), 400
        
        notification = notification_manager.create_notification(
            notification_type, title, content, target_users, metadata
        )
        
        return jsonify({
            'message': '알림이 성공적으로 생성되었습니다.',
            'notification_id': notification.id
        })
        
    except Exception as e:
        logger.error(f"알림 생성 실패: {e}")
        return jsonify({'error': f'알림 생성에 실패했습니다: {str(e)}'}), 500

@realtime_notifications_bp.route('/api/events/summary', methods=['GET'])
@login_required
def get_event_summary():
    """이벤트 요약 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('system_management', 'monitoring'):
            return jsonify({'error': '이벤트 모니터링 권한이 없습니다.'}), 403
        
        days = request.args.get('days', 7, type=int)
        summary = event_tracker.get_event_summary(days)
        
        if summary:
            return jsonify(summary)
        else:
            return jsonify({'error': '이벤트 요약 조회에 실패했습니다.'}), 500
        
    except Exception as e:
        logger.error(f"이벤트 요약 조회 실패: {e}")
        return jsonify({'error': '이벤트 요약 조회에 실패했습니다.'}), 500

@realtime_notifications_bp.route('/api/events/recent', methods=['GET'])
@login_required
def get_recent_events():
    """최근 이벤트 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('system_management', 'monitoring'):
            return jsonify({'error': '이벤트 모니터링 권한이 없습니다.'}), 403
        
        # 쿼리 파라미터
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        event_type = request.args.get('event_type')
        user_id = request.args.get('user_id', type=int)
        
        # 기본 쿼리
        query = db.session.query(ActionLog).join(User)
        
        # 필터링
        if event_type:
            query = query.filter(ActionLog.action == event_type)
        if user_id:
            query = query.filter(ActionLog.user_id == user_id)
        
        # 정렬 (최신순)
        query = query.order_by(ActionLog.created_at.desc())
        
        # 페이징
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 결과 데이터 구성
        events = []
        for event in pagination.items:
            event_data = {
                'id': event.id,
                'action': event.action,
                'description': event_tracker.event_types.get(event.action, event.action),
                'message': event.message,
                'user_id': event.user_id,
                'username': event.user.username if event.user else None,
                'ip_address': event.ip_address,
                'metadata': json.loads(event.metadata) if event.metadata else None,
                'created_at': event.created_at.isoformat()
            }
            events.append(event_data)
        
        return jsonify({
            'events': events,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"최근 이벤트 조회 실패: {e}")
        return jsonify({'error': '최근 이벤트 조회에 실패했습니다.'}), 500

@realtime_notifications_bp.route('/api/events/track', methods=['POST'])
@login_required
@csrf.exempt
def track_event():
    """이벤트 추적"""
    try:
        data = request.get_json()
        event_type = data.get('event_type')
        details = data.get('details')
        metadata = data.get('metadata')
        
        if not event_type:
            return jsonify({'error': '이벤트 타입은 필수입니다.'}), 400
        
        action_log = event_tracker.track_event(
            event_type, current_user.id, details, metadata
        )
        
        return jsonify({
            'message': '이벤트가 추적되었습니다.',
            'event_id': action_log.id
        })
        
    except Exception as e:
        logger.error(f"이벤트 추적 실패: {e}")
        return jsonify({'error': f'이벤트 추적에 실패했습니다: {str(e)}'}), 500

@realtime_notifications_bp.route('/api/notifications/cleanup', methods=['POST'])
@login_required
@csrf.exempt
def cleanup_notifications():
    """만료된 알림 정리"""
    try:
        # 권한 확인
        if not current_user.has_permission('notification_management', 'delete'):
            return jsonify({'error': '알림 관리 권한이 없습니다.'}), 403
        
        deleted_count = notification_manager.cleanup_expired_notifications()
        
        return jsonify({
            'message': f'만료된 알림 {deleted_count}개가 정리되었습니다.',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        logger.error(f"알림 정리 실패: {e}")
        return jsonify({'error': '알림 정리에 실패했습니다.'}), 500

@realtime_notifications_bp.route('/api/notifications/stats', methods=['GET'])
@login_required
def get_notification_stats():
    """알림 통계 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('notification_management', 'view'):
            return jsonify({'error': '알림 관리 권한이 없습니다.'}), 403
        
        # 전체 통계
        total_notifications = Notification.query.count()
        unread_notifications = Notification.query.filter_by(is_read=False).count()
        
        # 타입별 통계
        type_stats = db.session.query(
            Notification.type,
            func.count(Notification.id).label('count')
        ).group_by(Notification.type).all()
        
        # 심각도별 통계
        severity_stats = db.session.query(
            Notification.severity,
            func.count(Notification.id).label('count')
        ).group_by(Notification.severity).all()
        
        # 최근 24시간 통계
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_notifications = Notification.query.filter(
            Notification.created_at >= yesterday
        ).count()
        
        stats = {
            'total': total_notifications,
            'unread': unread_notifications,
            'recent_24h': recent_notifications,
            'type_stats': [
                {
                    'type': stat.type,
                    'count': stat.count
                } for stat in type_stats
            ],
            'severity_stats': [
                {
                    'severity': stat.severity,
                    'count': stat.count
                } for stat in severity_stats
            ]
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"알림 통계 조회 실패: {e}")
        return jsonify({'error': '알림 통계 조회에 실패했습니다.'}), 500 