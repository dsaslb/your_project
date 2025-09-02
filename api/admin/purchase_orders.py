#!/usr/bin/env python3
"""
관리자 발주 관리 API - 상태 변경 및 실시간 이벤트 송출
"""

from flask import Blueprint, request, jsonify, current_app
from extensions import db, csrf
from models import PurchaseOrder, User, Branch, Brand, Industry
from utils.events import emit_branch_event, EventNames
from utils.auth import admin_required
import logging

logger = logging.getLogger(__name__)

admin_po_bp = Blueprint('admin_purchase_orders', __name__, url_prefix='/api/admin')


@admin_po_bp.route('/purchase_orders/<int:po_id>/status', methods=['PUT'])
@csrf.exempt  # CSRF 보호 면제
@admin_required
def update_purchase_order_status(po_id):
    """
    발주 상태 변경 (테스트용 간소화 버전)
    
    요청 형식:
    {
        "status": "approved|rejected|processing|completed",
        "notes": "상태 변경 사유"
    }
    """
    try:
        data = request.get_json() or {}
        new_status = data.get('status')
        notes = data.get('notes', '')
        
        if not new_status:
            return jsonify({
                "error": "Missing status",
                "message": "새로운 상태가 필요합니다."
            }), 400
        
        # 유효한 상태값 검증
        valid_statuses = ['requested', 'approved', 'rejected', 'processing', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            return jsonify({
                "error": "Invalid status",
                "message": f"유효하지 않은 상태입니다. 허용된 값: {', '.join(valid_statuses)}"
            }), 400
        
        current_app.logger.info(f"테스트 발주 상태 변경: ID={po_id}, status={new_status}, notes={notes}")
        
        # 실시간 이벤트 송출 (테스트용)
        try:
            event_payload = {
                "id": po_id,
                "branch_id": 1,  # 테스트용
                "brand_id": 1,  # 테스트용
                "industry_id": 1,  # 테스트용
                "old_status": "requested",  # 테스트용
                "new_status": new_status,
                "user_id": 1,  # 테스트용
                "updated_by": getattr(request, 'user_id', 1),
                "notes": notes,
                "updated_at": None
            }
            
            emit_branch_event(EventNames.PO_STATUS, event_payload, 1)
            current_app.logger.info(f"실시간 이벤트 송출 성공: {EventNames.PO_STATUS}")
            
        except Exception as event_error:
            current_app.logger.warning(f"실시간 이벤트 송출 실패: {event_error}")
        
        return jsonify({
            "ok": True,
            "message": f"발주 상태가 '{new_status}'로 변경되었습니다.",
            "test_mode": True,
            "purchase_order": {
                "id": po_id,
                "status": new_status,
                "updated_at": None
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"발주 상태 변경 중 오류: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": f"발주 상태 변경 중 오류가 발생했습니다: {str(e)}"
        }), 500


@admin_po_bp.route('/purchase_orders', methods=['GET'])
@csrf.exempt  # CSRF 보호 면제
@admin_required
def list_purchase_orders():
    """발주 목록 조회 (관리자용)"""
    try:
        # 쿼리 파라미터
        branch_id = request.args.get('branch_id', type=int)
        brand_id = request.args.get('brand_id', type=int)
        status = request.args.get('status')
        count_only = request.args.get('countOnly', 'false').lower() == 'true'
        
        # 권한 확인
        current_user = User.query.get(request.user_id)
        if not current_user:
            return jsonify({
                "error": "User not found",
                "message": "사용자 정보를 찾을 수 없습니다."
            }), 404
        
        # 쿼리 구성
        query = PurchaseOrder.query
        
        # 브랜드 스코프 제한
        if current_user.role != 'super_admin':
            query = query.filter_by(brand_id=current_user.brand_id)
        
        if branch_id:
            query = query.filter_by(branch_id=branch_id)
        
        if brand_id:
            query = query.filter_by(brand_id=brand_id)
        
        if status:
            query = query.filter_by(status=status)
        
        if count_only:
            # 카운트만 반환 (사이드바 배지용)
            count = query.count()
            return jsonify({
                "ok": True,
                "count": count
            })
        
        # 전체 목록 반환
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


@admin_po_bp.route('/purchase_orders/<int:po_id>', methods=['GET'])
@csrf.exempt  # CSRF 보호 면제
@admin_required
def get_purchase_order(po_id):
    """특정 발주 상세 조회 (관리자용)"""
    try:
        purchase_order = PurchaseOrder.query.get_or_404(po_id)
        
        # 권한 확인
        current_user = User.query.get(request.user_id)
        if not current_user or current_user.brand_id != purchase_order.brand_id:
            return jsonify({
                "error": "Access denied",
                "message": "해당 발주에 접근할 권한이 없습니다."
            }), 403
        
        return jsonify({
            "ok": True,
            "purchase_order": purchase_order.to_dict()
        })
        
    except Exception as e:
        logger.error(f"발주 상세 조회 실패: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": "발주 상세 조회 중 오류가 발생했습니다."
        }), 500


@admin_po_bp.route('/purchase_orders/count', methods=['GET'])
@csrf.exempt
@admin_required
def get_purchase_order_count():
    """발주 카운트 조회 (테스트용)"""
    try:
        status = request.args.get('status', 'requested')
        count_only = request.args.get('countOnly', '0') == '1'
        
        # 테스트용 더미 카운트 반환
        test_count = 3  # 테스트용 고정 값
        
        current_app.logger.info(f"발주 카운트 조회: status={status}, count_only={count_only}")
        
        if count_only:
            return jsonify({
                "count": test_count,
                "status": status,
                "test_mode": True
            })
        else:
            return jsonify({
                "count": test_count,
                "status": status,
                "test_mode": True,
                "message": "테스트 모드: 더미 데이터"
            })
            
    except Exception as e:
        current_app.logger.error(f"발주 카운트 조회 중 오류: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": f"발주 카운트 조회 중 오류가 발생했습니다: {str(e)}"
        }), 500
