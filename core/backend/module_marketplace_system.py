"""
모듈 마켓플레이스 연동 시스템
업종별/브랜드별/매장별 관리자가 모듈을 자유롭게 적용/비활성화/설정할 수 있는 시스템
"""

import os
import json
import shutil
import zipfile
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging
from enum import Enum

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModuleStatus(Enum):
    """모듈 상태"""
    AVAILABLE = "available"      # 마켓플레이스에서 사용 가능
    INSTALLED = "installed"      # 설치됨
    ACTIVATED = "activated"      # 활성화됨
    DEACTIVATED = "deactivated"  # 비활성화됨
    UPDATING = "updating"        # 업데이트 중
    ERROR = "error"              # 오류 상태

class ModuleScope(Enum):
    """모듈 적용 범위"""
    SYSTEM = "system"           # 시스템 전체
    INDUSTRY = "industry"       # 업종별
    BRAND = "brand"            # 브랜드별
    BRANCH = "branch"          # 매장별
    USER = "user"              # 사용자별

class ModuleMarketplaceSystem:
    """모듈 마켓플레이스 연동 시스템"""
    
    def __init__(self, marketplace_dir: str = "marketplace", 
                 modules_dir: str = "plugins", 
                 db_session=None):
        self.marketplace_dir = Path(marketplace_dir)
        self.modules_dir = Path(modules_dir)
        self.db_session = db_session
        
        # 디렉토리 생성
        self.marketplace_dir.mkdir(parents=True, exist_ok=True)
        self.modules_dir.mkdir(parents=True, exist_ok=True)
        
        # 하위 디렉토리 생성
        (self.marketplace_dir / "modules").mkdir(exist_ok=True)
        (self.marketplace_dir / "installed").mkdir(exist_ok=True)
        (self.marketplace_dir / "configs").mkdir(exist_ok=True)
        (self.marketplace_dir / "backups").mkdir(exist_ok=True)
        
        # 데이터 파일 경로
        self.modules_file = self.marketplace_dir / "modules.json"
        self.installed_file = self.marketplace_dir / "installed.json"
        self.configs_file = self.marketplace_dir / "configs.json"
        
        # 초기화
        self._init_marketplace()
        
    def _init_marketplace(self):
        """마켓플레이스 초기화"""
        # 모듈 목록 초기화
        if not self.modules_file.exists():
            self._create_sample_modules()
        
        # 설치된 모듈 목록 초기화
        if not self.installed_file.exists():
            with open(self.installed_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=2, ensure_ascii=False)
        
        # 모듈 설정 초기화
        if not self.configs_file.exists():
            with open(self.configs_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=2, ensure_ascii=False)
    
    def _create_sample_modules(self):
        """샘플 모듈 생성"""
        sample_modules = {
            "attendance_management": {
                "id": "attendance_management",
                "name": "출퇴근 관리",
                "version": "1.0.0",
                "description": "직원 출퇴근 관리, 지각/초과근무 통계, 급여 연동",
                "author": "Your Program Team",
                "category": "hr",
                "tags": ["출퇴근", "인사", "급여", "통계"],
                "price": 0.0,
                "currency": "KRW",
                "scope": ModuleScope.BRANCH.value,
                "dependencies": [],
                "permissions": ["attendance_management"],
                "features": [
                    "직원별 출퇴근 기록",
                    "지각/초과근무 통계",
                    "급여 시스템 연동",
                    "AI 기반 근무 패턴 분석",
                    "실시간 알림"
                ],
                "screenshots": [
                    "/static/marketplace/attendance_1.png",
                    "/static/marketplace/attendance_2.png"
                ],
                "demo_url": "/demo/attendance",
                "documentation_url": "/docs/attendance",
                "support_url": "/support/attendance",
                "rating": 4.8,
                "downloads": 1250,
                "reviews": 89,
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z"
            },
            "sales_management": {
                "id": "sales_management",
                "name": "매출 관리",
                "version": "1.0.0",
                "description": "매출 통계, 분석, 예측, 인건비 대비 효율 분석",
                "author": "Your Program Team",
                "category": "sales",
                "tags": ["매출", "분석", "예측", "통계"],
                "price": 0.0,
                "currency": "KRW",
                "scope": ModuleScope.BRANCH.value,
                "dependencies": ["attendance_management"],
                "permissions": ["sales_management"],
                "features": [
                    "실시간 매출 통계",
                    "인건비 대비 효율 분석",
                    "AI 기반 매출 예측",
                    "직원별 성과 분석",
                    "브랜드별 비교 분석"
                ],
                "screenshots": [
                    "/static/marketplace/sales_1.png",
                    "/static/marketplace/sales_2.png"
                ],
                "demo_url": "/demo/sales",
                "documentation_url": "/docs/sales",
                "support_url": "/support/sales",
                "rating": 4.9,
                "downloads": 2100,
                "reviews": 156,
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z"
            },
            "payroll_management": {
                "id": "payroll_management",
                "name": "급여 관리",
                "version": "1.0.0",
                "description": "급여 계산, 세금 처리, 출퇴근 데이터 연동",
                "author": "Your Program Team",
                "category": "hr",
                "tags": ["급여", "세금", "계산", "인사"],
                "price": 0.0,
                "currency": "KRW",
                "scope": ModuleScope.BRANCH.value,
                "dependencies": ["attendance_management"],
                "permissions": ["payroll_management"],
                "features": [
                    "자동 급여 계산",
                    "세금 및 공제 처리",
                    "출퇴근 데이터 연동",
                    "급여 명세서 생성",
                    "세무 신고 지원"
                ],
                "screenshots": [
                    "/static/marketplace/payroll_1.png",
                    "/static/marketplace/payroll_2.png"
                ],
                "demo_url": "/demo/payroll",
                "documentation_url": "/docs/payroll",
                "support_url": "/support/payroll",
                "rating": 4.7,
                "downloads": 980,
                "reviews": 67,
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z"
            },
            "inventory_management": {
                "id": "inventory_management",
                "name": "재고 관리",
                "version": "1.0.0",
                "description": "재고 추적, 자동 발주, 매출 연동 분석",
                "author": "Your Program Team",
                "category": "inventory",
                "tags": ["재고", "발주", "관리", "분석"],
                "price": 0.0,
                "currency": "KRW",
                "scope": ModuleScope.BRANCH.value,
                "dependencies": ["sales_management"],
                "permissions": ["inventory_management"],
                "features": [
                    "실시간 재고 추적",
                    "자동 발주 시스템",
                    "매출 연동 분석",
                    "재고 비용 최적화",
                    "AI 기반 수요 예측"
                ],
                "screenshots": [
                    "/static/marketplace/inventory_1.png",
                    "/static/marketplace/inventory_2.png"
                ],
                "demo_url": "/demo/inventory",
                "documentation_url": "/docs/inventory",
                "support_url": "/support/inventory",
                "rating": 4.6,
                "downloads": 850,
                "reviews": 45,
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z"
            },
            "qsc_management": {
                "id": "qsc_management",
                "name": "QSC 관리",
                "version": "1.0.0",
                "description": "품질(Quality), 서비스(Service), 청결(Cleanliness) 관리",
                "author": "Your Program Team",
                "category": "quality",
                "tags": ["QSC", "품질", "서비스", "청결"],
                "price": 0.0,
                "currency": "KRW",
                "scope": ModuleScope.BRANCH.value,
                "dependencies": [],
                "permissions": ["qsc_management"],
                "features": [
                    "품질 관리 체크리스트",
                    "서비스 평가 시스템",
                    "청결도 모니터링",
                    "AI 기반 품질 분석",
                    "개선 제안 시스템"
                ],
                "screenshots": [
                    "/static/marketplace/qsc_1.png",
                    "/static/marketplace/qsc_2.png"
                ],
                "demo_url": "/demo/qsc",
                "documentation_url": "/docs/qsc",
                "support_url": "/support/qsc",
                "rating": 4.5,
                "downloads": 650,
                "reviews": 38,
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z"
            }
        }
        
        with open(self.modules_file, 'w', encoding='utf-8') as f:
            json.dump(sample_modules, f, indent=2, ensure_ascii=False)
    
    def get_available_modules(self, user_id: int = None, 
                            scope: ModuleScope = None,
                            category: str = None,
                            search: str = None) -> List[Dict[str, Any]]:
        """사용 가능한 모듈 목록 조회"""
        try:
            with open(self.modules_file, 'r', encoding='utf-8') as f:
                modules = json.load(f)
            
            # 필터링
            filtered_modules = []
            for module_id, module in modules.items():
                # 상태 필터
                if module.get('status') != 'active':
                    continue
                
                # 범위 필터
                if scope and module.get('scope') != scope.value:
                    continue
                
                # 카테고리 필터
                if category and module.get('category') != category:
                    continue
                
                # 검색 필터
                if search:
                    search_lower = search.lower()
                    if not (search_lower in module.get('name', '').lower() or
                           search_lower in module.get('description', '').lower() or
                           any(search_lower in str(tag).lower() for tag in module.get('tags', []))):
                        continue
                
                # 사용자별 설치 상태 확인
                if user_id:
                    module['is_installed'] = self.is_module_installed(module_id, user_id)
                    module['is_activated'] = self.is_module_activated(module_id, user_id)
                
                filtered_modules.append(module)
            
            return filtered_modules
            
        except Exception as e:
            logger.error(f"사용 가능한 모듈 목록 조회 실패: {e}")
            return []
    
    def get_module_detail(self, module_id: str) -> Optional[Dict[str, Any]]:
        """모듈 상세 정보 조회"""
        try:
            with open(self.modules_file, 'r', encoding='utf-8') as f:
                modules = json.load(f)
            
            if module_id not in modules:
                return None
            
            module = modules[module_id]
            
            # 설치된 사용자 수 조회
            installed_users = self.get_installed_users(module_id)
            module['installed_users'] = len(installed_users)
            
            # 리뷰 정보 조회
            reviews = self.get_module_reviews(module_id)
            module['reviews'] = reviews
            
            return module
            
        except Exception as e:
            logger.error(f"모듈 상세 정보 조회 실패: {e}")
            return None
    
    def install_module(self, module_id: str, user_id: int, 
                      scope_id: int = None, scope_type: ModuleScope = ModuleScope.USER) -> bool:
        """모듈 설치"""
        try:
            # 모듈 정보 확인
            module = self.get_module_detail(module_id)
            if not module:
                logger.error(f"모듈을 찾을 수 없습니다: {module_id}")
                return False
            
            # 이미 설치된 모듈인지 확인
            if self.is_module_installed(module_id, user_id, scope_id, scope_type):
                logger.warning(f"이미 설치된 모듈입니다: {module_id}")
                return True
            
            # 의존성 확인
            dependencies = module.get('dependencies', [])
            for dep in dependencies:
                if not self.is_module_installed(dep, user_id, scope_id, scope_type):
                    logger.error(f"의존성 모듈이 설치되지 않았습니다: {dep}")
                    return False
            
            # 설치 정보 저장
            installed_data = self._load_installed_data()
            
            install_key = f"{user_id}_{scope_type.value}_{scope_id}" if scope_id else f"{user_id}_{scope_type.value}"
            
            if install_key not in installed_data:
                installed_data[install_key] = {}
            
            installed_data[install_key][module_id] = {
                "installed_at": datetime.now().isoformat(),
                "status": ModuleStatus.INSTALLED.value,
                "version": module.get('version', '1.0.0'),
                "scope_type": scope_type.value,
                "scope_id": scope_id
            }
            
            self._save_installed_data(installed_data)
            
            # 다운로드 수 증가
            self._increment_downloads(module_id)
            
            # 모듈 파일 복사 (실제 구현에서는 더 복잡한 로직 필요)
            self._copy_module_files(module_id, user_id, scope_id, scope_type)
            
            logger.info(f"모듈 설치 완료: {module_id} -> {install_key}")
            return True
            
        except Exception as e:
            logger.error(f"모듈 설치 실패: {e}")
            return False
    
    def activate_module(self, module_id: str, user_id: int,
                       scope_id: int = None, scope_type: ModuleScope = ModuleScope.USER) -> bool:
        """모듈 활성화"""
        try:
            # 설치된 모듈인지 확인
            if not self.is_module_installed(module_id, user_id, scope_id, scope_type):
                logger.error(f"설치되지 않은 모듈입니다: {module_id}")
                return False
            
            # 활성화 상태 업데이트
            installed_data = self._load_installed_data()
            install_key = f"{user_id}_{scope_type.value}_{scope_id}" if scope_id else f"{user_id}_{scope_type.value}"
            
            if install_key in installed_data and module_id in installed_data[install_key]:
                installed_data[install_key][module_id]["status"] = ModuleStatus.ACTIVATED.value
                installed_data[install_key][module_id]["activated_at"] = datetime.now().isoformat()
                
                self._save_installed_data(installed_data)
                
                # 모듈 초기화 및 연동 설정
                self._initialize_module_integration(module_id, user_id, scope_id, scope_type)
                
                logger.info(f"모듈 활성화 완료: {module_id} -> {install_key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"모듈 활성화 실패: {e}")
            return False
    
    def deactivate_module(self, module_id: str, user_id: int,
                         scope_id: int = None, scope_type: ModuleScope = ModuleScope.USER) -> bool:
        """모듈 비활성화"""
        try:
            # 설치된 모듈인지 확인
            if not self.is_module_installed(module_id, user_id, scope_id, scope_type):
                logger.error(f"설치되지 않은 모듈입니다: {module_id}")
                return False
            
            # 비활성화 상태 업데이트
            installed_data = self._load_installed_data()
            install_key = f"{user_id}_{scope_type.value}_{scope_id}" if scope_id else f"{user_id}_{scope_type.value}"
            
            if install_key in installed_data and module_id in installed_data[install_key]:
                installed_data[install_key][module_id]["status"] = ModuleStatus.DEACTIVATED.value
                installed_data[install_key][module_id]["deactivated_at"] = datetime.now().isoformat()
                
                self._save_installed_data(installed_data)
                
                logger.info(f"모듈 비활성화 완료: {module_id} -> {install_key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"모듈 비활성화 실패: {e}")
            return False
    
    def uninstall_module(self, module_id: str, user_id: int,
                        scope_id: int = None, scope_type: ModuleScope = ModuleScope.USER) -> bool:
        """모듈 제거"""
        try:
            # 설치된 모듈인지 확인
            if not self.is_module_installed(module_id, user_id, scope_id, scope_type):
                logger.error(f"설치되지 않은 모듈입니다: {module_id}")
                return False
            
            # 의존하는 모듈이 있는지 확인
            dependent_modules = self._get_dependent_modules(module_id, user_id, scope_id, scope_type)
            if dependent_modules:
                logger.error(f"이 모듈에 의존하는 모듈이 있습니다: {dependent_modules}")
                return False
            
            # 제거
            installed_data = self._load_installed_data()
            install_key = f"{user_id}_{scope_type.value}_{scope_id}" if scope_id else f"{user_id}_{scope_type.value}"
            
            if install_key in installed_data and module_id in installed_data[install_key]:
                del installed_data[install_key][module_id]
                
                # 빈 키 제거
                if not installed_data[install_key]:
                    del installed_data[install_key]
                
                self._save_installed_data(installed_data)
                
                # 모듈 파일 정리
                self._cleanup_module_files(module_id, user_id, scope_id, scope_type)
                
                logger.info(f"모듈 제거 완료: {module_id} -> {install_key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"모듈 제거 실패: {e}")
            return False
    
    def get_installed_modules(self, user_id: int,
                            scope_id: int = None, scope_type: ModuleScope = ModuleScope.USER) -> List[Dict[str, Any]]:
        """설치된 모듈 목록 조회"""
        try:
            installed_data = self._load_installed_data()
            install_key = f"{user_id}_{scope_type.value}_{scope_id}" if scope_id else f"{user_id}_{scope_type.value}"
            
            if install_key not in installed_data:
                return []
            
            installed_modules = []
            for module_id, install_info in installed_data[install_key].items():
                module_detail = self.get_module_detail(module_id)
                if module_detail:
                    module_detail.update(install_info)
                    installed_modules.append(module_detail)
            
            return installed_modules
            
        except Exception as e:
            logger.error(f"설치된 모듈 목록 조회 실패: {e}")
            return []
    
    def update_module_config(self, module_id: str, user_id: int, config: Dict[str, Any],
                           scope_id: int = None, scope_type: ModuleScope = ModuleScope.USER) -> bool:
        """모듈 설정 업데이트"""
        try:
            # 설치된 모듈인지 확인
            if not self.is_module_installed(module_id, user_id, scope_id, scope_type):
                logger.error(f"설치되지 않은 모듈입니다: {module_id}")
                return False
            
            # 설정 저장
            configs_data = self._load_configs_data()
            config_key = f"{user_id}_{scope_type.value}_{scope_id}" if scope_id else f"{user_id}_{scope_type.value}"
            
            if config_key not in configs_data:
                configs_data[config_key] = {}
            
            configs_data[config_key][module_id] = {
                "config": config,
                "updated_at": datetime.now().isoformat()
            }
            
            self._save_configs_data(configs_data)
            
            logger.info(f"모듈 설정 업데이트 완료: {module_id} -> {config_key}")
            return True
            
        except Exception as e:
            logger.error(f"모듈 설정 업데이트 실패: {e}")
            return False
    
    def get_module_config(self, module_id: str, user_id: int,
                         scope_id: int = None, scope_type: ModuleScope = ModuleScope.USER) -> Optional[Dict[str, Any]]:
        """모듈 설정 조회"""
        try:
            configs_data = self._load_configs_data()
            config_key = f"{user_id}_{scope_type.value}_{scope_id}" if scope_id else f"{user_id}_{scope_type.value}"
            
            if config_key in configs_data and module_id in configs_data[config_key]:
                return configs_data[config_key][module_id]["config"]
            
            return None
            
        except Exception as e:
            logger.error(f"모듈 설정 조회 실패: {e}")
            return None
    
    def get_module_statistics(self, user_id: int = None) -> Dict[str, Any]:
        """모듈 통계 조회"""
        try:
            installed_data = self._load_installed_data()
            
            stats = {
                "total_installed": 0,
                "total_activated": 0,
                "total_deactivated": 0,
                "modules_by_category": {},
                "modules_by_status": {},
                "recent_installations": [],
                "popular_modules": []
            }
            
            # 사용자별 필터링
            if user_id:
                install_keys = [k for k in installed_data.keys() if k.startswith(f"{user_id}_")]
            else:
                install_keys = list(installed_data.keys())
            
            for install_key in install_keys:
                for module_id, install_info in installed_data[install_key].items():
                    stats["total_installed"] += 1
                    
                    status = install_info.get("status", ModuleStatus.INSTALLED.value)
                    if status == ModuleStatus.ACTIVATED.value:
                        stats["total_activated"] += 1
                    elif status == ModuleStatus.DEACTIVATED.value:
                        stats["total_deactivated"] += 1
                    
                    # 카테고리별 통계
                    module_detail = self.get_module_detail(module_id)
                    if module_detail:
                        category = module_detail.get("category", "unknown")
                        stats["modules_by_category"][category] = stats["modules_by_category"].get(category, 0) + 1
                    
                    # 상태별 통계
                    stats["modules_by_status"][status] = stats["modules_by_status"].get(status, 0) + 1
            
            return stats
            
        except Exception as e:
            logger.error(f"모듈 통계 조회 실패: {e}")
            return {}
    
    # 내부 헬퍼 메서드들
    def _load_installed_data(self) -> Dict[str, Any]:
        """설치된 모듈 데이터 로드"""
        try:
            with open(self.installed_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            logger.error(f"설치된 모듈 데이터 로드 실패: {e}")
            return {}
    
    def _save_installed_data(self, data: Dict[str, Any]):
        """설치된 모듈 데이터 저장"""
        try:
            with open(self.installed_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"설치된 모듈 데이터 저장 실패: {e}")
    
    def _load_configs_data(self) -> Dict[str, Any]:
        """모듈 설정 데이터 로드"""
        try:
            with open(self.configs_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            logger.error(f"모듈 설정 데이터 로드 실패: {e}")
            return {}
    
    def _save_configs_data(self, data: Dict[str, Any]):
        """모듈 설정 데이터 저장"""
        try:
            with open(self.configs_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"모듈 설정 데이터 저장 실패: {e}")
    
    def is_module_installed(self, module_id: str, user_id: int,
                          scope_id: int = None, scope_type: ModuleScope = ModuleScope.USER) -> bool:
        """모듈 설치 여부 확인"""
        installed_data = self._load_installed_data()
        install_key = f"{user_id}_{scope_type.value}_{scope_id}" if scope_id else f"{user_id}_{scope_type.value}"
        return install_key in installed_data and module_id in installed_data[install_key]
    
    def is_module_activated(self, module_id: str, user_id: int,
                          scope_id: int = None, scope_type: ModuleScope = ModuleScope.USER) -> bool:
        """모듈 활성화 여부 확인"""
        installed_data = self._load_installed_data()
        install_key = f"{user_id}_{scope_type.value}_{scope_id}" if scope_id else f"{user_id}_{scope_type.value}"
        
        if install_key in installed_data and module_id in installed_data[install_key]:
            return installed_data[install_key][module_id].get("status") == ModuleStatus.ACTIVATED.value
        
        return False
    
    def get_installed_users(self, module_id: str) -> List[int]:
        """모듈을 설치한 사용자 목록"""
        installed_data = self._load_installed_data()
        users = []
        
        for install_key, modules in installed_data.items():
            if module_id in modules:
                user_id = int(install_key.split('_')[0])
                if user_id not in users:
                    users.append(user_id)
        
        return users
    
    def get_module_reviews(self, module_id: str) -> List[Dict[str, Any]]:
        """모듈 리뷰 목록"""
        # 실제 구현에서는 데이터베이스에서 조회
        return [
            {
                "id": 1,
                "user_name": "김철수",
                "rating": 5,
                "comment": "정말 유용한 모듈입니다!",
                "created_at": "2024-01-10T15:30:00Z"
            },
            {
                "id": 2,
                "user_name": "이영희",
                "rating": 4,
                "comment": "기능이 잘 구현되어 있어요.",
                "created_at": "2024-01-08T12:15:00Z"
            }
        ]
    
    def _increment_downloads(self, module_id: str):
        """다운로드 수 증가"""
        try:
            with open(self.modules_file, 'r', encoding='utf-8') as f:
                modules = json.load(f)
            
            if module_id in modules:
                modules[module_id]["downloads"] = modules[module_id].get("downloads", 0) + 1
                
                with open(self.modules_file, 'w', encoding='utf-8') as f:
                    json.dump(modules, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"다운로드 수 증가 실패: {e}")
    
    def _copy_module_files(self, module_id: str, user_id: int, scope_id: int, scope_type: ModuleScope):
        """모듈 파일 복사"""
        # 실제 구현에서는 모듈 파일을 해당 범위에 복사
        pass
    
    def _cleanup_module_files(self, module_id: str, user_id: int, scope_id: int, scope_type: ModuleScope):
        """모듈 파일 정리"""
        # 실제 구현에서는 모듈 파일을 정리
        pass
    
    def _initialize_module_integration(self, module_id: str, user_id: int, scope_id: int, scope_type: ModuleScope):
        """모듈 초기화 및 연동 설정"""
        # 실제 구현에서는 모듈을 중앙 시스템과 연동
        pass
    
    def _get_dependent_modules(self, module_id: str, user_id: int, scope_id: int, scope_type: ModuleScope) -> List[str]:
        """의존하는 모듈 목록"""
        installed_data = self._load_installed_data()
        install_key = f"{user_id}_{scope_type.value}_{scope_id}" if scope_id else f"{user_id}_{scope_type.value}"
        
        if install_key not in installed_data:
            return []
        
        dependent_modules = []
        for installed_module_id in installed_data[install_key].keys():
            module_detail = self.get_module_detail(installed_module_id)
            if module_detail and module_id in module_detail.get('dependencies', []):
                dependent_modules.append(installed_module_id)
        
        return dependent_modules 