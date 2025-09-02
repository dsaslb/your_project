#!/usr/bin/env python3
"""
모바일 발주 API - 멱등성 키 검증 및 실시간 이벤트 송출
"""

from flask import Blueprint, request, jsonify, current_app
from extensions import db, csrf
from models import PurchaseOrder, User, Branch, Brand, Industry
from utils.idempotency import require_idempotency_key
from utils.events import emit_branch_event, EventNames
from utils.auth import auth_required
import logging

logger = logging.getLogger(__name__)

mobile_po_bp = Blueprint('mobile_purchase_orders', __name__, url_prefix='/api/mobile')


@mobile_po_bp.route('/purchase_orders', methods=['POST'])
@csrf.exempt  # CSRF 보호 면제
@auth_required
@require_idempotency_key()
def create_purchase_order():
    """
    모바일에서 발주 생성 (테스트용 간소화 버전)
    
    요청 형식:
    {
        "branch_id": 123,
        "items": [
            {"barcode": "123456789", "name": "상품명", "qty": 5}
        ],
        "notes": "비고사항"
    }
    
    헤더: X-Idempotency-Key: <uuid>
    """
    try:
        data = request.get_json() or {}
        
        # 필수 필드 검증
        branch_id = data.get('branch_id')
        items = data.get('items', [])
        
        if not branch_id:
            return jsonify({
                "error": "Missing branch_id",
                "message": "지점 ID가 필요합니다."
            }), 400
        
        if not items or not isinstance(items, list):
            return jsonify({
                "error": "Invalid items",
                "message": "상품 목록이 필요합니다."
            }), 400
        
        # 테스트용 더미 발주 ID 생성
        import uuid
        test_po_id = str(uuid.uuid4())[:8]
        
        current_app.logger.info(f"테스트 발주 생성 성공: ID={test_po_id}, branch_id={branch_id}, items_count={len(items)}")
        
        # 실시간 이벤트 송출 (테스트용)
        try:
            event_payload = {
                "id": test_po_id,
                "branch_id": branch_id,
                "brand_id": 1,  # 테스트용
                "industry_id": 1,  # 테스트용
                "status": "requested",
                "user_id": getattr(request, 'user_id', 1),
                "items_count": len(items),
                "created_at": None
            }
            
            emit_branch_event(EventNames.PO_CREATED, event_payload, branch_id)
            current_app.logger.info(f"실시간 이벤트 송출 성공: {EventNames.PO_CREATED}")
            
        except Exception as event_error:
            current_app.logger.warning(f"실시간 이벤트 송출 실패: {event_error}")
        
        return jsonify({
            "ok": True,
            "id": test_po_id,
            "message": "발주가 성공적으로 생성되었습니다.",
            "test_mode": True
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"발주 생성 중 오류: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": f"발주 생성 중 오류가 발생했습니다: {str(e)}"
        }), 500


@mobile_po_bp.route('/purchase_orders/<int:po_id>', methods=['GET'])
@csrf.exempt  # CSRF 보호 면제
@auth_required
def get_purchase_order(po_id):
    """특정 발주 조회"""
    try:
        purchase_order = PurchaseOrder.query.get_or_404(po_id)
        
        # 권한 확인 (같은 지점 사용자만)
        if purchase_order.branch_id != request.user.branch_id:
            return jsonify({
                "error": "Access denied",
                "message": "해당 발주에 접근할 권한이 없습니다."
            }), 403
        
        return jsonify({
            "ok": True,
            "purchase_order": purchase_order.to_dict()
        })
        
    except Exception as e:
        logger.error(f"발주 조회 실패: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": "발주 조회 중 오류가 발생했습니다."
        }), 500


@mobile_po_bp.route('/purchase_orders', methods=['GET'])
@csrf.exempt  # CSRF 보호 면제
@auth_required
def list_purchase_orders():
    """사용자의 발주 목록 조회"""
    try:
        user_id = request.user_id
        branch_id = request.args.get('branch_id', type=int)
        status = request.args.get('status')
        
        # 쿼리 구성
        query = PurchaseOrder.query.filter_by(user_id=user_id)
        
        if branch_id:
            query = query.filter_by(branch_id=branch_id)
        
        if status:
            query = query.filter_by(status=status)
        
        # 최신순 정렬
        purchase_orders = query.order_by(PurchaseOrder.created_at.desc()).all()
        
        return jsonify({
            "ok": True,
            "purchase_orders": [po.to_dict() for po in purchase_orders],
            "total": len(purchase_orders)
        })
        
    except Exception as e:
        logger.error(f"발주 목록 조회 실패: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": "발주 목록 조회 중 오류가 발생했습니다."
        }), 500
