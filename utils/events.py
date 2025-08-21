from extensions import socketio
from datetime import datetime
import json
from typing import Dict, Any, Optional, Union

def emit_event(
    name: str, 
    payload: Dict[str, Any], 
    room: Optional[str] = None, 
    version: int = 1,
    include_timestamp: bool = True
) -> Dict[str, Any]:
    """
    Socket.IO 이벤트를 일원화하여 송출
    
    Args:
        name: 이벤트 이름 (예: 'attendance:update')
        payload: 이벤트 데이터
        room: 특정 룸으로 전송 (None이면 모든 클라이언트)
        version: 이벤트 버전
        include_timestamp: 서버 타임스탬프 포함 여부
    
    Returns:
        전송된 데이터 (디버깅용)
    """
    try:
        # 이벤트 데이터 구성
        event_data = {
            "v": version,  # 버전 정보
            **payload
        }
        
        # 서버 타임스탬프 추가
        if include_timestamp:
            event_data["server_timestamp"] = datetime.utcnow().isoformat()
        
        # 이벤트 송출
        if room:
            # 특정 룸으로 전송
            socketio.emit(name, event_data, room=room)
        else:
            # 모든 클라이언트로 브로드캐스트
            socketio.emit(name, event_data, room=None)
        
        # 로깅 (개발용)
        print(f"📡 이벤트 송출: {name} -> {room or 'broadcast'}")
        print(f"   데이터: {json.dumps(event_data, indent=2, ensure_ascii=False)}")
        
        return event_data
        
    except Exception as e:
        print(f"❌ 이벤트 송출 실패: {name} - {str(e)}")
        raise

def emit_attendance_update(attendance_data: Dict[str, Any], branch_id: Optional[str] = None):
    """출퇴근 업데이트 이벤트"""
    room = f"branch:{branch_id}" if branch_id else None
    return emit_event("attendance:update", attendance_data, room=room)

def emit_inventory_update(inventory_data: Dict[str, Any], branch_id: Optional[str] = None):
    """재고 업데이트 이벤트"""
    room = f"branch:{branch_id}" if branch_id else None
    return emit_event("inventory:update", inventory_data, room=room)

def emit_purchase_order_update(order_data: Dict[str, Any], branch_id: Optional[str] = None):
    """발주 업데이트 이벤트"""
    room = f"branch:{branch_id}" if branch_id else None
    return emit_event("purchase_order:update", order_data, room=room)

def emit_schedule_update(schedule_data: Dict[str, Any], branch_id: Optional[str] = None):
    """스케줄 업데이트 이벤트"""
    room = f"branch:{branch_id}" if branch_id else None
    return emit_event("schedule:update", schedule_data, room=room)

def emit_order_update(order_data: Dict[str, Any], branch_id: Optional[str] = None):
    """주문 업데이트 이벤트"""
    room = f"branch:{branch_id}" if branch_id else None
    return emit_event("order:update", order_data, room=room)

def emit_notification(
    notification_data: Dict[str, Any], 
    user_id: Optional[int] = None,
    role: Optional[str] = None,
    branch_id: Optional[str] = None
):
    """알림 이벤트 (사용자별/역할별/지점별)"""
    rooms = []
    
    if user_id:
        rooms.append(f"user:{user_id}")
    
    if role:
        rooms.append(f"role:{role}")
    
    if branch_id:
        rooms.append(f"branch:{branch_id}")
    
    # 여러 룸으로 전송
    for room in rooms:
        emit_event("notification", notification_data, room=room)
    
    # 룸이 없으면 모든 사용자에게 전송
    if not rooms:
        emit_event("notification", notification_data)

def emit_system_event(event_name: str, data: Dict[str, Any], admin_only: bool = True):
    """시스템 이벤트 (관리자용)"""
    room = "admin" if admin_only else None
    return emit_event(f"system:{event_name}", data, room=room)

def emit_error_event(error_data: Dict[str, Any], user_id: Optional[int] = None):
    """오류 이벤트"""
    room = f"user:{user_id}" if user_id else None
    return emit_event("error", error_data, room=room)

# 이벤트 타입별 헬퍼 함수들
EVENT_HELPERS = {
    "attendance": emit_attendance_update,
    "inventory": emit_inventory_update,
    "purchase_order": emit_purchase_order_update,
    "schedule": emit_schedule_update,
    "order": emit_order_update,
    "notification": emit_notification,
    "system": emit_system_event,
    "error": emit_error_event
}

def emit_by_type(event_type: str, data: Dict[str, Any], **kwargs):
    """이벤트 타입에 따라 적절한 헬퍼 함수 호출"""
    if event_type in EVENT_HELPERS:
        return EVENT_HELPERS[event_type](data, **kwargs)
    else:
        # 기본 이벤트 송출
        return emit_event(event_type, data, **kwargs)
