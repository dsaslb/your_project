from flask import Blueprint, request, jsonify
from extensions import db
from models.industry_models import Industry, BrandPlugin
from models.brand_models import Brand
from datetime import datetime

industry_admin_api = Blueprint('industry_admin_api', __name__, url_prefix='/api/admin/industry')

# 업종 리스트 조회
@industry_admin_api.route('/industries', methods=['GET'])
def get_industries():
    industries = Industry.query.all()
    return jsonify({'success': True, 'industries': [i.to_dict() for i in industries]})

# 업종 생성
@industry_admin_api.route('/industries', methods=['POST'])
def create_industry():
    data = request.json
    industry = Industry(name=data['name'], description=data.get('description'))
    db.session.add(industry)
    db.session.commit()
    return jsonify({'success': True, 'industry': industry.to_dict()})

# 브랜드 리스트 (업종별)
@industry_admin_api.route('/brands', methods=['GET'])
def get_brands():
    industry_id = request.args.get('industry_id', type=int)
    query = Brand.query
    if industry_id:
        query = query.filter_by(industry_id=industry_id)
    brands = query.all()
    return jsonify({'success': True, 'brands': [b.to_dict() for b in brands]})

# 브랜드 생성
@industry_admin_api.route('/brands', methods=['POST'])
def create_brand():
    data = request.json
    brand = Brand(name=data['name'], description=data.get('description'), industry_id=data.get('industry_id'))
    db.session.add(brand)
    db.session.commit()
    return jsonify({'success': True, 'brand': brand.to_dict()})

# 브랜드 승인/거절/수정/삭제
@industry_admin_api.route('/brands/<int:brand_id>', methods=['PUT'])
def update_brand(brand_id):
    data = request.json
    brand = Brand.query.get_or_404(brand_id)
    brand.name = data.get('name', brand.name)
    brand.description = data.get('description', brand.description)
    brand.status = data.get('status', brand.status)
    db.session.commit()
    return jsonify({'success': True, 'brand': brand.to_dict()})

@industry_admin_api.route('/brands/<int:brand_id>', methods=['DELETE'])
def delete_brand(brand_id):
    brand = Brand.query.get_or_404(brand_id)
    db.session.delete(brand)
    db.session.commit()
    return jsonify({'success': True})

# 브랜드별 플러그인 리스트/추가/수정/삭제
@industry_admin_api.route('/brands/<int:brand_id>/plugins', methods=['GET'])
def get_brand_plugins(brand_id):
    plugins = BrandPlugin.query.filter_by(brand_id=brand_id).all()
    return jsonify({'success': True, 'plugins': [p.to_dict() for p in plugins]})

@industry_admin_api.route('/brands/<int:brand_id>/plugins', methods=['POST'])
def add_brand_plugin(brand_id):
    data = request.json
    plugin = BrandPlugin(brand_id=brand_id, name=data['name'], description=data.get('description'), status='active')
    db.session.add(plugin)
    db.session.commit()
    return jsonify({'success': True, 'plugin': plugin.to_dict()})

@industry_admin_api.route('/brands/<int:brand_id>/plugins/<int:plugin_id>', methods=['PUT'])
def update_brand_plugin(brand_id, plugin_id):
    plugin = BrandPlugin.query.get_or_404(plugin_id)
    data = request.json
    plugin.name = data.get('name', plugin.name)
    plugin.description = data.get('description', plugin.description)
    plugin.status = data.get('status', plugin.status)
    db.session.commit()
    return jsonify({'success': True, 'plugin': plugin.to_dict()})

@industry_admin_api.route('/brands/<int:brand_id>/plugins/<int:plugin_id>', methods=['DELETE'])
def delete_brand_plugin(brand_id, plugin_id):
    plugin = BrandPlugin.query.get_or_404(plugin_id)
    db.session.delete(plugin)
    db.session.commit()
    return jsonify({'success': True}) 