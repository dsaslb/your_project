#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 Socket.IO 테스트 서버
"""

from flask import Flask
from flask_socketio import SocketIO, emit
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask 앱 생성
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key'

# Socket.IO 초기화
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Socket.IO 이벤트 핸들러
@socketio.on('connect')
def handle_connect():
    logger.info(f"클라이언트 연결됨: {request.sid}")
    emit('welcome', {'message': 'Socket.IO 서버에 연결되었습니다!', 'sid': request.sid})
    return {'status': 'connected', 'sid': request.sid}

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"클라이언트 연결 해제됨: {request.sid}")

@socketio.on('message')
def handle_message(data):
    logger.info(f"메시지 수신: {data}")
    emit('response', {'message': f'서버에서 응답: {data}'}, broadcast=True)

@socketio.on('po:created')
def handle_po_created(data):
    logger.info(f"발주 생성 이벤트 수신: {data}")
    emit('po:created', data, broadcast=True)

@socketio.on('po:status')
def handle_po_status(data):
    logger.info(f"발주 상태 변경 이벤트 수신: {data}")
    emit('po:status', data, broadcast=True)

# 기본 라우트
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Socket.IO 테스트 서버</title>
        <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    </head>
    <body>
        <h1>Socket.IO 테스트 서버</h1>
        <p>이 페이지는 Socket.IO 서버가 정상 작동하는지 테스트합니다.</p>
        <div id="status">연결 상태: 대기 중...</div>
        <div id="messages"></div>
        
        <script>
            const socket = io();
            
            socket.on('connect', () => {
                document.getElementById('status').textContent = '연결 상태: 연결됨';
                console.log('Socket.IO 연결 성공!', socket.id);
            });
            
            socket.on('disconnect', () => {
                document.getElementById('status').textContent = '연결 상태: 연결 해제됨';
                console.log('Socket.IO 연결 해제');
            });
            
            socket.on('welcome', (data) => {
                console.log('서버 환영 메시지:', data);
                addMessage('서버: ' + data.message);
            });
            
            socket.on('response', (data) => {
                addMessage('서버 응답: ' + data.message);
            });
            
            function addMessage(message) {
                const div = document.createElement('div');
                div.textContent = message;
                document.getElementById('messages').appendChild(div);
            }
            
            // 테스트 메시지 전송
            setTimeout(() => {
                if (socket.connected) {
                    socket.emit('message', '테스트 메시지');
                }
            }, 2000);
        </script>
    </body>
    </html>
    '''

@app.route('/favicon.ico')
def favicon():
    return '', 204  # No Content

if __name__ == '__main__':
    logger.info("Socket.IO 테스트 서버 시작 중...")
    logger.info("http://localhost:5001 에서 접속 가능")
    
    # Socket.IO 서버로 실행
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True)
