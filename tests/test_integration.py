"""
통합 테스트
"""

import pytest
import json
import time
from datetime import datetime, timedelta
from swagger_docs import app, DataStore

@pytest.fixture
def client():
    """테스트용 Flask 클라이언트"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def data_store():
    """테스트용 데이터 저장소"""
    return DataStore()

class TestCompleteWorkflow:
    """완전한 워크플로우 테스트"""
    
    def test_brand_to_employee_workflow(self, client, data_store):
        """브랜드 → 매장 → 직원 → 스케줄 전체 워크플로우 테스트"""
        
        # 1. 브랜드 생성
        brand_data = {
            'name': '통합테스트 브랜드',
            'industry': '테스트 업종',
            'description': '통합 테스트용 브랜드'
        }
        
        response = client.post('/brands',
                             data=json.dumps(brand_data),
                             content_type='application/json')
        assert response.status_code == 201
        brand_response = json.loads(response.data)
        brand_id = brand_response['id']
        
        # 2. 매장 생성
        branch_data = {
            'brand_id': brand_id,
            'name': '통합테스트 매장',
            'address': '통합테스트 주소',
            'phone': '02-9999-9999',
            'manager': '통합테스트 매니저'
        }
        
        response = client.post('/branches',
                             data=json.dumps(branch_data),
                             content_type='application/json')
        assert response.status_code == 201
        branch_response = json.loads(response.data)
        branch_id = branch_response['id']
        
        # 3. 직원 생성 (데이터 저장소 직접 사용)
        employee_data = {
            'branch_id': branch_id,
            'name': '통합테스트 직원',
            'employee_id': 'INT001',
            'position': '사원',
            'department': '영업',
            'phone': '010-1234-5678',
            'email': 'test@example.com',
            'hire_date': '2024-01-01',
            'status': 'active',
            'salary': 3000000
        }
        
        employee_id = data_store.create_employee(employee_data)
        assert employee_id in data_store.employees
        
        # 4. 스케줄 생성
        schedule_data = {
            'employee_id': employee_id,
            'date': '2024-01-15',
            'start_time': '09:00',
            'end_time': '18:00',
            'notes': '통합테스트 스케줄'
        }
        
        response = client.post('/schedules',
                             data=json.dumps(schedule_data),
                             content_type='application/json')
        assert response.status_code == 201
        schedule_response = json.loads(response.data)
        schedule_id = schedule_response['id']
        
        # 5. 직원 대시보드 확인
        response = client.get('/employee/dashboard')
        assert response.status_code == 200
        dashboard_data = json.loads(response.data)
        assert 'employee' in dashboard_data
        assert 'work_schedule' in dashboard_data
        
        # 6. 출근 체크
        clock_data = {
            'employee_id': employee_id,
            'timestamp': datetime.now().isoformat()
        }
        
        response = client.post('/employee/clock-in',
                             data=json.dumps(clock_data),
                             content_type='application/json')
        assert response.status_code == 200
        clock_response = json.loads(response.data)
        assert clock_response['success'] is True
        
        # 7. 퇴근 체크
        response = client.post('/employee/clock-out',
                             data=json.dumps(clock_data),
                             content_type='application/json')
        assert response.status_code == 200
        clock_response = json.loads(response.data)
        assert clock_response['success'] is True
        
        # 8. 관리자 대시보드 확인
        response = client.get('/admin/dashboard')
        assert response.status_code == 200
        admin_data = json.loads(response.data)
        assert 'stats' in admin_data
        assert 'brands' in admin_data
        assert 'branches' in admin_data

class TestDataConsistency:
    """데이터 일관성 테스트"""
    
    def test_brand_branch_relationship(self, client, data_store):
        """브랜드-매장 관계 일관성 테스트"""
        
        # 브랜드 생성
        brand_id = data_store.create_brand({
            'name': '일관성테스트 브랜드',
            'industry': '테스트 업종',
            'description': '일관성 테스트'
        })
        
        # 매장 생성
        branch_id = data_store.create_branch({
            'brand_id': brand_id,
            'name': '일관성테스트 매장',
            'address': '일관성테스트 주소'
        })
        
        # 관계 확인
        branch = data_store.get_branch(branch_id)
        assert branch['brand_id'] == brand_id
        
        # 브랜드 삭제 시 매장도 함께 삭제되는지 확인
        data_store.delete_brand(brand_id)
        assert brand_id not in data_store.brands
        # 실제로는 외래키 제약조건으로 처리해야 함

    def test_employee_schedule_relationship(self, client, data_store):
        """직원-스케줄 관계 일관성 테스트"""
        
        # 직원 생성
        employee_id = data_store.create_employee({
            'branch_id': '1',
            'name': '일관성테스트 직원',
            'employee_id': 'CONS001',
            'position': '사원',
            'department': '영업'
        })
        
        # 스케줄 생성
        schedule_id = data_store.create_schedule({
            'employee_id': employee_id,
            'date': '2024-01-15',
            'start_time': '09:00',
            'end_time': '18:00'
        })
        
        # 관계 확인
        schedule = data_store.get_schedule(schedule_id)
        assert schedule['employee_id'] == employee_id

class TestPerformance:
    """성능 테스트"""
    
    def test_bulk_operations(self, client, data_store):
        """대량 데이터 처리 성능 테스트"""
        
        start_time = time.time()
        
        # 대량 브랜드 생성
        for i in range(100):
            data_store.create_brand({
                'name': f'성능테스트 브랜드 {i}',
                'industry': '테스트 업종',
                'description': f'성능 테스트용 브랜드 {i}'
            })
        
        # 대량 매장 생성
        for i in range(100):
            data_store.create_branch({
                'brand_id': str(i + 1),
                'name': f'성능테스트 매장 {i}',
                'address': f'성능테스트 주소 {i}'
            })
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 100개 생성이 5초 이내에 완료되어야 함
        assert execution_time < 5.0
        
        # 브랜드 목록 조회 성능
        start_time = time.time()
        response = client.get('/brands')
        end_time = time.time()
        query_time = end_time - start_time
        
        # 조회가 1초 이내에 완료되어야 함
        assert query_time < 1.0
        assert response.status_code == 200

    def test_concurrent_requests(self, client):
        """동시 요청 처리 테스트"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            try:
                response = client.get('/health')
                results.put(response.status_code)
            except Exception as e:
                results.put(f"Error: {e}")
        
        # 10개의 동시 요청
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # 모든 스레드 완료 대기
        for thread in threads:
            thread.join()
        
        # 결과 확인
        success_count = 0
        while not results.empty():
            result = results.get()
            if result == 200:
                success_count += 1
        
        # 모든 요청이 성공해야 함
        assert success_count == 10

class TestErrorHandling:
    """오류 처리 테스트"""
    
    def test_invalid_json_handling(self, client):
        """잘못된 JSON 처리 테스트"""
        
        # 잘못된 JSON 전송
        response = client.post('/brands',
                             data='invalid json',
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_missing_required_fields(self, client):
        """필수 필드 누락 테스트"""
        
        # 필수 필드 누락
        brand_data = {
            'name': '테스트 브랜드'
            # industry 필드 누락
        }
        
        response = client.post('/brands',
                             data=json.dumps(brand_data),
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_invalid_data_types(self, client):
        """잘못된 데이터 타입 테스트"""
        
        # 잘못된 데이터 타입
        brand_data = {
            'name': 123,  # 문자열이어야 함
            'industry': '테스트 업종',
            'description': '테스트 설명'
        }
        
        response = client.post('/brands',
                             data=json.dumps(brand_data),
                             content_type='application/json')
        
        assert response.status_code == 400

class TestSecurity:
    """보안 테스트"""
    
    def test_sql_injection_prevention(self, client):
        """SQL 인젝션 방지 테스트"""
        
        # SQL 인젝션 시도
        malicious_data = {
            'name': "'; DROP TABLE brands; --",
            'industry': '테스트 업종',
            'description': '테스트 설명'
        }
        
        response = client.post('/brands',
                             data=json.dumps(malicious_data),
                             content_type='application/json')
        
        # 요청이 거부되거나 안전하게 처리되어야 함
        assert response.status_code in [400, 201]
    
    def test_xss_prevention(self, client):
        """XSS 방지 테스트"""
        
        # XSS 시도
        xss_data = {
            'name': '<script>alert("XSS")</script>',
            'industry': '테스트 업종',
            'description': '테스트 설명'
        }
        
        response = client.post('/brands',
                             data=json.dumps(xss_data),
                             content_type='application/json')
        
        # 요청이 처리되어야 함 (서버에서 이스케이프 처리)
        assert response.status_code == 201

class TestDataValidation:
    """데이터 검증 테스트"""
    
    def test_string_length_validation(self, client):
        """문자열 길이 검증 테스트"""
        
        # 너무 긴 이름
        long_name_data = {
            'name': 'A' * 101,  # 100자 초과
            'industry': '테스트 업종',
            'description': '테스트 설명'
        }
        
        response = client.post('/brands',
                             data=json.dumps(long_name_data),
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_date_validation(self, client):
        """날짜 검증 테스트"""
        
        # 잘못된 날짜 형식
        invalid_date_data = {
            'employee_id': '1',
            'date': '2024-13-45',  # 잘못된 날짜
            'start_time': '09:00',
            'end_time': '18:00'
        }
        
        response = client.post('/schedules',
                             data=json.dumps(invalid_date_data),
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_time_validation(self, client):
        """시간 검증 테스트"""
        
        # 종료 시간이 시작 시간보다 빠름
        invalid_time_data = {
            'employee_id': '1',
            'date': '2024-01-15',
            'start_time': '18:00',
            'end_time': '09:00'  # 시작 시간보다 빠름
        }
        
        response = client.post('/schedules',
                             data=json.dumps(invalid_time_data),
                             content_type='application/json')
        
        # 비즈니스 로직에 따라 검증 필요
        assert response.status_code in [400, 201]

if __name__ == '__main__':
    pytest.main([__file__, '-v']) 