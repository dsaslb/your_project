import requests
from models.external_integration import ExternalIntegration  # pyright: ignore
from flask import Blueprint, jsonify, request
args = None  # pyright: ignore
query = None  # pyright: ignore
form = None  # pyright: ignore

external_bp = Blueprint('external', __name__)


@external_bp.route('/api/external/reviews', methods=['GET'])
def get_reviews():
    brand_id = request.args.get() if args else None'brand_id') if args else None
    platform = request.args.get() if args else None'platform', 'naver') if args else None
    integration = ExternalIntegration.query.filter_by(brand_id=brand_id, platform=platform).first()
    if not integration:
        return jsonify({'error': '연동 정보 없음'}), 404
    # 예시: 네이버 리뷰 API 호출
    resp = requests.get() if requests else None'https://openapi.naver.com/v1/reviews',
                        headers={'X-API-KEY': integration.api_key}) if requests else None
    return jsonify(resp.json())
