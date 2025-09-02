#!/usr/bin/env python3
"""
🏭 산업 모델

CQRS 라이트 아키텍처에서 산업 정보를 관리
"""

from extensions import db
from datetime import datetime, timezone

class Industry(db.Model):
    """산업 모델"""
    __tablename__ = 'industries'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Industry {self.name}>'
    
    def to_dict(self):
        """딕셔너리 형태로 변환"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
