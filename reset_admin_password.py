#!/usr/bin/env python3
"""
admin 계정 비밀번호 재설정 스크립트
"""

import os
import sys

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# 프로젝트 루트를 경로에 추가
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import app, db
from models import User

# .env 파일 로드
load_dotenv()

def reset_admin_password():
    """admin 계정 비밀번호를 재설정합니다."""
    with app.app_context():
        # admin 계정 찾기
        admin_user = User.query.filter_by(username="admin").first()

        if not admin_user:
            print("❌ admin 계정을 찾을 수 없습니다!")
            return False

        # 새 비밀번호 설정
        new_password = "admin123!"
        admin_user.password_hash = generate_password_hash(new_password)
        
        # 브랜드 관리자 역할 확인
        if admin_user.role != "brand_admin":
            admin_user.role = "brand_admin"
            admin_user.branch_id = 1

        try:
            db.session.commit()
            print("✅ admin 계정 비밀번호가 성공적으로 재설정되었습니다!")
            print(f"   사용자명: admin")
            print(f"   새 비밀번호: {new_password}")
            print(f"   역할: {admin_user.role}")
            print(f"   상태: {admin_user.status}")
            print("\n🔐 로그인 정보:")
            print(f"   아이디: admin")
            print(f"   비밀번호: {new_password}")
            return True

        except Exception as e:
            print(f"❌ 비밀번호 재설정 중 오류 발생: {e}")
            db.session.rollback()
            return False

def main():
    """메인 실행 함수"""
    print("🚀 admin 계정 비밀번호 재설정 스크립트를 시작합니다...")
    print("=" * 50)

    try:
        success = reset_admin_password()

        if success:
            print("\n" + "=" * 50)
            print("🎉 비밀번호 재설정 완료!")
            print("이제 admin 계정으로 로그인할 수 있습니다.")
        else:
            print("\n" + "=" * 50)
            print("⚠️  비밀번호 재설정이 완료되지 않았습니다.")

    except Exception as e:
        print(f"❌ 스크립트 실행 중 오류 발생: {e}")
        print("데이터베이스 연결이나 모델 설정을 확인해주세요.")

if __name__ == "__main__":
    main() 