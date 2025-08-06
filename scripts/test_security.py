#!/usr/bin/env python3
"""
보안 시스템 테스트 스크립트
"""

import requests
import json
import time
from datetime import datetime

# 테스트 설정
BASE_URL = "http://localhost:5000"
TEST_USER = "admin"
TEST_PASSWORD = "admin123"

def print_test_result(test_name, success, message=""):
    """테스트 결과 출력"""
    status = "✅ 성공" if success else "❌ 실패"
    print(f"{test_name}: {status}")
    if message:
        print(f"  {message}")
    print()

def test_health_check():
    """보안 시스템 상태 확인 테스트"""
    print("=== 보안 시스템 상태 확인 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/security/health")
        success = response.status_code == 200
        data = response.json() if success else {}
        
        print_test_result(
            "상태 확인",
            success,
            f"상태: {data.get('status', 'unknown')}" if success else f"HTTP {response.status_code}"
        )
        return success
    except Exception as e:
        print_test_result("상태 확인", False, str(e))
        return False

def test_login():
    """로그인 테스트"""
    print("=== 로그인 테스트 ===")
    
    try:
        # 정상 로그인
        response = requests.post(f"{BASE_URL}/api/security/login", json={
            "username": TEST_USER,
            "password": TEST_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            session_id = data.get('session_id')
            
            print_test_result("정상 로그인", True, f"토큰: {token[:20]}...")
            return token, session_id
        else:
            print_test_result("정상 로그인", False, f"HTTP {response.status_code}")
            return None, None
            
    except Exception as e:
        print_test_result("로그인", False, str(e))
        return None, None

def test_invalid_login():
    """잘못된 로그인 테스트"""
    print("=== 잘못된 로그인 테스트 ===")
    
    try:
        # 잘못된 비밀번호로 로그인
        response = requests.post(f"{BASE_URL}/api/security/login", json={
            "username": TEST_USER,
            "password": "wrongpassword"
        })
        
        success = response.status_code == 401
        print_test_result("잘못된 비밀번호", success, f"HTTP {response.status_code}")
        
        # 존재하지 않는 사용자
        response = requests.post(f"{BASE_URL}/api/security/login", json={
            "username": "nonexistent",
            "password": "anypassword"
        })
        
        success = response.status_code == 401
        print_test_result("존재하지 않는 사용자", success, f"HTTP {response.status_code}")
        
    except Exception as e:
        print_test_result("잘못된 로그인", False, str(e))

def test_token_validation(token):
    """토큰 검증 테스트"""
    print("=== 토큰 검증 테스트 ===")
    
    if not token:
        print_test_result("토큰 검증", False, "토큰이 없습니다")
        return False
    
    try:
        # 유효한 토큰 검증
        response = requests.post(f"{BASE_URL}/api/security/validate-token", headers={
            "Authorization": f"Bearer {token}"
        })
        
        success = response.status_code == 200
        data = response.json() if success else {}
        
        print_test_result(
            "유효한 토큰 검증",
            success,
            f"사용자: {data.get('user_id', 'unknown')}" if success else f"HTTP {response.status_code}"
        )
        
        # 잘못된 토큰 검증
        response = requests.post(f"{BASE_URL}/api/security/validate-token", headers={
            "Authorization": "Bearer invalid_token"
        })
        
        success = response.status_code == 401
        print_test_result("잘못된 토큰 검증", success, f"HTTP {response.status_code}")
        
        return True
        
    except Exception as e:
        print_test_result("토큰 검증", False, str(e))
        return False

def test_password_validation():
    """비밀번호 강도 검증 테스트"""
    print("=== 비밀번호 강도 검증 테스트 ===")
    
    test_passwords = [
        ("weak", "123"),
        ("medium", "password123"),
        ("strong", "StrongPassword123!"),
        ("very_strong", "VeryStrongPassword123!@#")
    ]
    
    for strength, password in test_passwords:
        try:
            response = requests.post(f"{BASE_URL}/api/security/validate-password", json={
                "password": password
            })
            
            if response.status_code == 200:
                data = response.json()
                score = data.get('score', 0)
                is_valid = data.get('is_valid', False)
                
                print_test_result(
                    f"{strength} 비밀번호",
                    True,
                    f"점수: {score}, 유효: {is_valid}"
                )
            else:
                print_test_result(f"{strength} 비밀번호", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            print_test_result(f"{strength} 비밀번호", False, str(e))

def test_security_stats(token):
    """보안 통계 테스트"""
    print("=== 보안 통계 테스트 ===")
    
    if not token:
        print_test_result("보안 통계", False, "토큰이 없습니다")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/api/security/stats", headers={
            "Authorization": f"Bearer {token}"
        })
        
        if response.status_code == 200:
            data = response.json()
            
            print_test_result(
                "보안 통계 조회",
                True,
                f"활성 세션: {data.get('active_sessions', 0)}, "
                f"보안 점수: {data.get('security_score', 0)}"
            )
        else:
            print_test_result("보안 통계 조회", False, f"HTTP {response.status_code}")
            
    except Exception as e:
        print_test_result("보안 통계", False, str(e))

def test_security_events(token):
    """보안 이벤트 테스트"""
    print("=== 보안 이벤트 테스트 ===")
    
    if not token:
        print_test_result("보안 이벤트", False, "토큰이 없습니다")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/api/security/events", headers={
            "Authorization": f"Bearer {token}"
        })
        
        if response.status_code == 200:
            data = response.json()
            events = data.get('events', [])
            
            print_test_result(
                "보안 이벤트 조회",
                True,
                f"이벤트 수: {len(events)}"
            )
            
            # 이벤트 상세 정보 출력
            if events:
                print("  최근 이벤트:")
                for event in events[:3]:  # 최근 3개만
                    print(f"    - {event.get('event_type')}: {event.get('description')}")
                    
        else:
            print_test_result("보안 이벤트 조회", False, f"HTTP {response.status_code}")
            
    except Exception as e:
        print_test_result("보안 이벤트", False, str(e))

def test_sessions(token):
    """세션 관리 테스트"""
    print("=== 세션 관리 테스트 ===")
    
    if not token:
        print_test_result("세션 관리", False, "토큰이 없습니다")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/api/security/sessions", headers={
            "Authorization": f"Bearer {token}"
        })
        
        if response.status_code == 200:
            data = response.json()
            sessions = data.get('sessions', [])
            
            print_test_result(
                "세션 조회",
                True,
                f"활성 세션 수: {len(sessions)}"
            )
            
        else:
            print_test_result("세션 조회", False, f"HTTP {response.status_code}")
            
    except Exception as e:
        print_test_result("세션 관리", False, str(e))

def test_logout(token, session_id):
    """로그아웃 테스트"""
    print("=== 로그아웃 테스트 ===")
    
    if not token:
        print_test_result("로그아웃", False, "토큰이 없습니다")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        if session_id:
            headers["X-Session-ID"] = session_id
        
        response = requests.post(f"{BASE_URL}/api/security/logout", headers=headers)
        
        success = response.status_code == 200
        print_test_result("로그아웃", success, f"HTTP {response.status_code}")
        
        return success
        
    except Exception as e:
        print_test_result("로그아웃", False, str(e))
        return False

def test_unauthorized_access():
    """권한 없는 접근 테스트"""
    print("=== 권한 없는 접근 테스트 ===")
    
    try:
        # 토큰 없이 보호된 엔드포인트 접근
        response = requests.get(f"{BASE_URL}/api/security/stats")
        success = response.status_code == 401
        print_test_result("토큰 없는 접근", success, f"HTTP {response.status_code}")
        
        # 잘못된 토큰으로 접근
        response = requests.get(f"{BASE_URL}/api/security/stats", headers={
            "Authorization": "Bearer invalid_token"
        })
        success = response.status_code == 401
        print_test_result("잘못된 토큰 접근", success, f"HTTP {response.status_code}")
        
    except Exception as e:
        print_test_result("권한 없는 접근", False, str(e))

def main():
    """메인 테스트 함수"""
    print("🔒 보안 시스템 테스트 시작")
    print(f"테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"테스트 서버: {BASE_URL}")
    print("=" * 50)
    
    # 1. 상태 확인
    if not test_health_check():
        print("❌ 보안 시스템이 실행되지 않고 있습니다.")
        print("서버를 시작한 후 다시 시도해주세요.")
        return
    
    # 2. 잘못된 로그인 테스트
    test_invalid_login()
    
    # 3. 정상 로그인
    token, session_id = test_login()
    
    if token:
        # 4. 토큰 검증
        test_token_validation(token)
        
        # 5. 비밀번호 강도 검증
        test_password_validation()
        
        # 6. 보안 통계
        test_security_stats(token)
        
        # 7. 보안 이벤트
        test_security_events(token)
        
        # 8. 세션 관리
        test_sessions(token)
        
        # 9. 로그아웃
        test_logout(token, session_id)
    
    # 10. 권한 없는 접근 테스트
    test_unauthorized_access()
    
    print("=" * 50)
    print("🔒 보안 시스템 테스트 완료")
    print(f"완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 