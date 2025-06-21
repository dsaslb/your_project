#!/usr/bin/env python3
"""환경별 로깅 설정 테스트 스크립트"""

import os
import sys

def test_logging_config():
    """환경별 로깅 설정 테스트"""
    print("=== 환경별 로깅 설정 테스트 ===")
    
    # 개발 환경 테스트
    print("\n1. 개발 환경 테스트:")
    os.environ['FLASK_ENV'] = 'development'
    try:
        from config import config_by_name
        config = config_by_name['development']()
        print(f"   로그 레벨: {config.LOG_LEVEL}")
        print(f"   로그 파일: {config.LOG_FILE}")
        print(f"   DEBUG 모드: {config.DEBUG}")
    except Exception as e:
        print(f"   오류: {e}")
    
    # 운영 환경 테스트
    print("\n2. 운영 환경 테스트:")
    os.environ['FLASK_ENV'] = 'production'
    try:
        from config import config_by_name
        config = config_by_name['production']()
        print(f"   로그 레벨: {config.LOG_LEVEL}")
        print(f"   로그 파일: {config.LOG_FILE}")
        print(f"   DEBUG 모드: {config.DEBUG}")
    except Exception as e:
        print(f"   오류: {e}")
    
    # 테스트 환경 테스트
    print("\n3. 테스트 환경 테스트:")
    os.environ['FLASK_ENV'] = 'test'
    try:
        from config import config_by_name
        config = config_by_name['test']()
        print(f"   로그 레벨: {config.LOG_LEVEL}")
        print(f"   로그 파일: {config.LOG_FILE}")
        print(f"   DEBUG 모드: {config.DEBUG}")
    except Exception as e:
        print(f"   오류: {e}")

if __name__ == '__main__':
    test_logging_config() 