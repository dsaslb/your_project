#!/usr/bin/env python3
"""
공통 이벤트 헬퍼 - Socket.IO 이벤트 표준화
모든 이벤트 payload에 권한 스코프를 위한 industry_id, brand_id, branch_id 포함
"""

from extensions import socketio
from datetime import datetime
from typing import Optional, Dict, Any


def emit_event(name: str, payload: dict, *, room: Optional[str] = None, v: int = 1):
    """
    표준화된 이벤트 송출
    
    Args:
        name: 이벤트 이름 (예: po:created, attendance:update)
        payload: 이벤트 데이터
        room: 특정 룸으로 송출 (예: branch:123)
        v: 이벤트 버전 (기본값: 1)
    """
    # 표준 필드 추가
    data = {
        "v": v,
        "ts": datetime.utcnow().isoformat(),  # 서버 시간
        **payload
    }
    
    # 권한 스코프 필드 검증
    required_fields = ["industry_id", "brand_id", "branch_id"]
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        raise ValueError(f"이벤트 payload에 필수 필드가 누락되었습니다: {missing_fields}")
    
    # 이벤트 송출
    if room:
        socketio.emit(name, data, room=room)
    else:
        socketio.emit(name, data, broadcast=True)
    
    return data


def emit_branch_event(name: str, payload: dict, branch_id: int):
    """특정 지점으로 이벤트 송출"""
    return emit_event(name, payload, room=f"branch:{branch_id}")


def emit_brand_event(name: str, payload: dict, brand_id: int):
    """특정 브랜드로 이벤트 송출"""
    return emit_event(name, payload, room=f"brand:{brand_id}")


def emit_industry_event(name: str, payload: dict, industry_id: int):
    """특정 업종으로 이벤트 송출"""
    return emit_event(name, payload, room=f"industry:{industry_id}")


# 표준 이벤트 이름 상수
class EventNames:
    # 출퇴근 관련
    ATTENDANCE_UPDATE = "attendance:update"
    
    # 재고 관련
    INVENTORY_UPDATE = "inventory:update"
    
    # 발주 관련
    PO_CREATED = "po:created"
    PO_STATUS = "po:status"
    
    # 스케줄 관련
    SCHEDULE_UPDATE = "schedule:update"
    
    # 주문 관련
    ORDER_UPDATE = "order:update"
