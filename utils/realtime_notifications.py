"""
실시간 알림 시스템
WebSocket 기반 실시간 알림, 푸시 알림, 이메일 알림
"""

import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
from flask import Flask, request, current_app
from flask_socketio import SocketIO, emit, join_room, leave_room
from extensions import db, cache
from models_main import User, Notification

logger = logging.getLogger(__name__)


class RealtimeNotificationManager:
    """실시간 알림 관리자"""
    
    def __init__(self, app: Flask = None, socketio: SocketIO = None):
        self.app = app
        self.socketio = socketio
        self.connected_users: Dict[int, Set[str]] = {}  # user_id -> session_ids
        self.user_rooms: Dict[int, Set[str]] = {}  # user_id -> room_names
        self.notification_queue = []
        
        if app and socketio:
            self.init_app(app, socketio)
    
    def init_app(self, app: Flask, socketio: SocketIO):
        """Flask 앱에 실시간 알림 설정"""
        self.app = app
        self.socketio = socketio
        
        # WebSocket 이벤트 핸들러 등록
        self._register_socket_handlers()
        
        # 백그라운드 작업 시작
        self._start_background_tasks()
        
        logger.info("실시간 알림 시스템 초기화 완료")
    
    def _register_socket_handlers(self):
        """WebSocket 이벤트 핸들러 등록"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """클라이언트 연결"""
            logger.info(f"클라이언트 연결: {request.sid}")
            emit('connected', {'message': '연결되었습니다.'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """클라이언트 연결 해제"""
            user_id = self._get_user_id_from_session(request.sid)
            if user_id:
                self._remove_user_session(user_id, request.sid)
            logger.info(f"클라이언트 연결 해제: {request.sid}")
        
        @self.socketio.on('authenticate')
        def handle_authenticate(data):
            """사용자 인증"""
            try:
                user_id = data.get('user_id')
                token = data.get('token')
                
                if self._validate_token(user_id, token):
                    self._add_user_session(user_id, request.sid)
                    join_room(f"user_{user_id}")
                    
                    # 사용자별 룸에 참가
                    user = User.query.get(user_id)
                    if user:
                        self._join_user_rooms(user)
                    
                    emit('authenticated', {
                        'success': True,
                        'message': '인증되었습니다.',
                        'user_id': user_id
                    })
                    
                    # 미확인 알림 전송
                    self._send_unread_notifications(user_id)
                else:
                    emit('authenticated', {
                        'success': False,
                        'message': '인증에 실패했습니다.'
                    })
                    
            except Exception as e:
                logger.error(f"인증 처리 실패: {e}")
                emit('authenticated', {
                    'success': False,
                    'message': '인증 처리 중 오류가 발생했습니다.'
                })
        
        @self.socketio.on('join_room')
        def handle_join_room(data):
            """룸 참가"""
            room = data.get('room')
            user_id = self._get_user_id_from_session(request.sid)
            
            if room and user_id:
                join_room(room)
                if user_id not in self.user_rooms:
                    self.user_rooms[user_id] = set()
                self.user_rooms[user_id].add(room)
                
                emit('room_joined', {
                    'room': room,
                    'message': f'{room} 룸에 참가했습니다.'
                })
        
        @self.socketio.on('leave_room')
        def handle_leave_room(data):
            """룸 나가기"""
            room = data.get('room')
            user_id = self._get_user_id_from_session(request.sid)
            
            if room and user_id:
                leave_room(room)
                if user_id in self.user_rooms:
                    self.user_rooms[user_id].discard(room)
                
                emit('room_left', {
                    'room': room,
                    'message': f'{room} 룸을 나갔습니다.'
                })
        
        @self.socketio.on('mark_notification_read')
        def handle_mark_notification_read(data):
            """알림 읽음 표시"""
            notification_id = data.get('notification_id')
            user_id = self._get_user_id_from_session(request.sid)
            
            if notification_id and user_id:
                self._mark_notification_read(notification_id, user_id)
                emit('notification_marked_read', {
                    'notification_id': notification_id,
                    'success': True
                })
    
    def _add_user_session(self, user_id: int, session_id: str):
        """사용자 세션 추가"""
        if user_id not in self.connected_users:
            self.connected_users[user_id] = set()
        self.connected_users[user_id].add(session_id)
    
    def _remove_user_session(self, user_id: int, session_id: str):
        """사용자 세션 제거"""
        if user_id in self.connected_users:
            self.connected_users[user_id].discard(session_id)
            if not self.connected_users[user_id]:
                del self.connected_users[user_id]
    
    def _get_user_id_from_session(self, session_id: str) -> Optional[int]:
        """세션 ID로 사용자 ID 조회"""
        for user_id, sessions in self.connected_users.items():
            if session_id in sessions:
                return user_id
        return None
    
    def _validate_token(self, user_id: int, token: str) -> bool:
        """토큰 검증"""
        try:
            # JWT 토큰 검증 로직
            import jwt
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            return payload.get('user_id') == user_id
        except Exception as e:
            logger.error(f"토큰 검증 실패: {e}")
            return False
    
    def _join_user_rooms(self, user: User):
        """사용자별 룸 참가"""
        # 사용자 개인 룸
        join_room(f"user_{user.id}")
        
        # 브랜드 룸
        if user.brand_id:
            join_room(f"brand_{user.brand_id}")
        
        # 매장 룸
        if user.branch_id:
            join_room(f"branch_{user.branch_id}")
        
        # 역할별 룸
        join_room(f"role_{user.role}")
        
        # 업종 룸
        if user.industry_id:
            join_room(f"industry_{user.industry_id}")
    
    def send_notification(self, user_id: int, notification_data: Dict[str, Any]):
        """실시간 알림 전송"""
        try:
            # 데이터베이스에 알림 저장
            notification = Notification(
                user_id=user_id,
                title=notification_data.get('title', ''),
                content=notification_data.get('content', ''),
                type=notification_data.get('type', 'info'),
                data=notification_data.get('data', {}),
                is_read=False
            )
            db.session.add(notification)
            db.session.commit()
            
            # 실시간 전송
            if user_id in self.connected_users:
                notification_payload = {
                    'id': notification.id,
                    'title': notification.title,
                    'content': notification.content,
                    'type': notification.type,
                    'data': notification.data,
                    'created_at': notification.created_at.isoformat(),
                    'is_read': notification.is_read
                }
                
                # 사용자에게 직접 전송
                self.socketio.emit('new_notification', notification_payload, room=f"user_{user_id}")
                
                logger.info(f"실시간 알림 전송: user_{user_id} - {notification.title}")
            
            return notification.id
            
        except Exception as e:
            logger.error(f"알림 전송 실패: {e}")
            db.session.rollback()
            return None
    
    def send_broadcast_notification(self, room: str, notification_data: Dict[str, Any]):
        """브로드캐스트 알림 전송"""
        try:
            notification_payload = {
                'title': notification_data.get('title', ''),
                'content': notification_data.get('content', ''),
                'type': notification_data.get('type', 'info'),
                'data': notification_data.get('data', {}),
                'created_at': datetime.utcnow().isoformat(),
                'is_broadcast': True
            }
            
            self.socketio.emit('broadcast_notification', notification_payload, room=room)
            
            logger.info(f"브로드캐스트 알림 전송: {room} - {notification_data.get('title')}")
            
        except Exception as e:
            logger.error(f"브로드캐스트 알림 전송 실패: {e}")
    
    def send_system_notification(self, notification_data: Dict[str, Any], 
                               target_users: List[int] = None):
        """시스템 알림 전송"""
        try:
            if target_users:
                # 특정 사용자들에게 전송
                for user_id in target_users:
                    self.send_notification(user_id, notification_data)
            else:
                # 모든 연결된 사용자에게 전송
                notification_payload = {
                    'title': notification_data.get('title', ''),
                    'content': notification_data.get('content', ''),
                    'type': notification_data.get('type', 'system'),
                    'data': notification_data.get('data', {}),
                    'created_at': datetime.utcnow().isoformat(),
                    'is_system': True
                }
                
                self.socketio.emit('system_notification', notification_payload)
            
            logger.info(f"시스템 알림 전송: {notification_data.get('title')}")
            
        except Exception as e:
            logger.error(f"시스템 알림 전송 실패: {e}")
    
    def _send_unread_notifications(self, user_id: int):
        """미확인 알림 전송"""
        try:
            unread_notifications = Notification.query.filter_by(
                user_id=user_id, 
                is_read=False
            ).order_by(Notification.created_at.desc()).limit(10).all()
            
            for notification in unread_notifications:
                notification_payload = {
                    'id': notification.id,
                    'title': notification.title,
                    'content': notification.content,
                    'type': notification.type,
                    'data': notification.data,
                    'created_at': notification.created_at.isoformat(),
                    'is_read': notification.is_read
                }
                
                self.socketio.emit('unread_notification', notification_payload, 
                                 room=f"user_{user_id}")
            
            logger.info(f"미확인 알림 전송: user_{user_id} - {len(unread_notifications)}개")
            
        except Exception as e:
            logger.error(f"미확인 알림 전송 실패: {e}")
    
    def _mark_notification_read(self, notification_id: int, user_id: int):
        """알림 읽음 표시"""
        try:
            notification = Notification.query.filter_by(
                id=notification_id, 
                user_id=user_id
            ).first()
            
            if notification:
                notification.is_read = True
                notification.read_at = datetime.utcnow()
                db.session.commit()
                
                logger.info(f"알림 읽음 표시: {notification_id}")
            
        except Exception as e:
            logger.error(f"알림 읽음 표시 실패: {e}")
            db.session.rollback()
    
    def _start_background_tasks(self):
        """백그라운드 작업 시작"""
        def cleanup_old_notifications():
            """오래된 알림 정리"""
            try:
                cutoff_date = datetime.utcnow() - timedelta(days=30)
                deleted_count = Notification.query.filter(
                    Notification.created_at < cutoff_date,
                    Notification.is_read == True
                ).delete()
                
                db.session.commit()
                
                if deleted_count > 0:
                    logger.info(f"오래된 알림 정리: {deleted_count}개 삭제")
                    
            except Exception as e:
                logger.error(f"알림 정리 실패: {e}")
                db.session.rollback()
        
        # 주기적 정리 작업 (매일 새벽 2시)
        import threading
        import time
        
        def background_cleanup():
            while True:
                now = datetime.utcnow()
                if now.hour == 2 and now.minute == 0:
                    cleanup_old_notifications()
                time.sleep(60)  # 1분마다 체크
        
        cleanup_thread = threading.Thread(target=background_cleanup, daemon=True)
        cleanup_thread.start()
    
    def get_connected_users_count(self) -> int:
        """연결된 사용자 수 조회"""
        return len(self.connected_users)
    
    def get_user_notifications(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """사용자 알림 목록 조회"""
        try:
            notifications = Notification.query.filter_by(user_id=user_id)\
                .order_by(Notification.created_at.desc())\
                .limit(limit).all()
            
            return [{
                'id': n.id,
                'title': n.title,
                'content': n.content,
                'type': n.type,
                'data': n.data,
                'created_at': n.created_at.isoformat(),
                'is_read': n.is_read,
                'read_at': n.read_at.isoformat() if n.read_at else None
            } for n in notifications]
            
        except Exception as e:
            logger.error(f"사용자 알림 조회 실패: {e}")
            return []


# 전역 실시간 알림 관리자
realtime_notification_manager = RealtimeNotificationManager()


def send_notification_to_user(user_id: int, title: str, content: str, 
                            notification_type: str = 'info', data: Dict = None):
    """사용자에게 알림 전송"""
    notification_data = {
        'title': title,
        'content': content,
        'type': notification_type,
        'data': data or {}
    }
    
    return realtime_notification_manager.send_notification(user_id, notification_data)


def send_broadcast_notification(room: str, title: str, content: str, 
                              notification_type: str = 'info', data: Dict = None):
    """브로드캐스트 알림 전송"""
    notification_data = {
        'title': title,
        'content': content,
        'type': notification_type,
        'data': data or {}
    }
    
    realtime_notification_manager.send_broadcast_notification(room, notification_data)


def send_system_notification(title: str, content: str, target_users: List[int] = None,
                           notification_type: str = 'system', data: Dict = None):
    """시스템 알림 전송"""
    notification_data = {
        'title': title,
        'content': content,
        'type': notification_type,
        'data': data or {}
    }
    
    realtime_notification_manager.send_system_notification(notification_data, target_users) 