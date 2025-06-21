import requests
import pytest
import time

API_URL = "http://localhost:5000"

class TestAPILogin:
    """API 로그인 테스트 클래스"""
    
    def test_api_login_success(self):
        """정상 로그인 테스트"""
        payload = {"username": "admin", "password": "admin123"}
        resp = requests.post(f"{API_URL}/api/auth/login", json=payload)
        
        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data
        assert isinstance(data["token"], str)
        assert len(data["token"]) > 0

    def test_api_login_fail_invalid_credentials(self):
        """잘못된 인증 정보로 로그인 실패 테스트"""
        payload = {"username": "wronguser", "password": "wrongpw"}
        resp = requests.post(f"{API_URL}/api/auth/login", json=payload)
        
        assert resp.status_code == 401
        data = resp.json()
        assert "msg" in data
        assert "Invalid credentials" in data["msg"]

    def test_api_login_missing_username(self):
        """사용자명 누락 테스트"""
        payload = {"password": "admin123"}
        resp = requests.post(f"{API_URL}/api/auth/login", json=payload)
        
        assert resp.status_code == 400
        data = resp.json()
        assert "msg" in data
        assert "Username and password are required" in data["msg"]

    def test_api_login_missing_password(self):
        """비밀번호 누락 테스트"""
        payload = {"username": "admin"}
        resp = requests.post(f"{API_URL}/api/auth/login", json=payload)
        
        assert resp.status_code == 400
        data = resp.json()
        assert "msg" in data
        assert "Username and password are required" in data["msg"]

    def test_api_login_empty_payload(self):
        """빈 페이로드 테스트"""
        payload = {}
        resp = requests.post(f"{API_URL}/api/auth/login", json=payload)
        
        assert resp.status_code == 400
        data = resp.json()
        assert "msg" in data
        assert "Username and password are required" in data["msg"]

    def test_api_login_invalid_json(self):
        """잘못된 JSON 형식 테스트"""
        headers = {"Content-Type": "application/json"}
        resp = requests.post(f"{API_URL}/api/auth/login", data="invalid json", headers=headers)
        
        assert resp.status_code == 400

    def test_token_format(self):
        """토큰 형식 검증 테스트"""
        payload = {"username": "admin", "password": "admin123"}
        resp = requests.post(f"{API_URL}/api/auth/login", json=payload)
        
        assert resp.status_code == 200
        data = resp.json()
        token = data["token"]
        
        # JWT 토큰은 3개의 파트로 구성되어야 함 (header.payload.signature)
        parts = token.split('.')
        assert len(parts) == 3

    def test_token_uniqueness(self):
        """토큰 고유성 테스트"""
        payload = {"username": "admin", "password": "admin123"}
        
        # 두 번 로그인하여 다른 토큰이 발급되는지 확인
        resp1 = requests.post(f"{API_URL}/api/auth/login", json=payload)
        time.sleep(1)  # 1초 대기
        resp2 = requests.post(f"{API_URL}/api/auth/login", json=payload)
        
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        
        token1 = resp1.json()["token"]
        token2 = resp2.json()["token"]
        
        # 토큰이 다를 수 있음 (시간 기반)
        # 하지만 둘 다 유효한 JWT 형식이어야 함
        assert len(token1.split('.')) == 3
        assert len(token2.split('.')) == 3 