from flask import Blueprint, jsonify, request
from utils.auth import auth_required
from utils.events import emit_branch_event
import time

# 모바일 API 블루프린트
mobile_api = Blueprint('mobile_api', __name__, url_prefix='/api/mobile')

@mobile_api.route('/health', methods=['GET'])
def health_check():
    """모바일 API 헬스 체크"""
    return jsonify({
        'status': 'healthy',
        'service': 'mobile_api',
        'timestamp': request.timestamp.isoformat() if hasattr(request, 'timestamp') else None
    })

@mobile_api.route('/test', methods=['GET'])
def test_endpoint():
    """모바일 API 테스트 엔드포인트"""
    return jsonify({
        'message': '모바일 API가 정상 작동 중입니다',
        'status': 'success',
        'endpoints': [
            '/api/mobile/health',
            '/api/mobile/purchase_orders',
            '/api/mobile/test'
        ]
    })

@mobile_api.route('/purchase_orders', methods=['POST'])
@auth_required
def create_purchase_order():
    """발주 생성 API"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        if not data or 'branch_id' not in data or 'items' not in data:
            return jsonify({
                'error': '필수 필드가 누락되었습니다',
                'required': ['branch_id', 'items']
            }), 400
        
        # 테스트용 더미 응답
        test_po_id = f"PO_{int(request.timestamp.timestamp()) if hasattr(request, 'timestamp') else int(time.time())}"
        
        # 실시간 이벤트 발송
        event_payload = {
            'po_id': test_po_id,
            'branch_id': data['branch_id'],
            'brand_id': 'test_brand_001',
            'industry_id': 'test_industry_001',
            'items': data['items'],
            'status': 'requested',
            'created_at': request.timestamp.isoformat() if hasattr(request, 'timestamp') else None
        }
        
        emit_branch_event('po:created', event_payload, room=f"branch:{data['branch_id']}")
        
        return jsonify({
            'success': True,
            'po_id': test_po_id,
            'message': '발주가 성공적으로 생성되었습니다',
            'test_mode': True
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': '발주 생성 중 오류가 발생했습니다',
            'message': str(e)
        }), 500

# 블루프린트 등록
def init_app(app):
    app.register_blueprint(mobile_api)
