from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models_main import db, Industry, Brand, Branch, User

multitenancy_bp = Blueprint('multitenancy_api', __name__, url_prefix='/api')

# 권한 체크 데코레이터(간단 버전)
def require_role(*roles):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                return jsonify({'error': '권한이 없습니다.'}), 403
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator

# 1. 업종(Industry) CRUD
@multitenancy_bp.route('/industries', methods=['GET'])
@login_required
@require_role('admin')
def get_industries():
    industries = Industry.query.all()
    return jsonify([{'id': i.id, 'name': i.name, 'code': i.code, 'description': i.description} for i in industries])

@multitenancy_bp.route('/industries', methods=['POST'])
@login_required
@require_role('admin')
def create_industry():
    data = request.json
    industry = Industry(name=data['name'], code=data['code'], description=data.get('description'))
    db.session.add(industry)
    db.session.commit()
    return jsonify({'result': 'ok', 'id': industry.id})

@multitenancy_bp.route('/industries/<int:industry_id>', methods=['PUT'])
@login_required
@require_role('admin')
def update_industry(industry_id):
    industry = Industry.query.get_or_404(industry_id)
    data = request.json
    industry.name = data.get('name', industry.name)
    industry.code = data.get('code', industry.code)
    industry.description = data.get('description', industry.description)
    db.session.commit()
    return jsonify({'result': 'ok'})

@multitenancy_bp.route('/industries/<int:industry_id>', methods=['DELETE'])
@login_required
@require_role('admin')
def delete_industry(industry_id):
    industry = Industry.query.get_or_404(industry_id)
    db.session.delete(industry)
    db.session.commit()
    return jsonify({'result': 'ok'})

# 2. 브랜드(Brand) CRUD
@multitenancy_bp.route('/brands', methods=['GET'])
@login_required
@require_role('admin', 'brand_admin')
def get_brands():
    brands = Brand.query.all()
    return jsonify([{'id': b.id, 'name': b.name, 'code': b.code, 'industry_id': b.industry_id, 'description': b.description} for b in brands])

@multitenancy_bp.route('/brands', methods=['POST'])
@login_required
@require_role('admin')
def create_brand():
    data = request.json
    brand = Brand(name=data['name'], code=data['code'], industry_id=data['industry_id'], description=data.get('description'))
    db.session.add(brand)
    db.session.commit()
    return jsonify({'result': 'ok', 'id': brand.id})

@multitenancy_bp.route('/brands/<int:brand_id>', methods=['PUT'])
@login_required
@require_role('admin', 'brand_admin')
def update_brand(brand_id):
    brand = Brand.query.get_or_404(brand_id)
    data = request.json
    brand.name = data.get('name', brand.name)
    brand.code = data.get('code', brand.code)
    brand.description = data.get('description', brand.description)
    db.session.commit()
    return jsonify({'result': 'ok'})

@multitenancy_bp.route('/brands/<int:brand_id>', methods=['DELETE'])
@login_required
@require_role('admin')
def delete_brand(brand_id):
    brand = Brand.query.get_or_404(brand_id)
    db.session.delete(brand)
    db.session.commit()
    return jsonify({'result': 'ok'})

# 3. 매장(Branch) CRUD
@multitenancy_bp.route('/branches', methods=['GET'])
@login_required
@require_role('admin', 'brand_admin', 'store_admin')
def get_branches():
    branches = Branch.query.all()
    return jsonify([{'id': b.id, 'name': b.name, 'brand_id': b.brand_id, 'industry_id': b.industry_id, 'address': b.address} for b in branches])

@multitenancy_bp.route('/branches', methods=['POST'])
@login_required
@require_role('admin', 'brand_admin')
def create_branch():
    data = request.json
    branch = Branch(name=data['name'], brand_id=data['brand_id'], industry_id=data['industry_id'], address=data.get('address'))
    db.session.add(branch)
    db.session.commit()
    return jsonify({'result': 'ok', 'id': branch.id})

@multitenancy_bp.route('/branches/<int:branch_id>', methods=['PUT'])
@login_required
@require_role('admin', 'brand_admin', 'store_admin')
def update_branch(branch_id):
    branch = Branch.query.get_or_404(branch_id)
    data = request.json
    branch.name = data.get('name', branch.name)
    branch.address = data.get('address', branch.address)
    db.session.commit()
    return jsonify({'result': 'ok'})

@multitenancy_bp.route('/branches/<int:branch_id>', methods=['DELETE'])
@login_required
@require_role('admin', 'brand_admin')
def delete_branch(branch_id):
    branch = Branch.query.get_or_404(branch_id)
    db.session.delete(branch)
    db.session.commit()
    return jsonify({'result': 'ok'})

# 4. 직원(User/Staff) CRUD
@multitenancy_bp.route('/users', methods=['GET'])
@login_required
@require_role('admin', 'brand_admin', 'store_admin')
def get_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'username': u.username, 'role': u.role, 'brand_id': u.brand_id, 'branch_id': u.branch_id, 'industry_id': u.industry_id} for u in users])

@multitenancy_bp.route('/users', methods=['POST'])
@login_required
@require_role('admin', 'brand_admin', 'store_admin')
def create_user():
    data = request.json
    user = User(username=data['username'], email=data['email'], role=data['role'], brand_id=data.get('brand_id'), branch_id=data.get('branch_id'), industry_id=data.get('industry_id'))
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'result': 'ok', 'id': user.id})

@multitenancy_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
@require_role('admin', 'brand_admin', 'store_admin')
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.role = data.get('role', user.role)
    db.session.commit()
    return jsonify({'result': 'ok'})

@multitenancy_bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
@require_role('admin', 'brand_admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'result': 'ok'}) 