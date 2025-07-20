"""
재고관리 플러그인 데이터베이스 모델
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from extensions import db
import enum

class TransactionType(enum.Enum):
    """재고 거래 유형"""
    IN = "in"  # 입고
    OUT = "out"  # 출고
    ADJUSTMENT = "adjustment"  # 재고 조정
    RETURN = "return"  # 반품
    DAMAGE = "damage"  # 손실

class Product(db.Model):
    """상품 모델"""
    __tablename__ = 'inventory_products'
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    name = Column(String(100), nullable=False)
    sku = Column(String(50), unique=True, nullable=False)  # Stock Keeping Unit
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)
    unit = Column(String(20), default='개')  # 단위 (개, kg, L 등)
    cost_price = Column(Float, default=0.0)  # 원가
    selling_price = Column(Float, default=0.0)  # 판매가
    current_stock = Column(Integer, default=0)  # 현재 재고
    min_stock = Column(Integer, default=0)  # 최소 재고
    max_stock = Column(Integer, default=1000)  # 최대 재고
    supplier = Column(String(100), nullable=True)  # 공급업체
    location = Column(String(50), nullable=True)  # 보관 위치
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    store = relationship('Branch', backref='inventory_products')
    transactions = relationship('InventoryTransaction', backref='product')
    
    def __repr__(self):
        return f'<Product {self.name} ({self.sku})>'
    
    def update_stock(self, quantity, transaction_type):
        """재고 업데이트"""
        if transaction_type == TransactionType.IN:
            self.current_stock += quantity
        elif transaction_type == TransactionType.OUT:
            self.current_stock -= quantity
        elif transaction_type == TransactionType.ADJUSTMENT:
            self.current_stock = quantity
        elif transaction_type == TransactionType.RETURN:
            self.current_stock += quantity
        elif transaction_type == TransactionType.DAMAGE:
            self.current_stock -= quantity
        
        self.updated_at = datetime.utcnow()
    
    def is_low_stock(self):
        """재고 부족 여부 확인"""
        return self.current_stock <= self.min_stock

class InventoryTransaction(db.Model):
    """재고 거래 기록 모델"""
    __tablename__ = 'inventory_transactions'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('inventory_products.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, default=0.0)  # 단가
    total_amount = Column(Float, default=0.0)  # 총 금액
    reference_number = Column(String(50), nullable=True)  # 참조 번호 (주문번호 등)
    notes = Column(Text, nullable=True)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계 설정
    user = relationship('User', backref='inventory_transactions')
    
    def __repr__(self):
        return f'<InventoryTransaction {self.transaction_type.value} {self.quantity}>'
    
    def calculate_total(self):
        """총 금액 계산"""
        self.total_amount = self.quantity * self.unit_price
        return self.total_amount

class InventorySettings(db.Model):
    """재고 관리 설정 모델"""
    __tablename__ = 'inventory_settings'
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    low_stock_threshold = Column(Integer, default=10)  # 재고 부족 임계값
    auto_reorder_enabled = Column(Boolean, default=False)  # 자동 재주문 활성화
    reorder_quantity = Column(Integer, default=50)  # 재주문 수량
    stock_alert_email = Column(Boolean, default=True)  # 재고 알림 이메일
    stock_alert_sms = Column(Boolean, default=False)  # 재고 알림 SMS
    alert_recipients = Column(Text, nullable=True)  # 알림 수신자 (JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    store = relationship('Branch', backref='inventory_settings')
    
    def __repr__(self):
        return f'<InventorySettings {self.store_id}>'

class InventoryReport(db.Model):
    """재고 리포트 모델"""
    __tablename__ = 'inventory_reports'
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    report_date = Column(DateTime, nullable=False)
    total_products = Column(Integer, default=0)
    low_stock_products = Column(Integer, default=0)
    out_of_stock_products = Column(Integer, default=0)
    total_value = Column(Float, default=0.0)  # 총 재고 가치
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계 설정
    store = relationship('Branch', backref='inventory_reports')
    
    def __repr__(self):
        return f'<InventoryReport {self.store_id} {self.report_date.date()}>' 