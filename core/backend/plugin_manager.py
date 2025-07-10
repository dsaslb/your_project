"""
플러그인 관리 시스템
동적으로 플러그인을 로드, 언로드, 관리하는 핵심 시스템
"""

import json
import importlib
import importlib.util
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class PluginMetadata:
    """플러그인 메타데이터"""
    name: str
    version: str
    description: str
    author: str
    category: str
    dependencies: List[str]
    permissions: List[str]
    enabled: bool = True
    config: Optional[Dict[str, Any]] = None

class PluginManager:
    """플러그인 관리자"""
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, PluginMetadata] = {}
        self.loaded_plugins: Dict[str, Any] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
        
        # 플러그인 디렉토리 생성
        self.plugins_dir.mkdir(exist_ok=True)
        
        # 초기 플러그인 로드
        self.scan_plugins()
    
    def scan_plugins(self) -> List[str]:
        """플러그인 디렉토리 스캔"""
        discovered_plugins = []
        
        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir():
                plugin_name = plugin_dir.name
                config_file = plugin_dir / "config" / "plugin.json"
                
                if config_file.exists():
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                        
                        metadata = PluginMetadata(
                            name=config.get('name', plugin_name),
                            version=config.get('version', '1.0.0'),
                            description=config.get('description', ''),
                            author=config.get('author', ''),
                            category=config.get('category', 'general'),
                            dependencies=config.get('dependencies', []),
                            permissions=config.get('permissions', []),
                            enabled=config.get('enabled', True),
                            config=config.get('config', {})
                        )
                        
                        self.plugins[plugin_name] = metadata
                        discovered_plugins.append(plugin_name)
                        
                        logger.info(f"플러그인 발견: {plugin_name} v{metadata.version}")
                        
                    except Exception as e:
                        logger.error(f"플러그인 {plugin_name} 설정 로드 실패: {e}")
        
        return discovered_plugins
    
    def load_plugin(self, plugin_name: str) -> bool:
        """플러그인 로드"""
        if plugin_name not in self.plugins:
            logger.error(f"플러그인 {plugin_name}을 찾을 수 없습니다")
            return False
        
        if plugin_name in self.loaded_plugins:
            logger.warning(f"플러그인 {plugin_name}이 이미 로드되어 있습니다")
            return True
        
        metadata = self.plugins[plugin_name]
        
        # 의존성 확인
        if not self._check_dependencies(metadata.dependencies):
            logger.error(f"플러그인 {plugin_name}의 의존성이 충족되지 않습니다")
            return False
        
        try:
            # 플러그인 모듈 로드
            plugin_path = self.plugins_dir / plugin_name / "backend"
            if not plugin_path.exists():
                logger.error(f"플러그인 {plugin_name}의 백엔드 디렉토리가 없습니다")
                return False
            
            # 메인 플러그인 파일 로드
            main_file = plugin_path / "main.py"
            if main_file.exists():
                spec = importlib.util.spec_from_file_location(
                    f"plugins.{plugin_name}.main", 
                    main_file
                )
                if spec is None:
                    logger.error(f"플러그인 {plugin_name} 모듈 스펙 생성 실패")
                    return False
                    
                module = importlib.util.module_from_spec(spec)
                if spec.loader is None:
                    logger.error(f"플러그인 {plugin_name} 로더가 없습니다")
                    return False
                    
                spec.loader.exec_module(module)
                
                # 플러그인 초기화
                if hasattr(module, 'initialize_plugin'):
                    plugin_instance = module.initialize_plugin()
                    self.loaded_plugins[plugin_name] = plugin_instance
                    
                    logger.info(f"플러그인 {plugin_name} 로드 완료")
                    return True
                else:
                    logger.error(f"플러그인 {plugin_name}에 initialize_plugin 함수가 없습니다")
                    return False
            
        except Exception as e:
            logger.error(f"플러그인 {plugin_name} 로드 실패: {e}")
            return False
        # 모든 경로에서 반환 보장
        return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """플러그인 언로드"""
        if plugin_name not in self.loaded_plugins:
            logger.warning(f"플러그인 {plugin_name}이 로드되어 있지 않습니다")
            return True
        
        try:
            plugin_instance = self.loaded_plugins[plugin_name]
            
            # 플러그인 정리
            if hasattr(plugin_instance, 'cleanup'):
                plugin_instance.cleanup()
            
            del self.loaded_plugins[plugin_name]
            
            logger.info(f"플러그인 {plugin_name} 언로드 완료")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 {plugin_name} 언로드 실패: {e}")
            return False
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """플러그인 활성화"""
        if plugin_name not in self.plugins:
            logger.error(f"플러그인 {plugin_name}을 찾을 수 없습니다")
            return False
        
        self.plugins[plugin_name].enabled = True
        self._save_plugin_config(plugin_name)
        
        # 플러그인이 로드되어 있지 않으면 로드
        if plugin_name not in self.loaded_plugins:
            return self.load_plugin(plugin_name)
        
        return True
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """플러그인 비활성화"""
        if plugin_name not in self.plugins:
            logger.error(f"플러그인 {plugin_name}을 찾을 수 없습니다")
            return False
        
        # 먼저 언로드
        if plugin_name in self.loaded_plugins:
            self.unload_plugin(plugin_name)
        
        self.plugins[plugin_name].enabled = False
        self._save_plugin_config(plugin_name)
        
        return True
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginMetadata]:
        """플러그인 정보 조회"""
        return self.plugins.get(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, PluginMetadata]:
        """모든 플러그인 정보 조회"""
        return self.plugins.copy()
    
    def get_loaded_plugins(self) -> List[str]:
        """로드된 플러그인 목록 조회"""
        return list(self.loaded_plugins.keys())
    
    def get_plugin_routes(self, plugin_name: str) -> List[Dict[str, Any]]:
        """플러그인의 API 라우트 조회"""
        if plugin_name not in self.loaded_plugins:
            return []
        
        plugin_instance = self.loaded_plugins[plugin_name]
        
        if hasattr(plugin_instance, 'get_routes'):
            return plugin_instance.get_routes()
        
        return []
    
    def get_all_routes(self) -> List[Dict[str, Any]]:
        """모든 플러그인의 API 라우트 조회"""
        all_routes = []
        
        for plugin_name in self.loaded_plugins:
            routes = self.get_plugin_routes(plugin_name)
            for route in routes:
                route['plugin'] = plugin_name
                all_routes.append(route)
        
        return all_routes
    
    def _check_dependencies(self, dependencies: List[str]) -> bool:
        """의존성 확인"""
        for dep in dependencies:
            if dep not in self.loaded_plugins and dep not in self.plugins:
                logger.warning(f"의존성 {dep}이 충족되지 않습니다")
                return False
        return True
    
    def _save_plugin_config(self, plugin_name: str):
        """플러그인 설정 저장"""
        if plugin_name not in self.plugins:
            return
        
        metadata = self.plugins[plugin_name]
        config_file = self.plugins_dir / plugin_name / "config" / "plugin.json"
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            config['enabled'] = metadata.enabled
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"플러그인 {plugin_name} 설정 저장 실패: {e}")

# 전역 플러그인 관리자 인스턴스
plugin_manager = PluginManager() 