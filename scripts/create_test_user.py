#!/usr/bin/env python3
"""
테스트용 사용자 생성 스크립트
"""

import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models.user import User
from werkzeug.security import generate_password_hash

def create_test_users():
    """테스트용 사용자들을 생성합니다."""
    
    with app.app_context():
        try:
            print("테스트용 사용자 생성 중...")
            
            # 기존 사용자 확인
            existing_users = User.query.all()
            if existing_users:
                print(f"기존 사용자 {len(existing_users)}명이 있습니다:")
                for user in existing_users:
                    print(f"  - {user.username} ({user.role})")
            
            # 테스트 사용자들
            test_users = [
                {
                    'username': 'admin',
                    'password': 'admin123',
                    'email': 'admin@example.com',
                    'role': 'admin',
                    'full_name': '관리자',
                    'department': 'IT',
                    'position': '시스템 관리자'
                },
                {
                    'username': 'manager',
                    'password': 'manager123',
                    'email': 'manager@example.com',
                    'role': 'manager',
                    'full_name': '매니저',
                    'department': '영업',
                    'position': '팀장'
                },
                {
                    'username': 'user1',
                    'password': 'user123',
                    'email': 'user1@example.com',
                    'role': 'employee',
                    'full_name': '직원1',
                    'department': '영업',
                    'position': '사원'
                }
            ]
            
            created_count = 0
            for user_data in test_users:
                # 사용자가 이미 존재하는지 확인
                existing_user = User.query.filter_by(username=user_data['username']).first()
                if existing_user:
                    print(f"사용자 '{user_data['username']}'는 이미 존재합니다.")
                    continue
                
                # 새 사용자 생성
                new_user = User(
                    username=user_data['username'],
                    password_hash=generate_password_hash(user_data['password']),
                    email=user_data['email'],
                    role=user_data['role'],
                    name=user_data['full_name'],  # full_name 대신 name 사용
                    department=user_data['department'],
                    position=user_data['position']
                )
                
                db.session.add(new_user)
                created_count += 1
                print(f"사용자 생성: {user_data['username']} ({user_data['role']})")
            
            if created_count > 0:
                db.session.commit()
                print(f"✅ {created_count}명의 테스트 사용자가 생성되었습니다!")
            else:
                print("새로 생성된 사용자가 없습니다.")
            
            print("\n📋 테스트 계정 정보:")
            print("관리자: admin / admin123")
            print("매니저: manager / manager123")
            print("직원: user1 / user123")
            
        except Exception as e:
            print(f"❌ 사용자 생성 실패: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    create_test_users()
