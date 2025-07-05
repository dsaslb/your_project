from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user
from models import db, User, PermissionChangeLog, Notification
from datetime import datetime

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

@staff_bp.route('/api/staff/<int:staff_id>/permissions', methods=['GET'])
@login_required
def get_staff_permissions(staff_id):
    """직원 권한 조회 API"""
    try:
        user = User.query.get(staff_id)
        if not user:
            return jsonify({"success": False, "message": "직원을 찾을 수 없습니다."}), 404
        
        # 현재 권한 정보 반환
        permissions = {
            "perm_employee_management": user.permissions.get("employee_management", {}).get("view", False),
            "perm_schedule_management": user.permissions.get("schedule_management", {}).get("view", False),
            "perm_order_management": user.permissions.get("order_management", {}).get("view", False),
            "perm_inventory_management": user.permissions.get("inventory_management", {}).get("view", False),
            "perm_notification_management": user.permissions.get("notification_management", {}).get("view", False),
            "perm_reports": user.permissions.get("reports", {}).get("view", False),
            "perm_system_management": user.permissions.get("system_management", {}).get("view", False)
        }
        
        return jsonify({"success": True, "data": permissions})
    except Exception as e:
        return jsonify({"success": False, "message": f"권한 조회 중 오류가 발생했습니다: {str(e)}"}), 500

@staff_bp.route('/api/staff/<int:staff_id>/permissions', methods=['PUT'])
@login_required
def update_staff_permissions(staff_id):
    """직원 권한 변경 API"""
    try:
        user = User.query.get(staff_id)
        if not user:
            return jsonify({"success": False, "message": "직원을 찾을 수 없습니다."}), 404
        
        data = request.get_json()
        
        # 이전 권한 저장 (이력 기록용)
        old_permissions = user.permissions.copy()
        
        # 새로운 권한 설정
        new_permissions = {
            "employee_management": {"view": data.get("perm_employee_management", False)},
            "schedule_management": {"view": data.get("perm_schedule_management", False)},
            "order_management": {"view": data.get("perm_order_management", False)},
            "inventory_management": {"view": data.get("perm_inventory_management", False)},
            "notification_management": {"view": data.get("perm_notification_management", False)},
            "reports": {"view": data.get("perm_reports", False)},
            "system_management": {"view": data.get("perm_system_management", False)}
        }
        
        # 권한 변경 이력 기록
        change_log = PermissionChangeLog(
            user_id=staff_id,
            changed_by=current_user.id,
            change_type="permission",
            before_value=str(old_permissions),
            after_value=str(new_permissions),
            reason=data.get("reason", "관리자 권한 변경"),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(change_log)
        
        # 권한 업데이트
        user.permissions = new_permissions
        db.session.commit()
        
        # 권한 변경 알림 발송 (관리자에게)
        notification = Notification(
            user_id=current_user.id,
            title="직원 권한 변경 알림",
            message=f"{user.name} 직원의 권한이 변경되었습니다. 변경자: {current_user.name}",
            type="permission_change",
            priority="normal",
            data={
                "target_user_id": staff_id,
                "target_user_name": user.name,
                "changed_by": current_user.name,
                "change_type": "permission"
            }
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": "권한이 성공적으로 변경되었습니다.",
            "data": {
                "user_id": staff_id,
                "user_name": user.name,
                "changed_by": current_user.name,
                "changed_at": datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"권한 변경 중 오류가 발생했습니다: {str(e)}"}), 500

@staff_bp.route('/api/staff/<int:staff_id>/permission-history')
@login_required
def get_staff_permission_history(staff_id):
    """직원 권한 변경 이력 조회 API"""
    try:
        # 최근 10개 권한 변경 이력 조회
        history = PermissionChangeLog.query.filter_by(user_id=staff_id)\
            .order_by(PermissionChangeLog.created_at.desc())\
            .limit(10).all()
        
        history_data = []
        for record in history:
            changer = User.query.get(record.changed_by)
            history_data.append({
                "id": record.id,
                "changed_by": changer.name if changer else "알 수 없음",
                "change_type": record.change_type,
                "before_value": record.before_value,
                "after_value": record.after_value,
                "reason": record.reason,
                "changed_at": record.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({"success": True, "data": history_data})
        
    except Exception as e:
        return jsonify({"success": False, "message": f"이력 조회 중 오류가 발생했습니다: {str(e)}"}), 500 