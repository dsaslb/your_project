# api/admin 패키지 초기화 파일

from flask import Blueprint, jsonify, request
from utils.auth_decorators import admin_required

# 관리자 API 블루프린트
admin_api = Blueprint('admin_api', __name__, url_prefix='/api/admin')

@admin_api.route('/attendance', methods=['GET'])
@admin_required
def get_attendance_count():
    """출근 기록 수량 조회"""
    count_only = request.args.get('countOnly', '0') == '1'
    
    if count_only:
        # 테스트용 더미 데이터
        return jsonify({
            'count': 5,
            'test_mode': True
        })
    
    return jsonify({
        'data': [],
        'count': 5,
        'test_mode': True
    })

@admin_api.route('/inventory', methods=['GET'])
@admin_required
def get_inventory_count():
    """재고 항목 수량 조회"""
    count_only = request.args.get('countOnly', '0') == '1'
    
    if count_only:
        # 테스트용 더미 데이터
        return jsonify({
            'count': 12,
            'test_mode': True
        })
    
    return jsonify({
        'data': [],
        'count': 12,
        'test_mode': True
    })

@admin_api.route('/schedule', methods=['GET'])
@admin_required
def get_schedule_count():
    """일정 수량 조회"""
    count_only = request.args.get('countOnly', '0') == '1'
    
    if count_only:
        # 테스트용 더미 데이터
        return jsonify({
            'count': 8,
            'test_mode': True
        })
    
    return jsonify({
        'data': [],
        'count': 8,
        'test_mode': True
    })

@admin_api.route('/orders', methods=['GET'])
@admin_required
def get_orders_count():
    """주문 수량 조회"""
    count_only = request.args.get('countOnly', '0') == '1'
    
    if count_only:
        # 테스트용 더미 데이터
        return jsonify({
            'count': 15,
            'test_mode': True
        })
    
    return jsonify({
        'data': [],
        'count': 15,
        'test_mode': True
    })

@admin_api.route('/dashboard-stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    """대시보드 통계 조회"""
    try:
        # 테스트용 더미 데이터
        stats = {
            'total_users': 1250,
            'active_users': 890,
            'total_orders': 3450,
            'pending_orders': 45,
            'total_revenue': 1250000,
            'monthly_growth': 12.5,
            'top_products': [
                {'name': '상품 A', 'sales': 150},
                {'name': '상품 B', 'sales': 120},
                {'name': '상품 C', 'sales': 95}
            ],
            'recent_activities': [
                {'type': 'order', 'message': '새 주문이 생성되었습니다', 'time': '2024-01-15T10:30:00Z'},
                {'type': 'user', 'message': '새 사용자가 가입했습니다', 'time': '2024-01-15T09:15:00Z'},
                {'type': 'payment', 'message': '결제가 완료되었습니다', 'time': '2024-01-15T08:45:00Z'}
            ],
            'test_mode': True
        }
        
        return jsonify({
            'status': 'success',
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'대시보드 통계 조회 실패: {str(e)}'
        }), 500

# 블루프린트 등록
def init_app(app):
    app.register_blueprint(admin_api)
