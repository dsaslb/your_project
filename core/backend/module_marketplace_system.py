from enum import Enum
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import hashlib
import zipfile
import shutil
import json
import os
from typing import Optional
config = None  # pyright: ignore
form = None  # pyright: ignore
"""
모듈 마켓플레이스 연동 시스템
업종별/브랜드별/매장별 관리자가 모듈을 자유롭게 적용/비활성화/설정할 수 있는 시스템
"""


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
        self.marketplace_dir = marketplace_dir
        self.modules_dir = modules_dir
        self.db_session = db_session
        
        # 파일 경로
        self.modules_file = os.path.join(marketplace_dir, "modules.json")
        self.installed_file = os.path.join(marketplace_dir, "installed.json")
        self.configs_file = os.path.join(marketplace_dir, "configs.json")
        self.reviews_file = os.path.join(marketplace_dir, "reviews.json")
        self.downloads_file = os.path.join(marketplace_dir, "downloads.json")
        
        # 초기화
        self._init_marketplace()

    def _init_marketplace(self):
        """마켓플레이스 초기화"""
        try:
            # 디렉토리 생성
            os.makedirs(self.marketplace_dir, exist_ok=True)
            os.makedirs(self.modules_dir, exist_ok=True)
            
            # 파일 초기화
            if not os.path.exists(self.modules_file):
                self._create_sample_modules()
            
            if not os.path.exists(self.installed_file):
                with open(self.installed_file, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
            
            if not os.path.exists(self.configs_file):
                with open(self.configs_file, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
            
            if not os.path.exists(self.reviews_file):
                with open(self.reviews_file, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
            
            if not os.path.exists(self.downloads_file):
                with open(self.downloads_file, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
                    
        except Exception as e:
            logger.error(f"마켓플레이스 초기화 실패: {e}")

    def _create_sample_modules(self):
        """샘플 모듈 생성"""
        sample_modules = {
            "attendance_management": {
                "id": "attendance_management",
                "name": "출근 관리",
                "description": "직원 출근/퇴근 관리 모듈",
                "version": "1.0.0",
                "category": "management",
                "tags": ["attendance", "employee", "management"],
                "author": "System",
                "status": "active",
                "scope": "branch",
                "dependencies": [],
                "downloads": 0,
                "rating": 4.5,
                "created_at": datetime.now().isoformat()
            },
            "inventory_management": {
                "id": "inventory_management",
                "name": "재고 관리",
                "description": "상품 재고 관리 모듈",
                "version": "1.0.0",
                "category": "management",
                "tags": ["inventory", "stock", "management"],
                "author": "System",
                "status": "active",
                "scope": "branch",
                "dependencies": [],
                "downloads": 0,
                "rating": 4.3,
                "created_at": datetime.now().isoformat()
            }
        }
        
        with open(self.modules_file, 'w', encoding='utf-8') as f:
            json.dump(sample_modules, f, ensure_ascii=False, indent=2)

    def get_available_modules(self, user_id: Optional[int] = None,
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
                       scope_id: Optional[int] = None, scope_type: ModuleScope = ModuleScope.USER) -> bool:
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
                        scope_id: Optional[int] = None, scope_type: ModuleScope = ModuleScope.USER) -> bool:
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
                          scope_id: Optional[int] = None, scope_type: ModuleScope = ModuleScope.USER) -> bool:
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
                         scope_id: Optional[int] = None, scope_type: ModuleScope = ModuleScope.USER) -> bool:
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
                              scope_id: Optional[int] = None, scope_type: ModuleScope = ModuleScope.USER) -> List[Dict[str, Any]]:
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
                             scope_id: Optional[int] = None, scope_type: ModuleScope = ModuleScope.USER) -> bool:
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

            configs_data[config_key][module_id] = config
            self._save_configs_data(configs_data)

            logger.info(f"모듈 설정 업데이트 완료: {module_id} -> {config_key}")
            return True

        except Exception as e:
            logger.error(f"모듈 설정 업데이트 실패: {e}")
            return False

    def get_module_config(self, module_id: str, user_id: int,
                          scope_id: Optional[int] = None, scope_type: ModuleScope = ModuleScope.USER) -> Optional[Dict[str, Any]]:
        """모듈 설정 조회"""
        try:
            configs_data = self._load_configs_data()
            config_key = f"{user_id}_{scope_type.value}_{scope_id}" if scope_id else f"{user_id}_{scope_type.value}"

            if config_key in configs_data and module_id in configs_data[config_key]:
                return configs_data[config_key][module_id]

            return None

        except Exception as e:
            logger.error(f"모듈 설정 조회 실패: {e}")
            return None

    def get_module_statistics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """모듈 통계 조회"""
        try:
            stats = {
                "total_modules": 0,
                "installed_modules": 0,
                "activated_modules": 0,
                "popular_modules": [],
                "recent_installations": []
            }

            # 전체 모듈 수
            with open(self.modules_file, 'r', encoding='utf-8') as f:
                modules = json.load(f)
                stats["total_modules"] = len(modules)

            # 사용자별 설치 통계
            if user_id:
                installed_modules = self.get_installed_modules(user_id)
                stats["installed_modules"] = len(installed_modules)
                stats["activated_modules"] = len([m for m in installed_modules if m.get('status') == ModuleStatus.ACTIVATED.value])

            # 인기 모듈 (다운로드 수 기준)
            with open(self.downloads_file, 'r', encoding='utf-8') as f:
                downloads = json.load(f)
                popular_modules = sorted(downloads.items(), key=lambda x: x[1], reverse=True)[:5]
                stats["popular_modules"] = [{"module_id": module_id, "downloads": count} for module_id, count in popular_modules]

            return stats

        except Exception as e:
            logger.error(f"모듈 통계 조회 실패: {e}")
            return {}

    # 내부 헬퍼 메서드들
    def _load_installed_data(self) -> Dict[str, Any]:
        """설치 데이터 로드"""
        try:
            with open(self.installed_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_installed_data(self, data: Dict[str, Any]):
        """설치 데이터 저장"""
        with open(self.installed_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_configs_data(self) -> Dict[str, Any]:
        """설정 데이터 로드"""
        try:
            with open(self.configs_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_configs_data(self, data: Dict[str, Any]):
        """설정 데이터 저장"""
        with open(self.configs_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def is_module_installed(self, module_id: str, user_id: int,
                            scope_id: Optional[int] = None, scope_type: ModuleScope = ModuleScope.USER) -> bool:
        """모듈 설치 여부 확인"""
        installed_data = self._load_installed_data()
        install_key = f"{user_id}_{scope_type.value}_{scope_id}" if scope_id else f"{user_id}_{scope_type.value}"
        return install_key in installed_data and module_id in installed_data[install_key]

    def is_module_activated(self, module_id: str, user_id: int,
                            scope_id: Optional[int] = None, scope_type: ModuleScope = ModuleScope.USER) -> bool:
        """모듈 활성화 여부 확인"""
        installed_data = self._load_installed_data()
        install_key = f"{user_id}_{scope_type.value}_{scope_id}" if scope_id else f"{user_id}_{scope_type.value}"
        if install_key in installed_data and module_id in installed_data[install_key]:
            return installed_data[install_key][module_id].get('status') == ModuleStatus.ACTIVATED.value
        return False

    def get_installed_users(self, module_id: str) -> List[int]:
        """모듈을 설치한 사용자 목록"""
        try:
            installed_data = self._load_installed_data()
            users = []
            for install_key in installed_data:
                if module_id in installed_data[install_key]:
                    user_id = int(install_key.split('_')[0])
                    users.append(user_id)
            return users
        except Exception as e:
            logger.error(f"설치된 사용자 목록 조회 실패: {e}")
            return []

    def get_module_reviews(self, module_id: str) -> List[Dict[str, Any]]:
        """모듈 리뷰 목록"""
        try:
            with open(self.reviews_file, 'r', encoding='utf-8') as f:
                reviews = json.load(f)
                return reviews.get(module_id, [])
        except Exception:
            return []

    def _increment_downloads(self, module_id: str):
        """다운로드 수 증가"""
        try:
            with open(self.downloads_file, 'r', encoding='utf-8') as f:
                downloads = json.load(f)
        except Exception:
            downloads = {}

        downloads[module_id] = downloads.get(module_id, 0) + 1

        with open(self.downloads_file, 'w', encoding='utf-8') as f:
            json.dump(downloads, f, ensure_ascii=False, indent=2)

    def _copy_module_files(self, module_id: str, user_id: int, scope_id: int, scope_type: ModuleScope):
        """모듈 파일 복사 (실제 구현에서는 더 복잡한 로직 필요)"""
        # 실제 구현에서는 모듈 파일을 사용자별 디렉토리로 복사
        pass

    def _cleanup_module_files(self, module_id: str, user_id: int, scope_id: int, scope_type: ModuleScope):
        """모듈 파일 정리 (실제 구현에서는 더 복잡한 로직 필요)"""
        # 실제 구현에서는 모듈 파일을 정리
        pass

    def _initialize_module_integration(self, module_id: str, user_id: int, scope_id: int, scope_type: ModuleScope):
        """모듈 연동 초기화 (실제 구현에서는 더 복잡한 로직 필요)"""
        # 실제 구현에서는 모듈 연동 설정
        pass

    def _get_dependent_modules(self, module_id: str, user_id: int, scope_id: int, scope_type: ModuleScope) -> List[str]:
        """의존하는 모듈 목록 조회"""
        # 실제 구현에서는 의존성 분석
        return []
