#!/usr/bin/env python3
"""
인증 및 권한 관리 시스템 테스트 스크립트
"""

import requests
import json
import time
from datetime import datetime

# 테스트 설정
BASE_URL = "http://localhost:5000"
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!",
    "full_name": "테스트 사용자",
    "role": "employee"
}

class AuthSystemTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        
    def print_test_result(self, test_name, success, message=""):
        """테스트 결과 출력"""
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{test_name}: {status}")
        if message:
            print(f"  └─ {message}")
        print()
    
    def test_health_check(self):
        """인증 시스템 상태 확인 테스트"""
        try:
            response = self.session.get(f"{BASE_URL}/api/auth/health")
            if response.status_code == 200:
                data = response.json()
                self.print_test_result(
                    "인증 시스템 상태 확인",
                    True,
                    f"총 사용자: {data.get('data', {}).get('total_users', 0)}명"
                )
                return True
            else:
                self.print_test_result("인증 시스템 상태 확인", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("인증 시스템 상태 확인", False, f"오류: {str(e)}")
            return False
    
    def test_login_success(self):
        """성공적인 로그인 테스트"""
        try:
            response = self.session.post(f"{BASE_URL}/api/auth/login", json={
                "username": "admin",
                "password": "Admin123!"
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    self.access_token = data['data']['access_token']
                    self.refresh_token = data['data']['refresh_token']
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.access_token}'
                    })
                    self.print_test_result(
                        "로그인 성공",
                        True,
                        f"사용자: {data['data']['user']['username']}"
                    )
                    return True
                else:
                    self.print_test_result("로그인 성공", False, data.get('message', '알 수 없는 오류'))
                    return False
            else:
                self.print_test_result("로그인 성공", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("로그인 성공", False, f"오류: {str(e)}")
            return False
    
    def test_login_failed(self):
        """실패한 로그인 테스트"""
        try:
            response = self.session.post(f"{BASE_URL}/api/auth/login", json={
                "username": "admin",
                "password": "wrongpassword"
            })
            
            if response.status_code == 401:
                data = response.json()
                self.print_test_result(
                    "로그인 실패",
                    True,
                    data.get('message', '로그인 실패')
                )
                return True
            else:
                self.print_test_result("로그인 실패", False, f"예상 401, 실제: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("로그인 실패", False, f"오류: {str(e)}")
            return False
    
    def test_token_validation(self):
        """토큰 검증 테스트"""
        if not self.access_token:
            self.print_test_result("토큰 검증", False, "액세스 토큰이 없습니다")
            return False
        
        try:
            response = self.session.get(f"{BASE_URL}/api/auth/validate")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    self.print_test_result(
                        "토큰 검증",
                        True,
                        f"사용자: {data['data']['username']}, 역할: {data['data']['role']}"
                    )
                    return True
                else:
                    self.print_test_result("토큰 검증", False, data.get('message', '알 수 없는 오류'))
                    return False
            else:
                self.print_test_result("토큰 검증", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("토큰 검증", False, f"오류: {str(e)}")
            return False
    
    def test_password_validation(self):
        """비밀번호 정책 검증 테스트"""
        test_cases = [
            ("weak", "weak", False),
            ("Strong123!", "Strong123!", True),
            ("nouppercase123!", "nouppercase123!", False),
            ("NOLOWERCASE123!", "NOLOWERCASE123!", False),
            ("NoNumbers!", "NoNumbers!", False),
            ("NoSpecial123", "NoSpecial123", False),
        ]
        
        for test_name, password, expected in test_cases:
            try:
                response = self.session.post(f"{BASE_URL}/api/auth/validate-password", json={
                    "password": password
                })
                
                if response.status_code == 200:
                    data = response.json()
                    result = data.get('data', {}).get('valid', False)
                    success = result == expected
                    self.print_test_result(
                        f"비밀번호 검증 - {test_name}",
                        success,
                        f"예상: {expected}, 실제: {result}"
                    )
                else:
                    self.print_test_result(f"비밀번호 검증 - {test_name}", False, f"상태 코드: {response.status_code}")
            except Exception as e:
                self.print_test_result(f"비밀번호 검증 - {test_name}", False, f"오류: {str(e)}")
    
    def test_get_users(self):
        """사용자 목록 조회 테스트"""
        if not self.access_token:
            self.print_test_result("사용자 목록 조회", False, "액세스 토큰이 없습니다")
            return False
        
        try:
            response = self.session.get(f"{BASE_URL}/api/auth/users")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    users = data.get('data', [])
                    self.print_test_result(
                        "사용자 목록 조회",
                        True,
                        f"총 {len(users)}명의 사용자"
                    )
                    return True
                else:
                    self.print_test_result("사용자 목록 조회", False, data.get('message', '알 수 없는 오류'))
                    return False
            else:
                self.print_test_result("사용자 목록 조회", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("사용자 목록 조회", False, f"오류: {str(e)}")
            return False
    
    def test_create_user(self):
        """사용자 생성 테스트"""
        if not self.access_token:
            self.print_test_result("사용자 생성", False, "액세스 토큰이 없습니다")
            return False
        
        try:
            response = self.session.post(f"{BASE_URL}/api/auth/users", json=TEST_USER)
            
            if response.status_code == 201:
                data = response.json()
                if data.get('status') == 'success':
                    self.print_test_result(
                        "사용자 생성",
                        True,
                        f"생성된 사용자 ID: {data['data']['user_id']}"
                    )
                    return True
                else:
                    self.print_test_result("사용자 생성", False, data.get('message', '알 수 없는 오류'))
                    return False
            else:
                self.print_test_result("사용자 생성", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("사용자 생성", False, f"오류: {str(e)}")
            return False
    
    def test_get_roles(self):
        """역할 목록 조회 테스트"""
        if not self.access_token:
            self.print_test_result("역할 목록 조회", False, "액세스 토큰이 없습니다")
            return False
        
        try:
            response = self.session.get(f"{BASE_URL}/api/auth/roles")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    roles = data.get('data', [])
                    self.print_test_result(
                        "역할 목록 조회",
                        True,
                        f"총 {len(roles)}개의 역할"
                    )
                    return True
                else:
                    self.print_test_result("역할 목록 조회", False, data.get('message', '알 수 없는 오류'))
                    return False
            else:
                self.print_test_result("역할 목록 조회", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("역할 목록 조회", False, f"오류: {str(e)}")
            return False
    
    def test_get_permissions(self):
        """권한 목록 조회 테스트"""
        if not self.access_token:
            self.print_test_result("권한 목록 조회", False, "액세스 토큰이 없습니다")
            return False
        
        try:
            response = self.session.get(f"{BASE_URL}/api/auth/permissions")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    permissions = data.get('data', [])
                    self.print_test_result(
                        "권한 목록 조회",
                        True,
                        f"총 {len(permissions)}개의 권한"
                    )
                    return True
                else:
                    self.print_test_result("권한 목록 조회", False, data.get('message', '알 수 없는 오류'))
                    return False
            else:
                self.print_test_result("권한 목록 조회", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("권한 목록 조회", False, f"오류: {str(e)}")
            return False
    
    def test_get_security_events(self):
        """보안 이벤트 조회 테스트"""
        if not self.access_token:
            self.print_test_result("보안 이벤트 조회", False, "액세스 토큰이 없습니다")
            return False
        
        try:
            response = self.session.get(f"{BASE_URL}/api/auth/security-events?limit=10")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    events = data.get('data', [])
                    self.print_test_result(
                        "보안 이벤트 조회",
                        True,
                        f"총 {len(events)}개의 이벤트"
                    )
                    return True
                else:
                    self.print_test_result("보안 이벤트 조회", False, data.get('message', '알 수 없는 오류'))
                    return False
            else:
                self.print_test_result("보안 이벤트 조회", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("보안 이벤트 조회", False, f"오류: {str(e)}")
            return False
    
    def test_get_profile(self):
        """사용자 프로필 조회 테스트"""
        if not self.access_token:
            self.print_test_result("사용자 프로필 조회", False, "액세스 토큰이 없습니다")
            return False
        
        try:
            response = self.session.get(f"{BASE_URL}/api/auth/profile")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    profile = data.get('data', {})
                    self.print_test_result(
                        "사용자 프로필 조회",
                        True,
                        f"사용자: {profile.get('username')}, 역할: {profile.get('role')}"
                    )
                    return True
                else:
                    self.print_test_result("사용자 프로필 조회", False, data.get('message', '알 수 없는 오류'))
                    return False
            else:
                self.print_test_result("사용자 프로필 조회", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("사용자 프로필 조회", False, f"오류: {str(e)}")
            return False
    
    def test_unauthorized_access(self):
        """권한 없는 접근 테스트"""
        # 토큰 없이 접근
        try:
            response = requests.get(f"{BASE_URL}/api/auth/users")
            
            if response.status_code == 401:
                self.print_test_result("권한 없는 접근", True, "예상대로 401 오류 발생")
                return True
            else:
                self.print_test_result("권한 없는 접근", False, f"예상 401, 실제: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("권한 없는 접근", False, f"오류: {str(e)}")
            return False
    
    def test_logout(self):
        """로그아웃 테스트"""
        if not self.access_token:
            self.print_test_result("로그아웃", False, "액세스 토큰이 없습니다")
            return False
        
        try:
            response = self.session.post(f"{BASE_URL}/api/auth/logout", headers={
                'X-Session-ID': 'test-session-id'
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    self.print_test_result("로그아웃", True, "로그아웃 성공")
                    # 토큰 초기화
                    self.access_token = None
                    self.refresh_token = None
                    self.session.headers.pop('Authorization', None)
                    return True
                else:
                    self.print_test_result("로그아웃", False, data.get('message', '알 수 없는 오류'))
                    return False
            else:
                self.print_test_result("로그아웃", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("로그아웃", False, f"오류: {str(e)}")
            return False
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🔐 인증 및 권한 관리 시스템 테스트 시작")
        print("=" * 50)
        
        tests = [
            ("시스템 상태 확인", self.test_health_check),
            ("로그인 실패", self.test_login_failed),
            ("로그인 성공", self.test_login_success),
            ("토큰 검증", self.test_token_validation),
            ("비밀번호 정책 검증", self.test_password_validation),
            ("사용자 목록 조회", self.test_get_users),
            ("역할 목록 조회", self.test_get_roles),
            ("권한 목록 조회", self.test_get_permissions),
            ("보안 이벤트 조회", self.test_get_security_events),
            ("사용자 프로필 조회", self.test_get_profile),
            ("사용자 생성", self.test_create_user),
            ("로그아웃", self.test_logout),
            ("권한 없는 접근", self.test_unauthorized_access),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                time.sleep(0.5)  # API 호출 간격
            except Exception as e:
                self.print_test_result(test_name, False, f"테스트 실행 오류: {str(e)}")
        
        print("=" * 50)
        print(f"📊 테스트 결과: {passed}/{total} 통과")
        
        if passed == total:
            print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        else:
            print("⚠️ 일부 테스트가 실패했습니다.")
        
        return passed == total

def main():
    """메인 함수"""
    print("인증 및 권한 관리 시스템 테스트를 시작합니다...")
    print(f"테스트 대상 URL: {BASE_URL}")
    print()
    
    tester = AuthSystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ 인증 시스템이 정상적으로 작동합니다!")
    else:
        print("\n❌ 인증 시스템에 문제가 있습니다. 로그를 확인해주세요.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 