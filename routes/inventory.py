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
            "name": "소고기",
            "category": "육류",
            "current_stock": 15,
            "min_stock": 20,
            "unit": "kg",
            "price": 45000,
            "supplier": "한우공급업체",
            "last_updated": "2025-03-03",
            "status": "부족"
        },
        {
            "id": 2,
            "name": "돼지고기",
            "category": "육류",
            "current_stock": 25,
            "min_stock": 15,
            "unit": "kg",
            "price": 28000,
            "supplier": "돈육공급업체",
            "last_updated": "2025-03-03",
            "status": "충분"
        },
        {
            "id": 3,
            "name": "양파",
            "category": "채소",
            "current_stock": 8,
            "min_stock": 10,
            "unit": "kg",
            "price": 3000,
            "supplier": "채소공급업체",
            "last_updated": "2025-03-03",
            "status": "부족"
        },
        {
            "id": 4,
            "name": "김치",
            "category": "반찬",
            "current_stock": 5,
            "min_stock": 8,
            "unit": "kg",
            "price": 8000,
            "supplier": "김치공급업체",
            "last_updated": "2025-03-01",
            "status": "부족"
        }
    ]
    
    return jsonify({"success": True, "data": inventory_list})

@inventory_bp.route('/api/inventory', methods=['POST'])
# @login_required
def create_inventory_item():
    """재고 품목 추가 API"""
    data = request.get_json()
    
    # 더미 응답
    new_item = {
        "id": 999,
        "name": data.get('name', '새 품목'),
        "category": data.get('category', '기타'),
        "current_stock": data.get('current_stock', 0),
        "min_stock": data.get('min_stock', 0),
        "unit": data.get('unit', '개'),
        "price": data.get('price', 0),
        "supplier": data.get('supplier', '기타공급업체'),
        "description": data.get('description', ''),
        "status": data.get('status', '부족'),
        "last_updated": datetime.now().strftime('%Y-%m-%d'),
        "created_at": datetime.now().isoformat()
    }
    
    return jsonify({"success": True, "data": new_item, "message": "품목이 성공적으로 추가되었습니다."})

@inventory_bp.route('/api/inventory/<int:item_id>', methods=['PUT'])
@login_required
def update_inventory_item(item_id):
    """재고 품목 수정 API"""
    data = request.get_json()
    
    # 더미 응답
    updated_item = {
        "id": item_id,
        "name": data.get('name', '수정된 품목'),
        "category": data.get('category', '기타'),
        "current_stock": data.get('current_stock', 0),
        "min_stock": data.get('min_stock', 0),
        "unit": data.get('unit', '개'),
        "price": data.get('price', 0),
        "supplier": data.get('supplier', '기타공급업체'),
        "description": data.get('description', ''),
        "status": data.get('status', '부족'),
        "last_updated": datetime.now().strftime('%Y-%m-%d'),
        "updated_at": datetime.now().isoformat()
    }
    
    return jsonify({"success": True, "data": updated_item, "message": "품목이 수정되었습니다."})

@inventory_bp.route('/api/inventory/<int:item_id>', methods=['DELETE'])
@login_required
def delete_inventory_item(item_id):
    """재고 품목 삭제 API"""
    return jsonify({"success": True, "message": f"품목 {item_id}가 삭제되었습니다."})

@inventory_bp.route('/api/inventory/<int:item_id>')
@login_required
def get_inventory_item(item_id):
    """재고 품목 상세 조회 API"""
    # 더미 상세 데이터
    item_detail = {
        "id": item_id,
        "name": "소고기",
        "category": "육류",
        "current_stock": 15,
        "min_stock": 20,
        "unit": "kg",
        "price": 45000,
        "supplier": "한우공급업체",
        "description": "한우 등급 소고기",
        "status": "부족",
        "last_updated": "2025-03-03",
        "created_at": "2025-01-15T10:00:00Z",
        "total_value": 675000,
        "stock_ratio": 75
    }
    
    return jsonify({"success": True, "data": item_detail})

@inventory_bp.route('/api/inventory/stats')
@login_required
def get_inventory_stats():
    """재고 통계 API"""
    # 더미 통계 데이터
    stats = {
        "total_items": 156,
        "low_stock_items": 23,
        "sufficient_items": 120,
        "danger_items": 13,
        "total_value": 8500000,
        "categories": {
            "육류": 25,
            "채소": 45,
            "반찬": 20,
            "곡물": 15,
            "조미료": 30,
            "유제품": 10,
            "음료": 11
        }
    }
    
    return jsonify({"success": True, "data": stats})

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