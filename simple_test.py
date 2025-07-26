#!/usr/bin/env python3
"""
간단한 API 테스트 스크립트
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_brand_creation():
    """브랜드 생성 테스트"""
    print("브랜드 생성 테스트 시작...")
    
    data = {
        "brand_name": "테스트 카페",
        "brand_description": "테스트용 카페 브랜드",
        "admin_name": "김브랜드",
        "admin_email": "brand@test.com",
        "admin_phone": "010-1234-5678"
    }
    
    print(f"전송할 데이터: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/industry/create_brand_with_admin",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"응답 상태 코드: {response.status_code}")
        print(f"응답 헤더: {dict(response.headers)}")
        print(f"응답 내용: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 성공!")
            return result
        else:
            print("❌ 실패!")
            return None
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return None

def test_brands_list():
    """브랜드 목록 조회 테스트"""
    print("\n브랜드 목록 조회 테스트 시작...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/industry/brands")
        
        print(f"응답 상태 코드: {response.status_code}")
        print(f"응답 내용: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 성공!")
            return result
        else:
            print("❌ 실패!")
            return None
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return None

if __name__ == "__main__":
    print("🚀 간단한 API 테스트 시작")
    
    # 브랜드 생성 테스트
    brand_result = test_brand_creation()
    
    # 브랜드 목록 조회 테스트
    brands_result = test_brands_list()
    
    print("\n🎉 테스트 완료!") 