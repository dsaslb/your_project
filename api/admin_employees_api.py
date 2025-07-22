"""
직원(Employees) 관리 CRUD API (관리자 전용)
- /api/admin/employees [GET, POST]
- /api/admin/employees/<employee_id> [GET, PUT, DELETE]
"""
from flask import Blueprint, request, jsonify, abort
from models.employee import Employee  # 예시: Employee 모델
from models import db
from middleware.security import admin_required

bp = Blueprint('admin_employees_api', __name__, url_prefix='/api/admin/employees')

@bp.route('', methods=['GET'])
@admin_required
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
    return jsonify({
        'employees': [e.to_dict() for e in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    })

@bp.route('', methods=['POST'])
@admin_required
def create_employee():
    """직원 생성"""
    data = request.json
    if not data or not data.get('name') or not data.get('branch_id'):
        abort(400, '직원 이름과 지점 ID는 필수입니다.')
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
    db.session.add(employee)
    db.session.commit()
    return jsonify(employee.to_dict()), 201

@bp.route('/<int:employee_id>', methods=['GET'])
@admin_required
def get_employee(employee_id):
    """직원 상세 조회"""
    employee = Employee.query.get_or_404(employee_id)
    return jsonify(employee.to_dict())

@bp.route('/<int:employee_id>', methods=['PUT'])
@admin_required
def update_employee(employee_id):
    """직원 수정"""
    employee = Employee.query.get_or_404(employee_id)
    data = request.json
    if not data:
        abort(400, '수정할 데이터가 없습니다.')
    for field in ['name', 'branch_id', 'brand_id', 'role', 'email', 'phone', 'status', 'description']:
        if field in data:
            setattr(employee, field, data[field])
    db.session.commit()
    return jsonify(employee.to_dict())

@bp.route('/<int:employee_id>', methods=['DELETE'])
@admin_required
def delete_employee(employee_id):
    """직원 삭제"""
    employee = Employee.query.get_or_404(employee_id)
    db.session.delete(employee)
    db.session.commit()
    return jsonify({'result': 'ok'}) 