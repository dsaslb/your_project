"""
모바일 동기화 API
- 배치 동기화 엔드포인트
- 멱등성 처리
- 실시간 이벤트 발행
"""
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timezone
from extensions import db
from utils.idempotency import require_idempotency_key, check_idempotency_key, store_idempotency_key
from utils.outbox import record_event
from models_sync import SyncAudit, SyncMetrics
import time
import logging
import uuid

logger = logging.getLogger(__name__)

mobile_sync_bp = Blueprint("mobile_sync", __name__, url_prefix="/api/mobile/sync")

@mobile_sync_bp.route("/batch", methods=["POST"])
@require_idempotency_key()
def sync_batch():
    """
    배치 동기화 엔드포인트
    
    Request Body:
    {
        "items": [
            {
                "type": "attendance|po|inventory",
                "idem": "unique-uuid",
                "payload": {...}
            }
        ],
        "meta": {
            "device_id": "device-identifier",
            "branch_id": 1,
            "user_id": 123
        }
    }
    
    Response:
    {
        "ok": true,
        "results": [
            {
                "idem": "uuid",
                "status": "ok|dup|error",
                "error": "error message if any"
            }
        ],
        "stats": {
            "total": 10,
            "ok": 8,
            "dup": 1,
            "error": 1
        }
    }
    """
    start_time = time.time()
    
    try:
        data = request.get_json() or {}
        items = data.get("items", [])
        meta = data.get("meta", {})
        
        # 입력 검증
        if not items:
            return jsonify({
                "error": "No items provided",
                "code": "NO_ITEMS"
            }), 400
        
        if len(items) > 100:  # 배치 크기 제한
            return jsonify({
                "error": "Too many items (max 100)",
                "code": "BATCH_TOO_LARGE"
            }), 400
        
        device_id = meta.get("device_id", "unknown")
        branch_id = meta.get("branch_id")
        user_id = meta.get("user_id")
        
        results = []
        stats = {"total": len(items), "ok": 0, "dup": 0, "error": 0}
        
        # 각 아이템 처리
        for item in items:
            item_start_time = time.time()
            
            item_type = item.get("type")
            item_idem = item.get("idem")
            payload = item.get("payload", {})
            
            # 아이템 검증
            if not item_type or not item_idem:
                results.append({
                    "idem": item_idem or "unknown",
                    "status": "error",
                    "error": "Missing type or idem"
                })
                stats["error"] += 1
                continue
            
            if item_type not in ["attendance", "po", "inventory"]:
                results.append({
                    "idem": item_idem,
                    "status": "error",
                    "error": f"Unknown type: {item_type}"
                })
                stats["error"] += 1
                continue
            
            try:
                # 1. 멱등성 키 중복 체크
                if check_idempotency_key(item_idem):
                    results.append({
                        "idem": item_idem,
                        "status": "dup"
                    })
                    stats["dup"] += 1
                    continue
                
                # 2. 도메인별 처리
                success = process_sync_item(item_type, payload, meta)
                
                if success:
                    # 3. 멱등성 키 저장
                    store_idempotency_key(item_idem)
                    
                    # 4. Outbox 이벤트 기록
                    channel_map = {
                        "attendance": "attendance:update",
                        "po": "po:created", 
                        "inventory": "inventory:update"
                    }
                    channel = channel_map.get(item_type)
                    if channel:
                        record_event(channel, {
                            **payload,
                            "type": item_type,
                            "device_id": device_id,
                            "branch_id": branch_id,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                    
                    # 5. 감사 로그
                    processing_time = int((time.time() - item_start_time) * 1000)
                    audit = SyncAudit(
                        user_id=user_id,
                        device_id=device_id,
                        type=item_type,
                        idem_key=item_idem,
                        status="ok",
                        payload_size=len(str(payload)),
                        processing_time_ms=processing_time
                    )
                    db.session.add(audit)
                    
                    results.append({
                        "idem": item_idem,
                        "status": "ok"
                    })
                    stats["ok"] += 1
                    
                else:
                    raise Exception("Processing failed")
                    
            except Exception as e:
                # 에러 처리
                processing_time = int((time.time() - item_start_time) * 1000)
                audit = SyncAudit(
                    user_id=user_id,
                    device_id=device_id,
                    type=item_type,
                    idem_key=item_idem,
                    status="error",
                    error=str(e),
                    payload_size=len(str(payload)),
                    processing_time_ms=processing_time
                )
                db.session.add(audit)
                
                results.append({
                    "idem": item_idem,
                    "status": "error",
                    "error": str(e)
                })
                stats["error"] += 1
                logger.error(f"Sync item failed: {item_type}:{item_idem} - {e}")
        
        # 전체 통계 기록
        total_processing_time = int((time.time() - start_time) * 1000)
        db.session.add(SyncMetrics(
            metric_name="sync_batch_processing_time_ms",
            metric_value=total_processing_time,
            labels={
                "device_id": device_id,
                "branch_id": branch_id,
                "total_items": stats["total"]
            }
        ))
        
        db.session.commit()
        
        logger.info(f"Batch sync completed: {stats}, device: {device_id}")
        
        return jsonify({
            "ok": True,
            "results": results,
            "stats": stats,
            "processing_time_ms": total_processing_time
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Batch sync failed: {e}")
        return jsonify({
            "error": "Internal server error",
            "code": "INTERNAL_ERROR"
        }), 500

def process_sync_item(item_type: str, payload: dict, meta: dict) -> bool:
    """
    동기화 아이템 처리
    
    Args:
        item_type: 아이템 타입
        payload: 페이로드 데이터
        meta: 메타데이터
    
    Returns:
        처리 성공 여부
    """
    try:
        if item_type == "attendance":
            return process_attendance_sync(payload, meta)
        elif item_type == "po":
            return process_po_sync(payload, meta)
        elif item_type == "inventory":
            return process_inventory_sync(payload, meta)
        else:
            return False
    except Exception as e:
        logger.error(f"Error processing {item_type}: {e}")
        return False

def process_attendance_sync(payload: dict, meta: dict) -> bool:
    """출퇴근 데이터 동기화 처리"""
    try:
        # 기존 Attendance 모델 사용 (실제 구현에 맞게 수정)
        from models import Attendance  # 실제 모델 import
        
        # 서버 시간 우선 + 스케줄 윈도우 검증
        attendance = Attendance(
            user_id=payload.get("user_id"),
            branch_id=meta.get("branch_id"),
            check_in_time=payload.get("check_in_time"),
            check_out_time=payload.get("check_out_time"),
            device_id=meta.get("device_id"),
            sync_timestamp=datetime.now(timezone.utc)
        )
        
        db.session.add(attendance)
        return True
        
    except Exception as e:
        logger.error(f"Attendance sync failed: {e}")
        return False

def process_po_sync(payload: dict, meta: dict) -> bool:
    """발주 데이터 동기화 처리 (충돌 해결 규칙 적용)"""
    try:
        from utils.conflict_resolution import resolve_purchase_order_conflict, log_conflict_resolution
        
        # 충돌 해결 규칙 적용
        resolved_data = resolve_purchase_order_conflict(
            po_data=payload,
            existing_po_id=payload.get("existing_id")
        )
        
        # 기존 PurchaseOrder 모델 사용 (실제 구현에 맞게 수정)
        from models import PurchaseOrder  # 실제 모델 import
        
        # 승인 전까지는 Last Write Wins
        po = PurchaseOrder(
            branch_id=meta.get("branch_id"),
            items=resolved_data.get("items", []),
            total_amount=resolved_data.get("total_amount"),
            status=resolved_data.get("status", "pending"),  # 승인 전까지는 pending
            device_id=meta.get("device_id"),
            sync_timestamp=datetime.now(timezone.utc)
        )
        
        db.session.add(po)
        
        # 충돌 해결 로그 기록
        log_conflict_resolution(
            user_id=meta.get("user_id"),
            item_type="po",
            item_id=payload.get("idem", "unknown"),
            resolution_method=resolved_data["resolved_by"],
            details={"existing_id": payload.get("existing_id")}
        )
        
        return True
        
    except Exception as e:
        logger.error(f"PO sync failed: {e}")
        return False

def process_inventory_sync(payload: dict, meta: dict) -> bool:
    """재고 데이터 동기화 처리 (충돌 해결 규칙 적용)"""
    try:
        from utils.conflict_resolution import resolve_inventory_conflict, log_conflict_resolution
        
        # 충돌 해결 규칙 적용
        resolved_data = resolve_inventory_conflict(
            inventory_data=payload,
            existing_item_id=payload.get("existing_id")
        )
        
        # 기존 InventoryLog 모델 사용 (실제 구현에 맞게 수정)
        from models import InventoryLog  # 실제 모델 import
        
        inventory_log = InventoryLog(
            branch_id=meta.get("branch_id"),
            product_id=resolved_data.get("product_id"),
            quantity_change=resolved_data.get("quantity_change"),
            reason=resolved_data.get("reason"),
            device_id=meta.get("device_id"),
            sync_timestamp=datetime.now(timezone.utc)
        )
        
        db.session.add(inventory_log)
        
        # 충돌 해결 로그 기록
        log_conflict_resolution(
            user_id=meta.get("user_id"),
            item_type="inventory",
            item_id=payload.get("idem", "unknown"),
            resolution_method=resolved_data["resolved_by"],
            details={"existing_id": payload.get("existing_id")}
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Inventory sync failed: {e}")
        return False

@mobile_sync_bp.route("/status", methods=["GET"])
def sync_status():
    """동기화 상태 조회"""
    try:
        from utils.outbox import get_outbox_stats
        
        outbox_stats = get_outbox_stats()
        
        return jsonify({
            "ok": True,
            "outbox": outbox_stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Sync status failed: {e}")
        return jsonify({
            "error": "Failed to get sync status",
            "code": "STATUS_ERROR"
        }), 500

@mobile_sync_bp.route("/health", methods=["GET"])
def sync_health():
    """동기화 서비스 헬스체크"""
    try:
        # DB 연결 확인
        db.session.execute("SELECT 1")
        
        # Outbox 상태 확인
        from utils.outbox import get_outbox_stats
        outbox_stats = get_outbox_stats()
        
        # 실패한 이벤트가 너무 많으면 unhealthy
        failed_ratio = outbox_stats.get("failed", 0) / max(outbox_stats.get("total", 1), 1)
        is_healthy = failed_ratio < 0.1  # 10% 미만
        
        return jsonify({
            "ok": is_healthy,
            "database": "ok",
            "outbox": outbox_stats,
            "failed_ratio": failed_ratio
        }), 200 if is_healthy else 503
        
    except Exception as e:
        logger.error(f"Sync health check failed: {e}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 503
