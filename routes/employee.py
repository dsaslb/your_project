import logging
from datetime import datetime, date
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models_main import Staff, Branch

logger = logging.getLogger(__name__)

employee_bp = Blueprint('employee', __name__, url_prefix='/api/employee')

@employee_bp.route('/dashboard', methods=['GET'])
@login_required
def employee_dashboard():
    """직원 대시보드 데이터"""
    try:
        # 현재 사용자가 직원인지 확인
        if not hasattr(current_user, 'role') or current_user.role != 'employee':
            return jsonify({'success': False, 'message': '직원 권한이 필요합니다.'}), 403
        
        # 직원 정보 조회
        employee = Staff.query.filter_by(email=current_user.email).first()
        if not employee:
            return jsonify({'success': False, 'message': '직원 정보를 찾을 수 없습니다.'}), 404
        
        # 통계 데이터 (임시 데이터)
        stats = {
            'totalWorkDays': 22,
            'averageHours': 8.5,
            'performanceRating': 4.2,
            'completedTasks': 15,
            'pendingTasks': 3,
            'monthlySalary': int(employee.salary) if employee.salary else 2500000
        }
        
        # 근무 일정 (임시 데이터)
        schedule = [
            {
                'id': 1,
                'date': '2024-01-15',
                'startTime': '09:00',
                'endTime': '18:00',
                'status': 'completed',
                'type': 'regular'
            },
            {
                'id': 2,
                'date': '2024-01-16',
                'startTime': '09:00',
                'endTime': '18:00',
                'status': 'scheduled',
                'type': 'regular'
            },
            {
                'id': 3,
                'date': '2024-01-17',
                'startTime': '09:00',
                'endTime': '18:00',
                'status': 'scheduled',
                'type': 'regular'
            }
        ]
        
        # 업무 목록 (임시 데이터)
        tasks = [
            {
                'id': 1,
                'title': '고객 응대 업무',
                'description': '전화 및 이메일 고객 문의 처리',
                'dueDate': '2024-01-16',
                'status': 'in_progress',
                'priority': 'high'
            },
            {
                'id': 2,
                'title': '재고 정리',
                'description': '매장 재고 현황 점검 및 정리',
                'dueDate': '2024-01-17',
                'status': 'pending',
                'priority': 'medium'
            },
            {
                'id': 3,
                'title': '매장 청소',
                'description': '매장 내부 청소 및 정리',
                'dueDate': '2024-01-18',
                'status': 'pending',
                'priority': 'low'
            }
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'stats': stats,
                'schedule': schedule,
                'tasks': tasks
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching employee dashboard: {str(e)}")
        return jsonify({'success': False, 'message': '대시보드 데이터 조회 중 오류가 발생했습니다.'}), 500

@employee_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """직원 프로필 정보 조회"""
    try:
        # 현재 사용자가 직원인지 확인
        if not hasattr(current_user, 'role') or current_user.role != 'employee':
            return jsonify({'success': False, 'message': '직원 권한이 필요합니다.'}), 403
        
        # 직원 정보 조회
        employee = Staff.query.filter_by(email=current_user.email).first()
        if not employee:
            return jsonify({'success': False, 'message': '직원 정보를 찾을 수 없습니다.'}), 404
        
        # 매장 정보 조회
        branch = Branch.query.get(employee.branch_id)
        
        profile_data = {
            'id': employee.id,
            'name': employee.name,
            'email': employee.email,
            'phone': employee.phone,
            'position': employee.position,
            'department': employee.department,
            'hire_date': employee.hire_date.strftime('%Y-%m-%d') if employee.hire_date else None,
            'status': employee.status,
            'salary': employee.salary,
            'branch': {
                'id': branch.id,
                'name': branch.name,
                'address': branch.address
            } if branch else None
        }
        
        return jsonify({
            'success': True,
            'data': profile_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching employee profile: {str(e)}")
        return jsonify({'success': False, 'message': '프로필 정보 조회 중 오류가 발생했습니다.'}), 500

@employee_bp.route('/schedule', methods=['GET'])
@login_required
def get_schedule():
    """직원 근무 일정 조회"""
    try:
        # 현재 사용자가 직원인지 확인
        if not hasattr(current_user, 'role') or current_user.role != 'employee':
            return jsonify({'success': False, 'message': '직원 권한이 필요합니다.'}), 403
        
        # 직원 정보 조회
        employee = Staff.query.filter_by(email=current_user.email).first()
        if not employee:
            return jsonify({'success': False, 'message': '직원 정보를 찾을 수 없습니다.'}), 404
        
        # 근무 일정 (임시 데이터)
        schedule = [
            {
                'id': 1,
                'date': '2024-01-15',
                'startTime': '09:00',
                'endTime': '18:00',
                'status': 'completed',
                'type': 'regular'
            },
            {
                'id': 2,
                'date': '2024-01-16',
                'startTime': '09:00',
                'endTime': '18:00',
                'status': 'scheduled',
                'type': 'regular'
            },
            {
                'id': 3,
                'date': '2024-01-17',
                'startTime': '09:00',
                'endTime': '18:00',
                'status': 'scheduled',
                'type': 'regular'
            },
            {
                'id': 4,
                'date': '2024-01-18',
                'startTime': '09:00',
                'endTime': '18:00',
                'status': 'scheduled',
                'type': 'regular'
            },
            {
                'id': 5,
                'date': '2024-01-19',
                'startTime': '09:00',
                'endTime': '18:00',
                'status': 'scheduled',
                'type': 'regular'
            }
        ]
        
        return jsonify({
            'success': True,
            'data': schedule
        })
        
    except Exception as e:
        logger.error(f"Error fetching employee schedule: {str(e)}")
        return jsonify({'success': False, 'message': '근무 일정 조회 중 오류가 발생했습니다.'}), 500

@employee_bp.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    """직원 업무 목록 조회"""
    try:
        # 현재 사용자가 직원인지 확인
        if not hasattr(current_user, 'role') or current_user.role != 'employee':
            return jsonify({'success': False, 'message': '직원 권한이 필요합니다.'}), 403
        
        # 직원 정보 조회
        employee = Staff.query.filter_by(email=current_user.email).first()
        if not employee:
            return jsonify({'success': False, 'message': '직원 정보를 찾을 수 없습니다.'}), 404
        
        # 업무 목록 (임시 데이터)
        tasks = [
            {
                'id': 1,
                'title': '고객 응대 업무',
                'description': '전화 및 이메일 고객 문의 처리',
                'dueDate': '2024-01-16',
                'status': 'in_progress',
                'priority': 'high'
            },
            {
                'id': 2,
                'title': '재고 정리',
                'description': '매장 재고 현황 점검 및 정리',
                'dueDate': '2024-01-17',
                'status': 'pending',
                'priority': 'medium'
            },
            {
                'id': 3,
                'title': '매장 청소',
                'description': '매장 내부 청소 및 정리',
                'dueDate': '2024-01-18',
                'status': 'pending',
                'priority': 'low'
            },
            {
                'id': 4,
                'title': '제품 진열',
                'description': '신상품 진열 및 기존 상품 정리',
                'dueDate': '2024-01-19',
                'status': 'completed',
                'priority': 'medium'
            }
        ]
        
        return jsonify({
            'success': True,
            'data': tasks
        })
        
    except Exception as e:
        logger.error(f"Error fetching employee tasks: {str(e)}")
        return jsonify({'success': False, 'message': '업무 목록 조회 중 오류가 발생했습니다.'}), 500 