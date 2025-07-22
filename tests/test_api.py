"""
API 단위 테스트
"""

import pytest
import json
from datetime import datetime, date
from unittest.mock import patch, MagicMock
from swagger_docs import app, DataStore

@pytest.fixture
def client():
    """테스트용 Flask 클라이언트"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_headers():
    """인증 헤더"""
    return {'Authorization': 'Bearer test-token'}

class TestHealthCheck:
    """헬스체크 API 테스트"""
    
    def test_health_check_success(self, client):
        """헬스체크 성공 테스트"""
        response = client.get('/health')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['status'] == 'healthy'
        assert 'message' in data
        assert 'timestamp' in data

class TestAuthentication:
    """인증 API 테스트"""
    
    def test_login_success(self, client):
        """로그인 성공 테스트"""
        login_data = {
            'username': 'admin',
            'password': 'password123'
        }
        
        response = client.post('/security/auth/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert 'data' in data

    def test_login_invalid_credentials(self, client):
        """잘못된 로그인 정보 테스트"""
        login_data = {
            'username': 'invalid',
            'password': 'wrong'
        }
        
        response = client.post('/security/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 401
        assert data['success'] is False

class TestBrandAPI:
    """브랜드 API 테스트"""
    
    def test_get_brands_success(self, client):
        """브랜드 목록 조회 성공 테스트"""
        response = client.get('/brands')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert 'data' in data
        assert 'total' in data
        assert len(data['data']) > 0

    def test_create_brand_success(self, client):
        """브랜드 생성 성공 테스트"""
        brand_data = {
            'name': '테스트 브랜드',
            'industry': '테스트 업종',
            'description': '테스트 설명'
        }
        
        response = client.post('/brands',
                             data=json.dumps(brand_data),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 201
        assert data['name'] == brand_data['name']
        assert data['industry'] == brand_data['industry']

    def test_create_brand_validation_error(self, client):
        """브랜드 생성 검증 오류 테스트"""
        brand_data = {
            'name': '',  # 빈 이름
            'industry': '테스트 업종'
        }
        
        response = client.post('/brands',
                             data=json.dumps(brand_data),
                             content_type='application/json')
        
        assert response.status_code == 400

    def test_get_brand_detail_success(self, client):
        """브랜드 상세 조회 성공 테스트"""
        response = client.get('/brands/1')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['id'] == '1'
        assert 'name' in data
        assert 'industry' in data

    def test_get_brand_detail_not_found(self, client):
        """브랜드 상세 조회 실패 테스트"""
        response = client.get('/brands/999')
        
        assert response.status_code == 404

class TestBranchAPI:
    """매장 API 테스트"""
    
    def test_get_branches_success(self, client):
        """매장 목록 조회 성공 테스트"""
        response = client.get('/branches')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert len(data) > 0
        assert 'id' in data[0]
        assert 'name' in data[0]

    def test_create_branch_success(self, client):
        """매장 생성 성공 테스트"""
        branch_data = {
            'brand_id': '1',
            'name': '테스트 매장',
            'address': '테스트 주소',
            'phone': '02-1234-5678',
            'manager': '테스트 매니저'
        }
        
        response = client.post('/branches',
                             data=json.dumps(branch_data),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 201
        assert data['name'] == branch_data['name']
        assert data['brand_id'] == branch_data['brand_id']

    def test_get_branch_detail_success(self, client):
        """매장 상세 조회 성공 테스트"""
        response = client.get('/branches/1')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['id'] == '1'
        assert 'name' in data
        assert 'address' in data

class TestEmployeeAPI:
    """직원 API 테스트"""
    
    def test_get_employees_success(self, client):
        """직원 목록 조회 성공 테스트"""
        response = client.get('/employees')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert len(data) > 0
        assert 'id' in data[0]
        assert 'name' in data[0]

    def test_get_employee_detail_success(self, client):
        """직원 상세 조회 성공 테스트"""
        response = client.get('/employees/1')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['id'] == '1'
        assert 'name' in data
        assert 'position' in data

class TestScheduleAPI:
    """스케줄 API 테스트"""
    
    def test_get_schedules_success(self, client):
        """스케줄 목록 조회 성공 테스트"""
        response = client.get('/schedules')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert len(data) > 0
        assert 'id' in data[0]
        assert 'employee_id' in data[0]

    def test_create_schedule_success(self, client):
        """스케줄 생성 성공 테스트"""
        schedule_data = {
            'employee_id': '1',
            'date': '2024-01-15',
            'start_time': '09:00',
            'end_time': '18:00',
            'notes': '테스트 스케줄'
        }
        
        response = client.post('/schedules',
                             data=json.dumps(schedule_data),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 201
        assert data['employee_id'] == schedule_data['employee_id']
        assert data['start_time'] == schedule_data['start_time']

class TestEmployeeDashboard:
    """직원 대시보드 API 테스트"""
    
    def test_employee_dashboard_success(self, client):
        """직원 대시보드 조회 성공 테스트"""
        response = client.get('/employee/dashboard')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert 'employee' in data
        assert 'work_schedule' in data

    def test_clock_in_success(self, client):
        """출근 체크 성공 테스트"""
        clock_data = {
            'employee_id': '1',
            'timestamp': datetime.now().isoformat()
        }
        
        response = client.post('/employee/clock-in',
                             data=json.dumps(clock_data),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True

    def test_clock_out_success(self, client):
        """퇴근 체크 성공 테스트"""
        clock_data = {
            'employee_id': '1',
            'timestamp': datetime.now().isoformat()
        }
        
        response = client.post('/employee/clock-out',
                             data=json.dumps(clock_data),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True

class TestAdminDashboard:
    """관리자 대시보드 API 테스트"""
    
    def test_admin_dashboard_success(self, client):
        """관리자 대시보드 조회 성공 테스트"""
        response = client.get('/admin/dashboard')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert 'stats' in data
        assert 'recent_activities' in data
        assert 'brands' in data
        assert 'branches' in data

class TestNotificationAPI:
    """알림 API 테스트"""
    
    def test_notification_success(self, client):
        """알림 전송 성공 테스트"""
        notification_data = {
            'message': '테스트 알림 메시지'
        }
        
        response = client.post('/test/notification',
                             data=json.dumps(notification_data),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True

    def test_system_alert_success(self, client):
        """시스템 알림 성공 테스트"""
        alert_data = {
            'type': 'info',
            'message': '테스트 시스템 알림'
        }
        
        response = client.post('/test/system-alert',
                             data=json.dumps(alert_data),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True

class TestDataStore:
    """데이터 저장소 테스트"""
    
    def test_data_store_initialization(self):
        """데이터 저장소 초기화 테스트"""
        store = DataStore()
        
        assert len(store.brands) > 0
        assert len(store.branches) > 0
        assert len(store.employees) > 0
        assert len(store.schedules) > 0

    def test_brand_operations(self):
        """브랜드 CRUD 테스트"""
        store = DataStore()
        
        # 브랜드 생성
        brand_id = store.create_brand({
            'name': '테스트 브랜드',
            'industry': '테스트 업종',
            'description': '테스트 설명'
        })
        
        assert brand_id in store.brands
        
        # 브랜드 조회
        brand = store.get_brand(brand_id)
        assert brand['name'] == '테스트 브랜드'
        
        # 브랜드 업데이트
        store.update_brand(brand_id, {'name': '수정된 브랜드'})
        updated_brand = store.get_brand(brand_id)
        assert updated_brand['name'] == '수정된 브랜드'
        
        # 브랜드 삭제
        store.delete_brand(brand_id)
        assert brand_id not in store.brands

    def test_branch_operations(self):
        """매장 CRUD 테스트"""
        store = DataStore()
        
        # 매장 생성
        branch_id = store.create_branch({
            'brand_id': '1',
            'name': '테스트 매장',
            'address': '테스트 주소'
        })
        
        assert branch_id in store.branches
        
        # 매장 조회
        branch = store.get_branch(branch_id)
        assert branch['name'] == '테스트 매장'

    def test_employee_operations(self):
        """직원 CRUD 테스트"""
        store = DataStore()
        
        # 직원 생성
        employee_id = store.create_employee({
            'branch_id': '1',
            'name': '테스트 직원',
            'employee_id': 'EMP001',
            'position': '사원',
            'department': '영업'
        })
        
        assert employee_id in store.employees
        
        # 직원 조회
        employee = store.get_employee(employee_id)
        assert employee['name'] == '테스트 직원'

    def test_schedule_operations(self):
        """스케줄 CRUD 테스트"""
        store = DataStore()
        
        # 스케줄 생성
        schedule_id = store.create_schedule({
            'employee_id': '1',
            'date': '2024-01-15',
            'start_time': '09:00',
            'end_time': '18:00'
        })
        
        assert schedule_id in store.schedules
        
        # 스케줄 조회
        schedule = store.get_schedule(schedule_id)
        assert schedule['employee_id'] == '1'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
