"""
Outbox 워커 시작 스크립트
"""
import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from extensions import db, socketio
from workers.outbox_worker import init_worker

def create_app():
    """Flask 앱 생성"""
    app = Flask(__name__)
    
    # 기본 설정
    app.config['SECRET_KEY'] = 'dev-secret-key'
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'your_program_dev.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 확장 모듈 초기화
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    return app

def start_worker():
    """Outbox 워커 시작"""
    app = create_app()
    
    with app.app_context():
        # 워커 초기화 및 시작
        worker = init_worker(app, interval=1.0, batch_size=100)
        worker.start()
        
        print("🚀 Outbox 워커가 시작되었습니다")
        print("📊 설정:")
        print(f"  - 처리 간격: {worker.interval}초")
        print(f"  - 배치 크기: {worker.batch_size}개")
        print("🔄 워커가 실행 중입니다. Ctrl+C로 중지하세요.")
        
        try:
            # 메인 스레드에서 대기
            import time
            while worker.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️ 워커 중지 중...")
            worker.stop()
            print("✅ 워커가 안전하게 중지되었습니다")

if __name__ == '__main__':
    start_worker()
