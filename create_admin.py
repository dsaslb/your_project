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

def create_admin_user():
    """관리자 계정을 생성합니다."""
    with app.app_context():
        # 기존 admin 계정이 있는지 확인
        existing_admin = User.query.filter_by(username="admin").first()

        if existing_admin:
            print("⚠️  admin 계정이 이미 존재합니다!")
            print(f"   기존 계정 ID: {existing_admin.id}")
            print(f"   상태: {existing_admin.status}")
            print(f"   역할: {existing_admin.role}")
            
            # admin을 브랜드 관리자로 변경
            existing_admin.role = "brand_admin"
            existing_admin.branch_id = 1  # 기본 매장 ID
            db.session.commit()
            print("✅ admin 계정을 브랜드 관리자로 변경했습니다!")
            return True

        # 관리자 비밀번호 설정 (여기서 변경 가능)
        admin_password = "admin123!"  # 원하는 비밀번호로 변경하세요

        # 새 브랜드 관리자 계정 생성
        admin_user = User(
            username="admin", 
            email="admin@example.com", 
            status="approved", 
            role="brand_admin",
            branch_id=1  # 기본 매장 ID
        )
        admin_user.set_password(admin_password)

        try:
            db.session.add(admin_user)
            db.session.commit()

            print("✅ 브랜드 관리자 계정이 성공적으로 생성되었습니다!")
            print(f"   사용자명: admin")
            print(f"   비밀번호: {admin_password}")
            print(f"   역할: brand_admin")
            print(f"   상태: approved")
            print(f"   매장 ID: 1")
            print("\n🔐 로그인 정보:")
            print(f"   아이디: admin")
            print(f"   비밀번호: {admin_password}")

            return True

        except Exception as e:
            print(f"❌ 관리자 계정 생성 중 오류 발생: {e}")
            db.session.rollback()
            return False

def create_brand_admin_for_branches():
    """5개 매장에 브랜드 관리자 계정을 생성합니다."""
    with app.app_context():
        branches = [
            {"id": 1, "name": "강남점"},
            {"id": 2, "name": "홍대점"},
            {"id": 3, "name": "부산점"},
            {"id": 4, "name": "대구점"},
            {"id": 5, "name": "인천점"}
        ]
        
        for branch in branches:
            # 각 매장별 브랜드 관리자 계정 생성
            username = f"admin_branch_{branch['id']}"
            email = f"admin_branch_{branch['id']}@example.com"
            
            existing_user = User.query.filter_by(username=username).first()
            
            if existing_user:
                print(f"⚠️  {username} 계정이 이미 존재합니다!")
                continue
            
            brand_admin = User(
                username=username,
                email=email,
                status="approved",
                role="brand_admin",
                branch_id=branch['id']
            )
            brand_admin.set_password("admin123!")
            
            try:
                db.session.add(brand_admin)
                db.session.commit()
                print(f"✅ {branch['name']} 브랜드 관리자 계정 생성: {username}")
            except Exception as e:
                print(f"❌ {branch['name']} 브랜드 관리자 생성 실패: {e}")
                db.session.rollback()

def main():
    """메인 실행 함수"""
    print("🚀 브랜드 관리자 계정 생성 스크립트를 시작합니다...")
    print("=" * 50)

    try:
        success = create_admin_user()
        
        if success:
            print("\n" + "=" * 50)
            print("🏢 5개 매장 브랜드 관리자 계정을 생성합니다...")
            create_brand_admin_for_branches()
            
            print("\n" + "=" * 50)
            print("🎉 브랜드 관리자 계정 생성 완료!")
            print("생성된 계정들:")
            print("1. admin (기본 브랜드 관리자)")
            print("2. admin_branch_1 (강남점)")
            print("3. admin_branch_2 (홍대점)")
            print("4. admin_branch_3 (부산점)")
            print("5. admin_branch_4 (대구점)")
            print("6. admin_branch_5 (인천점)")
            print("\n모든 계정의 비밀번호: admin123!")
        else:
            print("\n" + "=" * 50)
            print("⚠️  브랜드 관리자 계정 생성이 완료되지 않았습니다.")

    except Exception as e:
        print(f"❌ 스크립트 실행 중 오류 발생: {e}")
        print("데이터베이스 연결이나 모델 설정을 확인해주세요.")

if __name__ == "__main__":
    main()
