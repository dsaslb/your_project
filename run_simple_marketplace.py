#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 모듈 마켓플레이스 실행 스크립트
"""

import os
import sys
import subprocess

def check_dependencies():
    """필요한 패키지가 설치되어 있는지 확인"""
    required_packages = ['flask', 'flask-login']
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package} 설치됨")
        except ImportError:
            print(f"✗ {package} 설치 필요")
            return False
    
    return True

def install_dependencies():
    """필요한 패키지 설치"""
    print("필요한 패키지를 설치합니다...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'flask', 'flask-login'])
    print("패키지 설치 완료!")

def create_directories():
    """필요한 디렉토리 생성"""
    directories = ['templates']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ {directory} 디렉토리 생성됨")

def main():
    print("=== 간단한 모듈 마켓플레이스 시스템 ===")
    print()
    
    # 디렉토리 생성
    create_directories()
    
    # 의존성 확인
    if not check_dependencies():
        print("\n의존성 패키지를 설치하시겠습니까? (y/n): ", end="")
        if input().lower() == 'y':
            install_dependencies()
        else:
            print("패키지 설치를 취소했습니다.")
            return
    
    print("\n=== 시스템 시작 ===")
    print("서버가 시작되면 다음 URL로 접속하세요:")
    print("http://localhost:5001")
    print()
    print("테스트 계정:")
    print("- 관리자: admin / password")
    print("- 매니저: manager / password") 
    print("- 직원: employee / password")
    print()
    print("서버를 중지하려면 Ctrl+C를 누르세요.")
    print("=" * 50)
    
    # 서버 실행
    try:
        from simple_marketplace import app
        app.run(debug=True, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\n서버가 중지되었습니다.")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

if __name__ == '__main__':
    main() 