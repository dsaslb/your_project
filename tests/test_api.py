import pytest
import json
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    """테스트 클라이언트 생성"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def auth_headers():
    """인증 헤더 생성"""
    def _auth_headers(token):
        return {'Authorization': f'Bearer {token}'}
    return _auth_headers

@pytest.fixture
def test_user():
    """테스트 사용자 생성"""
    user = User(
        username='testuser',
        name='Test User',
        email='test@example.com',
        role='store_manager',
        is_active=True
    )
    user.set_password('testpass123')
    return user

class TestAuthAPI:
    """인증 API 테스트"""
    
    def test_login_success(self, client, test_user):
        """로그인 성공 테스트"""
        with client.application.app_context():
            db.session.add(test_user)
            db.session.commit()
        
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'user' in data
        assert data['user']['username'] == 'testuser'
    
    def test_login_invalid_credentials(self, client):
        """잘못된 로그인 정보 테스트"""
        response = client.post('/api/auth/login', json={
            'username': 'wronguser',
            'password': 'wrongpass'
        })
        
        assert response.status_code == 401
    
    def test_login_missing_fields(self, client):
        """필수 필드 누락 테스트"""
        response = client.post('/api/auth/login', json={
            'username': 'testuser'
        })
        
        assert response.status_code == 400

class TestUserManagementAPI:
    """사용자 관리 API 테스트"""
    
    def test_get_users_unauthorized(self, client):
        """권한 없는 사용자 목록 조회 테스트"""
        response = client.get('/api/modules/user/users')
        assert response.status_code == 401
    
    def test_get_users_success(self, client, test_user, auth_headers):
        """사용자 목록 조회 성공 테스트"""
        with client.application.app_context():
            db.session.add(test_user)
            db.session.commit()
        
        # 먼저 로그인하여 토큰 획득
        login_response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'testpass123'
        })
        token = json.loads(login_response.data)['access_token']
        
        response = client.get('/api/modules/user/users', 
                            headers=auth_headers(token))
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'users' in data
        assert 'pagination' in data

class TestNotificationAPI:
    """알림 API 테스트"""
    
    def test_get_notifications_unauthorized(self, client):
        """권한 없는 알림 조회 테스트"""
        response = client.get('/api/modules/notification/notifications')
        assert response.status_code == 401
    
    def test_get_notifications_success(self, client, test_user, auth_headers):
        """알림 조회 성공 테스트"""
        with client.application.app_context():
            db.session.add(test_user)
            db.session.commit()
        
        # 로그인하여 토큰 획득
        login_response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'testpass123'
        })
        token = json.loads(login_response.data)['access_token']
        
        response = client.get('/api/modules/notification/notifications', 
                            headers=auth_headers(token))
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'notifications' in data

class TestScheduleAPI:
    """스케줄 API 테스트"""
    
    def test_get_schedules_unauthorized(self, client):
        """권한 없는 스케줄 조회 테스트"""
        response = client.get('/api/modules/schedule/schedules')
        assert response.status_code == 401
    
    def test_get_schedules_success(self, client, test_user, auth_headers):
        """스케줄 조회 성공 테스트"""
        with client.application.app_context():
            db.session.add(test_user)
            db.session.commit()
        
        # 로그인하여 토큰 획득
        login_response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'testpass123'
        })
        token = json.loads(login_response.data)['access_token']
        
        response = client.get('/api/modules/schedule/schedules', 
                            headers=auth_headers(token))
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'schedules' in data

class TestOptimizationAPI:
    """최적화 API 테스트"""
    
    def test_optimized_users_unauthorized(self, client):
        """권한 없는 최적화된 사용자 조회 테스트"""
        response = client.get('/api/modules/optimization/users/optimized')
        assert response.status_code == 401
    
    def test_cached_stats_unauthorized(self, client):
        """권한 없는 캐시된 통계 조회 테스트"""
        response = client.get('/api/modules/optimization/stats/cached')
        assert response.status_code == 401

class TestMonitoringAPI:
    """모니터링 API 테스트"""
    
    def test_system_status_unauthorized(self, client):
        """권한 없는 시스템 상태 조회 테스트"""
        response = client.get('/api/modules/monitoring/system/status')
        assert response.status_code == 401
    
    def test_error_logs_unauthorized(self, client):
        """권한 없는 오류 로그 조회 테스트"""
        response = client.get('/api/modules/monitoring/logs/errors')
        assert response.status_code == 401

class TestHealthCheck:
    """헬스 체크 테스트"""
    
    def test_health_check(self, client):
        """헬스 체크 API 테스트"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data

class TestCORS:
    """CORS 테스트"""
    
    def test_cors_headers(self, client):
        """CORS 헤더 확인 테스트"""
        response = client.get('/api/health')
        assert 'Access-Control-Allow-Origin' in response.headers
        assert 'Access-Control-Allow-Credentials' in response.headers

if __name__ == '__main__':
    pytest.main([__file__]) 