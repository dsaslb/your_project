#!/usr/bin/env python3
"""
직원 데이터 확인 스크립트
"""

from app import app, db
from models import User

def check_users():
    """직원 데이터 확인"""
    with app.app_context():
        users = User.query.all()
        print(f"총 직원 수: {len(users)}")
        print("\n=== 직원 목록 ===")
        for user in users:
            print(f"ID: {user.id}, 이름: {user.name}, 상태: {user.status}, 역할: {user.role}, 직책: {user.position}, 부서: {user.department}")
        
        # 승인된 직원만
        approved_users = User.query.filter_by(status="approved").all()
        print(f"\n승인된 직원 수: {len(approved_users)}")
        
        # 미승인 직원만
        pending_users = User.query.filter_by(status="pending").all()
        print(f"미승인 직원 수: {len(pending_users)}")

if __name__ == '__main__':
    check_users()
