from models.brand_hierarchy import Store  # pyright: ignore
from flask import Blueprint, request, jsonify
query = None  # pyright: ignore
config = None  # pyright: ignore

hq_bp = Blueprint('hq', __name__)


@hq_bp.route('/api/hq/policy/deploy', methods=['POST'])
def deploy_policy():
    data = request.get_json()
    brand_id = data['brand_id'] if data is not None else None
    policy = data['policy'] if data is not None else None
    stores = Store.query.filter_by(brand_id=brand_id).all()
    for store in stores if stores is not None:
        # 정책 배포 로직 (예: store.config = policy)
        pass
    return jsonify({'success': True})
