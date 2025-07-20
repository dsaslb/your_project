"""
구매관리 플러그인 API 라우트
"""

from datetime import datetime, timedelta
from flask import request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import and_, func
from extensions import db
from models_main import PurchaseSupplier as Supplier, PurchaseOrder, PurchaseOrderItem, PurchaseSettings
from plugins.purchase_management import purchase_bp

@purchase_bp.route('/suppliers', methods=['GET'])
@login_required
def get_suppliers():
    """공급업체 목록 조회"""
    try:
        store_id = request.args.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        suppliers = Supplier.query.filter_by(store_id=store_id, is_active=True).order_by(Supplier.name).all()
        
        supplier_list = []
        for supplier in suppliers:
            supplier_list.append({
                'id': supplier.id,
                'name': supplier.name,
                'contact_person': supplier.contact_person,
                'email': supplier.email,
                'phone': supplier.phone,
                'address': supplier.address,
                'business_number': supplier.business_number,
                'payment_terms': supplier.payment_terms,
                'credit_limit': supplier.credit_limit,
                'notes': supplier.notes
            })
        
        return jsonify({
            'suppliers': supplier_list,
            'total_count': len(supplier_list)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"공급업체 목록 조회 오류: {str(e)}")
        return jsonify({'error': '공급업체 목록 조회 중 오류가 발생했습니다.'}), 500

@purchase_bp.route('/suppliers', methods=['POST'])
@login_required
def create_supplier():
    """공급업체 생성"""
    try:
        data = request.get_json()
        store_id = data.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        if not data.get('name'):
            return jsonify({'error': '공급업체명이 필요합니다.'}), 400
        
        supplier = Supplier(
            store_id=store_id,
            name=data['name'],
            contact_person=data.get('contact_person'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            business_number=data.get('business_number'),
            payment_terms=data.get('payment_terms', 30),
            credit_limit=data.get('credit_limit', 0.0),
            notes=data.get('notes')
        )
        
        db.session.add(supplier)
        db.session.commit()
        
        return jsonify({
            'message': '공급업체가 생성되었습니다.',
            'supplier_id': supplier.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"공급업체 생성 오류: {str(e)}")
        return jsonify({'error': '공급업체 생성 중 오류가 발생했습니다.'}), 500

@purchase_bp.route('/orders', methods=['GET'])
@login_required
def get_purchase_orders():
    """구매 주문 목록 조회"""
    try:
        store_id = request.args.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        status = request.args.get('status')
        supplier_id = request.args.get('supplier_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        query = PurchaseOrder.query.filter_by(store_id=store_id)
        
        if status:
            query = query.filter(PurchaseOrder.status == PurchaseStatus(status))
        
        if supplier_id:
            query = query.filter_by(supplier_id=supplier_id)
        
        if start_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(PurchaseOrder.order_date >= start_datetime)
        
        if end_date:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(PurchaseOrder.order_date <= end_datetime)
        
        orders = query.order_by(PurchaseOrder.order_date.desc()).all()
        
        order_list = []
        for order in orders:
            order_list.append({
                'id': order.id,
                'order_number': order.order_number,
                'supplier_name': order.supplier.name,
                'order_date': order.order_date.isoformat(),
                'expected_delivery_date': order.expected_delivery_date.isoformat() if order.expected_delivery_date else None,
                'status': order.status.value,
                'payment_status': order.payment_status.value,
                'total_amount': order.total_amount,
                'created_by': order.created_user.username,
                'approved_by': order.approved_user.username if order.approved_user else None
            })
        
        return jsonify({
            'orders': order_list,
            'total_count': len(order_list)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"구매 주문 목록 조회 오류: {str(e)}")
        return jsonify({'error': '구매 주문 목록 조회 중 오류가 발생했습니다.'}), 500

@purchase_bp.route('/orders', methods=['POST'])
@login_required
def create_purchase_order():
    """구매 주문 생성"""
    try:
        data = request.get_json()
        store_id = data.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        if not data.get('supplier_id'):
            return jsonify({'error': '공급업체 ID가 필요합니다.'}), 400
        
        if not data.get('items') or len(data['items']) == 0:
            return jsonify({'error': '주문 항목이 필요합니다.'}), 400
        
        # 주문번호 생성
        order_number = f"PO{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 구매 주문 생성
        order = PurchaseOrder(
            store_id=store_id,
            supplier_id=data['supplier_id'],
            order_number=order_number,
            expected_delivery_date=datetime.strptime(data['expected_delivery_date'], '%Y-%m-%d') if data.get('expected_delivery_date') else None,
            notes=data.get('notes'),
            created_by=current_user.id
        )
        
        db.session.add(order)
        db.session.flush()  # ID 생성
        
        # 주문 항목 생성
        for item_data in data['items']:
            item = PurchaseOrderItem(
                purchase_order_id=order.id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                notes=item_data.get('notes')
            )
            item.calculate_total()
            db.session.add(item)
        
        # 총액 계산
        order.calculate_totals()
        
        # 자동 승인 여부 확인
        settings = PurchaseSettings.query.filter_by(store_id=store_id).first()
        if settings and order.total_amount <= settings.auto_approval_limit:
            order.status = PurchaseStatus.APPROVED
            order.approved_by = current_user.id
            order.approved_at = datetime.now()
        else:
            order.status = PurchaseStatus.PENDING
        
        db.session.commit()
        
        return jsonify({
            'message': '구매 주문이 생성되었습니다.',
            'order_id': order.id,
            'order_number': order.order_number,
            'status': order.status.value
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"구매 주문 생성 오류: {str(e)}")
        return jsonify({'error': '구매 주문 생성 중 오류가 발생했습니다.'}), 500

@purchase_bp.route('/orders/<int:order_id>', methods=['GET'])
@login_required
def get_purchase_order_detail(order_id):
    """구매 주문 상세 조회"""
    try:
        order = PurchaseOrder.query.get_or_404(order_id)
        
        order_detail = {
            'id': order.id,
            'order_number': order.order_number,
            'supplier': {
                'id': order.supplier.id,
                'name': order.supplier.name,
                'contact_person': order.supplier.contact_person,
                'email': order.supplier.email,
                'phone': order.supplier.phone
            },
            'order_date': order.order_date.isoformat(),
            'expected_delivery_date': order.expected_delivery_date.isoformat() if order.expected_delivery_date else None,
            'status': order.status.value,
            'payment_status': order.payment_status.value,
            'subtotal': order.subtotal,
            'tax_amount': order.tax_amount,
            'total_amount': order.total_amount,
            'notes': order.notes,
            'created_by': order.created_user.username,
            'approved_by': order.approved_user.username if order.approved_user else None,
            'approved_at': order.approved_at.isoformat() if order.approved_at else None,
            'items': []
        }
        
        for item in order.order_items:
            order_detail['items'].append({
                'id': item.id,
                'product_name': item.product.name,
                'product_sku': item.product.sku,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'total_price': item.total_price,
                'received_quantity': item.received_quantity,
                'notes': item.notes
            })
        
        return jsonify(order_detail), 200
        
    except Exception as e:
        current_app.logger.error(f"구매 주문 상세 조회 오류: {str(e)}")
        return jsonify({'error': '구매 주문 상세 조회 중 오류가 발생했습니다.'}), 500

@purchase_bp.route('/orders/<int:order_id>/approve', methods=['POST'])
@login_required
def approve_purchase_order(order_id):
    """구매 주문 승인"""
    try:
        order = PurchaseOrder.query.get_or_404(order_id)
        
        if order.status != PurchaseStatus.PENDING:
            return jsonify({'error': '승인 대기 상태의 주문만 승인할 수 있습니다.'}), 400
        
        order.status = PurchaseStatus.APPROVED
        order.approved_by = current_user.id
        order.approved_at = datetime.now()
        
        db.session.commit()
        
        return jsonify({'message': '구매 주문이 승인되었습니다.'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"구매 주문 승인 오류: {str(e)}")
        return jsonify({'error': '구매 주문 승인 중 오류가 발생했습니다.'}), 500

@purchase_bp.route('/orders/<int:order_id>/receive', methods=['POST'])
@login_required
def receive_purchase_order(order_id):
    """구매 주문 입고 처리"""
    try:
        data = request.get_json()
        order = PurchaseOrder.query.get_or_404(order_id)
        
        if order.status != PurchaseStatus.ORDERED:
            return jsonify({'error': '주문된 상태의 주문만 입고 처리할 수 있습니다.'}), 400
        
        received_items = data.get('received_items', [])
        
        for received_item in received_items:
            item_id = received_item['item_id']
            received_quantity = received_item['received_quantity']
            
            order_item = PurchaseOrderItem.query.get(item_id)
            if order_item and order_item.purchase_order_id == order.id:
                order_item.received_quantity = received_quantity
        
        # 모든 항목이 입고되었는지 확인
        all_received = all(
            item.received_quantity >= item.quantity 
            for item in order.order_items
        )
        
        if all_received:
            order.status = PurchaseStatus.RECEIVED
        
        db.session.commit()
        
        return jsonify({'message': '입고 처리가 완료되었습니다.'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"구매 주문 입고 처리 오류: {str(e)}")
        return jsonify({'error': '입고 처리 중 오류가 발생했습니다.'}), 500

@purchase_bp.route('/settings', methods=['GET'])
@login_required
def get_purchase_settings():
    """구매 관리 설정 조회"""
    try:
        store_id = request.args.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        settings = PurchaseSettings.query.filter_by(store_id=store_id).first()
        
        if not settings:
            return jsonify({'error': '구매 관리 설정이 없습니다.'}), 404
        
        return jsonify({
            'auto_approval_limit': settings.auto_approval_limit,
            'default_payment_terms': settings.default_payment_terms,
            'email_notifications': settings.email_notifications,
            'sms_notifications': settings.sms_notifications,
            'approval_workflow': settings.approval_workflow
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"구매 설정 조회 오류: {str(e)}")
        return jsonify({'error': '구매 설정 조회 중 오류가 발생했습니다.'}), 500

@purchase_bp.route('/settings', methods=['PUT'])
@login_required
def update_purchase_settings():
    """구매 관리 설정 업데이트"""
    try:
        store_id = request.args.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        data = request.get_json()
        settings = PurchaseSettings.query.filter_by(store_id=store_id).first()
        
        if not settings:
            settings = PurchaseSettings(store_id=store_id)
            db.session.add(settings)
        
        # 설정 업데이트
        updatable_fields = [
            'auto_approval_limit', 'default_payment_terms', 'email_notifications',
            'sms_notifications', 'approval_workflow'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(settings, field, data[field])
        
        db.session.commit()
        
        return jsonify({'message': '구매 관리 설정이 업데이트되었습니다.'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"구매 설정 업데이트 오류: {str(e)}")
        return jsonify({'error': '구매 설정 업데이트 중 오류가 발생했습니다.'}), 500 