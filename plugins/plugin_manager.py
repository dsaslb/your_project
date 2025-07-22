"""
플러그인 관리 시스템 - 고도화 버전
"""

import os
import json
import importlib
import importlib.util
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class PluginStatus(Enum):
    """플러그인 상태"""
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"
    LOADING = "loading"
    UPDATING = "updating"

class PluginPermission(Enum):
    """플러그인 권한"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    SYSTEM = "system"

@dataclass
class PluginConfig:
    """플러그인 설정"""
    name: str
    version: str
    description: str
    author: str
    permissions: List[str]
    dependencies: List[str]
    settings: Dict[str, Any]
    status: str = PluginStatus.DISABLED.value
    enabled_at: Optional[str] = None
    disabled_at: Optional[str] = None
    last_error: Optional[str] = None
    created_at: str = None
    updated_at: str = None

@dataclass
class PluginInstance:
    """플러그인 인스턴스"""
    config: PluginConfig
    module: Optional[Any] = None
    routes: List[str] = []
    hooks: Dict[str, List[callable]] = None

class PluginManager:
    """플러그인 관리자"""
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = plugins_dir
        self.plugins: Dict[str, PluginInstance] = {}
        self.hooks: Dict[str, List[callable]] = {}
        self.permissions: Dict[str, List[str]] = {}
        self.config_file = os.path.join(plugins_dir, "plugin_config.json")
        self.load_config()
    
    def load_config(self):
        """플러그인 설정 로드"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    for plugin_name, config in config_data.items():
                        plugin_config = PluginConfig(**config)
                        self.plugins[plugin_name] = PluginInstance(
                            config=plugin_config,
                            hooks={}
                        )
            except Exception as e:
                logger.error(f"플러그인 설정 로드 실패: {e}")
    
    def save_config(self):
        """플러그인 설정 저장"""
        try:
            config_data = {}
            for name, instance in self.plugins.items():
                config_data[name] = asdict(instance.config)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"플러그인 설정 저장 실패: {e}")
    
    def discover_plugins(self) -> List[str]:
        """플러그인 발견"""
        plugins = []
        if not os.path.exists(self.plugins_dir):
            return plugins
        
        for item in os.listdir(self.plugins_dir):
            plugin_path = os.path.join(self.plugins_dir, item)
            if os.path.isdir(plugin_path):
                # __init__.py 파일 확인
                init_file = os.path.join(plugin_path, "__init__.py")
                if os.path.exists(init_file):
                    plugins.append(item)
        
        return plugins
    
    def load_plugin(self, plugin_name: str) -> bool:
        """플러그인 로드"""
        try:
            plugin_path = os.path.join(self.plugins_dir, plugin_name)
            if not os.path.exists(plugin_path):
                logger.error(f"플러그인 경로를 찾을 수 없습니다: {plugin_path}")
                return False
            
            # 플러그인 모듈 로드
            spec = importlib.util.spec_from_file_location(
                plugin_name,
                os.path.join(plugin_path, "__init__.py")
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 플러그인 설정 로드
            config_file = os.path.join(plugin_path, "config.json")
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            else:
                # 기본 설정 생성
                config_data = {
                    "name": plugin_name,
                    "version": "1.0.0",
                    "description": f"{plugin_name} 플러그인",
                    "author": "Unknown",
                    "permissions": ["read"],
                    "dependencies": [],
                    "settings": {}
                }
            
            # 플러그인 인스턴스 생성
            plugin_config = PluginConfig(
                **config_data,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            plugin_instance = PluginInstance(
                config=plugin_config,
                module=module,
                hooks={}
            )
            
            self.plugins[plugin_name] = plugin_instance
            logger.info(f"플러그인 로드 성공: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 로드 실패 {plugin_name}: {e}")
            return False
    
    def enable_plugin(self, plugin_name: str, user_permissions: List[str] = None) -> bool:
        """플러그인 활성화"""
        if plugin_name not in self.plugins:
            logger.error(f"플러그인을 찾을 수 없습니다: {plugin_name}")
            return False
        
        plugin_instance = self.plugins[plugin_name]
        plugin_config = plugin_instance.config
        
        # 권한 확인
        if user_permissions and not self.check_permissions(plugin_config.permissions, user_permissions):
            logger.error(f"플러그인 활성화 권한이 없습니다: {plugin_name}")
            return False
        
        try:
            # 의존성 확인
            if not self.check_dependencies(plugin_config.dependencies):
                logger.error(f"플러그인 의존성을 만족하지 않습니다: {plugin_name}")
                return False
            
            # 플러그인 초기화
            if hasattr(plugin_instance.module, 'initialize'):
                plugin_instance.module.initialize()
            
            # 상태 업데이트
            plugin_config.status = PluginStatus.ENABLED.value
            plugin_config.enabled_at = datetime.now().isoformat()
            plugin_config.last_error = None
            
            # 훅 등록
            if hasattr(plugin_instance.module, 'register_hooks'):
                plugin_instance.module.register_hooks(self)
            
            # 라우트 등록
            if hasattr(plugin_instance.module, 'register_routes'):
                routes = plugin_instance.module.register_routes()
                plugin_instance.routes = routes
            
            logger.info(f"플러그인 활성화 성공: {plugin_name}")
            self.save_config()
            return True
            
        except Exception as e:
            plugin_config.status = PluginStatus.ERROR.value
            plugin_config.last_error = str(e)
            logger.error(f"플러그인 활성화 실패 {plugin_name}: {e}")
            return False
    
    def disable_plugin(self, plugin_name: str, user_permissions: List[str] = None) -> bool:
        """플러그인 비활성화"""
        if plugin_name not in self.plugins:
            logger.error(f"플러그인을 찾을 수 없습니다: {plugin_name}")
            return False
        
        plugin_instance = self.plugins[plugin_name]
        plugin_config = plugin_instance.config
        
        # 권한 확인
        if user_permissions and not self.check_permissions(plugin_config.permissions, user_permissions):
            logger.error(f"플러그인 비활성화 권한이 없습니다: {plugin_name}")
            return False
        
        try:
            # 플러그인 정리
            if hasattr(plugin_instance.module, 'cleanup'):
                plugin_instance.module.cleanup()
            
            # 상태 업데이트
            plugin_config.status = PluginStatus.DISABLED.value
            plugin_config.disabled_at = datetime.now().isoformat()
            plugin_config.last_error = None
            
            # 훅 제거
            plugin_instance.hooks = {}
            
            logger.info(f"플러그인 비활성화 성공: {plugin_name}")
            self.save_config()
            return True
            
        except Exception as e:
            plugin_config.status = PluginStatus.ERROR.value
            plugin_config.last_error = str(e)
            logger.error(f"플러그인 비활성화 실패 {plugin_name}: {e}")
            return False
    
    def check_permissions(self, required_permissions: List[str], user_permissions: List[str]) -> bool:
        """권한 확인"""
        if not user_permissions:
            return False
        
        # 시스템 권한이 있으면 모든 권한 허용
        if PluginPermission.SYSTEM.value in user_permissions:
            return True
        
        # 관리자 권한이 있으면 대부분 권한 허용
        if PluginPermission.ADMIN.value in user_permissions:
            return True
        
        # 필요한 권한이 사용자 권한에 포함되어 있는지 확인
        for permission in required_permissions:
            if permission not in user_permissions:
                return False
        
        return True
    
    def check_dependencies(self, dependencies: List[str]) -> bool:
        """의존성 확인"""
        for dependency in dependencies:
            try:
                importlib.import_module(dependency)
            except ImportError:
                logger.error(f"의존성 모듈을 찾을 수 없습니다: {dependency}")
                return False
        return True
    
    def register_hook(self, plugin_name: str, hook_name: str, callback: callable):
        """훅 등록"""
        if plugin_name not in self.plugins:
            return
        
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        
        self.hooks[hook_name].append(callback)
        self.plugins[plugin_name].hooks[hook_name] = callback
    
    def execute_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """훅 실행"""
        results = []
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    result = callback(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    logger.error(f"훅 실행 오류 {hook_name}: {e}")
        return results
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """플러그인 정보 조회"""
        if plugin_name not in self.plugins:
            return None
        
        plugin_instance = self.plugins[plugin_name]
        return {
            "name": plugin_instance.config.name,
            "version": plugin_instance.config.version,
            "description": plugin_instance.config.description,
            "author": plugin_instance.config.author,
            "status": plugin_instance.config.status,
            "permissions": plugin_instance.config.permissions,
            "dependencies": plugin_instance.config.dependencies,
            "settings": plugin_instance.config.settings,
            "enabled_at": plugin_instance.config.enabled_at,
            "disabled_at": plugin_instance.config.disabled_at,
            "last_error": plugin_instance.config.last_error,
            "created_at": plugin_instance.config.created_at,
            "updated_at": plugin_instance.config.updated_at,
            "routes": plugin_instance.routes
        }
    
    def get_all_plugins(self) -> List[Dict[str, Any]]:
        """모든 플러그인 정보 조회"""
        plugins = []
        for plugin_name in self.plugins:
            plugin_info = self.get_plugin_info(plugin_name)
            if plugin_info:
                plugins.append(plugin_info)
        return plugins
    
    def update_plugin_settings(self, plugin_name: str, settings: Dict[str, Any], user_permissions: List[str] = None) -> bool:
        """플러그인 설정 업데이트"""
        if plugin_name not in self.plugins:
            return False
        
        plugin_instance = self.plugins[plugin_name]
        plugin_config = plugin_instance.config
        
        # 권한 확인
        if user_permissions and not self.check_permissions(plugin_config.permissions, user_permissions):
            return False
        
        try:
            plugin_config.settings.update(settings)
            plugin_config.updated_at = datetime.now().isoformat()
            self.save_config()
            return True
        except Exception as e:
            logger.error(f"플러그인 설정 업데이트 실패 {plugin_name}: {e}")
            return False
    
    def install_plugin(self, plugin_path: str, user_permissions: List[str] = None) -> bool:
        """플러그인 설치"""
        if not user_permissions or PluginPermission.ADMIN.value not in user_permissions:
            logger.error("플러그인 설치 권한이 없습니다.")
            return False
        
        try:
            # 플러그인 파일 복사
            plugin_name = os.path.basename(plugin_path)
            target_path = os.path.join(self.plugins_dir, plugin_name)
            
            if os.path.exists(target_path):
                logger.error(f"플러그인이 이미 존재합니다: {plugin_name}")
                return False
            
            # 플러그인 로드
            if self.load_plugin(plugin_name):
                logger.info(f"플러그인 설치 성공: {plugin_name}")
                return True
            else:
                logger.error(f"플러그인 설치 실패: {plugin_name}")
                return False
                
        except Exception as e:
            logger.error(f"플러그인 설치 중 오류: {e}")
            return False
    
    def uninstall_plugin(self, plugin_name: str, user_permissions: List[str] = None) -> bool:
        """플러그인 제거"""
        if not user_permissions or PluginPermission.ADMIN.value not in user_permissions:
            logger.error("플러그인 제거 권한이 없습니다.")
            return False
        
        if plugin_name not in self.plugins:
            logger.error(f"플러그인을 찾을 수 없습니다: {plugin_name}")
            return False
        
        try:
            # 플러그인 비활성화
            if self.plugins[plugin_name].config.status == PluginStatus.ENABLED.value:
                self.disable_plugin(plugin_name, user_permissions)
            
            # 플러그인 제거
            del self.plugins[plugin_name]
            self.save_config()
            
            logger.info(f"플러그인 제거 성공: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 제거 실패 {plugin_name}: {e}")
            return False

# 전역 플러그인 관리자 인스턴스
plugin_manager = PluginManager() 