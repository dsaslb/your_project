from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/staff')
@login_required
def staff():
    """직원 관리 메인 페이지"""
    return render_template('staff.html', user=current_user)

@staff_bp.route('/api/staff')
@login_required
def get_staff_list():
    """직원 목록 조회 API"""
    # 더미 직원 데이터
    staff_list = [
        {
            "id": 1,
            "name": "홍길동",
            "email": "hong@restaurant.com",
            "phone": "010-1234-5678",
            "role": "manager",
            "status": "active",
            "branch": "본점",
            "hire_date": "2023-01-15",
            "position": "매장관리자"
        },
        {
            "id": 2,
            "name": "김철수",
            "email": "kim@restaurant.com",
            "phone": "010-2345-6789",
            "role": "employee",
            "status": "active",
            "branch": "본점",
            "hire_date": "2023-03-20",
            "position": "주방직원"
        },
        {
            "id": 3,
            "name": "이영희",
            "email": "lee@restaurant.com",
            "phone": "010-3456-7890",
            "role": "employee",
            "status": "active",
            "branch": "본점",
            "hire_date": "2023-05-10",
            "position": "홀서빙"
        },
        {
            "id": 4,
            "name": "박민수",
            "email": "park@restaurant.com",
            "phone": "010-4567-8901",
            "role": "employee",
            "status": "inactive",
            "branch": "본점",
            "hire_date": "2023-02-01",
            "position": "청소직원"
        }
    ]
    
    return jsonify({"success": True, "data": staff_list})

@staff_bp.route('/api/staff', methods=['POST'])
@login_required
def create_staff():
    """직원 등록 API"""
    data = request.get_json()
    
    # 더미 응답
    new_staff = {
        "id": 999,
        "name": data.get('name', '새 직원'),
        "email": data.get('email', 'new@restaurant.com'),
        "phone": data.get('phone', '010-0000-0000'),
        "role": data.get('role', 'employee'),
        "status": "active",
        "branch": data.get('branch', '본점'),
        "hire_date": data.get('hire_date', '2024-01-15'),
        "position": data.get('position', '직원')
    }
    
    return jsonify({"success": True, "data": new_staff, "message": "직원이 등록되었습니다."})

@staff_bp.route('/api/staff/<int:staff_id>', methods=['PUT'])
@login_required
def update_staff(staff_id):
    """직원 정보 수정 API"""
    data = request.get_json()
    
    # 더미 응답
    updated_staff = {
        "id": staff_id,
        "name": data.get('name', '수정된 직원'),
        "email": data.get('email', 'updated@restaurant.com'),
        "phone": data.get('phone', '010-0000-0000'),
        "role": data.get('role', 'employee'),
        "status": data.get('status', 'active'),
        "branch": data.get('branch', '본점'),
        "hire_date": data.get('hire_date', '2024-01-15'),
        "position": data.get('position', '직원')
    }
    
    return jsonify({"success": True, "data": updated_staff, "message": "직원 정보가 수정되었습니다."})

@staff_bp.route('/api/staff/<int:staff_id>', methods=['DELETE'])
@login_required
def delete_staff(staff_id):
    """직원 삭제 API"""
    return jsonify({"success": True, "message": f"직원 {staff_id}가 삭제되었습니다."})

@staff_bp.route('/api/staff/<int:staff_id>')
@login_required
def get_staff_detail(staff_id):
    """직원 상세 정보 조회 API"""
    # 더미 상세 데이터
    staff_detail = {
        "id": staff_id,
        "name": "홍길동",
        "email": "hong@restaurant.com",
        "phone": "010-1234-5678",
        "role": "manager",
        "status": "active",
        "branch": "본점",
        "hire_date": "2023-01-15",
        "position": "매장관리자",
        "address": "서울시 강남구 테헤란로 123",
        "emergency_contact": "010-9876-5432",
        "salary": 3000000,
        "work_hours": 40,
        "permissions": ["manage_staff", "manage_orders", "view_reports"]
    }
    
    return jsonify({"success": True, "data": staff_detail})

@staff_bp.route('/api/staff/<int:staff_id>/attendance')
@login_required
def get_staff_attendance(staff_id):
    """직원 출근 기록 조회 API"""
    # 더미 출근 데이터
    attendance_records = [
        {
            "id": 1,
            "date": "2024-01-15",
            "clock_in": "09:00",
            "clock_out": "17:00",
            "status": "normal",
            "work_hours": 8
        },
        {
            "id": 2,
            "date": "2024-01-14",
            "clock_in": "09:15",
            "clock_out": "17:00",
            "status": "late",
            "work_hours": 7.75
        },
        {
            "id": 3,
            "date": "2024-01-13",
            "clock_in": "09:00",
            "clock_out": "18:00",
            "status": "overtime",
            "work_hours": 9
        }
    ]
    
    return jsonify({"success": True, "data": attendance_records})

@staff_bp.route('/api/staff/stats')
@login_required
def get_staff_stats():
    """직원 통계 API"""
    # 더미 통계 데이터
    stats = {
        "total_staff": 12,
        "active_staff": 10,
        "inactive_staff": 2,
        "managers": 3,
        "employees": 9,
        "new_hires_this_month": 2,
        "attendance_rate": 95.5
    }
    
    return jsonify({"success": True, "data": stats}) 