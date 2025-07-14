#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
메뉴 자동 생성/통합 시스템
모듈 설치 시 메뉴를 자동으로 생성하고 권한/브랜드/매장별로 필터링
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import os

class MenuIntegrationSystem:
    def __init__(self, db_path: str = "menu_system.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 메뉴 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id TEXT NOT NULL,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                icon TEXT,
                parent_id INTEGER,
                order_index INTEGER DEFAULT 0,
                permission_level TEXT DEFAULT 'all',
                brand_id TEXT,
                store_id TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 메뉴 접근 통계 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                menu_id INTEGER,
                user_id TEXT,
                access_count INTEGER DEFAULT 0,
                last_access TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (menu_id) REFERENCES menus (id)
            )
        ''')
        
        # 모듈 설치 상태 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS module_installations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                brand_id TEXT,
                store_id TEXT,
                status TEXT DEFAULT 'installed',
                settings TEXT,
                onboarding_completed BOOLEAN DEFAULT 0,
                installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activated_at TIMESTAMP,
                configured_at TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_module_menus(self, module_id: str, module_info: Dict) -> List[Dict]:
        """모듈 설치 시 메뉴 자동 생성"""
        menus = []
        
        # 모듈별 기본 메뉴 구조 정의
        menu_structure = self.get_module_menu_structure(module_id, module_info)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for menu in menu_structure:
            cursor.execute('''
                INSERT INTO menus (module_id, name, url, icon, parent_id, order_index, permission_level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                module_id,
                menu['name'],
                menu['url'],
                menu.get('icon', ''),
                menu.get('parent_id'),
                menu.get('order_index', 0),
                menu.get('permission_level', 'all')
            ))
            menus.append(menu)
        
        conn.commit()
        conn.close()
        
        return menus
    
    def get_module_menu_structure(self, module_id: str, module_info: Dict) -> List[Dict]:
        """모듈별 메뉴 구조 반환"""
        base_menus = {
            'attendance': [
                {
                    'name': '출퇴근 관리',
                    'url': '/attendance',
                    'icon': 'clock',
                    'order_index': 1,
                    'permission_level': 'manager'
                },
                {
                    'name': '출근 기록',
                    'url': '/attendance/check-in',
                    'icon': 'login',
                    'parent_id': 1,
                    'order_index': 1,
                    'permission_level': 'all'
                },
                {
                    'name': '퇴근 기록',
                    'url': '/attendance/check-out',
                    'icon': 'logout',
                    'parent_id': 1,
                    'order_index': 2,
                    'permission_level': 'all'
                },
                {
                    'name': '근무 통계',
                    'url': '/attendance/stats',
                    'icon': 'chart',
                    'parent_id': 1,
                    'order_index': 3,
                    'permission_level': 'manager'
                }
            ],
            'schedule': [
                {
                    'name': '스케줄 관리',
                    'url': '/schedule',
                    'icon': 'calendar',
                    'order_index': 2,
                    'permission_level': 'manager'
                },
                {
                    'name': '월간 스케줄',
                    'url': '/schedule/monthly',
                    'icon': 'calendar-month',
                    'parent_id': 2,
                    'order_index': 1,
                    'permission_level': 'all'
                },
                {
                    'name': '주간 스케줄',
                    'url': '/schedule/weekly',
                    'icon': 'calendar-week',
                    'parent_id': 2,
                    'order_index': 2,
                    'permission_level': 'all'
                },
                {
                    'name': '휴가 신청',
                    'url': '/schedule/vacation',
                    'icon': 'vacation',
                    'parent_id': 2,
                    'order_index': 3,
                    'permission_level': 'all'
                }
            ],
            'inventory': [
                {
                    'name': '재고 관리',
                    'url': '/inventory',
                    'icon': 'box',
                    'order_index': 3,
                    'permission_level': 'manager'
                },
                {
                    'name': '재고 현황',
                    'url': '/inventory/status',
                    'icon': 'list',
                    'parent_id': 3,
                    'order_index': 1,
                    'permission_level': 'all'
                },
                {
                    'name': '입고 관리',
                    'url': '/inventory/inbound',
                    'icon': 'arrow-down',
                    'parent_id': 3,
                    'order_index': 2,
                    'permission_level': 'manager'
                },
                {
                    'name': '출고 관리',
                    'url': '/inventory/outbound',
                    'icon': 'arrow-up',
                    'parent_id': 3,
                    'order_index': 3,
                    'permission_level': 'manager'
                }
            ]
        }
        
        return base_menus.get(module_id, [])
    
    def get_user_menus(self, user_id: str, user_role: str, brand_id: Optional[str] = None, store_id: Optional[str] = None) -> List[Dict]:
        """사용자별 메뉴 반환 (권한/브랜드/매장 필터링)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 권한별 메뉴 조회
        cursor.execute('''
            SELECT id, module_id, name, url, icon, parent_id, order_index, permission_level
            FROM menus 
            WHERE is_active = 1 
            AND (permission_level = 'all' OR permission_level = ?)
            ORDER BY order_index
        ''', (user_role,))
        
        menus = []
        for row in cursor.fetchall():
            menu = {
                'id': row[0],
                'module_id': row[1],
                'name': row[2],
                'url': row[3],
                'icon': row[4],
                'parent_id': row[5],
                'order_index': row[6],
                'permission_level': row[7]
            }
            menus.append(menu)
        
        conn.close()
        
        # 계층 구조로 변환
        return self.build_menu_hierarchy(menus)
    
    def build_menu_hierarchy(self, menus: List[Dict]) -> List[Dict]:
        """메뉴를 계층 구조로 변환"""
        menu_dict = {menu['id']: menu for menu in menus}
        root_menus = []
        
        for menu in menus:
            if menu['parent_id'] is None:
                root_menus.append(menu)
            else:
                parent = menu_dict.get(menu['parent_id'])
                if parent:
                    if 'children' not in parent:
                        parent['children'] = []
                    parent['children'].append(menu)
        
        return root_menus
    
    def record_menu_access(self, menu_id: int, user_id: str):
        """메뉴 접근 기록"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 통계 확인
        cursor.execute('''
            SELECT id, access_count FROM menu_stats 
            WHERE menu_id = ? AND user_id = ?
        ''', (menu_id, user_id))
        
        existing = cursor.fetchone()
        if existing:
            # 기존 통계 업데이트
            cursor.execute('''
                UPDATE menu_stats 
                SET access_count = access_count + 1, last_access = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (existing[0],))
        else:
            # 새 통계 생성
            cursor.execute('''
                INSERT INTO menu_stats (menu_id, user_id, access_count, last_access)
                VALUES (?, ?, 1, CURRENT_TIMESTAMP)
            ''', (menu_id, user_id))
        
        conn.commit()
        conn.close()
    
    def get_menu_statistics(self) -> Dict:
        """메뉴 통계 반환"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 인기 메뉴 (접근 수 기준)
        cursor.execute('''
            SELECT m.name, ms.access_count, m.url
            FROM menu_stats ms
            JOIN menus m ON ms.menu_id = m.id
            ORDER BY ms.access_count DESC
            LIMIT 10
        ''')
        popular_menus = [{'name': row[0], 'access_count': row[1], 'url': row[2]} for row in cursor.fetchall()]
        
        # 최근 접근 메뉴
        cursor.execute('''
            SELECT m.name, ms.last_access, m.url
            FROM menu_stats ms
            JOIN menus m ON ms.menu_id = m.id
            ORDER BY ms.last_access DESC
            LIMIT 10
        ''')
        recent_menus = [{'name': row[0], 'last_access': row[1], 'url': row[2]} for row in cursor.fetchall()]
        
        # 비활성 메뉴
        cursor.execute('''
            SELECT name, url FROM menus 
            WHERE is_active = 0
        ''')
        inactive_menus = [{'name': row[0], 'url': row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'popular_menus': popular_menus,
            'recent_menus': recent_menus,
            'inactive_menus': inactive_menus
        }
    
    def install_module(self, module_id: str, user_id: str, module_info: Dict, 
                      brand_id: Optional[str] = None, store_id: Optional[str] = None) -> Dict:
        """모듈 설치 (4단계 플로우)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1단계: 설치
        cursor.execute('''
            INSERT INTO module_installations (module_id, user_id, brand_id, store_id, status)
            VALUES (?, ?, ?, ?, 'installed')
        ''', (module_id, user_id, brand_id, store_id))
        
        installation_id = cursor.lastrowid
        
        # 2단계: 메뉴 생성
        menus = self.create_module_menus(module_id, module_info)
        
        # 3단계: 활성화
        cursor.execute('''
            UPDATE module_installations 
            SET status = 'activated', activated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (installation_id,))
        
        conn.commit()
        conn.close()
        
        return {
            'installation_id': installation_id,
            'status': 'activated',
            'menus_created': len(menus),
            'next_step': 'configuration'
        }
    
    def configure_module(self, installation_id: int, settings: Dict) -> Dict:
        """모듈 설정"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE module_installations 
            SET status = 'configured', settings = ?, configured_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (json.dumps(settings), installation_id))
        
        conn.commit()
        conn.close()
        
        return {'status': 'configured', 'next_step': 'onboarding'}
    
    def complete_onboarding(self, installation_id: int) -> Dict:
        """온보딩 완료"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE module_installations 
            SET status = 'completed', onboarding_completed = 1
            WHERE id = ?
        ''', (installation_id,))
        
        conn.commit()
        conn.close()
        
        return {'status': 'completed'}
    
    def uninstall_module(self, module_id: str, user_id: str) -> Dict:
        """모듈 제거"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 메뉴 비활성화
        cursor.execute('''
            UPDATE menus SET is_active = 0 WHERE module_id = ?
        ''', (module_id,))
        
        # 설치 기록 삭제
        cursor.execute('''
            DELETE FROM module_installations 
            WHERE module_id = ? AND user_id = ?
        ''', (module_id, user_id))
        
        conn.commit()
        conn.close()
        
        return {'status': 'uninstalled'}

# 전역 인스턴스
menu_system = MenuIntegrationSystem() 