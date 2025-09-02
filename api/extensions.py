#!/usr/bin/env python3
"""
🔧 Flask 확장 모듈들

데이터베이스, Socket.IO 등의 확장 기능을 초기화
"""

from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

# SQLAlchemy 데이터베이스 인스턴스
db = SQLAlchemy()

# Socket.IO 인스턴스
socketio = SocketIO()

def init_extensions(app):
    """확장 모듈들 초기화"""
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
