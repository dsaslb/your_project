#!/usr/bin/env python3
"""
Idempotency 테이블 생성 스크립트
"""

import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models.idempotency import IdempotencyKey

def create_idempotency_table():
    """Idempotency 테이블을 생성합니다."""
    
    with app.app_context():
        try:
            print("Idempotency 테이블 생성 중...")
            
            # 테이블 생성
            db.create_all()
            
            print("✅ Idempotency 테이블 생성 완료!")
            
            # 테이블 정보 확인
            print("\n📊 생성된 테이블:")
            if 'idempotency_keys' in db.metadata.tables:
                print("- idempotency_keys")
            else:
                print("❌ idempotency_keys 테이블이 생성되지 않았습니다.")
            
        except Exception as e:
            print(f"❌ 테이블 생성 실패: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    create_idempotency_table()
