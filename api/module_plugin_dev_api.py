import logging
from pathlib import Path
from datetime import datetime
import zipfile
import shutil
import json
import os
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, request, jsonify, current_app
query = None  # pyright: ignore
config = None  # pyright: ignore
form = None  # pyright: ignore
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모듈/플러그인 통합 개발 API
모듈과 플러그인을 모두 지원하는 통합 개발 환경 제공
"""


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 블루프린트 생성
module_plugin_dev_bp = Blueprint('module_plugin_dev', __name__, url_prefix='/api/module-plugin-dev')


class ModulePluginDevManager:
    """모듈/플러그인 통합 개발 관리자"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.plugins_dir = self.project_root / "plugins"
        self.sample_modules_dir = self.project_root / "sample_modules"
        self.marketplace_dir = self.project_root / "marketplace"

    def create_project(self,  project_type,  name,  template="basic"):
        """새 프로젝트 생성 (모듈 또는 플러그인)"""
        try:
            if project_type == "plugin":
                target_dir = self.plugins_dir / name
            else:  # module
                target_dir = self.sample_modules_dir / name

            if target_dir.exists():
                return {"success": False, "error": f"{name} 프로젝트가 이미 존재합니다."}

            # 디렉토리 생성
            target_dir.mkdir(parents=True, exist_ok=True)

            # 기본 구조 생성
            self._create_basic_structure(target_dir,  project_type,  name,  template)

            return {
                "success": True,
                "message": f"{project_type} 프로젝트 '{name}' 생성 완료",
                "path": str(target_dir)
            }

        except Exception as e:
            logger.error(f"프로젝트 생성 실패: {e}")
            return {"success": False, "error": str(e)}

    def _create_basic_structure(self,  target_dir,  project_type,  name,  template):
        """기본 프로젝트 구조 생성"""

        # 백엔드 디렉토리
        backend_dir = target_dir / "backend"
        backend_dir.mkdir(exist_ok=True)

        # 설정 디렉토리
        config_dir = target_dir / "config"
        config_dir.mkdir(exist_ok=True)

        # 프론트엔드 디렉토리 (PWA 지원)
        frontend_dir = target_dir / "frontend"
        frontend_dir.mkdir(exist_ok=True)

        # 메타데이터 파일 생성
        if project_type == "plugin":
            self._create_plugin_metadata(target_dir,  name)
        else:
            self._create_module_metadata(target_dir,  name)

        # 기본 파일들 생성
        self._create_basic_files(backend_dir,  frontend_dir,  name,  template)

    def _create_plugin_metadata(self,  target_dir,  name):
        """플러그인 메타데이터 생성"""
        plugin_json = {
            "name": name,
            "version": "1.0.0",
            "description": f"{name} 플러그인",
            "author": "Your Program",
            "type": "plugin",
            "category": "business",
            "tags": ["management", "automation"],
            "dependencies": [],
            "permissions": ["read", "write"],
            "settings": {
                "enabled": True,
                "auto_start": False
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        with open(target_dir / "config" / "plugin.json", "w", encoding="utf-8") as f:
            json.dump(plugin_json, f, indent=2, ensure_ascii=False)

    def _create_module_metadata(self,  target_dir,  name):
        """모듈 메타데이터 생성"""
        module_json = {
            "name": name,
            "version": "1.0.0",
            "description": f"{name} 모듈",
            "author": "Your Program",
            "type": "module",
            "category": "business",
            "tags": ["management", "automation"],
            "dependencies": [],
            "permissions": ["read", "write"],
            "settings": {
                "enabled": True,
                "auto_start": False
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        with open(target_dir / "config" / "module.json", "w", encoding="utf-8") as f:
            json.dump(module_json, f, indent=2, ensure_ascii=False)

    def _create_basic_files(self,  backend_dir,  frontend_dir,  name,  template):
        """기본 파일들 생성"""

        # 백엔드 파일들
        backend_files = {
            "main.py": f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{name} 메인 모듈
"""

from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)

# 블루프린트 생성
{name}_bp = Blueprint('{name}', __name__, url_prefix='/api/{name}')

@{name}_bp.route('/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({{
        "status": "healthy",
        "module": "{name}",
        "timestamp": "{datetime.now().isoformat()}"
    }})

@{name}_bp.route('/status', methods=['GET'])
def get_status():
    """상태 조회"""
    return jsonify({{
        "status": "active",
        "module": "{name}",
        "version": "1.0.0"
    }})
''',
            "models.py": f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{name} 데이터 모델
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class {name.capitalize()}Model(db.Model):
    """{name} 모델"""
    __tablename__ = '{name}_data'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {{
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }}
''',
            "service.py": f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{name} 서비스 로직
"""

from .models import {name.capitalize()}Model, db  # pyright: ignore
import logging

logger = logging.getLogger(__name__)

class {name.capitalize()}Service:
    """{name} 서비스 클래스"""
    
    @staticmethod
    def get_all():
        """모든 데이터 조회"""
        try:
            items = {name.capitalize()}Model.query.all()
            return [item.to_dict() for item in items]
        except Exception as e:
            logger.error(f"데이터 조회 실패: {{e}}")
            return []
    
    @staticmethod
    def create(data):
        """새 데이터 생성"""
        try:
            item = {name.capitalize()}Model(**data)
            db.session.add(item)
            db.session.commit()
            return item.to_dict()
        except Exception as e:
            logger.error(f"데이터 생성 실패: {{e}}")
            db.session.rollback()
            return None
'''
        }

        # 파일 생성
        for filename, content in backend_files.items() if backend_files is not None else []:
            with open(backend_dir / filename, "w", encoding="utf-8") as f:
                f.write(content)

        # 프론트엔드 파일들 (PWA 지원)
        frontend_files = {
            "index.html": f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <link rel="stylesheet" href="styles.css">
    <link rel="manifest" href="manifest.json">
</head>
<body>
    <div id="app">
        <header>
            <h1>{name}</h1>
        </header>
        <main>
            <div id="content">
                <p>환영합니다! {name} 모듈이 로드되었습니다.</p>
            </div>
        </main>
    </div>
    <script src="app.js"></script>
</body>
</html>''',
            "app.js": f'''// {name} 메인 애플리케이션
class {name.capitalize()}App {{
    constructor() {{
        this.init();
    }}
    
    init() {{
        console.log('{name} 앱 초기화');
        this.loadData();
    }}
    
    async loadData() {{
        try {{
            const response = await fetch('/api/{name}/status');
            const data = await response.json();
            console.log('상태:', data);
        }} catch (error) {{
            console.error('데이터 로드 실패:', error);
        }}
    }}
}}

// 앱 시작
document.addEventListener('DOMContentLoaded', () => {{
    new {name.capitalize()}App();
}});''',
            "manifest.json": f'''{{
    "name": "{name}",
    "short_name": "{name}",
    "description": "{name} 모듈",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#ffffff",
    "theme_color": "#000000",
    "icons": [
        {{
            "src": "icon-192.png",
            "sizes": "192x192",
            "type": "image/png"
        }},
        {{
            "src": "icon-512.png",
            "sizes": "512x512",
            "type": "image/png"
        }}
    ]
}}''',
            "styles.css": f'''/* {name} 스타일 */
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f5f5f5;
}}

#app {{
    max-width: 800px;
    margin: 0 auto;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    overflow: hidden;
}}

header {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    text-align: center;
}}

header h1 {{
    margin: 0;
    font-size: 2em;
}}

main {{
    padding: 20px;
}}

#content {{
    text-align: center;
    padding: 40px 20px;
}}

#content p {{
    font-size: 1.2em;
    color: #666;
}}
'''
        }

        # 프론트엔드 파일 생성
        for filename, content in frontend_files.items() if frontend_files is not None else []:
            with open(frontend_dir / filename, "w", encoding="utf-8") as f:
                f.write(content)

    def convert_project(self,  source_path,  target_type):
        """프로젝트 타입 변환 (모듈 ↔ 플러그인)"""
        try:
            source_path = Path(source_path)
            if not source_path.exists():
                return {"success": False, "error": "소스 경로가 존재하지 않습니다."}

            # 메타데이터 파일 확인
            if target_type == "plugin":
                source_meta = source_path / "config" / "module.json"
                target_meta = source_path / "config" / "plugin.json"
                target_dir = self.plugins_dir / source_path.name
            else:
                source_meta = source_path / "config" / "plugin.json"
                target_meta = source_path / "config" / "module.json"
                target_dir = self.sample_modules_dir / source_path.name

            if not source_meta.exists():
                return {"success": False, "error": "메타데이터 파일을 찾을 수 없습니다."}

            # 메타데이터 변환
            with open(source_meta, "r", encoding="utf-8") as f:
                meta_data = json.load(f)

            meta_data["type"] = target_type
            meta_data["updated_at"] = datetime.now().isoformat()

            # 새 위치로 복사
            if target_dir.exists():
                shutil.rmtree(target_dir)
            shutil.copytree(source_path, target_dir)

            # 메타데이터 파일 이름 변경
            target_meta_path = target_dir / "config" / f"{target_type}.json"
            with open(target_meta_path, "w", encoding="utf-8") as f:
                json.dump(meta_data, f, indent=2, ensure_ascii=False)

            # 기존 메타데이터 파일 삭제
            old_meta = target_dir / "config" / f"{'module' if target_type == 'plugin' else 'plugin'}.json"
            if old_meta.exists():
                old_meta.unlink()

            return {
                "success": True,
                "message": f"프로젝트가 {target_type}로 변환되었습니다.",
                "new_path": str(target_dir)
            }

        except Exception as e:
            logger.error(f"프로젝트 변환 실패: {e}")
            return {"success": False, "error": str(e)}

    def get_templates(self):
        """사용 가능한 템플릿 목록 반환"""
        templates = {
            "basic": {
                "name": "기본 템플릿",
                "description": "기본적인 CRUD 기능을 포함한 템플릿",
                "features": ["CRUD", "API", "기본 UI"]
            },
            "pwa": {
                "name": "PWA 템플릿",
                "description": "Progressive Web App 지원 템플릿",
                "features": ["PWA", "오프라인 지원", "푸시 알림"]
            },
            "dashboard": {
                "name": "대시보드 템플릿",
                "description": "차트와 그래프를 포함한 대시보드 템플릿",
                "features": ["차트", "그래프", "실시간 데이터"]
            },
            "ledger": {
                "name": "가계부 템플릿",
                "description": "정기지출/수입 관리 템플릿",
                "features": ["정기지출", "수입관리", "차트", "알림"]
            }
        }
        return templates

    def deploy_to_marketplace(self,  project_path,  metadata):
        """마켓플레이스에 배포"""
        try:
            project_path = Path(project_path)
            if not project_path.exists():
                return {"success": False, "error": "프로젝트 경로가 존재하지 않습니다."}

            # ZIP 파일 생성
            zip_path = self.marketplace_dir / f"{project_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(project_path):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(project_path)
                        zipf.write(file_path, arcname)

            # 마켓플레이스 메타데이터 업데이트
            marketplace_meta = self.marketplace_dir / "modules.json"
            if marketplace_meta.exists():
                with open(marketplace_meta, "r", encoding="utf-8") as f:
                    modules = json.load(f)
            else:
                modules = []

            # 새 모듈 정보 추가
            module_info = {
                "name": metadata.get("name", project_path.name) if metadata else project_path.name,
                "version": metadata.get("version", "1.0.0") if metadata else "1.0.0",
                "description": metadata.get("description", "") if metadata else "",
                "type": metadata.get("type", "module") if metadata else "module",
                "author": metadata.get("author", "Your Program") if metadata else "Your Program",
                "download_url": str(zip_path),
                "created_at": datetime.now().isoformat(),
                "downloads": 0,
                "rating": 0
            }

            modules.append(module_info)

            with open(marketplace_meta, "w", encoding="utf-8") as f:
                json.dump(modules, f, indent=2, ensure_ascii=False)

            return {
                "success": True,
                "message": "마켓플레이스에 배포되었습니다.",
                "zip_path": str(zip_path)
            }

        except Exception as e:
            logger.error(f"마켓플레이스 배포 실패: {e}")
            return {"success": False, "error": str(e)}


# 전역 인스턴스
dev_manager = ModulePluginDevManager()

# API 엔드포인트들


@module_plugin_dev_bp.route('/create', methods=['POST'])
@jwt_required()
def create_project():
    """새 프로젝트 생성"""
    try:
        data = request.get_json()
        project_type = data.get("type", "module") if data else "module"  # module 또는 plugin
        name = data.get("name") if data else None
        template = data.get("template", "basic") if data else "basic"

        if not name:
            return jsonify({"success": False, "error": "프로젝트 이름이 필요합니다."}), 400

        result = dev_manager.create_project(project_type,  name,  template)
        return jsonify(result)

    except Exception as e:
        logger.error(f"프로젝트 생성 API 오류: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@module_plugin_dev_bp.route('/convert', methods=['POST'])
@jwt_required()
def convert_project():
    """프로젝트 타입 변환"""
    try:
        data = request.get_json()
        source_path = data.get("source_path") if data else None
        target_type = data.get("target_type") if data else None  # module 또는 plugin

        if not source_path or not target_type:
            return jsonify({"success": False, "error": "소스 경로와 타겟 타입이 필요합니다."}), 400

        result = dev_manager.convert_project(source_path,  target_type)
        return jsonify(result)

    except Exception as e:
        logger.error(f"프로젝트 변환 API 오류: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@module_plugin_dev_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_templates():
    """사용 가능한 템플릿 목록"""
    try:
        templates = dev_manager.get_templates()
        return jsonify({"success": True, "templates": templates})

    except Exception as e:
        logger.error(f"템플릿 목록 API 오류: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@module_plugin_dev_bp.route('/deploy', methods=['POST'])
@jwt_required()
def deploy_project():
    """마켓플레이스에 배포"""
    try:
        data = request.get_json()
        project_path = data.get("project_path") if data else None
        metadata = data.get("metadata", {}) if data else {}

        if not project_path:
            return jsonify({"success": False, "error": "프로젝트 경로가 필요합니다."}), 400

        result = dev_manager.deploy_to_marketplace(project_path,  metadata)
        return jsonify(result)

    except Exception as e:
        logger.error(f"배포 API 오류: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@module_plugin_dev_bp.route('/list', methods=['GET'])
@jwt_required()
def list_projects():
    """프로젝트 목록 조회"""
    try:
        projects = []

        # 플러그인 목록
        for plugin_dir in dev_manager.plugins_dir.iterdir():
            if plugin_dir.is_dir():
                plugin_meta = plugin_dir / "config" / "plugin.json"
                if plugin_meta.exists():
                    with open(plugin_meta, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    projects.append({
                        "name": meta.get("name", plugin_dir.name) if meta else plugin_dir.name,
                        "type": "plugin",
                        "path": str(plugin_dir),
                        "version": meta.get("version", "1.0.0") if meta else "1.0.0",
                        "description": meta.get("description", "") if meta else "",
                        "enabled": meta.get("settings", {}).get("enabled", True) if meta else True
                    })

        # 모듈 목록
        for module_dir in dev_manager.sample_modules_dir.iterdir():
            if module_dir.is_dir():
                module_meta = module_dir / "config" / "module.json"
                if module_meta.exists():
                    with open(module_meta, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    projects.append({
                        "name": meta.get("name", module_dir.name) if meta else module_dir.name,
                        "type": "module",
                        "path": str(module_dir),
                        "version": meta.get("version", "1.0.0") if meta else "1.0.0",
                        "description": meta.get("description", "") if meta else "",
                        "enabled": meta.get("settings", {}).get("enabled", True) if meta else True
                    })

        return jsonify({"success": True, "projects": projects})

    except Exception as e:
        logger.error(f"프로젝트 목록 API 오류: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
