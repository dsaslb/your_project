import pytest
from app import app

def test_notify_test(client):
    response = client.get('/api/notify_test')
    assert response.status_code == 200
    assert response.get_json()['success'] is True 