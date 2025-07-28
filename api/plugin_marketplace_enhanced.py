# -*- coding: utf-8 -*-
"""
향상된 플러그인 마켓플레이스 API
플러그인 등록/설치/업데이트/비활성/삭제/롤백
설치/사용/충돌/의존성/업데이트/오류 자동 추적
플러그인 상태/통계/배포 현황 모니터링
"""

import logging
import json
import os
import shutil
import zipfile
import tempfile
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import and_, or_, func, desc
import hashlib
import requests
from pathlib import Path

from extensions import db, csrf
from models_main import (
    Module, PluginDeployment, PluginAccessControl,
    PluginVersionHistory, PluginActivation, PluginPermission,
    PluginHierarchy, PluginTestResult, ActionLog, User, Industry, Brand, Branch
)
from models.plugin_models import PluginInstallation as PluginInstall

# 로깅 설정
logger = logging.getLogger(__name__)

# Blueprint 생성
plugin_marketplace_bp = Blueprint('plugin_marketplace_enhanced', __name__)

class PluginManager:
    """플러그인 관리자 클래스"""
    
    def __init__(self):
        self.plugins_dir = Path(current_app.config.get('PLUGINS_DIR', 'plugins'))
        self.marketplace_dir = Path(current_app.config.get('MARKETPLACE_DIR', 'marketplace'))
        self.backup_dir = Path(current_app.config.get('PLUGIN_BACKUP_DIR', 'backups/plugins'))
        
        # 디렉토리 생성
        self.plugins_dir.mkdir(exist_ok=True)
        self.marketplace_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_plugin_manifest(self, manifest_data):
        """플러그인 매니페스트 유효성 검사"""
        required_fields = ['name', 'version', 'description', 'author', 'compatibility']
        
        for field in required_fields:
            if field not in manifest_data:
                return False, f"필수 필드 '{field}'가 누락되었습니다."
        
        # 버전 형식 검사
        if not self._is_valid_version(manifest_data['version']):
            return False, "유효하지 않은 버전 형식입니다."
        
        # 호환성 검사
        if not self._check_compatibility(manifest_data['compatibility']):
            return False, "시스템 호환성 검사에 실패했습니다."
        
        return True, "유효한 매니페스트입니다."
    
    def _is_valid_version(self, version):
        """버전 형식 검사"""
        import re
        pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$'
        return re.match(pattern, version) is not None
    
    def _check_compatibility(self, compatibility):
        """호환성 검사"""
        current_version = current_app.config.get('APP_VERSION', '1.0.0')
        min_version = compatibility.get('min_version', '0.0.0')
        max_version = compatibility.get('max_version', '999.999.999')
        
        return self._compare_versions(min_version, current_version) <= 0 and \
               self._compare_versions(current_version, max_version) <= 0
    
    def _compare_versions(self, v1, v2):
        """버전 비교"""
        from packaging import version
        return version.parse(v1).__cmp__(version.parse(v2))
    
    def install_plugin(self, plugin_file, target_type, target_id, install_options=None):
        """플러그인 설치"""
        try:
            # 임시 디렉토리에 파일 추출
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # ZIP 파일 추출
                with zipfile.ZipFile(plugin_file, 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
                
                # 매니페스트 파일 확인
                manifest_file = temp_path / 'manifest.json'
                if not manifest_file.exists():
                    raise ValueError("매니페스트 파일을 찾을 수 없습니다.")
                
                # 매니페스트 읽기
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    manifest_data = json.load(f)
                
                # 매니페스트 유효성 검사
                is_valid, message = self.validate_plugin_manifest(manifest_data)
                if not is_valid:
                    raise ValueError(f"매니페스트 검증 실패: {message}")
                
                # 플러그인 ID 생성
                plugin_id = f"{manifest_data['name']}-{manifest_data['version']}"
                
                # 기존 설치 확인
                existing_install = PluginInstall.query.filter_by(
                    plugin_id=manifest_data['name'],
                    target_type=target_type,
                    target_id=target_id
                ).first()
                
                if existing_install:
                    # 업데이트 모드
                    return self._update_plugin(existing_install, manifest_data, temp_path, install_options)
                else:
                    # 신규 설치 모드
                    return self._new_install_plugin(manifest_data, temp_path, target_type, target_id, install_options)
        
        except Exception as e:
            logger.error(f"플러그인 설치 실패: {e}")
            raise
    
    def _new_install_plugin(self, manifest_data, temp_path, target_type, target_id, install_options):
        """신규 플러그인 설치"""
        # 플러그인 디렉토리 생성
        plugin_dir = self.plugins_dir / manifest_data['name']
        plugin_dir.mkdir(exist_ok=True)
        
        # 파일 복사
        for item in temp_path.iterdir():
            if item.is_file():
                shutil.copy2(item, plugin_dir / item.name)
            elif item.is_dir():
                shutil.copytree(item, plugin_dir / item.name, dirs_exist_ok=True)
        
        # 데이터베이스에 설치 정보 기록
        plugin_install = PluginInstall(
            plugin_id=manifest_data['name'],
            version=manifest_data['version'],
            target_type=target_type,
            target_id=target_id,
            install_path=str(plugin_dir),
            install_options=install_options or {},
            status='installed',
            installed_by=current_user.id,
            installed_at=datetime.utcnow()
        )
        
        db.session.add(plugin_install)
        
        # 버전 이력 기록
        version_history = PluginVersionHistory(
            plugin_id=manifest_data['name'],
            version=manifest_data['version'],
            changelog=manifest_data.get('changelog', ''),
            release_notes=manifest_data.get('release_notes', ''),
            compatibility=manifest_data.get('compatibility', {}),
            security_notes=manifest_data.get('security_notes', ''),
            is_stable=manifest_data.get('is_stable', True),
            release_date=datetime.utcnow()
        )
        
        db.session.add(version_history)
        
        # 활동 로그 기록
        action_log = ActionLog(
            user_id=current_user.id,
            action='install_plugin',
            message=f'플러그인 설치: {manifest_data["name"]} v{manifest_data["version"]}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        db.session.add(action_log)
        db.session.commit()
        
        logger.info(f"플러그인 설치 완료: {manifest_data['name']} v{manifest_data['version']}")
        
        return {
            'success': True,
            'plugin_id': manifest_data['name'],
            'version': manifest_data['version'],
            'install_path': str(plugin_dir)
        }
    
    def _update_plugin(self, existing_install, manifest_data, temp_path, install_options):
        """플러그인 업데이트"""
        # 백업 생성
        backup_path = self._create_backup(existing_install)
        
        # 기존 파일 삭제
        if os.path.exists(existing_install.install_path):
            shutil.rmtree(existing_install.install_path)
        
        # 새 파일 복사
        plugin_dir = Path(existing_install.install_path)
        plugin_dir.mkdir(exist_ok=True)
        
        for item in temp_path.iterdir():
            if item.is_file():
                shutil.copy2(item, plugin_dir / item.name)
            elif item.is_dir():
                shutil.copytree(item, plugin_dir / item.name, dirs_exist_ok=True)
        
        # 설치 정보 업데이트
        old_version = existing_install.version
        existing_install.version = manifest_data['version']
        existing_install.install_options = install_options or {}
        existing_install.updated_at = datetime.utcnow()
        existing_install.backup_path = str(backup_path)
        
        # 버전 이력 기록
        version_history = PluginVersionHistory(
            plugin_id=manifest_data['name'],
            version=manifest_data['version'],
            changelog=manifest_data.get('changelog', ''),
            release_notes=manifest_data.get('release_notes', ''),
            compatibility=manifest_data.get('compatibility', {}),
            security_notes=manifest_data.get('security_notes', ''),
            is_stable=manifest_data.get('is_stable', True),
            release_date=datetime.utcnow()
        )
        
        db.session.add(version_history)
        
        # 활동 로그 기록
        action_log = ActionLog(
            user_id=current_user.id,
            action='update_plugin',
            message=f'플러그인 업데이트: {manifest_data["name"]} v{old_version} → v{manifest_data["version"]}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        db.session.add(action_log)
        db.session.commit()
        
        logger.info(f"플러그인 업데이트 완료: {manifest_data['name']} v{old_version} → v{manifest_data['version']}")
        
        return {
            'success': True,
            'plugin_id': manifest_data['name'],
            'version': manifest_data['version'],
            'old_version': old_version,
            'backup_path': str(backup_path)
        }
    
    def _create_backup(self, plugin_install):
        """플러그인 백업 생성"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{plugin_install.plugin_id}_v{plugin_install.version}_{timestamp}.zip"
        backup_path = self.backup_dir / backup_name
        
        if os.path.exists(plugin_install.install_path):
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(plugin_install.install_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, plugin_install.install_path)
                        zipf.write(file_path, arcname)
        
        return backup_path
    
    def uninstall_plugin(self, plugin_id, target_type, target_id):
        """플러그인 제거"""
        try:
            plugin_install = PluginInstall.query.filter_by(
                plugin_id=plugin_id,
                target_type=target_type,
                target_id=target_id
            ).first()
            
            if not plugin_install:
                raise ValueError("설치된 플러그인을 찾을 수 없습니다.")
            
            # 백업 생성
            backup_path = self._create_backup(plugin_install)
            
            # 파일 삭제
            if os.path.exists(plugin_install.install_path):
                shutil.rmtree(plugin_install.install_path)
            
            # 데이터베이스에서 제거
            db.session.delete(plugin_install)
            
            # 활동 로그 기록
            action_log = ActionLog(
                user_id=current_user.id,
                action='uninstall_plugin',
                message=f'플러그인 제거: {plugin_id} v{plugin_install.version}',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            db.session.add(action_log)
            db.session.commit()
            
            logger.info(f"플러그인 제거 완료: {plugin_id} v{plugin_install.version}")
            
            return {
                'success': True,
                'backup_path': str(backup_path)
            }
        
        except Exception as e:
            logger.error(f"플러그인 제거 실패: {e}")
            raise
    
    def rollback_plugin(self, plugin_id, target_type, target_id, version):
        """플러그인 롤백"""
        try:
            plugin_install = PluginInstall.query.filter_by(
                plugin_id=plugin_id,
                target_type=target_type,
                target_id=target_id
            ).first()
            
            if not plugin_install:
                raise ValueError("설치된 플러그인을 찾을 수 없습니다.")
            
            # 롤백할 버전의 백업 찾기
            backup_pattern = f"{plugin_id}_v{version}_*.zip"
            backup_files = list(self.backup_dir.glob(backup_pattern))
            
            if not backup_files:
                raise ValueError(f"버전 {version}의 백업을 찾을 수 없습니다.")
            
            # 최신 백업 선택
            backup_file = max(backup_files, key=lambda x: x.stat().st_mtime)
            
            # 현재 버전 백업
            current_backup = self._create_backup(plugin_install)
            
            # 기존 파일 삭제
            if os.path.exists(plugin_install.install_path):
                shutil.rmtree(plugin_install.install_path)
            
            # 백업에서 복원
            plugin_dir = Path(plugin_install.install_path)
            plugin_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(backup_file, 'r') as zip_ref:
                zip_ref.extractall(plugin_dir)
            
            # 설치 정보 업데이트
            old_version = plugin_install.version
            plugin_install.version = version
            plugin_install.updated_at = datetime.utcnow()
            plugin_install.backup_path = str(current_backup)
            
            # 활동 로그 기록
            action_log = ActionLog(
                user_id=current_user.id,
                action='rollback_plugin',
                message=f'플러그인 롤백: {plugin_id} v{old_version} → v{version}',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            db.session.add(action_log)
            db.session.commit()
            
            logger.info(f"플러그인 롤백 완료: {plugin_id} v{old_version} → v{version}")
            
            return {
                'success': True,
                'old_version': old_version,
                'new_version': version,
                'backup_path': str(current_backup)
            }
        
        except Exception as e:
            logger.error(f"플러그인 롤백 실패: {e}")
            raise

# 플러그인 매니저 인스턴스 (지연 초기화)
plugin_manager = None

def get_plugin_manager():
    """플러그인 매니저 인스턴스 반환 (지연 초기화)"""
    global plugin_manager
    if plugin_manager is None:
        plugin_manager = PluginManager()
    return plugin_manager

@plugin_marketplace_bp.route('/api/plugin/market', methods=['GET'])
@login_required
def get_marketplace_plugins():
    """마켓플레이스 플러그인 목록 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('plugin_management', 'view'):
            return jsonify({'error': '플러그인 마켓플레이스 접근 권한이 없습니다.'}), 403
        
        # 쿼리 파라미터
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category')
        search = request.args.get('search')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # 기본 쿼리
        query = Module.query.filter_by(is_marketplace=True)
        
        # 필터링
        if category:
            query = query.filter(Module.category == category)
        if search:
            search_filter = or_(
                Module.name.ilike(f'%{search}%'),
                Module.description.ilike(f'%{search}%'),
                Module.author.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        # 정렬
        if sort_by == 'name':
            order_column = Module.name
        elif sort_by == 'downloads':
            order_column = Module.download_count
        elif sort_by == 'rating':
            order_column = Module.rating
        else:
            order_column = Module.created_at
        
        if sort_order == 'asc':
            query = query.order_by(order_column.asc())
        else:
            query = query.order_by(order_column.desc())
        
        # 페이징
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 결과 데이터 구성
        plugins = []
        for plugin in pagination.items:
            # 설치 상태 확인
            is_installed = PluginInstall.query.filter_by(
                plugin_id=plugin.id,
                target_type='system',
                target_id=0
            ).first() is not None
            
            plugin_data = {
                'id': plugin.id,
                'name': plugin.name,
                'version': plugin.version,
                'description': plugin.description,
                'author': plugin.author,
                'category': plugin.category,
                'tags': plugin.tags,
                'download_count': plugin.download_count,
                'rating': plugin.rating,
                'price': plugin.price,
                'is_free': plugin.is_free,
                'is_installed': is_installed,
                'compatibility': plugin.compatibility,
                'created_at': plugin.created_at.isoformat(),
                'updated_at': plugin.updated_at.isoformat()
            }
            plugins.append(plugin_data)
        
        return jsonify({
            'plugins': plugins,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"마켓플레이스 플러그인 목록 조회 실패: {e}")
        return jsonify({'error': '마켓플레이스 플러그인 목록 조회에 실패했습니다.'}), 500

@plugin_marketplace_bp.route('/api/plugin/market/<plugin_id>', methods=['GET'])
@login_required
def get_marketplace_plugin_detail(plugin_id):
    """마켓플레이스 플러그인 상세 정보"""
    try:
        # 권한 확인
        if not current_user.has_permission('plugin_management', 'view'):
            return jsonify({'error': '플러그인 마켓플레이스 접근 권한이 없습니다.'}), 403
        
        plugin = Module.query.filter_by(id=plugin_id, is_marketplace=True).first()
        if not plugin:
            return jsonify({'error': '존재하지 않는 플러그인입니다.'}), 404
        
        # 설치 상태 확인
        is_installed = PluginInstall.query.filter_by(
            plugin_id=plugin.id,
            target_type='system',
            target_id=0
        ).first() is not None
        
        # 설치된 버전 확인
        installed_version = None
        if is_installed:
            install = PluginInstall.query.filter_by(
                plugin_id=plugin.id,
                target_type='system',
                target_id=0
            ).first()
            installed_version = install.version if install else None
        
        plugin_data = {
            'id': plugin.id,
            'name': plugin.name,
            'version': plugin.version,
            'description': plugin.description,
            'author': plugin.author,
            'category': plugin.category,
            'tags': plugin.tags,
            'download_count': plugin.download_count,
            'rating': plugin.rating,
            'price': plugin.price,
            'is_free': plugin.is_free,
            'is_installed': is_installed,
            'installed_version': installed_version,
            'compatibility': plugin.compatibility,
            'dependencies': plugin.dependencies,
            'changelog': plugin.changelog,
            'release_notes': plugin.release_notes,
            'documentation': plugin.documentation,
            'created_at': plugin.created_at.isoformat(),
            'updated_at': plugin.updated_at.isoformat()
        }
        
        return jsonify(plugin_data)
        
    except Exception as e:
        logger.error(f"마켓플레이스 플러그인 상세 조회 실패: {e}")
        return jsonify({'error': '마켓플레이스 플러그인 상세 조회에 실패했습니다.'}), 500

@plugin_marketplace_bp.route('/api/plugin/market/<plugin_id>/install', methods=['POST'])
@login_required
@csrf.exempt
def install_marketplace_plugin(plugin_id):
    """마켓플레이스 플러그인 설치"""
    try:
        # 권한 확인
        if not current_user.has_permission('plugin_management', 'install'):
            return jsonify({'error': '플러그인 설치 권한이 없습니다.'}), 403
        
        plugin = Module.query.filter_by(id=plugin_id, is_marketplace=True).first()
        if not plugin:
            return jsonify({'error': '존재하지 않는 플러그인입니다.'}), 404
        
        data = request.get_json()
        target_type = data.get('target_type', 'system')
        target_id = data.get('target_id', 0)
        install_options = data.get('install_options', {})
        
        # 플러그인 파일 다운로드
        plugin_file_path = plugin_marketplace_bp.marketplace_dir / f"{plugin.id}.zip"
        if not plugin_file_path.exists():
            return jsonify({'error': '플러그인 파일을 찾을 수 없습니다.'}), 404
        
        # 플러그인 설치
        plugin_mgr = get_plugin_manager()
        result = plugin_mgr.install_plugin(
            plugin_file_path,
            target_type,
            target_id,
            install_options
        )
        
        # 다운로드 카운트 증가
        plugin.download_count += 1
        db.session.commit()
        
        return jsonify({
            'message': '플러그인이 성공적으로 설치되었습니다.',
            'result': result
        })
        
    except Exception as e:
        logger.error(f"마켓플레이스 플러그인 설치 실패: {e}")
        return jsonify({'error': f'플러그인 설치에 실패했습니다: {str(e)}'}), 500

@plugin_marketplace_bp.route('/api/plugin/market/<plugin_id>/uninstall', methods=['POST'])
@login_required
@csrf.exempt
def uninstall_marketplace_plugin(plugin_id):
    """마켓플레이스 플러그인 제거"""
    try:
        # 권한 확인
        if not current_user.has_permission('plugin_management', 'uninstall'):
            return jsonify({'error': '플러그인 제거 권한이 없습니다.'}), 403
        
        data = request.get_json()
        target_type = data.get('target_type', 'system')
        target_id = data.get('target_id', 0)
        
        # 플러그인 제거
        plugin_mgr = get_plugin_manager()
        result = plugin_mgr.uninstall_plugin(plugin_id, target_type, target_id)
        
        return jsonify({
            'message': '플러그인이 성공적으로 제거되었습니다.',
            'result': result
        })
        
    except Exception as e:
        logger.error(f"마켓플레이스 플러그인 제거 실패: {e}")
        return jsonify({'error': f'플러그인 제거에 실패했습니다: {str(e)}'}), 500

@plugin_marketplace_bp.route('/api/plugin/market/<plugin_id>/rollback', methods=['POST'])
@login_required
@csrf.exempt
def rollback_marketplace_plugin(plugin_id):
    """마켓플레이스 플러그인 롤백"""
    try:
        # 권한 확인
        if not current_user.has_permission('plugin_management', 'rollback'):
            return jsonify({'error': '플러그인 롤백 권한이 없습니다.'}), 403
        
        data = request.get_json()
        target_type = data.get('target_type', 'system')
        target_id = data.get('target_id', 0)
        version = data.get('version')
        
        if not version:
            return jsonify({'error': '롤백할 버전을 지정해주세요.'}), 400
        
        # 플러그인 롤백
        plugin_mgr = get_plugin_manager()
        result = plugin_mgr.rollback_plugin(plugin_id, target_type, target_id, version)
        
        return jsonify({
            'message': '플러그인이 성공적으로 롤백되었습니다.',
            'result': result
        })
        
    except Exception as e:
        logger.error(f"마켓플레이스 플러그인 롤백 실패: {e}")
        return jsonify({'error': f'플러그인 롤백에 실패했습니다: {str(e)}'}), 500

@plugin_marketplace_bp.route('/api/plugin/market/stats', methods=['GET'])
@login_required
def get_marketplace_stats():
    """마켓플레이스 통계"""
    try:
        # 권한 확인
        if not current_user.has_permission('plugin_management', 'view'):
            return jsonify({'error': '플러그인 마켓플레이스 접근 권한이 없습니다.'}), 403
        
        # 전체 통계
        total_plugins = Module.query.filter_by(is_marketplace=True).count()
        total_downloads = db.session.query(func.sum(Module.download_count)).filter_by(is_marketplace=True).scalar() or 0
        total_installs = PluginInstall.query.count()
        
        # 카테고리별 통계
        category_stats = db.session.query(
            Module.category,
            func.count(Module.id).label('count'),
            func.sum(Module.download_count).label('downloads')
        ).filter_by(is_marketplace=True).group_by(Module.category).all()
        
        # 최근 설치 통계
        recent_installs = db.session.query(
            PluginInstall.plugin_id,
            PluginInstall.version,
            PluginInstall.installed_at,
            User.username.label('installed_by')
        ).join(User).order_by(PluginInstall.installed_at.desc()).limit(10).all()
        
        # 인기 플러그인
        popular_plugins = db.session.query(
            Module.name,
            Module.download_count,
            Module.rating
        ).filter_by(is_marketplace=True).order_by(Module.download_count.desc()).limit(10).all()
        
        stats = {
            'total_plugins': total_plugins,
            'total_downloads': total_downloads,
            'total_installs': total_installs,
            'category_stats': [
                {
                    'category': stat.category,
                    'count': stat.count,
                    'downloads': stat.downloads or 0
                } for stat in category_stats
            ],
            'recent_installs': [
                {
                    'plugin_id': install.plugin_id,
                    'version': install.version,
                    'installed_at': install.installed_at.isoformat(),
                    'installed_by': install.installed_by
                } for install in recent_installs
            ],
            'popular_plugins': [
                {
                    'name': plugin.name,
                    'download_count': plugin.download_count,
                    'rating': plugin.rating
                } for plugin in popular_plugins
            ]
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"마켓플레이스 통계 조회 실패: {e}")
        return jsonify({'error': '마켓플레이스 통계 조회에 실패했습니다.'}), 500 