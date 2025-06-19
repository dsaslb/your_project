#!/usr/bin/env python3
"""
관리자 계정 확인 및 재설정 스크립트
"""

import os
import sys
from werkzeug.security import generate_password_hash, check_password_hash

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User

def check_admin_user():
    """기존 admin 계정 정보를 확인합니다."""
    
    with app.app_context():
        admin_user = User.query.filter_by(username='admin').first()
        
        if not admin_user:
            print("❌ admin 계정을 찾을 수 없습니다.")
            return None
        
        print("📋 기존 admin 계정 정보:")
        print(f"   ID: {admin_user.id}")
        print(f"   사용자명: {admin_user.username}")
        print(f"   역할: {admin_user.role}")
        print(f"   상태: {admin_user.status}")
        print(f"   생성일: {admin_user.created_at}")
        
        return admin_user

def reset_admin_password(new_password="admin123"):
    """admin 계정의 비밀번호를 재설정합니다."""
    
    with app.app_context():
        admin_user = User.query.filter_by(username='admin').first()
        
        if not admin_user:
            print("❌ admin 계정을 찾을 수 없습니다.")
            return False
        
        # 새 비밀번호 해시 생성
        new_password_hash = generate_password_hash(new_password)
        
        try:
            # 비밀번호 업데이트
            admin_user.password = new_password_hash
            db.session.commit()
            
            print("✅ admin 계정 비밀번호가 성공적으로 재설정되었습니다!")
            print(f"   새 비밀번호: {new_password}")
            print("\n🔐 로그인 정보:")
            print(f"   아이디: admin")
            print(f"   비밀번호: {new_password}")
            
            return True
            
        except Exception as e:
            print(f"❌ 비밀번호 재설정 중 오류 발생: {e}")
            db.session.rollback()
            return False

def test_admin_login(password):
    """admin 계정 로그인을 테스트합니다."""
    
    with app.app_context():
        admin_user = User.query.filter_by(username='admin').first()
        
        if not admin_user:
            print("❌ admin 계정을 찾을 수 없습니다.")
            return False
        
        if check_password_hash(admin_user.password, password):
            print("✅ 비밀번호가 올바릅니다!")
            return True
        else:
            print("❌ 비밀번호가 올바르지 않습니다.")
            return False

def main():
    """메인 실행 함수"""
    print("🔍 관리자 계정 확인 및 관리 스크립트")
    print("=" * 50)
    
    try:
        # 기존 admin 계정 확인
        admin_user = check_admin_user()
        
        if admin_user:
            print("\n" + "-" * 30)
            print("옵션을 선택하세요:")
            print("1. 비밀번호 재설정 (기본: admin123)")
            print("2. 로그인 테스트")
            print("3. 종료")
            
            choice = input("\n선택 (1-3): ").strip()
            
            if choice == "1":
                new_password = input("새 비밀번호 (기본값 사용하려면 Enter): ").strip()
                if not new_password:
                    new_password = "admin123"
                reset_admin_password(new_password)
                
            elif choice == "2":
                test_password = input("테스트할 비밀번호: ").strip()
                test_admin_login(test_password)
                
            elif choice == "3":
                print("종료합니다.")
                
            else:
                print("잘못된 선택입니다.")
        
    except Exception as e:
        print(f"❌ 스크립트 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    main() 