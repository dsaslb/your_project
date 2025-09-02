#!/usr/bin/env python3
"""
👤 사용자 모델

CQRS 라이트 아키텍처에서 사용자 정보를 관리
"""

from extensions import db
from datetime import datetime, timezone

class User(db.Model):
    """사용자 모델"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='employee')
    
    # 테넌트 스코프
    industry_id = db.Column(db.Integer, nullable=True)
    brand_id = db.Column(db.Integer, nullable=True)
    branch_id = db.Column(db.Integer, nullable=True)
    
    # 상태 및 메타데이터
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        """딕셔너리 형태로 변환"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'industry_id': self.industry_id,
            'brand_id': self.brand_id,
            'branch_id': self.branch_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
