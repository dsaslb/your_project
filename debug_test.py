#!/usr/bin/env python3
"""
디버깅 테스트 스크립트
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_simple_request():
    """간단한 GET 요청 테스트"""
    print("1. 간단한 GET 요청 테스트...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   상태 코드: {response.status_code}")
        print(f"   응답: {response.text}")
    except Exception as e:
        print(f"   오류: {str(e)}")

def test_json_parsing():
    """JSON 파싱 테스트"""
    print("\n2. JSON 파싱 테스트...")
    
    # 간단한 JSON 데이터
    data = {"test": "value"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/test/setup",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        print(f"   상태 코드: {response.status_code}")
        print(f"   응답: {response.text}")
    except Exception as e:
        print(f"   오류: {str(e)}")

def test_brand_creation_step_by_step():
    """브랜드 생성 단계별 테스트"""
    print("\n3. 브랜드 생성 단계별 테스트...")
    
    # 1단계: 요청 데이터 준비
    data = {
        "brand_name": "테스트 카페",
        "brand_description": "테스트용 카페 브랜드",
        "admin_name": "김브랜드",
        "admin_email": "brand@test.com",
        "admin_phone": "010-1234-5678"
    }
    
    print(f"   전송할 데이터: {json.dumps(data, ensure_ascii=False)}")
    
    # 2단계: 요청 전송
    try:
        response = requests.post(
            f"{BASE_URL}/api/industry/create_brand_with_admin",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   상태 코드: {response.status_code}")
        print(f"   응답 헤더: {dict(response.headers)}")
        print(f"   응답 내용: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ 성공!")
            return result
        else:
            print("   ❌ 실패!")
            return None
            
    except Exception as e:
        print(f"   ❌ 오류: {str(e)}")
        return None

def test_form_data():
    """폼 데이터로 테스트"""
    print("\n4. 폼 데이터로 테스트...")
    
    data = {
        "brand_name": "테스트 카페",
        "brand_description": "테스트용 카페 브랜드",
        "admin_name": "김브랜드",
        "admin_email": "brand@test.com",
        "admin_phone": "010-1234-5678"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/industry/create_brand_with_admin",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"   상태 코드: {response.status_code}")
        print(f"   응답: {response.text}")
        
    except Exception as e:
        print(f"   ❌ 오류: {str(e)}")

if __name__ == "__main__":
    print("🔍 디버깅 테스트 시작")
    
    # 1. 간단한 GET 요청
    test_simple_request()
    
    # 2. JSON 파싱 테스트
    test_json_parsing()
    
    # 3. 브랜드 생성 단계별 테스트
    test_brand_creation_step_by_step()
    
    # 4. 폼 데이터로 테스트
    test_form_data()
    
    print("\n🎉 디버깅 테스트 완료!") 