"""
브랜드 관리 CRUD API (관리자 전용)
- /api/admin/brands [GET, POST]
- /api/admin/brands/<brand_id> [GET, PUT, DELETE]
"""
from flask import Blueprint, request, jsonify, abort
from models.branch import Brand  # 예시: Brand 모델
from models import db
from middleware.security import admin_required  # 관리자 권한 데코레이터 예시

bp = Blueprint('admin_brands_api', __name__, url_prefix='/api/admin/brands')

@bp.route('', methods=['GET'])
@admin_required
def list_brands():
    """브랜드 목록 조회 (검색/페이징 지원)"""
    q = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    query = Brand.query
    if q:
        query = query.filter(Brand.name.ilike(f'%{q}%'))
    pagination = query.order_by(Brand.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'brands': [b.to_dict() for b in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    })

@bp.route('', methods=['POST'])
@admin_required
def create_brand():
    """브랜드 생성"""
    data = request.json
    if not data or not data.get('name'):
        abort(400, '브랜드 이름은 필수입니다.')
    brand = Brand(name=data['name'], description=data.get('description', ''))
    db.session.add(brand)
    db.session.commit()
    return jsonify(brand.to_dict()), 201

@bp.route('/<int:brand_id>', methods=['GET'])
@admin_required
def get_brand(brand_id):
    """브랜드 상세 조회"""
    brand = Brand.query.get_or_404(brand_id)
    return jsonify(brand.to_dict())

@bp.route('/<int:brand_id>', methods=['PUT'])
@admin_required
def update_brand(brand_id):
    """브랜드 수정"""
    brand = Brand.query.get_or_404(brand_id)
    data = request.json
    if not data:
        abort(400, '수정할 데이터가 없습니다.')
    if 'name' in data:
        brand.name = data['name']
    if 'description' in data:
        brand.description = data['description']
    db.session.commit()
    return jsonify(brand.to_dict())

@bp.route('/<int:brand_id>', methods=['DELETE'])
@admin_required
def delete_brand(brand_id):
    """브랜드 삭제"""
    brand = Brand.query.get_or_404(brand_id)
    db.session.delete(brand)
    db.session.commit()
    return jsonify({'result': 'ok'}) 