"""
충돌 해결 규칙 유틸리티
- 출퇴근: 서버시간 우선 + 스케줄 윈도우
- 발주/재고: 승인 전까지는 Last Write Wins, 승인 후엔 관리자만 변경
"""
from datetime import datetime, timezone, timedelta
from extensions import db
from models_sync import SyncAudit
import logging

logger = logging.getLogger(__name__)

class ConflictResolutionError(Exception):
    """충돌 해결 중 발생한 오류"""
    pass

def resolve_attendance_conflict(user_id: int, attendance_type: str, client_timestamp: str, 
                               lat: float = None, lng: float = None) -> dict:
    """
    출퇴근 충돌 해결: 서버시간 우선 + 스케줄 윈도우 검증
    
    Args:
        user_id: 사용자 ID
        attendance_type: 'in' 또는 'out'
        client_timestamp: 클라이언트에서 보낸 시간
        lat, lng: 위치 정보
    
    Returns:
        해결된 출퇴근 데이터
    """
    try:
        # 서버 시간 사용 (클라이언트 시간 무시)
        server_time = datetime.now(timezone.utc)
        
        # 스케줄 윈도우 검증 (예: 출근은 06:00-10:00, 퇴근은 17:00-23:00)
        current_hour = server_time.hour
        
        if attendance_type == 'in':
            if not (6 <= current_hour <= 10):
                raise ConflictResolutionError(f"출근 시간이 아닙니다 (현재: {current_hour}시)")
        elif attendance_type == 'out':
            if not (17 <= current_hour <= 23):
                raise ConflictResolutionError(f"퇴근 시간이 아닙니다 (현재: {current_hour}시)")
        
        # 중복 출퇴근 체크 (같은 날 같은 타입)
        today = server_time.date()
        from models import Attendance  # 실제 모델 import 필요
        
        existing = Attendance.query.filter_by(
            user_id=user_id,
            type=attendance_type
        ).filter(
            db.func.date(Attendance.at) == today
        ).first()
        
        if existing:
            raise ConflictResolutionError(f"오늘 이미 {attendance_type} 처리되었습니다")
        
        return {
            'user_id': user_id,
            'type': attendance_type,
            'at': server_time,
            'lat': lat,
            'lng': lng,
            'resolved_by': 'server_time_priority',
            'client_timestamp': client_timestamp
        }
        
    except Exception as e:
        logger.error(f"출퇴근 충돌 해결 실패: {e}")
        raise ConflictResolutionError(str(e))

def resolve_purchase_order_conflict(po_data: dict, existing_po_id: int = None) -> dict:
    """
    발주 충돌 해결: 승인 전까지는 Last Write Wins, 승인 후엔 관리자만 변경
    
    Args:
        po_data: 발주 데이터
        existing_po_id: 기존 발주 ID (있는 경우)
    
    Returns:
        해결된 발주 데이터
    """
    try:
        if existing_po_id:
            from models import PurchaseOrder  # 실제 모델 import 필요
            
            existing_po = PurchaseOrder.query.get(existing_po_id)
            if not existing_po:
                raise ConflictResolutionError("기존 발주를 찾을 수 없습니다")
            
            # 승인된 발주는 관리자만 수정 가능
            if existing_po.status in ['approved', 'completed']:
                raise ConflictResolutionError("승인된 발주는 수정할 수 없습니다")
            
            # 승인 전 발주는 Last Write Wins
            logger.info(f"발주 {existing_po_id} 업데이트 (Last Write Wins)")
            
            return {
                **po_data,
                'id': existing_po_id,
                'resolved_by': 'last_write_wins',
                'updated_at': datetime.now(timezone.utc)
            }
        else:
            # 새 발주 생성
            return {
                **po_data,
                'status': 'requested',
                'resolved_by': 'new_creation',
                'created_at': datetime.now(timezone.utc)
            }
            
    except Exception as e:
        logger.error(f"발주 충돌 해결 실패: {e}")
        raise ConflictResolutionError(str(e))

def resolve_inventory_conflict(inventory_data: dict, existing_item_id: int = None) -> dict:
    """
    재고 충돌 해결: 승인 전까지는 Last Write Wins, 승인 후엔 관리자만 변경
    
    Args:
        inventory_data: 재고 데이터
        existing_item_id: 기존 재고 항목 ID (있는 경우)
    
    Returns:
        해결된 재고 데이터
    """
    try:
        if existing_item_id:
            from models import InventoryLog  # 실제 모델 import 필요
            
            existing_item = InventoryLog.query.get(existing_item_id)
            if not existing_item:
                raise ConflictResolutionError("기존 재고 항목을 찾을 수 없습니다")
            
            # 승인된 재고는 관리자만 수정 가능
            if existing_item.status in ['approved', 'completed']:
                raise ConflictResolutionError("승인된 재고는 수정할 수 없습니다")
            
            # 승인 전 재고는 Last Write Wins
            logger.info(f"재고 {existing_item_id} 업데이트 (Last Write Wins)")
            
            return {
                **inventory_data,
                'id': existing_item_id,
                'resolved_by': 'last_write_wins',
                'updated_at': datetime.now(timezone.utc)
            }
        else:
            # 새 재고 항목 생성
            return {
                **inventory_data,
                'status': 'pending',
                'resolved_by': 'new_creation',
                'created_at': datetime.now(timezone.utc)
            }
            
    except Exception as e:
        logger.error(f"재고 충돌 해결 실패: {e}")
        raise ConflictResolutionError(str(e))

def log_conflict_resolution(user_id: int, item_type: str, item_id: str, 
                           resolution_method: str, details: dict = None):
    """
    충돌 해결 로그 기록
    
    Args:
        user_id: 사용자 ID
        item_type: 항목 타입 ('attendance', 'po', 'inventory')
        item_id: 항목 ID
        resolution_method: 해결 방법
        details: 추가 세부사항
    """
    try:
        audit = SyncAudit(
            user_id=user_id,
            type=item_type,
            idem_key=item_id,
            status='conflict_resolved',
            error=f"Resolved by: {resolution_method}",
            details=details or {}
        )
        
        db.session.add(audit)
        db.session.commit()
        
        logger.info(f"충돌 해결 로그 기록: {item_type} {item_id} - {resolution_method}")
        
    except Exception as e:
        logger.error(f"충돌 해결 로그 기록 실패: {e}")
        db.session.rollback()

def validate_schedule_window(user_id: int, attendance_type: str) -> bool:
    """
    스케줄 윈도우 검증
    
    Args:
        user_id: 사용자 ID
        attendance_type: 출퇴근 타입
    
    Returns:
        스케줄 윈도우 내 여부
    """
    try:
        # 실제 구현에서는 사용자의 스케줄을 DB에서 조회
        # 여기서는 간단한 시간 윈도우만 검증
        current_hour = datetime.now(timezone.utc).hour
        
        if attendance_type == 'in':
            return 6 <= current_hour <= 10
        elif attendance_type == 'out':
            return 17 <= current_hour <= 23
        
        return False
        
    except Exception as e:
        logger.error(f"스케줄 윈도우 검증 실패: {e}")
        return False
