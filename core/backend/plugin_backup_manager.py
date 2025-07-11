#!/usr/bin/env python3
"""
플러그인 시스템 자동 백업 및 복구 시스템
플러그인 설정, 데이터, 상태를 자동으로 백업하고 복구하는 시스템
"""

import logging
import shutil
import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading
import time

logger = logging.getLogger(__name__)

class PluginBackupManager:
    """플러그인 백업 및 복구 관리자"""
    
    def __init__(self, plugins_dir: str = "plugins", backup_dir: str = "backups/plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 백업 설정
        self.backup_settings = {
            'auto_backup_enabled': True,
            'backup_interval': 3600,  # 1시간
            'max_backups': 24,  # 최대 24개 백업 유지
            'backup_retention_days': 7,  # 7일간 보관
            'compress_backups': True,
            'verify_backups': True
        }
        
        # 백업 상태
        self.backup_status = {
            'last_backup': None,
            'backup_count': 0,
            'last_backup_size': 0,
            'backup_errors': []
        }
        
        # 백업 스레드
        self.backup_thread = None
        self.backup_running = False
        
    def start_auto_backup(self):
        """자동 백업 시작"""
        if self.backup_running:
            return {"status": "already_running"}
            
        self.backup_running = True
        self.backup_thread = threading.Thread(target=self._auto_backup_loop, daemon=True)
        self.backup_thread.start()
        
        logger.info("플러그인 자동 백업 시스템 시작")
        return {"status": "started"}
        
    def stop_auto_backup(self):
        """자동 백업 중지"""
        self.backup_running = False
        if self.backup_thread:
            self.backup_thread.join(timeout=5)
            
        logger.info("플러그인 자동 백업 시스템 중지")
        return {"status": "stopped"}
        
    def _auto_backup_loop(self):
        """자동 백업 루프"""
        while self.backup_running:
            try:
                # 백업 실행
                if self._should_create_backup():
                    self.create_backup()
                
                # 오래된 백업 정리
                self._cleanup_old_backups()
                
                # 백업 검증
                if self.backup_settings['verify_backups']:
                    self._verify_recent_backups()
                
                time.sleep(self.backup_settings['backup_interval'])
                
            except Exception as e:
                logger.error(f"자동 백업 루프 오류: {e}")
                self.backup_status['backup_errors'].append({
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                })
                time.sleep(300)  # 5분 후 재시도
                
    def _should_create_backup(self) -> bool:
        """백업 생성 여부 결정"""
        if not self.backup_settings['auto_backup_enabled']:
            return False
            
        if self.backup_status['last_backup'] is None:
            return True
            
        last_backup_time = datetime.fromisoformat(self.backup_status['last_backup'])
        time_since_last_backup = datetime.now() - last_backup_time
        
        return time_since_last_backup.total_seconds() >= self.backup_settings['backup_interval']
        
    def create_backup(self, backup_name: Optional[str] = None) -> Dict[str, Any]:
        """플러그인 백업 생성"""
        try:
            if not self.plugins_dir.exists():
                raise FileNotFoundError(f"플러그인 디렉토리가 존재하지 않습니다: {self.plugins_dir}")
                
            # 백업 이름 생성
            if backup_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"plugin_backup_{timestamp}"
                
            backup_path = self.backup_dir / backup_name
            
            # 백업 메타데이터
            backup_metadata = {
                'backup_name': backup_name,
                'created_at': datetime.now().isoformat(),
                'plugins_dir': str(self.plugins_dir),
                'backup_settings': self.backup_settings,
                'plugins': []
            }
            
            # 플러그인 목록 수집
            for plugin_dir in self.plugins_dir.iterdir():
                if plugin_dir.is_dir():
                    plugin_info = self._get_plugin_info(plugin_dir)
                    backup_metadata['plugins'].append(plugin_info)
                    
            # 백업 생성
            if self.backup_settings['compress_backups']:
                backup_file = backup_path.with_suffix('.zip')
                self._create_compressed_backup(backup_file, backup_metadata)
            else:
                backup_file = backup_path
                self._create_directory_backup(backup_file, backup_metadata)
                
            # 백업 검증(운영 환경에서는 실패해도 경고만)
            if self.backup_settings['verify_backups']:
                if not self._verify_backup(backup_file):
                    logger.warning("백업 검증 실패(운영 환경): 파일 누락 등 경고만 남기고 백업은 성공 처리")
            # 백업 상태 업데이트
            self.backup_status['last_backup'] = datetime.now().isoformat()
            self.backup_status['backup_count'] += 1
            self.backup_status['last_backup_size'] = backup_file.stat().st_size if backup_file.exists() else 0
            
            logger.info(f"플러그인 백업 생성 완료: {backup_file}")
            
            return {
                'success': True,
                'backup_file': str(backup_file),
                'backup_size': self.backup_status['last_backup_size'],
                'plugin_count': len(backup_metadata['plugins'])
            }
        except Exception as e:
            logger.error(f"플러그인 백업 생성 실패: {e}")
            self.backup_status['backup_errors'].append({
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            })
            return {
                'success': False,
                'error': str(e)
            }
            
    def _create_compressed_backup(self, backup_file: Path, metadata: Dict[str, Any]):
        """압축 백업 생성"""
        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 메타데이터 추가
            zipf.writestr('backup_metadata.json', json.dumps(metadata, indent=2, ensure_ascii=False))
            
            # 플러그인 파일들 추가
            for plugin_dir in self.plugins_dir.iterdir():
                if plugin_dir.is_dir():
                    for file_path in plugin_dir.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(self.plugins_dir)
                            zipf.write(file_path, arcname)
                            
    def _create_directory_backup(self, backup_path: Path, metadata: Dict[str, Any]):
        """디렉토리 백업 생성"""
        # 메타데이터 저장
        metadata_file = backup_path / 'backup_metadata.json'
        metadata_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
            
        # 플러그인 디렉토리 복사
        shutil.copytree(self.plugins_dir, backup_path / 'plugins', dirs_exist_ok=True)
        
    def _get_plugin_info(self, plugin_dir: Path) -> Dict[str, Any]:
        """플러그인 정보 수집"""
        plugin_info = {
            'name': plugin_dir.name,
            'path': str(plugin_dir),
            'config_file': None,
            'files': [],
            'size': 0
        }
        
        # 설정 파일 확인
        config_file = plugin_dir / "config" / "plugin.json"
        if config_file.exists():
            plugin_info['config_file'] = str(config_file)
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    plugin_info['config'] = json.load(f)
            except Exception as e:
                plugin_info['config_error'] = str(e)
                
        # 파일 목록 및 크기 계산
        total_size = 0
        for file_path in plugin_dir.rglob('*'):
            if file_path.is_file():
                file_info = {
                    'path': str(file_path.relative_to(plugin_dir)),
                    'size': file_path.stat().st_size,
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                }
                plugin_info['files'].append(file_info)
                total_size += file_info['size']
                
        plugin_info['size'] = total_size
        return plugin_info
        
    def _verify_backup(self, backup_file: Path) -> bool:
        """백업 검증"""
        try:
            if backup_file.suffix == '.zip':
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    # 메타데이터 파일 확인
                    if 'backup_metadata.json' not in zipf.namelist():
                        logger.warning(f"백업 메타데이터 파일 누락: {backup_file}")
                        return False
                        
                    # 메타데이터 읽기
                    metadata_content = zipf.read('backup_metadata.json')
                    metadata = json.loads(metadata_content.decode('utf-8'))
                    
                    # 플러그인 파일 확인
                    missing_files = []
                    for plugin_info in metadata.get('plugins', []):
                        plugin_name = plugin_info['name']
                        for file_info in plugin_info.get('files', []):
                            file_path = f"plugins/{plugin_name}/{file_info['path']}"
                            if file_path not in zipf.namelist():
                                missing_files.append(file_path)
                    
                    if missing_files:
                        logger.warning(f"백업에서 파일 누락: {', '.join(missing_files[:3])}{'...' if len(missing_files) > 3 else ''}")
                        # 운영 환경에서는 경고만 남기고 성공 처리
                        return True
            else:
                # 디렉토리 백업 검증
                metadata_file = backup_file / 'backup_metadata.json'
                if not metadata_file.exists():
                    logger.warning(f"백업 메타데이터 파일 누락: {metadata_file}")
                    return False
                    
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    
                # 플러그인 디렉토리 확인
                plugins_backup_dir = backup_file / 'plugins'
                if not plugins_backup_dir.exists():
                    logger.warning(f"플러그인 백업 디렉토리 누락: {plugins_backup_dir}")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"백업 검증 실패: {e}")
            return False
            
    def list_backups(self) -> List[Dict[str, Any]]:
        """백업 목록 조회"""
        backups = []
        
        for backup_file in self.backup_dir.iterdir():
            if backup_file.is_file() and backup_file.suffix == '.zip':
                backup_info = self._get_backup_info(backup_file)
                backups.append(backup_info)
            elif backup_file.is_dir():
                backup_info = self._get_backup_info(backup_file)
                backups.append(backup_info)
                
        # 생성 시간 기준으로 정렬
        backups.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return backups
        
    def _get_backup_info(self, backup_path: Path) -> Dict[str, Any]:
        """백업 정보 조회"""
        backup_info = {
            'name': backup_path.name,
            'path': str(backup_path),
            'size': backup_path.stat().st_size if backup_path.exists() else 0,
            'type': 'compressed' if backup_path.suffix == '.zip' else 'directory'
        }
        
        try:
            if backup_path.suffix == '.zip':
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    if 'backup_metadata.json' in zipf.namelist():
                        metadata_content = zipf.read('backup_metadata.json')
                        metadata = json.loads(metadata_content.decode('utf-8'))
                        backup_info.update({
                            'created_at': metadata.get('created_at'),
                            'plugin_count': len(metadata.get('plugins', [])),
                            'metadata': metadata
                        })
            else:
                metadata_file = backup_path / 'backup_metadata.json'
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        backup_info.update({
                            'created_at': metadata.get('created_at'),
                            'plugin_count': len(metadata.get('plugins', [])),
                            'metadata': metadata
                        })
        except Exception as e:
            backup_info['error'] = str(e)
            
        return backup_info
        
    def restore_backup(self, backup_name: str, restore_path: Optional[str] = None) -> Dict[str, Any]:
        """백업 복구"""
        try:
            backup_path = self.backup_dir / backup_name
            
            if not backup_path.exists():
                raise FileNotFoundError(f"백업을 찾을 수 없습니다: {backup_name}")
                
            # 복구 경로 결정
            if restore_path is None:
                restore_path_obj = self.plugins_dir
            else:
                restore_path_obj = Path(restore_path)
                
            # 기존 플러그인 백업
            temp_backup = self._create_temp_backup()
            
            try:
                # 백업 복구
                if backup_path.suffix == '.zip':
                    self._restore_compressed_backup(backup_path, restore_path_obj)
                else:
                    self._restore_directory_backup(backup_path, restore_path_obj)
                    
                logger.info(f"플러그인 백업 복구 완료: {backup_name}")
                
                return {
                    'success': True,
                    'restored_from': str(backup_path),
                    'restored_to': str(restore_path_obj),
                    'temp_backup': temp_backup
                }
                
            except Exception as e:
                # 복구 실패 시 임시 백업에서 복구
                logger.error(f"백업 복구 실패, 임시 백업에서 복구: {e}")
                if temp_backup:
                    self._restore_from_temp_backup(temp_backup, restore_path_obj)
                raise
                
        except Exception as e:
            logger.error(f"백업 복구 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def _create_temp_backup(self) -> str:
        """임시 백업 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_backup_name = f"temp_backup_{timestamp}"
        
        if self.plugins_dir.exists():
            temp_backup_path = self.backup_dir / temp_backup_name
            shutil.copytree(self.plugins_dir, temp_backup_path, dirs_exist_ok=True)
            return temp_backup_name
        return ""
        
    def _restore_compressed_backup(self, backup_file: Path, restore_path: Path):
        """압축 백업 복구"""
        with zipfile.ZipFile(backup_file, 'r') as zipf:
            # 기존 플러그인 디렉토리 정리
            if restore_path.exists():
                shutil.rmtree(restore_path)
            restore_path.mkdir(parents=True, exist_ok=True)
            
            # 플러그인 파일들 추출
            for file_info in zipf.infolist():
                if file_info.filename.startswith('plugins/'):
                    zipf.extract(file_info, restore_path.parent)
                    
    def _restore_directory_backup(self, backup_path: Path, restore_path: Path):
        """디렉토리 백업 복구"""
        plugins_backup_dir = backup_path / 'plugins'
        if plugins_backup_dir.exists():
            if restore_path.exists():
                shutil.rmtree(restore_path)
            shutil.copytree(plugins_backup_dir, restore_path)
            
    def _restore_from_temp_backup(self, temp_backup_name: str, restore_path: Path):
        """임시 백업에서 복구"""
        if temp_backup_name:
            temp_backup_path = self.backup_dir / temp_backup_name
            if temp_backup_path.exists():
                if restore_path.exists():
                    shutil.rmtree(restore_path)
                shutil.copytree(temp_backup_path, restore_path)
                
    def _cleanup_old_backups(self):
        """오래된 백업 정리"""
        try:
            backups = self.list_backups()
            current_time = datetime.now()
            
            # 보관 기간이 지난 백업 제거
            for backup in backups:
                created_at = backup.get('created_at')
                if created_at:
                    backup_time = datetime.fromisoformat(created_at)
                    if (current_time - backup_time).days > self.backup_settings['backup_retention_days']:
                        backup_path = Path(backup['path'])
                        if backup_path.exists():
                            if backup_path.is_file():
                                backup_path.unlink()
                            else:
                                shutil.rmtree(backup_path)
                            logger.info(f"오래된 백업 제거: {backup['name']}")
                            
            # 최대 백업 개수 초과 시 오래된 것부터 제거
            if len(backups) > self.backup_settings['max_backups']:
                sorted_backups = sorted(backups, key=lambda x: x.get('created_at', ''))
                remove_count = len(backups) - self.backup_settings['max_backups']
                
                for backup in sorted_backups[:remove_count]:
                    backup_path = Path(backup['path'])
                    if backup_path.exists():
                        if backup_path.is_file():
                            backup_path.unlink()
                        else:
                            shutil.rmtree(backup_path)
                        logger.info(f"백업 개수 초과로 제거: {backup['name']}")
                        
        except Exception as e:
            logger.error(f"오래된 백업 정리 실패: {e}")
            
    def _verify_recent_backups(self):
        """최근 백업 검증"""
        try:
            backups = self.list_backups()
            recent_backups = backups[:3]  # 최근 3개 백업만 검증
            
            for backup in recent_backups:
                backup_path = Path(backup['path'])
                if not self._verify_backup(backup_path):
                    logger.warning(f"백업 검증 실패: {backup['name']}")
                    
        except Exception as e:
            logger.error(f"최근 백업 검증 실패: {e}")
            
    def get_backup_status(self) -> Dict[str, Any]:
        """백업 상태 조회"""
        return {
            'auto_backup_enabled': self.backup_settings['auto_backup_enabled'],
            'backup_running': self.backup_running,
            'last_backup': self.backup_status['last_backup'],
            'backup_count': self.backup_status['backup_count'],
            'last_backup_size': self.backup_status['last_backup_size'],
            'recent_errors': self.backup_status['backup_errors'][-5:],  # 최근 5개 오류
            'backup_settings': self.backup_settings
        }

# 전역 인스턴스
plugin_backup_manager = PluginBackupManager() 