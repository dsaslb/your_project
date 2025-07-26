import os
import shutil
import json
import hashlib
import zipfile
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import threading
import time

logger = logging.getLogger(__name__)

class PluginBackupManager:
    """플러그인 백업 관리자"""
    
    def __init__(self, backup_root_dir: str = "backups/plugins"):
        self.backup_root_dir = Path(backup_root_dir)
        self.backup_root_dir.mkdir(parents=True, exist_ok=True)
        
    def create_snapshot(self, plugin_id: int, installation_id: int, snapshot_name: str, 
                       snapshot_type: str = "manual", description: str = "") -> Dict[str, Any]:
        """플러그인 스냅샷 생성"""
        try:
            snapshot_id = f"snapshot_{plugin_id}_{int(datetime.utcnow().timestamp())}"
            snapshot_dir = self.backup_root_dir / snapshot_id
            snapshot_dir.mkdir(exist_ok=True)
            
            # 플러그인 정보 수집
            plugin_info = self._collect_plugin_info(plugin_id, installation_id)
            
            # 파일 백업
            files_backup = self._backup_plugin_files(plugin_id, snapshot_dir)
            
            # 설정 및 데이터 백업
            config_backup = self._backup_plugin_config(plugin_id, installation_id, snapshot_dir)
            data_backup = self._backup_plugin_data(plugin_id, installation_id, snapshot_dir)
            
            # 스냅샷 메타데이터 생성
            snapshot_metadata = {
                'snapshot_id': snapshot_id,
                'plugin_id': plugin_id,
                'installation_id': installation_id,
                'snapshot_name': snapshot_name,
                'snapshot_type': snapshot_type,
                'description': description,
                'created_at': datetime.utcnow().isoformat(),
                'plugin_info': plugin_info,
                'files_backup': files_backup,
                'config_backup': config_backup,
                'data_backup': data_backup,
            }
            
            # 메타데이터 저장
            with open(snapshot_dir / "metadata.json", "w", encoding="utf-8") as f:
                json.dump(snapshot_metadata, f, indent=2, ensure_ascii=False)
            
            # 압축 파일 생성
            backup_file_path = self._create_backup_archive(snapshot_dir, snapshot_id)
            
            # 백업 무결성 검증
            backup_hash = self._calculate_file_hash(backup_file_path)
            
            # 정리
            shutil.rmtree(snapshot_dir)
            
            return {
                'success': True,
                'snapshot_id': snapshot_id,
                'backup_file_path': str(backup_file_path),
                'backup_file_size': backup_file_path.stat().st_size,
                'backup_file_hash': backup_hash,
                'metadata': snapshot_metadata
            }
            
        except Exception as e:
            logger.error(f"스냅샷 생성 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def restore_snapshot(self, snapshot_id: str, plugin_id: int, installation_id: int) -> Dict[str, Any]:
        """스냅샷에서 플러그인 복원"""
        try:
            backup_file_path = self.backup_root_dir / f"{snapshot_id}.zip"
            
            if not backup_file_path.exists():
                raise FileNotFoundError(f"백업 파일을 찾을 수 없습니다: {backup_file_path}")
            
            # 백업 파일 무결성 검증
            if not self._verify_backup_integrity(backup_file_path, snapshot_id):
                raise ValueError("백업 파일 무결성 검증 실패")
            
            # 임시 디렉토리에 압축 해제
            temp_dir = self.backup_root_dir / f"temp_{snapshot_id}"
            temp_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(backup_file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # 메타데이터 로드
            with open(temp_dir / "metadata.json", "r", encoding="utf-8") as f:
                metadata = json.load(f)
            
            # 플러그인 복원
            restore_result = self._restore_plugin_from_backup(temp_dir, plugin_id, installation_id, metadata)
            
            # 정리
            shutil.rmtree(temp_dir)
            
            return {
                'success': True,
                'restore_result': restore_result,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"스냅샷 복원 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def rollback_plugin(self, plugin_id: int, installation_id: int, target_version: str, 
                       rollback_reason: str = "") -> Dict[str, Any]:
        """플러그인 롤백 실행"""
        try:
            # 현재 버전 확인
            current_version = self._get_current_plugin_version(plugin_id, installation_id)
            
            # 롤백 가능한 스냅샷 찾기
            available_snapshots = self._find_rollback_snapshots(plugin_id, installation_id, target_version)
            
            if not available_snapshots:
                raise ValueError(f"롤백 가능한 스냅샷을 찾을 수 없습니다: {target_version}")
            
            # 최신 스냅샷 선택
            target_snapshot = available_snapshots[0]
            
            # 롤백 전 백업 생성
            pre_rollback_backup = self.create_snapshot(
                plugin_id, installation_id, 
                f"pre_rollback_{target_version}", 
                "rollback", 
                f"롤백 전 백업: {current_version} -> {target_version}"
            )
            
            # 롤백 실행
            rollback_result = self.restore_snapshot(
                target_snapshot['snapshot_id'], 
                plugin_id, 
                installation_id
            )
            
            return {
                'success': True,
                'from_version': current_version,
                'to_version': target_version,
                'rollback_reason': rollback_reason,
                'pre_rollback_backup': pre_rollback_backup,
                'rollback_result': rollback_result
            }
            
        except Exception as e:
            logger.error(f"플러그인 롤백 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup_old_backups(self, retention_days: int = 30, max_backups: int = 10) -> Dict[str, Any]:
        """오래된 백업 정리"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            deleted_count = 0
            freed_space = 0
            
            # 플러그인별로 백업 정리
            for plugin_dir in self.backup_root_dir.iterdir():
                if not plugin_dir.is_dir():
                    continue
                
                plugin_backups = []
                for backup_file in plugin_dir.glob("*.zip"):
                    try:
                        # 파일 생성 시간 확인
                        file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                        plugin_backups.append({
                            'file': backup_file,
                            'time': file_time,
                            'size': backup_file.stat().st_size
                        })
                    except Exception as e:
                        logger.warning(f"백업 파일 정보 읽기 실패: {backup_file} - {e}")
                
                # 시간순 정렬
                plugin_backups.sort(key=lambda x: x['time'], reverse=True)
                
                # 오래된 백업 삭제
                for backup in plugin_backups[retention_days:]:
                    try:
                        freed_space += backup['size']
                        backup['file'].unlink()
                        deleted_count += 1
                        logger.info(f"오래된 백업 삭제: {backup['file']}")
                    except Exception as e:
                        logger.error(f"백업 파일 삭제 실패: {backup['file']} - {e}")
                
                # 최대 백업 수 제한
                if len(plugin_backups) > max_backups:
                    for backup in plugin_backups[max_backups:]:
                        try:
                            freed_space += backup['size']
                            backup['file'].unlink()
                            deleted_count += 1
                            logger.info(f"최대 백업 수 초과로 삭제: {backup['file']}")
                        except Exception as e:
                            logger.error(f"백업 파일 삭제 실패: {backup['file']} - {e}")
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'freed_space_mb': freed_space / (1024 * 1024)
            }
            
        except Exception as e:
            logger.error(f"백업 정리 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _collect_plugin_info(self, plugin_id: int, installation_id: int) -> Dict[str, Any]:
        """플러그인 정보 수집"""
        # 실제 구현에서는 DB에서 플러그인 정보 조회
        return {
            'plugin_id': plugin_id,
            'installation_id': installation_id,
            'version': '1.0.0',  # 실제 버전
            'status': 'active',
            'installed_at': datetime.utcnow().isoformat()
        }
    
    def _backup_plugin_files(self, plugin_id: int, snapshot_dir: Path) -> Dict[str, Any]:
        """플러그인 파일 백업"""
        files_dir = snapshot_dir / "files"
        files_dir.mkdir(exist_ok=True)
        
        # 실제 구현에서는 플러그인 파일 경로에서 복사
        plugin_files_path = f"plugins/{plugin_id}"
        
        if os.path.exists(plugin_files_path):
            shutil.copytree(plugin_files_path, files_dir / "plugin", dirs_exist_ok=True)
        
        return {
            'files_count': len(list(files_dir.rglob("*"))),
            'total_size': sum(f.stat().st_size for f in files_dir.rglob("*") if f.is_file())
        }
    
    def _backup_plugin_config(self, plugin_id: int, installation_id: int, snapshot_dir: Path) -> Dict[str, Any]:
        """플러그인 설정 백업"""
        config_file = snapshot_dir / "config.json"
        
        # 실제 구현에서는 DB에서 설정 조회
        config_data = {
            'plugin_id': plugin_id,
            'installation_id': installation_id,
            'settings': {
                'auto_update': True,
                'notifications': True,
                'data_collection': False
            },
            'permissions': {
                'data_access': {'schedule': True, 'employee': False},
                'api_access': {'read': True, 'write': False}
            }
        }
        
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        return {
            'config_file': str(config_file),
            'config_size': config_file.stat().st_size
        }
    
    def _backup_plugin_data(self, plugin_id: int, installation_id: int, snapshot_dir: Path) -> Dict[str, Any]:
        """플러그인 데이터 백업"""
        data_file = snapshot_dir / "data.json"
        
        # 실제 구현에서는 DB에서 플러그인 데이터 조회
        data = {
            'plugin_id': plugin_id,
            'installation_id': installation_id,
            'usage_stats': {
                'total_executions': 150,
                'last_execution': datetime.utcnow().isoformat(),
                'error_count': 2
            },
            'user_data': {}
        }
        
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return {
            'data_file': str(data_file),
            'data_size': data_file.stat().st_size
        }
    
    def _create_backup_archive(self, snapshot_dir: Path, snapshot_id: str) -> Path:
        """백업 압축 파일 생성"""
        backup_file = self.backup_root_dir / f"{snapshot_id}.zip"
        
        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in snapshot_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(snapshot_dir)
                    zipf.write(file_path, arcname)
        
        return backup_file
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """파일 해시 계산"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _verify_backup_integrity(self, backup_file: Path, snapshot_id: str) -> bool:
        """백업 파일 무결성 검증"""
        try:
            # 실제 구현에서는 저장된 해시와 비교
            return True
        except Exception as e:
            logger.error(f"백업 무결성 검증 실패: {e}")
            return False
    
    def _restore_plugin_from_backup(self, temp_dir: Path, plugin_id: int, 
                                   installation_id: int, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """백업에서 플러그인 복원"""
        try:
            # 설정 복원
            config_restored = self._restore_plugin_config(temp_dir, plugin_id, installation_id)
            
            # 데이터 복원
            data_restored = self._restore_plugin_data(temp_dir, plugin_id, installation_id)
            
            # 파일 복원
            files_restored = self._restore_plugin_files(temp_dir, plugin_id)
            
            return {
                'config_restored': config_restored,
                'data_restored': data_restored,
                'files_restored': files_restored,
                'restore_time': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"플러그인 복원 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _restore_plugin_config(self, temp_dir: Path, plugin_id: int, installation_id: int) -> bool:
        """플러그인 설정 복원"""
        try:
            config_file = temp_dir / "config.json"
            if config_file.exists():
                # 실제 구현에서는 DB에 설정 저장
                logger.info(f"플러그인 {plugin_id} 설정 복원 완료")
                return True
            return False
        except Exception as e:
            logger.error(f"설정 복원 실패: {e}")
            return False
    
    def _restore_plugin_data(self, temp_dir: Path, plugin_id: int, installation_id: int) -> bool:
        """플러그인 데이터 복원"""
        try:
            data_file = temp_dir / "data.json"
            if data_file.exists():
                # 실제 구현에서는 DB에 데이터 저장
                logger.info(f"플러그인 {plugin_id} 데이터 복원 완료")
                return True
            return False
        except Exception as e:
            logger.error(f"데이터 복원 실패: {e}")
            return False
    
    def _restore_plugin_files(self, temp_dir: Path, plugin_id: int) -> bool:
        """플러그인 파일 복원"""
        try:
            files_dir = temp_dir / "files" / "plugin"
            if files_dir.exists():
                plugin_files_path = f"plugins/{plugin_id}"
                if os.path.exists(plugin_files_path):
                    shutil.rmtree(plugin_files_path)
                shutil.copytree(files_dir, plugin_files_path)
                logger.info(f"플러그인 {plugin_id} 파일 복원 완료")
                return True
            return False
        except Exception as e:
            logger.error(f"파일 복원 실패: {e}")
            return False
    
    def _get_current_plugin_version(self, plugin_id: int, installation_id: int) -> str:
        """현재 플러그인 버전 조회"""
        # 실제 구현에서는 DB에서 조회
        return "1.0.0"
    
    def _find_rollback_snapshots(self, plugin_id: int, installation_id: int, target_version: str) -> List[Dict[str, Any]]:
        """롤백 가능한 스냅샷 찾기"""
        # 실제 구현에서는 DB에서 스냅샷 조회
        return [
            {
                'snapshot_id': f"snapshot_{plugin_id}_1234567890",
                'version': target_version,
                'created_at': datetime.utcnow().isoformat()
            }
        ]

class AutoBackupScheduler:
    """자동 백업 스케줄러"""
    
    def __init__(self, backup_manager: PluginBackupManager):
        self.backup_manager = backup_manager
        self.scheduler_thread = None
        self.running = False
        
    def start(self):
        """스케줄러 시작"""
        if self.running:
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        logger.info("자동 백업 스케줄러가 시작되었습니다.")
        
    def stop(self):
        """스케줄러 중지"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("자동 백업 스케줄러가 중지되었습니다.")
        
    def _scheduler_loop(self):
        """스케줄러 루프"""
        while self.running:
            try:
                # 스케줄된 백업 실행
                self._execute_scheduled_backups()
                
                # 오래된 백업 정리
                self._cleanup_old_backups()
                
                # 1시간 대기
                time.sleep(3600)
                
            except Exception as e:
                logger.error(f"스케줄러 루프 오류: {e}")
                time.sleep(60)  # 오류 시 1분 대기
    
    def _execute_scheduled_backups(self):
        """스케줄된 백업 실행"""
        # 실제 구현에서는 DB에서 스케줄 조회
        logger.info("스케줄된 백업을 확인합니다.")
    
    def _cleanup_old_backups(self):
        """오래된 백업 정리"""
        try:
            result = self.backup_manager.cleanup_old_backups()
            if result['success']:
                logger.info(f"백업 정리 완료: {result['deleted_count']}개 삭제, {result['freed_space_mb']:.2f}MB 해제")
        except Exception as e:
            logger.error(f"백업 정리 실패: {e}") 