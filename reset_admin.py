#!/usr/bin/env python3
"""
관리자 계정 비밀번호 자동 재설정
"""

import os
import sys

from werkzeug.security import generate_password_hash

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User


def reset_admin_password():
    """admin 계정의 비밀번호를 admin123으로 재설정합니다."""

    with app.app_context():
        admin_user = User.query.filter_by(username="admin").first()

        if not admin_user:
            print("❌ admin 계정을 찾을 수 없습니다.")
            return False

        # 새 비밀번호 설정
        new_password = "admin123"
        new_password_hash = generate_password_hash(new_password)

        try:
            # 비밀번호 업데이트
            admin_user.password = new_password_hash
            db.session.commit()

            print("✅ admin 계정 비밀번호가 성공적으로 재설정되었습니다!")
            print("\n🔐 로그인 정보:")
            print(f"   아이디: admin")
            print(f"   비밀번호: {new_password}")
            print("\n이제 웹 애플리케이션에서 로그인할 수 있습니다!")

            return True

        except Exception as e:
            print(f"❌ 비밀번호 재설정 중 오류 발생: {e}")
            db.session.rollback()
            return False


if __name__ == "__main__":
    print("🔄 admin 계정 비밀번호 재설정 중...")
    reset_admin_password()
