"""
Outbox 패턴 유틸리티
- 이벤트 발행을 위한 Outbox 패턴 구현
- 안정적인 이벤트 전송 보장
"""
from extensions import db, socketio
from models_sync import OutboxEvent
from datetime import datetime, timezone
import logging
import json

logger = logging.getLogger(__name__)

def record_event(channel: str, payload: dict, max_retries: int = 3) -> int:
    """
    이벤트를 Outbox에 기록
    
    Args:
        channel: 이벤트 채널명 (예: 'attendance:update')
        payload: 이벤트 데이터
        max_retries: 최대 재시도 횟수
    
    Returns:
        생성된 이벤트 ID
    """
    try:
        # 페이로드 검증
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a dictionary")
        
        # 채널명 검증
        if not channel or not isinstance(channel, str):
            raise ValueError("Channel must be a non-empty string")
        
        # 이벤트 생성
        event = OutboxEvent(
            channel=channel,
            payload=payload,
            delivered=False,
            max_retries=max_retries,
            retry_count=0
        )
        
        db.session.add(event)
        db.session.commit()
        
        logger.info(f"Event recorded in outbox: {event.id} - {channel}")
        return event.id
        
    except Exception as e:
        logger.error(f"Failed to record event in outbox: {e}")
        db.session.rollback()
        raise

def deliver_pending_events(limit: int = 100, retry_failed: bool = True) -> dict:
    """
    대기 중인 이벤트들을 전송
    
    Args:
        limit: 한 번에 처리할 최대 이벤트 수
        retry_failed: 실패한 이벤트 재시도 여부
    
    Returns:
        처리 결과 통계
    """
    stats = {
        'processed': 0,
        'delivered': 0,
        'failed': 0,
        'skipped': 0
    }
    
    try:
        # 대기 중인 이벤트 조회
        query = OutboxEvent.query.filter_by(delivered=False)
        
        if retry_failed:
            # 재시도 가능한 이벤트들 포함
            query = query.filter(OutboxEvent.retry_count < OutboxEvent.max_retries)
        else:
            # 아직 재시도하지 않은 이벤트만
            query = query.filter_by(retry_count=0)
        
        events = query.order_by(OutboxEvent.id.asc()).limit(limit).all()
        
        for event in events:
            stats['processed'] += 1
            
            try:
                # SocketIO로 이벤트 전송
                socketio.emit(event.channel, event.payload, broadcast=True)
                
                # 성공 처리
                event.delivered = True
                event.delivered_at = datetime.now(timezone.utc)
                event.last_error = None
                
                stats['delivered'] += 1
                logger.debug(f"Event delivered: {event.id} - {event.channel}")
                
            except Exception as e:
                # 실패 처리
                event.retry_count += 1
                event.last_error = str(e)
                
                if event.retry_count >= event.max_retries:
                    logger.error(f"Event failed permanently: {event.id} - {e}")
                    stats['failed'] += 1
                else:
                    logger.warning(f"Event delivery failed, will retry: {event.id} - {e}")
                    stats['skipped'] += 1
        
        # 변경사항 커밋
        db.session.commit()
        
        if stats['processed'] > 0:
            logger.info(f"Outbox processing completed: {stats}")
        
        return stats
        
    except Exception as e:
        logger.error(f"Error in deliver_pending_events: {e}")
        db.session.rollback()
        raise

def get_outbox_stats() -> dict:
    """Outbox 상태 통계 조회"""
    try:
        total = OutboxEvent.query.count()
        pending = OutboxEvent.query.filter_by(delivered=False).count()
        delivered = OutboxEvent.query.filter_by(delivered=True).count()
        failed = OutboxEvent.query.filter(
            OutboxEvent.delivered == False,
            OutboxEvent.retry_count >= OutboxEvent.max_retries
        ).count()
        
        return {
            'total': total,
            'pending': pending,
            'delivered': delivered,
            'failed': failed,
            'delivery_rate': (delivered / total * 100) if total > 0 else 0
        }
    except Exception as e:
        logger.error(f"Error getting outbox stats: {e}")
        return {
            'total': 0,
            'pending': 0,
            'delivered': 0,
            'failed': 0,
            'delivery_rate': 0
        }

def cleanup_delivered_events(days: int = 7):
    """전송 완료된 오래된 이벤트 정리"""
    try:
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        deleted_count = OutboxEvent.query.filter(
            OutboxEvent.delivered == True,
            OutboxEvent.delivered_at < cutoff_date
        ).delete()
        
        db.session.commit()
        logger.info(f"Cleaned up {deleted_count} old delivered events")
        return deleted_count
    except Exception as e:
        logger.error(f"Error cleaning up delivered events: {e}")
        db.session.rollback()
        return 0

def retry_failed_events():
    """영구 실패한 이벤트들의 재시도 횟수 초기화"""
    try:
        updated_count = OutboxEvent.query.filter(
            OutboxEvent.delivered == False,
            OutboxEvent.retry_count >= OutboxEvent.max_retries
        ).update({
            'retry_count': 0,
            'last_error': None
        })
        
        db.session.commit()
        logger.info(f"Reset retry count for {updated_count} failed events")
        return updated_count
    except Exception as e:
        logger.error(f"Error retrying failed events: {e}")
        db.session.rollback()
        return 0
