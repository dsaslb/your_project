"""
레스토랑 관리 플러그인
레스토랑 업종 전용 관리 기능을 제공하는 플러그인
"""

from datetime import datetime
from flask import Blueprint, jsonify, request
from core.backend.plugin_interface import (
    BasePlugin,
    PluginMetadata,
    PluginRoute,
    PluginMenu,
    PluginConfig,
    PluginDependency,
)


class RestaurantManagementPlugin(BasePlugin):
    """레스토랑 관리 플러그인"""

    def __init__(self):
        super().__init__()
        self.blueprint = Blueprint("your_program_management", __name__)
        self._setup_routes()
        self._setup_menus()
        self._setup_config_schema()
        self._setup_dependencies()

    def _setup_routes(self):
        """라우트 설정"""
        self.routes = [
            PluginRoute(
                path="/menu",
                methods=["GET", "POST"],
                handler="handle_menu",
                auth_required=True,
                roles=["admin", "manager"],
                description="메뉴 관리 API",
                version="v1",
            ),
            PluginRoute(
                path="/orders",
                methods=["GET", "POST", "PUT"],
                handler="handle_orders",
                auth_required=True,
                roles=["admin", "manager", "employee"],
                description="주문 관리 API",
                version="v1",
            ),
            PluginRoute(
                path="/inventory",
                methods=["GET", "POST", "PUT"],
                handler="handle_inventory",
                auth_required=True,
                roles=["admin", "manager"],
                description="재고 관리 API",
                version="v1",
            ),
            PluginRoute(
                path="/analytics",
                methods=["GET"],
                handler="handle_analytics",
                auth_required=True,
                roles=["admin", "manager"],
                description="레스토랑 분석 API",
                version="v1",
            ),
        ]

    def _setup_menus(self):
        """메뉴 설정"""
        self.menus = [
            PluginMenu(
                title="메뉴 관리",
                path="/restaurant/menu",
                icon="utensils",
                parent="restaurant",
                roles=["admin", "manager"],
                order=1,
            ),
            PluginMenu(
                title="주문 관리",
                path="/restaurant/orders",
                icon="shopping-cart",
                parent="restaurant",
                roles=["admin", "manager", "employee"],
                order=2,
                badge="New",
            ),
            PluginMenu(
                title="재고 관리",
                path="/restaurant/inventory",
                icon="package",
                parent="restaurant",
                roles=["admin", "manager"],
                order=3,
            ),
            PluginMenu(
                title="레스토랑 분석",
                path="/restaurant/analytics",
                icon="chart-bar",
                parent="restaurant",
                roles=["admin", "manager"],
                order=4,
            ),
        ]

    def _setup_config_schema(self):
        """설정 스키마 설정"""
        self.config_schema = [
            PluginConfig(
                key="auto_order",
                type="boolean",
                default=True,
                required=False,
                description="자동 주문 처리 활성화",
            ),
            PluginConfig(
                key="inventory_alert_threshold",
                type="number",
                default=10,
                required=False,
                description="재고 부족 알림 임계값",
                validation={"min": 0, "max": 1000},
            ),
            PluginConfig(
                key="order_timeout",
                type="number",
                default=30,
                required=False,
                description="주문 타임아웃 시간(분)",
                validation={"min": 5, "max": 120},
            ),
            PluginConfig(
                key="payment_methods",
                type="select",
                default="card",
                required=False,
                description="결제 방법",
                options=["card", "cash", "mobile", "all"],
            ),
            PluginConfig(
                key="restaurant_name",
                type="string",
                default="",
                required=False,
                description="레스토랑 이름",
                validation={"min_length": 1, "max_length": 100},
            ),
        ]

    def _setup_dependencies(self):
        """의존성 설정"""
        self.dependencies = [
            PluginDependency(
                plugin_id="core_management",
                version="1.0.0",
                required=True,
                description="핵심 관리 기능",
            )
        ]

    def initialize(self) -> bool:
        """플러그인 초기화"""
        try:
            # 메타데이터 설정
            self.metadata = PluginMetadata(
                name="레스토랑 관리",
                version="1.0.0",
                description="레스토랑 업종 전용 관리 기능",
                author="Your Program Team",
                category="restaurant",
                dependencies=["core_management"],
                permissions=["your_program_management"],
                enabled=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            # 의존성 플러그인 알림 (플러그인 레지스트리가 있을 때만)
            try:
                from core.backend.plugin_interface import plugin_registry

                for dep in self.dependencies:
                    if dep.plugin_id in plugin_registry.plugins:
                        dep_plugin = plugin_registry.plugins[dep.plugin_id]
                        self.on_dependency_loaded(dep.plugin_id, dep_plugin)
            except ImportError:
                pass  # 플러그인 레지스트리를 찾을 수 없는 경우 무시

            self._initialized = True
            return True

        except Exception as e:
            print(f"레스토랑 관리 플러그인 초기화 실패: {e}")
            return False

    def cleanup(self) -> bool:
        """플러그인 정리"""
        try:
            self._initialized = False
            return True
        except Exception as e:
            print(f"레스토랑 관리 플러그인 정리 실패: {e}")
            return False

    def get_metadata(self) -> PluginMetadata:
        """메타데이터 반환"""
        if self.metadata is None:
            raise ValueError("플러그인 메타데이터가 설정되지 않았습니다")
        return self.metadata

    # API 핸들러 메서드들
    def handle_menu(self):
        """메뉴 관리 핸들러"""
        if request.method == "GET":
            # 메뉴 목록 조회
            menus = [
                {"id": 1, "name": "김치찌개", "price": 8000, "category": "메인"},
                {"id": 2, "name": "된장찌개", "price": 7000, "category": "메인"},
                {"id": 3, "name": "비빔밥", "price": 9000, "category": "메인"},
            ]
            return jsonify({"menus": menus})
        elif request.method == "POST":
            # 새 메뉴 추가
            data = request.get_json()
            return jsonify({"message": "메뉴가 추가되었습니다", "menu": data})

    def handle_orders(self):
        """주문 관리 핸들러"""
        if request.method == "GET":
            # 주문 목록 조회
            orders = [
                {
                    "id": 1,
                    "customer": "홍길동",
                    "items": ["김치찌개"],
                    "total": 8000,
                    "status": "완료",
                },
                {
                    "id": 2,
                    "customer": "김철수",
                    "items": ["된장찌개", "비빔밥"],
                    "total": 16000,
                    "status": "조리중",
                },
            ]
            return jsonify({"orders": orders})
        elif request.method == "POST":
            # 새 주문 생성
            data = request.get_json()
            return jsonify({"message": "주문이 생성되었습니다", "order": data})
        elif request.method == "PUT":
            # 주문 상태 업데이트
            data = request.get_json()
            return jsonify({"message": "주문 상태가 업데이트되었습니다"})

    def handle_inventory(self):
        """재고 관리 핸들러"""
        if request.method == "GET":
            # 재고 목록 조회
            inventory = [
                {
                    "id": 1,
                    "item": "김치",
                    "quantity": 50,
                    "unit": "kg",
                    "alert_threshold": 10,
                },
                {
                    "id": 2,
                    "item": "된장",
                    "quantity": 30,
                    "unit": "kg",
                    "alert_threshold": 5,
                },
                {
                    "id": 3,
                    "item": "쌀",
                    "quantity": 200,
                    "unit": "kg",
                    "alert_threshold": 20,
                },
            ]
            return jsonify({"inventory": inventory})
        elif request.method == "POST":
            # 재고 추가
            data = request.get_json()
            return jsonify({"message": "재고가 추가되었습니다", "item": data})
        elif request.method == "PUT":
            # 재고 업데이트
            data = request.get_json()
            return jsonify({"message": "재고가 업데이트되었습니다"})

    def handle_analytics(self):
        """레스토랑 분석 핸들러"""
        if request.method == "GET":
            # 분석 데이터 반환
            analytics = {
                "daily_sales": 150000,
                "monthly_sales": 4500000,
                "popular_items": ["김치찌개", "된장찌개", "비빔밥"],
                "customer_count": 45,
                "average_order_value": 12000,
            }
            return jsonify(analytics)


def create_plugin() -> RestaurantManagementPlugin:
    """플러그인 인스턴스 생성"""
    return RestaurantManagementPlugin()
