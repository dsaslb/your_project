"""
조리 예상시간 혁신 기능용 API
- 실시간 조리 예상시간, 권한 분기, 통계/상태 반환 등 구현 예정
"""
from flask import Blueprint, jsonify, request

cooktime_api = Blueprint('cooktime_api', __name__)

@cooktime_api.route('/api/cooktime', methods=['GET'])
def get_cooktime():
    # TODO: 조리 예상시간 데이터 반환, 권한 분기 등 구현
    return jsonify({'message': '조리 예상시간 데이터'}), 200 