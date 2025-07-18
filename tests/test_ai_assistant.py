import requests


def test_ai_report():
    """
    AI 경영 어시스턴트 리포트 API 정상 동작 테스트
    """
    res = requests.post("http://localhost:5000/api/ai/assistant/report")
    assert res.status_code == 200
    data = res.json()
    assert "llm_report" in data
    assert "diagnosis" in data
    assert "prediction" in data
    assert "improvement" in data


def test_ai_alerts():
    """
    AI 경영 어시스턴트 경보 API 정상 동작 테스트
    """
    res = requests.get("http://localhost:5000/api/ai/assistant/alerts")
    assert res.status_code == 200
    data = res.json()
    assert "alerts" in data
