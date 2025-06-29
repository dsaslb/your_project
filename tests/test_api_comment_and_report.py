import time

import pytest

from models import Notice
from models import NoticeComment as Comment


class TestAPIComment:
    """댓글 API 테스트 클래스"""

    def test_comment_post_and_delete(self, client, admin_headers, notice):
        """댓글 작성 및 삭제 테스트"""
        comment_resp = client.post(
            f"/api/notices/{notice.id}/comments",
            headers=admin_headers,
            json={"content": "테스트 댓글 내용입니다."},
        )
        assert comment_resp.status_code == 201
        assert "comment_id" in comment_resp.json
        comment_id = comment_resp.json["comment_id"]

        delete_resp = client.delete(
            f"/api/comments/{comment_id}", headers=admin_headers
        )
        assert delete_resp.status_code == 200
        assert "Comment deleted successfully" in delete_resp.json["msg"]

    def test_comment_post_without_token(self, client, notice):
        """토큰 없이 댓글 작성 실패 테스트"""
        resp = client.post(
            f"/api/notices/{notice.id}/comments", json={"content": "테스트 댓글"}
        )
        assert resp.status_code == 401


class TestAPIReport:
    """신고 API 테스트 클래스"""

    def test_report_notice(self, client, admin_headers, notice):
        """공지사항 신고 테스트"""
        report_resp = client.post(
            "/api/report/",
            headers=admin_headers,
            json={
                "target_type": "notice",
                "target_id": notice.id,
                "reason": "욕설/비방",
                "category": "부적절한 내용",
            },
        )
        assert report_resp.status_code == 201
        assert "msg" in report_resp.json

    def test_report_without_token(self, client, notice):
        """토큰 없이 신고 실패 테스트"""
        resp = client.post(
            "/api/report/",
            json={
                "target_type": "notice",
                "target_id": notice.id,
                "reason": "테스트",
                "category": "기타",
            },
        )
        assert resp.status_code == 401


class TestAPIAdminReports:
    """관리자 신고 관리 API 테스트 클래스"""

    def test_admin_reports_list(self, client, admin_headers):
        """관리자용 신고 목록 조회 테스트"""
        resp = client.get("/api/admin/reports/", headers=admin_headers)
        assert resp.status_code == 200
        assert "reports" in resp.json

    def test_admin_system_logs(self, client, admin_headers):
        """시스템 로그 조회 테스트"""
        resp = client.get("/api/admin/system-logs/", headers=admin_headers)
        assert resp.status_code == 200
        assert "logs" in resp.json

    def test_admin_report_statistics(self, client, admin_headers):
        """신고 통계 조회 테스트"""
        resp = client.get("/api/admin/report-stats/", headers=admin_headers)
        assert resp.status_code == 200
        assert "stats" in resp.json
