from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models import db, Order, InventoryItem, User, Branch, StockMovement
import json

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
    try:
        # 현재 사용자의 매장 ID 가져오기
        branch_id = current_user.branch_id
        
        # 발주 목록 조회 (발주자 정보 포함)
        orders = Order.query.filter_by(store_id=branch_id).order_by(Order.created_at.desc()).all()
        
        orders_list = []
        for order in orders:
            # 발주자 정보 조회
            ordered_by_user = User.query.get(order.ordered_by)
            ordered_by_name = ordered_by_user.name if ordered_by_user else "알 수 없음"
            
            orders_list.append({
                "id": order.id,
                "item": order.item,
                "quantity": order.quantity,
                "unit": order.unit,
                "order_date": order.order_date.strftime('%Y-%m-%d'),
                "ordered_by": ordered_by_name,  # 발주자 이름
                "ordered_by_id": order.ordered_by,  # 발주자 ID
                "status": order.status,
                "detail": order.detail,
                "memo": order.memo,
                "supplier": order.supplier,
                "unit_price": order.unit_price,
                "total_cost": order.total_cost,
                "created_at": order.created_at.strftime('%Y-%m-%d %H:%M'),
                "completed_at": order.completed_at.strftime('%Y-%m-%d %H:%M') if order.completed_at else None
            })
        
        return jsonify({"success": True, "data": orders_list})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@orders_bp.route('/api/orders', methods=['POST'])
@login_required
def create_order():
    """발주 생성 API"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        if not data.get('item') or not data.get('quantity'):
            return jsonify({"success": False, "error": "물품명과 수량은 필수입니다."}), 400
        
        # 재고 품목 확인 (기존 품목이 있는지)
        inventory_item = None
        if data.get('inventory_item_id'):
            inventory_item = InventoryItem.query.get(data.get('inventory_item_id'))
            if inventory_item and inventory_item.branch_id != current_user.branch_id:
                return jsonify({"success": False, "error": "권한이 없습니다."}), 403
        
        # 새 발주 생성 (발주자 정보 자동 저장)
        new_order = Order()
        new_order.item = data.get('item')
        new_order.quantity = data.get('quantity')
        new_order.unit = data.get('unit', '개')
        new_order.order_date = datetime.strptime(data.get('order_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
        new_order.ordered_by = current_user.id  # 현재 로그인 사용자가 발주자
        new_order.status = 'pending'
        new_order.detail = data.get('detail', '')
        new_order.memo = data.get('memo', '')
        new_order.store_id = current_user.branch_id
        new_order.inventory_item_id = inventory_item.id if inventory_item else None
        new_order.supplier = data.get('supplier', '')
        new_order.unit_price = data.get('unit_price', 0)
        new_order.total_cost = (data.get('quantity', 0) * data.get('unit_price', 0))
        
        db.session.add(new_order)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "data": {
                "id": new_order.id,
                "item": new_order.item,
                "quantity": new_order.quantity,
                "status": new_order.status,
                "ordered_by": current_user.name,  # 발주자 이름 반환
                "created_at": new_order.created_at.strftime('%Y-%m-%d %H:%M')
            }, 
            "message": "발주가 성공적으로 생성되었습니다."
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@orders_bp.route('/api/orders/<int:order_id>', methods=['PUT'])
@login_required
def update_order(order_id):
    """발주 수정 API"""
    try:
        data = request.get_json()
        order = Order.query.get_or_404(order_id)
        
        # 권한 확인
        if order.store_id != current_user.branch_id:
            return jsonify({"success": False, "error": "권한이 없습니다."}), 403
        
        # 승인된 발주는 수정 불가
        if order.status in ['approved', 'delivered']:
            return jsonify({"success": False, "error": "승인된 발주는 수정할 수 없습니다."}), 400
        
        # 필드 업데이트
        if 'item' in data:
            order.item = data['item']
        if 'quantity' in data:
            order.quantity = data['quantity']
        if 'unit' in data:
            order.unit = data['unit']
        if 'order_date' in data:
            order.order_date = datetime.strptime(data['order_date'], '%Y-%m-%d').date()
        if 'detail' in data:
            order.detail = data['detail']
        if 'memo' in data:
            order.memo = data['memo']
        if 'supplier' in data:
            order.supplier = data['supplier']
        if 'unit_price' in data:
            order.unit_price = data['unit_price']
            order.total_cost = order.quantity * data['unit_price']
        
        order.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "data": {
                "id": order.id,
                "item": order.item,
                "quantity": order.quantity,
                "status": order.status
            }, 
            "message": "발주가 수정되었습니다."
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@orders_bp.route('/api/orders/<int:order_id>', methods=['DELETE'])
@login_required
def delete_order(order_id):
    """발주 삭제 API"""
    try:
        order = Order.query.get_or_404(order_id)
        
        # 권한 확인
        if order.store_id != current_user.branch_id:
            return jsonify({"success": False, "error": "권한이 없습니다."}), 403
        
        # 승인된 발주는 삭제 불가
        if order.status in ['approved', 'delivered']:
            return jsonify({"success": False, "error": "승인된 발주는 삭제할 수 없습니다."}), 400
        
        db.session.delete(order)
        db.session.commit()
        
        return jsonify({"success": True, "message": f"발주 {order_id}가 삭제되었습니다."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@orders_bp.route('/api/orders/<int:order_id>')
@login_required
def get_order_detail(order_id):
    """발주 상세 조회 API"""
    try:
        order = Order.query.get_or_404(order_id)
        
        # 권한 확인
        if order.store_id != current_user.branch_id:
            return jsonify({"success": False, "error": "권한이 없습니다."}), 403
        
        order_detail = {
            "id": order.id,
            "item": order.item,
            "quantity": order.quantity,
            "unit": order.unit,
            "order_date": order.order_date.strftime('%Y-%m-%d'),
            "ordered_by": order.user.name if order.user else "알 수 없음",
            "status": order.status,
            "detail": order.detail,
            "memo": order.memo,
            "supplier": order.supplier,
            "unit_price": order.unit_price,
            "total_cost": order.total_cost,
            "created_at": order.created_at.strftime('%Y-%m-%d %H:%M'),
            "updated_at": order.updated_at.strftime('%Y-%m-%d %H:%M'),
            "completed_at": order.completed_at.strftime('%Y-%m-%d %H:%M') if order.completed_at else None,
            "inventory_item_id": order.inventory_item_id,
            "inventory_item_name": order.inventory_item.name if order.inventory_item else None
        }
        
        return jsonify({"success": True, "data": order_detail})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@orders_bp.route('/api/orders/<int:order_id>/approve', methods=['POST'])
@login_required
def approve_order(order_id):
    """발주 승인 API"""
    try:
        order = Order.query.get_or_404(order_id)
        
        # 권한 확인 (매장 관리자 또는 최고 관리자만)
        if current_user.branch_id != order.store_id and current_user.role != 'admin':
            return jsonify({"success": False, "error": "권한이 없습니다."}), 403
        
        order.status = 'approved'
        order.completed_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": "발주가 승인되었습니다."
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@orders_bp.route('/api/orders/<int:order_id>/reject', methods=['POST'])
@login_required
def reject_order(order_id):
    """발주 거절 API"""
    try:
        data = request.get_json()
        order = Order.query.get_or_404(order_id)
        
        # 권한 확인 (매장 관리자 또는 최고 관리자만)
        if current_user.branch_id != order.store_id and current_user.role != 'admin':
            return jsonify({"success": False, "error": "권한이 없습니다."}), 403
        
        order.status = 'rejected'
        order.memo = f"거절 사유: {data.get('reason', '관리자 거절')}"
        order.completed_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": "발주가 거절되었습니다."
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@orders_bp.route('/api/orders/<int:order_id>/deliver', methods=['POST'])
@login_required
def deliver_order(order_id):
    """발주 배송완료 API"""
    try:
        order = Order.query.get_or_404(order_id)
        
        # 권한 확인 (매장 관리자 또는 최고 관리자만)
        if current_user.branch_id != order.store_id and current_user.role != 'admin':
            return jsonify({"success": False, "error": "권한이 없습니다."}), 403
        
        order.status = 'delivered'
        order.completed_at = datetime.utcnow()
        
        # 재고에 자동 입고 처리
        if order.inventory_item_id:
            inventory_item = InventoryItem.query.get(order.inventory_item_id)
            if inventory_item:
                inventory_item.current_stock += order.quantity
                inventory_item.updated_at = datetime.utcnow()
                
                # 재고 변동 이력 기록
                stock_movement = StockMovement()
                stock_movement.inventory_item_id = inventory_item.id
                stock_movement.movement_type = 'in'
                stock_movement.quantity = order.quantity
                stock_movement.before_stock = inventory_item.current_stock
                stock_movement.after_stock = inventory_item.current_stock + order.quantity
                stock_movement.reason = f'발주 입고 (발주번호: {order.id})'
                stock_movement.created_by = current_user.id
                db.session.add(stock_movement)
        
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": "발주가 배송완료되었고 재고에 입고되었습니다."
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@orders_bp.route('/api/orders/stats')
@login_required
def get_orders_stats():
    """발주 통계 API"""
    try:
        branch_id = current_user.branch_id
        
        # 전체 발주 수
        total_orders = Order.query.filter_by(store_id=branch_id).count()
        
        # 상태별 통계
        pending_orders = Order.query.filter_by(store_id=branch_id, status='pending').count()
        approved_orders = Order.query.filter_by(store_id=branch_id, status='approved').count()
        delivered_orders = Order.query.filter_by(store_id=branch_id, status='delivered').count()
        rejected_orders = Order.query.filter_by(store_id=branch_id, status='rejected').count()
        
        # 총 비용
        total_cost = db.session.query(db.func.sum(Order.total_cost)).filter_by(store_id=branch_id).scalar() or 0
        
        # 이번 달 발주 수
        this_month = datetime.now().replace(day=1)
        monthly_orders = Order.query.filter(
            Order.store_id == branch_id,
            Order.created_at >= this_month
        ).count()
        
        # 이번 주 발주 수
        this_week = datetime.now() - timedelta(days=datetime.now().weekday())
        weekly_orders = Order.query.filter(
            Order.store_id == branch_id,
            Order.created_at >= this_week
        ).count()
        
        stats = {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "approved_orders": approved_orders,
            "delivered_orders": delivered_orders,
            "rejected_orders": rejected_orders,
            "total_cost": total_cost,
            "monthly_orders": monthly_orders,
            "weekly_orders": weekly_orders
        }
        
        return jsonify({"success": True, "data": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@orders_bp.route('/api/orders/inventory-items')
@login_required
def get_inventory_items_for_order():
    """발주용 재고 품목 목록 API"""
    try:
        branch_id = current_user.branch_id
        
        # 재고 품목 조회
        items = InventoryItem.query.filter_by(branch_id=branch_id, status='active').all()
        
        items_list = []
        for item in items:
            items_list.append({
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "current_stock": item.current_stock,
                "min_stock": item.min_stock,
                "unit": item.unit,
                "unit_price": item.unit_price,
                "supplier": item.supplier,
                "status": item.stock_status
            })
        
        return jsonify({"success": True, "data": items_list})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500 