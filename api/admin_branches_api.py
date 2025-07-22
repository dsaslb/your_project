"""
지점(Branch) 관리 CRUD API (관리자 전용)
- /api/admin/branches [GET, POST]
- /api/admin/branches/<branch_id> [GET, PUT, DELETE]
"""
from flask import Blueprint, request, jsonify, abort
from models.branch import Branch  # 예시: Branch 모델
from models import db
from middleware.security import admin_required

bp = Blueprint('admin_branches_api', __name__, url_prefix='/api/admin/branches')

@bp.route('', methods=['GET'])
@admin_required
def list_branches():
    """지점 목록 조회 (검색/페이징 지원)"""
    q = request.args.get('q', '')
    brand_id = request.args.get('brand_id')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    query = Branch.query
    if brand_id:
        query = query.filter(Branch.brand_id == brand_id)
    if q:
        query = query.filter(Branch.name.ilike(f'%{q}%'))
    pagination = query.order_by(Branch.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'branches': [b.to_dict() for b in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    })

@bp.route('', methods=['POST'])
@admin_required
def create_branch():
    """지점 생성"""
    data = request.json
    if not data or not data.get('name') or not data.get('brand_id'):
        abort(400, '지점 이름과 브랜드 ID는 필수입니다.')
    branch = Branch(name=data['name'], brand_id=data['brand_id'], description=data.get('description', ''))
    db.session.add(branch)
    db.session.commit()
    return jsonify(branch.to_dict()), 201

@bp.route('/<int:branch_id>', methods=['GET'])
@admin_required
def get_branch(branch_id):
    """지점 상세 조회"""
    branch = Branch.query.get_or_404(branch_id)
    return jsonify(branch.to_dict())

@bp.route('/<int:branch_id>', methods=['PUT'])
@admin_required
def update_branch(branch_id):
    """지점 수정"""
    branch = Branch.query.get_or_404(branch_id)
    data = request.json
    if not data:
        abort(400, '수정할 데이터가 없습니다.')
    if 'name' in data:
        branch.name = data['name']
    if 'description' in data:
        branch.description = data['description']
    if 'brand_id' in data:
        branch.brand_id = data['brand_id']
    db.session.commit()
    return jsonify(branch.to_dict())

@bp.route('/<int:branch_id>', methods=['DELETE'])
@admin_required
def delete_branch(branch_id):
    """지점 삭제"""
    branch = Branch.query.get_or_404(branch_id)
    db.session.delete(branch)
    db.session.commit()
    return jsonify({'result': 'ok'}) 