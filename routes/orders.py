from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders')
@login_required
def orders():
    """발주 관리 메인 페이지"""
    return render_template('orders.html', user=current_user)

@orders_bp.route('/api/orders')
@login_required
def get_orders():
    """발주 목록 조회 API"""
    # 더미 발주 데이터
    orders_list = [
        {
            "id": 1,
            "item": "토마토",
            "quantity": 50,
            "unit": "kg",
            "order_date": "2024-01-15",
            "ordered_by": "홍길동",
            "status": "pending",
            "detail": "신선한 토마토 필요",
            "memo": "급하게 필요합니다",
            "created_at": "2024-01-15T10:00:00Z"
        },
        {
            "id": 2,
            "item": "치즈",
            "quantity": 20,
            "unit": "kg",
            "order_date": "2024-01-14",
            "ordered_by": "김철수",
            "status": "approved",
            "detail": "모짜렐라 치즈",
            "memo": "",
            "created_at": "2024-01-14T14:30:00Z"
        },
        {
            "id": 3,
            "item": "밀가루",
            "quantity": 100,
            "unit": "kg",
            "order_date": "2024-01-13",
            "ordered_by": "이영희",
            "status": "delivered",
            "detail": "고급 밀가루",
            "memo": "이미 배송완료",
            "created_at": "2024-01-13T09:15:00Z"
        },
        {
            "id": 4,
            "item": "올리브오일",
            "quantity": 10,
            "unit": "L",
            "order_date": "2024-01-12",
            "ordered_by": "박민수",
            "status": "rejected",
            "detail": "엑스트라 버진",
            "memo": "예산 초과로 거절",
            "created_at": "2024-01-12T16:45:00Z"
        }
    ]
    
    return jsonify({"success": True, "data": orders_list})

@orders_bp.route('/api/orders', methods=['POST'])
# @login_required
def create_order():
    """주문 생성 API"""
    data = request.get_json()
    
    # 더미 응답
    new_order = {
        "id": f"ORD-{str(999).zfill(3)}",
        "customer_name": data.get('customer_name', '새 고객'),
        "phone": data.get('phone', '010-0000-0000'),
        "table": data.get('table', 'A-1'),
        "items": data.get('items', []),
        "notes": data.get('notes', ''),
        "estimated_time": data.get('estimated_time', '30'),
        "total": data.get('total', 0),
        "status": "대기중",
        "order_time": datetime.now().strftime('%Y-%m-%d %H:%M'),
        "estimated_completion": (datetime.now() + timedelta(minutes=int(data.get('estimated_time', 30)))).strftime('%H:%M')
    }
    
    return jsonify({"success": True, "data": new_order, "message": "주문이 성공적으로 추가되었습니다."})

@orders_bp.route('/api/orders/<int:order_id>', methods=['PUT'])
@login_required
def update_order(order_id):
    """발주 수정 API"""
    data = request.get_json()
    
    # 더미 응답
    updated_order = {
        "id": order_id,
        "item": data.get('item', '수정된 물품'),
        "quantity": data.get('quantity', 1),
        "unit": data.get('unit', '개'),
        "order_date": data.get('order_date', datetime.now().strftime('%Y-%m-%d')),
        "ordered_by": data.get('ordered_by', '수정자'),
        "status": data.get('status', 'pending'),
        "detail": data.get('detail', ''),
        "memo": data.get('memo', ''),
        "updated_at": datetime.now().isoformat()
    }
    
    return jsonify({"success": True, "data": updated_order, "message": "발주가 수정되었습니다."})

@orders_bp.route('/api/orders/<int:order_id>', methods=['DELETE'])
@login_required
def delete_order(order_id):
    """발주 삭제 API"""
    return jsonify({"success": True, "message": f"발주 {order_id}가 삭제되었습니다."})

@orders_bp.route('/api/orders/<int:order_id>')
@login_required
def get_order_detail(order_id):
    """발주 상세 조회 API"""
    # 더미 상세 데이터
    order_detail = {
        "id": order_id,
        "item": "토마토",
        "quantity": 50,
        "unit": "kg",
        "order_date": "2024-01-15",
        "ordered_by": "홍길동",
        "status": "pending",
        "detail": "신선한 토마토 필요",
        "memo": "급하게 필요합니다",
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T10:00:00Z",
        "approved_by": None,
        "approved_at": None,
        "delivered_at": None,
        "supplier": "농산물공급업체",
        "estimated_cost": 150000,
        "actual_cost": None
    }
    
    return jsonify({"success": True, "data": order_detail})

@orders_bp.route('/api/orders/<int:order_id>/approve', methods=['POST'])
@login_required
def approve_order(order_id):
    """발주 승인 API"""
    return jsonify({"success": True, "message": f"발주 {order_id}가 승인되었습니다."})

@orders_bp.route('/api/orders/<int:order_id>/reject', methods=['POST'])
@login_required
def reject_order(order_id):
    """발주 거절 API"""
    data = request.get_json()
    reason = data.get('reason', '사유 없음')
    return jsonify({"success": True, "message": f"발주 {order_id}가 거절되었습니다. 사유: {reason}"})

@orders_bp.route('/api/orders/<int:order_id>/deliver', methods=['POST'])
@login_required
def deliver_order(order_id):
    """발주 배송완료 API"""
    return jsonify({"success": True, "message": f"발주 {order_id}가 배송완료되었습니다."})

@orders_bp.route('/api/orders/stats')
@login_required
def get_orders_stats():
    """발주 통계 API"""
    # 더미 통계 데이터
    stats = {
        "total_orders": 156,
        "pending_orders": 23,
        "approved_orders": 45,
        "delivered_orders": 78,
        "rejected_orders": 10,
        "total_cost": 8500000,
        "monthly_orders": 45,
        "weekly_orders": 12
    }
    
    return jsonify({"success": True, "data": stats})

@orders_bp.route('/api/orders/suppliers')
@login_required
def get_suppliers():
    """공급업체 목록 API"""
    # 더미 공급업체 데이터
    suppliers = [
        {"id": 1, "name": "농산물공급업체", "contact": "010-1111-2222", "category": "농산물"},
        {"id": 2, "name": "육류공급업체", "contact": "010-2222-3333", "category": "육류"},
        {"id": 3, "name": "수산물공급업체", "contact": "010-3333-4444", "category": "수산물"},
        {"id": 4, "name": "조미료공급업체", "contact": "010-4444-5555", "category": "조미료"}
    ]
    
    return jsonify({"success": True, "data": suppliers}) 