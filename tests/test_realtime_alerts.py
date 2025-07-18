import pytest
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_realtime_dashboard(client):
    """
    실시간 대시보드 API 정상 동작 테스트
    """
    response = client.get("/api/realtime/dashboard")
    assert response.status_code == 200
    data = response.get_json()
    assert "system_alerts" in data
    assert "performance_metrics" in data


def test_push_notification(client):
    """
    실시간 알림 발송 API 정상 동작 테스트
    """
    payload = {"message": "테스트 알림", "title": "테스트", "priority": "critical"}
    response = client.post("/api/realtime/notifications/push", json=payload)
    assert response.status_code in (200, 201)
    data = response.get_json()
    assert "success" in data or "notification_id" in data
