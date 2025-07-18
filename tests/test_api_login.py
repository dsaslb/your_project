import time

# from models_main import User  # 사용되지 않으므로 삭제


class TestAPILogin:
    """API 로그인 테스트 클래스"""

    def test_api_login_success(self, client, admin_user, session):
        """정상 로그인 테스트"""
        session.add(admin_user)
        session.commit()
        payload = {
            "username": admin_user.username,
            "password": "admin123",
        }
        resp = client.post("/api/auth/login", json=payload)

        assert resp.status_code == 200
        assert "access_token" in resp.json

    def test_api_login_fail_invalid_credentials(self, client):
        """잘못된 인증 정보로 로그인 실패 테스트"""
        payload = {"username": "wronguser", "password": "wrongpw"}
        resp = client.post("/api/auth/login", json=payload)

        assert resp.status_code == 401
        data = resp.json
        assert "message" in data
        assert "잘못된 사용자명 또는 비밀번호입니다" in data["message"]

    def test_api_login_missing_username(self, client):
        """사용자명 누락 테스트"""
        payload = {"password": "admin123"}
        resp = client.post("/api/auth/login", json=payload)

        assert resp.status_code == 400
        data = resp.json
        assert "message" in data
        assert "사용자명과 비밀번호를 입력해주세요" in data["message"]

    def test_api_login_missing_password(self, client, admin_user):
        """비밀번호 누락 테스트"""
        payload = {"username": admin_user.username}
        resp = client.post("/api/auth/login", json=payload)

        assert resp.status_code == 400
        data = resp.json
        assert "message" in data
        assert "사용자명과 비밀번호를 입력해주세요" in data["message"]

    def test_api_login_empty_payload(self, client):
        """빈 페이로드 테스트"""
        payload = {}
        resp = client.post("/api/auth/login", json=payload)

        assert resp.status_code == 400
        data = resp.json
        assert "message" in data
        assert "사용자명과 비밀번호를 입력해주세요" in data["message"]

    def test_api_login_invalid_json(self, client):
        """잘못된 JSON 형식 테스트"""
        headers = {"Content-Type": "application/json"}
        resp = client.post("/api/auth/login", data="invalid json", headers=headers)

        assert resp.status_code == 400

    def test_token_format(self, client, admin_user, session):
        """토큰 형식 검증 테스트"""
        session.add(admin_user)
        session.commit()
        payload = {
            "username": admin_user.username,
            "password": "admin123",
        }
        resp = client.post("/api/auth/login", json=payload)

        assert resp.status_code == 200
        data = resp.json
        assert "access_token" in data

        token_parts = data["access_token"].split(".")
        assert len(token_parts) == 3

    def test_token_uniqueness(self, client, admin_user, session):
        """토큰 고유성 테스트"""
        session.add(admin_user)
        session.commit()
        payload = {
            "username": admin_user.username,
            "password": "admin123",
        }

        # 첫 번째 로그인
        resp1 = client.post("/api/auth/login", json=payload)
        assert resp1.status_code == 200
        token1 = resp1.json.get("access_token")
        assert token1 is not None

        # 시간 차이를 두고 두 번째 로그인
        time.sleep(1)  # 1초 대기
        resp2 = client.post("/api/auth/login", json=payload)
        assert resp2.status_code == 200
        token2 = resp2.json.get("access_token")
        assert token2 is not None

        # 토큰이 다른지 확인 (시간이 다르므로 다른 토큰이 생성되어야 함)
        assert token1 != token2
