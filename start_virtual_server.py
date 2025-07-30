#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
가상 서버용 애플리케이션 시작 스크립트
Redis 없이도 안정적으로 작동하도록 최적화됨
"""

import os
import sys
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 가상 서버 환경변수 로드
from dotenv import load_dotenv
load_dotenv('config/virtual_server.env')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_virtual_server_environment():
    """가상 서버 환경 설정"""
    logger.info("🚀 가상 서버 환경 설정 중...")
    
    # 필요한 디렉토리 생성
    os.makedirs('instance', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # 가상 서버 모드 활성화
    os.environ['VIRTUAL_SERVER_MODE'] = 'true'
    os.environ['DISABLE_REDIS'] = 'true'
    
    logger.info("✅ 가상 서버 환경 설정 완료")

def initialize_cache_fallback():
    """캐시 Fallback 시스템 초기화"""
    try:
        from config.cache_fallback import init_cache_system
        init_cache_system()
        logger.info("✅ 캐시 시스템 초기화 완료 (메모리 캐시 모드)")
    except Exception as e:
        logger.warning(f"⚠️ 캐시 시스템 초기화 실패: {e}")

def main():
    """메인 실행 함수"""
    try:
        logger.info("🌐 가상 서버 모드로 애플리케이션 시작")
        
        # 가상 서버 환경 설정
        setup_virtual_server_environment()
        
        # 캐시 시스템 초기화
        initialize_cache_fallback()
        
        # Flask 애플리케이션 import 및 실행
        from app import app, socketio
        
        logger.info("📡 서버 시작:")
        logger.info(f"   - 백엔드: http://0.0.0.0:5000")
        logger.info(f"   - 프론트엔드: http://0.0.0.0:3000 (별도 실행 필요)")
        logger.info("   - 가상 서버 최적화 모드 활성화")
        
        # SocketIO 서버 실행
        if os.getenv('WEBSOCKET_ENABLED', 'true').lower() == 'true':
            socketio.run(
                app,
                debug=True,
                host="0.0.0.0",
                port=5000,
                allow_unsafe_werkzeug=True
            )
        else:
            # 일반 Flask 서버 실행
            app.run(
                debug=True,
                host="0.0.0.0",
                port=5000
            )
            
    except Exception as e:
        logger.error(f"❌ 서버 시작 실패: {e}")
        raise

if __name__ == "__main__":
    main()