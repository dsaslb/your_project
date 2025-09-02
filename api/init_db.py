#!/usr/bin/env python3
"""
🗄️ 데이터베이스 초기화 스크립트

CQRS 라이트 아키텍처에 필요한 테이블들을 생성하고 테스트 데이터를 삽입
"""

import os
import sys
from datetime import datetime, timezone

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from models.idempotency import IdempotencyKey
from models.event_log import EventLog
from models.user import User
from models.industry import Industry
from models.brand import Brand
from models.branch import Branch

def init_database():
    """데이터베이스 초기화"""
    print("🗄️ 데이터베이스 초기화 시작...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # 데이터베이스 테이블 생성
            db.create_all()
            print("✅ 데이터베이스 테이블 생성 완료")
            
            # 테스트 데이터 삽입
            insert_test_data()
            print("✅ 테스트 데이터 삽입 완료")
            
        except Exception as e:
            print(f"❌ 데이터베이스 초기화 실패: {e}")
            return False
    
    return True

def insert_test_data():
    """테스트 데이터 삽입"""
    print("📝 테스트 데이터 삽입 시작...")
    
    # 1. 산업 생성
    industry = Industry(
        name="테스트 산업",
        description="CQRS 테스트용 산업",
        status="active"
    )
    db.session.add(industry)
    db.session.flush()  # ID 생성
    
    # 2. 브랜드 생성
    brand = Brand(
        name="테스트 브랜드",
        industry_id=industry.id,
        description="CQRS 테스트용 브랜드",
        status="active"
    )
    db.session.add(brand)
    db.session.flush()
    
    # 3. 지점 생성
    branch = Branch(
        name="테스트 지점",
        brand_id=brand.id,
        industry_id=industry.id,
        address="서울시 강남구 테스트로 123",
        status="active"
    )
    db.session.add(branch)
    db.session.flush()
    
    # 4. 테스트 사용자 생성
    test_user = User(
        username="test_user",
        email="test@example.com",
        password_hash="test_password_hash",  # 실제로는 해시된 비밀번호
        role="employee",
        industry_id=industry.id,
        brand_id=brand.id,
        branch_id=branch.id,
        status="active"
    )
    db.session.add(test_user)
    db.session.flush()
    
    # 5. 관리자 사용자 생성
    admin_user = User(
        username="admin",
        email="admin@example.com",
        password_hash="admin_password_hash",
        role="admin",
        industry_id=industry.id,
        brand_id=brand.id,
        branch_id=branch.id,
        status="active"
    )
    db.session.add(admin_user)
    
    # 변경사항 커밋
    db.session.commit()
    
    print(f"✅ 테스트 데이터 생성 완료:")
    print(f"   - 산업: {industry.name} (ID: {industry.id})")
    print(f"   - 브랜드: {brand.name} (ID: {brand.id})")
    print(f"   - 지점: {branch.name} (ID: {branch.id})")
    print(f"   - 테스트 사용자: {test_user.username} (ID: {test_user.id})")
    print(f"   - 관리자: {admin_user.username} (ID: {admin_user.id})")

def verify_database():
    """데이터베이스 검증"""
    print("🔍 데이터베이스 검증 시작...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # 사용자 수 확인
            user_count = User.query.count()
            print(f"✅ 사용자 수: {user_count}")
            
            # 산업 수 확인
            industry_count = Industry.query.count()
            print(f"✅ 산업 수: {industry_count}")
            
            # 브랜드 수 확인
            brand_count = Brand.query.count()
            print(f"✅ 브랜드 수: {brand_count}")
            
            # 지점 수 확인
            branch_count = Branch.query.count()
            print(f"✅ 지점 수: {branch_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ 데이터베이스 검증 실패: {e}")
            return False

if __name__ == "__main__":
    print("🚀 CQRS 라이트 아키텍처 데이터베이스 초기화")
    print("=" * 60)
    
    # 데이터베이스 초기화
    if init_database():
        print("\n✅ 데이터베이스 초기화 성공!")
        
        # 검증
        if verify_database():
            print("🎉 모든 설정이 완료되었습니다!")
        else:
            print("⚠️ 데이터베이스 검증에 실패했습니다.")
    else:
        print("❌ 데이터베이스 초기화에 실패했습니다.")
