#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데이터베이스 초기화 스크립트
- your_program.db 파일 생성
- 모든 테이블 생성
- 기본 데이터 초기화
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app, db
from models_main import Brand, Branch, User, Industry
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """데이터베이스 초기화"""
    
    with app.app_context():
        try:
            # 1. 테이블 생성
            logger.info("데이터베이스 테이블 생성 중...")
            db.create_all()
            logger.info("데이터베이스 테이블 생성 완료!")
            
            # 2. 기본 업종 생성
            logger.info("기본 업종 생성 중...")
            industry = Industry.query.filter_by(name='음식점').first()
            if not industry:
                industry = Industry(
                    name='음식점',
                    code='RESTAURANT',
                    description='음식점 업종',
                    icon='🍽️',
                    color='#FF6B6B',
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.session.add(industry)
                db.session.commit()
                logger.info("음식점 업종 생성 완료!")
            else:
                logger.info("음식점 업종이 이미 존재합니다.")
            
            # 3. 기본 관리자 계정 생성
            logger.info("기본 관리자 계정 생성 중...")
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    email='admin@example.com',
                    password_hash='admin123',  # 실제로는 해시된 비밀번호여야 함
                    role='admin',
                    is_active=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.session.add(admin_user)
                db.session.commit()
                logger.info("기본 관리자 계정 생성 완료! (admin / admin123)")
            else:
                logger.info("기본 관리자 계정이 이미 존재합니다.")
            
            # 4. 옥된장 브랜드 생성
            logger.info("옥된장 브랜드 생성 중...")
            okdoenjang_brand = Brand.query.filter_by(name='옥된장').first()
            if not okdoenjang_brand:
                okdoenjang_brand = Brand(
                    name='옥된장',
                    code='OKDOENJANG',
                    description='옥된장 브랜드',
                    industry_id=industry.id,
                    logo_url='',
                    website_url='',
                    contact_email='info@okdoenjang.com',
                    contact_phone='02-1234-5678',
                    address='서울시 강남구',
                    status='active',
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.session.add(okdoenjang_brand)
                db.session.commit()
                logger.info("옥된장 브랜드 생성 완료!")
            else:
                logger.info("옥된장 브랜드가 이미 존재합니다.")
            
            # 5. 양주점 매장 생성
            logger.info("양주점 매장 생성 중...")
            yangju_branch = Branch.query.filter_by(name='양주점').first()
            if not yangju_branch:
                yangju_branch = Branch(
                    name='양주점',
                    code='YANGJU',
                    brand_id=okdoenjang_brand.id,
                    address='경기도 양주시',
                    phone='031-123-4567',
                    manager_id=admin_user.id,
                    status='active',
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.session.add(yangju_branch)
                db.session.commit()
                logger.info("양주점 매장 생성 완료!")
            else:
                logger.info("양주점 매장이 이미 존재합니다.")
            
            logger.info("=== 데이터베이스 초기화 완료 ===")
            logger.info("생성된 항목:")
            logger.info("- 업종: 음식점")
            logger.info("- 브랜드: 옥된장")
            logger.info("- 매장: 양주점")
            logger.info("- 관리자 계정: admin / admin123")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    init_database() 