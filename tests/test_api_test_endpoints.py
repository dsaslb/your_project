import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_setup_test_environment(client):
    """E2E 테스트를 위한 환경 설정"""
    response = client.post('/api/test/setup')
    assert response.status_code == 200
    assert response.get_json()['success'] is True

def test_create_test_user(client):
    """E2E 테스트용 사용자 생성"""
    response = client.post('/api/test/create-test-user')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'user_id' in data

def test_cleanup_test_environment(client):
    """E2E 테스트 환경 정리"""
    response = client.post('/api/test/cleanup')
    assert response.status_code == 200
    assert response.get_json()['success'] is True 