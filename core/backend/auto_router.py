from .plugin_interface import plugin_registry  # pyright: ignore
from .plugin_loader import plugin_loader  # pyright: ignore
from flask import Flask, Blueprint
from typing import Dict, Optional, List, Any  # pyright: ignore
import logging
import importlib
from typing import Optional
from flask import request

form = None  # pyright: ignore
"""
자동 라우터 시스템
플러그인과 기존 블루프린트를 자동으로 등록하는 시스템
"""


logger = logging.getLogger(__name__)


class AutoRouter:
    """자동 라우터"""

    def __init__(self, app: Flask):
        self.app = app
        self.registered_blueprints: Dict[str, Blueprint] = {}  # pyright: ignore
        self.plugin_loader = plugin_loader

    def register_plugin_routes(self) -> bool:
        """플러그인 라우트 자동 등록"""
        logger.info("플러그인 라우트 등록 시작")

        # 먼저 모든 플러그인 로드
        loaded_plugins = self.plugin_loader.load_all_plugins()

        success_count = 0
        total_count = len(loaded_plugins)

        for plugin_id, plugin in (
            loaded_plugins.items() if loaded_plugins is not None else []
        ):
            try:
                # 플러그인 라우트 정보 가져오기
                routes = plugin.get_routes()
                if not routes:
                    logger.info(f"플러그인 {plugin_id}에 등록할 라우트가 없습니다")
                    continue

                # 플러그인용 Blueprint 생성
                blueprint_name = f"plugin_{plugin_id}"
                blueprint = Blueprint(blueprint_name, __name__)

                # 각 라우트 등록
                if routes is not None:
                    for route in routes:
                        self._register_plugin_route(blueprint, route, plugin_id)

                # Blueprint 등록
                url_prefix = f"/api/plugins/{plugin_id}"
                self.app.register_blueprint(blueprint, url_prefix=url_prefix)
                self.registered_blueprints[plugin_id] = blueprint  # pyright: ignore

                success_count += 1
                logger.info(f"플러그인 {plugin_id}의 {len(routes)}개 라우트 등록 완료")

            except Exception as e:
                logger.error(f"플러그인 {plugin_id} 라우트 등록 실패: {e}")

        logger.info(f"플러그인 라우트 등록 완료: {success_count}/{total_count}")
        return success_count > 0

    def _register_plugin_route(self, blueprint: Blueprint, route, plugin_id: str):
        """플러그인 라우트 등록"""
        try:
            # 플러그인에서 핸들러 함수 가져오기
            plugin = plugin_registry.get_plugin(plugin_id)
            if not plugin:
                logger.error(f"플러그인 {plugin_id}을 찾을 수 없습니다")
                return

            # 핸들러 함수 이름으로 함수 가져오기
            handler_name = route.handler
            if hasattr(plugin, handler_name):
                handler_func = getattr(plugin, handler_name)

                # Blueprint에 라우트 등록
                blueprint.add_url_rule(
                    route.path,
                    f"{plugin_id}_{handler_name}",
                    handler_func,
                    methods=route.methods,
                )
                logger.info(f"플러그인 라우트 등록: {plugin_id}{route.path}")
            else:
                logger.warning(
                    f"플러그인 {plugin_id}에 핸들러 {handler_name}이 없습니다"
                )

        except Exception as e:
            logger.error(f"플러그인 라우트 등록 실패: {e}")

    def register_legacy_blueprints(self) -> bool:
        """기존 블루프린트 자동 등록"""
        logger.info("기존 블루프린트 자동 등록 시작")

        # 기존 블루프린트 목록 (app.py에서 수동 등록하던 것들)
        legacy_blueprints = [
            # API 블루프린트
            ("api.auth", "api_auth_bp"),
            ("api.notice", "api_notice_bp"),
            ("api.comment", "api_comment_bp"),
            ("api.report", "api_report_bp"),
            ("api.admin_log", "admin_log_bp"),
            ("api.admin_report", "admin_report_bp"),
            ("api.admin_report_stat", "admin_report_stat_bp"),
            ("api.comment_report", "comment_report_bp"),
            ("api.staff", "staff_bp"),
            ("api.contracts", "contracts_bp"),
            ("api.health", "health_bp"),
            ("api.brand_management", "brand_management_bp"),
            ("api.store_management", "store_management_bp"),
            ("api.ai_management", "ai_management_bp"),
            ("api.approval_workflow", "approval_workflow_bp"),
            ("api.improvement_requests", "improvement_requests_bp"),
            ("api.iot_api", "iot_bp"),
            # 모듈 블루프린트
            ("api.modules.user_management", "user_management"),
            ("api.modules.notification_system", "notification_system"),
            ("api.modules.schedule_management", "schedule_management"),
            ("api.modules.optimization", "optimization"),
            ("api.modules.monitoring", "monitoring"),
            # 플러그인 관리 블루프린트
            ("api.plugin_management", "plugin_management_bp"),
            ("api.plugin_security", "plugin_security_bp"),
            # ('api.plugin_marketplace_api', 'plugin_marketplace_bp'),  # [중요] 중복/경로 충돌 방지 위해 제외
            ("api.plugin_system_manager_api", "plugin_system_manager_bp"),
            ("api.plugin_operations_api", "plugin_operations_bp"),
            ("api.dynamic_schema", "dynamic_schema_bp"),
            ("api.realtime_notifications", "realtime_notifications_bp"),
            ("api.ai_prediction", "ai_prediction_bp"),
            ("api.advanced_analytics", "advanced_analytics_bp"),
            ("api.mobile_api", "mobile_api_bp"),
            ("api.security_enhanced", "security_enhanced_bp"),
            ("api.performance_optimized", "performance_optimized_bp"),
            # 라우트 블루프린트
            ("routes.plugin_management", "plugin_management_page_bp"),
        ]

        success_count = 0
        total_count = len(legacy_blueprints)

        for module_path, blueprint_name in legacy_blueprints:
            try:
                # 모듈 동적 로드
                module = importlib.import_module(module_path)

                # 블루프린트 객체 가져오기
                if hasattr(module, blueprint_name):
                    blueprint = getattr(module, blueprint_name)

                    # URL 프리픽스 결정
                    url_prefix = self._determine_url_prefix(module_path, blueprint_name)

                    # 블루프린트 등록
                    self.app.register_blueprint(blueprint, url_prefix=url_prefix)
                    self.registered_blueprints[f"{module_path}.{blueprint_name}"] = (
                        blueprint  # pyright: ignore
                    )

                    success_count += 1
                    logger.info(f"블루프린트 등록 완료: {module_path}.{blueprint_name}")
                else:
                    logger.warning(
                        f"블루프린트를 찾을 수 없습니다: {module_path}.{blueprint_name}"
                    )

            except ImportError as e:
                logger.warning(f"모듈을 로드할 수 없습니다: {module_path} - {e}")
            except Exception as e:
                logger.error(
                    f"블루프린트 등록 실패: {module_path}.{blueprint_name} - {e}"
                )

        logger.info(f"기존 블루프린트 등록 완료: {success_count}/{total_count}")
        return success_count > 0

    def _determine_url_prefix(
        self, module_path: str, blueprint_name: str
    ) -> Optional[str]:
        """URL 프리픽스 결정"""
        # API 모듈
        if module_path.startswith("api."):
            if "modules" in module_path:
                # 모듈 API는 /api/modules/ 경로
                module_name = module_path.split(".")[-1]
                return f"/api/modules/{module_name}"
            else:
                # 일반 API는 이미 블루프린트에 프리픽스가 설정되어 있으므로 None 반환
                return None

        # 라우트 모듈
        elif module_path.startswith("routes."):
            return None  # 기본 경로 사용

        return None

    def register_all(self) -> bool:
        """모든 라우트 등록"""
        logger.info("자동 라우터 등록 시작")

        # 1. 기존 블루프린트 등록
        legacy_success = self.register_legacy_blueprints()

        # 2. 플러그인 라우트 등록
        plugin_success = self.register_plugin_routes()

        total_success = legacy_success or plugin_success
        logger.info(f"자동 라우터 등록 완료: 성공={total_success}")

        return total_success

    def get_registered_blueprints(self) -> Dict[str, Blueprint]:
        """등록된 블루프린트 조회"""
        return self.registered_blueprints.copy()

    def get_plugin_menus(self) -> List[Dict[str, Any]]:  # pyright: ignore
        """플러그인 메뉴 정보 수집"""
        menus = []

        for plugin_id, plugin in plugin_registry.get_all_plugins().items():
            plugin_menus = plugin.get_menus()
            if plugin_menus is not None:
                for menu in plugin_menus:
                    menus.append(
                        {
                            "plugin_id": plugin_id,
                            "title": menu.title,
                            "path": menu.path,
                            "icon": menu.icon,
                            "parent": menu.parent,
                            "roles": menu.roles,
                            "order": menu.order,
                            "badge": menu.badge,
                        }
                    )

        return menus

    def get_plugin_status(self) -> Dict[str, Any]:  # pyright: ignore
        """플러그인 상태 정보 수집"""
        status: Dict[str, Any] = {
            "total_plugins": len(plugin_registry.get_all_plugins()),
            "loaded_plugins": [],
            "registered_blueprints": len(self.registered_blueprints),
        }

        for plugin_id, plugin in plugin_registry.get_all_plugins().items():
            plugin_status = plugin.get_health_status()
            if plugin_status is not None:
                plugin_status["id"] = plugin_id
                plugin_status["metadata"] = (
                    plugin.get_metadata().__dict__ if plugin.get_metadata() else None
                )
                status["loaded_plugins"].append(plugin_status)

        return status


def setup_auto_router(app: Flask) -> AutoRouter:
    """자동 라우터 설정"""
    auto_router = AutoRouter(app)

    # 모든 라우트 자동 등록
    auto_router.register_all()

    return auto_router
