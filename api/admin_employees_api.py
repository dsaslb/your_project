"""
직원(Employees) 관리 CRUD API (관리자 전용)
- /api/admin/employees [GET, POST]
- /api/admin/employees/<employee_id> [GET, PUT, DELETE]
"""
from flask import Blueprint, request, jsonify, abort, current_app
from datetime import datetime
from models.employee_models import Employee

bp = Blueprint('admin_employees_api', __name__, url_prefix='/api/admin/employees')

@bp.route('', methods=['GET'])
def list_employees():
    """직원 목록 조회 (검색/필터/페이징 지원)"""
    q = request.args.get('q', '')
    branch_id = request.args.get('branch_id')
    brand_id = request.args.get('brand_id')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    query = Employee.query
    if brand_id:
        query = query.filter(Employee.brand_id == brand_id)
    if branch_id:
        query = query.filter(Employee.branch_id == branch_id)
    if q:
        query = query.filter(Employee.name.ilike(f'%{q}%'))
    pagination = query.order_by(Employee.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    # 프론트엔드 API 형식에 맞춰 응답
    return jsonify({
        'success': True,
        'data': [e.to_dict() for e in pagination.items],
        'message': '직원 목록을 성공적으로 조회했습니다.',
        'timestamp': datetime.utcnow().isoformat(),
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }
    })

@bp.route('', methods=['POST'])
def create_employee():
    """직원 생성"""
    data = request.json
    if not data or not data.get('name') or not data.get('branch_id'):
        return jsonify({
            'success': False,
            'error': '직원 이름과 지점 ID는 필수입니다.',
            'timestamp': datetime.utcnow().isoformat()
        }), 400
    
    try:
        employee = Employee(
            name=data['name'],
            branch_id=data['branch_id'],
            brand_id=data.get('brand_id'),
            role=data.get('role', 'staff'),
            email=data.get('email'),
            phone=data.get('phone'),
            status=data.get('status', 'active'),
            description=data.get('description', '')
        )
        current_app.extensions['sqlalchemy'].db.session.add(employee)
        current_app.extensions['sqlalchemy'].db.session.commit()
        
        return jsonify({
            'success': True,
            'data': employee.to_dict(),
            'message': '직원이 성공적으로 생성되었습니다.',
            'timestamp': datetime.utcnow().isoformat()
        }), 201
    except Exception as e:
        current_app.extensions['sqlalchemy'].db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'직원 생성 중 오류가 발생했습니다: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@bp.route('/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    """직원 상세 조회"""
    employee = Employee.query.get_or_404(employee_id)
    return jsonify({
        'success': True,
        'data': employee.to_dict(),
        'message': '직원 정보를 성공적으로 조회했습니다.',
        'timestamp': datetime.utcnow().isoformat()
    })

@bp.route('/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    """직원 수정"""
    employee = Employee.query.get_or_404(employee_id)
    data = request.json
    if not data:
        return jsonify({
            'success': False,
            'error': '수정할 데이터가 없습니다.',
            'timestamp': datetime.utcnow().isoformat()
        }), 400
    
    try:
        for field in ['name', 'branch_id', 'brand_id', 'role', 'email', 'phone', 'status', 'description']:
            if field in data:
                setattr(employee, field, data[field])
        current_app.extensions['sqlalchemy'].db.session.commit()
        
        return jsonify({
            'success': True,
            'data': employee.to_dict(),
            'message': '직원 정보가 성공적으로 수정되었습니다.',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        current_app.extensions['sqlalchemy'].db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'직원 수정 중 오류가 발생했습니다: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@bp.route('/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    """직원 삭제"""
    employee = Employee.query.get_or_404(employee_id)
    try:
        current_app.extensions['sqlalchemy'].db.session.delete(employee)
        current_app.extensions['sqlalchemy'].db.session.commit()
        return jsonify({
            'success': True,
            'message': '직원이 성공적으로 삭제되었습니다.',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        current_app.extensions['sqlalchemy'].db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'직원 삭제 중 오류가 발생했습니다: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }), 500 