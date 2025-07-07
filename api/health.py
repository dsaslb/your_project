from flask import Blueprint, jsonify
from flask_cors import cross_origin

health_bp = Blueprint('health', __name__)

@health_bp.route('/api/health', methods=['GET'])
@cross_origin()
def health_check():
    """백엔드 서버 상태 확인"""
    return jsonify({
        'status': 'ok',
        'message': 'Backend server is running',
        'timestamp': '2024-01-01T00:00:00Z'
    }), 200 