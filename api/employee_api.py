"""
직원 관리 API
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models_main import User, Staff, Branch, Brand, db
from utils.role_required import role_required
from utils.logger import logger
from datetime import datetime

employee_api = Blueprint('employee_api', __name__)

@employee_api.route('/api/employees', methods=['GET'])
@login_required
@role_required(['admin', 'super_admin', 'brand_manager', 'store_manager'])
def get_employees():
    """직원 목록 조회"""
    try:
        # 검색 파라미터
        search = request.args.get('search', '')
        department = request.args.get('department', '')
        status = request.args.get('status', '')
        branch_id = request.args.get('branch_id', '')
        brand_id = request.args.get('brand_id', '')
        
        # 기본 쿼리 - User 테이블에서 직원 데이터 조회
        query = User.query.filter(User.role.in_(['employee', 'manager', 'store_manager']))
        
        # 권한에 따른 필터링
        if current_user.role == 'brand_manager':
            query = query.filter(User.brand_id == current_user.brand_id)
        elif current_user.role == 'store_manager':
            query = query.filter(User.branch_id == current_user.branch_id)
        elif current_user.role == 'admin':
            # 관리자는 자신의 브랜드/매장 직원만 조회
            if current_user.brand_id:
                query = query.filter(User.brand_id == current_user.brand_id)
            if current_user.branch_id:
                query = query.filter(User.branch_id == current_user.branch_id)
        
        # 검색 필터
        if search:
            query = query.filter(
                db.or_(
                    User.name.contains(search),
                    User.username.contains(search),
                    User.email.contains(search)
                )
            )
        
        # 부서 필터
        if department:
            query = query.filter(User.department == department)
        
        # 상태 필터
        if status:
            query = query.filter(User.status == status)
        else:
            # 기본적으로 활성 상태 직원만
            query = query.filter(User.status.in_(['approved', 'active']))
        
        # 매장 필터
        if branch_id:
            query = query.filter(User.branch_id == int(branch_id))
        
        # 브랜드 필터
        if brand_id:
            query = query.filter(User.brand_id == int(brand_id))
        
        # 정렬
        query = query.order_by(User.name)
        
        # 결과 조회
        employees = query.all()
        
        # 응답 데이터 구성
        employee_list = []
        for user in employees:
            # Staff 정보 조회
            staff = Staff.query.filter_by(user_id=user.id).first()
            
            # 매장 정보 조회
            branch = Branch.query.get(user.branch_id) if user.branch_id else None
            brand = Brand.query.get(user.brand_id) if user.brand_id else None
            
            employee_data = {
                'id': user.id,
                'name': user.name or user.username,
                'username': user.username,
                'email': user.email,
                'phone': staff.phone if staff else None,
                'position': user.position or (staff.position if staff else '직원'),
                'department': user.department or (staff.department if staff else ''),
                'store_id': user.branch_id,
                'store_name': branch.name if branch else None,
                'brand_id': user.brand_id,
                'brand_name': brand.name if brand else None,
                'status': user.status,
                'role': user.role,
                'hire_date': staff.hire_date.isoformat() if staff and staff.hire_date else None,
                'salary': staff.salary if staff else None,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            }
            employee_list.append(employee_data)
        
        return jsonify({
            'success': True,
            'employees': employee_list,
            'total': len(employee_list)
        })
        
    except Exception as e:
        logger.error(f"직원 목록 조회 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '직원 목록을 불러오는 중 오류가 발생했습니다.'
        }), 500

@employee_api.route('/api/employees/<int:employee_id>', methods=['GET'])
@login_required
@role_required(['admin', 'super_admin', 'brand_manager', 'store_manager'])
def get_employee_detail(employee_id):
    """직원 상세 정보 조회"""
    try:
        user = User.query.get_or_404(employee_id)
        
        # 권한 확인
        if current_user.role == 'brand_manager' and user.brand_id != current_user.brand_id:
            return jsonify({'error': '권한이 없습니다.'}), 403
        elif current_user.role == 'store_manager' and user.branch_id != current_user.branch_id:
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        # Staff 정보 조회
        staff = Staff.query.filter_by(user_id=user.id).first()
        
        # 매장 및 브랜드 정보 조회
        branch = Branch.query.get(user.branch_id) if user.branch_id else None
        brand = Brand.query.get(user.brand_id) if user.brand_id else None
        
        employee_data = {
            'id': user.id,
            'name': user.name or user.username,
            'username': user.username,
            'email': user.email,
            'phone': staff.phone if staff else None,
            'position': user.position or (staff.position if staff else '직원'),
            'department': user.department or (staff.department if staff else ''),
            'store_id': user.branch_id,
            'store_name': branch.name if branch else None,
            'brand_id': user.brand_id,
            'brand_name': brand.name if brand else None,
            'status': user.status,
            'role': user.role,
            'hire_date': staff.hire_date.isoformat() if staff and staff.hire_date else None,
            'salary': staff.salary if staff else None,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None
        }
        
        return jsonify({
            'success': True,
            'employee': employee_data
        })
        
    except Exception as e:
        logger.error(f"직원 상세 정보 조회 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '직원 정보를 불러오는 중 오류가 발생했습니다.'
        }), 500

@employee_api.route('/api/stores', methods=['GET'])
@login_required
@role_required(['admin', 'super_admin', 'brand_manager', 'store_manager'])
def get_stores():
    """매장 목록 조회"""
    try:
        # 권한에 따른 필터링
        if current_user.role == 'brand_manager':
            stores = Branch.query.filter_by(brand_id=current_user.brand_id).all()
        elif current_user.role == 'store_manager':
            stores = [Branch.query.get(current_user.branch_id)] if current_user.branch_id else []
        elif current_user.role == 'admin':
            if current_user.brand_id:
                stores = Branch.query.filter_by(brand_id=current_user.brand_id).all()
            else:
                stores = Branch.query.all()
        else:  # super_admin
            stores = Branch.query.all()
        
        store_list = []
        for store in stores:
            if store:
                brand = Brand.query.get(store.brand_id) if store.brand_id else None
                store_data = {
                    'id': store.id,
                    'name': store.name,
                    'address': store.address,
                    'brand_id': store.brand_id,
                    'brand_name': brand.name if brand else None,
                    'status': store.status
                }
                store_list.append(store_data)
        
        return jsonify({
            'success': True,
            'stores': store_list
        })
        
    except Exception as e:
        logger.error(f"매장 목록 조회 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '매장 목록을 불러오는 중 오류가 발생했습니다.'
        }), 500
