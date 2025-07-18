import semver
import json
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Any  # pyright: ignore
from abc import ABC, abstractmethod
from typing import Optional

config = None  # pyright: ignore
form = None  # pyright: ignore
"""
플러그인 표준 인터페이스
모든 플러그인이 구현해야 하는 기본 인터페이스 정의
"""


@dataclass
class PluginMetadata:
    """플러그인 메타데이터"""

    name: str
    version: str
    description: str
    author: str
    category: str
    dependencies: List[str]  # pyright: ignore
    permissions: List[str]  # pyright: ignore
    enabled: bool = True
    config: Optional[Dict[str, Any]] = None  # pyright: ignore
    created_at: Optional[datetime] = None  # pyright: ignore
    updated_at: Optional[datetime] = None  # pyright: ignore

    def validate_version(self) -> bool:
        """버전 형식 검증"""
        try:
            semver.VersionInfo.parse(self.version)
            return True
        except ValueError:
            return False

    def is_compatible_with(self, required_version: str) -> bool:
        """호환성 검사"""
        try:
            current = semver.VersionInfo.parse(self.version)
            required = semver.VersionInfo.parse(required_version)
            return current >= required
        except ValueError:
            return False


@dataclass
class PluginRoute:
    """플러그인 라우트 정보"""

    path: str
    methods: List[str]  # pyright: ignore
    handler: str
    auth_required: bool = True
    roles: Optional[List[str]] = None  # pyright: ignore
    description: str = ""
    version: str = "v1"  # API 버전


@dataclass
class PluginMenu:
    """플러그인 메뉴 정보"""

    title: str
    path: str
    icon: str
    parent: Optional[str] = None  # pyright: ignore
    roles: Optional[List[str]] = None  # pyright: ignore
    order: int = 0
    badge: Optional[str] = None  # pyright: ignore
    visible: bool = True


@dataclass
class PluginConfig:
    """플러그인 설정 스키마"""

    key: str
    type: str  # string, number, boolean, select, json, file
    default: Any
    required: bool = False
    description: str = ""
    options: Optional[List[Any]] = None  # pyright: ignore
    validation: Optional[Dict[str, Any]] = None  # pyright: ignore


@dataclass
class PluginDependency:
    """플러그인 의존성 정보"""

    plugin_id: str
    version: str
    required: bool = True
    description: str = ""


class BasePlugin(ABC):
    """플러그인 기본 인터페이스"""

    def __init__(self):
        self.metadata: Optional[PluginMetadata] = None
        self.routes: List[PluginRoute] = []
        self.menus: List[PluginMenu] = []
        self.config_schema: List[PluginConfig] = []
        self.db_migrations: List[str] = []
        self.dependencies: List[PluginDependency] = []
        self._initialized = False

    @abstractmethod
    def initialize(self) -> bool:
        """플러그인 초기화"""
        pass

    @abstractmethod
    def cleanup(self) -> bool:
        """플러그인 정리"""
        pass

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """플러그인 메타데이터 반환"""
        pass

    def get_routes(self) -> List[PluginRoute]:
        """플러그인 라우트 반환"""
        return self.routes

    def get_menus(self) -> List[PluginMenu]:
        """플러그인 메뉴 반환"""
        return self.menus

    def get_config_schema(self) -> List[PluginConfig]:
        """플러그인 설정 스키마 반환"""
        return self.config_schema

    def get_db_migrations(self) -> List[str]:
        """플러그인 DB 마이그레이션 반환"""
        return self.db_migrations

    def get_dependencies(self) -> List[PluginDependency]:
        """플러그인 의존성 반환"""
        return self.dependencies

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """설정 유효성 검증"""
        if not self.config_schema:
            return True

        for schema in self.config_schema:
            if schema.required and schema.key not in config:
                return False

            if schema.key in config:
                value = config[schema.key]
                if not self._validate_config_value(schema, value):
                    return False

        return True

    def _validate_config_value(self, schema: PluginConfig, value: Any) -> bool:
        """설정 값 유효성 검증"""
        if schema.type == "string":
            if not isinstance(value, str):
                return False
            # 문자열 길이 검증
            if schema.validation and "min_length" in schema.validation:
                if len(value) < schema.validation["min_length"]:
                    return False
            if schema.validation and "max_length" in schema.validation:
                if len(value) > schema.validation["max_length"]:
                    return False
        elif schema.type == "number":
            if not isinstance(value, (int, float)):
                return False
            # 숫자 범위 검증
            if schema.validation and "min" in schema.validation:
                if value < schema.validation["min"]:
                    return False
            if schema.validation and "max" in schema.validation:
                if value > schema.validation["max"]:
                    return False
        elif schema.type == "boolean":
            return isinstance(value, bool)
        elif schema.type == "select":
            return value in (schema.options or [])
        elif schema.type == "json":
            try:
                json.dumps(value)
                return True
            except:
                return False
        elif schema.type == "file":
            # 파일 경로 검증
            return isinstance(value, str) and len(value) > 0
        return True

    def on_enable(self) -> bool:
        """플러그인 활성화 시 호출"""
        return True

    def on_disable(self) -> bool:
        """플러그인 비활성화 시 호출"""
        return True

    def on_config_change(
        self, old_config: Dict[str, Any], new_config: Dict[str, Any]
    ) -> bool:
        """설정 변경 시 호출"""
        return True

    def on_dependency_loaded(
        self, dependency_id: str, dependency_plugin: "BasePlugin"
    ) -> bool:
        """의존성 플러그인 로드 시 호출"""
        return True

    def get_health_status(self) -> Dict[str, Any]:
        """플러그인 상태 정보 반환"""
        return {
            "enabled": self.metadata.enabled if self.metadata else False,
            "initialized": self._initialized,
            "routes_count": len(self.routes),
            "menus_count": len(self.menus),
            "dependencies_count": len(self.dependencies),
            "last_check": datetime.utcnow().isoformat(),
        }

    def get_api_documentation(self) -> Dict[str, Any]:
        """API 문서화 정보 반환"""
        docs = {
            "name": self.metadata.name if self.metadata else "Unknown",
            "version": self.metadata.version if self.metadata else "1.0.0",
            "description": self.metadata.description if self.metadata else "",
            "endpoints": [],  # pyright: ignore
        }
        for route in self.routes:
            if isinstance(docs["endpoints"], list):
                docs["endpoints"].append(
                    {
                        "path": route.path,
                        "methods": route.methods,
                        "description": route.description,
                        "auth_required": route.auth_required,
                        "roles": route.roles,
                        "version": route.version,
                    }
                )
        return docs


class PluginRegistry:
    """플러그인 레지스트리"""

    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}  # pyright: ignore
        self.metadata: Dict[str, PluginMetadata] = {}  # pyright: ignore
        self.dependency_graph: Dict[str, List[str]] = {}  # pyright: ignore

    def register(self, plugin_id: str, plugin: BasePlugin) -> bool:
        """플러그인 등록"""
        try:
            metadata = plugin.get_metadata()
            # 버전 검증
            if not metadata.validate_version():
                print(
                    f"플러그인 {plugin_id}의 버전 형식이 잘못되었습니다: {metadata.version}"
                )
                return False
            # 의존성 검사
            if not self._check_dependencies(plugin_id, plugin):
                print(f"플러그인 {plugin_id}의 의존성이 충족되지 않았습니다")
                return False
            self.plugins[plugin_id] = plugin  # pyright: ignore
            self.metadata[plugin_id] = metadata  # pyright: ignore
            # 의존성 그래프 업데이트
            self._update_dependency_graph(plugin_id, plugin)
            return True
        except Exception as e:
            print(f"플러그인 등록 실패 {plugin_id}: {e}")
            return False

    def _check_dependencies(self, plugin_id: str, plugin: BasePlugin) -> bool:
        """의존성 검사"""
        for dep in plugin.get_dependencies():
            if dep.plugin_id not in self.plugins:
                if dep.required:
                    return False
                continue
            dep_plugin = self.plugins[dep.plugin_id]
            dep_metadata = dep_plugin.get_metadata()
            if not dep_metadata.is_compatible_with(dep.version):
                if dep.required:
                    return False
        return True

    def _update_dependency_graph(self, plugin_id: str, plugin: BasePlugin):
        """의존성 그래프 업데이트"""
        self.dependency_graph[plugin_id] = [
            dep.plugin_id for dep in plugin.get_dependencies()
        ]

    def unregister(self, plugin_id: str) -> bool:
        """플러그인 등록 해제"""
        if plugin_id in self.plugins:
            plugin = self.plugins[plugin_id]
            plugin.cleanup()
            del self.plugins[plugin_id]
            del self.metadata[plugin_id]
            # 의존성 그래프에서 제거
            if plugin_id in self.dependency_graph:
                del self.dependency_graph[plugin_id]
            return True
        return False

    def get_plugin(self, plugin_id: str) -> Optional[BasePlugin]:
        """플러그인 조회"""
        return self.plugins.get(plugin_id)

    def get_all_plugins(self) -> Dict[str, BasePlugin]:
        """모든 플러그인 조회"""
        return self.plugins.copy()

    def get_all_metadata(self) -> Dict[str, PluginMetadata]:
        """모든 플러그인 메타데이터 조회"""
        return self.metadata.copy()

    def get_plugins_by_category(self, category: str) -> Dict[str, BasePlugin]:
        """카테고리별 플러그인 조회"""
        return {
            plugin_id: plugin
            for plugin_id, plugin in self.plugins.items()
            if plugin.get_metadata().category == category
        }

    def get_dependency_order(self) -> List[str]:
        """의존성 순서로 정렬된 플러그인 목록"""
        # 위상 정렬을 사용하여 의존성 순서 결정
        visited = set()
        temp_visited = set()
        order = []

        def dfs(plugin_id: str):
            if plugin_id in temp_visited:
                raise ValueError(f"순환 의존성 발견: {plugin_id}")
            if plugin_id in visited:
                return
            temp_visited.add(plugin_id)
            for dep_id in self.dependency_graph.get(plugin_id, []):
                if dep_id in self.plugins:
                    dfs(dep_id)
            temp_visited.remove(plugin_id)
            visited.add(plugin_id)
            order.append(plugin_id)

        for plugin_id in self.plugins:
            if plugin_id not in visited:
                dfs(plugin_id)
        return order


# 전역 플러그인 레지스트리
plugin_registry = PluginRegistry()
