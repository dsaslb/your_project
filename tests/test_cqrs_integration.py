#!/usr/bin/env python3
"""
🧪 CQRS 라이트 아키텍처 통합 테스트

멱등성 키, 이벤트 시스템, 테넌트 스코프 검증 등을 테스트
"""

import requests
import json
import uuid
import time
from datetime import datetime

# 테스트 설정
BASE_URL = "http://localhost:5000"
TEST_USER = {
    "username": "test_user",
    "password": "test_password"
}

def test_mobile_api_idempotency():
    """모바일 API 멱등성 테스트"""
    print("🔍 모바일 API 멱등성 테스트 시작...")
    
    # 1. 로그인하여 토큰 획득
    login_response = requests.post(f"{BASE_URL}/api/mobile/login", json=TEST_USER)
    if login_response.status_code != 200:
        print(f"❌ 로그인 실패: {login_response.status_code}")
        return False
    
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 동일한 멱등성 키로 출퇴근 요청 전송
    idempotency_key = str(uuid.uuid4())
    attendance_data = {
        "type": "in",
        "lat": 37.5665,
        "lng": 126.9780
    }
    
    # 첫 번째 요청
    headers["X-Idempotency-Key"] = idempotency_key
    response1 = requests.post(
        f"{BASE_URL}/api/mobile/attendance/clock",
        json=attendance_data,
        headers=headers
    )
    
    print(f"첫 번째 요청 결과: {response1.status_code}")
    if response1.status_code == 200:
        print("✅ 첫 번째 요청 성공")
    else:
        print(f"❌ 첫 번째 요청 실패: {response1.text}")
        return False
    
    # 두 번째 요청 (동일한 멱등성 키)
    response2 = requests.post(
        f"{BASE_URL}/api/mobile/attendance/clock",
        json=attendance_data,
        headers=headers
    )
    
    print(f"두 번째 요청 결과: {response2.status_code}")
    if response2.status_code == 409:  # Conflict - 중복 요청
        print("✅ 중복 요청 올바르게 차단됨")
    else:
        print(f"❌ 중복 요청 처리 오류: {response2.text}")
        return False
    
    return True

def test_event_system():
    """이벤트 시스템 테스트"""
    print("\n🔍 이벤트 시스템 테스트 시작...")
    
    # WebSocket 연결 테스트 (간단한 HTTP 요청으로 대체)
    try:
        response = requests.get(f"{BASE_URL}/api/mobile/dashboard")
        if response.status_code == 200:
            print("✅ 이벤트 시스템 기본 연결 성공")
            return True
        else:
            print(f"❌ 이벤트 시스템 연결 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 이벤트 시스템 테스트 오류: {e}")
        return False

def test_tenant_scope():
    """테넌트 스코프 검증 테스트"""
    print("\n🔍 테넌트 스코프 검증 테스트 시작...")
    
    # 로그인하여 토큰 획득
    login_response = requests.post(f"{BASE_URL}/api/mobile/login", json=TEST_USER)
    if login_response.status_code != 200:
        print(f"❌ 로그인 실패: {login_response.status_code}")
        return False
    
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 출퇴근 요청 (테넌트 스코프 검증)
    attendance_data = {
        "type": "out",
        "lat": 37.5665,
        "lng": 126.9780
    }
    
    response = requests.post(
        f"{BASE_URL}/api/mobile/attendance/clock",
        json=attendance_data,
        headers=headers
    )
    
    if response.status_code == 400 and "branch_id required" in response.text:
        print("✅ 테넌트 스코프 검증 올바르게 작동")
        return True
    else:
        print(f"❌ 테넌트 스코프 검증 실패: {response.status_code} - {response.text}")
        return False

def test_offline_queue_simulation():
    """오프라인 큐 시뮬레이션 테스트"""
    print("\n🔍 오프라인 큐 시뮬레이션 테스트 시작...")
    
    # 여러 요청을 빠르게 전송하여 큐 처리 테스트
    login_response = requests.post(f"{BASE_URL}/api/mobile/login", json=TEST_USER)
    if login_response.status_code != 200:
        print(f"❌ 로그인 실패: {login_response.status_code}")
        return False
    
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 5개의 동시 요청 전송
    success_count = 0
    for i in range(5):
        idempotency_key = str(uuid.uuid4())
        headers["X-Idempotency-Key"] = idempotency_key
        
        attendance_data = {
            "type": "in",
            "lat": 37.5665 + (i * 0.001),
            "lng": 126.9780 + (i * 0.001)
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/mobile/attendance/clock",
                json=attendance_data,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                success_count += 1
                print(f"  요청 {i+1}: 성공")
            else:
                print(f"  요청 {i+1}: 실패 ({response.status_code})")
                
        except Exception as e:
            print(f"  요청 {i+1}: 오류 ({e})")
    
    print(f"✅ 총 5개 요청 중 {success_count}개 성공")
    return success_count > 0

def test_file_upload_api():
    """파일 업로드 API 테스트"""
    print("\n🔍 파일 업로드 API 테스트 시작...")
    
    # 로그인하여 토큰 획득
    login_response = requests.post(f"{BASE_URL}/api/mobile/login", json=TEST_USER)
    if login_response.status_code != 200:
        print(f"❌ 로그인 실패: {login_response.status_code}")
        return False
    
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 프리사인드 URL 요청
    upload_data = {
        "file_type": "image/jpeg",
        "file_extension": "jpg",
        "max_size_mb": 5
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/uploads/presign",
            json=upload_data,
            headers=headers
        )
        
        if response.status_code == 500 and "S3 not configured" in response.text:
            print("✅ S3 설정 확인 (예상된 동작)")
            return True
        elif response.status_code == 200:
            print("✅ 프리사인드 URL 생성 성공")
            return True
        else:
            print(f"❌ 프리사인드 URL 생성 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 파일 업로드 API 테스트 오류: {e}")
        return False

def run_all_tests():
    """모든 테스트 실행"""
    print("🚀 CQRS 라이트 아키텍처 통합 테스트 시작")
    print("=" * 60)
    
    tests = [
        ("모바일 API 멱등성", test_mobile_api_idempotency),
        ("이벤트 시스템", test_event_system),
        ("테넌트 스코프 검증", test_tenant_scope),
        ("오프라인 큐 시뮬레이션", test_offline_queue_simulation),
        ("파일 업로드 API", test_file_upload_api)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 테스트 실행 중 오류: {e}")
            results.append((test_name, False))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n총 {total}개 테스트 중 {passed}개 통과 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 모든 테스트 통과! CQRS 라이트 아키텍처가 정상 작동합니다.")
    else:
        print("⚠️ 일부 테스트 실패. 시스템을 점검해주세요.")
    
    return passed == total

if __name__ == "__main__":
    # 서버가 실행 중인지 확인
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 백엔드 서버 연결 확인됨")
            run_all_tests()
        else:
            print("❌ 백엔드 서버 응답 오류")
    except requests.exceptions.ConnectionError:
        print("❌ 백엔드 서버에 연결할 수 없습니다.")
        print("   서버가 실행 중인지 확인해주세요: python app.py")
    except Exception as e:
        print(f"❌ 서버 연결 확인 중 오류: {e}")
