"""
재고관리 플러그인 API 라우트
"""

from datetime import datetime
from flask import request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import and_, func
from extensions import db
from models_main import InventoryProduct as Product, InventoryTransaction, InventorySettings
from plugins.inventory_management import inventory_bp

@inventory_bp.route('/products', methods=['GET'])
@login_required
def get_products():
    """상품 목록 조회"""
    try:
        store_id = request.args.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        category = request.args.get('category')
        low_stock_only = request.args.get('low_stock_only', 'false').lower() == 'true'
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        query = Product.query.filter_by(store_id=store_id, is_active=True)
        
        if category:
            query = query.filter_by(category=category)
        
        if low_stock_only:
            query = query.filter(Product.current_stock <= Product.min_stock)
        
        products = query.order_by(Product.name).all()
        
        product_list = []
        for product in products:
            product_list.append({
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'description': product.description,
                'category': product.category,
                'unit': product.unit,
                'cost_price': product.cost_price,
                'selling_price': product.selling_price,
                'current_stock': product.current_stock,
                'min_stock': product.min_stock,
                'max_stock': product.max_stock,
                'supplier': product.supplier,
                'location': product.location,
                'is_low_stock': product.is_low_stock(),
                'total_value': product.current_stock * product.cost_price
            })
        
        return jsonify({
            'products': product_list,
            'total_count': len(product_list)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"상품 목록 조회 오류: {str(e)}")
        return jsonify({'error': '상품 목록 조회 중 오류가 발생했습니다.'}), 500

@inventory_bp.route('/products', methods=['POST'])
@login_required
def create_product():
    """상품 생성"""
    try:
        data = request.get_json()
        store_id = data.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        # 필수 필드 검증
        required_fields = ['name', 'sku']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} 필드가 필요합니다.'}), 400
        
        # SKU 중복 확인
        existing_product = Product.query.filter_by(sku=data['sku']).first()
        if existing_product:
            return jsonify({'error': '이미 존재하는 SKU입니다.'}), 400
        
        # 상품 생성
        product = Product(
            store_id=store_id,
            name=data['name'],
            sku=data['sku'],
            description=data.get('description'),
            category=data.get('category'),
            unit=data.get('unit', '개'),
            cost_price=data.get('cost_price', 0.0),
            selling_price=data.get('selling_price', 0.0),
            current_stock=data.get('current_stock', 0),
            min_stock=data.get('min_stock', 0),
            max_stock=data.get('max_stock', 1000),
            supplier=data.get('supplier'),
            location=data.get('location')
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'message': '상품이 생성되었습니다.',
            'product_id': product.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"상품 생성 오류: {str(e)}")
        return jsonify({'error': '상품 생성 중 오류가 발생했습니다.'}), 500

@inventory_bp.route('/products/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    """상품 정보 업데이트"""
    try:
        data = request.get_json()
        product = Product.query.get_or_404(product_id)
        
        # 업데이트 가능한 필드들
        updatable_fields = [
            'name', 'description', 'category', 'unit', 'cost_price', 
            'selling_price', 'min_stock', 'max_stock', 'supplier', 'location'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(product, field, data[field])
        
        db.session.commit()
        
        return jsonify({'message': '상품 정보가 업데이트되었습니다.'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"상품 업데이트 오류: {str(e)}")
        return jsonify({'error': '상품 업데이트 중 오류가 발생했습니다.'}), 500

@inventory_bp.route('/transactions', methods=['POST'])
@login_required
def create_transaction():
    """재고 거래 생성"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        transaction_type = data.get('transaction_type')
        quantity = data.get('quantity')
        
        if not all([product_id, transaction_type, quantity]):
            return jsonify({'error': 'product_id, transaction_type, quantity가 필요합니다.'}), 400
        
        # 상품 확인
        product = Product.query.get_or_404(product_id)
        
        # 거래 유형 검증
        try:
            transaction_type_enum = TransactionType(transaction_type)
        except ValueError:
            return jsonify({'error': '유효하지 않은 거래 유형입니다.'}), 400
        
        # 출고 시 재고 확인
        if transaction_type_enum in [TransactionType.OUT, TransactionType.DAMAGE]:
            if product.current_stock < quantity:
                return jsonify({'error': '재고가 부족합니다.'}), 400
        
        # 거래 생성
        transaction = InventoryTransaction(
            product_id=product_id,
            user_id=current_user.id,
            transaction_type=transaction_type_enum,
            quantity=quantity,
            unit_price=data.get('unit_price', 0.0),
            reference_number=data.get('reference_number'),
            notes=data.get('notes'),
            transaction_date=datetime.now()
        )
        
        # 총 금액 계산
        transaction.calculate_total()
        
        # 재고 업데이트
        product.update_stock(quantity, transaction_type_enum)
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': '재고 거래가 생성되었습니다.',
            'transaction_id': transaction.id,
            'new_stock': product.current_stock
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"재고 거래 생성 오류: {str(e)}")
        return jsonify({'error': '재고 거래 생성 중 오류가 발생했습니다.'}), 500

@inventory_bp.route('/transactions', methods=['GET'])
@login_required
def get_transactions():
    """재고 거래 기록 조회"""
    try:
        store_id = request.args.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        product_id = request.args.get('product_id')
        transaction_type = request.args.get('transaction_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        # 상품 ID로 필터링
        if product_id:
            transactions = InventoryTransaction.query.join(Product).filter(
                and_(
                    Product.store_id == store_id,
                    InventoryTransaction.product_id == product_id
                )
            )
        else:
            transactions = InventoryTransaction.query.join(Product).filter(
                Product.store_id == store_id
            )
        
        # 거래 유형 필터링
        if transaction_type:
            transactions = transactions.filter(
                InventoryTransaction.transaction_type == TransactionType(transaction_type)
            )
        
        # 날짜 범위 필터링
        if start_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            transactions = transactions.filter(
                InventoryTransaction.transaction_date >= start_datetime
            )
        
        if end_date:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            transactions = transactions.filter(
                InventoryTransaction.transaction_date <= end_datetime
            )
        
        transactions = transactions.order_by(InventoryTransaction.transaction_date.desc()).all()
        
        transaction_list = []
        for transaction in transactions:
            transaction_list.append({
                'id': transaction.id,
                'product_name': transaction.product.name,
                'product_sku': transaction.product.sku,
                'transaction_type': transaction.transaction_type.value,
                'quantity': transaction.quantity,
                'unit_price': transaction.unit_price,
                'total_amount': transaction.total_amount,
                'reference_number': transaction.reference_number,
                'notes': transaction.notes,
                'transaction_date': transaction.transaction_date.isoformat(),
                'user_name': transaction.user.username
            })
        
        return jsonify({
            'transactions': transaction_list,
            'total_count': len(transaction_list)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"재고 거래 조회 오류: {str(e)}")
        return jsonify({'error': '재고 거래 조회 중 오류가 발생했습니다.'}), 500

@inventory_bp.route('/low-stock', methods=['GET'])
@login_required
def get_low_stock_products():
    """재고 부족 상품 조회"""
    try:
        store_id = request.args.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        # 재고 부족 상품 조회
        low_stock_products = Product.query.filter(
            and_(
                Product.store_id == store_id,
                Product.is_active == True,
                Product.current_stock <= Product.min_stock
            )
        ).all()
        
        product_list = []
        for product in low_stock_products:
            product_list.append({
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'current_stock': product.current_stock,
                'min_stock': product.min_stock,
                'supplier': product.supplier,
                'location': product.location
            })
        
        return jsonify({
            'low_stock_products': product_list,
            'total_count': len(product_list)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"재고 부족 상품 조회 오류: {str(e)}")
        return jsonify({'error': '재고 부족 상품 조회 중 오류가 발생했습니다.'}), 500

@inventory_bp.route('/settings', methods=['GET'])
@login_required
def get_inventory_settings():
    """재고 관리 설정 조회"""
    try:
        store_id = request.args.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        settings = InventorySettings.query.filter_by(store_id=store_id).first()
        
        if not settings:
            return jsonify({'error': '재고 관리 설정이 없습니다.'}), 404
        
        return jsonify({
            'low_stock_threshold': settings.low_stock_threshold,
            'auto_reorder_enabled': settings.auto_reorder_enabled,
            'reorder_quantity': settings.reorder_quantity,
            'stock_alert_email': settings.stock_alert_email,
            'stock_alert_sms': settings.stock_alert_sms,
            'alert_recipients': settings.alert_recipients
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"재고 설정 조회 오류: {str(e)}")
        return jsonify({'error': '재고 설정 조회 중 오류가 발생했습니다.'}), 500

@inventory_bp.route('/settings', methods=['PUT'])
@login_required
def update_inventory_settings():
    """재고 관리 설정 업데이트"""
    try:
        store_id = request.args.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        data = request.get_json()
        settings = InventorySettings.query.filter_by(store_id=store_id).first()
        
        if not settings:
            settings = InventorySettings(store_id=store_id)
            db.session.add(settings)
        
        # 설정 업데이트
        updatable_fields = [
            'low_stock_threshold', 'auto_reorder_enabled', 'reorder_quantity',
            'stock_alert_email', 'stock_alert_sms', 'alert_recipients'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(settings, field, data[field])
        
        db.session.commit()
        
        return jsonify({'message': '재고 관리 설정이 업데이트되었습니다.'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"재고 설정 업데이트 오류: {str(e)}")
        return jsonify({'error': '재고 설정 업데이트 중 오류가 발생했습니다.'}), 500 