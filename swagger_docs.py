#!/usr/bin/env python3
"""
Swagger/OpenAPI 문서화가 완성된 Flask API 서버
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_smorest import Api, Blueprint, abort
from flask_restful import Resource
from marshmallow import Schema, fields, validate
import datetime
import uuid
from typing import Dict, List, Any

app = Flask(__name__)
app.config["API_TITLE"] = "멀티테넌시 관리 시스템 API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.2"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
app.config["OPENAPI_REDOC_PATH"] = "/redoc"
app.config["OPENAPI_REDOC_URL"] = "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"

api = Api(app)
CORS(app)

# ===== 스키마 정의 =====

class HealthResponseSchema(Schema):
    status = fields.Str(required=True, metadata={"description": "서버 상태"})
    message = fields.Str(required=True, metadata={"description": "상태 메시지"})
    timestamp = fields.DateTime(required=True, metadata={"description": "타임스탬프"})

class UserSchema(Schema):
    id = fields.Int(required=True, metadata={"description": "사용자 ID"})
    username = fields.Str(required=True, metadata={"description": "사용자명"})
    name = fields.Str(required=True, metadata={"description": "이름"})
    role = fields.Str(required=True, metadata={"description": "역할"})
    email = fields.Str(metadata={"description": "이메일"})

class LoginRequestSchema(Schema):
    username = fields.Str(required=True, metadata={"description": "사용자명"})
    password = fields.Str(required=True, metadata={"description": "비밀번호"})

class LoginResponseSchema(Schema):
    success = fields.Bool(required=True, metadata={"description": "성공 여부"})
    message = fields.Str(required=True, metadata={"description": "응답 메시지"})
    data = fields.Dict(metadata={"description": "응답 데이터"})

class BrandSchema(Schema):
    id = fields.Str(required=True, metadata={"description": "브랜드 ID"})
    name = fields.Str(required=True, metadata={"description": "브랜드명"})
    industry = fields.Str(required=True, metadata={"description": "업종"})
    description = fields.Str(metadata={"description": "설명"})
    created_at = fields.DateTime(required=True, metadata={"description": "생성일"})
    status = fields.Str(required=True, metadata={"description": "상태"})

class BrandCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100), metadata={"description": "브랜드명"})
    industry = fields.Str(required=True, validate=validate.Length(min=1, max=50), metadata={"description": "업종"})
    description = fields.Str(validate=validate.Length(max=500), metadata={"description": "설명"})

class BrandListResponseSchema(Schema):
    success = fields.Bool(required=True, metadata={"description": "성공 여부"})
    data = fields.List(fields.Nested(BrandSchema), required=True, metadata={"description": "브랜드 목록"})
    total = fields.Int(required=True, metadata={"description": "총 개수"})

class BranchSchema(Schema):
    id = fields.Str(required=True, metadata={"description": "매장 ID"})
    brand_id = fields.Str(required=True, metadata={"description": "브랜드 ID"})
    name = fields.Str(required=True, metadata={"description": "매장명"})
    address = fields.Str(required=True, metadata={"description": "주소"})
    phone = fields.Str(metadata={"description": "전화번호"})
    manager = fields.Str(metadata={"description": "매니저"})
    status = fields.Str(required=True, metadata={"description": "상태"})
    created_at = fields.DateTime(required=True, metadata={"description": "생성일"})

class BranchCreateSchema(Schema):
    brand_id = fields.Str(required=True, metadata={"description": "브랜드 ID"})
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100), metadata={"description": "매장명"})
    address = fields.Str(required=True, validate=validate.Length(min=1, max=200), metadata={"description": "주소"})
    phone = fields.Str(validate=validate.Length(max=20), metadata={"description": "전화번호"})
    manager = fields.Str(validate=validate.Length(max=50), metadata={"description": "매니저"})

class EmployeeSchema(Schema):
    id = fields.Str(required=True, metadata={"description": "직원 ID"})
    branch_id = fields.Str(required=True, metadata={"description": "매장 ID"})
    name = fields.Str(required=True, metadata={"description": "이름"})
    employee_id = fields.Str(required=True, metadata={"description": "직원번호"})
    position = fields.Str(required=True, metadata={"description": "직책"})
    department = fields.Str(required=True, metadata={"description": "부서"})
    phone = fields.Str(metadata={"description": "전화번호"})
    email = fields.Str(metadata={"description": "이메일"})
    hire_date = fields.Date(required=True, metadata={"description": "입사일"})
    status = fields.Str(required=True, metadata={"description": "상태"})
    salary = fields.Int(metadata={"description": "급여"})

class ScheduleSchema(Schema):
    id = fields.Str(required=True, metadata={"description": "스케줄 ID"})
    employee_id = fields.Str(required=True, metadata={"description": "직원 ID"})
    date = fields.Date(required=True, metadata={"description": "날짜"})
    start_time = fields.Str(required=True, metadata={"description": "시작 시간"})
    end_time = fields.Str(required=True, metadata={"description": "종료 시간"})
    status = fields.Str(required=True, metadata={"description": "상태"})
    notes = fields.Str(metadata={"description": "메모"})

class ScheduleCreateSchema(Schema):
    employee_id = fields.Str(required=True, metadata={"description": "직원 ID"})
    date = fields.Date(required=True, metadata={"description": "날짜"})
    start_time = fields.Str(required=True, metadata={"description": "시작 시간"})
    end_time = fields.Str(required=True, metadata={"description": "종료 시간"})
    notes = fields.Str(metadata={"description": "메모"})

class EmployeeDashboardSchema(Schema):
    employee = fields.Dict(required=True, metadata={"description": "직원 정보"})
    work_schedule = fields.List(fields.Nested(ScheduleSchema), required=True, metadata={"description": "근무 스케줄"})

class ClockInOutRequestSchema(Schema):
    employee_id = fields.Str(metadata={"description": "직원 ID"})
    timestamp = fields.DateTime(metadata={"description": "타임스탬프"})

class ClockInOutResponseSchema(Schema):
    success = fields.Bool(required=True, metadata={"description": "성공 여부"})
    message = fields.Str(required=True, metadata={"description": "응답 메시지"})
    data = fields.Dict(metadata={"description": "응답 데이터"})

class AdminDashboardSchema(Schema):
    stats = fields.Dict(required=True, metadata={"description": "통계 데이터"})
    recent_activities = fields.List(fields.Dict, required=True, metadata={"description": "최근 활동"})
    brands = fields.List(fields.Nested(BrandSchema), required=True, metadata={"description": "브랜드 목록"})
    branches = fields.List(fields.Nested(BranchSchema), required=True, metadata={"description": "매장 목록"})

class NotificationRequestSchema(Schema):
    message = fields.Str(required=True, validate=validate.Length(min=1, max=500), metadata={"description": "알림 메시지"})

class SystemAlertRequestSchema(Schema):
    type = fields.Str(required=True, validate=validate.OneOf(['info', 'warning', 'error']), metadata={"description": "알림 타입"})
    message = fields.Str(required=True, validate=validate.Length(min=1, max=500), metadata={"description": "알림 메시지"})

# ===== 실제 데이터 저장소 =====

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

data_store = DataStore()

# ===== 블루프린트 정의 =====

# 헬스체크 블루프린트
health_blp = Blueprint("health", __name__, description="헬스체크 관련 API")

@health_blp.route("/health")
class HealthCheck(Resource):
    @health_blp.response(200, HealthResponseSchema)
    def get(self):
        """서버 상태 확인"""
        return {
            "status": "healthy",
            "message": "서버가 정상적으로 실행 중입니다.",
            "timestamp": datetime.datetime.now().isoformat()
        }

# 인증 블루프린트
auth_blp = Blueprint("auth", __name__, description="인증 관련 API")

@auth_blp.route("/security/auth/login")
class Login(Resource):
    @auth_blp.arguments(LoginRequestSchema)
    @auth_blp.response(200, LoginResponseSchema)
    @auth_blp.response(401, LoginResponseSchema)
    def post(self, login_data):
        """사용자 로그인"""
        username = login_data.get('username')
        password = login_data.get('password')
        
        if username == "admin" and password == "admin123":
            return {
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
            }
        else:
            abort(401, message="아이디 또는 비밀번호가 올바르지 않습니다.")

# 브랜드 블루프린트
brand_blp = Blueprint("brands", __name__, description="브랜드 관련 API")

@brand_blp.route("/brands")
class BrandList(Resource):
    @brand_blp.response(200, BrandListResponseSchema)
    def get(self):
        """브랜드 목록 조회"""
        try:
            brands = list(data_store.brands.values())
            return {
                'success': True,
                'data': brands,
                'total': len(brands)
            }
        except Exception as e:
            abort(500, message=f'브랜드 조회 실패: {str(e)}')

    @brand_blp.arguments(BrandCreateSchema)
    @brand_blp.response(201, BrandSchema)
    def post(self, brand_data):
        """브랜드 생성"""
        try:
            brand_id = str(len(data_store.brands) + 1)
            
            new_brand = {
                'id': brand_id,
                'name': brand_data.get('name'),
                'industry': brand_data.get('industry'),
                'description': brand_data.get('description'),
                'created_at': datetime.datetime.now().isoformat(),
                'status': 'active'
            }
            
            data_store.brands[brand_id] = new_brand
            
            return new_brand, 201
        except Exception as e:
            abort(500, message=f'브랜드 생성 실패: {str(e)}')

@brand_blp.route("/brands/<brand_id>")
class BrandDetail(Resource):
    @brand_blp.response(200, BrandSchema)
    @brand_blp.response(404, description="브랜드를 찾을 수 없습니다.")
    def get(self, brand_id):
        """브랜드 상세 조회"""
        try:
            brand = data_store.brands.get(brand_id)
            if not brand:
                abort(404, message="브랜드를 찾을 수 없습니다.")
                
            return brand
        except Exception as e:
            abort(500, message=f'브랜드 조회 실패: {str(e)}')

# 매장 블루프린트
branch_blp = Blueprint("branches", __name__, description="매장 관련 API")

@branch_blp.route("/branches")
class BranchList(Resource):
    @branch_blp.response(200, schema=fields.List(fields.Nested(BranchSchema)))
    def get(self):
        """매장 목록 조회"""
        try:
            brand_id = request.args.get('brand_id')
            if brand_id:
                branches = [b for b in data_store.branches.values() if b['brand_id'] == brand_id]
            else:
                branches = list(data_store.branches.values())
                
            return branches
        except Exception as e:
            abort(500, message=f'매장 조회 실패: {str(e)}')

    @branch_blp.arguments(BranchCreateSchema)
    @branch_blp.response(201, BranchSchema)
    def post(self, branch_data):
        """매장 생성"""
        try:
            branch_id = str(len(data_store.branches) + 1)
            
            new_branch = {
                'id': branch_id,
                'brand_id': branch_data.get('brand_id'),
                'name': branch_data.get('name'),
                'address': branch_data.get('address'),
                'phone': branch_data.get('phone'),
                'manager': branch_data.get('manager'),
                'status': 'active',
                'created_at': datetime.datetime.now().isoformat()
            }
            
            data_store.branches[branch_id] = new_branch
            
            return new_branch, 201
        except Exception as e:
            abort(500, message=f'매장 생성 실패: {str(e)}')

@branch_blp.route("/branches/<branch_id>")
class BranchDetail(Resource):
    @branch_blp.response(200, BranchSchema)
    @branch_blp.response(404, description="매장을 찾을 수 없습니다.")
    def get(self, branch_id):
        """매장 상세 조회"""
        try:
            branch = data_store.branches.get(branch_id)
            if not branch:
                abort(404, message="매장을 찾을 수 없습니다.")
                
            return branch
        except Exception as e:
            abort(500, message=f'매장 조회 실패: {str(e)}')

# 직원 블루프린트
employee_blp = Blueprint("employees", __name__, description="직원 관련 API")

@employee_blp.route("/employees")
class EmployeeList(Resource):
    @employee_blp.response(200, schema=fields.List(fields.Nested(EmployeeSchema)))
    def get(self):
        """직원 목록 조회"""
        try:
            branch_id = request.args.get('branch_id')
            if branch_id:
                employees = [e for e in data_store.employees.values() if e['branch_id'] == branch_id]
            else:
                employees = list(data_store.employees.values())
                
            return employees
        except Exception as e:
            abort(500, message=f'직원 조회 실패: {str(e)}')

@employee_blp.route("/employees/<employee_id>")
class EmployeeDetail(Resource):
    @employee_blp.response(200, EmployeeSchema)
    @employee_blp.response(404, description="직원을 찾을 수 없습니다.")
    def get(self, employee_id):
        """직원 상세 조회"""
        try:
            employee = data_store.employees.get(employee_id)
            if not employee:
                abort(404, message="직원을 찾을 수 없습니다.")
                
            return employee
        except Exception as e:
            abort(500, message=f'직원 조회 실패: {str(e)}')

# 스케줄 블루프린트
schedule_blp = Blueprint("schedules", __name__, description="스케줄 관련 API")

@schedule_blp.route("/schedules")
class ScheduleList(Resource):
    @schedule_blp.response(200, schema=fields.List(fields.Nested(ScheduleSchema)))
    def get(self):
        """스케줄 목록 조회"""
        try:
            employee_id = request.args.get('employee_id')
            date = request.args.get('date', datetime.date.today().isoformat())
            
            if employee_id:
                schedules = [s for s in data_store.schedules.values() 
                            if s['employee_id'] == employee_id and s['date'] == date]
            else:
                schedules = [s for s in data_store.schedules.values() if s['date'] == date]
                
            return schedules
        except Exception as e:
            abort(500, message=f'스케줄 조회 실패: {str(e)}')

    @schedule_blp.arguments(ScheduleCreateSchema)
    @schedule_blp.response(201, ScheduleSchema)
    def post(self, schedule_data):
        """스케줄 생성"""
        try:
            schedule_id = str(len(data_store.schedules) + 1)
            
            new_schedule = {
                'id': schedule_id,
                'employee_id': schedule_data.get('employee_id'),
                'date': schedule_data.get('date').isoformat(),
                'start_time': schedule_data.get('start_time'),
                'end_time': schedule_data.get('end_time'),
                'status': 'scheduled',
                'notes': schedule_data.get('notes', '')
            }
            
            data_store.schedules[schedule_id] = new_schedule
            
            return new_schedule, 201
        except Exception as e:
            abort(500, message=f'스케줄 생성 실패: {str(e)}')

# 직원 대시보드 블루프린트
employee_dashboard_blp = Blueprint("employee-dashboard", __name__, description="직원 대시보드 관련 API")

@employee_dashboard_blp.route("/employee/dashboard")
class EmployeeDashboard(Resource):
    @employee_dashboard_blp.response(200, EmployeeDashboardSchema)
    def get(self):
        """직원 대시보드 데이터"""
        try:
            employee = data_store.employees.get("1")
            if not employee:
                abort(404, message="직원 정보를 찾을 수 없습니다.")
                
            branch = data_store.branches.get(employee['branch_id'])
            
            today_schedule = None
            for schedule in data_store.schedules.values():
                if schedule['employee_id'] == employee['id'] and schedule['date'] == datetime.date.today().isoformat():
                    today_schedule = schedule
                    break
            
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
            
            return dashboard_data
        except Exception as e:
            abort(500, message=f'대시보드 데이터 조회 실패: {str(e)}')

@employee_dashboard_blp.route("/employee/clock-in")
class EmployeeClockIn(Resource):
    @employee_dashboard_blp.arguments(ClockInOutRequestSchema)
    @employee_dashboard_blp.response(200, ClockInOutResponseSchema)
    def post(self, data):
        """직원 출근 체크"""
        try:
            employee_id = data.get('employee_id', '1')
            timestamp = data.get('timestamp', datetime.datetime.now().isoformat())
            
            attendance_record = {
                'id': str(len(data_store.attendance_records) + 1),
                'employee_id': employee_id,
                'type': 'clock_in',
                'timestamp': timestamp,
                'date': datetime.date.today().isoformat()
            }
            data_store.attendance_records.append(attendance_record)
            
            for schedule in data_store.schedules.values():
                if schedule['employee_id'] == employee_id and schedule['date'] == datetime.date.today().isoformat():
                    schedule['status'] = 'working'
                    break
            
            return {
                'success': True,
                'message': '출근이 기록되었습니다.',
                'data': {
                    'employee_id': employee_id,
                    'clock_in_time': timestamp,
                    'status': 'working'
                }
            }
        except Exception as e:
            abort(500, message=f'출근 기록 실패: {str(e)}')

@employee_dashboard_blp.route("/employee/clock-out")
class EmployeeClockOut(Resource):
    @employee_dashboard_blp.arguments(ClockInOutRequestSchema)
    @employee_dashboard_blp.response(200, ClockInOutResponseSchema)
    def post(self, data):
        """직원 퇴근 체크"""
        try:
            employee_id = data.get('employee_id', '1')
            timestamp = data.get('timestamp', datetime.datetime.now().isoformat())
            
            attendance_record = {
                'id': str(len(data_store.attendance_records) + 1),
                'employee_id': employee_id,
                'type': 'clock_out',
                'timestamp': timestamp,
                'date': datetime.date.today().isoformat()
            }
            data_store.attendance_records.append(attendance_record)
            
            for schedule in data_store.schedules.values():
                if schedule['employee_id'] == employee_id and schedule['date'] == datetime.date.today().isoformat():
                    schedule['status'] = 'completed'
                    break
            
            return {
                'success': True,
                'message': '퇴근이 기록되었습니다.',
                'data': {
                    'employee_id': employee_id,
                    'clock_out_time': timestamp,
                    'status': 'completed'
                }
            }
        except Exception as e:
            abort(500, message=f'퇴근 기록 실패: {str(e)}')

# 관리자 대시보드 블루프린트
admin_dashboard_blp = Blueprint("admin-dashboard", __name__, description="관리자 대시보드 관련 API")

@admin_dashboard_blp.route("/admin/dashboard")
class AdminDashboard(Resource):
    @admin_dashboard_blp.response(200, AdminDashboardSchema)
    def get(self):
        """관리자 대시보드 데이터"""
        try:
            stats = {
                'total_brands': len(data_store.brands),
                'total_branches': len(data_store.branches),
                'total_employees': len(data_store.employees),
                'active_schedules': len([s for s in data_store.schedules.values() if s['status'] == 'working']),
                'today_attendance': len([a for a in data_store.attendance_records if a['date'] == datetime.date.today().isoformat()])
            }
            
            recent_activities = []
            for record in data_store.attendance_records[-10:]:
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
            
            return dashboard_data
        except Exception as e:
            abort(500, message=f'관리자 대시보드 조회 실패: {str(e)}')

# 테스트 알림 블루프린트
test_blp = Blueprint("test", __name__, description="테스트 관련 API")

@test_blp.route("/test/notification")
class TestNotification(Resource):
    @test_blp.arguments(NotificationRequestSchema)
    @test_blp.response(200, LoginResponseSchema)
    def post(self, data):
        """테스트 알림 전송"""
        message = data.get('message', '테스트 알림입니다.')
        
        return {
            'success': True,
            'message': f'알림이 전송되었습니다: {message}',
            'timestamp': datetime.datetime.now().isoformat()
        }

@test_blp.route("/test/system-alert")
class TestSystemAlert(Resource):
    @test_blp.arguments(SystemAlertRequestSchema)
    @test_blp.response(200, LoginResponseSchema)
    def post(self, data):
        """시스템 알림 테스트"""
        alert_type = data.get('type', 'info')
        message = data.get('message', '시스템 알림입니다.')
        
        return {
            'success': True,
            'message': f'{alert_type.upper()} 알림: {message}',
            'timestamp': datetime.datetime.now().isoformat()
        }

# ===== 블루프린트 등록 =====

api.register_blueprint(health_blp)
api.register_blueprint(auth_blp)
api.register_blueprint(brand_blp)
api.register_blueprint(branch_blp)
api.register_blueprint(employee_blp)
api.register_blueprint(schedule_blp)
api.register_blueprint(employee_dashboard_blp)
api.register_blueprint(admin_dashboard_blp)
api.register_blueprint(test_blp)

if __name__ == "__main__":
    print("🚀 Swagger 문서화 API 서버 시작...")
    print("📍 서버 주소: http://localhost:5000")
    print("📋 Swagger UI: http://localhost:5000/swagger-ui")
    print("📋 ReDoc: http://localhost:5000/redoc")
    print("📋 OpenAPI JSON: http://localhost:5000/openapi.json")
    print("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=5000) 