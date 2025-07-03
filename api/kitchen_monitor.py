"""
주방 모니터링 혁신 기능용 API
- 실시간 주방 상태, 권한 분기, 통계/상태 반환 등 구현 예정
"""
from flask import Blueprint, jsonify, request

kitchen_monitor_api = Blueprint('kitchen_monitor_api', __name__)

@kitchen_monitor_api.route('/api/kitchen-monitor', methods=['GET'])
def get_kitchen_monitor():
    # TODO: 주방 상태 데이터 반환, 권한 분기 등 구현
    return jsonify({'message': '주방 모니터링 데이터'}), 200 