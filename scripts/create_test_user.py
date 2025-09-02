#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
테스트용 사용자 생성 스크립트
"""

from app import app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash

def create_test_user():
    """테스트용 사용자 생성"""
    with app.app_context():
        try:
            # 기존 테스트 사용자 확인
            existing_user = User.query.filter_by(username='demo').first()
            if existing_user:
                print("✅ 테스트 사용자 'demo'가 이미 존재합니다.")
                return existing_user
            
            # 새 테스트 사용자 생성 (기본 속성만 사용)
            test_user = User(
                username='demo',
                email='demo@example.com',
                password_hash=generate_password_hash('demo123'),
                role='employee'
            )
            
            db.session.add(test_user)
            db.session.commit()
            
            print("✅ 테스트 사용자 'demo'가 생성되었습니다.")
            print(f"  - 사용자명: {test_user.username}")
            print(f"  - 이메일: {test_user.email}")
            print(f"  - 역할: {test_user.role}")
            print(f"  - 비밀번호: demo123")
            
            return test_user
            
        except Exception as e:
            print(f"❌ 테스트 사용자 생성 실패: {e}")
            db.session.rollback()
            return None

if __name__ == "__main__":
    create_test_user()
