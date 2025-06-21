import requests
import pytest
import time

API_URL = "http://localhost:5000"

class TestAPINotice:
    """API 공지사항 테스트 클래스"""
    
    def get_token(self):
        """테스트용 토큰 발급"""
        payload = {"username": "admin", "password": "admin123"}
        resp = requests.post(f"{API_URL}/api/auth/login", json=payload)
        if resp.status_code == 200:
            return resp.json()["token"]
        return None

    def test_notice_get_list(self):
        """공지사항 목록 조회 테스트"""
        resp = requests.get(f"{API_URL}/api/notices")
        
        assert resp.status_code == 200
        data = resp.json()
        assert "notices" in data
        assert isinstance(data["notices"], list)

    def test_notice_get_list_with_pagination(self):
        """페이징 파라미터로 공지사항 목록 조회 테스트"""
        resp = requests.get(f"{API_URL}/api/notices?page=1&per_page=5")
        
        assert resp.status_code == 200
        data = resp.json()
        assert "notices" in data
        assert isinstance(data["notices"], list)
        assert len(data["notices"]) <= 5

    def test_notice_post_success(self):
        """공지사항 등록 성공 테스트"""
        token = self.get_token()
        assert token is not None, "토큰 발급 실패"
        
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "title": f"테스트 공지 {int(time.time())}",
            "content": "테스트 공지사항 내용입니다.",
            "category": "공지사항"
        }
        
        resp = requests.post(f"{API_URL}/api/notices", headers=headers, json=payload)
        
        assert resp.status_code == 201
        data = resp.json()
        assert "message" in data
        assert "notice_id" in data
        assert data["message"] == "New notice created!"

    def test_notice_post_without_token(self):
        """토큰 없이 공지사항 등록 실패 테스트"""
        payload = {
            "title": "테스트 공지",
            "content": "테스트 공지사항 내용입니다."
        }
        
        resp = requests.post(f"{API_URL}/api/notices", json=payload)
        
        assert resp.status_code == 401
        data = resp.json()
        assert "message" in data

    def test_notice_post_missing_title(self):
        """제목 누락으로 공지사항 등록 실패 테스트"""
        token = self.get_token()
        assert token is not None, "토큰 발급 실패"
        
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "content": "테스트 공지사항 내용입니다."
        }
        
        resp = requests.post(f"{API_URL}/api/notices", headers=headers, json=payload)
        
        assert resp.status_code == 400
        data = resp.json()
        assert "msg" in data
        assert "Title and content are required" in data["msg"]

    def test_notice_post_missing_content(self):
        """내용 누락으로 공지사항 등록 실패 테스트"""
        token = self.get_token()
        assert token is not None, "토큰 발급 실패"
        
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "title": "테스트 공지"
        }
        
        resp = requests.post(f"{API_URL}/api/notices", headers=headers, json=payload)
        
        assert resp.status_code == 400
        data = resp.json()
        assert "msg" in data
        assert "Title and content are required" in data["msg"]

    def test_notice_post_with_category(self):
        """카테고리와 함께 공지사항 등록 테스트"""
        token = self.get_token()
        assert token is not None, "토큰 발급 실패"
        
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "title": f"카테고리 테스트 공지 {int(time.time())}",
            "content": "카테고리가 포함된 테스트 공지사항입니다.",
            "category": "자료실"
        }
        
        resp = requests.post(f"{API_URL}/api/notices", headers=headers, json=payload)
        
        assert resp.status_code == 201
        data = resp.json()
        assert "notice_id" in data

    def test_notice_post_and_get_integration(self):
        """공지사항 등록 후 목록 조회 통합 테스트"""
        token = self.get_token()
        assert token is not None, "토큰 발급 실패"
        
        # 공지사항 등록
        headers = {"Authorization": f"Bearer {token}"}
        unique_title = f"통합 테스트 공지 {int(time.time())}"
        payload = {
            "title": unique_title,
            "content": "통합 테스트용 공지사항입니다."
        }
        
        resp = requests.post(f"{API_URL}/api/notices", headers=headers, json=payload)
        assert resp.status_code == 201
        
        # 잠시 대기 후 목록 조회
        time.sleep(1)
        
        # 공지사항 목록 조회
        resp2 = requests.get(f"{API_URL}/api/notices")
        assert resp2.status_code == 200
        
        notices = resp2.json()["notices"]
        # 등록한 공지사항이 목록에 있는지 확인
        found = any(notice["title"] == unique_title for notice in notices)
        assert found, f"등록한 공지사항 '{unique_title}'을 목록에서 찾을 수 없습니다"

    def test_notice_post_invalid_token(self):
        """잘못된 토큰으로 공지사항 등록 실패 테스트"""
        headers = {"Authorization": "Bearer invalid_token_here"}
        payload = {
            "title": "테스트 공지",
            "content": "테스트 공지사항 내용입니다."
        }
        
        resp = requests.post(f"{API_URL}/api/notices", headers=headers, json=payload)
        
        assert resp.status_code == 401

    def test_notice_post_empty_payload(self):
        """빈 페이로드로 공지사항 등록 실패 테스트"""
        token = self.get_token()
        assert token is not None, "토큰 발급 실패"
        
        headers = {"Authorization": f"Bearer {token}"}
        payload = {}
        
        resp = requests.post(f"{API_URL}/api/notices", headers=headers, json=payload)
        
        assert resp.status_code == 400
        data = resp.json()
        assert "msg" in data
        assert "Title and content are required" in data["msg"]

    def test_notice_response_format(self):
        """공지사항 응답 형식 검증 테스트"""
        resp = requests.get(f"{API_URL}/api/notices")
        
        assert resp.status_code == 200
        data = resp.json()
        assert "notices" in data
        
        if data["notices"]:  # 공지사항이 있는 경우
            notice = data["notices"][0]
            required_fields = ["id", "title", "author", "created_at"]
            for field in required_fields:
                assert field in notice, f"필수 필드 '{field}'가 응답에 없습니다" 