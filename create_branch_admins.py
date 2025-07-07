#!/usr/bin/env python3
"""
브랜드 관리자(admin) + 5개 매장 관리자(admin1~admin5) 계정 생성/수정 스크립트
"""
import os
import sys
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from app import app, db
from models import User

load_dotenv()

def upsert_user(username, password, role, branch_id, status="approved", email=None):
    user = User.query.filter_by(username=username).first()
    if user:
        user.password_hash = generate_password_hash(password)
        user.role = role
        user.branch_id = branch_id
        user.status = status
        if email:
            user.email = email
        print(f"✅ 계정 수정: {username} ({role}, branch {branch_id})")
    else:
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role=role,
            branch_id=branch_id,
            status=status,
            email=email
        )
        db.session.add(user)
        print(f"✅ 계정 생성: {username} ({role}, branch {branch_id})")
    return user

def main():
    with app.app_context():
        # 브랜드 관리자
        upsert_user("admin", "admin123!", "brand_admin", 1, email="admin@brand.com")
        # 5개 매장 관리자
        for i in range(1, 6):
            upsert_user(f"admin{i}", "admin123!", "manager", i, email=f"admin{i}@brand.com")
        db.session.commit()
        print("\n🎉 모든 계정이 정상적으로 생성/수정되었습니다!")
        print("\n[로그인 정보]")
        print("브랜드 관리자: admin / admin123!")
        for i in range(1, 6):
            print(f"매장{i} 관리자: admin{i} / admin123! (branch_id={i})")

if __name__ == "__main__":
    main() 