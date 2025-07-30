#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
계층별 관리 시스템 샘플 데이터 생성 스크립트
Industry -> Brand -> Branch -> Employee 구조의 샘플 데이터를 생성합니다.
"""

from app import app, db
from models_main import Industry, Brand, Branch, User
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_sample_data():
    """샘플 데이터 생성"""
    with app.app_context():
        print("🔄 샘플 데이터 생성을 시작합니다...")
        
        # 1. 업종 데이터 생성
        print("📊 업종 데이터 생성 중...")
        industries_data = [
            {
                'name': '외식업',
                'code': 'FOOD',
                'color': '#FF6B6B',
                'icon': '🍽️',
                'description': '음식점, 카페, 패스트푸드 등'
            },
            {
                'name': '유통업',
                'code': 'RETAIL',
                'color': '#4ECDC4',
                'icon': '🛒',
                'description': '편의점, 마트, 백화점 등'
            },
            {
                'name': '서비스업',
                'code': 'SERVICE',
                'color': '#45B7D1',
                'icon': '🔧',
                'description': '미용실, 세탁소, 수리업 등'
            },
            {
                'name': '제조업',
                'code': 'MANUFACTURE',
                'color': '#96CEB4',
                'icon': '🏭',
                'description': '식품 제조, 가공업 등'
            }
        ]
        
        created_industries = []
        for ind_data in industries_data:
            industry = Industry.query.filter_by(name=ind_data['name']).first()
            if not industry:
                industry = Industry(
                    name=ind_data['name'],
                    code=ind_data['code'],
                    color=ind_data['color'],
                    icon=ind_data['icon'],
                    description=ind_data['description'],
                    is_active=True,
                    created_at=datetime.now()
                )
                db.session.add(industry)
                created_industries.append(industry)
                print(f"  ✅ {ind_data['name']} 업종 생성")
            else:
                created_industries.append(industry)
                print(f"  ⚠️ {ind_data['name']} 업종 이미 존재")
        
        db.session.commit()
        
        # 2. 브랜드 데이터 생성
        print("🏢 브랜드 데이터 생성 중...")
        brands_data = [
            # 외식업 브랜드들
            {'name': '스타벅스', 'code': 'SBUX', 'industry_id': 1, 'description': '글로벌 커피 체인'},
            {'name': '맥도날드', 'code': 'MCD', 'industry_id': 1, 'description': '패스트푸드 체인'},
            {'name': '올리브영', 'code': 'OLIVE', 'industry_id': 2, 'description': '헬스앤뷰티 체인'},
            {'name': 'CU', 'code': 'CU', 'industry_id': 2, 'description': '편의점 체인'},
            {'name': 'GS25', 'code': 'GS25', 'industry_id': 2, 'description': '편의점 체인'},
            {'name': '이마트', 'code': 'EMART', 'industry_id': 2, 'description': '대형마트'},
            {'name': '토니모리', 'code': 'TONYMOLY', 'industry_id': 3, 'description': '뷰티 브랜드'},
            {'name': '네일샵', 'code': 'NAIL', 'industry_id': 3, 'description': '네일 아트샵'},
            {'name': '삼성전자', 'code': 'SAMSUNG', 'industry_id': 4, 'description': '전자제품 제조'},
            {'name': 'LG화학', 'code': 'LGCHEM', 'industry_id': 4, 'description': '화학제품 제조'}
        ]
        
        created_brands = []
        for brand_data in brands_data:
            brand = Brand.query.filter_by(name=brand_data['name']).first()
            if not brand:
                brand = Brand(
                    name=brand_data['name'],
                    code=brand_data['code'],
                    industry_id=brand_data['industry_id'],
                    description=brand_data['description'],
                    status='active',
                    created_at=datetime.now()
                )
                db.session.add(brand)
                created_brands.append(brand)
                print(f"  ✅ {brand_data['name']} 브랜드 생성")
            else:
                created_brands.append(brand)
                print(f"  ⚠️ {brand_data['name']} 브랜드 이미 존재")
        
        db.session.commit()
        
        # 3. 매장 데이터 생성
        print("🏪 매장 데이터 생성 중...")
        branches_data = [
            # 스타벅스 매장들
            {'name': '스타벅스 강남점', 'store_code': 'SBUX001', 'brand_id': 1, 'address': '서울시 강남구 강남대로 123'},
            {'name': '스타벅스 홍대점', 'store_code': 'SBUX002', 'brand_id': 1, 'address': '서울시 마포구 홍대로 456'},
            {'name': '스타벅스 부산점', 'store_code': 'SBUX003', 'brand_id': 1, 'address': '부산시 해운대구 해운대로 789'},
            
            # 맥도날드 매장들
            {'name': '맥도날드 강남점', 'store_code': 'MCD001', 'brand_id': 2, 'address': '서울시 강남구 테헤란로 111'},
            {'name': '맥도날드 신촌점', 'store_code': 'MCD002', 'brand_id': 2, 'address': '서울시 서대문구 신촌로 222'},
            
            # 올리브영 매장들
            {'name': '올리브영 강남점', 'store_code': 'OLIVE001', 'brand_id': 3, 'address': '서울시 강남구 역삼로 333'},
            {'name': '올리브영 홍대점', 'store_code': 'OLIVE002', 'brand_id': 3, 'address': '서울시 마포구 와우산로 444'},
            
            # CU 매장들
            {'name': 'CU 강남점', 'store_code': 'CU001', 'brand_id': 4, 'address': '서울시 강남구 삼성로 555'},
            {'name': 'CU 홍대점', 'store_code': 'CU002', 'brand_id': 4, 'address': '서울시 마포구 양화로 666'},
            
            # GS25 매장들
            {'name': 'GS25 강남점', 'store_code': 'GS25001', 'brand_id': 5, 'address': '서울시 강남구 영동대로 777'},
            {'name': 'GS25 홍대점', 'store_code': 'GS25002', 'brand_id': 5, 'address': '서울시 마포구 동교로 888'}
        ]
        
        created_branches = []
        for branch_data in branches_data:
            branch = Branch.query.filter_by(store_code=branch_data['store_code']).first()
            if not branch:
                branch = Branch(
                    name=branch_data['name'],
                    store_code=branch_data['store_code'],
                    brand_id=branch_data['brand_id'],
                    address=branch_data['address'],
                    status='active',
                    created_at=datetime.now()
                )
                db.session.add(branch)
                created_branches.append(branch)
                print(f"  ✅ {branch_data['name']} 매장 생성")
            else:
                created_branches.append(branch)
                print(f"  ⚠️ {branch_data['name']} 매장 이미 존재")
        
        db.session.commit()
        
        # 4. 직원 데이터 생성
        print("👥 직원 데이터 생성 중...")
        employees_data = [
            # 스타벅스 강남점 직원들
            {'username': 'kim_manager', 'email': 'kim@starbucks.com', 'role': 'manager', 'branch_id': 1},
            {'username': 'lee_barista', 'email': 'lee@starbucks.com', 'role': 'employee', 'branch_id': 1},
            {'username': 'park_barista', 'email': 'park@starbucks.com', 'role': 'employee', 'branch_id': 1},
            
            # 스타벅스 홍대점 직원들
            {'username': 'choi_manager', 'email': 'choi@starbucks.com', 'role': 'manager', 'branch_id': 2},
            {'username': 'jung_barista', 'email': 'jung@starbucks.com', 'role': 'employee', 'branch_id': 2},
            
            # 맥도날드 강남점 직원들
            {'username': 'yoon_manager', 'email': 'yoon@mcdonalds.com', 'role': 'manager', 'branch_id': 4},
            {'username': 'han_employee', 'email': 'han@mcdonalds.com', 'role': 'employee', 'branch_id': 4},
            
            # 올리브영 강남점 직원들
            {'username': 'shin_manager', 'email': 'shin@oliveyoung.com', 'role': 'manager', 'branch_id': 6},
            {'username': 'oh_employee', 'email': 'oh@oliveyoung.com', 'role': 'employee', 'branch_id': 6},
            
            # CU 강남점 직원들
            {'username': 'kwon_manager', 'email': 'kwon@cu.co.kr', 'role': 'manager', 'branch_id': 8},
            {'username': 'baek_employee', 'email': 'baek@cu.co.kr', 'role': 'employee', 'branch_id': 8}
        ]
        
        created_employees = []
        for emp_data in employees_data:
            employee = User.query.filter_by(username=emp_data['username']).first()
            if not employee:
                employee = User(
                    username=emp_data['username'],
                    email=emp_data['email'],
                    password_hash=generate_password_hash('password123'),
                    role=emp_data['role'],
                    branch_id=emp_data['branch_id'],
                    status='approved',
                    created_at=datetime.now()
                )
                db.session.add(employee)
                created_employees.append(employee)
                print(f"  ✅ {emp_data['username']} 직원 생성")
            else:
                created_employees.append(employee)
                print(f"  ⚠️ {emp_data['username']} 직원 이미 존재")
        
        db.session.commit()
        
        print("\n🎉 샘플 데이터 생성 완료!")
        print(f"📊 생성된 데이터:")
        print(f"  - 업종: {len(created_industries)}개")
        print(f"  - 브랜드: {len(created_brands)}개")
        print(f"  - 매장: {len(created_branches)}개")
        print(f"  - 직원: {len(created_employees)}개")
        
        print("\n🔗 계층 구조:")
        for industry in created_industries:
            print(f"  📁 {industry.name} ({industry.icon})")
            brands = Brand.query.filter_by(industry_id=industry.id).all()
            for brand in brands:
                print(f"    🏢 {brand.name}")
                branches = Branch.query.filter_by(brand_id=brand.id).all()
                for branch in branches:
                    print(f"      🏪 {branch.name}")
                    employees = User.query.filter_by(branch_id=branch.id).all()
                    for emp in employees:
                        print(f"        👤 {emp.username} ({emp.role})")

if __name__ == "__main__":
    create_sample_data() 