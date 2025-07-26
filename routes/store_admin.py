import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models_main import User, Branch, Staff
from werkzeug.security import generate_password_hash
import re

logger = logging.getLogger(__name__)

store_admin_bp = Blueprint('store_admin', __name__, url_prefix='/api/store')

def validate_email(email):
    """이메일 형식 검증"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """전화번호 형식 검증"""
    pattern = r'^[0-9-+\s()]{10,15}$'
    return re.match(pattern, phone) is not None

def generate_temp_password():
    """임시 비밀번호 생성"""
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

@store_admin_bp.route('/dashboard', methods=['GET'])
def store_dashboard():
    """매장관리자 대시보드 데이터"""
    try:
        # 현재 매장 ID (실제로는 로그인된 사용자의 매장 ID)
        store_id = request.args.get('store_id', 1, type=int)
        
        # 직원 통계
        total_employees = Staff.query.filter_by(branch_id=store_id).count()
        active_employees = Staff.query.filter_by(branch_id=store_id, status='active').count()
        
        # 매출 통계 (실제 데이터로 대체 필요)
        total_sales = 15000000
        daily_sales = 850000
        growth_rate = 12.5
        pending_requests = 2
        
        # 직원 목록
        employees = Staff.query.filter_by(branch_id=store_id).all()
        employee_list = []
        
        for emp in employees:
            employee_list.append({
                'id': emp.id,
                'name': emp.name,
                'email': emp.email,
                'phone': emp.phone,
                'position': emp.position,
                'department': emp.department,
                'hire_date': emp.hire_date.strftime('%Y-%m-%d') if emp.hire_date else '',
                'status': emp.status,
                'salary': emp.salary or 0,
                'performance_rating': 85  # 실제 성과 데이터로 대체 필요
            })
        
        return jsonify({
            'success': True,
            'data': {
                'stats': {
                    'totalEmployees': total_employees,
                    'activeEmployees': active_employees,
                    'totalSales': total_sales,
                    'dailySales': daily_sales,
                    'growthRate': growth_rate,
                    'pendingRequests': pending_requests
                },
                'employees': employee_list
            }
        })
        
    except Exception as e:
        logger.error(f'매장관리자 대시보드 오류: {str(e)}')
        return jsonify({
            'success': False,
            'error': '대시보드 데이터 로드 중 오류가 발생했습니다.'
        }), 500

@store_admin_bp.route('/create_employee', methods=['POST'])
def create_employee():
    """직원 계정 생성"""
    try:
        data = request.json
        
        # 필수 필드 검증
        required_fields = ['name', 'email', 'phone', 'position', 'hire_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} 필드는 필수입니다.'
                }), 400
        
        # 이메일 형식 검증
        if not validate_email(data['email']):
            return jsonify({
                'success': False,
                'error': '올바른 이메일 형식을 입력해주세요.'
            }), 400
        
        # 전화번호 형식 검증
        if not validate_phone(data['phone']):
            return jsonify({
                'success': False,
                'error': '올바른 전화번호 형식을 입력해주세요.'
            }), 400
        
        # 이메일 중복 검사
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({
                'success': False,
                'error': '이미 사용 중인 이메일입니다.'
            }), 400
        
        # 현재 로그인된 사용자가 매장관리자인지 확인
        if not hasattr(current_user, 'role') or current_user.role != 'store_admin':
            return jsonify({
                'success': False,
                'error': '매장관리자 권한이 필요합니다.'
            }), 403
        
        # 현재 사용자의 매장 ID
        store_id = current_user.branch_id
        
        # 임시 비밀번호 생성
        temp_password = generate_temp_password()
        
        # 직원 계정 생성
        new_employee = Staff(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            position=data['position'],
            department=data.get('department', ''),
            hire_date=datetime.strptime(data['hire_date'], '%Y-%m-%d'),
            salary=int(data.get('salary', 0)) if data.get('salary') else None,
            status='active',
            branch_id=store_id,
            password_hash=generate_password_hash(temp_password)
        )
        
        db.session.add(new_employee)
        db.session.commit()
        
        logger.info(f'직원 계정 생성 완료: {data["email"]}')
        
        return jsonify({
            'success': True,
            'message': '직원 계정이 성공적으로 생성되었습니다.',
            'data': {
                'employee_id': new_employee.id,
                'temp_password': temp_password
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'직원 생성 오류: {str(e)}')
        return jsonify({
            'success': False,
            'error': '직원 계정 생성 중 오류가 발생했습니다.'
        }), 500

@store_admin_bp.route('/employees', methods=['GET'])
@login_required
def get_employees():
    """직원 목록 조회"""
    try:
        # 현재 사용자가 매장관리자인지 확인
        if current_user.role != 'store_admin':
            return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403
        
        # 현재 사용자의 매장 ID
        store_id = current_user.branch_id
        
        employees = Staff.query.filter_by(branch_id=store_id).all()
        employee_list = []
        
        for emp in employees:
            employee_list.append({
                'id': emp.id,
                'name': emp.name,
                'email': emp.email,
                'phone': emp.phone,
                'position': emp.position,
                'department': emp.department,
                'hire_date': emp.hire_date.strftime('%Y-%m-%d') if emp.hire_date else '',
                'status': emp.status,
                'salary': emp.salary or 0
            })
        
        return jsonify({
            'success': True,
            'data': employee_list
        })
        
    except Exception as e:
        logger.error(f'직원 목록 조회 오류: {str(e)}')
        return jsonify({
            'success': False,
            'error': '직원 목록 조회 중 오류가 발생했습니다.'
        }), 500

@store_admin_bp.route('/employee/<int:employee_id>', methods=['GET'])
def get_employee_details(employee_id):
    """직원 상세 정보 조회"""
    try:
        employee = Staff.query.get_or_404(employee_id)
        
        return jsonify({
            'success': True,
            'data': {
                'id': employee.id,
                'name': employee.name,
                'email': employee.email,
                'phone': employee.phone,
                'position': employee.position,
                'department': employee.department,
                'hire_date': employee.hire_date.strftime('%Y-%m-%d') if employee.hire_date else '',
                'status': employee.status,
                'salary': employee.salary or 0,
                'branch_id': employee.branch_id
            }
        })
        
    except Exception as e:
        logger.error(f'직원 상세 정보 조회 오류: {str(e)}')
        return jsonify({
            'success': False,
            'error': '직원 정보 조회 중 오류가 발생했습니다.'
        }), 500

@store_admin_bp.route('/employee/<int:employee_id>/status', methods=['PUT'])
def update_employee_status(employee_id):
    """직원 상태 업데이트"""
    try:
        data = request.json
        new_status = data.get('status')
        
        if new_status not in ['active', 'inactive', 'pending']:
            return jsonify({
                'success': False,
                'error': '올바르지 않은 상태값입니다.'
            }), 400
        
        employee = Staff.query.get_or_404(employee_id)
        employee.status = new_status
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '직원 상태가 업데이트되었습니다.'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'직원 상태 업데이트 오류: {str(e)}')
        return jsonify({
            'success': False,
            'error': '직원 상태 업데이트 중 오류가 발생했습니다.'
        }), 500 