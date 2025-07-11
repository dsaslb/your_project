"""
알림 히스토리 및 통계 모델
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from database import Base

class NotificationHistory(Base):
    """알림 히스토리"""
    __tablename__ = 'notification_history'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    level = Column(String(20), nullable=False)  # info, warning, critical
    channel = Column(String(100), nullable=False)
    recipient = Column(String(255))
    metadata = Column(JSON)
    sent_at = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    # 인덱스 생성
    __table_args__ = (
        Index('idx_notification_level', 'level'),
        Index('idx_notification_channel', 'channel'),
        Index('idx_notification_sent_at', 'sent_at'),
        Index('idx_notification_success', 'success'),
    )

class NotificationChannel(Base):
    """알림 채널 설정"""
    __tablename__ = 'notification_channels'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    type = Column(String(50), nullable=False)  # email, sms, slack, discord, webhook
    enabled = Column(Boolean, default=True)
    config = Column(JSON, nullable=False)
    priority = Column(Integer, default=2)  # 1: 높음, 2: 중간, 3: 낮음
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 인덱스 생성
    __table_args__ = (
        Index('idx_channel_name', 'name'),
        Index('idx_channel_type', 'type'),
        Index('idx_channel_enabled', 'enabled'),
        Index('idx_channel_priority', 'priority'),
    )

class NotificationTemplate(Base):
    """알림 템플릿"""
    __tablename__ = 'notification_templates'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    title_template = Column(String(255), nullable=False)
    message_template = Column(Text, nullable=False)
    level = Column(String(20), default='info')
    channels = Column(JSON)  # 사용할 채널 목록
    variables = Column(JSON)  # 템플릿 변수 정의
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 인덱스 생성
    __table_args__ = (
        Index('idx_template_name', 'name'),
        Index('idx_template_level', 'level'),
    )

class NotificationRule(Base):
    """알림 규칙"""
    __tablename__ = 'notification_rules'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    condition_type = Column(String(50), nullable=False)  # threshold, pattern, schedule
    condition_config = Column(JSON, nullable=False)
    template_id = Column(Integer, ForeignKey('notification_templates.id'))
    enabled = Column(Boolean, default=True)
    cooldown_minutes = Column(Integer, default=0)  # 알림 간격 (분)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    template = relationship("NotificationTemplate")
    
    # 인덱스 생성
    __table_args__ = (
        Index('idx_rule_name', 'name'),
        Index('idx_rule_enabled', 'enabled'),
        Index('idx_rule_condition_type', 'condition_type'),
    )

class NotificationEscalation(Base):
    """알림 에스컬레이션"""
    __tablename__ = 'notification_escalations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    trigger_condition = Column(JSON, nullable=False)  # 에스컬레이션 조건
    escalation_steps = Column(JSON, nullable=False)  # 에스컬레이션 단계
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 인덱스 생성
    __table_args__ = (
        Index('idx_escalation_name', 'name'),
        Index('idx_escalation_enabled', 'enabled'),
    )

class NotificationStatistics(Base):
    """알림 통계"""
    __tablename__ = 'notification_statistics'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    channel = Column(String(100), nullable=False)
    level = Column(String(20), nullable=False)
    total_sent = Column(Integer, default=0)
    successful_sent = Column(Integer, default=0)
    failed_sent = Column(Integer, default=0)
    avg_response_time = Column(Integer)  # 평균 응답 시간 (ms)
    
    # 인덱스 생성
    __table_args__ = (
        Index('idx_statistics_date', 'date'),
        Index('idx_statistics_channel', 'channel'),
        Index('idx_statistics_level', 'level'),
        Index('idx_statistics_date_channel', 'date', 'channel'),
    ) 