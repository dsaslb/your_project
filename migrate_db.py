#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데이터베이스 마이그레이션 스크립트
"""

from app import app, db
from models_main import Industry, Brand, Branch, User

def migrate_database():
    """데이터베이스 마이그레이션 실행"""
    with app.app_context():
        print("🔄 데이터베이스 마이그레이션을 시작합니다...")
        
        try:
            # 모든 테이블 생성
            db.create_all()
            print("✅ 모든 테이블이 성공적으로 생성되었습니다.")
            
            # 기존 데이터 확인
            industries = Industry.query.all()
            brands = Brand.query.all()
            branches = Branch.query.all()
            users = User.query.all()
            
            print(f"📊 현재 데이터베이스 상태:")
            print(f"  - 업종: {len(industries)}개")
            print(f"  - 브랜드: {len(brands)}개")
            print(f"  - 매장: {len(branches)}개")
            print(f"  - 사용자: {len(users)}개")
            
        except Exception as e:
            print(f"❌ 마이그레이션 중 오류 발생: {e}")
            return False
        
        return True

if __name__ == "__main__":
    migrate_database() 