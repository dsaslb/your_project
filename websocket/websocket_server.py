"""
WebSocket 서버 초기화 및 설정
Flask-SocketIO 서버 설정 및 이벤트 처리
"""

import logging
from flask import Flask
from flask_socketio import SocketIO
import eventlet

from websocket.real_time_notifications import RealTimeNotificationManager, notification_manager

logger = logging.getLogger(__name__)

def create_websocket_server(app: Flask) -> SocketIO:
    """WebSocket 서버 생성 및 초기화"""
    
    # Eventlet 설정
    eventlet.monkey_patch()
    
    # SocketIO 서버 생성
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode='eventlet',
        logger=True,
        engineio_logger=True,
        ping_timeout=60,
        ping_interval=25
    )
    
    # 실시간 알림 관리자 초기화
    global notification_manager
    notification_manager = RealTimeNotificationManager(socketio)
    
    logger.info("WebSocket 서버 초기화 완료")
    
    return socketio

def get_notification_manager() -> RealTimeNotificationManager:
    """알림 관리자 인스턴스 반환"""
    return notification_manager

def broadcast_notification(notification_type: str, message: str, data: dict = None, 
                          target_rooms: list = None, target_users: list = None):
    """알림 브로드캐스트 헬퍼 함수"""
    if notification_manager:
        return notification_manager.send_notification(
            notification_type, message, data, target_rooms, target_users
        )
    else:
        logger.warning("알림 관리자가 초기화되지 않았습니다.")
        return None 