"""
동기화 관련 모델들
- IdempotencyKey: 멱등성 키 관리
- SyncAudit: 동기화 감사 로그
- OutboxEvent: 이벤트 발행을 위한 Outbox 패턴
"""
from extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
import json

class IdempotencyKey(db.Model):
    """멱등성 키 관리 테이블"""
    __tablename__ = 'idempotency_keys'
    
    key = db.Column(db.String(64), primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    
    def __repr__(self):
        return f'<IdempotencyKey {self.key}>'

class SyncAudit(db.Model):
    """동기화 감사 로그 테이블"""
    __tablename__ = 'sync_audits'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, index=True, nullable=True)
    device_id = db.Column(db.String(128), index=True, nullable=True)
    type = db.Column(db.String(32), nullable=False)  # 'attendance'|'po'|'inventory'
    idem_key = db.Column(db.String(64), index=True, nullable=False)
    status = db.Column(db.String(16), nullable=False)  # 'ok'|'dup'|'error'
    error = db.Column(db.Text, nullable=True)
    payload_size = db.Column(db.Integer, nullable=True)  # 페이로드 크기 추적
    processing_time_ms = db.Column(db.Integer, nullable=True)  # 처리 시간
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    
    def __repr__(self):
        return f'<SyncAudit {self.type}:{self.status}>'

class OutboxEvent(db.Model):
    """Outbox 패턴을 위한 이벤트 테이블"""
    __tablename__ = 'outbox_events'
    
    id = db.Column(db.Integer, primary_key=True)
    channel = db.Column(db.String(64), nullable=False, index=True)  # 'attendance:update' 등
    payload = db.Column(db.JSON, nullable=False)  # 이벤트 데이터
    delivered = db.Column(db.Boolean, default=False, index=True, nullable=False)
    retry_count = db.Column(db.Integer, default=0, nullable=False)
    max_retries = db.Column(db.Integer, default=3, nullable=False)
    last_error = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    delivered_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<OutboxEvent {self.channel}:{self.delivered}>'
    
    def to_dict(self):
        """이벤트를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'channel': self.channel,
            'payload': self.payload,
            'delivered': self.delivered,
            'retry_count': self.retry_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None
        }

class SyncMetrics(db.Model):
    """동기화 메트릭 테이블 (선택적)"""
    __tablename__ = 'sync_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(64), nullable=False, index=True)
    metric_value = db.Column(db.Float, nullable=False)
    labels = db.Column(db.JSON, nullable=True)  # 추가 라벨 정보
    timestamp = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    
    def __repr__(self):
        return f'<SyncMetrics {self.metric_name}:{self.metric_value}>'
