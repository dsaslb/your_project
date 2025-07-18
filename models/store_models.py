from extensions import db
from datetime import datetime

class Store(db.Model):
    """매장 모델"""
    __tablename__ = 'stores'
    
    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(20), default='active')  # active, inactive, closed
    opening_hours = db.Column(db.Text, nullable=True)  # JSON 형태로 저장
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    brand = db.relationship('Brand', backref='store_brand')
    manager = db.relationship('User', backref='managed_stores')
    
    def to_dict(self):
        return {
            'id': self.id,
            'brand_id': self.brand_id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'manager_id': self.manager_id,
            'status': self.status,
            'opening_hours': self.opening_hours,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class StoreInventory(db.Model):
    """매장 재고 모델"""
    __tablename__ = 'store_inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    unit = db.Column(db.String(20), nullable=True)
    min_stock = db.Column(db.Integer, default=0)
    max_stock = db.Column(db.Integer, nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계
    store = db.relationship('Store', backref='inventory')
    
    def to_dict(self):
        return {
            'id': self.id,
            'store_id': self.store_id,
            'item_name': self.item_name,
            'quantity': self.quantity,
            'unit': self.unit,
            'min_stock': self.min_stock,
            'max_stock': self.max_stock,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

class StoreSales(db.Model):
    """매장 매출 모델"""
    __tablename__ = 'store_sales'
    
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    total_sales = db.Column(db.Float, default=0.0)
    total_orders = db.Column(db.Integer, default=0)
    average_order_value = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계
    store = db.relationship('Store', backref='sales_records')
    
    def to_dict(self):
        return {
            'id': self.id,
            'store_id': self.store_id,
            'date': self.date.isoformat() if self.date else None,
            'total_sales': self.total_sales,
            'total_orders': self.total_orders,
            'average_order_value': self.average_order_value,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 