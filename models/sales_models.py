# -*- coding: utf-8 -*-
"""
매출 데이터 모델
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Sales(Base):
    """매출 데이터 모델"""
    __tablename__ = 'sales'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    store_id = Column(Integer, ForeignKey('stores.id'), nullable=False)
    store_name = Column(String(255), nullable=False)
    total_amount = Column(Float, nullable=False, default=0.0)
    order_count = Column(Integer, nullable=False, default=0)
    customer_count = Column(Integer, nullable=False, default=0)
    average_order_value = Column(Float, nullable=False, default=0.0)
    payment_method = Column(String(50), nullable=False, default='card')  # cash, card, mobile, online
    category = Column(String(100), nullable=False, default='음식')  # 음식, 음료, 디저트, 기타
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    store = relationship("Store", back_populates="sales")
    
    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'store_id': self.store_id,
            'store_name': self.store_name,
            'total_amount': self.total_amount,
            'order_count': self.order_count,
            'customer_count': self.customer_count,
            'average_order_value': self.average_order_value,
            'payment_method': self.payment_method,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SalesSummary(Base):
    """매출 요약 데이터 모델"""
    __tablename__ = 'sales_summaries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    store_id = Column(Integer, ForeignKey('stores.id'), nullable=False)
    total_revenue = Column(Float, nullable=False, default=0.0)
    total_orders = Column(Integer, nullable=False, default=0)
    total_customers = Column(Integer, nullable=False, default=0)
    average_order_value = Column(Float, nullable=False, default=0.0)
    growth_rate = Column(Float, nullable=False, default=0.0)
    top_performing_store = Column(String(255))
    top_category = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'store_id': self.store_id,
            'total_revenue': self.total_revenue,
            'total_orders': self.total_orders,
            'total_customers': self.total_customers,
            'average_order_value': self.average_order_value,
            'growth_rate': self.growth_rate,
            'top_performing_store': self.top_performing_store,
            'top_category': self.top_category,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 