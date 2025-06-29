#!/usr/bin/env python3
"""
간단한 관리자 계정 생성 스크립트
"""

from werkzeug.security import generate_password_hash

from app import app
from models import User, db


def create_admin():
    with app.app_context():
        # 기존 admin 계정이 있는지 확인
        existing_admin = User.query.filter_by(username="admin").first()

        if existing_admin:
            print("Admin account already exists!")
            return

        # 새 관리자 계정 생성
        admin = User(
            username="admin",
            password=generate_password_hash("admin123"),
            status="approved",
            role="admin",
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin account created successfully!")
        print("Username: admin")
        print("Password: admin123")


if __name__ == "__main__":
    create_admin()
