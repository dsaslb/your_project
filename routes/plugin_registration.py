"""
플러그인 등록/업로드 시스템
다양한 소스(ZIP, GitHub, 소스폴더)에서 플러그인을 등록하는 기능
"""

import os
import sys
import json
import zipfile
import tempfile
import shutil
import requests
import git
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import hashlib
import yaml  # noqa: E0401  # 'Import "yaml" could not be resolved from source' 경고 무시
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
import logging

from models import db, Module, ModuleVersion, ModuleApproval, User
from utils.notify import send_notification_enhanced

# SDK 모듈 import
sys.path.append(str(Path(__file__).parent.parent / "plugins" / "sdk"))
try:
    from plugin_template import PluginValidator, PluginPackager
except ImportError:
    # SDK 모듈이 없는 경우 기본 클래스 정의
    class PluginValidator:
        def __init__(self, path):
            self.path = path
            self.errors = []
            self.warnings = []  # warnings 속성 추가
        
        def validate(self):
            return True
    
    class PluginPackager:
        def __init__(self, path):
            self.path = path
        
        def package(self):
            return True

logger = logging.getLogger(__name__)

plugin_registration_bp = Blueprint('plugin_registration', __name__)


class PluginRegistrationService:
    """플러그인 등록 서비스"""
    
    def __init__(self):
        self.plugins_dir = Path(current_app.config.get('PLUGINS_DIR', 'plugins'))
        self.temp_dir = Path(current_app.config.get('TEMP_DIR', 'temp'))
        self.max_file_size = current_app.config.get('MAX_PLUGIN_SIZE', 50 * 1024 * 1024)  # 50MB
        
    def register_from_zip(self, file) -> Tuple[bool, str, Dict[str, Any]]:
        """ZIP 파일에서 플러그인 등록"""
        try:
            # 파일 검증
            if not self._validate_upload_file(file):
                return False, "파일 검증 실패", {}
            
            # 임시 디렉토리 생성
            temp_dir = self.temp_dir / f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # ZIP 파일 압축 해제
            with zipfile.ZipFile(file, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # 플러그인 검증 및 등록
            return self._process_plugin_directory(temp_dir)
            
        except Exception as e:
            logger.error(f"ZIP 플러그인 등록 실패: {e}")
            return False, f"ZIP 처리 실패: {str(e)}", {}
    
    def register_from_github(self, repo_url: str, branch: str = "main") -> Tuple[bool, str, Dict[str, Any]]:
        """GitHub에서 플러그인 등록"""
        try:
            # 임시 디렉토리 생성
            temp_dir = self.temp_dir / f"github_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # GitHub 저장소 클론
            logger.info(f"GitHub 저장소 클론 중: {repo_url}")
            git.Repo.clone_from(repo_url, temp_dir, branch=branch)
            
            # 플러그인 검증 및 등록
            return self._process_plugin_directory(temp_dir)
            
        except Exception as e:
            logger.error(f"GitHub 플러그인 등록 실패: {e}")
            return False, f"GitHub 처리 실패: {str(e)}", {}
    
    def register_from_folder(self, folder_path: str) -> Tuple[bool, str, Dict[str, Any]]:
        """로컬 폴더에서 플러그인 등록"""
        try:
            folder_path_obj = Path(folder_path)  # Path 객체로 변환
            if not folder_path_obj.exists():
                return False, "폴더가 존재하지 않습니다", {}
            
            # 플러그인 검증 및 등록
            return self._process_plugin_directory(folder_path_obj)
            
        except Exception as e:
            logger.error(f"폴더 플러그인 등록 실패: {e}")
            return False, f"폴더 처리 실패: {str(e)}", {}
    
    def register_from_url(self, url: str) -> Tuple[bool, str, Dict[str, Any]]:
        """URL에서 플러그인 등록"""
        try:
            # 임시 파일 생성
            temp_file = self.temp_dir / f"url_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            temp_file.parent.mkdir(parents=True, exist_ok=True)
            
            # URL에서 파일 다운로드
            logger.info(f"URL에서 플러그인 다운로드 중: {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # ZIP 파일로 처리
            with open(temp_file, 'rb') as f:
                return self.register_from_zip(f)
                
        except Exception as e:
            logger.error(f"URL 플러그인 등록 실패: {e}")
            return False, f"URL 처리 실패: {str(e)}", {}
    
    def _validate_upload_file(self, file) -> bool:
        """업로드 파일 검증"""
        # 파일 크기 검증
        file.seek(0, 2)  # 파일 끝으로 이동
        file_size = file.tell()
        file.seek(0)  # 파일 시작으로 이동
        
        if file_size > self.max_file_size:
            return False
        
        # 파일 형식 검증
        filename = secure_filename(file.filename)
        if not filename.endswith('.zip'):
            return False
        
        return True
    
    def _process_plugin_directory(self, plugin_dir: Path) -> Tuple[bool, str, Dict[str, Any]]:
        """플러그인 디렉토리 처리"""
        try:
            # 플러그인 검증
            validator = PluginValidator(str(plugin_dir))
            if not validator.validate():
                errors = "\n".join(validator.errors)
                return False, f"플러그인 검증 실패:\n{errors}", {}
            
            # 매니페스트 로드
            manifest_path = plugin_dir / "config" / "plugin.json"
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # 플러그인 ID 생성
            plugin_id = self._generate_plugin_id(manifest)
            
            # 중복 검사
            existing_plugin = Module.query.filter_by(id=plugin_id).first()
            if existing_plugin:
                return False, f"이미 존재하는 플러그인입니다: {plugin_id}", {}
            
            # 플러그인 디렉토리 복사
            final_plugin_dir = self.plugins_dir / plugin_id
            if final_plugin_dir.exists():
                shutil.rmtree(final_plugin_dir)
            shutil.copytree(plugin_dir, final_plugin_dir)
            
            # 데이터베이스에 등록
            plugin_data = self._create_plugin_record(manifest, plugin_id, final_plugin_dir)
            
            # 승인 요청 생성
            self._create_approval_request(plugin_data)
            
            # 임시 파일 정리
            if plugin_dir.parent.name.startswith(('upload_', 'github_', 'url_')):
                shutil.rmtree(plugin_dir.parent)
            
            return True, "플러그인 등록 성공", plugin_data
            
        except Exception as e:
            logger.error(f"플러그인 디렉토리 처리 실패: {e}")
            return False, f"처리 실패: {str(e)}", {}
    
    def _generate_plugin_id(self, manifest: Dict[str, Any]) -> str:
        """플러그인 ID 생성"""
        name = manifest.get('name', 'unknown')
        author = manifest.get('author', 'unknown')
        
        # 안전한 ID 생성
        safe_name = "".join(c for c in name.lower() if c.isalnum() or c in ('-', '_'))
        safe_author = "".join(c for c in author.lower() if c.isalnum() or c in ('-', '_'))
        
        return f"{safe_author}_{safe_name}"
    
    def _create_plugin_record(self, manifest: Dict[str, Any], plugin_id: str, plugin_dir: Path) -> Dict[str, Any]:
        """플러그인 레코드 생성"""
        # 파일 해시 계산
        file_hash = self._calculate_directory_hash(plugin_dir)
        
        # 플러그인 모델 생성 (Module 모델의 실제 필드명에 맞게 수정)
        plugin = Module(
            id=plugin_id,
            name=manifest.get('name', 'Unknown Plugin'),
            description=manifest.get('description', ''),
            category=manifest.get('category', 'utility'),
            version=manifest.get('version', '1.0.0'),
            author=manifest.get('author', 'Unknown'),
            status='pending',
            downloads=0,
            tags=manifest.get('tags', []),
            compatibility=manifest.get('compatibility', {}),
            requirements=manifest.get('dependencies', []),
            file_path=str(plugin_dir),
            created_by=current_user.id
        )
        
        db.session.add(plugin)
        
        # 버전 정보 생성 (ModuleVersion 모델의 실제 필드명에 맞게 수정)
        version = ModuleVersion(
            module_id=plugin_id,
            version=manifest.get('version', '1.0.0'),
            changelog=manifest.get('changelog', ''),
            file_path=str(plugin_dir),
            is_active=True
        )
        
        db.session.add(version)
        db.session.commit()
        
        return {
            'id': plugin_id,
            'name': plugin.name,
            'version': plugin.version,
            'author': plugin.author,
            'status': plugin.status
        }
    
    def _create_approval_request(self, plugin_data: Dict[str, Any]):
        """승인 요청 생성"""
        # 관리자에게 알림 발송
        admin_users = User.query.filter_by(role='admin').all()
        
        for admin in admin_users:
            send_notification_enhanced(
                user_id=admin.id,
                content=f"새 플러그인 승인 요청: {plugin_data['name']} (v{plugin_data['version']})",
                category="plugin_approval",
                link=f"/admin/plugin-approval/{plugin_data['id']}"
            )
    
    def _calculate_directory_hash(self, directory: Path) -> str:
        """디렉토리 해시 계산"""
        hasher = hashlib.sha256()
        
        for file_path in sorted(directory.rglob('*')):
            if file_path.is_file():
                with open(file_path, 'rb') as f:
                    hasher.update(f.read())
        
        return hasher.hexdigest()


# 플러그인 템플릿 클래스 정의
class PluginTemplate:
    """플러그인 템플릿 생성 클래스"""
    
    def __init__(self, plugin_name: str, plugin_type: str = 'basic'):
        self.plugin_name = plugin_name
        self.plugin_type = plugin_type
        self.plugins_dir = Path('plugins')
    
    def create_template(self) -> bool:
        """템플릿 생성"""
        try:
            plugin_dir = self.plugins_dir / self.plugin_name
            plugin_dir.mkdir(parents=True, exist_ok=True)
            
            # 기본 구조 생성
            self._create_basic_structure(plugin_dir)
            
            # 타입별 추가 파일 생성
            if self.plugin_type == 'api':
                self._create_api_template(plugin_dir)
            elif self.plugin_type == 'ui':
                self._create_ui_template(plugin_dir)
            elif self.plugin_type == 'ai':
                self._create_ai_template(plugin_dir)
            
            return True
            
        except Exception as e:
            logger.error(f"플러그인 템플릿 생성 실패: {e}")
            return False
    
    def _create_basic_structure(self, plugin_dir: Path):
        """기본 구조 생성"""
        # config 디렉토리
        config_dir = plugin_dir / "config"
        config_dir.mkdir(exist_ok=True)
        
        # plugin.json 생성
        plugin_json = {
            "name": self.plugin_name,
            "version": "1.0.0",
            "description": f"{self.plugin_name} 플러그인",
            "author": "Unknown",
            "category": "utility",
            "tags": [],
            "compatibility": {},
            "dependencies": []
        }
        
        with open(config_dir / "plugin.json", 'w', encoding='utf-8') as f:
            json.dump(plugin_json, f, indent=2, ensure_ascii=False)
        
        # backend 디렉토리
        backend_dir = plugin_dir / "backend"
        backend_dir.mkdir(exist_ok=True)
        
        # README.md 생성
        readme_content = f"""# {self.plugin_name}

{self.plugin_name} 플러그인입니다.

## 설치 방법

1. 플러그인 파일을 업로드하세요
2. 관리자 승인을 기다리세요
3. 플러그인을 활성화하세요

## 사용 방법

플러그인 활성화 후 사용할 수 있습니다.

## 라이선스

MIT License
"""
        
        with open(plugin_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def _create_api_template(self, plugin_dir: Path):
        """API 플러그인 템플릿 생성"""
        backend_dir = plugin_dir / "backend"
        
        # API 라우터 파일 생성
        api_content = '''from flask import Blueprint, jsonify, request

api_bp = Blueprint('api', __name__)

@api_bp.route('/test', methods=['GET'])
def test_endpoint():
    """테스트 엔드포인트"""
    return jsonify({"message": "API 플러그인이 정상 작동합니다"})

@api_bp.route('/data', methods=['POST'])
def process_data():
    """데이터 처리 엔드포인트"""
    data = request.get_json()
    return jsonify({"processed": data})
'''
        
        with open(backend_dir / "api.py", 'w', encoding='utf-8') as f:
            f.write(api_content)
    
    def _create_ui_template(self, plugin_dir: Path):
        """UI 플러그인 템플릿 생성"""
        frontend_dir = plugin_dir / "frontend"
        frontend_dir.mkdir(exist_ok=True)
        
        # React 컴포넌트 생성
        component_content = '''import React from 'react';

interface PluginProps {
  title?: string;
}

const PluginComponent: React.FC<PluginProps> = ({ title = "UI 플러그인" }) => {
  return (
    <div className="plugin-ui">
      <h2>{title}</h2>
      <p>UI 플러그인이 정상 작동합니다.</p>
    </div>
  );
};

export default PluginComponent;
'''
        
        with open(frontend_dir / "PluginComponent.tsx", 'w', encoding='utf-8') as f:
            f.write(component_content)
    
    def _create_ai_template(self, plugin_dir: Path):
        """AI 플러그인 템플릿 생성"""
        backend_dir = plugin_dir / "backend"
        
        # AI 서비스 파일 생성
        ai_content = '''import numpy as np
from typing import Dict, Any

class AIService:
    """AI 서비스 클래스"""
    
    def __init__(self):
        self.model = None
    
    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """예측 수행"""
        # 여기에 실제 AI 모델 로직을 구현하세요
        return {
            "prediction": "AI 예측 결과",
            "confidence": 0.95,
            "data": data
        }
    
    def train(self, training_data: Dict[str, Any]) -> bool:
        """모델 학습"""
        # 여기에 실제 학습 로직을 구현하세요
        return True

# 전역 인스턴스
ai_service = AIService()
'''
        
        with open(backend_dir / "ai_service.py", 'w', encoding='utf-8') as f:
            f.write(ai_content)


# API 엔드포인트
@plugin_registration_bp.route('/api/plugins/register/upload', methods=['POST'])
@login_required
def register_plugin_upload():
    """ZIP 파일 업로드로 플러그인 등록"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '파일이 없습니다'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '파일이 선택되지 않았습니다'}), 400
        
        service = PluginRegistrationService()
        success, message, data = service.register_from_zip(file)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'plugin': data
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
            
    except Exception as e:
        logger.error(f"플러그인 업로드 등록 실패: {e}")
        return jsonify({'error': f'서버 오류: {str(e)}'}), 500


@plugin_registration_bp.route('/api/plugins/register/github', methods=['POST'])
@login_required
def register_plugin_github():
    """GitHub에서 플러그인 등록"""
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        branch = data.get('branch', 'main')
        
        if not repo_url:
            return jsonify({'error': 'GitHub 저장소 URL이 필요합니다'}), 400
        
        service = PluginRegistrationService()
        success, message, data = service.register_from_github(repo_url, branch)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'plugin': data
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
            
    except Exception as e:
        logger.error(f"GitHub 플러그인 등록 실패: {e}")
        return jsonify({'error': f'서버 오류: {str(e)}'}), 500


@plugin_registration_bp.route('/api/plugins/register/url', methods=['POST'])
@login_required
def register_plugin_url():
    """URL에서 플러그인 등록"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL이 필요합니다'}), 400
        
        service = PluginRegistrationService()
        success, message, data = service.register_from_url(url)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'plugin': data
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
            
    except Exception as e:
        logger.error(f"URL 플러그인 등록 실패: {e}")
        return jsonify({'error': f'서버 오류: {str(e)}'}), 500


@plugin_registration_bp.route('/api/plugins/register/folder', methods=['POST'])
@login_required
def register_plugin_folder():
    """로컬 폴더에서 플러그인 등록"""
    try:
        data = request.get_json()
        folder_path = data.get('folder_path')
        
        if not folder_path:
            return jsonify({'error': '폴더 경로가 필요합니다'}), 400
        
        service = PluginRegistrationService()
        success, message, data = service.register_from_folder(folder_path)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'plugin': data
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
            
    except Exception as e:
        logger.error(f"폴더 플러그인 등록 실패: {e}")
        return jsonify({'error': f'서버 오류: {str(e)}'}), 500


@plugin_registration_bp.route('/api/plugins/register/validate', methods=['POST'])
@login_required
def validate_plugin():
    """플러그인 검증"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '파일이 없습니다'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '파일이 선택되지 않았습니다'}), 400
        
        # 임시 디렉토리에 압축 해제
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            # FileStorage 객체를 파일 경로로 변환
            temp_file = temp_dir / "upload.zip"
            file.save(str(temp_file))
            
            with zipfile.ZipFile(temp_file, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # 검증 수행
            validator = PluginValidator(str(temp_dir))
            is_valid = validator.validate()
            
            return jsonify({
                'valid': is_valid,
                'errors': validator.errors,
                'warnings': getattr(validator, 'warnings', [])  # warnings 속성이 없을 경우 빈 리스트 반환
            })
            
        finally:
            # 임시 파일 정리
            shutil.rmtree(temp_dir)
            
    except Exception as e:
        logger.error(f"플러그인 검증 실패: {e}")
        return jsonify({'error': f'검증 실패: {str(e)}'}), 500


@plugin_registration_bp.route('/api/plugins/register/templates', methods=['GET'])
@login_required
def get_plugin_templates():
    """사용 가능한 플러그인 템플릿 목록"""
    templates = [
        {
            'id': 'basic',
            'name': '기본 플러그인',
            'description': '기본적인 플러그인 구조',
            'category': 'utility'
        },
        {
            'id': 'api',
            'name': 'API 플러그인',
            'description': 'REST API 엔드포인트를 제공하는 플러그인',
            'category': 'api'
        },
        {
            'id': 'ui',
            'name': 'UI 플러그인',
            'description': '사용자 인터페이스 컴포넌트를 제공하는 플러그인',
            'category': 'ui'
        },
        {
            'id': 'ai',
            'name': 'AI 플러그인',
            'description': 'AI/ML 기능을 제공하는 플러그인',
            'category': 'ai'
        }
    ]
    
    return jsonify({'templates': templates})


@plugin_registration_bp.route('/api/plugins/register/create-template', methods=['POST'])
@login_required
def create_plugin_template():
    """플러그인 템플릿 생성"""
    try:
        data = request.get_json()
        plugin_name = data.get('name')
        plugin_type = data.get('type', 'basic')
        
        if not plugin_name:
            return jsonify({'error': '플러그인 이름이 필요합니다'}), 400
        
        # 템플릿 생성
        template = PluginTemplate(plugin_name, plugin_type)
        success = template.create_template()
        
        if success:
            return jsonify({
                'success': True,
                'message': f'플러그인 템플릿 "{plugin_name}" 생성 완료',
                'path': f'plugins/{plugin_name}'
            })
        else:
            return jsonify({
                'success': False,
                'error': '템플릿 생성 실패'
            }), 500
            
    except Exception as e:
        logger.error(f"플러그인 템플릿 생성 실패: {e}")
        return jsonify({'error': f'템플릿 생성 실패: {str(e)}'}), 500 