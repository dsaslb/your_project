"""
구매관리 플러그인 데이터베이스 모델
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from extensions import db
import enum

class PurchaseStatus(enum.Enum):
    """구매 주문 상태"""
    DRAFT = "draft"  # 임시저장
    PENDING = "pending"  # 승인 대기
    APPROVED = "approved"  # 승인됨
    ORDERED = "ordered"  # 주문됨
    RECEIVED = "received"  # 입고됨
    CANCELLED = "cancelled"  # 취소됨

class PaymentStatus(enum.Enum):
    """결제 상태"""
    PENDING = "pending"  # 미결제
    PARTIAL = "partial"  # 부분 결제
    PAID = "paid"  # 완료
    OVERDUE = "overdue"  # 연체

class Supplier(db.Model):
    """공급업체 모델"""
    __tablename__ = 'purchase_suppliers'
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    name = Column(String(100), nullable=False)
    contact_person = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    business_number = Column(String(20), nullable=True)  # 사업자등록번호
    payment_terms = Column(Integer, default=30)  # 결제 조건 (일)
    credit_limit = Column(Float, default=0.0)  # 신용 한도
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    store = relationship('Branch', backref='purchase_suppliers')
    purchase_orders = relationship('PurchaseOrder', backref='supplier')
    
    def __repr__(self):
        return f'<Supplier {self.name}>'

class PurchaseOrder(db.Model):
    """구매 주문 모델"""
    __tablename__ = 'purchase_orders'
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    supplier_id = Column(Integer, ForeignKey('purchase_suppliers.id'), nullable=False)
    order_number = Column(String(50), unique=True, nullable=False)  # 주문번호
    order_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    expected_delivery_date = Column(DateTime, nullable=True)
    status = Column(Enum(PurchaseStatus), default=PurchaseStatus.DRAFT)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    subtotal = Column(Float, default=0.0)  # 소계
    tax_amount = Column(Float, default=0.0)  # 세금
    total_amount = Column(Float, default=0.0)  # 총액
    notes = Column(Text, nullable=True)
    approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    store = relationship('Branch', backref='purchase_orders')
    approved_user = relationship('User', foreign_keys=[approved_by], backref='approved_purchase_orders')
    created_user = relationship('User', foreign_keys=[created_by], backref='created_purchase_orders')
    order_items = relationship('PurchaseOrderItem', backref='purchase_order', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<PurchaseOrder {self.order_number}>'
    
    def calculate_totals(self):
        """총액 계산"""
        self.subtotal = sum(item.total_price for item in self.order_items)
        self.tax_amount = self.subtotal * 0.1  # 10% 부가세
        self.total_amount = self.subtotal + self.tax_amount
        return self.total_amount

class PurchaseOrderItem(db.Model):
    """구매 주문 항목 모델"""
    __tablename__ = 'purchase_order_items'
    
    id = Column(Integer, primary_key=True)
    purchase_order_id = Column(Integer, ForeignKey('purchase_orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('inventory_products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, default=0.0)
    received_quantity = Column(Integer, default=0)  # 입고된 수량
    notes = Column(Text, nullable=True)
    
    # 관계 설정
    product = relationship('Product', backref='purchase_order_items')
    
    def __repr__(self):
        return f'<PurchaseOrderItem {self.product.name} x {self.quantity}>'
    
    def calculate_total(self):
        """총 가격 계산"""
        self.total_price = self.quantity * self.unit_price
        return self.total_price

class PurchaseSettings(db.Model):
    """구매 관리 설정 모델"""
    __tablename__ = 'purchase_settings'
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    auto_approval_limit = Column(Float, default=100000)  # 자동 승인 한도
    default_payment_terms = Column(Integer, default=30)  # 기본 결제 조건
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    approval_workflow = Column(Text, nullable=True)  # 승인 워크플로우 (JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    store = relationship('Branch', backref='purchase_settings')
    
    def __repr__(self):
        return f'<PurchaseSettings {self.store_id}>'

class PurchaseReport(db.Model):
    """구매 리포트 모델"""
    __tablename__ = 'purchase_reports'
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    report_date = Column(DateTime, nullable=False)
    total_orders = Column(Integer, default=0)
    total_amount = Column(Float, default=0.0)
    pending_orders = Column(Integer, default=0)
    pending_amount = Column(Float, default=0.0)
    overdue_payments = Column(Integer, default=0)
    overdue_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계 설정
    store = relationship('Branch', backref='purchase_reports')
    
    def __repr__(self):
        return f'<PurchaseReport {self.store_id} {self.report_date.date()}>' 