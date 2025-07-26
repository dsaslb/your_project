#!/usr/bin/env python3
"""
매우 간단한 API 테스트
"""

import requests

BASE_URL = "http://localhost:5000"

def test_health():
    """헬스 체크"""
    print("1. 헬스 체크...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   상태 코드: {response.status_code}")
        print(f"   응답: {response.text}")
    except Exception as e:
        print(f"   오류: {str(e)}")

def test_industry_brands():
    """업종관리자 브랜드 목록 조회"""
    print("\n2. 업종관리자 브랜드 목록 조회...")
    try:
        response = requests.get(f"{BASE_URL}/api/industry/brands")
        print(f"   상태 코드: {response.status_code}")
        print(f"   응답: {response.text}")
    except Exception as e:
        print(f"   오류: {str(e)}")

def test_simple_post():
    """간단한 POST 요청"""
    print("\n3. 간단한 POST 요청...")
    try:
        data = {"test": "value"}
        response = requests.post(
            f"{BASE_URL}/api/test/setup",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        print(f"   상태 코드: {response.status_code}")
        print(f"   응답: {response.text}")
    except Exception as e:
        print(f"   오류: {str(e)}")

if __name__ == "__main__":
    print("🔍 매우 간단한 API 테스트 시작")
    
    test_health()
    test_industry_brands()
    test_simple_post()
    
    print("\n🎉 테스트 완료!") 