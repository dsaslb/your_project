#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
플러그인 관리 시스템 데이터베이스 초기화 스크립트
"""

import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models_main import (
    PluginActivation, PluginPermission, PluginHierarchy, PluginTestResult,
    User, Brand, Branch
)

def init_plugin_management_tables():
    """플러그인 관리 테이블 초기화"""
    try:
        with app.app_context():
            print("플러그인 관리 테이블 생성 중...")
            
            # 테이블 생성
            db.create_all()
            
            print("✅ 플러그인 관리 테이블 생성 완료")
            
            # 샘플 데이터 생성 (선택사항)
            create_sample_data()
            
            print("✅ 플러그인 관리 시스템 초기화 완료")
            
    except Exception as e:
        print(f"❌ 플러그인 관리 테이블 생성 실패: {e}")
        return False
    
    return True

def create_sample_data():
    """샘플 데이터 생성"""
    try:
        # 관리자 사용자 확인
        admin_user = User.query.filter_by(role='admin').first()
        if not admin_user:
            print("⚠️  관리자 사용자가 없습니다. 샘플 데이터 생성을 건너뜁니다.")
            return
        
        # 브랜드 확인
        brand = Brand.query.first()
        if not brand:
            print("⚠️  브랜드가 없습니다. 샘플 데이터 생성을 건너뜁니다.")
            return
        
        # 매장 확인
        store = Branch.query.first()
        if not store:
            print("⚠️  매장이 없습니다. 샘플 데이터 생성을 건너뜁니다.")
            return
        
        print("샘플 플러그인 활성화 데이터 생성 중...")
        
        # 출근관리 플러그인 활성화 (브랜드 레벨)
        attendance_activation = PluginActivation.query.filter_by(
            plugin_id='attendance_management',
            target_type='brand',
            target_id=brand.id
        ).first()
        
        if not attendance_activation:
            attendance_activation = PluginActivation(
                plugin_id='attendance_management',
                target_type='brand',
                target_id=brand.id,
                is_active=True,
                activation_date=db.func.now(),
                activated_by=admin_user.id,
                settings={
                    'work_start_time': '09:00',
                    'work_end_time': '18:00',
                    'break_time': 60,
                    'overtime_threshold': 8.0
                },
                version='1.0.0'
            )
            db.session.add(attendance_activation)
        
        # 재고관리 플러그인 활성화 (매장 레벨)
        inventory_activation = PluginActivation.query.filter_by(
            plugin_id='inventory_management',
            target_type='store',
            target_id=store.id
        ).first()
        
        if not inventory_activation:
            inventory_activation = PluginActivation(
                plugin_id='inventory_management',
                target_type='store',
                target_id=store.id,
                is_active=True,
                activation_date=db.func.now(),
                activated_by=admin_user.id,
                settings={
                    'low_stock_threshold': 10,
                    'auto_reorder_enabled': True,
                    'stock_alert_email': True
                },
                version='1.0.0'
            )
            db.session.add(inventory_activation)
        
        # 권한 설정 샘플 데이터
        print("샘플 플러그인 권한 데이터 생성 중...")
        
        # 브랜드 관리자 권한 (출근관리)
        brand_admin_permission = PluginPermission.query.filter_by(
            plugin_id='attendance_management',
            target_type='brand',
            target_id=brand.id,
            role='brand_admin'
        ).first()
        
        if not brand_admin_permission:
            brand_admin_permission = PluginPermission(
                plugin_id='attendance_management',
                target_type='brand',
                target_id=brand.id,
                role='brand_admin',
                permissions={
                    'view': True,
                    'create': True,
                    'edit': True,
                    'delete': False,
                    'approve': True
                },
                is_inherited=False,
                created_by=admin_user.id
            )
            db.session.add(brand_admin_permission)
        
        # 매장 관리자 권한 (재고관리)
        store_admin_permission = PluginPermission.query.filter_by(
            plugin_id='inventory_management',
            target_type='store',
            target_id=store.id,
            role='store_admin'
        ).first()
        
        if not store_admin_permission:
            store_admin_permission = PluginPermission(
                plugin_id='inventory_management',
                target_type='store',
                target_id=store.id,
                role='store_admin',
                permissions={
                    'view': True,
                    'create': True,
                    'edit': True,
                    'delete': True,
                    'approve': True
                },
                is_inherited=False,
                created_by=admin_user.id
            )
            db.session.add(store_admin_permission)
        
        # 계층 구조 샘플 데이터
        print("샘플 플러그인 계층 구조 데이터 생성 중...")
        
        # 브랜드 -> 매장 계층 구조
        hierarchy = PluginHierarchy.query.filter_by(
            plugin_id='attendance_management',
            parent_type='brand',
            parent_id=brand.id,
            child_type='store',
            child_id=store.id
        ).first()
        
        if not hierarchy:
            hierarchy = PluginHierarchy(
                plugin_id='attendance_management',
                parent_type='brand',
                parent_id=brand.id,
                child_type='store',
                child_id=store.id,
                inheritance_type='full',
                inheritance_settings={
                    'inherit_activation': True,
                    'inherit_permissions': True,
                    'override_settings': False
                }
            )
            db.session.add(hierarchy)
        
        db.session.commit()
        print("✅ 샘플 데이터 생성 완료")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 샘플 데이터 생성 실패: {e}")

if __name__ == "__main__":
    print("플러그인 관리 시스템 초기화 시작...")
    success = init_plugin_management_tables()
    
    if success:
        print("\n🎉 플러그인 관리 시스템이 성공적으로 초기화되었습니다!")
        print("\n사용 가능한 API 엔드포인트:")
        print("- GET  /api/plugin-management/plugins")
        print("- GET  /api/plugin-management/activation")
        print("- POST /api/plugin-management/activation")
        print("- GET  /api/plugin-management/permissions")
        print("- POST /api/plugin-management/permissions")
        print("- GET  /api/plugin-management/hierarchy")
        print("- POST /api/plugin-management/hierarchy")
        print("- POST /api/plugin-management/test")
        print("- GET  /api/plugin-management/test-results")
        print("- POST /api/plugin-management/bulk-activate")
        print("- GET  /api/plugin-management/status")
    else:
        print("\n❌ 플러그인 관리 시스템 초기화에 실패했습니다.")
        sys.exit(1) 