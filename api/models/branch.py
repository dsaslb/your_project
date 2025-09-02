#!/usr/bin/env python3
"""
🏪 지점 모델

CQRS 라이트 아키텍처에서 지점 정보를 관리
"""

from extensions import db
from datetime import datetime, timezone

class Branch(db.Model):
    """지점 모델"""
    __tablename__ = 'branches'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)
    industry_id = db.Column(db.Integer, db.ForeignKey('industries.id'), nullable=False)
    address = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # 관계 설정
    brand = db.relationship('Brand', backref='branches')
    industry = db.relationship('Industry', backref='branches')
    
    def __repr__(self):
        return f'<Branch {self.name}>'
    
    def to_dict(self):
        """딕셔너리 형태로 변환"""
        return {
            'id': self.id,
            'name': self.name,
            'brand_id': self.brand_id,
            'industry_id': self.industry_id,
            'address': self.address,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
