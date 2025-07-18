from .plugin_interface import BasePlugin, plugin_registry  # pyright: ignore
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
import json
import importlib.util
import importlib
from typing import Optional

config = None  # pyright: ignore
form = None  # pyright: ignore
"""
플러그인 자동 로딩 시스템
플러그인 디렉토리를 스캔하고 자동으로 로드하는 시스템
"""


logger = logging.getLogger(__name__)


class PluginLoader:
    """플러그인 자동 로더"""

    def __init__(self, plugins_dir="plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.loaded_plugins: Dict[str, BasePlugin] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}

        # 플러그인 디렉토리 생성
        self.plugins_dir.mkdir(exist_ok=True)

    def scan_plugins(self) -> List[str]:
        """플러그인 디렉토리 스캔"""
        discovered_plugins = []

        if not self.plugins_dir.exists():
            logger.warning(f"플러그인 디렉토리가 존재하지 않습니다: {self.plugins_dir}")
            return discovered_plugins

        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir() and not plugin_dir.name.startswith("."):
                plugin_id = plugin_dir.name
                config_file = plugin_dir / "config" / "plugin.json"

                if config_file.exists():
                    try:
                        with open(config_file, "r", encoding="utf-8") as f:
                            config = json.load(f)

                        # 플러그인 활성화 상태 확인
                        if config and config.get("enabled", True):
                            discovered_plugins.append(plugin_id)
                            logger.info(f"플러그인 발견: {plugin_id}")
                        else:
                            logger.info(f"플러그인 비활성화됨: {plugin_id}")

                    except Exception as e:
                        logger.error(f"플러그인 {plugin_id} 설정 로드 실패: {e}")
                else:
                    logger.warning(
                        f"플러그인 {plugin_id}에 config/plugin.json이 없습니다"
                    )

        return discovered_plugins

    def load_plugin(self, plugin_id: str) -> Optional[BasePlugin]:
        """플러그인 로드"""
        if plugin_id in self.loaded_plugins:
            logger.warning(f"플러그인 {plugin_id}이 이미 로드되어 있습니다")
            return self.loaded_plugins[plugin_id]

        plugin_dir = self.plugins_dir / plugin_id
        if not plugin_dir.exists():
            logger.error(f"플러그인 디렉토리가 존재하지 않습니다: {plugin_dir}")
            return None

        try:
            # 플러그인 메인 파일 로드
            main_file = plugin_dir / "backend" / "main.py"
            if not main_file.exists():
                logger.error(f"플러그인 {plugin_id}의 backend/main.py가 없습니다")
                return None

            # 모듈 로드
            spec = importlib.util.spec_from_file_location(
                f"plugins.{plugin_id}.main", main_file
            )
            if spec is None:
                logger.error(f"플러그인 {plugin_id} 모듈 스펙 생성 실패")
                return None

            module = importlib.util.module_from_spec(spec)
            if spec.loader is None:
                logger.error(f"플러그인 {plugin_id} 로더가 없습니다")
                return None

            spec.loader.exec_module(module)

            # 플러그인 인스턴스 생성
            if hasattr(module, "create_plugin"):
                plugin = module.create_plugin()
            elif hasattr(module, "Plugin"):
                plugin = module.Plugin()
            else:
                logger.error(
                    f"플러그인 {plugin_id}에 create_plugin 함수나 Plugin 클래스가 없습니다"
                )
                return None

            # 플러그인 초기화
            if not plugin.initialize():
                logger.error(f"플러그인 {plugin_id} 초기화 실패")
                return None

            # 레지스트리에 등록
            if plugin_registry.register(plugin_id, plugin):
                self.loaded_plugins[plugin_id] = plugin  # pyright: ignore
                logger.info(f"플러그인 {plugin_id} 로드 완료")
                return plugin
            else:
                logger.error(f"플러그인 {plugin_id} 레지스트리 등록 실패")
                return None

        except Exception as e:
            logger.error(f"플러그인 {plugin_id} 로드 실패: {e}")
            return None

    def unload_plugin(self, plugin_id: str) -> bool:
        """플러그인 언로드"""
        if plugin_id not in self.loaded_plugins:
            logger.warning(f"플러그인 {plugin_id}이 로드되어 있지 않습니다")
            return True

        try:
            plugin = self.loaded_plugins[plugin_id]

            # 레지스트리에서 제거
            if plugin_registry.unregister(plugin_id):
                # 플러그인 정리
                plugin.cleanup()
                del self.loaded_plugins[plugin_id]

                logger.info(f"플러그인 {plugin_id} 언로드 완료")
                return True
            else:
                logger.error(f"플러그인 {plugin_id} 레지스트리 제거 실패")
                return False

        except Exception as e:
            logger.error(f"플러그인 {plugin_id} 언로드 실패: {e}")
            return False

    def reload_plugin(self, plugin_id: str) -> Optional[BasePlugin]:
        """플러그인 재로드"""
        logger.info(f"플러그인 {plugin_id} 재로드 시작")

        # 기존 플러그인 언로드
        if plugin_id in self.loaded_plugins:
            self.unload_plugin(plugin_id)

        # 새로 로드
        return self.load_plugin(plugin_id)

    def load_all_plugins(self) -> Dict[str, BasePlugin]:
        """모든 활성화된 플러그인 로드"""
        logger.info("모든 플러그인 로드 시작")

        discovered_plugins = self.scan_plugins()
        loaded_plugins: Dict[str, BasePlugin] = {}

        for plugin_id in discovered_plugins:
            plugin = self.load_plugin(plugin_id)
            if plugin:
                loaded_plugins[plugin_id] = plugin  # pyright: ignore

        logger.info(
            f"플러그인 로드 완료: {len(loaded_plugins)}/{len(discovered_plugins)}"
        )
        return loaded_plugins

    def get_plugin_config(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """플러그인 설정 조회"""
        config_file = self.plugins_dir / plugin_id / "config" / "plugin.json"

        if not config_file.exists():
            return None

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"플러그인 {plugin_id} 설정 로드 실패: {e}")
            return None

    def save_plugin_config(self, plugin_id: str, config: Dict[str, Any]) -> bool:
        """플러그인 설정 저장"""
        config_file = self.plugins_dir / plugin_id / "config" / "plugin.json"

        try:
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"플러그인 {plugin_id} 설정 저장 실패: {e}")
            return False

    def enable_plugin(self, plugin_id: str) -> bool:
        """플러그인 활성화"""
        config = self.get_plugin_config(plugin_id)
        if not config:
            return False

        config["enabled"] = True
        config["updated_at"] = datetime.utcnow().isoformat()

        if self.save_plugin_config(plugin_id, config):
            # 플러그인이 로드되어 있지 않으면 로드
            if plugin_id not in self.loaded_plugins:
                return self.load_plugin(plugin_id) is not None
            return True
        return False

    def disable_plugin(self, plugin_id: str) -> bool:
        """플러그인 비활성화"""
        config = self.get_plugin_config(plugin_id)
        if not config:
            return False

        config["enabled"] = False
        config["updated_at"] = datetime.utcnow().isoformat()

        if self.save_plugin_config(plugin_id, config):
            # 플러그인이 로드되어 있으면 언로드
            if plugin_id in self.loaded_plugins:
                return self.unload_plugin(plugin_id)
            return True
        return False

    def get_plugin_status(self, plugin_id: str) -> Dict[str, Any]:
        """플러그인 상태 정보"""
        config = self.get_plugin_config(plugin_id)
        plugin = self.loaded_plugins.get(plugin_id)
        # 상태 정보 구성 (예시)
        return {"config": config, "plugin": plugin}

    def get_all_plugin_status(self) -> Dict[str, Dict[str, Any]]:
        """모든 플러그인 상태 정보"""
        statuses = {}

        # 로드된 플러그인들
        for plugin_id in self.loaded_plugins:
            statuses[plugin_id] = self.get_plugin_status(plugin_id)

        # 발견되었지만 로드되지 않은 플러그인들
        discovered_plugins = self.scan_plugins()
        for plugin_id in discovered_plugins:
            if plugin_id not in statuses:
                statuses[plugin_id] = self.get_plugin_status(plugin_id)

        return statuses


# 전역 플러그인 로더 인스턴스
plugin_loader = PluginLoader()
