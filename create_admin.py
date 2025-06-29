#!/usr/bin/env python3
"""
관리자 계정 자동 생성 스크립트
"""

import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash

# 프로젝트 루트를 경로에 추가
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import app, db
from models import User

# .env 파일 로드
load_dotenv()

with app.app_context():
    try:
        # 기존 admin 사용자 확인
        admin_user = User.query.filter_by(username="admin").first()

        if not admin_user:
            print("Creating new admin user...")
            # 사용자 정보 설정
            username = "admin"
            password = "admin_password"  # 실제 운영에서는 더 강력한 비밀번호를 사용해야 합니다.
            email = "admin@example.com"

            # 새 사용자 생성
            new_admin = User(
                username=username,
                email=email,
                role="admin",
                status="approved",  # 바로 승인된 상태로 생성
            )
            new_admin.set_password(password)

            db.session.add(new_admin)
            db.session.commit()

            print(
                f"Admin user '{username}' created successfully with password '{password}'."
            )
        else:
            print(f"Admin user 'admin' already exists.")
            # 비밀번호 재설정 (필요시)
            # print("Resetting admin password...")
            # admin_user.set_password('new_admin_password')
            # db.session.commit()
            # print("Admin password has been reset.")

    except Exception as e:
        print(f"An error occurred: {e}")
        db.session.rollback()


def create_admin_user():
    """관리자 계정을 생성합니다."""

    with app.app_context():
        # 기존 admin 계정이 있는지 확인
        existing_admin = User.query.filter_by(username="admin").first()

        if existing_admin:
            print("⚠️  admin 계정이 이미 존재합니다!")
            print(f"   기존 계정 ID: {existing_admin.id}")
            print(f"   상태: {existing_admin.status}")
            return False

        # 관리자 비밀번호 설정 (여기서 변경 가능)
        admin_password = "admin123"  # 원하는 비밀번호로 변경하세요

        # 비밀번호 해시 생성
        password_hash = generate_password_hash(admin_password)

        # 새 관리자 계정 생성
        admin_user = User(
            username="admin", password=password_hash, status="approved", role="admin"
        )

        try:
            db.session.add(admin_user)
            db.session.commit()

            print("✅ 관리자 계정이 성공적으로 생성되었습니다!")
            print(f"   사용자명: admin")
            print(f"   비밀번호: {admin_password}")
            print(f"   역할: admin")
            print(f"   상태: approved")
            print("\n🔐 로그인 정보:")
            print(f"   아이디: admin")
            print(f"   비밀번호: {admin_password}")

            return True

        except Exception as e:
            print(f"❌ 관리자 계정 생성 중 오류 발생: {e}")
            db.session.rollback()
            return False


def main():
    """메인 실행 함수"""
    print("🚀 관리자 계정 생성 스크립트를 시작합니다...")
    print("=" * 50)

    try:
        success = create_admin_user()

        if success:
            print("\n" + "=" * 50)
            print("🎉 관리자 계정 생성 완료!")
            print("이제 웹 애플리케이션에서 admin 계정으로 로그인할 수 있습니다.")
        else:
            print("\n" + "=" * 50)
            print("⚠️  관리자 계정 생성이 완료되지 않았습니다.")

    except Exception as e:
        print(f"❌ 스크립트 실행 중 오류 발생: {e}")
        print("데이터베이스 연결이나 모델 설정을 확인해주세요.")


if __name__ == "__main__":
    main()
