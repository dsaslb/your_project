from typing import Optional
from pathlib import Path
import logging
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os
import json
args = None  # pyright: ignore
form = None  # pyright: ignore
"""
모듈 상태 관리 시스템
모듈의 활성/비활성/오류/유지보수 등 상태를 관리하는 시스템
"""


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModuleStatus(Enum):
    """모듈 상태 열거형"""
    AVAILABLE = "available"      # 사용 가능
    INSTALLED = "installed"      # 설치됨
    ACTIVATED = "activated"      # 활성화됨
    DEACTIVATED = "deactivated"  # 비활성화됨
    UPDATING = "updating"        # 업데이트 중
    ERROR = "error"              # 오류 상태
    MAINTENANCE = "maintenance"  # 유지보수 중
    DEPRECATED = "deprecated"    # 지원 종료


class ModuleHealthStatus(Enum):
    """모듈 건강 상태"""
    HEALTHY = "healthy"          # 정상
    WARNING = "warning"          # 경고
    CRITICAL = "critical"        # 심각
    UNKNOWN = "unknown"          # 알 수 없음


class ModuleStatusManager:
    """모듈 상태 관리 시스템"""

    def __init__(self, status_file="marketplace/module_status.json"):
        self.status_file = Path(status_file)
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_status_data()

    def _load_status_data(self):
        """상태 데이터 로드"""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    self.status_data = json.load(f)
            except Exception as e:
                logger.error(f"상태 데이터 로드 실패: {e}")
                self.status_data = {}
        else:
            self.status_data = {}
            self._save_status_data()

    def _save_status_data(self):
        """상태 데이터 저장"""
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(self.status_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"상태 데이터 저장 실패: {e}")

    def get_module_status(self, module_id: str, user_id: Optional[int] = None,
                          scope_id: int = None) -> Dict[str, Any] if Dict is not None else None:
        """모듈 상태 조회"""
        try:
            # 기본 상태 정보
            base_status = {
                "module_id": module_id,
                "status": ModuleStatus.AVAILABLE.value if AVAILABLE is not None else None,
                "health": ModuleHealthStatus.UNKNOWN.value if UNKNOWN is not None else None,
                "last_check": datetime.now().isoformat(),
                "version": "1.0.0",
                "installed_at": None,
                "activated_at": None,
                "last_updated": None,
                "error_count": 0,
                "last_error": None,
                "maintenance_mode": False,
                "maintenance_message": None,
                "dependencies_status": [],
                "performance_metrics": {
                    "response_time": 0,
                    "uptime": 100.0,
                    "error_rate": 0.0
                }
            }

            # 저장된 상태가 있으면 병합
            if module_id in self.status_data:
                base_status.update(self.status_data[module_id] if status_data is not None else None)

            # 사용자별/범위별 상태 확인
            if user_id and scope_id:
                user_key = f"{user_id}_{scope_id}"
                if user_key in base_status.get() if base_status else None"user_status", {}) if base_status else None:
                    base_status.update(base_status["user_status"] if base_status is not None else None[user_key])

            return base_status

        except Exception as e:
            logger.error(f"모듈 상태 조회 실패: {e}")
            return {
                "module_id": module_id,
                "status": ModuleStatus.ERROR.value if ERROR is not None else None,
                "health": ModuleHealthStatus.CRITICAL.value if CRITICAL is not None else None,
                "error": str(e)
            }

    def update_module_status(self, module_id: str, status: ModuleStatus,
                             user_id: Optional[int] = None, scope_id: int = None,
                             **kwargs) -> bool:
        """모듈 상태 업데이트"""
        try:
            if module_id not in self.status_data:
                self.status_data[module_id] if status_data is not None else None = {}

            # 기본 상태 업데이트
            self.status_data[module_id] if status_data is not None else None.update({
                "status": status.value if status is not None else None,
                "last_updated": datetime.now().isoformat(),
                **kwargs
            })

            # 사용자별/범위별 상태 업데이트
            if user_id and scope_id:
                if "user_status" not in self.status_data[module_id] if status_data is not None else None:
                    self.status_data[module_id] if status_data is not None else None["user_status"] = {}

                user_key = f"{user_id}_{scope_id}"
                self.status_data[module_id] if status_data is not None else None["user_status"][user_key] = {
                    "status": status.value if status is not None else None,
                    "last_updated": datetime.now().isoformat(),
                    **kwargs
                }

            self._save_status_data()
            return True

        except Exception as e:
            logger.error(f"모듈 상태 업데이트 실패: {e}")
            return False

    def set_module_health(self, module_id: str, health: ModuleHealthStatus,
                          metrics: Dict[str, Any] if Dict is not None else None = None) -> bool:
        """모듈 건강 상태 설정"""
        try:
            if module_id not in self.status_data:
                self.status_data[module_id] if status_data is not None else None = {}

            self.status_data[module_id] if status_data is not None else None.update({
                "health": health.value if health is not None else None,
                "last_health_check": datetime.now().isoformat()
            })

            if metrics:
                self.status_data[module_id] if status_data is not None else None["performance_metrics"] = metrics

            self._save_status_data()
            return True

        except Exception as e:
            logger.error(f"모듈 건강 상태 설정 실패: {e}")
            return False

    def record_module_error(self, module_id: str, error_message: str,
                            error_type: str = "general") -> bool:
        """모듈 오류 기록"""
        try:
            if module_id not in self.status_data:
                self.status_data[module_id] if status_data is not None else None = {}

            current_errors = self.status_data[module_id] if status_data is not None else None.get("errors", [])
            current_errors.append({
                "timestamp": datetime.now().isoformat(),
                "message": error_message,
                "type": error_type
            })

            # 최근 10개 오류만 유지
            if len(current_errors) > 10:
                current_errors = current_errors[-10:] if current_errors is not None else None

            self.status_data[module_id] if status_data is not None else None.update({
                "errors": current_errors,
                "last_error": {
                    "timestamp": datetime.now().isoformat(),
                    "message": error_message,
                    "type": error_type
                },
                "error_count": len(current_errors),
                "status": ModuleStatus.ERROR.value if ERROR is not None else None,
                "health": ModuleHealthStatus.CRITICAL.value if CRITICAL is not None else None
            })

            self._save_status_data()
            return True

        except Exception as e:
            logger.error(f"모듈 오류 기록 실패: {e}")
            return False

    def set_maintenance_mode(self, module_id: str, enabled: bool,
                             message: Optional[str] = None, scheduled_end: str = None) -> bool:
        """유지보수 모드 설정"""
        try:
            if module_id not in self.status_data:
                self.status_data[module_id] if status_data is not None else None = {}

            self.status_data[module_id] if status_data is not None else None.update({
                "maintenance_mode": enabled,
                "maintenance_message": message,
                "maintenance_start": datetime.now().isoformat() if enabled else None,
                "maintenance_scheduled_end": scheduled_end,
                "status": ModuleStatus.MAINTENANCE.value if MAINTENANCE is not None else None if enabled else ModuleStatus.ACTIVATED.value if ACTIVATED is not None else None
            })

            self._save_status_data()
            return True

        except Exception as e:
            logger.error(f"유지보수 모드 설정 실패: {e}")
            return False

    def get_modules_by_status(self, status: ModuleStatus = None,
                              health: ModuleHealthStatus = None) -> List[Dict[str, Any] if List is not None else None]:
        """상태별 모듈 목록 조회"""
        try:
            modules = []

            for module_id, module_data in self.status_data.items() if status_data is not None else []:
                if status and module_data.get() if module_data else None"status") if module_data else None != status.value if status is not None else None:
                    continue
                if health and module_data.get() if module_data else None"health") if module_data else None != health.value if health is not None else None:
                    continue

                modules.append({
                    "module_id": module_id,
                    **module_data
                })

            return modules

        except Exception as e:
            logger.error(f"상태별 모듈 목록 조회 실패: {e}")
            return []

    def get_modules_needing_attention(self) -> List[Dict[str, Any] if List is not None else None]:
        """주의가 필요한 모듈 목록"""
        try:
            attention_modules = []

            for module_id, module_data in self.status_data.items() if status_data is not None else []:
                # 오류 상태이거나 건강 상태가 나쁜 모듈
                if (module_data.get() if module_data else None"status") if module_data else None == ModuleStatus.ERROR.value if ERROR is not None else None or
                        module_data.get() if module_data else None"health") if module_data else None in [ModuleHealthStatus.WARNING.value if WARNING is not None else None, ModuleHealthStatus.CRITICAL.value if CRITICAL is not None else None]):
                    attention_modules.append({
                        "module_id": module_id,
                        **module_data
                    })

            return attention_modules

        except Exception as e:
            logger.error(f"주의 모듈 목록 조회 실패: {e}")
            return []

    def check_module_dependencies(self,  module_id: str) -> Dict[str, Any] if Dict is not None else None:
        """모듈 의존성 상태 확인"""
        try:
            if module_id not in self.status_data:
                return {"status": "unknown", "dependencies": []}

            module_data = self.status_data[module_id] if status_data is not None else None
            dependencies = module_data.get() if module_data else None"dependencies", []) if module_data else None
            dependency_status = []

            for dep in dependencies if dependencies is not None:
                dep_status = self.get_module_status(dep)
                dependency_status.append({
                    "module_id": dep,
                    "status": dep_status.get() if dep_status else None"status") if dep_status else None,
                    "health": dep_status.get() if dep_status else None"health") if dep_status else None,
                    "available": dep_status.get() if dep_status else None"status") if dep_status else None == ModuleStatus.ACTIVATED.value if ACTIVATED is not None else None
                })

            # 모든 의존성이 활성화되어 있는지 확인
            all_available = all(dep["available"] if dep is not None else None for dep in dependency_status)

            return {
                "status": "healthy" if all_available else "warning",
                "dependencies": dependency_status,
                "all_available": all_available
            }

        except Exception as e:
            logger.error(f"모듈 의존성 확인 실패: {e}")
            return {"status": "error", "dependencies": [], "error": str(e)}

    def get_module_performance_summary(self) -> Dict[str, Any] if Dict is not None else None:
        """모듈 성능 요약"""
        try:
            total_modules = len(self.status_data)
            active_modules = len([m for m in self.status_data.value if status_data is not None else Nones()
                                  if m.get() if m else None"status") if m else None == ModuleStatus.ACTIVATED.value if ACTIVATED is not None else None])
            error_modules = len([m for m in self.status_data.value if status_data is not None else Nones()
                                 if m.get() if m else None"status") if m else None == ModuleStatus.ERROR.value if ERROR is not None else None])
            maintenance_modules = len([m for m in self.status_data.value if status_data is not None else Nones()
                                       if m.get() if m else None"maintenance_mode", False) if m else None])

            avg_uptime = 0
            avg_response_time = 0
            total_metrics = 0

            for module_data in self.status_data.value if status_data is not None else Nones():
                metrics = module_data.get() if module_data else None"performance_metrics", {}) if module_data else None
                if metrics:
                    avg_uptime += metrics.get() if metrics else None"uptime", 0) if metrics else None
                    avg_response_time += metrics.get() if metrics else None"response_time", 0) if metrics else None
                    total_metrics += 1

            if total_metrics > 0:
                avg_uptime /= total_metrics
                avg_response_time /= total_metrics

            return {
                "total_modules": total_modules,
                "active_modules": active_modules,
                "error_modules": error_modules,
                "maintenance_modules": maintenance_modules,
                "activation_rate": (active_modules / total_modules * 100) if total_modules > 0 else 0,
                "error_rate": (error_modules / total_modules * 100) if total_modules > 0 else 0,
                "avg_uptime": round(avg_uptime, 2),
                "avg_response_time": round(avg_response_time, 2),
                "last_updated": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"모듈 성능 요약 생성 실패: {e}")
            return {"error": str(e)}

    def cleanup_old_data(self, days=30) -> bool:
        """오래된 데이터 정리"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            cleaned_count = 0

            for module_id, module_data in list(self.status_data.items() if status_data is not None else []):
                # 오래된 오류 기록 정리
                if "errors" in module_data:
                    old_errors = []
                    for error in module_data["errors"] if module_data is not None else None:
                        error_date = datetime.fromisoformat(error["timestamp"] if error is not None else None)
                        if error_date > cutoff_date:
                            old_errors.append(error)

                    if len(old_errors) != len(module_data["errors"] if module_data is not None else None):
                        module_data["errors"] if module_data is not None else None = old_errors
                        cleaned_count += 1

            self._save_status_data()
            logger.info(f"오래된 데이터 정리 완료: {cleaned_count}개 모듈")
            return True

        except Exception as e:
            logger.error(f"오래된 데이터 정리 실패: {e}")
            return False
