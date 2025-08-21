from extensions import db
from datetime import datetime
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.dialects.postgresql import JSONB

class MobileAttendance(db.Model):
    """모바일 출퇴근 기록"""
    __tablename__ = 'mobile_attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    type = db.Column(db.String(10), nullable=False)  # 'in' 또는 'out'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    qr_code = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    user = db.relationship('models_main.User', backref='mobile_attendance_records', foreign_keys=[user_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'timestamp': self.timestamp.isoformat(),
            'latitude': self.latitude,
            'longitude': self.longitude,
            'qr_code': self.qr_code,
            'created_at': self.created_at.isoformat()
        }

class MobileInventoryLog(db.Model):
    """모바일 재고 조사 로그"""
    __tablename__ = 'mobile_inventory_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    barcode = db.Column(db.String(128), nullable=False, index=True)
    quantity = db.Column(db.Integer, default=0)
    photo_url = db.Column(db.String(512))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    user = db.relationship('models_main.User', backref='mobile_inventory_logs', foreign_keys=[user_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'barcode': self.barcode,
            'quantity': self.quantity,
            'photo_url': self.photo_url,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

class MobilePurchaseOrder(db.Model):
    """모바일 발주 요청"""
    __tablename__ = 'mobile_purchase_order'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    status = db.Column(db.String(20), default='requested')  # requested, approved, ordered, received
    items = db.Column(SQLiteJSON)  # 발주 항목들
    total_amount = db.Column(db.Numeric(10, 2))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    user = db.relationship('models_main.User', backref='mobile_purchase_orders', foreign_keys=[user_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'items': self.items,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class MobileSchedule(db.Model):
    """모바일 스케줄 관리"""
    __tablename__ = 'mobile_schedule'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    type = db.Column(db.String(20), default='work')  # work, vacation, sick, etc.
    status = db.Column(db.String(20), default='scheduled')  # scheduled, approved, rejected
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    user = db.relationship('models_main.User', backref='mobile_schedules', foreign_keys=[user_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'title': self.title,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'type': self.type,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

class MobileOrder(db.Model):
    """모바일 주문 관리"""
    __tablename__ = 'mobile_order'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_name = db.Column(db.String(255))
    items = db.Column(SQLiteJSON)  # 주문 항목들
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, preparing, ready, delivered
    total_amount = db.Column(db.Numeric(10, 2))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    user = db.relationship('models_main.User', backref='mobile_orders', foreign_keys=[user_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'order_number': self.order_number,
            'customer_name': self.customer_name,
            'items': self.items,
            'status': self.status,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
