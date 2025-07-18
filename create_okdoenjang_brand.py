#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
옥된장 브랜드 및 양주점 매장 생성 스크립트
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 데이터베이스 경로를 기존 app.db로 설정
os.environ['DATABASE_URL'] = 'sqlite:///instance/your_program.db'

from app import app
from models_main import db, Brand, Branch, User, Industry
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_okdoenjang_brand():
    """옥된장 브랜드 및 양주점 매장 생성"""
    
    with app.app_context():
        try:
            # 1. 음식점 업종 확인 또는 생성
            industry = Industry.query.filter_by(name='음식점').first()
            if not industry:
                industry = Industry(
                    name='음식점',
                    code='RESTAURANT',
                    description='음식점 업종',
                    icon='🍽️',
                    color='#FF6B6B',
                    is_active=True
                )
                db.session.add(industry)
                db.session.commit()
                logger.info("음식점 업종 생성 완료")
            
            # 2. 옥된장 브랜드 생성
            existing_brand = Brand.query.filter_by(name='옥된장').first()
            if existing_brand:
                logger.info("옥된장 브랜드가 이미 존재합니다.")
                brand = existing_brand
            else:
                brand = Brand(
                    name='옥된장',
                    code='REST_OKDE_001',
                    description='전통 된장 전문점',
                    industry_id=industry.id,
                    contact_email='admin@okdoenjang.com',
                    contact_phone='031-123-4567',
                    address='경기도 양주시',
                    store_type='individual',
                    status='active'
                )
                db.session.add(brand)
                db.session.commit()
                logger.info("옥된장 브랜드 생성 완료")
            
            # 3. 양주점 매장 생성
            existing_store = Branch.query.filter_by(name='양주점').first()
            if existing_store:
                logger.info("양주점이 이미 존재합니다.")
                store = existing_store
            else:
                store = Branch(
                    name='양주점',
                    address='경기도 양주시 양주로 123',
                    phone='031-123-4567',
                    store_code='OKDE_YANGJU_001',
                    store_type='franchise',
                    brand_id=brand.id,
                    industry_id=industry.id,
                    status='active',
                    business_hours={
                        'monday': {'open': '09:00', 'close': '21:00'},
                        'tuesday': {'open': '09:00', 'close': '21:00'},
                        'wednesday': {'open': '09:00', 'close': '21:00'},
                        'thursday': {'open': '09:00', 'close': '21:00'},
                        'friday': {'open': '09:00', 'close': '21:00'},
                        'saturday': {'open': '09:00', 'close': '21:00'},
                        'sunday': {'open': '09:00', 'close': '20:00'}
                    },
                    capacity=50
                )
                db.session.add(store)
                db.session.commit()
                logger.info("양주점 매장 생성 완료")
            
            # 4. admin 계정 확인 및 설정
            admin_user = User.query.filter_by(username='admin').first()
            if admin_user:
                # 기존 admin 계정 업데이트
                admin_user.set_password('admin123')
                admin_user.status = 'approved'
                admin_user.is_active = True
                admin_user.brand_id = brand.id
                admin_user.branch_id = store.id
                admin_user.role = 'admin'
                admin_user.grade = 'ceo'
                admin_user.position = '대표'
                admin_user.department = '경영진'
                logger.info("기존 admin 계정 업데이트 완료")
            else:
                # 새 admin 계정 생성
                admin_user = User(
                    username='admin',
                    email='admin@okdoenjang.com',
                    name='관리자',
                    role='admin',
                    grade='ceo',
                    status='approved',
                    is_active=True,
                    brand_id=brand.id,
                    branch_id=store.id,
                    position='대표',
                    department='경영진',
                    phone='010-1234-5678'
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                logger.info("새 admin 계정 생성 완료")
            
            db.session.commit()
            
            # 5. 결과 출력
            logger.info("=== 생성 완료 ===")
            logger.info(f"브랜드: {brand.name} (ID: {brand.id})")
            logger.info(f"매장: {store.name} (ID: {store.id})")
            logger.info(f"관리자: {admin_user.username} (ID: {admin_user.id})")
            logger.info("로그인 정보: admin / admin123")
            
            return {
                'brand_id': brand.id,
                'store_id': store.id,
                'admin_id': admin_user.id
            }
            
        except Exception as e:
            logger.error(f"브랜드 생성 중 오류 발생: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    result = create_okdoenjang_brand()
    print(f"\n생성 완료!")
    print(f"브랜드 ID: {result['brand_id']}")
    print(f"매장 ID: {result['store_id']}")
    print(f"관리자 ID: {result['admin_id']}")
    print("로그인: admin / admin123") 