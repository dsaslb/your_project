from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user
from datetime import datetime

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
    # 더미 재고 데이터
    inventory_list = [
        {
            "id": 1,
            "name": "토마토",
            "category": "농산물",
            "quantity": 25,
            "unit": "kg",
            "min_quantity": 10,
            "max_quantity": 100,
            "status": "normal",
            "last_updated": "2024-01-15T14:30:00Z",
            "expiry_date": "2024-01-25",
            "supplier": "농산물공급업체"
        },
        {
            "id": 2,
            "name": "치즈",
            "category": "유제품",
            "quantity": 5,
            "unit": "kg",
            "min_quantity": 8,
            "max_quantity": 50,
            "status": "low",
            "last_updated": "2024-01-15T12:00:00Z",
            "expiry_date": "2024-02-15",
            "supplier": "유제품공급업체"
        },
        {
            "id": 3,
            "name": "밀가루",
            "category": "곡물",
            "quantity": 80,
            "unit": "kg",
            "min_quantity": 20,
            "max_quantity": 200,
            "status": "normal",
            "last_updated": "2024-01-14T16:45:00Z",
            "expiry_date": "2024-06-15",
            "supplier": "곡물공급업체"
        },
        {
            "id": 4,
            "name": "올리브오일",
            "category": "조미료",
            "quantity": 15,
            "unit": "L",
            "min_quantity": 5,
            "max_quantity": 30,
            "status": "normal",
            "last_updated": "2024-01-13T09:20:00Z",
            "expiry_date": "2024-12-31",
            "supplier": "조미료공급업체"
        },
        {
            "id": 5,
            "name": "소고기",
            "category": "육류",
            "quantity": 3,
            "unit": "kg",
            "min_quantity": 5,
            "max_quantity": 25,
            "status": "low",
            "last_updated": "2024-01-15T08:15:00Z",
            "expiry_date": "2024-01-18",
            "supplier": "육류공급업체"
        }
    ]
    
    return jsonify({"success": True, "data": inventory_list})

@inventory_bp.route('/api/inventory', methods=['POST'])
@login_required
def create_inventory_item():
    """재고 항목 생성 API"""
    data = request.get_json()
    
    # 더미 응답
    new_item = {
        "id": 999,
        "name": data.get('name', '새 재고'),
        "category": data.get('category', '기타'),
        "quantity": data.get('quantity', 0),
        "unit": data.get('unit', '개'),
        "min_quantity": data.get('min_quantity', 0),
        "max_quantity": data.get('max_quantity', 100),
        "status": "normal",
        "last_updated": datetime.now().isoformat(),
        "expiry_date": data.get('expiry_date', ''),
        "supplier": data.get('supplier', '')
    }
    
    return jsonify({"success": True, "data": new_item, "message": "재고 항목이 생성되었습니다."})

@inventory_bp.route('/api/inventory/<int:item_id>', methods=['PUT'])
@login_required
def update_inventory_item(item_id):
    """재고 항목 수정 API"""
    data = request.get_json()
    
    # 더미 응답
    updated_item = {
        "id": item_id,
        "name": data.get('name', '수정된 재고'),
        "category": data.get('category', '기타'),
        "quantity": data.get('quantity', 0),
        "unit": data.get('unit', '개'),
        "min_quantity": data.get('min_quantity', 0),
        "max_quantity": data.get('max_quantity', 100),
        "status": "normal",
        "last_updated": datetime.now().isoformat(),
        "expiry_date": data.get('expiry_date', ''),
        "supplier": data.get('supplier', '')
    }
    
    return jsonify({"success": True, "data": updated_item, "message": "재고 항목이 수정되었습니다."})

@inventory_bp.route('/api/inventory/<int:item_id>', methods=['DELETE'])
@login_required
def delete_inventory_item(item_id):
    """재고 항목 삭제 API"""
    return jsonify({"success": True, "message": f"재고 항목 {item_id}가 삭제되었습니다."})

@inventory_bp.route('/api/inventory/<int:item_id>')
@login_required
def get_inventory_detail(item_id):
    """재고 상세 조회 API"""
    # 더미 상세 데이터
    item_detail = {
        "id": item_id,
        "name": "토마토",
        "category": "농산물",
        "quantity": 25,
        "unit": "kg",
        "min_quantity": 10,
        "max_quantity": 100,
        "status": "normal",
        "last_updated": "2024-01-15T14:30:00Z",
        "expiry_date": "2024-01-25",
        "supplier": "농산물공급업체",
        "description": "신선한 토마토",
        "price_per_unit": 3000,
        "total_value": 75000,
        "location": "냉장고 A-1",
        "barcode": "1234567890123"
    }
    
    return jsonify({"success": True, "data": item_detail})

@inventory_bp.route('/api/inventory/<int:item_id>/adjust', methods=['POST'])
@login_required
def adjust_inventory(item_id):
    """재고 수량 조정 API"""
    data = request.get_json()
    adjustment = data.get('adjustment', 0)
    reason = data.get('reason', '수량 조정')
    
    return jsonify({
        "success": True, 
        "message": f"재고 {item_id}의 수량이 {adjustment:+d} 조정되었습니다. 사유: {reason}"
    })

@inventory_bp.route('/api/inventory/low-stock')
@login_required
def get_low_stock_items():
    """재고 부족 항목 조회 API"""
    # 더미 재고 부족 데이터
    low_stock_items = [
        {
            "id": 2,
            "name": "치즈",
            "quantity": 5,
            "min_quantity": 8,
            "unit": "kg",
            "status": "low"
        },
        {
            "id": 5,
            "name": "소고기",
            "quantity": 3,
            "min_quantity": 5,
            "unit": "kg",
            "status": "low"
        }
    ]
    
    return jsonify({"success": True, "data": low_stock_items})

@inventory_bp.route('/api/inventory/expiring')
@login_required
def get_expiring_items():
    """유통기한 임박 항목 조회 API"""
    # 더미 유통기한 임박 데이터
    expiring_items = [
        {
            "id": 1,
            "name": "토마토",
            "expiry_date": "2024-01-25",
            "days_left": 10,
            "quantity": 25,
            "unit": "kg"
        },
        {
            "id": 5,
            "name": "소고기",
            "expiry_date": "2024-01-18",
            "days_left": 3,
            "quantity": 3,
            "unit": "kg"
        }
    ]
    
    return jsonify({"success": True, "data": expiring_items})

@inventory_bp.route('/api/inventory/stats')
@login_required
def get_inventory_stats():
    """재고 통계 API"""
    # 더미 통계 데이터
    stats = {
        "total_items": 45,
        "low_stock_items": 3,
        "expiring_items": 2,
        "total_value": 1250000,
        "categories": {
            "농산물": 15,
            "육류": 8,
            "유제품": 5,
            "조미료": 12,
            "곡물": 5
        },
        "monthly_usage": 850000,
        "waste_value": 25000
    }
    
    return jsonify({"success": True, "data": stats})

@inventory_bp.route('/api/inventory/categories')
@login_required
def get_inventory_categories():
    """재고 카테고리 목록 API"""
    # 더미 카테고리 데이터
    categories = [
        {"id": 1, "name": "농산물", "description": "신선한 채소와 과일"},
        {"id": 2, "name": "육류", "description": "신선한 고기류"},
        {"id": 3, "name": "유제품", "description": "우유, 치즈 등"},
        {"id": 4, "name": "조미료", "description": "소스, 향신료 등"},
        {"id": 5, "name": "곡물", "description": "쌀, 밀가루 등"}
    ]
    
    return jsonify({"success": True, "data": categories}) 