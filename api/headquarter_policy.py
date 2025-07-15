from flask import Blueprint, request, jsonify
from models.brand_hierarchy import Store

hq_bp = Blueprint('hq', __name__)

@hq_bp.route('/api/hq/policy/deploy', methods=['POST'])
def deploy_policy():
    data = request.get_json()
    brand_id = data['brand_id']
    policy = data['policy']
    stores = Store.query.filter_by(brand_id=brand_id).all()
    for store in stores:
        # 정책 배포 로직 (예: store.config = policy)
        pass
    return jsonify({'success': True}) 