#!/usr/bin/env python3
"""
WebSocket 데이터 동기화 서버 실행 스크립트
프로젝트 루트에서 실행하여 모듈 import 문제를 해결합니다.
"""

import os
import sys
import asyncio
import logging
from websocket.data_sync_server import create_websocket_server

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.ConsoleHandler(),
        logging.FileHandler('logs/websocket_server.log', encoding='utf-8')
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
    print("🚀 데이터 동기화 WebSocket 서버")
    print("실시간 데이터 동기화를 위한 WebSocket 서버를 시작합니다.")
    print("=" * 60)
    print()
    
    # logs 디렉토리 생성 (없는 경우)
    os.makedirs('logs', exist_ok=True)
    
    main()