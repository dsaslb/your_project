import requests
import json

# API 기본 URL
BASE_URL = "http://localhost:5000"

def test_login():
    """로그인 테스트"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"로그인 응답: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"로그인 성공: {data.get('message')}")
        return data.get('access_token')
    else:
        print(f"로그인 실패: {response.text}")
        return None

def test_create_improvement_request(token):
    """개선 요청 생성 테스트"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    request_data = {
        "title": "시스템 성능 개선 요청",
        "description": "현재 시스템이 느려서 개선이 필요합니다.",
        "category": "system",
        "priority": "high",
        "brand_id": 1,
        "store_id": 1
    }
    
    response = requests.post(f"{BASE_URL}/api/requests", json=request_data, headers=headers)
    print(f"개선 요청 생성 응답: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print(f"개선 요청 생성 성공: {data.get('message')}")
        return data.get('request_id')
    else:
        print(f"개선 요청 생성 실패: {response.text}")
        return None

def test_get_improvement_requests(token):
    """개선 요청 목록 조회 테스트"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/api/requests", headers=headers)
    print(f"개선 요청 목록 조회 응답: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"개선 요청 목록 조회 성공: {len(data.get('requests', []))}개 요청")
        for req in data.get('requests', []):
            print(f"  - {req.get('title')} ({req.get('status')})")
    else:
        print(f"개선 요청 목록 조회 실패: {response.text}")

def test_get_improvement_request(token, request_id):
    """특정 개선 요청 조회 테스트"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/api/requests/{request_id}", headers=headers)
    print(f"개선 요청 상세 조회 응답: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        req = data.get('request')
        print(f"개선 요청 상세 조회 성공: {req.get('title')}")
        print(f"  상태: {req.get('status')}")
        print(f"  우선순위: {req.get('priority')}")
    else:
        print(f"개선 요청 상세 조회 실패: {response.text}")

def test_approve_improvement_request(token, request_id):
    """개선 요청 승인 테스트"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    approve_data = {
        "comments": "승인합니다. 좋은 제안입니다."
    }
    
    response = requests.post(f"{BASE_URL}/api/requests/{request_id}/approve", json=approve_data, headers=headers)
    print(f"개선 요청 승인 응답: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"개선 요청 승인 성공: {data.get('message')}")
    else:
        print(f"개선 요청 승인 실패: {response.text}")

def main():
    """메인 테스트 함수"""
    print("=== 개선 요청 API 테스트 시작 ===")
    
    # 1. 로그인
    token = test_login()
    if not token:
        print("로그인 실패로 테스트를 중단합니다.")
        return
    
    print(f"토큰: {token[:50]}...")
    
    # 2. 개선 요청 생성
    request_id = test_create_improvement_request(token)
    if not request_id:
        print("개선 요청 생성 실패로 테스트를 중단합니다.")
        return
    
    # 3. 개선 요청 목록 조회
    test_get_improvement_requests(token)
    
    # 4. 특정 개선 요청 조회
    test_get_improvement_request(token, request_id)
    
    # 5. 개선 요청 승인
    test_approve_improvement_request(token, request_id)
    
    # 6. 승인 후 상태 확인
    test_get_improvement_request(token, request_id)
    
    print("=== 개선 요청 API 테스트 완료 ===")

if __name__ == "__main__":
    main() 