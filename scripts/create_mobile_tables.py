#!/usr/bin/env python3
"""
모바일 앱용 데이터베이스 테이블 생성 스크립트
"""

import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models.mobile_models import (
    MobileAttendance,
    MobileInventoryLog, 
    MobilePurchaseOrder,
    MobileSchedule,
    MobileOrder
)

def create_mobile_tables():
    """모바일 앱용 테이블들을 생성합니다."""
    
    with app.app_context():
        try:
            print("모바일 앱용 데이터베이스 테이블 생성 중...")
            
            # 테이블 생성
            db.create_all()
            
            print("✅ 모바일 앱용 테이블 생성 완료!")
            print("\n생성된 테이블들:")
            print("- mobile_attendance (출퇴근 기록)")
            print("- mobile_inventory_log (재고 조사 로그)")
            print("- mobile_purchase_order (발주 요청)")
            print("- mobile_schedule (스케줄 관리)")
            print("- mobile_order (주문 관리)")
            
            # 테이블 정보 확인
            print("\n📊 테이블 정보:")
            for table in db.metadata.tables:
                if table.startswith('mobile_'):
                    print(f"- {table}")
            
        except Exception as e:
            print(f"❌ 테이블 생성 실패: {e}")
            db.session.rollback()
            raise

def drop_mobile_tables():
    """모바일 앱용 테이블들을 삭제합니다. (주의: 모든 데이터가 삭제됩니다)"""
    
    with app.app_context():
        try:
            print("⚠️  모바일 앱용 테이블 삭제 중...")
            
            # 테이블 삭제
            MobileAttendance.__table__.drop(db.engine, checkfirst=True)
            MobileInventoryLog.__table__.drop(db.engine, checkfirst=True)
            MobilePurchaseOrder.__table__.drop(db.engine, checkfirst=True)
            MobileSchedule.__table__.drop(db.engine, checkfirst=True)
            MobileOrder.__table__.drop(db.engine, checkfirst=True)
            
            print("✅ 모바일 앱용 테이블 삭제 완료!")
            
        except Exception as e:
            print(f"❌ 테이블 삭제 실패: {e}")
            raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="모바일 앱용 데이터베이스 테이블 관리")
    parser.add_argument("--action", choices=["create", "drop"], default="create",
                       help="실행할 작업 (create: 테이블 생성, drop: 테이블 삭제)")
    
    args = parser.parse_args()
    
    if args.action == "create":
        create_mobile_tables()
    elif args.action == "drop":
        confirm = input("정말로 모든 모바일 앱 데이터를 삭제하시겠습니까? (yes/no): ")
        if confirm.lower() == "yes":
            drop_mobile_tables()
        else:
            print("작업이 취소되었습니다.")
