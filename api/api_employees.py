from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.employee import UserInfo
from datetime import datetime

api_employees = Blueprint('api_employees', __name__)

@api_employees.route('/employees', methods=['GET'])
@login_required
def get_employees():
    """직원 목록 조회 (Admin만)"""
    if not current_user.is_admin:
        return jsonify({'error': '권한이 없습니다'}), 403
    
    try:
        employees = UserInfo.query.all()
        return jsonify({
            'success': True,
            'data': [emp.to_dict() for emp in employees]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_employees.route('/employees/<int:employee_id>', methods=['GET'])
@login_required
def get_employee(employee_id):
    """직원 상세 정보 조회 (Admin만)"""
    if not current_user.is_admin:
        return jsonify({'error': '권한이 없습니다'}), 403
    
    try:
        employee = UserInfo.query.get_or_404(employee_id)
        return jsonify({
            'success': True,
            'data': employee.to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_employees.route('/employees', methods=['POST'])
@login_required
def create_employee():
    """직원 생성 (Admin만)"""
    if not current_user.is_admin:
        return jsonify({'error': '권한이 없습니다'}), 403
    
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['user_id', 'employee_number', 'position', 'department']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'필수 필드가 누락되었습니다: {field}'}), 400
        
        # 중복 검사
        existing = UserInfo.query.filter_by(employee_number=data['employee_number']).first()
        if existing:
            return jsonify({'error': '이미 존재하는 사원번호입니다'}), 400
        
        # 직원 생성
        employee = UserInfo(
            user_id=data['user_id'],
            employee_number=data['employee_number'],
            position=data['position'],
            department=data['department'],
            hire_date=datetime.fromisoformat(data['hire_date']) if data.get('hire_date') else datetime.utcnow(),
            salary=data.get('salary'),
            status=data.get('status', 'active')
        )
        
        db.session.add(employee)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': employee.to_dict(),
            'message': '직원이 성공적으로 생성되었습니다'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_employees.route('/employees/<int:employee_id>', methods=['PUT'])
@login_required
def update_employee(employee_id):
    """직원 정보 수정 (Admin만)"""
    if not current_user.is_admin:
        return jsonify({'error': '권한이 없습니다'}), 403
    
    try:
        employee = UserInfo.query.get_or_404(employee_id)
        data = request.get_json()
        
        # 업데이트 가능한 필드들
        if 'position' in data:
            employee.position = data['position']
        if 'department' in data:
            employee.department = data['department']
        if 'salary' in data:
            employee.salary = data['salary']
        if 'status' in data:
            employee.status = data['status']
        if 'hire_date' in data:
            employee.hire_date = datetime.fromisoformat(data['hire_date'])
        
        employee.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': employee.to_dict(),
            'message': '직원 정보가 성공적으로 수정되었습니다'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_employees.route('/employees/<int:employee_id>', methods=['DELETE'])
@login_required
def delete_employee(employee_id):
    """직원 삭제 (Admin만)"""
    if not current_user.is_admin:
        return jsonify({'error': '권한이 없습니다'}), 403
    
    try:
        employee = UserInfo.query.get_or_404(employee_id)
        db.session.delete(employee)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '직원이 성공적으로 삭제되었습니다'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
