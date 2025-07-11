#!/usr/bin/env python3
"""
테스트용 사용자 계정 생성 스크립트
"""

import os
import sys
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Branch
from werkzeug.security import generate_password_hash

def create_test_users():
    """테스트용 사용자 계정 생성"""
    print("🚀 테스트용 사용자 계정 생성 스크립트를 시작합니다...")
    print("=" * 50)
    
    with app.app_context():
        # 데이터베이스 테이블 생성
        db.create_all()
        
        # 테스트 사용자 목록
        test_users = [
            {
                'username': 'admin',
                'password': 'admin123',
                'email': 'admin@test.com',
                'name': '업종별 관리자',
                'role': 'admin',
                'grade': 'ceo',
                'status': 'approved',
                'position': '업종별 관리자',
                'department': '경영진'
            },
            {
                'username': 'brand_admin',
                'password': 'admin123',
                'email': 'brand_admin@test.com',
                'name': '브랜드 관리자',
                'role': 'brand_admin',
                'grade': 'brand_manager',
                'status': 'approved',
                'position': '브랜드 관리자',
                'department': '브랜드팀'
            },
            {
                'username': 'store_admin',
                'password': 'admin123',
                'email': 'store_admin@test.com',
                'name': '매장 관리자',
                'role': 'store_admin',
                'grade': 'store_manager',
                'status': 'approved',
                'position': '매장 관리자',
                'department': '매장운영팀'
            },
            {
                'username': 'employee',
                'password': 'admin123',
                'email': 'employee@test.com',
                'name': '직원',
                'role': 'employee',
                'grade': 'staff',
                'status': 'approved',
                'position': '직원',
                'department': '서비스팀'
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for user_data in test_users:
            username = user_data['username']
            existing_user = User.query.filter_by(username=username).first()
            
            if existing_user:
                print(f"⚠️  {username} 계정이 이미 존재합니다. 업데이트합니다...")
                # 기존 계정 업데이트
                for key, value in user_data.items():
                    if key != 'password':
                        setattr(existing_user, key, value)
                existing_user.set_password(user_data['password'])
                updated_count += 1
            else:
                print(f"✅ {username} 계정을 생성합니다...")
                # 새 계정 생성
                new_user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    name=user_data['name'],
                    role=user_data['role'],
                    grade=user_data['grade'],
                    status=user_data['status'],
                    position=user_data['position'],
                    department=user_data['department']
                )
                new_user.set_password(user_data['password'])
                db.session.add(new_user)
                created_count += 1
        
        db.session.commit()
        
        print("\n" + "=" * 50)
        print("🎉 테스트용 사용자 계정 생성 완료!")
        print(f"생성된 계정: {created_count}개")
        print(f"업데이트된 계정: {updated_count}개")
        print("\n테스트 계정 정보:")
        print("모든 계정의 비밀번호: admin123")
        print("\n1. 업종별 관리자 (admin)")
        print("   - 역할: admin")
        print("   - 접속 페이지: /admin-dashboard")
        print("\n2. 브랜드 관리자 (brand_admin)")
        print("   - 역할: brand_admin")
        print("   - 접속 페이지: /brand-dashboard")
        print("\n3. 매장 관리자 (store_admin)")
        print("   - 역할: store_admin")
        print("   - 접속 페이지: /store-dashboard")
        print("\n4. 직원 (employee)")
        print("   - 역할: employee")
        print("   - 접속 페이지: /employee-dashboard")
        print("\n테스트 로그인 페이지: /test-login")

if __name__ == '__main__':
    create_test_users() 