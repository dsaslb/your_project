#!/usr/bin/env python3
"""
계층별 연동 테스트 스크립트
업종관리자 → 브랜드관리자 → 매장관리자 → 직원 순서로 생성하고 연동 확인
"""

import requests
import json
import time
from datetime import datetime

# 서버 설정
BASE_URL = "http://localhost:5000"

def test_industry_admin_creation():
    """업종관리자 브랜드 + 브랜드관리자 생성 테스트"""
    print("=" * 50)
    print("1. 업종관리자 브랜드 + 브랜드관리자 생성 테스트")
    print("=" * 50)
    
    # 브랜드 + 브랜드관리자 생성 데이터
    brand_data = {
        "brand_name": "테스트 카페",
        "brand_description": "테스트용 카페 브랜드",
        "admin_name": "김브랜드",
        "admin_email": "brand@test.com",
        "admin_phone": "010-1234-5678"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/industry/create_brand_with_admin",
            json=brand_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 브랜드 + 브랜드관리자 생성 성공!")
            print(f"   브랜드 ID: {result.get('brand_id')}")
            print(f"   브랜드관리자 ID: {result.get('admin_id')}")
            print(f"   임시 비밀번호: {result.get('temp_password')}")
            return result
        else:
            print(f"❌ 브랜드 + 브랜드관리자 생성 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 브랜드 + 브랜드관리자 생성 중 오류: {str(e)}")
        return None

def test_brand_admin_creation(brand_result):
    """브랜드관리자 매장 + 매장관리자 생성 테스트"""
    print("\n" + "=" * 50)
    print("2. 브랜드관리자 매장 + 매장관리자 생성 테스트")
    print("=" * 50)
    
    if not brand_result:
        print("❌ 브랜드 생성 결과가 없어 매장 생성 테스트를 건너뜁니다.")
        return None
    
    # 매장 + 매장관리자 생성 데이터
    store_data = {
        "store_name": "테스트 매장",
        "store_address": "서울시 강남구 테스트로 123",
        "store_phone": "02-1234-5678",
        "manager_name": "박매장",
        "manager_email": "store@test.com",
        "manager_phone": "010-2345-6789"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/brand/create_store_with_manager",
            json=store_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 매장 + 매장관리자 생성 성공!")
            print(f"   매장 ID: {result.get('store_id')}")
            print(f"   매장관리자 ID: {result.get('manager_id')}")
            print(f"   임시 비밀번호: {result.get('temp_password')}")
            return result
        else:
            print(f"❌ 매장 + 매장관리자 생성 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 매장 + 매장관리자 생성 중 오류: {str(e)}")
        return None

def test_store_admin_creation(store_result):
    """매장관리자 직원 생성 테스트"""
    print("\n" + "=" * 50)
    print("3. 매장관리자 직원 생성 테스트")
    print("=" * 50)
    
    if not store_result:
        print("❌ 매장 생성 결과가 없어 직원 생성 테스트를 건너뜁니다.")
        return None
    
    # 직원 생성 데이터
    employee_data = {
        "name": "이직원",
        "email": "employee@test.com",
        "phone": "010-3456-7890",
        "position": "바리스타",
        "department": "제조팀",
        "salary": "2500000",
        "hire_date": "2024-01-15"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/store/create_employee",
            json=employee_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 직원 생성 성공!")
            print(f"   직원 ID: {result.get('data', {}).get('employee_id')}")
            print(f"   임시 비밀번호: {result.get('data', {}).get('temp_password')}")
            return result
        else:
            print(f"❌ 직원 생성 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 직원 생성 중 오류: {str(e)}")
        return None

def test_data_verification():
    """생성된 데이터 검증 테스트"""
    print("\n" + "=" * 50)
    print("4. 생성된 데이터 검증 테스트")
    print("=" * 50)
    
    try:
        # 브랜드 목록 조회
        print("📋 브랜드 목록 조회:")
        response = requests.get(f"{BASE_URL}/api/industry/brands")
        if response.status_code == 200:
            brands = response.json().get('brands', [])
            for brand in brands:
                print(f"   - {brand.get('name')} (ID: {brand.get('id')})")
                print(f"     관리자: {brand.get('admin_name')} ({brand.get('admin_email')})")
                print(f"     매장 수: {brand.get('store_count')}")
        else:
            print(f"   ❌ 브랜드 목록 조회 실패: {response.status_code}")
        
        # 매장 목록 조회
        print("\n📋 매장 목록 조회:")
        response = requests.get(f"{BASE_URL}/api/brand/stores")
        if response.status_code == 200:
            stores = response.json().get('stores', [])
            for store in stores:
                print(f"   - {store.get('name')} (ID: {store.get('id')})")
                print(f"     관리자: {store.get('manager_name')} ({store.get('manager_email')})")
                print(f"     직원 수: {store.get('employee_count')}")
        else:
            print(f"   ❌ 매장 목록 조회 실패: {response.status_code}")
        
        # 직원 목록 조회
        print("\n📋 직원 목록 조회:")
        response = requests.get(f"{BASE_URL}/api/store/employees")
        if response.status_code == 200:
            employees = response.json().get('data', [])
            for employee in employees:
                print(f"   - {employee.get('name')} (ID: {employee.get('id')})")
                print(f"     직책: {employee.get('position')}")
                print(f"     부서: {employee.get('department')}")
        else:
            print(f"   ❌ 직원 목록 조회 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 데이터 검증 중 오류: {str(e)}")

def test_dashboard_access():
    """대시보드 접근 테스트"""
    print("\n" + "=" * 50)
    print("5. 대시보드 접근 테스트")
    print("=" * 50)
    
    dashboards = [
        ("업종관리자 대시보드", "/api/industry/dashboard"),
        ("브랜드관리자 대시보드", "/api/brand/dashboard"),
        ("매장관리자 대시보드", "/api/store/dashboard"),
        ("직원 대시보드", "/api/employee/dashboard")
    ]
    
    for name, endpoint in dashboards:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                print(f"✅ {name}: 접근 가능")
            else:
                print(f"❌ {name}: 접근 실패 ({response.status_code})")
        except Exception as e:
            print(f"❌ {name}: 오류 발생 ({str(e)})")

def main():
    """메인 테스트 함수"""
    print("🚀 계층별 연동 테스트 시작")
    print(f"📅 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 업종관리자 브랜드 + 브랜드관리자 생성
    brand_result = test_industry_admin_creation()
    
    # 2. 브랜드관리자 매장 + 매장관리자 생성
    store_result = test_brand_admin_creation(brand_result)
    
    # 3. 매장관리자 직원 생성
    employee_result = test_store_admin_creation(store_result)
    
    # 4. 생성된 데이터 검증
    test_data_verification()
    
    # 5. 대시보드 접근 테스트
    test_dashboard_access()
    
    print("\n" + "=" * 50)
    print("🎉 계층별 연동 테스트 완료!")
    print("=" * 50)
    
    if brand_result and store_result and employee_result:
        print("✅ 모든 계층별 생성이 성공적으로 완료되었습니다!")
        print("\n📊 생성 결과 요약:")
        print(f"   - 브랜드: {brand_result.get('brand_id')}")
        print(f"   - 매장: {store_result.get('store_id')}")
        print(f"   - 직원: {employee_result.get('data', {}).get('employee_id')}")
    else:
        print("❌ 일부 계층별 생성에 실패했습니다.")
        print("   서버 로그를 확인하여 오류를 해결해주세요.")

if __name__ == "__main__":
    main() 