"""
모바일 앱 통합 API
PWA 지원, 오프라인 기능, 푸시 알림 통합
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from functools import wraps
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

mobile_api_bp = Blueprint('mobile_api', __name__)

def mobile_required(f):
    """모바일 앱 권한 확인 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 모바일 앱 헤더 확인
        user_agent = request.headers.get('User-Agent', '')
        is_mobile = any(agent in user_agent.lower() for agent in ['mobile', 'android', 'ios'])
        
        if not is_mobile:
            return jsonify({'error': '모바일 앱에서만 접근 가능합니다.'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

@mobile_api_bp.route('/api/mobile/dashboard', methods=['GET'])
@login_required
@mobile_required
def mobile_dashboard():
    """모바일 대시보드 데이터"""
    try:
        # 모바일 최적화된 대시보드 데이터
        dashboard_data = {
            'user_info': {
                'id': current_user.id,
                'username': current_user.username,
                'role': current_user.role,
                'branch_id': current_user.branch_id
            },
            'quick_stats': {
                'today_orders': 15,
                'pending_orders': 3,
                'today_revenue': 450000,
                'staff_on_duty': 8
            },
            'recent_activities': [
                {
                    'id': 1,
                    'type': 'order',
                    'title': '새 주문 접수',
                    'message': '테이블 5번에서 김치찌개 2개 주문',
                    'timestamp': datetime.now().isoformat(),
                    'priority': 'normal'
                },
                {
                    'id': 2,
                    'type': 'inventory',
                    'title': '재고 부족 알림',
                    'message': '김치 재고가 부족합니다',
                    'timestamp': (datetime.now() - timedelta(minutes=30)).isoformat(),
                    'priority': 'high'
                }
            ],
            'quick_actions': [
                {
                    'id': 'new_order',
                    'title': '새 주문',
                    'icon': 'plus-circle',
                    'color': 'blue'
                },
                {
                    'id': 'inventory_check',
                    'title': '재고 확인',
                    'icon': 'package',
                    'color': 'green'
                },
                {
                    'id': 'staff_schedule',
                    'title': '근무표',
                    'icon': 'calendar',
                    'color': 'purple'
                },
                {
                    'id': 'reports',
                    'title': '리포트',
                    'icon': 'bar-chart',
                    'color': 'orange'
                }
            ]
        }
        
        return jsonify({
            'success': True,
            'data': dashboard_data,
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"모바일 대시보드 조회 실패: {e}")
        return jsonify({'error': '대시보드 조회에 실패했습니다.'}), 500

@mobile_api_bp.route('/api/mobile/offline-data', methods=['GET'])
@login_required
@mobile_required
def get_offline_data():
    """오프라인용 데이터 제공"""
    try:
        # 오프라인에서 필요한 기본 데이터
        offline_data = {
            'menu_items': [
                {
                    'id': 1,
                    'name': '김치찌개',
                    'price': 12000,
                    'category': '메인',
                    'available': True
                },
                {
                    'id': 2,
                    'name': '된장찌개',
                    'price': 10000,
                    'category': '메인',
                    'available': True
                },
                {
                    'id': 3,
                    'name': '비빔밥',
                    'price': 13000,
                    'category': '메인',
                    'available': True
                }
            ],
            'staff_list': [
                {
                    'id': 1,
                    'name': '김철수',
                    'role': '서버',
                    'phone': '010-1234-5678'
                },
                {
                    'id': 2,
                    'name': '이영희',
                    'role': '주방',
                    'phone': '010-2345-6789'
                }
            ],
            'tables': [
                {'id': 1, 'name': '테이블 1', 'capacity': 4, 'status': 'available'},
                {'id': 2, 'name': '테이블 2', 'capacity': 4, 'status': 'occupied'},
                {'id': 3, 'name': '테이블 3', 'capacity': 6, 'status': 'available'}
            ],
            'settings': {
                'restaurant_name': '맛있는 레스토랑',
                'address': '서울시 강남구 테헤란로 123',
                'phone': '02-1234-5678',
                'opening_hours': '09:00-22:00'
            }
        }
        
        return jsonify({
            'success': True,
            'data': offline_data,
            'cache_until': (datetime.now() + timedelta(hours=24)).isoformat()
        })
        
    except Exception as e:
        logger.error(f"오프라인 데이터 조회 실패: {e}")
        return jsonify({'error': '오프라인 데이터 조회에 실패했습니다.'}), 500

@mobile_api_bp.route('/api/mobile/sync', methods=['POST'])
@login_required
@mobile_required
def sync_offline_data():
    """오프라인 데이터 동기화"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        sync_data = data.get('sync_data', {})
        
        # 동기화할 데이터 처리
        synced_items = {
            'orders': [],
            'inventory_updates': [],
            'attendance_records': [],
            'sync_timestamp': datetime.now().isoformat()
        }
        
        # 주문 데이터 동기화
        if 'orders' in sync_data:
            for order in sync_data['orders']:
                # 주문 처리 로직
                synced_items['orders'].append({
                    'id': order.get('id'),
                    'status': 'synced',
                    'synced_at': datetime.now().isoformat()
                })
        
        # 재고 업데이트 동기화
        if 'inventory_updates' in sync_data:
            for update in sync_data['inventory_updates']:
                # 재고 업데이트 처리 로직
                synced_items['inventory_updates'].append({
                    'id': update.get('id'),
                    'status': 'synced',
                    'synced_at': datetime.now().isoformat()
                })
        
        # 출근 기록 동기화
        if 'attendance_records' in sync_data:
            for record in sync_data['attendance_records']:
                # 출근 기록 처리 로직
                synced_items['attendance_records'].append({
                    'id': record.get('id'),
                    'status': 'synced',
                    'synced_at': datetime.now().isoformat()
                })
        
        return jsonify({
            'success': True,
            'synced_items': synced_items,
            'message': f'{len(synced_items["orders"])}개 주문, {len(synced_items["inventory_updates"])}개 재고 업데이트, {len(synced_items["attendance_records"])}개 출근 기록이 동기화되었습니다.'
        })
        
    except Exception as e:
        logger.error(f"오프라인 데이터 동기화 실패: {e}")
        return jsonify({'error': '데이터 동기화에 실패했습니다.'}), 500

@mobile_api_bp.route('/api/mobile/push-token', methods=['POST'])
@login_required
@mobile_required
def register_push_token():
    """푸시 알림 토큰 등록"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        token = data.get('token')
        platform = data.get('platform', 'unknown')
        
        if not token:
            return jsonify({'error': '토큰이 필요합니다.'}), 400
        
        # 토큰 저장 로직 (실제로는 데이터베이스에 저장)
        # 여기서는 간단히 로그만 남김
        logger.info(f"푸시 토큰 등록: 사용자 {current_user.id}, 플랫폼 {platform}")
        
        return jsonify({
            'success': True,
            'message': '푸시 토큰이 성공적으로 등록되었습니다.',
            'registered_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"푸시 토큰 등록 실패: {e}")
        return jsonify({'error': '푸시 토큰 등록에 실패했습니다.'}), 500

@mobile_api_bp.route('/api/mobile/notifications', methods=['GET'])
@login_required
@mobile_required
def get_mobile_notifications():
    """모바일 알림 목록"""
    try:
        # 모바일 최적화된 알림 데이터
        notifications = [
            {
                'id': 1,
                'type': 'order',
                'title': '새 주문',
                'message': '테이블 3번에서 주문이 들어왔습니다.',
                'timestamp': datetime.now().isoformat(),
                'read': False,
                'priority': 'high'
            },
            {
                'id': 2,
                'type': 'inventory',
                'title': '재고 알림',
                'message': '김치 재고가 20% 미만입니다.',
                'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                'read': False,
                'priority': 'normal'
            },
            {
                'id': 3,
                'type': 'system',
                'title': '시스템 업데이트',
                'message': '새로운 기능이 추가되었습니다.',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'read': True,
                'priority': 'low'
            }
        ]
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'unread_count': len([n for n in notifications if not n['read']])
        })
        
    except Exception as e:
        logger.error(f"모바일 알림 조회 실패: {e}")
        return jsonify({'error': '알림 조회에 실패했습니다.'}), 500

@mobile_api_bp.route('/api/mobile/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
@mobile_required
def mark_notification_read(notification_id):
    """알림 읽음 처리"""
    try:
        # 알림 읽음 처리 로직
        logger.info(f"알림 읽음 처리: 사용자 {current_user.id}, 알림 {notification_id}")
        
        return jsonify({
            'success': True,
            'message': '알림이 읽음 처리되었습니다.',
            'notification_id': notification_id
        })
        
    except Exception as e:
        logger.error(f"알림 읽음 처리 실패: {e}")
        return jsonify({'error': '알림 읽음 처리에 실패했습니다.'}), 500

@mobile_api_bp.route('/api/mobile/orders/quick', methods=['POST'])
@login_required
@mobile_required
def create_quick_order():
    """빠른 주문 생성"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        table_id = data.get('table_id')
        items = data.get('items', [])
        
        if not table_id or not items:
            return jsonify({'error': '테이블 ID와 주문 항목이 필요합니다.'}), 400
        
        # 빠른 주문 생성 로직
        order_data = {
            'id': 12345,  # 실제로는 데이터베이스에서 생성
            'table_id': table_id,
            'items': items,
            'total_amount': sum(item.get('price', 0) * item.get('quantity', 1) for item in items),
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'created_by': current_user.id
        }
        
        return jsonify({
            'success': True,
            'order': order_data,
            'message': '주문이 성공적으로 생성되었습니다.'
        })
        
    except Exception as e:
        logger.error(f"빠른 주문 생성 실패: {e}")
        return jsonify({'error': '주문 생성에 실패했습니다.'}), 500

@mobile_api_bp.route('/api/mobile/orders/<int:order_id>/status', methods=['PUT'])
@login_required
@mobile_required
def update_order_status(order_id):
    """주문 상태 업데이트"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'error': '새로운 상태가 필요합니다.'}), 400
        
        # 주문 상태 업데이트 로직
        updated_order = {
            'id': order_id,
            'status': new_status,
            'updated_at': datetime.now().isoformat(),
            'updated_by': current_user.id
        }
        
        return jsonify({
            'success': True,
            'order': updated_order,
            'message': f'주문 상태가 {new_status}로 업데이트되었습니다.'
        })
        
    except Exception as e:
        logger.error(f"주문 상태 업데이트 실패: {e}")
        return jsonify({'error': '주문 상태 업데이트에 실패했습니다.'}), 500

@mobile_api_bp.route('/api/mobile/inventory/check', methods=['GET'])
@login_required
@mobile_required
def check_inventory():
    """재고 확인"""
    try:
        # 재고 확인 로직
        inventory_data = [
            {
                'id': 1,
                'name': '김치',
                'current_stock': 15,
                'min_stock': 20,
                'unit': 'kg',
                'status': 'low'
            },
            {
                'id': 2,
                'name': '된장',
                'current_stock': 25,
                'min_stock': 10,
                'unit': 'kg',
                'status': 'normal'
            },
            {
                'id': 3,
                'name': '고추가루',
                'current_stock': 8,
                'min_stock': 15,
                'unit': 'kg',
                'status': 'low'
            }
        ]
        
        return jsonify({
            'success': True,
            'inventory': inventory_data,
            'low_stock_count': len([item for item in inventory_data if item['status'] == 'low'])
        })
        
    except Exception as e:
        logger.error(f"재고 확인 실패: {e}")
        return jsonify({'error': '재고 확인에 실패했습니다.'}), 500

@mobile_api_bp.route('/api/mobile/attendance/check-in', methods=['POST'])
@login_required
@mobile_required
def mobile_check_in():
    """모바일 출근 체크인"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        location = data.get('location', {})
        
        # 출근 체크인 로직
        attendance_record = {
            'id': 12345,  # 실제로는 데이터베이스에서 생성
            'user_id': current_user.id,
            'check_in_time': datetime.now().isoformat(),
            'location': location,
            'status': 'checked_in'
        }
        
        return jsonify({
            'success': True,
            'attendance': attendance_record,
            'message': '출근이 기록되었습니다.'
        })
        
    except Exception as e:
        logger.error(f"모바일 출근 체크인 실패: {e}")
        return jsonify({'error': '출근 체크인에 실패했습니다.'}), 500

@mobile_api_bp.route('/api/mobile/attendance/check-out', methods=['POST'])
@login_required
@mobile_required
def mobile_check_out():
    """모바일 퇴근 체크아웃"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        location = data.get('location', {})
        
        # 퇴근 체크아웃 로직
        attendance_record = {
            'id': 12345,  # 실제로는 데이터베이스에서 생성
            'user_id': current_user.id,
            'check_out_time': datetime.now().isoformat(),
            'location': location,
            'status': 'checked_out'
        }
        
        return jsonify({
            'success': True,
            'attendance': attendance_record,
            'message': '퇴근이 기록되었습니다.'
        })
        
    except Exception as e:
        logger.error(f"모바일 퇴근 체크아웃 실패: {e}")
        return jsonify({'error': '퇴근 체크아웃에 실패했습니다.'}), 500 