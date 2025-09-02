"""
📝 이벤트 로그 모델

모든 시스템 변경사항을 누적하여 감사, 분쟁 해결, 분석에 활용
"""

from extensions import db
from datetime import datetime, timezone, timedelta
import json
from typing import Dict, Any, Optional

class EventLog(db.Model):
    """시스템 이벤트 로그"""
    __tablename__ = 'event_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 이벤트 기본 정보
    event_type = db.Column(db.String(100), nullable=False, index=True)  # 'attendance:update', 'inventory:update' 등
    event_version = db.Column(db.Integer, default=1, nullable=False)    # 이벤트 버전
    
    # 사용자 정보
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    user_role = db.Column(db.String(50), nullable=True)
    
    # 테넌트 스코프
    industry_id = db.Column(db.Integer, nullable=True, index=True)
    brand_id = db.Column(db.Integer, nullable=True, index=True)
    branch_id = db.Column(db.Integer, nullable=True, index=True)
    
    # 리소스 정보
    resource_type = db.Column(db.String(50), nullable=True)  # 'attendance', 'inventory', 'order' 등
    resource_id = db.Column(db.String(100), nullable=True)   # 리소스 ID
    
    # 변경 내용
    old_values = db.Column(db.Text, nullable=True)  # JSON 형태의 이전 값
    new_values = db.Column(db.Text, nullable=True)  # JSON 형태의 새로운 값
    changes = db.Column(db.Text, nullable=True)     # JSON 형태의 변경 사항
    
    # 메타데이터
    ip_address = db.Column(db.String(45), nullable=True)     # IPv4/IPv6
    user_agent = db.Column(db.String(500), nullable=True)    # 브라우저/앱 정보
    device_id = db.Column(db.String(100), nullable=True)     # 모바일 디바이스 ID
    
    # 시간 정보
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    
    # 관계 설정
    user = db.relationship('models_main.User', backref='event_logs', foreign_keys=[user_id])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc)
    
    def set_old_values(self, data: Dict[str, Any]):
        """이전 값 설정"""
        self.old_values = json.dumps(data, ensure_ascii=False, default=str)
    
    def set_new_values(self, data: Dict[str, Any]):
        """새로운 값 설정"""
        self.new_values = json.dumps(data, ensure_ascii=False, default=str)
    
    def set_changes(self, changes: Dict[str, Any]):
        """변경 사항 설정"""
        self.changes = json.dumps(changes, ensure_ascii=False, default=str)
    
    def get_old_values(self) -> Optional[Dict[str, Any]]:
        """이전 값 조회"""
        if self.old_values:
            try:
                return json.loads(self.old_values)
            except json.JSONDecodeError:
                return None
        return None
    
    def get_new_values(self) -> Optional[Dict[str, Any]]:
        """새로운 값 조회"""
        if self.new_values:
            try:
                return json.loads(self.new_values)
            except json.JSONDecodeError:
                return None
        return None
    
    def get_changes(self) -> Optional[Dict[str, Any]]:
        """변경 사항 조회"""
        if self.changes:
            try:
                return json.loads(self.changes)
            except json.JSONDecodeError:
                return None
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리 형태로 변환"""
        return {
            'id': self.id,
            'event_type': self.event_type,
            'event_version': self.event_version,
            'user_id': self.user_id,
            'user_role': self.user_role,
            'industry_id': self.industry_id,
            'brand_id': self.brand_id,
            'branch_id': self.branch_id,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'old_values': self.get_old_values(),
            'new_values': self.get_new_values(),
            'changes': self.get_changes(),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'device_id': self.device_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def log_event(cls, 
                  event_type: str,
                  user_id: Optional[int] = None,
                  user_role: Optional[str] = None,
                  industry_id: Optional[int] = None,
                  brand_id: Optional[int] = None,
                  branch_id: Optional[int] = None,
                  resource_type: Optional[str] = None,
                  resource_id: Optional[str] = None,
                  old_values: Optional[Dict[str, Any]] = None,
                  new_values: Optional[Dict[str, Any]] = None,
                  changes: Optional[Dict[str, Any]] = None,
                  ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None,
                  device_id: Optional[str] = None,
                  event_version: int = 1) -> 'EventLog':
        """이벤트 로그 생성 헬퍼 메서드"""
        
        event_log = cls(
            event_type=event_type,
            event_version=event_version,
            user_id=user_id,
            user_role=user_role,
            industry_id=industry_id,
            brand_id=brand_id,
            branch_id=branch_id,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            device_id=device_id
        )
        
        if old_values:
            event_log.set_old_values(old_values)
        if new_values:
            event_log.set_new_values(new_values)
        if changes:
            event_log.set_changes(changes)
        
        db.session.add(event_log)
        db.session.commit()
        
        return event_log
    
    @classmethod
    def get_events_by_type(cls, event_type: str, limit: int = 100) -> list:
        """특정 타입의 이벤트 조회"""
        return cls.query.filter_by(event_type=event_type).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_events_by_user(cls, user_id: int, limit: int = 100) -> list:
        """특정 사용자의 이벤트 조회"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_events_by_branch(cls, branch_id: int, limit: int = 100) -> list:
        """특정 지점의 이벤트 조회"""
        return cls.query.filter_by(branch_id=branch_id).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_events_by_resource(cls, resource_type: str, resource_id: str, limit: int = 100) -> list:
        """특정 리소스의 이벤트 조회"""
        return cls.query.filter_by(
            resource_type=resource_type, 
            resource_id=resource_id
        ).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def cleanup_old_events(cls, days: int = 90):
        """오래된 이벤트 로그 정리"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        old_events = cls.query.filter(cls.created_at < cutoff_date).all()
        
        for event in old_events:
            db.session.delete(event)
        
        db.session.commit()
        return len(old_events)
