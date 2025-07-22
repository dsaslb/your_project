#!/usr/bin/env python3
"""
직원 API 테스트 스크립트
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_employee_dashboard():
    """직원 대시보드 API 테스트"""
    print("👤 직원 대시보드 API 테스트...")
    
    url = f"{BASE_URL}/api/employee/dashboard"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 직원 대시보드 데이터 로드 성공!")
                return result.get('data', {})
            else:
                print("❌ 직원 대시보드 데이터 로드 실패")
        else:
            print("❌ HTTP 오류")
            
    except Exception as e:
        print(f"❌ 요청 오류: {e}")
    
    return None

def test_employee_clock_in():
    """직원 출근 체크 API 테스트"""
    print("\n⏰ 직원 출근 체크 API 테스트...")
    
    url = f"{BASE_URL}/api/employee/clock-in"
    data = {
        "employee_id": "EMP001",
        "timestamp": "2025-07-20T19:30:00Z"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 출근 체크 성공!")
            else:
                print("❌ 출근 체크 실패")
        else:
            print("❌ HTTP 오류")
            
    except Exception as e:
        print(f"❌ 요청 오류: {e}")

def test_employee_clock_out():
    """직원 퇴근 체크 API 테스트"""
    print("\n🏠 직원 퇴근 체크 API 테스트...")
    
    url = f"{BASE_URL}/api/employee/clock-out"
    data = {
        "employee_id": "EMP001",
        "timestamp": "2025-07-20T18:00:00Z"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 퇴근 체크 성공!")
            else:
                print("❌ 퇴근 체크 실패")
        else:
            print("❌ HTTP 오류")
            
    except Exception as e:
        print(f"❌ 요청 오류: {e}")

def main():
    """메인 테스트 함수"""
    print("🚀 직원 API 테스트 시작...")
    print("=" * 50)
    
    # 직원 대시보드 테스트
    employee_data = test_employee_dashboard()
    
    # 출근 체크 테스트
    test_employee_clock_in()
    
    # 퇴근 체크 테스트
    test_employee_clock_out()
    
    print("\n" + "=" * 50)
    print("✅ 직원 API 테스트 완료!")
    print("\n📝 다음 단계:")
    print("1. 브라우저에서 http://localhost:3000/employee-dashboard 접속")
    print("2. 직원 대시보드 확인")
    print("3. 출근/퇴근 버튼 테스트")

if __name__ == "__main__":
    main() 