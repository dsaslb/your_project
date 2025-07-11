"""
실시간 알림 시스템
WebSocket 기반 실시간 알림 및 이벤트 브로드캐스팅
"""



import logging
from typing import Dict, List, Set, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """알림 타입"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class NotificationPriority(Enum):
    """알림 우선순위"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class Notification:
    """알림 객체"""
    id: str
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority
    user_id: Optional[str] = None
    group_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    read: bool = False
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        result = asdict(self)
        result['type'] = self.type.value
        result['priority'] = self.priority.value
        result['created_at'] = self.created_at.isoformat() if self.created_at else None
        if self.expires_at:
            result['expires_at'] = self.expires_at.isoformat()
        return result

class NotificationChannel:
    """알림 채널"""
    
    def __init__(self, channel_id: str, name: str, description: str = ""):
        self.channel_id = channel_id
        self.name = name
        self.description = description
        self.subscribers: Set[str] = set()
        self.notifications: List[Notification] = []
        self.max_notifications = 100
    
    def add_subscriber(self, user_id: str) -> bool:
        """구독자 추가"""
        self.subscribers.add(user_id)
        logger.info(f"사용자 {user_id}가 채널 {self.channel_id}에 구독")
        return True
    
    def remove_subscriber(self, user_id: str) -> bool:
        """구독자 제거"""
        if user_id in self.subscribers:
            self.subscribers.remove(user_id)
            logger.info(f"사용자 {user_id}가 채널 {self.channel_id}에서 구독 해제")
            return True
        return False
    
    def broadcast(self, notification: Notification) -> List[str]:
        """채널에 알림 브로드캐스트"""
        # 알림 저장
        self.notifications.append(notification)
        
        # 최대 알림 수 제한
        if len(self.notifications) > self.max_notifications:
            self.notifications = self.notifications[-self.max_notifications:]
        
        # 구독자 목록 반환
        return list(self.subscribers)
    
    def get_notifications(self, user_id: str, limit: int = 50) -> List[Notification]:
        """사용자별 알림 조회"""
        if user_id in self.subscribers:
            return self.notifications[-limit:]
        return []

class RealtimeNotificationManager:
    """실시간 알림 관리자"""
    
    def __init__(self):
        self.channels: Dict[str, NotificationChannel] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> connection_ids
        self.connection_users: Dict[str, str] = {}  # connection_id -> user_id
        self.notification_handlers: Dict[str, Any] = {}
        
        # 기본 채널 생성
        self._create_default_channels()
    
    def _create_default_channels(self):
        """기본 채널 생성"""
        default_channels = [
            ("system", "시스템 알림", "시스템 전반의 알림"),
            ("admin", "관리자 알림", "관리자 전용 알림"),
            ("user", "사용자 알림", "일반 사용자 알림"),
            ("restaurant", "레스토랑 알림", "레스토랑 관련 알림"),
            ("orders", "주문 알림", "주문 관련 알림"),
            ("inventory", "재고 알림", "재고 관련 알림")
        ]
        
        for channel_id, name, description in default_channels:
            self.create_channel(channel_id, name, description)
    
    def create_channel(self, channel_id: str, name: str, description: str = "") -> NotificationChannel:
        """채널 생성"""
        if channel_id in self.channels:
            logger.warning(f"채널 {channel_id}가 이미 존재합니다")
            return self.channels[channel_id]
        
        channel = NotificationChannel(channel_id, name, description)
        self.channels[channel_id] = channel
        logger.info(f"채널 생성: {channel_id} - {name}")
        return channel
    
    def get_channel(self, channel_id: str) -> Optional[NotificationChannel]:
        """채널 조회"""
        return self.channels.get(channel_id)
    
    def subscribe_user(self, user_id: str, channel_id: str) -> bool:
        """사용자를 채널에 구독"""
        channel = self.get_channel(channel_id)
        if not channel:
            logger.error(f"채널 {channel_id}를 찾을 수 없습니다")
            return False
        
        return channel.add_subscriber(user_id)
    
    def unsubscribe_user(self, user_id: str, channel_id: str) -> bool:
        """사용자 구독 해제"""
        channel = self.get_channel(channel_id)
        if not channel:
            return False
        
        return channel.remove_subscriber(user_id)
    
    def register_connection(self, connection_id: str, user_id: str) -> bool:
        """연결 등록"""
        self.connection_users[connection_id] = user_id
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        
        self.user_connections[user_id].add(connection_id)
        logger.info(f"연결 등록: {connection_id} -> {user_id}")
        return True
    
    def unregister_connection(self, connection_id: str) -> bool:
        """연결 해제"""
        user_id = self.connection_users.pop(connection_id, None)
        if user_id:
            if user_id in self.user_connections:
                self.user_connections[user_id].discard(connection_id)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            logger.info(f"연결 해제: {connection_id} -> {user_id}")
            return True
        return False
    
    def send_notification(self, 
                         channel_id: str, 
                         notification: Notification,
                         target_users: Optional[List[str]] = None) -> bool:
        """알림 전송"""
        try:
            channel = self.get_channel(channel_id)
            if not channel:
                logger.error(f"채널 {channel_id}를 찾을 수 없습니다")
                return False
            
            # 특정 사용자에게만 전송
            if target_users:
                subscribers = [user_id for user_id in target_users if user_id in channel.subscribers]
            else:
                # 채널 전체 브로드캐스트
                subscribers = channel.broadcast(notification)
            
            # 실시간 전송
            self._send_to_subscribers(subscribers, notification)
            
            logger.info(f"알림 전송 완료: {channel_id} -> {len(subscribers)}명")
            return True
            
        except Exception as e:
            logger.error(f"알림 전송 실패: {e}")
            return False
    
    def send_direct_notification(self, user_id: str, notification: Notification) -> bool:
        """개별 사용자에게 직접 알림 전송"""
        try:
            # 사용자 연결 확인
            if user_id not in self.user_connections:
                logger.warning(f"사용자 {user_id}의 활성 연결이 없습니다")
                return False
            
            # 직접 전송
            self._send_to_subscribers([user_id], notification)
            
            logger.info(f"직접 알림 전송 완료: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"직접 알림 전송 실패: {e}")
            return False
    
    def _send_to_subscribers(self, user_ids: List[str], notification: Notification):
        """구독자들에게 알림 전송"""
        for user_id in user_ids:
            if user_id in self.user_connections:
                for connection_id in self.user_connections[user_id]:
                    self._send_to_connection(connection_id, notification)
    
    def _send_to_connection(self, connection_id: str, notification: Notification):
        """연결에 알림 전송"""
        try:
            # WebSocket 또는 SSE를 통한 전송
            # 실제 구현에서는 WebSocket 라이브러리 사용
            message = {
                'type': 'notification',
                'data': notification.to_dict()
            }
            
            # 핸들러가 등록되어 있으면 호출
            if connection_id in self.notification_handlers:
                self.notification_handlers[connection_id](message)
            else:
                logger.debug(f"연결 {connection_id}에 대한 핸들러가 없습니다")
                
        except Exception as e:
            logger.error(f"연결 {connection_id}에 알림 전송 실패: {e}")
    
    def register_notification_handler(self, connection_id: str, handler: Any):
        """알림 핸들러 등록"""
        self.notification_handlers[connection_id] = handler
    
    def unregister_notification_handler(self, connection_id: str):
        """알림 핸들러 해제"""
        self.notification_handlers.pop(connection_id, None)
    
    def get_user_notifications(self, user_id: str, channel_id: Optional[str] = None, limit: int = 50) -> List[Notification]:
        """사용자 알림 조회"""
        notifications = []
        
        if channel_id:
            # 특정 채널의 알림만 조회
            channel = self.get_channel(channel_id)
            if channel:
                notifications = channel.get_notifications(user_id, limit)
        else:
            # 모든 채널의 알림 조회
            for channel in self.channels.values():
                channel_notifications = channel.get_notifications(user_id, limit // len(self.channels))
                notifications.extend(channel_notifications)
            
            # 생성 시간순 정렬
            notifications.sort(key=lambda x: x.created_at, reverse=True)
            notifications = notifications[:limit]
        
        return notifications
    
    def mark_as_read(self, user_id: str, notification_id: str) -> bool:
        """알림 읽음 표시"""
        for channel in self.channels.values():
            for notification in channel.notifications:
                if notification.id == notification_id and notification.user_id == user_id:
                    notification.read = True
                    return True
        return False
    
    def cleanup_expired_notifications(self):
        """만료된 알림 정리"""
        current_time = datetime.utcnow()
        
        for channel in self.channels.values():
            expired_notifications = [
                n for n in channel.notifications 
                if n.expires_at and n.expires_at < current_time
            ]
            
            for notification in expired_notifications:
                channel.notifications.remove(notification)
            
            if expired_notifications:
                logger.info(f"채널 {channel.channel_id}에서 {len(expired_notifications)}개 만료 알림 정리")

# 전역 알림 관리자 인스턴스
notification_manager = RealtimeNotificationManager() 