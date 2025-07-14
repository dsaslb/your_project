"""
모듈 설치 및 활성화 시스템
브랜드/매장별 모듈 설치, 활성화, 설정을 관리하는 시스템
"""

import json
import logging
import os
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import sqlite3
import threading

from core.backend.central_data_layer import central_data
from core.backend.integrated_module_system import integrated_system, IntegrationEvent, IntegrationEventData

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModuleInstallationSystem:
    """모듈 설치 및 활성화 시스템"""
    
    def __init__(self):
        self.installations_db_path = Path("data/module_installations.db")
        self.installations_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self._init_installations_database()
    
    def _init_installations_database(self):
        """설치 데이터베이스 초기화"""
        try:
            with sqlite3.connect(self.installations_db_path) as conn:
                cursor = conn.cursor()
                
                # 모듈 설치 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS module_installations (
                        id INTEGER PRIMARY KEY,
                        module_id TEXT NOT NULL,
                        module_name TEXT NOT NULL,
                        version TEXT NOT NULL,
                        installed_by INTEGER NOT NULL,
                        installed_for_type TEXT NOT NULL, -- 'brand', 'branch', 'system'
                        installed_for_id INTEGER NOT NULL,
                        status TEXT DEFAULT 'installed', -- 'installed', 'activated', 'deactivated', 'error'
                        settings JSON,
                        permissions JSON,
                        menu_config JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        activated_at TIMESTAMP,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (installed_by) REFERENCES users (id)
                    )
                ''')
                
                # 모듈 사용 통계 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS module_usage_stats (
                        id INTEGER PRIMARY KEY,
                        installation_id INTEGER,
                        module_id TEXT NOT NULL,
                        user_id INTEGER,
                        action TEXT NOT NULL,
                        data JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (installation_id) REFERENCES module_installations (id)
                    )
                ''')
                
                # 모듈 설정 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS module_settings (
                        id INTEGER PRIMARY KEY,
                        installation_id INTEGER,
                        setting_key TEXT NOT NULL,
                        setting_value TEXT,
                        setting_type TEXT DEFAULT 'string',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (installation_id) REFERENCES module_installations (id)
                    )
                ''')
                
                # 모듈 권한 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS module_permissions (
                        id INTEGER PRIMARY KEY,
                        installation_id INTEGER,
                        role TEXT NOT NULL,
                        permissions JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (installation_id) REFERENCES module_installations (id)
                    )
                ''')
                
                conn.commit()
                logger.info("모듈 설치 데이터베이스 초기화 완료")
                
        except Exception as e:
            logger.error(f"모듈 설치 데이터베이스 초기화 실패: {e}")
    
    def install_module(self, module_id: str, installed_by: int, 
                      installed_for_type: str, installed_for_id: int) -> Dict[str, Any]:
        """모듈 설치"""
        try:
            with self.lock:
                # 마켓플레이스에서 모듈 정보 조회
                with open('marketplace/modules.json', 'r', encoding='utf-8') as f:
                    modules = json.load(f)
                
                if module_id not in modules:
                    raise ValueError(f"모듈 {module_id}를 찾을 수 없습니다.")
                
                module_info = modules[module_id]
                
                # 이미 설치되어 있는지 확인
                existing_installation = self.get_installation(module_id, installed_for_type, installed_for_id)
                if existing_installation:
                    raise ValueError(f"모듈 {module_id}가 이미 설치되어 있습니다.")
                
                # 의존성 확인
                dependencies = module_info.get('dependencies', [])
                for dep in dependencies:
                    dep_installation = self.get_installation(dep, installed_for_type, installed_for_id)
                    if not dep_installation or dep_installation['status'] != 'activated':
                        raise ValueError(f"의존 모듈 {dep}가 설치되지 않았거나 활성화되지 않았습니다.")
                
                # 설치 정보 저장
                with sqlite3.connect(self.installations_db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        INSERT INTO module_installations 
                        (module_id, module_name, version, installed_by, installed_for_type, 
                         installed_for_id, status, settings, permissions, menu_config)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        module_id,
                        module_info['name'],
                        module_info['version'],
                        installed_by,
                        installed_for_type,
                        installed_for_id,
                        'installed',
                        json.dumps(module_info.get('default_settings', {})),
                        json.dumps(module_info.get('permissions', [])),
                        json.dumps(module_info.get('menu_config', {}))
                    ))
                    
                    installation_id = cursor.lastrowid
                    
                    # 기본 권한 설정
                    hierarchy_levels = module_info.get('hierarchy_levels', {})
                    for role, permissions in hierarchy_levels.items():
                        cursor.execute("""
                            INSERT INTO module_permissions (installation_id, role, permissions)
                            VALUES (?, ?, ?)
                        """, (installation_id, role, json.dumps(permissions)))
                    
                    conn.commit()
                
                # 설치 완료 이벤트 발생
                self._emit_installation_event(module_id, 'installed', installed_by, installed_for_type, installed_for_id)
                
                logger.info(f"모듈 {module_id} 설치 완료: {installed_for_type} {installed_for_id}")
                
                return {
                    "success": True,
                    "installation_id": installation_id,
                    "module_info": module_info,
                    "message": f"모듈 {module_info['name']}이(가) 성공적으로 설치되었습니다."
                }
                
        except Exception as e:
            logger.error(f"모듈 설치 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def activate_module(self, module_id: str, installed_for_type: str, 
                       installed_for_id: int, activated_by: int) -> Dict[str, Any]:
        """모듈 활성화"""
        try:
            with self.lock:
                installation = self.get_installation(module_id, installed_for_type, installed_for_id)
                if not installation:
                    raise ValueError(f"모듈 {module_id}가 설치되지 않았습니다.")
                
                if installation['status'] == 'activated':
                    raise ValueError(f"모듈 {module_id}가 이미 활성화되어 있습니다.")
                
                # 활성화 처리
                with sqlite3.connect(self.installations_db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE module_installations 
                        SET status = 'activated', activated_at = CURRENT_TIMESTAMP
                        WHERE module_id = ? AND installed_for_type = ? AND installed_for_id = ?
                    """, (module_id, installed_for_type, installed_for_id))
                    conn.commit()
                
                # 중앙 데이터 레이어에 모듈 등록
                self._register_module_to_central_data(module_id, installed_for_type, installed_for_id)
                
                # 통합 연동 시스템에 모듈 등록
                self._register_module_to_integration_system(module_id, installed_for_type, installed_for_id)
                
                # 모듈 메뉴 자동 추가
                self._add_module_menus(module_id, installed_for_type, installed_for_id)
                
                # 활성화 완료 이벤트 발생
                self._emit_installation_event(module_id, 'activated', activated_by, installed_for_type, installed_for_id)
                
                logger.info(f"모듈 {module_id} 활성화 완료: {installed_for_type} {installed_for_id}")
                
                return {
                    "success": True,
                    "message": f"모듈 {installation['module_name']}이(가) 성공적으로 활성화되었습니다."
                }
                
        except Exception as e:
            logger.error(f"모듈 활성화 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def deactivate_module(self, module_id: str, installed_for_type: str, 
                         installed_for_id: int, deactivated_by: int) -> Dict[str, Any]:
        """모듈 비활성화"""
        try:
            with self.lock:
                installation = self.get_installation(module_id, installed_for_type, installed_for_id)
                if not installation:
                    raise ValueError(f"모듈 {module_id}가 설치되지 않았습니다.")
                
                if installation['status'] != 'activated':
                    raise ValueError(f"모듈 {module_id}가 활성화되지 않았습니다.")
                
                # 비활성화 처리
                with sqlite3.connect(self.installations_db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE module_installations 
                        SET status = 'deactivated'
                        WHERE module_id = ? AND installed_for_type = ? AND installed_for_id = ?
                    """, (module_id, installed_for_type, installed_for_id))
                    conn.commit()
                
                # 비활성화 완료 이벤트 발생
                self._emit_installation_event(module_id, 'deactivated', deactivated_by, installed_for_type, installed_for_id)
                
                logger.info(f"모듈 {module_id} 비활성화 완료: {installed_for_type} {installed_for_id}")
                
                return {
                    "success": True,
                    "message": f"모듈 {installation['module_name']}이(가) 비활성화되었습니다."
                }
                
        except Exception as e:
            logger.error(f"모듈 비활성화 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def uninstall_module(self, module_id: str, installed_for_type: str, 
                        installed_for_id: int, uninstalled_by: int) -> Dict[str, Any]:
        """모듈 제거"""
        try:
            with self.lock:
                installation = self.get_installation(module_id, installed_for_type, installed_for_id)
                if not installation:
                    raise ValueError(f"모듈 {module_id}가 설치되지 않았습니다.")
                
                # 의존하는 모듈이 있는지 확인
                dependent_modules = self.get_dependent_modules(module_id, installed_for_type, installed_for_id)
                if dependent_modules:
                    raise ValueError(f"이 모듈에 의존하는 모듈이 있습니다: {', '.join(dependent_modules)}")
                
                # 모듈 메뉴 자동 제거
                self._remove_module_menus(module_id, installed_for_type, installed_for_id)
                
                # 제거 처리
                with sqlite3.connect(self.installations_db_path) as conn:
                    cursor = conn.cursor()
                    
                    # 관련 데이터 삭제
                    cursor.execute("DELETE FROM module_usage_stats WHERE installation_id = ?", (installation['id'],))
                    cursor.execute("DELETE FROM module_settings WHERE installation_id = ?", (installation['id'],))
                    cursor.execute("DELETE FROM module_permissions WHERE installation_id = ?", (installation['id'],))
                    cursor.execute("DELETE FROM module_installations WHERE id = ?", (installation['id'],))
                    
                    conn.commit()
                
                # 제거 완료 이벤트 발생
                self._emit_installation_event(module_id, 'uninstalled', uninstalled_by, installed_for_type, installed_for_id)
                
                logger.info(f"모듈 {module_id} 제거 완료: {installed_for_type} {installed_for_id}")
                
                return {
                    "success": True,
                    "message": f"모듈 {installation['module_name']}이(가) 제거되었습니다."
                }
                
        except Exception as e:
            logger.error(f"모듈 제거 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_installation(self, module_id: str, installed_for_type: str, 
                        installed_for_id: int) -> Optional[Dict[str, Any]]:
        """설치 정보 조회"""
        try:
            with sqlite3.connect(self.installations_db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM module_installations 
                    WHERE module_id = ? AND installed_for_type = ? AND installed_for_id = ?
                """, (module_id, installed_for_type, installed_for_id))
                
                result = cursor.fetchone()
                if result:
                    return dict(result)
                return None
                
        except Exception as e:
            logger.error(f"설치 정보 조회 실패: {e}")
            return None
    
    def get_installations(self, installed_for_type: str = None, 
                         installed_for_id: int = None) -> List[Dict[str, Any]]:
        """설치 목록 조회"""
        try:
            with sqlite3.connect(self.installations_db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT * FROM module_installations WHERE 1=1"
                params = []
                
                if installed_for_type:
                    query += " AND installed_for_type = ?"
                    params.append(installed_for_type)
                
                if installed_for_id:
                    query += " AND installed_for_id = ?"
                    params.append(installed_for_id)
                
                query += " ORDER BY created_at DESC"
                
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"설치 목록 조회 실패: {e}")
            return []
    
    def get_activated_modules(self, installed_for_type: str, installed_for_id: int) -> List[Dict[str, Any]]:
        """활성화된 모듈 목록 조회"""
        try:
            with sqlite3.connect(self.installations_db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM module_installations 
                    WHERE installed_for_type = ? AND installed_for_id = ? AND status = 'activated'
                    ORDER BY activated_at DESC
                """, (installed_for_type, installed_for_id))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"활성화된 모듈 목록 조회 실패: {e}")
            return []
    
    def update_module_settings(self, module_id: str, installed_for_type: str, 
                              installed_for_id: int, settings: Dict[str, Any]) -> Dict[str, Any]:
        """모듈 설정 업데이트"""
        try:
            with self.lock:
                installation = self.get_installation(module_id, installed_for_type, installed_for_id)
                if not installation:
                    raise ValueError(f"모듈 {module_id}가 설치되지 않았습니다.")
                
                with sqlite3.connect(self.installations_db_path) as conn:
                    cursor = conn.cursor()
                    
                    # 기존 설정 삭제
                    cursor.execute("DELETE FROM module_settings WHERE installation_id = ?", (installation['id'],))
                    
                    # 새 설정 저장
                    for key, value in settings.items():
                        cursor.execute("""
                            INSERT INTO module_settings (installation_id, setting_key, setting_value, setting_type)
                            VALUES (?, ?, ?, ?)
                        """, (installation['id'], key, str(value), type(value).__name__))
                    
                    # 설치 정보 업데이트
                    cursor.execute("""
                        UPDATE module_installations 
                        SET settings = ?, last_updated = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (json.dumps(settings), installation['id']))
                    
                    conn.commit()
                
                logger.info(f"모듈 {module_id} 설정 업데이트 완료")
                
                return {
                    "success": True,
                    "message": "모듈 설정이 업데이트되었습니다."
                }
                
        except Exception as e:
            logger.error(f"모듈 설정 업데이트 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_module_settings(self, module_id: str, installed_for_type: str, 
                           installed_for_id: int) -> Dict[str, Any]:
        """모듈 설정 조회"""
        try:
            installation = self.get_installation(module_id, installed_for_type, installed_for_id)
            if not installation:
                return {}
            
            with sqlite3.connect(self.installations_db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT setting_key, setting_value, setting_type 
                    FROM module_settings 
                    WHERE installation_id = ?
                """, (installation['id'],))
                
                settings = {}
                for row in cursor.fetchall():
                    key, value, value_type = row
                    
                    # 타입 변환
                    if value_type == 'int':
                        settings[key] = int(value)
                    elif value_type == 'float':
                        settings[key] = float(value)
                    elif value_type == 'bool':
                        settings[key] = value.lower() == 'true'
                    elif value_type == 'list' or value_type == 'dict':
                        try:
                            settings[key] = json.loads(value)
                        except:
                            settings[key] = value
                    else:
                        settings[key] = value
                
                return settings
                
        except Exception as e:
            logger.error(f"모듈 설정 조회 실패: {e}")
            return {}
    
    def get_dependent_modules(self, module_id: str, installed_for_type: str, 
                             installed_for_id: int) -> List[str]:
        """의존하는 모듈 목록 조회"""
        try:
            installations = self.get_installations(installed_for_type, installed_for_id)
            dependent_modules = []
            
            for installation in installations:
                if installation['status'] == 'activated':
                    # 마켓플레이스에서 의존성 확인
                    with open('marketplace/modules.json', 'r', encoding='utf-8') as f:
                        modules = json.load(f)
                    
                    if installation['module_id'] in modules:
                        dependencies = modules[installation['module_id']].get('dependencies', [])
                        if module_id in dependencies:
                            dependent_modules.append(installation['module_id'])
            
            return dependent_modules
            
        except Exception as e:
            logger.error(f"의존 모듈 조회 실패: {e}")
            return []
    
    def get_installation_statistics(self, installed_for_type: str | None = None, 
                                   installed_for_id: int | None = None) -> Dict[str, Any]:
        """설치 통계 조회"""
        try:
            with sqlite3.connect(self.installations_db_path) as conn:
                cursor = conn.cursor()
                
                query = "SELECT status, COUNT(*) as count FROM module_installations WHERE 1=1"
                params = []
                
                if installed_for_type:
                    query += " AND installed_for_type = ?"
                    params.append(installed_for_type)
                
                if installed_for_id:
                    query += " AND installed_for_id = ?"
                    params.append(installed_for_id)
                
                query += " GROUP BY status"
                
                cursor.execute(query, params)
                
                # 기본 통계 초기화
                total_installed = 0
                active_modules = 0
                inactive_modules = 0
                
                for row in cursor.fetchall():
                    status, count = row
                    total_installed += count
                    if status == 'activated':
                        active_modules = count
                    elif status == 'deactivated':
                        inactive_modules = count
                
                # 마켓플레이스에서 추가 통계 정보 가져오기
                total_downloads = 0
                total_rating = 0
                rating_count = 0
                
                try:
                    with open('marketplace/modules.json', 'r', encoding='utf-8') as f:
                        modules = json.load(f)
                    
                    for module_id, module_info in modules.items():
                        total_downloads += module_info.get('downloads', 0)
                        if 'rating' in module_info:
                            total_rating += module_info['rating']
                            rating_count += 1
                    
                    average_rating = total_rating / rating_count if rating_count > 0 else 0
                except Exception as e:
                    logger.warning(f"마켓플레이스 통계 로드 실패: {e}")
                    average_rating = 0
                
                # 프론트엔드가 기대하는 구조로 반환
                return {
                    'total_installed': total_installed,
                    'active_modules': active_modules,
                    'inactive_modules': inactive_modules,
                    'total_downloads': total_downloads,
                    'average_rating': average_rating
                }
                
        except Exception as e:
            logger.error(f"설치 통계 조회 실패: {e}")
            return {
                'total_installed': 0,
                'active_modules': 0,
                'inactive_modules': 0,
                'total_downloads': 0,
                'average_rating': 0
            }
    
    def _register_module_to_central_data(self, module_id: str, installed_for_type: str, installed_for_id: int):
        """중앙 데이터 레이어에 모듈 등록"""
        try:
            # 모듈별 초기 데이터 생성
            if module_id == 'attendance_management':
                self._create_attendance_sample_data(installed_for_type, installed_for_id)
            elif module_id == 'sales_management':
                self._create_sales_sample_data(installed_for_type, installed_for_id)
            elif module_id == 'payroll_management':
                self._create_payroll_sample_data(installed_for_type, installed_for_id)
            
            logger.info(f"모듈 {module_id} 중앙 데이터 레이어 등록 완료")
            
        except Exception as e:
            logger.error(f"중앙 데이터 레이어 등록 실패: {e}")
    
    def _register_module_to_integration_system(self, module_id: str, installed_for_type: str, installed_for_id: int):
        """통합 연동 시스템에 모듈 등록"""
        try:
            # 모듈을 통합 시스템에 등록
            if hasattr(integrated_system, 'module_registry'):
                integrated_system.module_registry[module_id] = {
                    "name": f"{module_id} ({installed_for_type} {installed_for_id})",
                    "type": "custom",
                    "version": "1.0.0",
                    "dependencies": [],
                    "integrations": ["central_data", "analytics", "notifications"]
                }
            
            logger.info(f"모듈 {module_id} 통합 연동 시스템 등록 완료")
            
        except Exception as e:
            logger.error(f"통합 연동 시스템 등록 실패: {e}")
    
    def _add_module_menus(self, module_id: str, installed_for_type: str, installed_for_id: int):
        """모듈 메뉴 자동 추가"""
        try:
            from core.backend.menu_integration_system import menu_integration_system
            
            result = menu_integration_system.add_module_menus(
                module_id, installed_for_type, installed_for_id
            )
            
            if result['success']:
                logger.info(f"모듈 {module_id} 메뉴 추가 완료")
            else:
                logger.error(f"모듈 {module_id} 메뉴 추가 실패: {result['error']}")
                
        except Exception as e:
            logger.error(f"모듈 메뉴 추가 실패: {e}")
    
    def _remove_module_menus(self, module_id: str, installed_for_type: str, installed_for_id: int):
        """모듈 메뉴 자동 제거"""
        try:
            from core.backend.menu_integration_system import menu_integration_system
            
            result = menu_integration_system.remove_module_menus(
                module_id, installed_for_type, installed_for_id
            )
            
            if result['success']:
                logger.info(f"모듈 {module_id} 메뉴 제거 완료")
            else:
                logger.error(f"모듈 {module_id} 메뉴 제거 실패: {result['error']}")
                
        except Exception as e:
            logger.error(f"모듈 메뉴 제거 실패: {e}")
    
    def _create_attendance_sample_data(self, installed_for_type: str, installed_for_id: int):
        """출퇴근 샘플 데이터 생성"""
        # 중앙 데이터 레이어에 샘플 데이터 추가
        pass
    
    def _create_sales_sample_data(self, installed_for_type: str, installed_for_id: int):
        """매출 샘플 데이터 생성"""
        # 중앙 데이터 레이어에 샘플 데이터 추가
        pass
    
    def _create_payroll_sample_data(self, installed_for_type: str, installed_for_id: int):
        """급여 샘플 데이터 생성"""
        # 중앙 데이터 레이어에 샘플 데이터 추가
        pass
    
    def _emit_installation_event(self, module_id: str, event_type: str, user_id: int, 
                                installed_for_type: str, installed_for_id: int):
        """설치 이벤트 발생"""
        try:
            event_data = IntegrationEventData(
                event_type=IntegrationEvent.ANALYTICS_GENERATED,  # 임시로 사용
                module_id=f"{module_id}_{event_type}",
                data={
                    "module_id": module_id,
                    "event_type": event_type,
                    "installed_for_type": installed_for_type,
                    "installed_for_id": installed_for_id,
                    "user_id": user_id
                },
                timestamp=datetime.now(),
                user_id=user_id
            )
            
            integrated_system.emit_event(event_data)
            
        except Exception as e:
            logger.error(f"설치 이벤트 발생 실패: {e}")

# 전역 인스턴스
module_installation_system = ModuleInstallationSystem() 