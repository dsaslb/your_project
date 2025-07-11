#!/usr/bin/env python3
"""
플러그인 마켓플레이스 시스템
플러그인 등록, 검색, 다운로드, 배포 관리 기능 제공
"""

import os
import json
import shutil
import zipfile
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PluginMarketplace:
    """플러그인 마켓플레이스 관리 클래스"""
    
    def __init__(self, marketplace_dir: str = "plugins/marketplace"):
        self.marketplace_dir = Path(marketplace_dir)
        self.marketplace_dir.mkdir(parents=True, exist_ok=True)
        
        # 하위 디렉토리 생성
        (self.marketplace_dir / "published").mkdir(exist_ok=True)
        (self.marketplace_dir / "pending").mkdir(exist_ok=True)
        (self.marketplace_dir / "rejected").mkdir(exist_ok=True)
        (self.marketplace_dir / "downloads").mkdir(exist_ok=True)
        (self.marketplace_dir / "metadata").mkdir(exist_ok=True)
        
        # 메타데이터 파일 경로
        self.metadata_file = self.marketplace_dir / "metadata" / "marketplace.json"
        self.load_marketplace_data()
    
    def load_marketplace_data(self):
        """마켓플레이스 데이터 로드"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.marketplace_data = json.load(f)
            except Exception as e:
                logger.error(f"마켓플레이스 데이터 로드 실패: {e}")
                self.marketplace_data = {
                    'plugins': {},
                    'categories': [],
                    'statistics': {
                        'total_plugins': 0,
                        'total_downloads': 0,
                        'total_ratings': 0
                    }
                }
        else:
            self.marketplace_data = {
                'plugins': {},
                'categories': [],
                'statistics': {
                    'total_plugins': 0,
                    'total_downloads': 0,
                    'total_ratings': 0
                }
            }
            self.save_marketplace_data()
    
    def save_marketplace_data(self):
        """마켓플레이스 데이터 저장"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.marketplace_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"마켓플레이스 데이터 저장 실패: {e}")
    
    def register_plugin(self, plugin_path: str, metadata: Dict[str, Any]) -> bool:
        """플러그인 등록"""
        try:
            plugin_id = metadata.get('plugin_id')
            if not plugin_id:
                logger.error("plugin_id가 필요합니다")
                return False
            
            # 플러그인 파일 검증
            if not self.validate_plugin(plugin_path, metadata):
                return False
            
            # 플러그인 패키징
            package_path = self.package_plugin(plugin_path, metadata)
            if not package_path:
                return False
            
            # 메타데이터 업데이트
            metadata.update({
                'registered_at': datetime.now().isoformat(),
                'status': 'pending',
                'downloads': 0,
                'rating': 0.0,
                'rating_count': 0,
                'package_path': str(package_path),
                'file_size': os.path.getsize(package_path),
                'checksum': self.calculate_checksum(package_path)
            })
            
            # 대기 중인 플러그인으로 이동
            pending_path = self.marketplace_dir / "pending" / f"{plugin_id}.zip"
            shutil.move(package_path, pending_path)
            metadata['package_path'] = str(pending_path)
            
            # 마켓플레이스 데이터에 추가
            self.marketplace_data['plugins'][plugin_id] = metadata
            self.save_marketplace_data()
            
            logger.info(f"플러그인 {plugin_id} 등록 완료")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 등록 실패: {e}")
            return False
    
    def validate_plugin(self, plugin_path: str, metadata: Dict[str, Any]) -> bool:
        """플러그인 유효성 검증"""
        try:
            plugin_dir = Path(plugin_path)
            
            # 필수 파일 확인
            required_files = ['plugin.json', 'README.md']
            for file_name in required_files:
                if not (plugin_dir / file_name).exists():
                    logger.error(f"필수 파일 누락: {file_name}")
                    return False
            
            # plugin.json 파싱 확인
            plugin_config = plugin_dir / "plugin.json"
            try:
                with open(plugin_config, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 필수 필드 확인
                required_fields = ['name', 'version', 'description', 'author']
                for field in required_fields:
                    if field not in config_data:
                        logger.error(f"필수 필드 누락: {field}")
                        return False
                
            except Exception as e:
                logger.error(f"plugin.json 파싱 실패: {e}")
                return False
            
            # 메타데이터와 config_data 일치 확인
            if metadata.get('plugin_id') != config_data.get('plugin_id'):
                logger.error("메타데이터와 plugin.json의 plugin_id가 일치하지 않습니다")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"플러그인 검증 실패: {e}")
            return False
    
    def package_plugin(self, plugin_path: str, metadata: Dict[str, Any]) -> Optional[Path]:
        """플러그인 패키징"""
        try:
            plugin_id = metadata.get('plugin_id')
            version = metadata.get('version', '1.0.0')
            
            # 임시 패키지 파일 경로
            temp_package = self.marketplace_dir / f"{plugin_id}_{version}.zip"
            
            # ZIP 파일 생성
            with zipfile.ZipFile(temp_package, 'w', zipfile.ZIP_DEFLATED) as zipf:
                plugin_dir = Path(plugin_path)
                
                # 플러그인 파일들을 ZIP에 추가
                for file_path in plugin_dir.rglob('*'):
                    if file_path.is_file():
                        # .git, __pycache__ 등 제외
                        if any(part.startswith('.') or part == '__pycache__' for part in file_path.parts):
                            continue
                        
                        arcname = file_path.relative_to(plugin_dir)
                        zipf.write(file_path, arcname)
            
            return temp_package
            
        except Exception as e:
            logger.error(f"플러그인 패키징 실패: {e}")
            return None
    
    def calculate_checksum(self, file_path: Path) -> str:
        """파일 체크섬 계산"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"체크섬 계산 실패: {e}")
            return ""
    
    def approve_plugin(self, plugin_id: str) -> bool:
        """플러그인 승인"""
        try:
            if plugin_id not in self.marketplace_data['plugins']:
                logger.error(f"플러그인을 찾을 수 없습니다: {plugin_id}")
                return False
            
            plugin_data = self.marketplace_data['plugins'][plugin_id]
            
            # 대기 중인 플러그인을 게시된 플러그인으로 이동
            pending_path = Path(plugin_data['package_path'])
            if pending_path.exists():
                published_path = self.marketplace_dir / "published" / f"{plugin_id}.zip"
                shutil.move(pending_path, published_path)
                plugin_data['package_path'] = str(published_path)
            
            # 상태 업데이트
            plugin_data['status'] = 'published'
            plugin_data['approved_at'] = datetime.now().isoformat()
            
            # 통계 업데이트
            self.marketplace_data['statistics']['total_plugins'] += 1
            
            self.save_marketplace_data()
            logger.info(f"플러그인 {plugin_id} 승인 완료")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 승인 실패: {e}")
            return False
    
    def reject_plugin(self, plugin_id: str, reason: str) -> bool:
        """플러그인 거부"""
        try:
            if plugin_id not in self.marketplace_data['plugins']:
                logger.error(f"플러그인을 찾을 수 없습니다: {plugin_id}")
                return False
            
            plugin_data = self.marketplace_data['plugins'][plugin_id]
            
            # 대기 중인 플러그인을 거부된 플러그인으로 이동
            pending_path = Path(plugin_data['package_path'])
            if pending_path.exists():
                rejected_path = self.marketplace_dir / "rejected" / f"{plugin_id}.zip"
                shutil.move(pending_path, rejected_path)
                plugin_data['package_path'] = str(rejected_path)
            
            # 상태 업데이트
            plugin_data['status'] = 'rejected'
            plugin_data['rejected_at'] = datetime.now().isoformat()
            plugin_data['rejection_reason'] = reason
            
            self.save_marketplace_data()
            logger.info(f"플러그인 {plugin_id} 거부 완료")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 거부 실패: {e}")
            return False
    
    def search_plugins(self, query: str = "", category: str = "", status: str = "published") -> List[Dict[str, Any]]:
        """플러그인 검색"""
        try:
            results = []
            
            for _, plugin_data in self.marketplace_data['plugins'].items():
                # 상태 필터
                if status and plugin_data.get('status') != status:
                    continue
                
                # 카테고리 필터
                if category and plugin_data.get('category') != category:
                    continue
                
                # 검색어 필터
                if query:
                    searchable_text = f"{plugin_data.get('name', '')} {plugin_data.get('description', '')} {plugin_data.get('author', '')}"
                    if query.lower() not in searchable_text.lower():
                        continue
                
                results.append(plugin_data)
            
            # 다운로드 수로 정렬
            results.sort(key=lambda x: x.get('downloads', 0), reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"플러그인 검색 실패: {e}")
            return []
    
    def download_plugin(self, plugin_id: str, target_dir: str) -> bool:
        """플러그인 다운로드"""
        try:
            if plugin_id not in self.marketplace_data['plugins']:
                logger.error(f"플러그인을 찾을 수 없습니다: {plugin_id}")
                return False
            
            plugin_data = self.marketplace_data['plugins'][plugin_id]
            
            if plugin_data.get('status') != 'published':
                logger.error(f"플러그인이 게시되지 않았습니다: {plugin_id}")
                return False
            
            package_path = Path(plugin_data['package_path'])
            if not package_path.exists():
                logger.error(f"플러그인 패키지를 찾을 수 없습니다: {package_path}")
                return False
            
            # 다운로드 디렉토리 생성
            target_path = Path(target_dir)
            target_path.mkdir(parents=True, exist_ok=True)
            
            # 플러그인 압축 해제
            with zipfile.ZipFile(package_path, 'r') as zipf:
                zipf.extractall(target_path)
            
            # 다운로드 수 증가
            plugin_data['downloads'] = plugin_data.get('downloads', 0) + 1
            self.marketplace_data['statistics']['total_downloads'] += 1
            self.save_marketplace_data()
            
            logger.info(f"플러그인 {plugin_id} 다운로드 완료")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 다운로드 실패: {e}")
            return False
    
    def rate_plugin(self, plugin_id: str, rating: float, user_id: str) -> bool:
        """플러그인 평점"""
        try:
            if plugin_id not in self.marketplace_data['plugins']:
                logger.error(f"플러그인을 찾을 수 없습니다: {plugin_id}")
                return False
            
            if not 1.0 <= rating <= 5.0:
                logger.error("평점은 1.0에서 5.0 사이여야 합니다")
                return False
            
            plugin_data = self.marketplace_data['plugins'][plugin_id]
            
            # 기존 평점 정보
            current_rating = plugin_data.get('rating', 0.0)
            current_count = plugin_data.get('rating_count', 0)
            
            # 새 평점 계산
            new_count = current_count + 1
            new_rating = ((current_rating * current_count) + rating) / new_count
            
            plugin_data['rating'] = round(new_rating, 2)
            plugin_data['rating_count'] = new_count
            
            # 통계 업데이트
            self.marketplace_data['statistics']['total_ratings'] += 1
            
            self.save_marketplace_data()
            logger.info(f"플러그인 {plugin_id} 평점 업데이트: {rating}")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 평점 실패: {e}")
            return False
    
    def get_plugin_statistics(self) -> Dict[str, Any]:
        """플러그인 통계 조회"""
        try:
            stats = self.marketplace_data['statistics'].copy()
            
            # 카테고리별 통계
            category_stats = {}
            for plugin_data in self.marketplace_data['plugins'].values():
                category = plugin_data.get('category', '기타')
                if category not in category_stats:
                    category_stats[category] = {
                        'count': 0,
                        'downloads': 0,
                        'avg_rating': 0.0
                    }
                
                category_stats[category]['count'] += 1
                category_stats[category]['downloads'] += plugin_data.get('downloads', 0)
                
                # 평균 평점 계산
                ratings = []
                for p in self.marketplace_data['plugins'].values():
                    if p.get('category') == category and p.get('rating', 0) > 0:
                        ratings.append(p.get('rating', 0))
                
                if ratings:
                    category_stats[category]['avg_rating'] = round(sum(ratings) / len(ratings), 2)
            
            stats['category_statistics'] = category_stats
            
            # 최근 등록된 플러그인
            recent_plugins = []
            for plugin_data in self.marketplace_data['plugins'].values():
                if plugin_data.get('status') == 'published':
                    recent_plugins.append({
                        'plugin_id': plugin_data.get('plugin_id'),
                        'name': plugin_data.get('name'),
                        'registered_at': plugin_data.get('registered_at'),
                        'downloads': plugin_data.get('downloads', 0)
                    })
            
            recent_plugins.sort(key=lambda x: x.get('registered_at', ''), reverse=True)
            stats['recent_plugins'] = recent_plugins[:10]
            
            return stats
            
        except Exception as e:
            logger.error(f"통계 조회 실패: {e}")
            return {}

class PluginDeploymentSystem:
    """플러그인 배포 관리 시스템"""
    
    def __init__(self, deployment_dir: str = "plugins/deployed"):
        self.deployment_dir = Path(deployment_dir)
        self.deployment_dir.mkdir(parents=True, exist_ok=True)
        
        # 배포 로그 파일
        self.deployment_log = self.deployment_dir / "deployment_log.json"
        self.load_deployment_log()
    
    def load_deployment_log(self):
        """배포 로그 로드"""
        if self.deployment_log.exists():
            try:
                with open(self.deployment_log, 'r', encoding='utf-8') as f:
                    self.deployment_data = json.load(f)
            except Exception as e:
                logger.error(f"배포 로그 로드 실패: {e}")
                self.deployment_data = {'deployments': {}, 'history': []}
        else:
            self.deployment_data = {'deployments': {}, 'history': []}
            self.save_deployment_log()
    
    def save_deployment_log(self):
        """배포 로그 저장"""
        try:
            with open(self.deployment_log, 'w', encoding='utf-8') as f:
                json.dump(self.deployment_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"배포 로그 저장 실패: {e}")
    
    def deploy_plugin(self, plugin_id: str, plugin_path: str, environment: str = "production") -> bool:
        """플러그인 배포"""
        try:
            # 배포 디렉토리 생성
            env_dir = self.deployment_dir / environment
            env_dir.mkdir(exist_ok=True)
            
            plugin_dir = env_dir / plugin_id
            if plugin_dir.exists():
                # 기존 플러그인 백업
                backup_dir = plugin_dir.parent / f"{plugin_id}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.move(plugin_dir, backup_dir)
            
            # 새 플러그인 복사
            shutil.copytree(plugin_path, plugin_dir)
            
            # 배포 정보 기록
            deployment_info = {
                'plugin_id': plugin_id,
                'environment': environment,
                'deployed_at': datetime.now().isoformat(),
                'version': self.get_plugin_version(plugin_path),
                'status': 'deployed'
            }
            
            self.deployment_data['deployments'][plugin_id] = deployment_info
            
            # 배포 히스토리에 추가
            self.deployment_data['history'].append({
                **deployment_info,
                'action': 'deploy'
            })
            
            self.save_deployment_log()
            logger.info(f"플러그인 {plugin_id} 배포 완료 ({environment})")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 배포 실패: {e}")
            return False
    
    def undeploy_plugin(self, plugin_id: str, environment: str = "production") -> bool:
        """플러그인 배포 해제"""
        try:
            env_dir = self.deployment_dir / environment
            plugin_dir = env_dir / plugin_id
            
            if not plugin_dir.exists():
                logger.error(f"배포된 플러그인을 찾을 수 없습니다: {plugin_id}")
                return False
            
            # 플러그인 제거
            shutil.rmtree(plugin_dir)
            
            # 배포 정보 업데이트
            if plugin_id in self.deployment_data['deployments']:
                self.deployment_data['deployments'][plugin_id]['status'] = 'undeployed'
                self.deployment_data['deployments'][plugin_id]['undeployed_at'] = datetime.now().isoformat()
            
            # 배포 히스토리에 추가
            self.deployment_data['history'].append({
                'plugin_id': plugin_id,
                'environment': environment,
                'action': 'undeploy',
                'timestamp': datetime.now().isoformat()
            })
            
            self.save_deployment_log()
            logger.info(f"플러그인 {plugin_id} 배포 해제 완료 ({environment})")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 배포 해제 실패: {e}")
            return False
    
    def get_plugin_version(self, plugin_path: str) -> str:
        """플러그인 버전 조회"""
        try:
            plugin_config = Path(plugin_path) / "plugin.json"
            if plugin_config.exists():
                with open(plugin_config, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    return config_data.get('version', 'unknown')
        except Exception as e:
            logger.error(f"플러그인 버전 조회 실패: {e}")
        
        return 'unknown'
    
    def get_deployment_status(self, plugin_id: Optional[str] = None) -> Dict[str, Any]:
        """배포 상태 조회"""
        try:
            if plugin_id:
                return self.deployment_data['deployments'].get(plugin_id, {})
            else:
                return self.deployment_data['deployments']
        except Exception as e:
            logger.error(f"배포 상태 조회 실패: {e}")
            return {}
    
    def get_deployment_history(self, plugin_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """배포 히스토리 조회"""
        try:
            history = self.deployment_data['history']
            
            if plugin_id:
                history = [h for h in history if h.get('plugin_id') == plugin_id]
            
            # 최신 순으로 정렬하고 제한
            history.sort(key=lambda x: x.get('deployed_at', x.get('timestamp', '')), reverse=True)
            return history[:limit]
            
        except Exception as e:
            logger.error(f"배포 히스토리 조회 실패: {e}")
            return []

# 전역 인스턴스
marketplace = PluginMarketplace()
deployment_system = PluginDeploymentSystem() 