import time

import pytest

from models_main import Notice


class TestAPINotice:
    """공지사항 API 테스트 클래스"""

    def test_notice_get_list(self, client):
        """공지사항 목록 조회 테스트"""
        resp = client.get("/api/notices/")
        assert resp.status_code == 200
        data = resp.json
        assert "notices" in data
        assert isinstance(data["notices"], list)
        assert "total" in data

    def test_notice_get_list_with_pagination(self, client):
        """페이징 파라미터로 공지사항 목록 조회 테스트"""
        resp = client.get("/api/notices/?page=1&per_page=5")
        assert resp.status_code == 200
        data = resp.json
        assert len(data["notices"]) <= 5

    def test_notice_post_success(self, client, admin_headers):
        """공지사항 등록 성공 테스트"""
        payload = {
            "title": f"테스트 공지 {int(time.time())}",
            "content": "테스트 공지사항 내용입니다.",
            "category": "공지사항",
        }
        resp = client.post("/api/notices/", headers=admin_headers, json=payload)
        assert resp.status_code == 201
        assert "notice_id" in resp.json

    def test_notice_post_without_token(self, client):
        """토큰 없이 공지사항 등록 실패 테스트"""
        payload = {"title": "테스트 공지", "content": "테스트 공지사항 내용입니다."}
        resp = client.post("/api/notices/", json=payload)
        assert resp.status_code == 401

    def test_notice_post_missing_title(self, client, admin_headers):
        """제목 누락으로 공지사항 등록 실패 테스트"""
        payload = {"content": "테스트 공지사항 내용입니다."}
        resp = client.post("/api/notices/", headers=admin_headers, json=payload)
        assert resp.status_code == 400

    def test_notice_post_missing_content(self, client, admin_headers):
        """내용 누락으로 공지사항 등록 실패 테스트"""
        payload = {"title": "테스트 공지"}
        resp = client.post("/api/notices/", headers=admin_headers, json=payload)
        assert resp.status_code == 400

    def test_notice_post_with_category(self, client, admin_headers, session):
        """카테고리와 함께 공지사항 등록 테스트"""
        payload = {
            "title": f"카테고리 테스트 공지 {int(time.time())}",
            "content": "카테고리가 포함된 테스트 공지사항입니다.",
            "category": "자료실",
        }
        resp = client.post("/api/notices/", headers=admin_headers, json=payload)
        assert resp.status_code == 201
        notice_id = resp.json["notice_id"]

        notice = session.get(Notice, notice_id)
        assert notice.category == "자료실"

    def test_notice_post_and_get_integration(self, client, admin_headers):
        """공지사항 등록 후 목록 조회 통합 테스트"""
        unique_title = f"통합 테스트 공지 {int(time.time())}"
        payload = {"title": unique_title, "content": "통합 테스트용 공지사항입니다."}
        resp = client.post("/api/notices/", headers=admin_headers, json=payload)
        assert resp.status_code == 201

        get_resp = client.get("/api/notices/")
        assert get_resp.status_code == 200
        titles = [n["title"] for n in get_resp.json.get("notices", [])]
        assert unique_title in titles

    def test_notice_post_invalid_token(self, client):
        """잘못된 토큰으로 공지사항 등록 실패 테스트"""
        payload = {"title": "테스트 공지", "content": "테스트 공지사항 내용입니다."}
        resp = client.post(
            "/api/notices/",
            headers={"Authorization": "Bearer invalidtoken"},
            json=payload,
        )
        assert resp.status_code == 401

    def test_notice_post_empty_payload(self, client, admin_headers):
        """빈 페이로드로 공지사항 등록 실패 테스트"""
        payload = {}
        resp = client.post("/api/notices/", headers=admin_headers, json=payload)
        assert resp.status_code == 400

    def test_notice_response_format(self, client):
        """공지사항 응답 형식 검증 테스트"""
        resp = client.get("/api/notices/")
        assert resp.status_code == 200
        data = resp.json
        assert "notices" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
