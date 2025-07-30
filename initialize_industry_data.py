#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
업종 관리 데이터 초기화 스크립트
업종 데이터와 업종별 관리자 샘플 데이터 생성
"""

import logging
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash

# Flask 앱 설정
from app import app
from extensions import db
from models_main import Industry, IndustryAdmin, User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_industries():
    """기본 업종 데이터베이스 초기화"""
    try:
        # 기본 업종 목록 (name, code, description, icon, color)
        default_industries = [
            ("레스토랑", "RESTAURANT", "일반 레스토랑 및 식당", "🍽️", "#ff6b35"),
            ("카페", "CAFE", "커피 전문점 및 카페", "☕", "#8b4513"),
            ("패스트푸드", "FASTFOOD", "패스트푸드 체인점", "🍔", "#ff4757"),
            ("고기집", "BBQ", "바베큐 및 고기 전문점", "🥩", "#d63031"),
            ("치킨집", "CHICKEN", "치킨 전문점", "🍗", "#fdcb6e"),
            ("피자집", "PIZZA", "피자 전문점", "🍕", "#e17055"),
            ("중식당", "CHINESE", "중국 음식 전문점", "🥢", "#00b894"),
            ("일식당", "JAPANESE", "일본 음식 전문점", "🍣", "#74b9ff"),
            ("분식점", "SNACKBAR", "분식 및 간편식", "🍜", "#ffeaa7"),
            ("디저트카페", "DESSERT", "디저트 및 베이커리", "🧁", "#fd79a8"),
            ("펜션", "PENSION", "펜션 및 숙박업", "🏠", "#00cec9"),
            ("미용실", "SALON", "헤어 및 미용 서비스", "✂️", "#a29bfe"),
            ("네일샵", "NAILSHOP", "네일아트 전문점", "💅", "#fd79a8"),
            ("마사지샵", "MASSAGE", "마사지 및 스파", "💆", "#6c5ce7"),
            ("편의점", "CONVENIENCE", "편의점 및 소매업", "🏪", "#00b894"),
            ("의류매장", "CLOTHING", "의류 및 패션", "👕", "#e84393"),
            ("병원", "HOSPITAL", "병원 및 의료 서비스", "🏥", "#00cec9"),
            ("약국", "PHARMACY", "약국 및 의약품", "💊", "#2d3436"),
            ("학원", "ACADEMY", "교육 및 학원", "📚", "#0984e3"),
            ("기타", "OTHER", "기타 업종", "🏢", "#636e72")
        ]

        for name, code, description, icon, color in default_industries:
            # 이미 존재하는지 확인
            existing = Industry.query.filter_by(code=code).first()
            if not existing:
                industry = Industry(
                    name=name,
                    code=code,
                    description=description,
                    icon=icon,
                    color=color,
                    is_active=True
                )
                db.session.add(industry)
                logger.info(f"업종 생성: {name} ({code})")

        db.session.commit()
        logger.info("기본 업종 초기화 완료")
        return True

    except Exception as e:
        logger.error(f"업종 초기화 실패: {e}")
        db.session.rollback()
        return False

def create_sample_users():
    """샘플 사용자 계정 생성"""
    try:
        sample_users = [
            {
                'username': 'restaurant_admin',
                'email': 'restaurant@admin.com',
                'password': 'password123',
                'role': 'industry_admin',
                'is_active': True
            },
            {
                'username': 'cafe_admin',
                'email': 'cafe@admin.com',
                'password': 'password123',
                'role': 'industry_admin',
                'is_active': True
            },
            {
                'username': 'fastfood_admin',
                'email': 'fastfood@admin.com',
                'password': 'password123',
                'role': 'industry_admin',
                'is_active': True
            },
            {
                'username': 'bbq_admin',
                'email': 'bbq@admin.com',
                'password': 'password123',
                'role': 'industry_admin',
                'is_active': True
            },
            {
                'username': 'salon_admin',
                'email': 'salon@admin.com',
                'password': 'password123',
                'role': 'industry_admin',
                'is_active': True
            }
        ]
        
        created_users = []
        for user_data in sample_users:
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if not existing_user:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    role=user_data['role'],
                    is_active=user_data['is_active']
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                created_users.append(user)
                logger.info(f"사용자 생성: {user_data['username']}")
        
        db.session.commit()
        logger.info(f"샘플 사용자 {len(created_users)}명 생성 완료")
        return created_users
        
    except Exception as e:
        logger.error(f"샘플 사용자 생성 실패: {e}")
        db.session.rollback()
        return []

def create_sample_industry_admins():
    """샘플 업종별 관리자 데이터 생성"""
    try:
        # 업종별 관리자 샘플 데이터
        admin_data = [
            {
                'industry_code': 'RESTAURANT',
                'username': 'restaurant_admin',
                'full_name': '김레스토랑',
                'contact_email': 'restaurant@admin.com',
                'contact_phone': '010-1234-5678',
                'business_license': '1234567890',
                'company_name': '맛있는 레스토랑',
                'status': 'approved'
            },
            {
                'industry_code': 'CAFE',
                'username': 'cafe_admin',
                'full_name': '이카페',
                'contact_email': 'cafe@admin.com',
                'contact_phone': '010-2345-6789',
                'business_license': '2345678901',
                'company_name': '향긋한 카페',
                'status': 'approved'
            },
            {
                'industry_code': 'FASTFOOD',
                'username': 'fastfood_admin',
                'full_name': '박패스트',
                'contact_email': 'fastfood@admin.com',
                'contact_phone': '010-3456-7890',
                'business_license': '3456789012',
                'company_name': '빠른 버거집',
                'status': 'pending'
            },
            {
                'industry_code': 'BBQ',
                'username': 'bbq_admin',
                'full_name': '최고기',
                'contact_email': 'bbq@admin.com',
                'contact_phone': '010-4567-8901',
                'business_license': '4567890123',
                'company_name': '맛있는 고기집',
                'status': 'approved'
            },
            {
                'industry_code': 'SALON',
                'username': 'salon_admin',
                'full_name': '정미용',
                'contact_email': 'salon@admin.com',
                'contact_phone': '010-5678-9012',
                'business_license': '5678901234',
                'company_name': '예쁜 미용실',
                'status': 'rejected'
            }
        ]
        
        created_admins = []
        for admin_info in admin_data:
            # 업종 찾기
            industry = Industry.query.filter_by(code=admin_info['industry_code']).first()
            if not industry:
                logger.warning(f"업종을 찾을 수 없음: {admin_info['industry_code']}")
                continue
                
            # 사용자 찾기
            user = User.query.filter_by(username=admin_info['username']).first()
            if not user:
                logger.warning(f"사용자를 찾을 수 없음: {admin_info['username']}")
                continue
            
            # 이미 존재하는지 확인
            existing_admin = IndustryAdmin.query.filter_by(
                user_id=user.id, 
                industry_id=industry.id
            ).first()
            
            if not existing_admin:
                industry_admin = IndustryAdmin(
                    user_id=user.id,
                    industry_id=industry.id,
                    full_name=admin_info['full_name'],
                    contact_email=admin_info['contact_email'],
                    contact_phone=admin_info['contact_phone'],
                    business_license=admin_info['business_license'],
                    company_name=admin_info['company_name'],
                    status=admin_info['status'],
                    approval_date=datetime.utcnow() if admin_info['status'] == 'approved' else None,
                    created_at=datetime.utcnow()
                )
                
                db.session.add(industry_admin)
                created_admins.append(industry_admin)
                logger.info(f"업종별 관리자 생성: {admin_info['full_name']} ({industry.name})")
        
        db.session.commit()
        logger.info(f"샘플 업종별 관리자 {len(created_admins)}명 생성 완료")
        return created_admins
        
    except Exception as e:
        logger.error(f"업종별 관리자 생성 실패: {e}")
        db.session.rollback()
        return []

def main():
    """메인 함수"""
    with app.app_context():
        try:
            logger.info("업종 관리 데이터 초기화 시작...")
            
            # 1. 기본 업종 데이터 초기화
            logger.info("1. 업종 데이터 초기화...")
            if not initialize_industries():
                logger.error("업종 데이터 초기화 실패")
                return False
            
            # 2. 샘플 사용자 생성
            logger.info("2. 샘플 사용자 생성...")
            users = create_sample_users()
            if not users:
                logger.warning("샘플 사용자 생성 실패 또는 이미 존재")
            
            # 3. 샘플 업종별 관리자 생성
            logger.info("3. 샘플 업종별 관리자 생성...")
            admins = create_sample_industry_admins()
            if not admins:
                logger.warning("업종별 관리자 생성 실패 또는 이미 존재")
            
            logger.info("✅ 업종 관리 데이터 초기화 완료!")
            logger.info(f"   - 업종 데이터: 초기화 완료")
            logger.info(f"   - 샘플 사용자: {len(users)}명 생성")
            logger.info(f"   - 업종별 관리자: {len(admins)}명 생성")
            
            return True
            
        except Exception as e:
            logger.error(f"데이터 초기화 중 오류 발생: {e}")
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 