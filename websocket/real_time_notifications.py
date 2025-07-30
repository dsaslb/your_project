"""
WebSocket 기반 실시간 알림 시스템
Flask-SocketIO를 사용한 실시간 통신 구현
"""

import logging
import json
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
import eventlet

logger = logging.getLogger(__name__)

class RealTimeNotificationManager:
    """실시간 알림 관리자"""
    
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.connected_clients = {}  # {client_id: {'user_id': str, 'rooms': set}}
        self.notification_history = []  # 최근 알림 히스토리
        self.max_history = 1000
        
        # 알림 타입별 설정
        self.notification_types = {
            'system_alert': {
                'priority': 'high',
                'ttl': 3600,  # 1시간
                'channels': ['dashboard', 'admin']
            },
            'ai_prediction': {
                'priority': 'medium',
                'ttl': 1800,  # 30분
                'channels': ['dashboard', 'analytics']
            },
            'performance_alert': {
                'priority': 'high',
                'ttl': 1800,
                'channels': ['dashboard', 'monitoring']
            },
            'user_activity': {
                'priority': 'low',
                'ttl': 600,  # 10분
                'channels': ['admin']
            },
            'data_update': {
                'priority': 'medium',
                'ttl': 1200,  # 20분
                'channels': ['dashboard']
            }
        }
        
        # WebSocket 이벤트 핸들러 등록
        self._register_event_handlers()
        
        # 백그라운드 작업 시작
        self._start_background_tasks()
    
    def _register_event_handlers(self):
        """WebSocket 이벤트 핸들러 등록"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """클라이언트 연결 처리"""
            client_id = request.sid
            user_id = request.args.get('user_id', 'anonymous')
            
            self.connected_clients[client_id] = {
                'user_id': user_id,
                'rooms': set(),
                'connected_at': datetime.now(),
                'last_activity': datetime.now()
            }
            
            # 기본 룸에 참가
            join_room('general')
            self.connected_clients[client_id]['rooms'].add('general')
            
            # 연결 확인 메시지 전송
            emit('connection_established', {
                'client_id': client_id,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'message': '실시간 알림 시스템에 연결되었습니다.'
            })
            
            # 최근 알림 히스토리 전송
            recent_notifications = self.notification_history[-10:]
            if recent_notifications:
                emit('notification_history', {
                    'notifications': recent_notifications,
                    'timestamp': datetime.now().isoformat()
                })
            
            logger.info(f"클라이언트 연결: {client_id} (사용자: {user_id})")
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """클라이언트 연결 해제 처리"""
            client_id = request.sid
            
            if client_id in self.connected_clients:
                user_id = self.connected_clients[client_id]['user_id']
                del self.connected_clients[client_id]
                logger.info(f"클라이언트 연결 해제: {client_id} (사용자: {user_id})")
        
        @self.socketio.on('join_room')
        def handle_join_room(data):
            """룸 참가 처리"""
            client_id = request.sid
            room = data.get('room')
            
            if not room:
                emit('error', {'message': '룸 이름이 필요합니다.'})
                return
            
            if client_id in self.connected_clients:
                join_room(room)
                self.connected_clients[client_id]['rooms'].add(room)
                
                emit('room_joined', {
                    'room': room,
                    'timestamp': datetime.now().isoformat(),
                    'message': f'룸 {room}에 참가했습니다.'
                })
                
                logger.info(f"클라이언트 {client_id}가 룸 {room}에 참가")
        
        @self.socketio.on('leave_room')
        def handle_leave_room(data):
            """룸 나가기 처리"""
            client_id = request.sid
            room = data.get('room')
            
            if not room:
                emit('error', {'message': '룸 이름이 필요합니다.'})
                return
            
            if client_id in self.connected_clients:
                leave_room(room)
                self.connected_clients[client_id]['rooms'].discard(room)
                
                emit('room_left', {
                    'room': room,
                    'timestamp': datetime.now().isoformat(),
                    'message': f'룸 {room}에서 나갔습니다.'
                })
                
                logger.info(f"클라이언트 {client_id}가 룸 {room}에서 나감")
        
        @self.socketio.on('subscribe_notifications')
        def handle_subscribe_notifications(data):
            """알림 구독 처리"""
            client_id = request.sid
            notification_types = data.get('types', [])
            
            if client_id in self.connected_clients:
                # 각 알림 타입별 룸에 참가
                for notification_type in notification_types:
                    room = f'notifications_{notification_type}'
                    join_room(room)
                    self.connected_clients[client_id]['rooms'].add(room)
                
                emit('subscription_confirmed', {
                    'types': notification_types,
                    'timestamp': datetime.now().isoformat(),
                    'message': f'{len(notification_types)}개 알림 타입을 구독했습니다.'
                })
                
                logger.info(f"클라이언트 {client_id}가 알림 구독: {notification_types}")
        
        @self.socketio.on('unsubscribe_notifications')
        def handle_unsubscribe_notifications(data):
            """알림 구독 해제 처리"""
            client_id = request.sid
            notification_types = data.get('types', [])
            
            if client_id in self.connected_clients:
                # 각 알림 타입별 룸에서 나감
                for notification_type in notification_types:
                    room = f'notifications_{notification_type}'
                    leave_room(room)
                    self.connected_clients[client_id]['rooms'].discard(room)
                
                emit('unsubscription_confirmed', {
                    'types': notification_types,
                    'timestamp': datetime.now().isoformat(),
                    'message': f'{len(notification_types)}개 알림 타입 구독을 해제했습니다.'
                })
                
                logger.info(f"클라이언트 {client_id}가 알림 구독 해제: {notification_types}")
        
        @self.socketio.on('mark_notification_read')
        def handle_mark_notification_read(data):
            """알림 읽음 처리"""
            notification_id = data.get('notification_id')
            
            if notification_id:
                # 알림 히스토리에서 읽음 상태 업데이트
                for notification in self.notification_history:
                    if notification.get('id') == notification_id:
                        notification['read'] = True
                        notification['read_at'] = datetime.now().isoformat()
                        break
                
                emit('notification_marked_read', {
                    'notification_id': notification_id,
                    'timestamp': datetime.now().isoformat()
                })
        
        @self.socketio.on('ping')
        def handle_ping():
            """핑 처리"""
            client_id = request.sid
            
            if client_id in self.connected_clients:
                self.connected_clients[client_id]['last_activity'] = datetime.now()
            
            emit('pong', {
                'timestamp': datetime.now().isoformat()
            })
    
    def _start_background_tasks(self):
        """백그라운드 작업 시작"""
        
        def cleanup_old_notifications():
            """오래된 알림 정리"""
            while True:
                try:
                    current_time = datetime.now()
                    cleaned_count = 0
                    
                    # TTL이 만료된 알림 제거
                    for notification in self.notification_history[:]:
                        created_at = datetime.fromisoformat(notification['created_at'])
                        notification_type = notification.get('type', 'system_alert')
                        ttl = self.notification_types.get(notification_type, {}).get('ttl', 3600)
                        
                        if (current_time - created_at).total_seconds() > ttl:
                            self.notification_history.remove(notification)
                            cleaned_count += 1
                    
                    # 히스토리 크기 제한
                    if len(self.notification_history) > self.max_history:
                        excess = len(self.notification_history) - self.max_history
                        self.notification_history = self.notification_history[excess:]
                        cleaned_count += excess
                    
                    if cleaned_count > 0:
                        logger.info(f"오래된 알림 정리 완료: {cleaned_count}개")
                    
                    time.sleep(300)  # 5분마다 실행
                    
                except Exception as e:
                    logger.error(f"알림 정리 중 오류: {e}")
                    time.sleep(60)
        
        def health_check():
            """연결 상태 확인"""
            while True:
                try:
                    current_time = datetime.now()
                    disconnected_clients = []
                    
                    for client_id, client_info in self.connected_clients.items():
                        last_activity = client_info['last_activity']
                        if (current_time - last_activity).total_seconds() > 300:  # 5분 이상 활동 없음
                            disconnected_clients.append(client_id)
                    
                    if disconnected_clients:
                        logger.info(f"비활성 클라이언트 정리: {len(disconnected_clients)}개")
                    
                    time.sleep(60)  # 1분마다 실행
                    
                except Exception as e:
                    logger.error(f"헬스 체크 중 오류: {e}")
                    time.sleep(30)
        
        # 백그라운드 스레드 시작
        cleanup_thread = threading.Thread(target=cleanup_old_notifications, daemon=True)
        health_thread = threading.Thread(target=health_check, daemon=True)
        
        cleanup_thread.start()
        health_thread.start()
        
        logger.info("백그라운드 작업 시작됨")
    
    def send_notification(self, notification_type: str, message: str, data: Dict[str, Any] = None, 
                         target_rooms: List[str] = None, target_users: List[str] = None):
        """알림 전송"""
        try:
            # 알림 생성
            notification = {
                'id': f"notif_{int(time.time() * 1000)}",
                'type': notification_type,
                'message': message,
                'data': data or {},
                'priority': self.notification_types.get(notification_type, {}).get('priority', 'medium'),
                'created_at': datetime.now().isoformat(),
                'read': False
            }
            
            # 알림 히스토리에 추가
            self.notification_history.append(notification)
            
            # 기본 타겟 룸 설정
            if not target_rooms:
                target_rooms = self.notification_types.get(notification_type, {}).get('channels', ['general'])
            
            # 특정 사용자에게 전송
            if target_users:
                for user_id in target_users:
                    for client_id, client_info in self.connected_clients.items():
                        if client_info['user_id'] == user_id:
                            self.socketio.emit('notification', notification, room=client_id)
            
            # 룸에 브로드캐스트
            for room in target_rooms:
                self.socketio.emit('notification', notification, room=room)
            
            logger.info(f"알림 전송: {notification_type} - {message} (룸: {target_rooms})")
            
            return notification
            
        except Exception as e:
            logger.error(f"알림 전송 실패: {e}")
            return None
    
    def broadcast_system_alert(self, alert_type: str, message: str, severity: str = 'info'):
        """시스템 알림 브로드캐스트"""
        return self.send_notification(
            notification_type='system_alert',
            message=message,
            data={
                'alert_type': alert_type,
                'severity': severity
            },
            target_rooms=['dashboard', 'admin']
        )
    
    def broadcast_ai_prediction(self, model_name: str, prediction: Any, confidence: float = None):
        """AI 예측 결과 브로드캐스트"""
        return self.send_notification(
            notification_type='ai_prediction',
            message=f"AI 모델 '{model_name}' 예측 완료",
            data={
                'model_name': model_name,
                'prediction': prediction,
                'confidence': confidence
            },
            target_rooms=['dashboard', 'analytics']
        )
    
    def broadcast_performance_alert(self, metric: str, value: float, threshold: float, status: str):
        """성능 알림 브로드캐스트"""
        return self.send_notification(
            notification_type='performance_alert',
            message=f"성능 알림: {metric} = {value} (임계값: {threshold})",
            data={
                'metric': metric,
                'value': value,
                'threshold': threshold,
                'status': status
            },
            target_rooms=['dashboard', 'monitoring']
        )
    
    def broadcast_data_update(self, data_type: str, action: str, record_count: int = None):
        """데이터 업데이트 브로드캐스트"""
        return self.send_notification(
            notification_type='data_update',
            message=f"데이터 업데이트: {data_type} {action}",
            data={
                'data_type': data_type,
                'action': action,
                'record_count': record_count
            },
            target_rooms=['dashboard']
        )
    
    def get_connected_clients_info(self) -> Dict[str, Any]:
        """연결된 클라이언트 정보 조회"""
        return {
            'total_clients': len(self.connected_clients),
            'clients_by_room': self._get_clients_by_room(),
            'notification_history_count': len(self.notification_history),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_clients_by_room(self) -> Dict[str, int]:
        """룸별 클라이언트 수 조회"""
        room_counts = {}
        
        for client_info in self.connected_clients.values():
            for room in client_info['rooms']:
                room_counts[room] = room_counts.get(room, 0) + 1
        
        return room_counts

# 전역 인스턴스 (나중에 초기화)
notification_manager = None 