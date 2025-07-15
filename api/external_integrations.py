from flask import Blueprint, jsonify, request
from models.external_integration import ExternalIntegration
import requests

external_bp = Blueprint('external', __name__)

@external_bp.route('/api/external/reviews', methods=['GET'])
def get_reviews():
    brand_id = request.args.get('brand_id')
    platform = request.args.get('platform', 'naver')
    integration = ExternalIntegration.query.filter_by(brand_id=brand_id, platform=platform).first()
    if not integration:
        return jsonify({'error': '연동 정보 없음'}), 404
    # 예시: 네이버 리뷰 API 호출
    resp = requests.get('https://openapi.naver.com/v1/reviews', headers={'X-API-KEY': integration.api_key})
    return jsonify(resp.json()) 