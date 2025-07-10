from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import json
import threading
import time
from datetime import datetime
import logging
from typing import Any, Dict, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# SocketIO 설정
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 연결된 클라이언트 관리
connected_clients = {}
notification_history = []

@app.route('/')
def index():
    return jsonify({"message": "WebSocket Server Running", "status": "ok"})

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """알림 히스토리 조회"""
    return jsonify(notification_history)

@app.route('/api/notifications', methods=['POST'])
def send_notification():
    """새 알림 전송"""
    data = request.json or {}
    notification = {
        'id': len(notification_history) + 1,
        'title': data.get('title', '알림'),
        'message': data.get('message', ''),
        'type': data.get('type', 'info'),
        'category': data.get('category', 'general'),
        'timestamp': datetime.now().isoformat(),
        'actionUrl': data.get('actionUrl'),
    }
    
    notification_history.append(notification)
    
    # 모든 연결된 클라이언트에게 실시간 전송
    socketio.emit('notification', notification, broadcast=True)  # type: ignore
    
    logger.info(f"알림 전송: {notification['title']}")
    return jsonify({"success": True, "notification": notification})

# WebSocket 이벤트 핸들러
@socketio.on('connect')
def handle_connect():
    """클라이언트 연결"""
    client_id = request.sid  # type: ignore
    connected_clients[client_id] = {
        'id': client_id,
        'connected_at': datetime.now().isoformat(),
        'user_id': None,
        'role': None
    }
    
    logger.info(f"클라이언트 연결: {client_id}")
    emit('connected', {'client_id': client_id, 'message': '연결되었습니다'})

@socketio.on('disconnect')
def handle_disconnect():
    """클라이언트 연결 해제"""
    client_id = request.sid  # type: ignore
    if client_id in connected_clients:
        del connected_clients[client_id]
    
    logger.info(f"클라이언트 연결 해제: {client_id}")

@socketio.on('join_room')
def handle_join_room(data):
    """특정 룸에 참가 (예: 매장별, 역할별)"""
    room = data.get('room')
    client_id = request.sid  # type: ignore
    
    if room:
        join_room(room)
        if client_id in connected_clients:
            connected_clients[client_id]['room'] = room
        
        logger.info(f"클라이언트 {client_id}가 룸 {room}에 참가")
        emit('room_joined', {'room': room}, room=room)  # type: ignore

@socketio.on('leave_room')
def handle_leave_room(data):
    """룸에서 나가기"""
    room = data.get('room')
    client_id = request.sid  # type: ignore
    
    if room:
        leave_room(room)
        if client_id in connected_clients:
            connected_clients[client_id]['room'] = None
        
        logger.info(f"클라이언트 {client_id}가 룸 {room}에서 나감")

@socketio.on('send_notification')
def handle_send_notification(data):
    """클라이언트에서 알림 전송 요청"""
    notification = {
        'id': len(notification_history) + 1,
        'title': data.get('title', '알림'),
        'message': data.get('message', ''),
        'type': data.get('type', 'info'),
        'category': data.get('category', 'general'),
        'timestamp': datetime.now().isoformat(),
        'actionUrl': data.get('actionUrl'),
    }
    
    notification_history.append(notification)
    
    # 특정 룸이나 모든 클라이언트에게 전송
    room = data.get('room')
    if room:
        socketio.emit('notification', notification, room=room)  # type: ignore
    else:
        socketio.emit('notification', notification, broadcast=True)  # type: ignore
    
    logger.info(f"클라이언트 알림 전송: {notification['title']}")

# 주기적인 시스템 알림 (예시)
def send_system_notifications():
    """시스템 상태 알림 전송"""
    while True:
        try:
            # 연결된 클라이언트 수 알림
            client_count = len(connected_clients)
            if client_count > 0:
                system_notification = {
                    'id': len(notification_history) + 1,
                    'title': '시스템 상태',
                    'message': f'현재 {client_count}명의 사용자가 연결되어 있습니다.',
                    'type': 'info',
                    'category': 'system',
                    'timestamp': datetime.now().isoformat(),
                }
                
                notification_history.append(system_notification)
                socketio.emit('notification', system_notification, broadcast=True)  # type: ignore
                
                logger.info(f"시스템 알림 전송: {client_count}명 연결")
            
            time.sleep(300)  # 5분마다
            
        except Exception as e:
            logger.error(f"시스템 알림 오류: {e}")
            time.sleep(60)

# 백그라운드 스레드로 시스템 알림 시작
def start_system_notifications():
    """시스템 알림 스레드 시작"""
    thread = threading.Thread(target=send_system_notifications, daemon=True)
    thread.start()

if __name__ == '__main__':
    logger.info("WebSocket 서버 시작...")
    start_system_notifications()
    
    # 개발 모드에서 실행
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True) 