#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API를 통한 업종 관리 데이터 초기화 스크립트
웹 API를 사용하여 업종 데이터와 업종별 관리자 샘플 데이터 생성
"""

import requests
import json
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 서버 설정
BASE_URL = "http://192.168.45.44:5000"
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def wait_for_server():
    """서버가 준비될 때까지 대기"""
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                logger.info("서버가 준비되었습니다.")
                return True
        except requests.exceptions.RequestException:
            pass
        
        logger.info(f"서버 대기 중... ({attempt + 1}/{max_attempts})")
        time.sleep(2)
    
    logger.error("서버가 준비되지 않았습니다.")
    return False

def login_admin():
    """관리자 로그인하여 세션 획득"""
    try:
        # 로그인 페이지에서 세션 시작
        session = requests.Session()
        
        # 로그인 요청
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        response = session.post(f"{BASE_URL}/auth/login", data=login_data, allow_redirects=False)
        
        if response.status_code in [200, 302]:
            logger.info("관리자 로그인 성공")
            return session
        else:
            logger.error(f"로그인 실패: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"로그인 오류: {e}")
        return None

def create_industries(session):
    """업종 데이터 생성"""
    industries = [
        {
            "name": "레스토랑",
            "code": "RESTAURANT",
            "description": "일반 레스토랑 및 식당",
            "icon": "🍽️",
            "color": "#ff6b35",
            "is_active": True
        },
        {
            "name": "카페",
            "code": "CAFE",
            "description": "커피 전문점 및 카페",
            "icon": "☕",
            "color": "#8b4513",
            "is_active": True
        },
        {
            "name": "패스트푸드",
            "code": "FASTFOOD",
            "description": "패스트푸드 체인점",
            "icon": "🍔",
            "color": "#ff4757",
            "is_active": True
        },
        {
            "name": "고기집",
            "code": "BBQ",
            "description": "바베큐 및 고기 전문점",
            "icon": "🥩",
            "color": "#d63031",
            "is_active": True
        },
        {
            "name": "치킨집",
            "code": "CHICKEN",
            "description": "치킨 전문점",
            "icon": "🍗",
            "color": "#fdcb6e",
            "is_active": True
        },
        {
            "name": "피자집",
            "code": "PIZZA",
            "description": "피자 전문점",
            "icon": "🍕",
            "color": "#e17055",
            "is_active": True
        },
        {
            "name": "중식당",
            "code": "CHINESE",
            "description": "중국 음식 전문점",
            "icon": "🥢",
            "color": "#00b894",
            "is_active": True
        },
        {
            "name": "일식당",
            "code": "JAPANESE",
            "description": "일본 음식 전문점",
            "icon": "🍣",
            "color": "#74b9ff",
            "is_active": True
        },
        {
            "name": "분식점",
            "code": "SNACKBAR",
            "description": "분식 및 간편식",
            "icon": "🍜",
            "color": "#ffeaa7",
            "is_active": True
        },
        {
            "name": "디저트카페",
            "code": "DESSERT",
            "description": "디저트 및 베이커리",
            "icon": "🧁",
            "color": "#fd79a8",
            "is_active": True
        },
        {
            "name": "미용실",
            "code": "SALON",
            "description": "헤어 및 미용 서비스",
            "icon": "✂️",
            "color": "#a29bfe",
            "is_active": True
        },
        {
            "name": "네일샵",
            "code": "NAILSHOP",
            "description": "네일아트 전문점",
            "icon": "💅",
            "color": "#fd79a8",
            "is_active": True
        },
        {
            "name": "편의점",
            "code": "CONVENIENCE",
            "description": "편의점 및 소매업",
            "icon": "🏪",
            "color": "#00b894",
            "is_active": True
        },
        {
            "name": "의류매장",
            "code": "CLOTHING",
            "description": "의류 및 패션",
            "icon": "👕",
            "color": "#e84393",
            "is_active": True
        },
        {
            "name": "병원",
            "code": "HOSPITAL",
            "description": "병원 및 의료 서비스",
            "icon": "🏥",
            "color": "#00cec9",
            "is_active": True
        },
        {
            "name": "기타",
            "code": "OTHER",
            "description": "기타 업종",
            "icon": "🏢",
            "color": "#636e72",
            "is_active": True
        }
    ]
    
    created_count = 0
    
    for industry_data in industries:
        try:
            response = session.post(
                f"{BASE_URL}/api/admin/industries",
                headers=HEADERS,
                json=industry_data
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                if result.get('success'):
                    logger.info(f"업종 생성 성공: {industry_data['name']}")
                    created_count += 1
                else:
                    logger.warning(f"업종 생성 실패: {industry_data['name']} - {result.get('error', 'Unknown error')}")
            else:
                logger.warning(f"업종 생성 실패: {industry_data['name']} - HTTP {response.status_code}")
                
        except Exception as e:
            logger.error(f"업종 생성 오류: {industry_data['name']} - {e}")
    
    logger.info(f"업종 생성 완료: {created_count}개 성공")
    return created_count

def create_sample_industry_admins(session):
    """샘플 업종별 관리자 생성"""
    admins = [
        {
            "full_name": "김레스토랑",
            "contact_email": "restaurant@admin.com",
            "contact_phone": "010-1234-5678",
            "business_license": "1234567890",
            "company_name": "맛있는 레스토랑",
            "industry_code": "RESTAURANT"
        },
        {
            "full_name": "이카페",
            "contact_email": "cafe@admin.com",
            "contact_phone": "010-2345-6789",
            "business_license": "2345678901",
            "company_name": "향긋한 카페",
            "industry_code": "CAFE"
        },
        {
            "full_name": "박패스트",
            "contact_email": "fastfood@admin.com",
            "contact_phone": "010-3456-7890",
            "business_license": "3456789012",
            "company_name": "빠른 버거집",
            "industry_code": "FASTFOOD"
        },
        {
            "full_name": "최고기",
            "contact_email": "bbq@admin.com",
            "contact_phone": "010-4567-8901",
            "business_license": "4567890123",
            "company_name": "맛있는 고기집",
            "industry_code": "BBQ"
        },
        {
            "full_name": "정미용",
            "contact_email": "salon@admin.com",
            "contact_phone": "010-5678-9012",
            "business_license": "5678901234",
            "company_name": "예쁜 미용실",
            "industry_code": "SALON"
        }
    ]
    
    created_count = 0
    
    for admin_data in admins:
        try:
            response = session.post(
                f"{BASE_URL}/api/industry-admin",
                headers=HEADERS,
                json=admin_data
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                if result.get('success'):
                    logger.info(f"업종별 관리자 생성 성공: {admin_data['full_name']}")
                    created_count += 1
                else:
                    logger.warning(f"업종별 관리자 생성 실패: {admin_data['full_name']} - {result.get('error', 'Unknown error')}")
            else:
                logger.warning(f"업종별 관리자 생성 실패: {admin_data['full_name']} - HTTP {response.status_code}")
                
        except Exception as e:
            logger.error(f"업종별 관리자 생성 오류: {admin_data['full_name']} - {e}")
    
    logger.info(f"업종별 관리자 생성 완료: {created_count}개 성공")
    return created_count

def check_existing_data(session):
    """기존 데이터 확인"""
    try:
        # 업종 데이터 확인
        response = session.get(f"{BASE_URL}/api/admin/industries")
        if response.status_code == 200:
            industries = response.json()
            logger.info(f"기존 업종 데이터: {len(industries.get('industries', []))}개")
        
        # 업종별 관리자 확인
        response = session.get(f"{BASE_URL}/api/industry-admin")
        if response.status_code == 200:
            admins = response.json()
            logger.info(f"기존 업종별 관리자: {len(admins.get('admins', []))}개")
            
    except Exception as e:
        logger.error(f"기존 데이터 확인 오류: {e}")

def main():
    """메인 함수"""
    logger.info("API를 통한 업종 관리 데이터 초기화 시작...")
    
    # 1. 서버 준비 확인
    if not wait_for_server():
        logger.error("서버가 준비되지 않아 종료합니다.")
        return False
    
    # 2. 관리자 로그인
    session = login_admin()
    if not session:
        logger.error("관리자 로그인에 실패하여 종료합니다.")
        return False
    
    # 3. 기존 데이터 확인
    check_existing_data(session)
    
    # 4. 업종 데이터 생성
    logger.info("업종 데이터 생성 시작...")
    industry_count = create_industries(session)
    
    # 5. 업종별 관리자 생성
    logger.info("업종별 관리자 생성 시작...")
    admin_count = create_sample_industry_admins(session)
    
    # 6. 완료 보고
    logger.info("✅ API를 통한 데이터 초기화 완료!")
    logger.info(f"   - 생성된 업종: {industry_count}개")
    logger.info(f"   - 생성된 관리자: {admin_count}개")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n데이터 초기화가 완료되었습니다!")
        print("브라우저에서 http://192.168.45.44:5000/admin/backend/industry-management 페이지를 확인해보세요.")
    else:
        print("\n데이터 초기화에 실패했습니다.") 