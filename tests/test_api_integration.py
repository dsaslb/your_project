"""
API 통합 테스트
전체 API 엔드포인트의 통합 테스트
"""

import pytest
import json
from datetime import datetime
from app import app, db
from models_main import User, Brand, Industry, Branch
from werkzeug.security import generate_password_hash


class TestAPIIntegration:
    """API 통합 테스트 클래스"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """테스트 설정"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            self.create_test_data()
            yield
            db.session.remove()
            db.drop_all()
    
    def create_test_data(self):
        """테스트 데이터 생성"""
        # 업종 생성
        industry = Industry(
            name="음식점",
            code="RESTAURANT",
            description="음식점 업종"
        )
        db.session.add(industry)
        db.session.commit()
        
        # 브랜드 생성
        brand = Brand(
            name="테스트 브랜드",
            code="TEST_BRAND",
            industry_id=industry.id,
            description="테스트용 브랜드"
        )
        db.session.add(brand)
        db.session.commit()
        
        # 매장 생성
        branch = Branch(
            name="테스트 매장",
            brand_id=brand.id,
            industry_id=industry.id,
            address="서울시 강남구",
            phone="02-1234-5678"
        )
        db.session.add(branch)
        db.session.commit()
        
        # 관리자 사용자 생성
        admin_user = User(
            username="admin",
            email="admin@test.com",
            password_hash=generate_password_hash("admin123"),
            role="admin",
            name="관리자",
            status="approved"
        )
        db.session.add(admin_user)
        db.session.commit()
        
        # 일반 사용자 생성
        user = User(
            username="user",
            email="user@test.com",
            password_hash=generate_password_hash("user123"),
            role="employee",
            name="일반사용자",
            status="approved",
            branch_id=branch.id
        )
        db.session.add(user)
        db.session.commit()
    
    def test_health_check(self):
        """헬스 체크 API 테스트"""
        with app.test_client() as client:
            response = client.get('/health')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['status'] == 'healthy'
    
    def test_login_success(self):
        """로그인 성공 테스트"""
        with app.test_client() as client:
            response = client.post('/api/auth/login', json={
                'username': 'admin',
                'password': 'admin123'
            })
            
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'token' in data['data']
            assert data['data']['user']['username'] == 'admin'
    
    def test_login_failure(self):
        """로그인 실패 테스트"""
        with app.test_client() as client:
            response = client.post('/api/auth/login', json={
                'username': 'admin',
                'password': 'wrongpassword'
            })
            
            assert response.status_code == 401
    
    def test_staff_list_without_auth(self):
        """인증 없이 직원 목록 조회 테스트"""
        with app.test_client() as client:
            response = client.get('/api/staff/list')
            assert response.status_code == 401
    
    def test_staff_list_with_auth(self):
        """인증 후 직원 목록 조회 테스트"""
        with app.test_client() as client:
            # 먼저 로그인
            login_response = client.post('/api/auth/login', json={
                'username': 'admin',
                'password': 'admin123'
            })
            token = json.loads(login_response.data)['data']['token']
            
            # 직원 목록 조회
            response = client.get('/api/staff/list', headers={
                'Authorization': f'Bearer {token}'
            })
            
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'staff' in data['data']
            assert len(data['data']['staff']) >= 2  # admin + user
    
    def test_staff_create(self):
        """직원 생성 테스트"""
        with app.test_client() as client:
            # 로그인
            login_response = client.post('/api/auth/login', json={
                'username': 'admin',
                'password': 'admin123'
            })
            token = json.loads(login_response.data)['data']['token']
            
            # 새 직원 생성
            new_staff_data = {
                'username': 'newuser',
                'email': 'newuser@test.com',
                'password': 'newuser123',
                'name': '새사용자',
                'role': 'employee'
            }
            
            response = client.post('/api/staff/create', 
                                 json=new_staff_data,
                                 headers={'Authorization': f'Bearer {token}'})
            
            assert response.status_code == 201
            
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['username'] == 'newuser'
    
    def test_staff_create_validation(self):
        """직원 생성 유효성 검사 테스트"""
        with app.test_client() as client:
            # 로그인
            login_response = client.post('/api/auth/login', json={
                'username': 'admin',
                'password': 'admin123'
            })
            token = json.loads(login_response.data)['data']['token']
            
            # 필수 필드 누락
            invalid_data = {
                'username': 'newuser',
                'email': 'newuser@test.com'
                # password와 name 누락
            }
            
            response = client.post('/api/staff/create',
                                 json=invalid_data,
                                 headers={'Authorization': f'Bearer {token}'})
            
            assert response.status_code == 400
    
    def test_admin_dashboard_stats(self):
        """관리자 대시보드 통계 테스트"""
        with app.test_client() as client:
            # 로그인
            login_response = client.post('/api/auth/login', json={
                'username': 'admin',
                'password': 'admin123'
            })
            token = json.loads(login_response.data)['data']['token']
            
            response = client.get('/api/admin/dashboard-stats',
                                headers={'Authorization': f'Bearer {token}'})
            
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'total_users' in data['data']
            assert 'total_brands' in data['data']
            assert 'total_stores' in data['data']
    
    def test_unauthorized_access(self):
        """권한 없는 접근 테스트"""
        with app.test_client() as client:
            # 일반 사용자로 로그인
            login_response = client.post('/api/auth/login', json={
                'username': 'user',
                'password': 'user123'
            })
            token = json.loads(login_response.data)['data']['token']
            
            # 관리자 전용 API 접근
            response = client.get('/api/admin/dashboard-stats',
                                headers={'Authorization': f'Bearer {token}'})
            
            assert response.status_code == 403
    
    def test_invalid_token(self):
        """잘못된 토큰 테스트"""
        with app.test_client() as client:
            response = client.get('/api/staff/list', headers={
                'Authorization': 'Bearer invalid_token'
            })
            
            assert response.status_code == 401
    
    def test_rate_limiting(self):
        """요청 제한 테스트"""
        with app.test_client() as client:
            # 여러 번 로그인 시도
            for _ in range(10):
                response = client.post('/api/auth/login', json={
                    'username': 'admin',
                    'password': 'wrongpassword'
                })
            
            # 마지막 요청이 제한되어야 함
            assert response.status_code == 429
    
    def test_api_status(self):
        """API 상태 확인 테스트"""
        with app.test_client() as client:
            response = client.get('/api/status')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'status' in data
            assert 'timestamp' in data
            assert 'version' in data
    
    def test_not_found_endpoint(self):
        """존재하지 않는 엔드포인트 테스트"""
        with app.test_client() as client:
            response = client.get('/api/nonexistent')
            assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """허용되지 않는 HTTP 메서드 테스트"""
        with app.test_client() as client:
            response = client.put('/api/auth/login')
            assert response.status_code == 405


if __name__ == '__main__':
    pytest.main([__file__]) 