"""
📱 모바일 전용 데이터 모델

모바일 앱에서 사용하는 경량 모델들
"""

from extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON

class InventoryLog(db.Model):
    """재고 조사 로그"""
    __tablename__ = 'mobile_inventory_logs'  # 테이블명 변경
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    barcode = db.Column(db.String(128), nullable=False)
    qty = db.Column(db.Integer, default=0)
    photo_url = db.Column(db.String(512))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    user = db.relationship('User', backref='mobile_inventory_logs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'barcode': self.barcode,
            'qty': self.qty,
            'photo_url': self.photo_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class MobilePurchaseOrder(db.Model):
    """발주"""
    __tablename__ = 'mobile_purchase_orders'  # 테이블명 변경
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    status = db.Column(db.String(32), default='requested')  # requested/approved/ordered/received
    items = db.Column(JSON)  # [{barcode, name, qty}]
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    user = db.relationship('User', backref='mobile_purchase_orders')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'items': self.items or [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class MobileAttendance(db.Model):
    """모바일 출퇴근 기록"""
    __tablename__ = 'mobile_attendances'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    type = db.Column(db.String(10), nullable=False)  # 'in' 또는 'out'
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    qr_code = db.Column(db.String(128))
    
    user = db.relationship('User', backref='mobile_attendances')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'qr_code': self.qr_code
        }
