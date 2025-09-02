#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모바일 관련 데이터베이스 테이블 생성 스크립트
"""

from app import app
from extensions import db
from models import MobileAttendance, InventoryLog, MobilePurchaseOrder

def create_mobile_tables():
    """모바일 관련 테이블 생성"""
    with app.app_context():
        try:
            print("🔍 모바일 관련 테이블 생성 시작...")
            
            # 모든 테이블 생성
            db.create_all()
            
            print("✅ 모바일 관련 테이블이 성공적으로 생성되었습니다!")
            print("   - mobile_attendances (출퇴근 기록)")
            print("   - mobile_inventory_logs (재고 조사 로그)")
            print("   - mobile_purchase_orders (모바일 발주)")
            
            # 테이블 존재 확인
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            mobile_tables = ['mobile_attendances', 'mobile_inventory_logs', 'mobile_purchase_orders']
            for table in mobile_tables:
                if table in existing_tables:
                    print(f"✅ {table} 테이블 확인됨")
                else:
                    print(f"❌ {table} 테이블 누락")
            
            return True
            
        except Exception as e:
            print(f"❌ 테이블 생성 실패: {e}")
            return False

if __name__ == "__main__":
    create_mobile_tables()
