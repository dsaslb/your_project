#!/usr/bin/env python3
"""
WebSocket 서버 실행 스크립트 (websocket 디렉토리용)
이 파일은 websocket 디렉토리에서 직접 실행할 수 있도록 만들어졌습니다.
"""

import os
import sys
import asyncio
import logging

# 상위 디렉토리를 Python path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from data_sync_server import create_websocket_server

# 로깅 설정
log_dir = os.path.join(parent_dir, 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.ConsoleHandler(),
        logging.FileHandler(os.path.join(log_dir, 'websocket_server.log'), encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """WebSocket 서버 메인 실행 함수"""
    try:
        # 환경 변수에서 설정 읽기
        host = os.getenv('WS_HOST', 'localhost')
        port = int(os.getenv('WS_PORT', 8765))
        secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
        
        logger.info(f"WebSocket 서버 시작: {host}:{port}")
        logger.info(f"환경: {'개발' if os.getenv('NODE_ENV') != 'production' else '운영'}")
        logger.info(f"실행 위치: {current_dir}")
        
        # WebSocket 서버 생성 및 시작
        server = create_websocket_server(host, port, secret_key)
        
        # 비동기 서버 실행
        asyncio.run(server.start_server())
        
    except KeyboardInterrupt:
        logger.info("사용자에 의해 서버가 중단되었습니다")
    except Exception as e:
        logger.error(f"서버 실행 오류: {e}")
        sys.exit(1)

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 데이터 동기화 WebSocket 서버 (websocket 디렉토리)")
    print("실시간 데이터 동기화를 위한 WebSocket 서버를 시작합니다.")
    print(f"실행 위치: {current_dir}")
    print(f"프로젝트 루트: {parent_dir}")
    print("=" * 60)
    print()
    
    main()