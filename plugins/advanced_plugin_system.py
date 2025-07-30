"""
고급 플러그인 시스템
엔터프라이즈급 플러그인 관리 및 확장 시스템
"""

import os
import sys
import json
import yaml
import zipfile
import shutil
import importlib
import inspect
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import logging
from pathlib import Path
import hashlib
import requests
from dataclasses import dataclass, asdict
import threading
import time

# 로깅 설정
logging.basicConfig(level=logging.INFO)
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
    api_version: str
    min_system_version: str
    max_system_version: str
    tags: List[str]
    icon: str
    homepage: str
    repository: str
    license: str
    created_at: str
    updated_at: str
    status: str  # active, inactive, error, updating
    install_path: str
    config_schema: Dict[str, Any]
    hooks: List[str]
    commands: List[str]
    events: List[str]

@dataclass
class PluginConfig:
    """플러그인 설정"""
    enabled: bool
    auto_update: bool
    debug_mode: bool
    custom_settings: Dict[str, Any]
    api_keys: Dict[str, str]
    webhooks: List[str]
    schedules: List[Dict[str, Any]]

class AdvancedPluginManager:
    """고급 플러그인 관리자"""
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(exist_ok=True)
        
        self.plugins: Dict[str, PluginMetadata] = {}
        self.configs: Dict[str, PluginConfig] = {}
        self.instances: Dict[str, Any] = {}
        self.hooks: Dict[str, List[Callable]] = {}
        self.commands: Dict[str, Callable] = {}
        self.events: Dict[str, List[Callable]] = {}
        
        self.plugin_registry_file = self.plugins_dir / "registry.json"
        self.config_file = self.plugins_dir / "config.json"
        
        self.load_registry()
        self.load_configs()
        self.scan_plugins()
    
    def load_registry(self):
        """플러그인 레지스트리 로드"""
        if self.plugin_registry_file.exists():
            try:
                with open(self.plugin_registry_file, 'r', encoding='utf-8') as f:
                    registry_data = json.load(f)
                    for plugin_data in registry_data.values():
                        self.plugins[plugin_data['name']] = PluginMetadata(**plugin_data)
            except Exception as e:
                logger.error(f"레지스트리 로드 오류: {e}")
    
    def save_registry(self):
        """플러그인 레지스트리 저장"""
        try:
            registry_data = {
                name: asdict(metadata) 
                for name, metadata in self.plugins.items()
            }
            with open(self.plugin_registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"레지스트리 저장 오류: {e}")
    
    def load_configs(self):
        """플러그인 설정 로드"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    for name, config in config_data.items():
                        self.configs[name] = PluginConfig(**config)
            except Exception as e:
                logger.error(f"설정 로드 오류: {e}")
    
    def save_configs(self):
        """플러그인 설정 저장"""
        try:
            config_data = {
                name: asdict(config) 
                for name, config in self.configs.items()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"설정 저장 오류: {e}")
    
    def scan_plugins(self):
        """플러그인 스캔"""
        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir() and (plugin_dir / "plugin.json").exists():
                try:
                    self.load_plugin_metadata(plugin_dir)
                except Exception as e:
                    logger.error(f"플러그인 스캔 오류 {plugin_dir.name}: {e}")
    
    def load_plugin_metadata(self, plugin_dir: Path):
        """플러그인 메타데이터 로드"""
        metadata_file = plugin_dir / "plugin.json"
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # 기본값 설정
        metadata.setdefault('status', 'inactive')
        metadata.setdefault('install_path', str(plugin_dir))
        metadata.setdefault('created_at', datetime.now().isoformat())
        metadata.setdefault('updated_at', datetime.now().isoformat())
        
        plugin_name = metadata['name']
        self.plugins[plugin_name] = PluginMetadata(**metadata)
        
        # 기본 설정 생성
        if plugin_name not in self.configs:
            self.configs[plugin_name] = PluginConfig(
                enabled=False,
                auto_update=True,
                debug_mode=False,
                custom_settings={},
                api_keys={},
                webhooks=[],
                schedules=[]
            )
    
    def install_plugin(self, plugin_path: str, source: str = "local") -> bool:
        """플러그인 설치"""
        try:
            plugin_path = Path(plugin_path)
            
            if source == "zip":
                # ZIP 파일에서 설치
                with zipfile.ZipFile(plugin_path, 'r') as zip_ref:
                    # 임시 디렉토리에 압축 해제
                    temp_dir = self.plugins_dir / f"temp_{plugin_path.stem}"
                    zip_ref.extractall(temp_dir)
                    
                    # plugin.json 찾기
                    plugin_json = None
                    for root, dirs, files in os.walk(temp_dir):
                        if "plugin.json" in files:
                            plugin_json = Path(root) / "plugin.json"
                            break
                    
                    if not plugin_json:
                        raise ValueError("plugin.json 파일을 찾을 수 없습니다")
                    
                    # 메타데이터 로드
                    with open(plugin_json, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    plugin_name = metadata['name']
                    install_dir = self.plugins_dir / plugin_name
                    
                    # 기존 설치 제거
                    if install_dir.exists():
                        shutil.rmtree(install_dir)
                    
                    # 새로 설치
                    shutil.move(str(plugin_json.parent), str(install_dir))
                    shutil.rmtree(temp_dir)
                    
            else:
                # 로컬 디렉토리에서 설치
                if not (plugin_path / "plugin.json").exists():
                    raise ValueError("plugin.json 파일을 찾을 수 없습니다")
                
                plugin_name = plugin_path.name
                install_dir = self.plugins_dir / plugin_name
                
                if install_dir.exists():
                    shutil.rmtree(install_dir)
                
                shutil.copytree(plugin_path, install_dir)
            
            # 메타데이터 로드
            self.load_plugin_metadata(install_dir)
            
            # 의존성 확인
            if not self.check_dependencies(plugin_name):
                logger.warning(f"플러그인 {plugin_name}의 의존성이 충족되지 않습니다")
            
            # 레지스트리 저장
            self.save_registry()
            
            logger.info(f"플러그인 {plugin_name} 설치 완료")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 설치 오류: {e}")
            return False
    
    def uninstall_plugin(self, plugin_name: str) -> bool:
        """플러그인 제거"""
        try:
            if plugin_name not in self.plugins:
                raise ValueError(f"플러그인 {plugin_name}이 설치되지 않았습니다")
            
            # 플러그인 비활성화
            self.disable_plugin(plugin_name)
            
            # 설치 디렉토리 제거
            install_dir = Path(self.plugins[plugin_name].install_path)
            if install_dir.exists():
                shutil.rmtree(install_dir)
            
            # 레지스트리에서 제거
            del self.plugins[plugin_name]
            if plugin_name in self.configs:
                del self.configs[plugin_name]
            if plugin_name in self.instances:
                del self.instances[plugin_name]
            
            # 레지스트리 저장
            self.save_registry()
            self.save_configs()
            
            logger.info(f"플러그인 {plugin_name} 제거 완료")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 제거 오류: {e}")
            return False
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """플러그인 활성화"""
        try:
            if plugin_name not in self.plugins:
                raise ValueError(f"플러그인 {plugin_name}이 설치되지 않았습니다")
            
            # 의존성 확인
            if not self.check_dependencies(plugin_name):
                raise ValueError(f"플러그인 {plugin_name}의 의존성이 충족되지 않습니다")
            
            # 플러그인 로드
            if self.load_plugin_instance(plugin_name):
                self.configs[plugin_name].enabled = True
                self.plugins[plugin_name].status = "active"
                self.save_configs()
                self.save_registry()
                
                logger.info(f"플러그인 {plugin_name} 활성화 완료")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"플러그인 활성화 오류: {e}")
            return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """플러그인 비활성화"""
        try:
            if plugin_name not in self.plugins:
                raise ValueError(f"플러그인 {plugin_name}이 설치되지 않았습니다")
            
            # 플러그인 언로드
            if plugin_name in self.instances:
                self.unload_plugin_instance(plugin_name)
            
            self.configs[plugin_name].enabled = False
            self.plugins[plugin_name].status = "inactive"
            self.save_configs()
            self.save_registry()
            
            logger.info(f"플러그인 {plugin_name} 비활성화 완료")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 비활성화 오류: {e}")
            return False
    
    def load_plugin_instance(self, plugin_name: str) -> bool:
        """플러그인 인스턴스 로드"""
        try:
            plugin_metadata = self.plugins[plugin_name]
            install_dir = Path(plugin_metadata.install_path)
            
            # 메인 모듈 로드
            main_file = install_dir / "main.py"
            if not main_file.exists():
                raise ValueError("main.py 파일을 찾을 수 없습니다")
            
            # 모듈 경로 설정
            sys.path.insert(0, str(install_dir))
            
            # 모듈 로드
            spec = importlib.util.spec_from_file_location(plugin_name, main_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 플러그인 클래스 찾기
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and hasattr(obj, 'name') and obj.name == plugin_name:
                    plugin_class = obj
                    break
            
            if not plugin_class:
                raise ValueError("플러그인 클래스를 찾을 수 없습니다")
            
            # 인스턴스 생성
            instance = plugin_class()
            
            # 초기화
            if hasattr(instance, 'initialize'):
                instance.initialize()
            
            # 훅 등록
            self.register_plugin_hooks(plugin_name, instance)
            
            # 명령어 등록
            self.register_plugin_commands(plugin_name, instance)
            
            # 이벤트 등록
            self.register_plugin_events(plugin_name, instance)
            
            self.instances[plugin_name] = instance
            
            logger.info(f"플러그인 {plugin_name} 인스턴스 로드 완료")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 인스턴스 로드 오류: {e}")
            return False
    
    def unload_plugin_instance(self, plugin_name: str):
        """플러그인 인스턴스 언로드"""
        try:
            if plugin_name in self.instances:
                instance = self.instances[plugin_name]
                
                # 정리
                if hasattr(instance, 'cleanup'):
                    instance.cleanup()
                
                # 훅 제거
                self.unregister_plugin_hooks(plugin_name)
                
                # 명령어 제거
                self.unregister_plugin_commands(plugin_name)
                
                # 이벤트 제거
                self.unregister_plugin_events(plugin_name)
                
                del self.instances[plugin_name]
                
                logger.info(f"플러그인 {plugin_name} 인스턴스 언로드 완료")
                
        except Exception as e:
            logger.error(f"플러그인 인스턴스 언로드 오류: {e}")
    
    def register_plugin_hooks(self, plugin_name: str, instance: Any):
        """플러그인 훅 등록"""
        if hasattr(instance, 'hooks'):
            for hook_name, hook_func in instance.hooks.items():
                if hook_name not in self.hooks:
                    self.hooks[hook_name] = []
                self.hooks[hook_name].append(hook_func)
    
    def unregister_plugin_hooks(self, plugin_name: str):
        """플러그인 훅 제거"""
        # 플러그인 관련 훅 제거 로직
        pass
    
    def register_plugin_commands(self, plugin_name: str, instance: Any):
        """플러그인 명령어 등록"""
        if hasattr(instance, 'commands'):
            for cmd_name, cmd_func in instance.commands.items():
                self.commands[f"{plugin_name}:{cmd_name}"] = cmd_func
    
    def unregister_plugin_commands(self, plugin_name: str):
        """플러그인 명령어 제거"""
        commands_to_remove = [cmd for cmd in self.commands.keys() if cmd.startswith(f"{plugin_name}:")]
        for cmd in commands_to_remove:
            del self.commands[cmd]
    
    def register_plugin_events(self, plugin_name: str, instance: Any):
        """플러그인 이벤트 등록"""
        if hasattr(instance, 'events'):
            for event_name, event_func in instance.events.items():
                if event_name not in self.events:
                    self.events[event_name] = []
                self.events[event_name].append(event_func)
    
    def unregister_plugin_events(self, plugin_name: str):
        """플러그인 이벤트 제거"""
        # 플러그인 관련 이벤트 제거 로직
        pass
    
    def check_dependencies(self, plugin_name: str) -> bool:
        """의존성 확인"""
        if plugin_name not in self.plugins:
            return False
        
        dependencies = self.plugins[plugin_name].dependencies
        
        for dep in dependencies:
            if dep not in self.plugins or self.plugins[dep].status != "active":
                return False
        
        return True
    
    def execute_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """훅 실행"""
        results = []
        
        if hook_name in self.hooks:
            for hook_func in self.hooks[hook_name]:
                try:
                    result = hook_func(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    logger.error(f"훅 실행 오류 {hook_name}: {e}")
        
        return results
    
    def execute_command(self, command: str, *args, **kwargs) -> Any:
        """명령어 실행"""
        if command in self.commands:
            try:
                return self.commands[command](*args, **kwargs)
            except Exception as e:
                logger.error(f"명령어 실행 오류 {command}: {e}")
                return None
        
        raise ValueError(f"명령어를 찾을 수 없습니다: {command}")
    
    def trigger_event(self, event_name: str, *args, **kwargs):
        """이벤트 트리거"""
        if event_name in self.events:
            for event_func in self.events[event_name]:
                try:
                    event_func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"이벤트 실행 오류 {event_name}: {e}")
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """플러그인 정보 조회"""
        if plugin_name not in self.plugins:
            return None
        
        metadata = self.plugins[plugin_name]
        config = self.configs.get(plugin_name)
        
        return {
            'metadata': asdict(metadata),
            'config': asdict(config) if config else None,
            'instance_loaded': plugin_name in self.instances
        }
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """플러그인 목록 조회"""
        plugins_info = []
        
        for name, metadata in self.plugins.items():
            config = self.configs.get(name)
            plugins_info.append({
                'name': name,
                'metadata': asdict(metadata),
                'config': asdict(config) if config else None,
                'instance_loaded': name in self.instances
            })
        
        return plugins_info
    
    def update_plugin(self, plugin_name: str) -> bool:
        """플러그인 업데이트"""
        try:
            if plugin_name not in self.plugins:
                raise ValueError(f"플러그인 {plugin_name}이 설치되지 않았습니다")
            
            metadata = self.plugins[plugin_name]
            
            # 업데이트 URL 확인
            if not metadata.repository:
                raise ValueError("업데이트 URL이 설정되지 않았습니다")
            
            # 현재 버전 확인
            current_version = metadata.version
            
            # 업데이트 확인
            # 실제 구현에서는 API를 통해 최신 버전 확인
            latest_version = self.check_latest_version(plugin_name)
            
            if latest_version == current_version:
                logger.info(f"플러그인 {plugin_name}은 최신 버전입니다")
                return True
            
            # 업데이트 다운로드 및 설치
            if self.download_update(plugin_name, latest_version):
                # 플러그인 재시작
                if self.configs[plugin_name].enabled:
                    self.disable_plugin(plugin_name)
                    self.enable_plugin(plugin_name)
                
                logger.info(f"플러그인 {plugin_name} 업데이트 완료: {current_version} -> {latest_version}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"플러그인 업데이트 오류: {e}")
            return False
    
    def check_latest_version(self, plugin_name: str) -> str:
        """최신 버전 확인"""
        # 실제 구현에서는 API를 통해 확인
        return "1.0.0"
    
    def download_update(self, plugin_name: str, version: str) -> bool:
        """업데이트 다운로드"""
        # 실제 구현에서는 다운로드 로직
        return True
    
    def backup_plugin(self, plugin_name: str) -> str:
        """플러그인 백업"""
        try:
            if plugin_name not in self.plugins:
                raise ValueError(f"플러그인 {plugin_name}이 설치되지 않았습니다")
            
            metadata = self.plugins[plugin_name]
            install_dir = Path(metadata.install_path)
            
            # 백업 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{plugin_name}_{metadata.version}_{timestamp}.zip"
            backup_path = self.plugins_dir / "backups" / backup_filename
            
            # 백업 디렉토리 생성
            backup_path.parent.mkdir(exist_ok=True)
            
            # ZIP 파일 생성
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(install_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(install_dir)
                        zipf.write(file_path, arcname)
            
            logger.info(f"플러그인 {plugin_name} 백업 완료: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"플러그인 백업 오류: {e}")
            return ""
    
    def restore_plugin(self, backup_path: str) -> bool:
        """플러그인 복원"""
        try:
            backup_path = Path(backup_path)
            
            if not backup_path.exists():
                raise ValueError("백업 파일을 찾을 수 없습니다")
            
            # 임시 디렉토리에 압축 해제
            temp_dir = self.plugins_dir / f"temp_restore_{backup_path.stem}"
            with zipfile.ZipFile(backup_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # plugin.json 찾기
            plugin_json = None
            for root, dirs, files in os.walk(temp_dir):
                if "plugin.json" in files:
                    plugin_json = Path(root) / "plugin.json"
                    break
            
            if not plugin_json:
                raise ValueError("plugin.json 파일을 찾을 수 없습니다")
            
            # 메타데이터 로드
            with open(plugin_json, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            plugin_name = metadata['name']
            
            # 기존 플러그인 제거
            if plugin_name in self.plugins:
                self.uninstall_plugin(plugin_name)
            
            # 복원
            install_dir = self.plugins_dir / plugin_name
            shutil.move(str(plugin_json.parent), str(install_dir))
            shutil.rmtree(temp_dir)
            
            # 메타데이터 로드
            self.load_plugin_metadata(install_dir)
            self.save_registry()
            
            logger.info(f"플러그인 {plugin_name} 복원 완료")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 복원 오류: {e}")
            return False

# 플러그인 기본 클래스
class BasePlugin:
    """플러그인 기본 클래스"""
    
    def __init__(self):
        self.name = ""
        self.version = "1.0.0"
        self.description = ""
        self.author = ""
        self.category = "general"
        self.dependencies = []
        self.permissions = []
        self.api_version = "1.0"
        self.min_system_version = "1.0.0"
        self.max_system_version = "2.0.0"
        self.tags = []
        self.icon = ""
        self.homepage = ""
        self.repository = ""
        self.license = "MIT"
        
        self.hooks = {}
        self.commands = {}
        self.events = {}
        
        self.config = {}
        self.logger = logging.getLogger(f"plugin.{self.name}")
    
    def initialize(self):
        """플러그인 초기화"""
        pass
    
    def cleanup(self):
        """플러그인 정리"""
        pass
    
    def on_enable(self):
        """플러그인 활성화 시 호출"""
        pass
    
    def on_disable(self):
        """플러그인 비활성화 시 호출"""
        pass
    
    def on_config_change(self, config: Dict[str, Any]):
        """설정 변경 시 호출"""
        self.config = config
    
    def get_config(self) -> Dict[str, Any]:
        """설정 조회"""
        return self.config
    
    def set_config(self, config: Dict[str, Any]):
        """설정 변경"""
        self.config = config
        self.on_config_change(config)

# 사용 예시
if __name__ == "__main__":
    # 플러그인 매니저 초기화
    plugin_manager = AdvancedPluginManager()
    
    # 플러그인 목록 조회
    plugins = plugin_manager.list_plugins()
    print(f"설치된 플러그인: {len(plugins)}개")
    
    for plugin in plugins:
        print(f"- {plugin['name']} v{plugin['metadata']['version']} ({plugin['metadata']['status']})")
    
    # 플러그인 활성화
    for plugin in plugins:
        if plugin['metadata']['status'] == 'inactive':
            plugin_manager.enable_plugin(plugin['name'])
    
    # 훅 실행 예시
    results = plugin_manager.execute_hook('before_request', {'url': '/api/test'})
    print(f"훅 실행 결과: {results}")
    
    # 명령어 실행 예시
    try:
        result = plugin_manager.execute_command('test:hello', 'world')
        print(f"명령어 실행 결과: {result}")
    except ValueError:
        print("명령어를 찾을 수 없습니다")
    
    # 이벤트 트리거 예시
    plugin_manager.trigger_event('user_login', {'user_id': 123, 'timestamp': datetime.now()}) 