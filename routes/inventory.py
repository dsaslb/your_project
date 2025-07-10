from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models import db, InventoryItem, StockMovement, Order, your_programOrder, User, Branch
import json

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/inventory')
@login_required
def inventory():
    """재고 관리 메인 페이지"""
    return render_template('inventory.html', user=current_user)

@inventory_bp.route('/api/inventory')
@login_required
def get_inventory():
    """재고 목록 조회 API"""
    try:
        # 현재 사용자의 매장 ID 가져오기
        branch_id = current_user.branch_id
        
        # 재고 품목 조회
        items = InventoryItem.query.filter_by(branch_id=branch_id, status='active').all()
        
        inventory_list = []
        for item in items:
            inventory_list.append({
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "current_stock": item.current_stock,
                "min_stock": item.min_stock,
                "max_stock": item.max_stock,
                "unit": item.unit,
                "unit_price": item.unit_price,
                "supplier": item.supplier,
                "description": item.description,
                "location": item.location,
                "status": item.stock_status,
                "total_value": item.total_value,
                "stock_ratio": item.stock_ratio,
                "last_updated": item.updated_at.strftime('%Y-%m-%d'),
                "expiry_date": item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else None
            })
        
        return jsonify({"success": True, "data": inventory_list})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@inventory_bp.route('/api/inventory', methods=['POST'])
@login_required
def create_inventory_item():
    """재고 품목 추가 API"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        if not data.get('name') or not data.get('category'):
            return jsonify({"success": False, "error": "품목명과 카테고리는 필수입니다."}), 400
        
        # 새 재고 품목 생성
        new_item = InventoryItem(
            name=data.get('name'),
            category=data.get('category'),
            current_stock=data.get('current_stock', 0),
            min_stock=data.get('min_stock', 0),
            max_stock=data.get('max_stock', 1000),
            unit=data.get('unit', '개'),
            unit_price=data.get('unit_price', 0),
            supplier=data.get('supplier', ''),
            description=data.get('description', ''),
            location=data.get('location', ''),
            branch_id=current_user.branch_id
        )
        
        db.session.add(new_item)
        db.session.commit()
        
        # 재고 변동 이력 기록
        if new_item.current_stock > 0:
            movement = StockMovement(
                inventory_item_id=new_item.id,
                movement_type='in',
                quantity=new_item.current_stock,
                before_stock=0,
                after_stock=new_item.current_stock,
                reason='초기 등록',
                reference_type='manual',
                created_by=current_user.id
            )
            db.session.add(movement)
            db.session.commit()
        
        return jsonify({
            "success": True, 
            "data": {
                "id": new_item.id,
                "name": new_item.name,
                "category": new_item.category,
                "current_stock": new_item.current_stock,
                "status": new_item.stock_status
            }, 
            "message": "품목이 성공적으로 추가되었습니다."
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@inventory_bp.route('/api/inventory/<int:item_id>', methods=['PUT'])
@login_required
def update_inventory_item(item_id):
    """재고 품목 수정 API"""
    try:
        data = request.get_json()
        item = InventoryItem.query.get_or_404(item_id)
        
        # 권한 확인 (같은 매장의 품목만 수정 가능)
        if item.branch_id != current_user.branch_id:
            return jsonify({"success": False, "error": "권한이 없습니다."}), 403
        
        # 기존 재고량 저장
        old_stock = item.current_stock
        
        # 필드 업데이트
        if 'name' in data:
            item.name = data['name']
        if 'category' in data:
            item.category = data['category']
        if 'min_stock' in data:
            item.min_stock = data['min_stock']
        if 'max_stock' in data:
            item.max_stock = data['max_stock']
        if 'unit' in data:
            item.unit = data['unit']
        if 'unit_price' in data:
            item.unit_price = data['unit_price']
        if 'supplier' in data:
            item.supplier = data['supplier']
        if 'description' in data:
            item.description = data['description']
        if 'location' in data:
            item.location = data['location']
        if 'status' in data:
            item.status = data['status']
        
        # 재고량 변경이 있는 경우 이력 기록
        if 'current_stock' in data and data['current_stock'] != old_stock:
            movement = StockMovement(
                inventory_item_id=item.id,
                movement_type='adjust',
                quantity=data['current_stock'] - old_stock,
                before_stock=old_stock,
                after_stock=data['current_stock'],
                reason=data.get('reason', '수동 조정'),
                reference_type='manual',
                created_by=current_user.id
            )
            db.session.add(movement)
            item.current_stock = data['current_stock']
        
        item.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "data": {
                "id": item.id,
                "name": item.name,
                "current_stock": item.current_stock,
                "status": item.stock_status
            }, 
            "message": "품목이 수정되었습니다."
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@inventory_bp.route('/api/inventory/<int:item_id>', methods=['DELETE'])
@login_required
def delete_inventory_item(item_id):
    """재고 품목 삭제 API"""
    try:
        item = InventoryItem.query.get_or_404(item_id)
        
        # 권한 확인
        if item.branch_id != current_user.branch_id:
            return jsonify({"success": False, "error": "권한이 없습니다."}), 403
        
        # 실제 삭제 대신 비활성화
        item.status = 'inactive'
        item.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({"success": True, "message": f"품목 {item.name}이 비활성화되었습니다."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@inventory_bp.route('/api/inventory/<int:item_id>')
@login_required
def get_inventory_item(item_id):
    """재고 품목 상세 조회 API"""
    try:
        item = InventoryItem.query.get_or_404(item_id)
        
        # 권한 확인
        if item.branch_id != current_user.branch_id:
            return jsonify({"success": False, "error": "권한이 없습니다."}), 403
        
        # 최근 재고 변동 이력 조회
        recent_movements = StockMovement.query.filter_by(inventory_item_id=item.id)\
            .order_by(StockMovement.created_at.desc()).limit(10).all()
        
        movements = []
        for movement in recent_movements:
            movements.append({
                "id": movement.id,
                "type": movement.movement_type,
                "quantity": movement.quantity,
                "before_stock": movement.before_stock,
                "after_stock": movement.after_stock,
                "reason": movement.reason,
                "created_at": movement.created_at.strftime('%Y-%m-%d %H:%M'),
                "created_by": movement.created_by_user.name if movement.created_by_user else "알 수 없음"
            })
        
        item_detail = {
            "id": item.id,
            "name": item.name,
            "category": item.category,
            "current_stock": item.current_stock,
            "min_stock": item.min_stock,
            "max_stock": item.max_stock,
            "unit": item.unit,
            "unit_price": item.unit_price,
            "supplier": item.supplier,
            "description": item.description,
            "location": item.location,
            "status": item.stock_status,
            "total_value": item.total_value,
            "stock_ratio": item.stock_ratio,
            "expiry_date": item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else None,
            "created_at": item.created_at.strftime('%Y-%m-%d'),
            "updated_at": item.updated_at.strftime('%Y-%m-%d'),
            "recent_movements": movements
        }
        
        return jsonify({"success": True, "data": item_detail})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@inventory_bp.route('/api/inventory/stats')
@login_required
def get_inventory_stats():
    """재고 통계 API"""
    try:
        branch_id = current_user.branch_id
        
        # 전체 품목 수
        total_items = InventoryItem.query.filter_by(branch_id=branch_id, status='active').count()
        
        # 재고 상태별 통계
        items = InventoryItem.query.filter_by(branch_id=branch_id, status='active').all()
        
        low_stock_items = sum(1 for item in items if item.stock_status == "부족")
        sufficient_items = sum(1 for item in items if item.stock_status == "충분")
        out_of_stock_items = sum(1 for item in items if item.stock_status == "품절")
        overstock_items = sum(1 for item in items if item.stock_status == "과다")
        
        # 총 재고 가치
        total_value = sum(item.total_value for item in items)
        
        # 카테고리별 통계
        categories = {}
        for item in items:
            if item.category not in categories:
                categories[item.category] = 0
            categories[item.category] += 1
        
        stats = {
            "total_items": total_items,
            "low_stock_items": low_stock_items,
            "sufficient_items": sufficient_items,
            "out_of_stock_items": out_of_stock_items,
            "overstock_items": overstock_items,
            "total_value": total_value,
            "categories": categories
        }
        
        return jsonify({"success": True, "data": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@inventory_bp.route('/api/inventory/low-stock')
@login_required
def get_low_stock_items():
    """재고 부족 품목 조회 API"""
    try:
        branch_id = current_user.branch_id
        
        # 재고 부족 또는 품절인 품목 조회
        low_stock_items = InventoryItem.query.filter(
            InventoryItem.branch_id == branch_id,
            InventoryItem.status == 'active',
            (InventoryItem.current_stock <= InventoryItem.min_stock) | 
            (InventoryItem.current_stock == 0)
        ).all()
        
        items = []
        for item in low_stock_items:
            items.append({
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "current_stock": item.current_stock,
                "min_stock": item.min_stock,
                "unit": item.unit,
                "status": item.stock_status,
                "supplier": item.supplier
            })
        
        return jsonify({"success": True, "data": items})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@inventory_bp.route('/api/inventory/consume', methods=['POST'])
@login_required
def consume_stock():
    """재고 소비 API (주문 처리 시 사용)"""
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        items = data.get('items', [])  # [{"item_id": 1, "quantity": 2}, ...]
        
        if not order_id or not items:
            return jsonify({"success": False, "error": "주문 ID와 소비할 품목 정보가 필요합니다."}), 400
        
        consumed_items = []
        
        for item_data in items:
            item_id = item_data.get('item_id')
            quantity = item_data.get('quantity', 0)
            
            if quantity <= 0:
                continue
                
            inventory_item = InventoryItem.query.get(item_id)
            if not inventory_item:
                continue
                
            # 권한 확인
            if inventory_item.branch_id != current_user.branch_id:
                continue
            
            # 재고 확인
            if inventory_item.current_stock < quantity:
                return jsonify({
                    "success": False, 
                    "error": f"{inventory_item.name}의 재고가 부족합니다. (현재: {inventory_item.current_stock}, 필요: {quantity})"
                }), 400
            
            # 재고 차감
            old_stock = inventory_item.current_stock
            inventory_item.current_stock -= quantity
            
            # 재고 변동 이력 기록
            movement = StockMovement(
                inventory_item_id=item_id,
                movement_type='out',
                quantity=-quantity,
                before_stock=old_stock,
                after_stock=inventory_item.current_stock,
                reason=f'주문 처리 (주문번호: {order_id})',
                reference_type='your_program_order',
                reference_id=order_id,
                created_by=current_user.id
            )
            
            db.session.add(movement)
            consumed_items.append({
                "item_id": item_id,
                "name": inventory_item.name,
                "quantity": quantity,
                "remaining_stock": inventory_item.current_stock
            })
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "data": consumed_items,
            "message": f"{len(consumed_items)}개 품목의 재고가 소비되었습니다."
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@inventory_bp.route('/api/inventory/receive-order', methods=['POST'])
@login_required
def receive_order():
    """발주 입고 처리 API"""
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        
        if not order_id:
            return jsonify({"success": False, "error": "발주 ID가 필요합니다."}), 400
        
        # 발주 정보 조회
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"success": False, "error": "발주를 찾을 수 없습니다."}), 404
        
        # 권한 확인
        if order.store_id != current_user.branch_id:
            return jsonify({"success": False, "error": "권한이 없습니다."}), 403
        
        # 발주 상태 확인
        if order.status != 'approved':
            return jsonify({"success": False, "error": "승인된 발주만 입고 처리할 수 있습니다."}), 400
        
        # 재고 품목 조회 또는 생성
        inventory_item = None
        if order.inventory_item_id:
            inventory_item = InventoryItem.query.get(order.inventory_item_id)
        else:
            # 새 재고 품목 생성
            inventory_item = InventoryItem(
                name=order.item,
                category='기타',
                current_stock=0,
                min_stock=0,
                unit=order.unit,
                unit_price=order.unit_price or 0,
                supplier=order.supplier or '',
                branch_id=current_user.branch_id
            )
            db.session.add(inventory_item)
            db.session.flush()  # ID 생성
        
        # 재고 입고 처리
        old_stock = inventory_item.current_stock
        inventory_item.current_stock += order.quantity
        
        # 재고 변동 이력 기록
        movement = StockMovement(
            inventory_item_id=inventory_item.id,
            movement_type='in',
            quantity=order.quantity,
            before_stock=old_stock,
            after_stock=inventory_item.current_stock,
            reason=f'발주 입고 (발주번호: {order_id})',
            reference_type='order',
            reference_id=order_id,
            created_by=current_user.id
        )
        
        # 발주 상태 업데이트
        order.status = 'delivered'
        order.completed_at = datetime.utcnow()
        
        db.session.add(movement)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "data": {
                "order_id": order_id,
                "item_name": inventory_item.name,
                "quantity": order.quantity,
                "new_stock": inventory_item.current_stock
            },
            "message": "발주가 성공적으로 입고되었습니다."
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@inventory_bp.route('/api/inventory/categories')
@login_required
def get_categories():
    """카테고리 목록 API"""
    categories = [
        {"id": 1, "name": "육류", "count": 25},
        {"id": 2, "name": "채소", "count": 45},
        {"id": 3, "name": "반찬", "count": 20},
        {"id": 4, "name": "곡물", "count": 15},
        {"id": 5, "name": "조미료", "count": 30},
        {"id": 6, "name": "유제품", "count": 10},
        {"id": 7, "name": "음료", "count": 11}
    ]
    
    return jsonify({"success": True, "data": categories})

@inventory_bp.route('/api/inventory/suppliers')
@login_required
def get_suppliers():
    """공급업체 목록 API"""
    suppliers = [
        {"id": 1, "name": "한우공급업체", "category": "육류", "contact": "010-1111-2222"},
        {"id": 2, "name": "돈육공급업체", "category": "육류", "contact": "010-2222-3333"},
        {"id": 3, "name": "채소공급업체", "category": "채소", "contact": "010-3333-4444"},
        {"id": 4, "name": "김치공급업체", "category": "반찬", "contact": "010-4444-5555"},
        {"id": 5, "name": "쌀공급업체", "category": "곡물", "contact": "010-5555-6666"},
        {"id": 6, "name": "조미료공급업체", "category": "조미료", "contact": "010-6666-7777"}
    ]
    
    return jsonify({"success": True, "data": suppliers}) 
