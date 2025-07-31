#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
테스트 데이터 생성 스크립트
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app_clean import app, db
from models_main import Industry, Brand, Branch, User
from werkzeug.security import generate_password_hash

def create_test_data():
    """테스트 데이터 생성"""
    with app.app_context():
        try:
            # 기존 데이터 삭제
            User.query.delete()
            Branch.query.delete()
            Brand.query.delete()
            Industry.query.delete()
            
            # 1. 업종 생성
            industry1 = Industry(
                name="음식점",
                code="FOOD",
                description="음식점 업종",
                color="#FF6B6B",
                icon="fa-utensils"
            )
            
            industry2 = Industry(
                name="카페",
                code="CAFE",
                description="카페 업종",
                color="#4ECDC4",
                icon="fa-coffee"
            )
            
            db.session.add(industry1)
            db.session.add(industry2)
            db.session.commit()
            
            # 2. 브랜드 생성
            brand1 = Brand(
                name="맛있는 피자",
                code="PIZZA001",
                industry_id=industry1.id,
                description="최고의 피자 브랜드"
            )
            
            brand2 = Brand(
                name="스타벅스",
                code="CAFE001",
                industry_id=industry2.id,
                description="글로벌 커피 브랜드"
            )
            
            db.session.add(brand1)
            db.session.add(brand2)
            db.session.commit()
            
            # 3. 매장 생성
            store1 = Branch(
                name="강남점",
                brand_id=brand1.id,
                industry_id=industry1.id,
                address="서울시 강남구 테헤란로 123",
                phone="02-1234-5678"
            )
            
            store2 = Branch(
                name="홍대점",
                brand_id=brand1.id,
                industry_id=industry1.id,
                address="서울시 마포구 홍대로 456",
                phone="02-2345-6789"
            )
            
            store3 = Branch(
                name="강남스타벅스",
                brand_id=brand2.id,
                industry_id=industry2.id,
                address="서울시 강남구 역삼동 789",
                phone="02-3456-7890"
            )
            
            db.session.add(store1)
            db.session.add(store2)
            db.session.add(store3)
            db.session.commit()
            
            # 4. 직원 생성
            # 최고관리자 (업종 관리자)
            admin1 = User(
                username="admin1",
                email="admin1@example.com",
                role="admin",
                status="approved",
                name="최고관리자",
                phone="010-1111-1111"
            )
            admin1.password_hash = generate_password_hash("password123", method="pbkdf2:sha256")
            
            # 브랜드 관리자
            brand_admin1 = User(
                username="brand_admin1",
                email="brand_admin1@example.com",
                role="brand_admin",
                status="approved",
                brand_id=brand1.id,
                name="피자브랜드관리자",
                phone="010-2222-2222"
            )
            brand_admin1.password_hash = generate_password_hash("password123", method="pbkdf2:sha256")
            
            brand_admin2 = User(
                username="brand_admin2",
                email="brand_admin2@example.com",
                role="brand_admin",
                status="approved",
                brand_id=brand2.id,
                name="스타벅스관리자",
                phone="010-3333-3333"
            )
            brand_admin2.password_hash = generate_password_hash("password123", method="pbkdf2:sha256")
            
            # 매장 관리자
            store_admin1 = User(
                username="store_admin1",
                email="store_admin1@example.com",
                role="store_admin",
                status="approved",
                branch_id=store1.id,
                brand_id=brand1.id,
                name="강남점매니저",
                phone="010-4444-4444"
            )
            store_admin1.password_hash = generate_password_hash("password123", method="pbkdf2:sha256")
            
            store_admin2 = User(
                username="store_admin2",
                email="store_admin2@example.com",
                role="store_admin",
                status="approved",
                branch_id=store3.id,
                brand_id=brand2.id,
                name="강남스타벅스매니저",
                phone="010-5555-5555"
            )
            store_admin2.password_hash = generate_password_hash("password123", method="pbkdf2:sha256")
            
            # 일반 직원
            employee1 = User(
                username="employee1",
                email="employee1@example.com",
                role="employee",
                status="approved",
                branch_id=store1.id,
                brand_id=brand1.id,
                name="이직원",
                phone="010-2345-6789"
            )
            employee1.password_hash = generate_password_hash("password123", method="pbkdf2:sha256")
            
            employee2 = User(
                username="barista1",
                email="barista1@example.com",
                role="employee",
                status="approved",
                branch_id=store3.id,
                brand_id=brand2.id,
                name="박바리스타",
                phone="010-3456-7890"
            )
            employee2.password_hash = generate_password_hash("password123", method="pbkdf2:sha256")
            
            db.session.add(admin1)
            db.session.add(brand_admin1)
            db.session.add(brand_admin2)
            db.session.add(store_admin1)
            db.session.add(store_admin2)
            db.session.add(employee1)
            db.session.add(employee2)
            db.session.commit()
            
            print("✅ 테스트 데이터 생성 완료!")
            print(f"📊 생성된 데이터:")
            print(f"   - 업종: {Industry.query.count()}개")
            print(f"   - 브랜드: {Brand.query.count()}개")
            print(f"   - 매장: {Branch.query.count()}개")
            print(f"   - 직원: {User.query.count()}개")
            
        except Exception as e:
            print(f"❌ 테스트 데이터 생성 실패: {e}")
            db.session.rollback()

if __name__ == "__main__":
    create_test_data() 