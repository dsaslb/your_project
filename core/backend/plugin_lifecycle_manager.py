#!/usr/bin/env python3
"""
플러그인 생명주기 관리 시스템
플러그인의 설치, 활성화, 비활성화, 업데이트, 제거 등의 생명주기를 관리
"""

import logging
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import threading
import time

logger = logging.getLogger(__name__)

class PluginState(Enum):
    """플러그인 상태"""
    INSTALLED = "installed"
    ACTIVATED = "activated"
    DEACTIVATED = "deactivated"
    UPDATING = "updating"
    ERROR = "error"
    REMOVED = "removed"

class PluginLifecycleEvent(Enum):
    """플러그인 생명주기 이벤트"""
    INSTALLED = "installed"
    ACTIVATED = "activated"
    DEACTIVATED = "deactivated"
    UPDATED = "updated"
    REMOVED = "removed"
    ERROR = "error"

class PluginLifecycleManager:
    """플러그인 생명주기 관리자"""
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(exist_ok=True)
        
        # 플러그인 상태 관리
        self.plugin_states: Dict[str, Dict[str, Any]] = {}
        self.plugin_metadata: Dict[str, Dict[str, Any]] = {}
        
        # 생명주기 이벤트 리스너
        self.event_listeners: Dict[PluginLifecycleEvent, List[Callable]] = {
            event: [] for event in PluginLifecycleEvent
        }
        
        # 플러그인 의존성 관리
        self.dependency_graph: Dict[str, List[str]] = {}
        
        # 업데이트 관리
        self.update_queue: List[Dict[str, Any]] = []
        self.update_running = False
        self.update_thread = None
        
        # 플러그인 검증
        self.validation_rules = {
            'required_files': ['config/plugin.json', 'backend/main.py'],
            'required_config_fields': ['name', 'version', 'description', 'author'],
            'max_plugin_size': 100 * 1024 * 1024,  # 100MB
            'allowed_extensions': ['.py', '.json', '.html', '.css', '.js', '.md']
        }
        
    def register_event_listener(self, event: PluginLifecycleEvent, callback: Callable):
        """이벤트 리스너 등록"""
        if event not in self.event_listeners:
            self.event_listeners[event] = []
        self.event_listeners[event].append(callback)
        
    def _trigger_event(self, event: PluginLifecycleEvent, plugin_name: str, data: Optional[Dict[str, Any]] = None):
        """이벤트 트리거"""
        event_data = {
            'event': event.value,
            'plugin_name': plugin_name,
            'timestamp': datetime.now().isoformat(),
            'data': data or {}
        }
        
        logger.info(f"플러그인 생명주기 이벤트: {event.value} - {plugin_name}")
        
        # 이벤트 리스너 호출
        for callback in self.event_listeners.get(event, []):
            try:
                callback(event_data)
            except Exception as e:
                logger.error(f"이벤트 리스너 오류: {e}")
                
    def install_plugin(self, plugin_source: str, plugin_name: Optional[str] = None) -> Dict[str, Any]:
        """플러그인 설치"""
        try:
            plugin_source_path = Path(plugin_source)
            
            if not plugin_source_path.exists():
                raise FileNotFoundError(f"플러그인 소스를 찾을 수 없습니다: {plugin_source}")
                
            # 플러그인 이름 결정
            if plugin_name is None:
                plugin_name = plugin_source_path.name
                
            plugin_dest_path = self.plugins_dir / plugin_name
            
            # 기존 플러그인 확인
            if plugin_dest_path.exists():
                raise FileExistsError(f"플러그인 {plugin_name}이 이미 존재합니다")
                
            # 플러그인 검증
            validation_result = self._validate_plugin_source(plugin_source_path)
            if not validation_result['valid']:
                raise ValueError(f"플러그인 검증 실패: {validation_result['errors']}")
                
            # 플러그인 복사
            if plugin_source_path.is_dir():
                shutil.copytree(plugin_source_path, plugin_dest_path)
            else:
                # 압축 파일인 경우
                import zipfile
                with zipfile.ZipFile(plugin_source_path, 'r') as zipf:
                    zipf.extractall(plugin_dest_path)
                    
            # 플러그인 메타데이터 로드
            metadata = self._load_plugin_metadata(plugin_dest_path)
            
            # 플러그인 상태 초기화
            self.plugin_states[plugin_name] = {
                'state': PluginState.INSTALLED.value,
                'installed_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'version': metadata.get('version', '1.0.0'),
                'dependencies': metadata.get('dependencies', []),
                'errors': []
            }
            
            self.plugin_metadata[plugin_name] = metadata
            
            # 의존성 그래프 업데이트
            self._update_dependency_graph(plugin_name, metadata.get('dependencies', []))
            
            # 이벤트 트리거
            self._trigger_event(PluginLifecycleEvent.INSTALLED, plugin_name, {
                'metadata': metadata,
                'install_path': str(plugin_dest_path)
            })
            
            logger.info(f"플러그인 설치 완료: {plugin_name}")
            
            return {
                'success': True,
                'plugin_name': plugin_name,
                'metadata': metadata,
                'install_path': str(plugin_dest_path)
            }
            
        except Exception as e:
            logger.error(f"플러그인 설치 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def activate_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """플러그인 활성화"""
        try:
            if plugin_name not in self.plugin_states:
                raise ValueError(f"플러그인 {plugin_name}이 설치되지 않았습니다")
                
            plugin_state = self.plugin_states[plugin_name]
            
            if plugin_state['state'] == PluginState.ACTIVATED.value:
                return {'success': True, 'message': '이미 활성화된 플러그인입니다'}
                
            # 의존성 검사
            dependencies = plugin_state.get('dependencies', [])
            for dep in dependencies:
                if dep not in self.plugin_states:
                    raise ValueError(f"의존성 플러그인 {dep}이 설치되지 않았습니다")
                if self.plugin_states[dep]['state'] != PluginState.ACTIVATED.value:
                    raise ValueError(f"의존성 플러그인 {dep}이 활성화되지 않았습니다")
                    
            # 플러그인 검증
            validation_result = self._validate_installed_plugin(plugin_name)
            if not validation_result['valid']:
                plugin_state['errors'] = validation_result['errors']
                plugin_state['state'] = PluginState.ERROR.value
                self._trigger_event(PluginLifecycleEvent.ERROR, plugin_name, {
                    'errors': validation_result['errors']
                })
                raise ValueError(f"플러그인 검증 실패: {validation_result['errors']}")
                
            # 플러그인 활성화
            plugin_state['state'] = PluginState.ACTIVATED.value
            plugin_state['activated_at'] = datetime.now().isoformat()
            plugin_state['errors'] = []
            
            # 이벤트 트리거
            self._trigger_event(PluginLifecycleEvent.ACTIVATED, plugin_name, {
                'metadata': self.plugin_metadata.get(plugin_name, {})
            })
            
            logger.info(f"플러그인 활성화 완료: {plugin_name}")
            
            return {
                'success': True,
                'plugin_name': plugin_name,
                'state': PluginState.ACTIVATED.value
            }
            
        except Exception as e:
            logger.error(f"플러그인 활성화 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def deactivate_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """플러그인 비활성화"""
        try:
            if plugin_name not in self.plugin_states:
                raise ValueError(f"플러그인 {plugin_name}이 설치되지 않았습니다")
                
            plugin_state = self.plugin_states[plugin_name]
            
            if plugin_state['state'] != PluginState.ACTIVATED.value:
                return {'success': True, 'message': '이미 비활성화된 플러그인입니다'}
                
            # 의존성 체크 (다른 플러그인이 이 플러그인에 의존하는지)
            dependent_plugins = self._get_dependent_plugins(plugin_name)
            if dependent_plugins:
                raise ValueError(f"다음 플러그인들이 {plugin_name}에 의존하고 있습니다: {dependent_plugins}")
                
            # 플러그인 비활성화
            plugin_state['state'] = PluginState.DEACTIVATED.value
            plugin_state['deactivated_at'] = datetime.now().isoformat()
            
            # 이벤트 트리거
            self._trigger_event(PluginLifecycleEvent.DEACTIVATED, plugin_name, {
                'metadata': self.plugin_metadata.get(plugin_name, {})
            })
            
            logger.info(f"플러그인 비활성화 완료: {plugin_name}")
            
            return {
                'success': True,
                'plugin_name': plugin_name,
                'state': PluginState.DEACTIVATED.value
            }
            
        except Exception as e:
            logger.error(f"플러그인 비활성화 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def update_plugin(self, plugin_name: str, update_source: str) -> Dict[str, Any]:
        """플러그인 업데이트"""
        try:
            if plugin_name not in self.plugin_states:
                raise ValueError(f"플러그인 {plugin_name}이 설치되지 않았습니다")
                
            # 업데이트 큐에 추가
            update_info = {
                'plugin_name': plugin_name,
                'update_source': update_source,
                'queued_at': datetime.now().isoformat(),
                'status': 'queued'
            }
            
            self.update_queue.append(update_info)
            
            # 업데이트 스레드 시작
            if not self.update_running:
                self._start_update_thread()
                
            return {
                'success': True,
                'message': f'플러그인 {plugin_name} 업데이트가 큐에 추가되었습니다',
                'queue_position': len(self.update_queue)
            }
            
        except Exception as e:
            logger.error(f"플러그인 업데이트 큐 추가 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def remove_plugin(self, plugin_name: str, force: bool = False) -> Dict[str, Any]:
        """플러그인 제거"""
        try:
            if plugin_name not in self.plugin_states:
                raise ValueError(f"플러그인 {plugin_name}이 설치되지 않았습니다")
                
            plugin_state = self.plugin_states[plugin_name]
            
            # 활성화된 플러그인 체크
            if plugin_state['state'] == PluginState.ACTIVATED.value and not force:
                raise ValueError(f"활성화된 플러그인 {plugin_name}을 제거하려면 force=True를 사용하세요")
                
            # 의존성 체크
            dependent_plugins = self._get_dependent_plugins(plugin_name)
            if dependent_plugins and not force:
                raise ValueError(f"다음 플러그인들이 {plugin_name}에 의존하고 있습니다: {dependent_plugins}")
                
            # 플러그인 디렉토리 제거
            plugin_path = self.plugins_dir / plugin_name
            if plugin_path.exists():
                shutil.rmtree(plugin_path)
                
            # 상태 정보 제거
            del self.plugin_states[plugin_name]
            if plugin_name in self.plugin_metadata:
                del self.plugin_metadata[plugin_name]
                
            # 의존성 그래프에서 제거
            if plugin_name in self.dependency_graph:
                del self.dependency_graph[plugin_name]
                
            # 이벤트 트리거
            self._trigger_event(PluginLifecycleEvent.REMOVED, plugin_name, {
                'force': force
            })
            
            logger.info(f"플러그인 제거 완료: {plugin_name}")
            
            return {
                'success': True,
                'plugin_name': plugin_name,
                'removed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"플러그인 제거 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def _start_update_thread(self):
        """업데이트 스레드 시작"""
        self.update_running = True
        self.update_thread = threading.Thread(target=self._update_worker, daemon=True)
        self.update_thread.start()
        
    def _update_worker(self):
        """업데이트 워커 스레드"""
        while self.update_running and self.update_queue:
            try:
                update_info = self.update_queue.pop(0)
                plugin_name = update_info['plugin_name']
                update_source = update_info['update_source']
                
                # 플러그인 상태를 업데이트 중으로 변경
                if plugin_name in self.plugin_states:
                    self.plugin_states[plugin_name]['state'] = PluginState.UPDATING.value
                    
                # 백업 생성
                backup_result = self._create_plugin_backup(plugin_name)
                
                try:
                    # 플러그인 업데이트
                    update_result = self._perform_plugin_update(plugin_name, update_source)
                    
                    if update_result['success']:
                        # 업데이트 성공
                        if plugin_name in self.plugin_states:
                            self.plugin_states[plugin_name]['state'] = PluginState.INSTALLED.value
                            self.plugin_states[plugin_name]['last_updated'] = datetime.now().isoformat()
                            
                        self._trigger_event(PluginLifecycleEvent.UPDATED, plugin_name, {
                            'backup_path': backup_result.get('backup_path'),
                            'new_version': update_result.get('new_version')
                        })
                        
                        logger.info(f"플러그인 업데이트 완료: {plugin_name}")
                    else:
                        # 업데이트 실패 시 백업에서 복구
                        self._restore_plugin_backup(plugin_name, backup_result.get('backup_path'))
                        if plugin_name in self.plugin_states:
                            self.plugin_states[plugin_name]['state'] = PluginState.ERROR.value
                            self.plugin_states[plugin_name]['errors'].append(update_result.get('error'))
                            
                        self._trigger_event(PluginLifecycleEvent.ERROR, plugin_name, {
                            'error': update_result.get('error'),
                            'backup_restored': True
                        })
                        
                        logger.error(f"플러그인 업데이트 실패: {plugin_name} - {update_result.get('error')}")
                        
                except Exception as e:
                    # 예외 발생 시 백업에서 복구
                    self._restore_plugin_backup(plugin_name, backup_result.get('backup_path'))
                    if plugin_name in self.plugin_states:
                        self.plugin_states[plugin_name]['state'] = PluginState.ERROR.value
                        self.plugin_states[plugin_name]['errors'].append(str(e))
                        
                    self._trigger_event(PluginLifecycleEvent.ERROR, plugin_name, {
                        'error': str(e),
                        'backup_restored': True
                    })
                    
                    logger.error(f"플러그인 업데이트 중 예외 발생: {plugin_name} - {e}")
                    
            except Exception as e:
                logger.error(f"업데이트 워커 오류: {e}")
                time.sleep(5)
                
        self.update_running = False
        
    def _create_plugin_backup(self, plugin_name: str) -> Dict[str, Any]:
        """플러그인 백업 생성"""
        try:
            plugin_path = self.plugins_dir / plugin_name
            if not plugin_path.exists():
                return {'success': False, 'error': '플러그인 경로가 존재하지 않습니다'}
                
            backup_dir = Path("backups/plugins")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{plugin_name}_backup_{timestamp}"
            backup_path = backup_dir / backup_name
            
            shutil.copytree(plugin_path, backup_path)
            
            return {
                'success': True,
                'backup_path': str(backup_path)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
            
    def _restore_plugin_backup(self, plugin_name: str, backup_path: Optional[str]):
        """플러그인 백업에서 복구"""
        try:
            if not backup_path:
                return
                
            plugin_path = self.plugins_dir / plugin_name
            backup_path_obj = Path(backup_path)
            
            if backup_path_obj.exists():
                if plugin_path.exists():
                    shutil.rmtree(plugin_path)
                shutil.copytree(backup_path_obj, plugin_path)
                
        except Exception as e:
            logger.error(f"플러그인 백업 복구 실패: {e}")
            
    def _perform_plugin_update(self, plugin_name: str, update_source: str) -> Dict[str, Any]:
        """플러그인 업데이트 수행"""
        try:
            plugin_path = self.plugins_dir / plugin_name
            update_source_path = Path(update_source)
            
            if not update_source_path.exists():
                return {'success': False, 'error': '업데이트 소스를 찾을 수 없습니다'}
                
            # 기존 플러그인 백업
            temp_backup = plugin_path.with_suffix('.backup')
            shutil.copytree(plugin_path, temp_backup)
            
            try:
                # 플러그인 업데이트
                if update_source_path.is_dir():
                    # 디렉토리에서 업데이트
                    for item in update_source_path.iterdir():
                        dest_item = plugin_path / item.name
                        if item.is_dir():
                            if dest_item.exists():
                                shutil.rmtree(dest_item)
                            shutil.copytree(item, dest_item)
                        else:
                            shutil.copy2(item, dest_item)
                else:
                    # 압축 파일에서 업데이트
                    import zipfile
                    with zipfile.ZipFile(update_source_path, 'r') as zipf:
                        zipf.extractall(plugin_path)
                        
                # 업데이트된 메타데이터 로드
                new_metadata = self._load_plugin_metadata(plugin_path)
                
                # 백업 정리
                shutil.rmtree(temp_backup)
                
                return {
                    'success': True,
                    'new_version': new_metadata.get('version'),
                    'metadata': new_metadata
                }
                
            except Exception as e:
                # 업데이트 실패 시 백업에서 복구
                if temp_backup.exists():
                    shutil.rmtree(plugin_path)
                    shutil.copytree(temp_backup, plugin_path)
                    shutil.rmtree(temp_backup)
                raise
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
            
    def _validate_plugin_source(self, source_path: Path) -> Dict[str, Any]:
        """플러그인 소스 검증"""
        errors = []
        
        # 필수 파일 체크
        for required_file in self.validation_rules['required_files']:
            if not (source_path / required_file).exists():
                errors.append(f"필수 파일이 없습니다: {required_file}")
                
        # 설정 파일 검증
        config_file = source_path / 'config' / 'plugin.json'
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                for field in self.validation_rules['required_config_fields']:
                    if field not in config:
                        errors.append(f"필수 설정 필드가 없습니다: {field}")
                        
            except Exception as e:
                errors.append(f"설정 파일 파싱 오류: {e}")
                
        # 크기 체크
        total_size = sum(f.stat().st_size for f in source_path.rglob('*') if f.is_file())
        if total_size > self.validation_rules['max_plugin_size']:
            errors.append(f"플러그인 크기가 너무 큽니다: {total_size} bytes")
            
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
        
    def _validate_installed_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """설치된 플러그인 검증"""
        plugin_path = self.plugins_dir / plugin_name
        return self._validate_plugin_source(plugin_path)
        
    def _load_plugin_metadata(self, plugin_path: Path) -> Dict[str, Any]:
        """플러그인 메타데이터 로드"""
        config_file = plugin_path / 'config' / 'plugin.json'
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"플러그인 메타데이터 로드 실패: {e}")
                
        return {}
        
    def _update_dependency_graph(self, plugin_name: str, dependencies: List[str]):
        """의존성 그래프 업데이트"""
        self.dependency_graph[plugin_name] = dependencies
        
    def _get_dependent_plugins(self, plugin_name: str) -> List[str]:
        """의존하는 플러그인 목록 조회"""
        dependent_plugins = []
        
        for plugin, deps in self.dependency_graph.items():
            if plugin_name in deps:
                dependent_plugins.append(plugin)
                
        return dependent_plugins
        
    def get_plugin_status(self, plugin_name: str) -> Dict[str, Any]:
        """플러그인 상태 조회"""
        if plugin_name not in self.plugin_states:
            return {'error': '플러그인이 설치되지 않았습니다'}
            
        return {
            'plugin_name': plugin_name,
            'state': self.plugin_states[plugin_name],
            'metadata': self.plugin_metadata.get(plugin_name, {}),
            'dependencies': self.dependency_graph.get(plugin_name, [])
        }
        
    def get_all_plugins_status(self) -> Dict[str, Any]:
        """모든 플러그인 상태 조회"""
        return {
            'plugins': {
                name: self.get_plugin_status(name)
                for name in self.plugin_states.keys()
            },
            'update_queue': self.update_queue,
            'update_running': self.update_running
        }

# 전역 인스턴스
plugin_lifecycle_manager = PluginLifecycleManager() 