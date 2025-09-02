#!/usr/bin/env python3
"""
🚀 CQRS 라이트 아키텍처 메인 Flask 앱

멱등성 키, 이벤트 시스템, 테넌트 스코프 검증 등을 포함한 통합 API 서버
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
import os
from datetime import datetime, timezone

# 확장 모듈들
from extensions import db
from models.idempotency import IdempotencyKey
from models.event_log import EventLog
from utils.idempotency import require_idempotency_key
from utils.events import emit_event

# API 블루프린트들
from mobile import mobile_bp
from uploads import uploads_bp

def create_app():
    """Flask 앱 생성"""
    app = Flask(__name__)
    
    # 기본 설정
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///test.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # CORS 설정
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 데이터베이스 초기화
    db.init_app(app)
    
    # Socket.IO 초기화
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # 블루프린트 등록
    app.register_blueprint(mobile_bp)
    app.register_blueprint(uploads_bp)
    
    # 헬스 체크 엔드포인트
    @app.route('/health')
    def health_check():
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0"
        })
    
    # 루트 엔드포인트
    @app.route('/')
    def root():
        return jsonify({
            "message": "CQRS Lite Architecture API Server",
            "version": "1.0.0",
            "endpoints": {
                "health": "/health",
                "mobile_api": "/api/mobile/*",
                "uploads_api": "/api/uploads/*"
            }
        })
    
    # 에러 핸들러
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500
    
    return app

def init_db():
    """데이터베이스 초기화"""
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✅ 데이터베이스 테이블 생성 완료")

if __name__ == '__main__':
    app = create_app()
    
    # 데이터베이스 초기화
    init_db()
    
    # 개발 서버 시작
    print("🚀 CQRS Lite Architecture API Server 시작 중...")
    print("📍 서버 주소: http://localhost:5000")
    print("🔌 Socket.IO 활성화됨")
    
    socketio = SocketIO(app, cors_allowed_origins="*")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
