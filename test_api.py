#!/usr/bin/env python3
"""
API 테스트 스크립트
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_login():
    """로그인 API 테스트"""
    print("🔐 로그인 API 테스트...")
    
    url = f"{BASE_URL}/api/security/auth/login"
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 로그인 성공!")
                return result.get('data', {}).get('token')
            else:
                print("❌ 로그인 실패")
        else:
            print("❌ HTTP 오류")
            
    except Exception as e:
        print(f"❌ 요청 오류: {e}")
    
    return None

def test_notification(token=None):
    """알림 테스트 API"""
    print("\n🔔 알림 테스트 API...")
    
    url = f"{BASE_URL}/api/test/notification"
    data = {
        "type": "info",
        "message": "테스트 알림입니다."
    }
    
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ 알림 전송 성공!")
        else:
            print("❌ 알림 전송 실패")
            
    except Exception as e:
        print(f"❌ 요청 오류: {e}")

def test_system_alert(token=None):
    """시스템 알림 테스트 API"""
    print("\n🚨 시스템 알림 테스트 API...")
    
    url = f"{BASE_URL}/api/test/system-alert"
    data = {
        "severity": "medium",
        "message": "테스트 시스템 알림입니다."
    }
    
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ 시스템 알림 전송 성공!")
        else:
            print("❌ 시스템 알림 전송 실패")
            
    except Exception as e:
        print(f"❌ 요청 오류: {e}")

def main():
    """메인 테스트 함수"""
    print("🚀 API 테스트 시작...")
    print("=" * 50)
    
    # 로그인 테스트
    token = test_login()
    
    # 알림 테스트
    test_notification(token)
    
    # 시스템 알림 테스트
    test_system_alert(token)
    
    print("\n" + "=" * 50)
    print("✅ API 테스트 완료!")
    print("\n📝 다음 단계:")
    print("1. 브라우저에서 http://localhost:3000 접속")
    print("2. 로그인 페이지에서 admin/admin123으로 로그인")
    print("3. 관리자 대시보드에서 실시간 기능 확인")

if __name__ == "__main__":
    main() 