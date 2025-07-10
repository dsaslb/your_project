#!/usr/bin/env python3
"""
계층형 구조 기본 데이터 생성 스크립트
업종 → 브랜드 → 매장 → 직원 구조로 기본 데이터를 생성합니다.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Industry, Brand, Branch, User, IndustryPlugin, BrandPlugin
from datetime import datetime
from werkzeug.security import generate_password_hash

def create_industries():
    """업종 데이터 생성"""
    industries = [
        {
            'name': '레스토랑',
            'code': 'restaurant',
            'description': '음식점 및 카페 업종',
            'icon': 'fas fa-utensils',
            'color': '#FF6B6B'
        },
        {
            'name': '병원',
            'code': 'hospital',
            'description': '의료기관 업종',
            'icon': 'fas fa-hospital',
            'color': '#4ECDC4'
        },
        {
            'name': '미용실',
            'code': 'beauty',
            'description': '미용 및 뷰티 업종',
            'icon': 'fas fa-cut',
            'color': '#45B7D1'
        },
        {
            'name': '옷가게',
            'code': 'clothing',
            'description': '의류 및 패션 업종',
            'icon': 'fas fa-tshirt',
            'color': '#96CEB4'
        },
        {
            'name': '편의점',
            'code': 'convenience',
            'description': '편의점 및 소매업',
            'icon': 'fas fa-store',
            'color': '#FFEAA7'
        }
    ]
    
    for industry_data in industries:
        industry = Industry(**industry_data)
        db.session.add(industry)
    
    db.session.commit()
    print("✅ 업종 데이터 생성 완료")

def create_brands():
    """브랜드 데이터 생성"""
    # 레스토랑 업종의 브랜드들
    restaurant_industry = Industry.query.filter_by(code='restaurant').first()
    if not restaurant_industry:
        print("❌ 레스토랑 업종을 찾을 수 없습니다")
        return
    
    restaurant_brands = [
        {
            'name': '맛있는 치킨',
            'code': 'delicious_chicken',
            'industry_id': restaurant_industry.id,
            'description': '국내 최고의 치킨 브랜드',
            'website': 'https://delicious-chicken.com',
            'contact_email': 'info@delicious-chicken.com',
            'contact_phone': '02-1234-5678'
        },
        {
            'name': '신선한 피자',
            'code': 'fresh_pizza',
            'industry_id': restaurant_industry.id,
            'description': '신선한 재료로 만드는 피자',
            'website': 'https://fresh-pizza.com',
            'contact_email': 'info@fresh-pizza.com',
            'contact_phone': '02-2345-6789'
        }
    ]
    
    # 병원 업종의 브랜드들
    hospital_industry = Industry.query.filter_by(code='hospital').first()
    if not hospital_industry:
        print("❌ 병원 업종을 찾을 수 없습니다")
        return
    
    hospital_brands = [
        {
            'name': '건강한 병원',
            'code': 'healthy_hospital',
            'industry_id': hospital_industry.id,
            'description': '환자 중심의 의료 서비스',
            'website': 'https://healthy-hospital.com',
            'contact_email': 'info@healthy-hospital.com',
            'contact_phone': '02-3456-7890'
        }
    ]
    
    # 미용실 업종의 브랜드들
    beauty_industry = Industry.query.filter_by(code='beauty').first()
    if not beauty_industry:
        print("❌ 미용실 업종을 찾을 수 없습니다")
        return
    
    beauty_brands = [
        {
            'name': '아름다운 미용실',
            'code': 'beautiful_beauty',
            'industry_id': beauty_industry.id,
            'description': '아름다움을 만드는 미용실',
            'website': 'https://beautiful-beauty.com',
            'contact_email': 'info@beautiful-beauty.com',
            'contact_phone': '02-4567-8901'
        }
    ]
    
    all_brands = restaurant_brands + hospital_brands + beauty_brands
    
    for brand_data in all_brands:
        brand = Brand(**brand_data)
        db.session.add(brand)
    
    db.session.commit()
    print("✅ 브랜드 데이터 생성 완료")

def create_branches():
    """매장 데이터 생성"""
    # 맛있는 치킨 브랜드의 매장들
    delicious_chicken = Brand.query.filter_by(code='delicious_chicken').first()
    if not delicious_chicken:
        print("❌ 맛있는 치킨 브랜드를 찾을 수 없습니다")
        return
    
    chicken_branches = [
        {
            'name': '맛있는 치킨 강남점',
            'brand_id': delicious_chicken.id,
            'industry_id': delicious_chicken.industry_id,
            'address': '서울시 강남구 테헤란로 123',
            'phone': '02-1234-5678',
            'store_code': 'CH001',
            'store_type': 'franchise',
            'capacity': 50
        },
        {
            'name': '맛있는 치킨 홍대점',
            'brand_id': delicious_chicken.id,
            'industry_id': delicious_chicken.industry_id,
            'address': '서울시 마포구 홍대로 456',
            'phone': '02-2345-6789',
            'store_code': 'CH002',
            'store_type': 'franchise',
            'capacity': 40
        }
    ]
    
    # 신선한 피자 브랜드의 매장들
    fresh_pizza = Brand.query.filter_by(code='fresh_pizza').first()
    if not fresh_pizza:
        print("❌ 신선한 피자 브랜드를 찾을 수 없습니다")
        return
    
    pizza_branches = [
        {
            'name': '신선한 피자 강남점',
            'brand_id': fresh_pizza.id,
            'industry_id': fresh_pizza.industry_id,
            'address': '서울시 강남구 역삼로 789',
            'phone': '02-3456-7890',
            'store_code': 'PZ001',
            'store_type': 'franchise',
            'capacity': 60
        }
    ]
    
    # 건강한 병원 브랜드의 매장들
    healthy_hospital = Brand.query.filter_by(code='healthy_hospital').first()
    if not healthy_hospital:
        print("❌ 건강한 병원 브랜드를 찾을 수 없습니다")
        return
    
    hospital_branches = [
        {
            'name': '건강한 병원 강남점',
            'brand_id': healthy_hospital.id,
            'industry_id': healthy_hospital.industry_id,
            'address': '서울시 강남구 삼성로 101',
            'phone': '02-4567-8901',
            'store_code': 'HP001',
            'store_type': 'corporate',
            'capacity': 100
        }
    ]
    
    all_branches = chicken_branches + pizza_branches + hospital_branches
    
    for branch_data in all_branches:
        branch = Branch(**branch_data)
        db.session.add(branch)
    
    db.session.commit()
    print("✅ 매장 데이터 생성 완료")

def create_users():
    """사용자 데이터 생성"""
    # 최고 관리자
    super_admin = User(
        username='admin',
        email='admin@example.com',
        password_hash=generate_password_hash('admin123'),
        role='super_admin',
        grade='ceo',
        status='approved',
        name='시스템 관리자',
        phone='010-1234-5678'
    )
    db.session.add(super_admin)
    
    # 브랜드별 관리자들
    delicious_chicken = Brand.query.filter_by(code='delicious_chicken').first()
    if not delicious_chicken:
        print("❌ 맛있는 치킨 브랜드를 찾을 수 없습니다")
        return
    
    ch_branch = Branch.query.filter_by(store_code='CH001').first()
    if not ch_branch:
        print("❌ 치킨 강남점을 찾을 수 없습니다")
        return
    
    chicken_admin = User(
        username='chicken_admin',
        email='chicken_admin@example.com',
        password_hash=generate_password_hash('admin123'),
        role='admin',
        grade='director',
        status='approved',
        brand_id=delicious_chicken.id,
        industry_id=delicious_chicken.industry_id,
        branch_id=ch_branch.id,
        name='치킨 브랜드 관리자',
        phone='010-2345-6789'
    )
    db.session.add(chicken_admin)
    
    # 매장 관리자들
    ch_manager = User(
        username='ch_manager',
        email='ch_manager@example.com',
        password_hash=generate_password_hash('admin123'),
        role='manager',
        grade='manager',
        status='approved',
        brand_id=delicious_chicken.id,
        industry_id=delicious_chicken.industry_id,
        branch_id=ch_branch.id,
        name='치킨 강남점 매니저',
        phone='010-3456-7890'
    )
    db.session.add(ch_manager)
    
    # 직원들
    ch_employee = User(
        username='ch_employee',
        email='ch_employee@example.com',
        password_hash=generate_password_hash('admin123'),
        role='employee',
        grade='staff',
        status='approved',
        brand_id=delicious_chicken.id,
        industry_id=delicious_chicken.industry_id,
        branch_id=ch_branch.id,
        name='치킨 강남점 직원',
        phone='010-4567-8901'
    )
    db.session.add(ch_employee)
    
    db.session.commit()
    print("✅ 사용자 데이터 생성 완료")

def create_plugins():
    """플러그인 데이터 생성"""
    # 레스토랑 업종 플러그인
    restaurant_industry = Industry.query.filter_by(code='restaurant').first()
    if not restaurant_industry:
        print("❌ 레스토랑 업종을 찾을 수 없습니다")
        return
    
    restaurant_plugins = [
        {
            'industry_id': restaurant_industry.id,
            'name': '주문 관리',
            'code': 'order_management',
            'description': '레스토랑 주문 관리 시스템',
            'version': '1.0.0',
            'config': {
                'auto_confirm': True,
                'delivery_radius': 5,
                'max_wait_time': 30
            }
        },
        {
            'industry_id': restaurant_industry.id,
            'name': '재고 관리',
            'code': 'inventory_management',
            'description': '식재료 재고 관리 시스템',
            'version': '1.0.0',
            'config': {
                'auto_reorder': True,
                'min_stock_level': 10,
                'expiry_alert_days': 7
            }
        }
    ]
    
    # 병원 업종 플러그인
    hospital_industry = Industry.query.filter_by(code='hospital').first()
    if not hospital_industry:
        print("❌ 병원 업종을 찾을 수 없습니다")
        return
    
    hospital_plugins = [
        {
            'industry_id': hospital_industry.id,
            'name': '환자 관리',
            'code': 'patient_management',
            'description': '환자 정보 관리 시스템',
            'version': '1.0.0',
            'config': {
                'privacy_level': 'high',
                'backup_frequency': 'daily',
                'retention_period': 10
            }
        },
        {
            'industry_id': hospital_industry.id,
            'name': '예약 관리',
            'code': 'appointment_management',
            'description': '진료 예약 관리 시스템',
            'version': '1.0.0',
            'config': {
                'auto_reminder': True,
                'reminder_hours': 24,
                'max_appointments_per_day': 50
            }
        }
    ]
    
    all_plugins = restaurant_plugins + hospital_plugins
    
    for plugin_data in all_plugins:
        plugin = IndustryPlugin(**plugin_data)
        db.session.add(plugin)
    
    db.session.commit()
    print("✅ 플러그인 데이터 생성 완료")

def main():
    """메인 실행 함수"""
    with app.app_context():
        print("🚀 계층형 구조 기본 데이터 생성 시작...")
        db.create_all()  # 테이블이 없으면 생성
        try:
            # 기존 데이터 삭제 (순서 주의)
            print("🗑️ 기존 데이터 삭제 중...")
            User.query.delete()
            Branch.query.delete()
            Brand.query.delete()
            IndustryPlugin.query.delete()
            BrandPlugin.query.delete()
            Industry.query.delete()
            db.session.commit()
            
            # 새 데이터 생성
            create_industries()
            create_brands()
            create_branches()
            create_users()
            create_plugins()
            
            print("🎉 모든 데이터 생성 완료!")
            print("\n📋 생성된 데이터 요약:")
            print(f"  - 업종: {Industry.query.count()}개")
            print(f"  - 브랜드: {Brand.query.count()}개")
            print(f"  - 매장: {Branch.query.count()}개")
            print(f"  - 사용자: {User.query.count()}개")
            print(f"  - 플러그인: {IndustryPlugin.query.count()}개")
            
            print("\n🔑 로그인 정보:")
            print("  - 최고관리자: admin / admin123")
            print("  - 브랜드관리자: chicken_admin / admin123")
            print("  - 매장관리자: ch_manager / admin123")
            print("  - 직원: ch_employee / admin123")
            
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    main() 