#!/usr/bin/env python3
"""
실제 데이터를 제공하는 Flask API 서버
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import json
import uuid
from typing import Dict, List, Any

app = Flask(__name__)
CORS(app)

# 실제 데이터 저장소 (메모리 기반, 실제로는 DB 사용)
class DataStore:
    def __init__(self):
        self.brands = {
            "1": {
                "id": "1",
                "name": "스타벅스",
                "industry": "카페",
                "description": "글로벌 커피 체인점",
                "created_at": "2024-01-01T00:00:00Z",
                "status": "active"
            },
            "2": {
                "id": "2", 
                "name": "배스킨라빈스",
                "industry": "아이스크림",
                "description": "아이스크림 전문점",
                "created_at": "2024-01-02T00:00:00Z",
                "status": "active"
            }
        }
        
        self.branches = {
            "1": {
                "id": "1",
                "brand_id": "1",
                "name": "강남점",
                "address": "서울시 강남구 테헤란로 123",
                "phone": "02-1234-5678",
                "manager": "김매니저",
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z"
            },
            "2": {
                "id": "2",
                "brand_id": "1", 
                "name": "홍대점",
                "address": "서울시 마포구 홍대로 456",
                "phone": "02-2345-6789",
                "manager": "이매니저",
                "status": "active",
                "created_at": "2024-01-02T00:00:00Z"
            },
            "3": {
                "id": "3",
                "brand_id": "2",
                "name": "신촌점",
                "address": "서울시 서대문구 신촌로 789",
                "phone": "02-3456-7890",
                "manager": "박매니저",
                "status": "active",
                "created_at": "2024-01-03T00:00:00Z"
            }
        }
        
        self.employees = {
            "1": {
                "id": "1",
                "branch_id": "1",
                "name": "김철수",
                "employee_id": "EMP001",
                "position": "매니저",
                "department": "영업팀",
                "phone": "010-1234-5678",
                "email": "kim.cheolsu@company.com",
                "hire_date": "2023-01-01",
                "status": "active",
                "salary": 3500000
            },
            "2": {
                "id": "2",
                "branch_id": "1",
                "name": "이영희",
                "employee_id": "EMP002", 
                "position": "바리스타",
                "department": "제조팀",
                "phone": "010-2345-6789",
                "email": "lee.younghee@company.com",
                "hire_date": "2023-02-01",
                "status": "active",
                "salary": 2800000
            },
            "3": {
                "id": "3",
                "branch_id": "2",
                "name": "박민수",
                "employee_id": "EMP003",
                "position": "매니저",
                "department": "영업팀", 
                "phone": "010-3456-7890",
                "email": "park.minsu@company.com",
                "hire_date": "2023-03-01",
                "status": "active",
                "salary": 3200000
            }
        }
        
        self.schedules = {
            "1": {
                "id": "1",
                "employee_id": "1",
                "date": datetime.date.today().isoformat(),
                "start_time": "09:00",
                "end_time": "18:00",
                "status": "scheduled",
                "notes": ""
            },
            "2": {
                "id": "2", 
                "employee_id": "2",
                "date": datetime.date.today().isoformat(),
                "start_time": "10:00",
                "end_time": "19:00",
                "status": "working",
                "notes": ""
            },
            "3": {
                "id": "3",
                "employee_id": "3", 
                "date": datetime.date.today().isoformat(),
                "start_time": "08:00",
                "end_time": "17:00",
                "status": "completed",
                "notes": ""
            }
        }
        
        self.attendance_records = []
        self.sales_records = []

# 전역 데이터 저장소
data_store = DataStore()

# 헬스체크
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': '서버가 정상적으로 실행 중입니다.',
        'timestamp': datetime.datetime.now().isoformat()
    })

# 인증 관련
@app.route('/api/security/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username == "admin" and password == "admin123":
        return jsonify({
            'success': True,
            'message': '로그인 성공',
            'data': {
                'token': 'mock-jwt-token-' + str(uuid.uuid4()),
                'user': {
                    'id': 1,
                    'username': username,
                    'role': 'admin',
                    'name': '관리자'
                }
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': '아이디 또는 비밀번호가 올바르지 않습니다.'
        }), 401

# 브랜드 관련 API
@app.route('/api/brands', methods=['GET'])
def get_brands():
    """브랜드 목록 조회"""
    try:
        brands = list(data_store.brands.values())
        return jsonify({
            'success': True,
            'data': brands,
            'total': len(brands)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'브랜드 조회 실패: {str(e)}'
        }), 500

@app.route('/api/brands/<brand_id>', methods=['GET'])
def get_brand(brand_id):
    """브랜드 상세 조회"""
    try:
        brand = data_store.brands.get(brand_id)
        if not brand:
            return jsonify({
                'success': False,
                'message': '브랜드를 찾을 수 없습니다.'
            }), 404
            
        return jsonify({
            'success': True,
            'data': brand
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'브랜드 조회 실패: {str(e)}'
        }), 500

@app.route('/api/brands', methods=['POST'])
def create_brand():
    """브랜드 생성"""
    try:
        data = request.get_json()
        brand_id = str(len(data_store.brands) + 1)
        
        new_brand = {
            'id': brand_id,
            'name': data.get('name'),
            'industry': data.get('industry'),
            'description': data.get('description'),
            'created_at': datetime.datetime.now().isoformat(),
            'status': 'active'
        }
        
        data_store.brands[brand_id] = new_brand
        
        return jsonify({
            'success': True,
            'message': '브랜드가 생성되었습니다.',
            'data': new_brand
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'브랜드 생성 실패: {str(e)}'
        }), 500

# 매장 관련 API
@app.route('/api/branches', methods=['GET'])
def get_branches():
    """매장 목록 조회"""
    try:
        brand_id = request.args.get('brand_id')
        if brand_id:
            branches = [b for b in data_store.branches.values() if b['brand_id'] == brand_id]
        else:
            branches = list(data_store.branches.values())
            
        return jsonify({
            'success': True,
            'data': branches,
            'total': len(branches)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'매장 조회 실패: {str(e)}'
        }), 500

@app.route('/api/branches/<branch_id>', methods=['GET'])
def get_branch(branch_id):
    """매장 상세 조회"""
    try:
        branch = data_store.branches.get(branch_id)
        if not branch:
            return jsonify({
                'success': False,
                'message': '매장을 찾을 수 없습니다.'
            }), 404
            
        return jsonify({
            'success': True,
            'data': branch
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'매장 조회 실패: {str(e)}'
        }), 500

# 직원 관련 API
@app.route('/api/employees', methods=['GET'])
def get_employees():
    """직원 목록 조회"""
    try:
        branch_id = request.args.get('branch_id')
        if branch_id:
            employees = [e for e in data_store.employees.values() if e['branch_id'] == branch_id]
        else:
            employees = list(data_store.employees.values())
            
        return jsonify({
            'success': True,
            'data': employees,
            'total': len(employees)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'직원 조회 실패: {str(e)}'
        }), 500

@app.route('/api/employees/<employee_id>', methods=['GET'])
def get_employee(employee_id):
    """직원 상세 조회"""
    try:
        employee = data_store.employees.get(employee_id)
        if not employee:
            return jsonify({
                'success': False,
                'message': '직원을 찾을 수 없습니다.'
            }), 404
            
        return jsonify({
            'success': True,
            'data': employee
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'직원 조회 실패: {str(e)}'
        }), 500

# 스케줄 관련 API
@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    """스케줄 목록 조회"""
    try:
        employee_id = request.args.get('employee_id')
        date = request.args.get('date', datetime.date.today().isoformat())
        
        if employee_id:
            schedules = [s for s in data_store.schedules.values() 
                        if s['employee_id'] == employee_id and s['date'] == date]
        else:
            schedules = [s for s in data_store.schedules.values() if s['date'] == date]
            
        return jsonify({
            'success': True,
            'data': schedules,
            'total': len(schedules)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'스케줄 조회 실패: {str(e)}'
        }), 500

@app.route('/api/schedules', methods=['POST'])
def create_schedule():
    """스케줄 생성"""
    try:
        data = request.get_json()
        schedule_id = str(len(data_store.schedules) + 1)
        
        new_schedule = {
            'id': schedule_id,
            'employee_id': data.get('employee_id'),
            'date': data.get('date'),
            'start_time': data.get('start_time'),
            'end_time': data.get('end_time'),
            'status': 'scheduled',
            'notes': data.get('notes', '')
        }
        
        data_store.schedules[schedule_id] = new_schedule
        
        return jsonify({
            'success': True,
            'message': '스케줄이 생성되었습니다.',
            'data': new_schedule
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'스케줄 생성 실패: {str(e)}'
        }), 500

# 직원 대시보드 API (기존 유지)
@app.route('/api/employee/dashboard', methods=['GET'])
def employee_dashboard():
    """직원 대시보드 데이터"""
    try:
        # 실제 데이터에서 직원 정보 조회
        employee = data_store.employees.get("1")  # 첫 번째 직원
        if not employee:
            return jsonify({
                'success': False,
                'message': '직원 정보를 찾을 수 없습니다.'
            }), 404
            
        # 매장 정보 조회
        branch = data_store.branches.get(employee['branch_id'])
        
        # 오늘 스케줄 조회
        today_schedule = None
        for schedule in data_store.schedules.values():
            if schedule['employee_id'] == employee['id'] and schedule['date'] == datetime.date.today().isoformat():
                today_schedule = schedule
                break
        
        # 통계 데이터 (실제로는 계산 필요)
        stats = {
            'total_work_hours': 160,
            'this_month_hours': 120,
            'attendance_rate': 95.5,
            'overtime_hours': 8
        }
        
        dashboard_data = {
            'employee': {
                'id': employee['id'],
                'name': employee['name'],
                'employee_id': employee['employee_id'],
                'position': employee['position'],
                'department': employee['department'],
                'branch': {
                    'id': branch['id'],
                    'name': branch['name'],
                    'address': branch['address']
                },
                'contact': {
                    'phone': employee['phone'],
                    'email': employee['email']
                },
                'schedule': {
                    'today': datetime.date.today().isoformat(),
                    'start_time': today_schedule['start_time'] if today_schedule else '09:00',
                    'end_time': today_schedule['end_time'] if today_schedule else '18:00',
                    'status': today_schedule['status'] if today_schedule else 'scheduled'
                },
                'stats': stats
            },
            'work_schedule': [
                {
                    'id': schedule['id'],
                    'date': schedule['date'],
                    'start_time': schedule['start_time'],
                    'end_time': schedule['end_time'],
                    'status': schedule['status'],
                    'notes': schedule['notes']
                }
                for schedule in data_store.schedules.values()
                if schedule['employee_id'] == employee['id']
            ]
        }
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'대시보드 데이터 조회 실패: {str(e)}'
        }), 500

@app.route('/api/employee/clock-in', methods=['POST'])
def employee_clock_in():
    """직원 출근 체크"""
    try:
        data = request.get_json()
        employee_id = data.get('employee_id', '1')
        timestamp = data.get('timestamp', datetime.datetime.now().isoformat())
        
        # 출근 기록 저장
        attendance_record = {
            'id': str(len(data_store.attendance_records) + 1),
            'employee_id': employee_id,
            'type': 'clock_in',
            'timestamp': timestamp,
            'date': datetime.date.today().isoformat()
        }
        data_store.attendance_records.append(attendance_record)
        
        # 스케줄 상태 업데이트
        for schedule in data_store.schedules.values():
            if schedule['employee_id'] == employee_id and schedule['date'] == datetime.date.today().isoformat():
                schedule['status'] = 'working'
                break
        
        return jsonify({
            'success': True,
            'message': '출근이 기록되었습니다.',
            'data': {
                'employee_id': employee_id,
                'clock_in_time': timestamp,
                'status': 'working'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'출근 기록 실패: {str(e)}'
        }), 500

@app.route('/api/employee/clock-out', methods=['POST'])
def employee_clock_out():
    """직원 퇴근 체크"""
    try:
        data = request.get_json()
        employee_id = data.get('employee_id', '1')
        timestamp = data.get('timestamp', datetime.datetime.now().isoformat())
        
        # 퇴근 기록 저장
        attendance_record = {
            'id': str(len(data_store.attendance_records) + 1),
            'employee_id': employee_id,
            'type': 'clock_out',
            'timestamp': timestamp,
            'date': datetime.date.today().isoformat()
        }
        data_store.attendance_records.append(attendance_record)
        
        # 스케줄 상태 업데이트
        for schedule in data_store.schedules.values():
            if schedule['employee_id'] == employee_id and schedule['date'] == datetime.date.today().isoformat():
                schedule['status'] = 'completed'
                break
        
        return jsonify({
            'success': True,
            'message': '퇴근이 기록되었습니다.',
            'data': {
                'employee_id': employee_id,
                'clock_out_time': timestamp,
                'status': 'completed'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'퇴근 기록 실패: {str(e)}'
        }), 500

# 관리자 대시보드 API
@app.route('/api/admin/dashboard', methods=['GET'])
def admin_dashboard():
    """관리자 대시보드 데이터"""
    try:
        # 통계 데이터
        stats = {
            'total_brands': len(data_store.brands),
            'total_branches': len(data_store.branches),
            'total_employees': len(data_store.employees),
            'active_schedules': len([s for s in data_store.schedules.values() if s['status'] == 'working']),
            'today_attendance': len([a for a in data_store.attendance_records if a['date'] == datetime.date.today().isoformat()])
        }
        
        # 최근 활동
        recent_activities = []
        for record in data_store.attendance_records[-10:]:  # 최근 10개
            employee = data_store.employees.get(record['employee_id'])
            if employee:
                recent_activities.append({
                    'id': record['id'],
                    'type': record['type'],
                    'employee_name': employee['name'],
                    'timestamp': record['timestamp'],
                    'date': record['date']
                })
        
        dashboard_data = {
            'stats': stats,
            'recent_activities': recent_activities,
            'brands': list(data_store.brands.values()),
            'branches': list(data_store.branches.values())
        }
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'관리자 대시보드 조회 실패: {str(e)}'
        }), 500

# 테스트 알림 API (기존 유지)
@app.route('/api/test/notification', methods=['POST'])
def test_notification():
    data = request.get_json()
    message = data.get('message', '테스트 알림입니다.')
    
    return jsonify({
        'success': True,
        'message': f'알림이 전송되었습니다: {message}',
        'timestamp': datetime.datetime.now().isoformat()
    })

@app.route('/api/test/system-alert', methods=['POST'])
def test_system_alert():
    data = request.get_json()
    alert_type = data.get('type', 'info')
    message = data.get('message', '시스템 알림입니다.')
    
    return jsonify({
        'success': True,
        'message': f'{alert_type.upper()} 알림: {message}',
        'timestamp': datetime.datetime.now().isoformat()
    })

if __name__ == "__main__":
    print("🚀 실제 데이터 API 서버 시작...")
    print("📍 서버 주소: http://localhost:5000")
    print("📋 사용 가능한 엔드포인트:")
    print("   - GET  /api/health")
    print("   - POST /api/security/auth/login")
    print("   - GET  /api/brands")
    print("   - GET  /api/branches")
    print("   - GET  /api/employees")
    print("   - GET  /api/schedules")
    print("   - GET  /api/employee/dashboard")
    print("   - POST /api/employee/clock-in")
    print("   - POST /api/employee/clock-out")
    print("   - GET  /api/admin/dashboard")
    print("   - POST /api/test/notification")
    print("   - POST /api/test/system-alert")
    print("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=5000) 