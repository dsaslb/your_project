"""
플러그인 관리 시스템
동적으로 플러그인을 로드, 언로드, 관리하는 핵심 시스템
"""

import importlib
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from flask import Flask, Blueprint
from pathlib import Path
from .plugin_schema import PluginSchemaValidator, PluginManifest
from .plugin_customization import PluginCustomizationManager

logger = logging.getLogger(__name__)

class PluginManager:
    """플러그인 자동 로딩/등록/관리 시스템"""
    
    def __init__(self, app: Flask, plugins_dir: str = "plugins"):
        self.app = app
        self.plugins_dir = plugins_dir
        self.plugins: Dict[str, Dict] = {}
        self.blueprints: Dict[str, Blueprint] = {}
        self.plugin_configs: Dict[str, Dict] = {}
        self.loaded_plugins: List[str] = []
        self.validator = PluginSchemaValidator()
        self.customization_manager = PluginCustomizationManager()
        
    def discover_plugins(self) -> List[str]:
        """플러그인 디렉토리에서 모든 플러그인을 탐색"""
        plugins = []
        plugins_path = Path(self.plugins_dir)
        
        if not plugins_path.exists():
            logger.warning(f"플러그인 디렉토리가 존재하지 않습니다: {self.plugins_dir}")
            return plugins
            
        for plugin_dir in plugins_path.iterdir():
            if plugin_dir.is_dir():
                config_file = plugin_dir / "config" / "plugin.json"
                if config_file.exists():
                    plugins.append(plugin_dir.name)
                    logger.info(f"플러그인 발견: {plugin_dir.name}")
                    
        return plugins
    
    def load_plugin_config(self, plugin_name: str, 
                          industry: str = "general", 
                          brand: str = "default", 
                          branch: Optional[str] = None) -> Optional[Dict]:
        """플러그인 설정 파일 로드 (커스터마이즈 적용)"""
        plugin_dir = Path(self.plugins_dir) / plugin_name
        manifest = PluginManifest(plugin_dir)
        
        try:
            config = manifest.load()
            if not config:
                logger.error(f"플러그인 {plugin_name} 매니페스트를 찾을 수 없습니다")
                return None
                
            # 기본값 설정
            config.setdefault('enabled', True)
            config.setdefault('category', 'general')
            config.setdefault('dependencies', [])
            config.setdefault('permissions', [])
            config.setdefault('routes', [])
            config.setdefault('menus', [])
            config.setdefault('config_schema', [])
            
            # 커스터마이즈 적용
            customized_config = self.customization_manager.apply_customizations(
                config, industry, brand, branch
            )
            
            return customized_config
            
        except Exception as e:
            logger.error(f"플러그인 {plugin_name} 설정 로드 실패: {e}")
            return None
    
    def load_plugin_module(self, plugin_name: str) -> Optional[Any]:
        """플러그인 모듈 로드"""
        try:
            module_path = f"{self.plugins_dir}.{plugin_name}.backend.main"
            module = importlib.import_module(module_path)
            return module
        except ImportError as e:
            logger.error(f"플러그인 {plugin_name} 모듈 로드 실패: {e}")
            return None
        except Exception as e:
            logger.error(f"플러그인 {plugin_name} 로드 중 오류: {e}")
            return None
    
    def register_plugin_blueprint(self, plugin_name: str, config: Dict) -> bool:
        """플러그인 블루프린트 등록"""
        try:
            module = self.load_plugin_module(plugin_name)
            if not module:
                return False
                
            # 블루프린트 생성
            blueprint_name = f"plugin_{plugin_name}"
            blueprint = Blueprint(
                blueprint_name,
                __name__,
                url_prefix=f"/api/plugins/{plugin_name}",
                template_folder=f"{self.plugins_dir}/{plugin_name}/templates",
                static_folder=f"{self.plugins_dir}/{plugin_name}/static"
            )
            
            # 모듈에서 블루프린트 등록 함수 호출
            if hasattr(module, 'register_blueprint'):
                module.register_blueprint(blueprint)
            elif hasattr(module, 'bp'):
                blueprint = module.bp
            elif hasattr(module, 'create_plugin'):
                # 플러그인 인스턴스 생성 후 blueprint 속성 확인
                plugin_instance = module.create_plugin()
                if hasattr(plugin_instance, 'blueprint') and plugin_instance.blueprint:
                    blueprint = plugin_instance.blueprint
                else:
                    logger.warning(f"플러그인 {plugin_name}에서 블루프린트를 찾을 수 없습니다")
                    return False
            else:
                logger.warning(f"플러그인 {plugin_name}에서 블루프린트를 찾을 수 없습니다")
                return False
            
            # Flask 앱에 블루프린트 등록
            self.app.register_blueprint(blueprint)
            self.blueprints[plugin_name] = blueprint
            
            logger.info(f"플러그인 {plugin_name} 블루프린트 등록 완료")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 {plugin_name} 블루프린트 등록 실패: {e}")
            return False
    
    def validate_plugin_dependencies(self, plugin_name: str, config: Dict) -> bool:
        """플러그인 의존성 검증"""
        dependencies = config.get('dependencies', [])
        
        for dep in dependencies:
            if dep not in self.loaded_plugins:
                logger.error(f"플러그인 {plugin_name}의 의존성 {dep}이 로드되지 않았습니다")
                return False
                
        return True
    
    def load_plugin(self, plugin_name: str) -> bool:
        """개별 플러그인 로드"""
        try:
            # 설정 로드
            config = self.load_plugin_config(plugin_name)
            if not config:
                return False
                
            # 플러그인이 비활성화된 경우 스킵
            if not config.get('enabled', True):
                logger.info(f"플러그인 {plugin_name}이 비활성화되어 있습니다")
                return False
                
            # 의존성 검증
            if not self.validate_plugin_dependencies(plugin_name, config):
                return False
                
            # 블루프린트 등록
            if not self.register_plugin_blueprint(plugin_name, config):
                return False
                
            # 플러그인 정보 저장
            self.plugins[plugin_name] = config
            self.plugin_configs[plugin_name] = config.get('config', {})
            self.loaded_plugins.append(plugin_name)
            
            logger.info(f"플러그인 {plugin_name} 로드 완료")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 {plugin_name} 로드 실패: {e}")
            return False
    
    def load_all_plugins(self) -> Dict[str, bool]:
        """모든 플러그인 자동 로드"""
        results = {}
        plugin_names = self.discover_plugins()
        
        # 의존성 순서로 정렬 (간단한 위상 정렬)
        sorted_plugins = self._sort_plugins_by_dependencies(plugin_names)
        
        for plugin_name in sorted_plugins:
            success = self.load_plugin(plugin_name)
            results[plugin_name] = success
            
        return results
    
    def _sort_plugins_by_dependencies(self, plugin_names: List[str]) -> List[str]:
        """의존성 순서로 플러그인 정렬"""
        # 간단한 위상 정렬 구현
        sorted_plugins = []
        visited = set()
        temp_visited = set()
        
        def visit(plugin_name):
            if plugin_name in temp_visited:
                raise ValueError(f"순환 의존성 발견: {plugin_name}")
            if plugin_name in visited:
                return
                
            temp_visited.add(plugin_name)
            
            # 의존성 먼저 방문
            config = self.load_plugin_config(plugin_name)
            if config:
                for dep in config.get('dependencies', []):
                    if dep in plugin_names:
                        visit(dep)
                        
            temp_visited.remove(plugin_name)
            visited.add(plugin_name)
            sorted_plugins.append(plugin_name)
        
        for plugin_name in plugin_names:
            if plugin_name not in visited:
                visit(plugin_name)
                
        return sorted_plugins
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """플러그인 언로드"""
        try:
            if plugin_name in self.blueprints:
                # 블루프린트 제거
                blueprint = self.blueprints[plugin_name]
                self.app.blueprints.pop(blueprint.name, None)
                del self.blueprints[plugin_name]
                
            # 플러그인 정보 제거
            self.plugins.pop(plugin_name, None)
            self.plugin_configs.pop(plugin_name, None)
            
            if plugin_name in self.loaded_plugins:
                self.loaded_plugins.remove(plugin_name)
                
            logger.info(f"플러그인 {plugin_name} 언로드 완료")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 {plugin_name} 언로드 실패: {e}")
            return False
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """플러그인 재로드"""
        try:
            # 기존 플러그인 언로드
            self.unload_plugin(plugin_name)
            
            # 플러그인 다시 로드
            return self.load_plugin(plugin_name)
            
        except Exception as e:
            logger.error(f"플러그인 {plugin_name} 재로드 실패: {e}")
            return False
    
    def get_plugin_status(self) -> Dict[str, Any]:
        """플러그인 상태 정보 반환"""
        return {
            'total_plugins': len(self.plugins),
            'loaded_plugins': self.loaded_plugins,
            'plugin_configs': self.plugin_configs,
            'blueprints': list(self.blueprints.keys())
        }
    
    def get_plugin_menus(self) -> List[Dict]:
        """모든 플러그인의 메뉴 정보 반환"""
        menus = []
        
        for plugin_name, config in self.plugins.items():
            plugin_menus = config.get('menus', [])
            for menu in plugin_menus:
                menu['plugin'] = plugin_name
                menus.append(menu)
                
        # order 기준으로 정렬
        menus.sort(key=lambda x: x.get('order', 999))
        return menus
    
    def get_plugin_routes(self) -> List[Dict]:
        """모든 플러그인의 라우트 정보 반환"""
        routes = []
        
        for plugin_name, config in self.plugins.items():
            plugin_routes = config.get('routes', [])
            for route in plugin_routes:
                route['plugin'] = plugin_name
                routes.append(route)
                
        return routes
    
    def update_plugin_config(self, plugin_name: str, config: Dict) -> bool:
        """플러그인 설정 업데이트"""
        try:
            if plugin_name not in self.plugins:
                return False
                
            # 스키마 검증
            is_valid, errors = self.validator.validate_plugin_config(config)
            if not is_valid:
                logger.error(f"플러그인 {plugin_name} 설정 검증 실패: {', '.join(errors)}")
                return False
                
            # 매니페스트 업데이트
            plugin_dir = Path(self.plugins_dir) / plugin_name
            manifest = PluginManifest(plugin_dir)
            manifest.save(config)
                
            # 메모리 설정 업데이트
            self.plugins[plugin_name] = config
            self.plugin_configs[plugin_name] = config.get('config', {})
            
            logger.info(f"플러그인 {plugin_name} 설정 업데이트 완료")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 {plugin_name} 설정 업데이트 실패: {e}")
            return False
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """플러그인 활성화"""
        if plugin_name not in self.plugins:
            return False
            
        config = self.plugins[plugin_name].copy()
        config['enabled'] = True
        config['updated_at'] = datetime.now().isoformat()
        
        return self.update_plugin_config(plugin_name, config)
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """플러그인 비활성화"""
        if plugin_name not in self.plugins:
            return False
            
        config = self.plugins[plugin_name].copy()
        config['enabled'] = False
        config['updated_at'] = datetime.now().isoformat()
        
        return self.update_plugin_config(plugin_name, config) 