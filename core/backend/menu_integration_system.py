#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class MenuIntegrationSystem:
    """메뉴 통합 시스템"""
    
    def __init__(self):
        self.menus = {}
        self.categories = {}
        self.integrations = {}
        
    def add_menu(self, menu_id: str, menu_data: Dict[str, Any]) -> bool:
        """메뉴 추가"""
        try:
            self.menus[menu_id] = {
                'id': menu_id,
                'name': menu_data.get('name', ''),
                'description': menu_data.get('description', ''),
                'category': menu_data.get('category', ''),
                'price': menu_data.get('price', 0),
                'available': menu_data.get('available', True),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            logger.info(f"메뉴 추가됨: {menu_id}")
            return True
        except Exception as e:
            logger.error(f"메뉴 추가 실패: {e}")
            return False
    
    def get_menu(self, menu_id: str) -> Optional[Dict[str, Any]]:
        """메뉴 조회"""
        return self.menus.get(menu_id)
    
    def get_all_menus(self) -> List[Dict[str, Any]]:
        """모든 메뉴 조회"""
        return list(self.menus.values())
    
    def update_menu(self, menu_id: str, menu_data: Dict[str, Any]) -> bool:
        """메뉴 업데이트"""
        try:
            if menu_id in self.menus:
                self.menus[menu_id].update(menu_data)
                self.menus[menu_id]['updated_at'] = datetime.utcnow()
                logger.info(f"메뉴 업데이트됨: {menu_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"메뉴 업데이트 실패: {e}")
            return False
    
    def delete_menu(self, menu_id: str) -> bool:
        """메뉴 삭제"""
        try:
            if menu_id in self.menus:
                del self.menus[menu_id]
                logger.info(f"메뉴 삭제됨: {menu_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"메뉴 삭제 실패: {e}")
            return False
    
    def get_menus_by_category(self, category: str) -> List[Dict[str, Any]]:
        """카테고리별 메뉴 조회"""
        return [menu for menu in self.menus.values() if menu.get('category') == category]
    
    def search_menus(self, query: str) -> List[Dict[str, Any]]:
        """메뉴 검색"""
        query = query.lower()
        return [
            menu for menu in self.menus.values()
            if query in menu.get('name', '').lower() or query in menu.get('description', '').lower()
        ]

# 전역 인스턴스
menu_integration_system = MenuIntegrationSystem()

# --- [자동화] 브랜드별 관리자 권한/메뉴/기본 데이터 자동 생성 함수 예시 ---
def assign_brand_admin_and_menu(brand):
    """
    신규 브랜드 생성 시 관리자 권한/메뉴/기본 데이터 자동 생성
    - 브랜드 관리자 계정 자동 생성 (예: brand_admin@brand.com)
    - 브랜드별 메뉴/권한 등록
    - 브랜드별 기본 샘플 데이터(매장/직원/매출/개선요청 등) 생성
    """
    from models_main import User, Branch, Staff, db
    import random, string
    # 1. 브랜드 관리자 계정 자동 생성 (이메일 중복 방지)
    admin_email = f"admin_{brand.id}@brand.com"
    if not User.query.filter_by(email=admin_email).first():
        admin_user = User(
            username=f"brand_admin_{brand.id}",
            email=admin_email,
            name=f"{brand.name} 관리자",
            role="brand_admin",
            brand_id=brand.id,
            status="approved"
        )
        admin_user.set_password('admin1234!')  # 초기 비밀번호
        db.session.add(admin_user)
        db.session.commit()
        brand.admin_id = admin_user.id
        db.session.commit()
    # 2. 브랜드별 메뉴/권한 등록 (예시: DB에 메뉴/권한 테이블이 있다면 추가)
    # (실제 메뉴/권한 테이블 구조에 맞게 구현 필요)
    # 3. 브랜드별 기본 샘플 데이터 생성 (매장/직원/매출/개선요청 등)
    if not Branch.query.filter_by(brand_id=brand.id).first():
        branch = Branch(
            name=f"{brand.name} 1호점",
            brand_id=brand.id,
            address="서울시 강남구 ...",
            phone="02-0000-0000",
            status="active"
        )
        db.session.add(branch)
        db.session.commit()
        # 샘플 직원
        staff = User(
            name="홍길동",
            branch_id=branch.id,
            role="manager",
            status="approved",
            email=f"staff_{brand.id}@brand.com",
            username=f"staff_{brand.id}",
            password_hash="",
        )
        staff.set_password('staff1234!')
        db.session.add(staff)
        db.session.commit()
    # (필요시 매출/개선요청 등 샘플 데이터 추가)
    # --- END ---
