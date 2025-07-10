#!/usr/bin/env python3
"""
슈퍼 관리자 계정 생성 스크립트
"""

import os
import sys
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Branch
from werkzeug.security import generate_password_hash

def create_super_admin():
    """슈퍼 관리자 계정 생성"""
    print("🚀 슈퍼 관리자 계정 설정 스크립트를 시작합니다...")
    print("=" * 50)
    
    with app.app_context():
        # 데이터베이스 테이블 생성
        db.create_all()
        
        # admin 계정 확인/생성
        admin = User.query.filter_by(username='admin').first()
        
        if admin:
            print(f"⚠️  admin 계정이 이미 존재합니다!")
            print(f"   기존 계정 ID: {admin.id}")
            print(f"   상태: {admin.status}")
            print(f"   역할: {admin.role}")
            
            # 슈퍼 관리자로 변경
            admin.role = 'super_admin'
            admin.status = 'approved'
            admin.grade = 'ceo'
            admin.name = '슈퍼 관리자'
            admin.email = 'admin@your_program.com'
            admin.position = '최고관리자'
            admin.department = '경영진'
            admin.set_password('admin123!')
            db.session.commit()
            print("✅ admin 계정을 슈퍼 관리자로 변경했습니다!")
        else:
            # 새 슈퍼 관리자 계정 생성
            admin = User(
                username='admin',
                email='admin@your_program.com',
                name='슈퍼 관리자',
                role='super_admin',
                grade='ceo',
                status='approved',
                position='최고관리자',
                department='경영진'
            )
            admin.set_password('admin123!')
            db.session.add(admin)
            db.session.commit()
            print("✅ 슈퍼 관리자 계정을 생성했습니다!")
        
        print("\n" + "=" * 50)
        print("🎉 슈퍼 관리자 계정 설정 완료!")
        print("슈퍼 관리자 계정:")
        print("1. 아이디: admin")
        print("2. 비밀번호: admin123!")
        print("\n접속 가능한 페이지:")
        print("- 슈퍼 관리자 대시보드: /admin-dashboard")
        print("- 브랜드 관리자 대시보드: /brand-dashboard")
        print("- 매장 관리자 대시보드: /store-dashboard")
        print("- 일반 대시보드: /dashboard")

if __name__ == '__main__':
    create_super_admin() 
