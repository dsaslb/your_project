"""
모듈 개발 모드 API
샌드박스 환경에서 모듈을 개발, 테스트, 배포하는 API
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import logging
import sqlite3
import json
from datetime import datetime

from core.backend.module_development_system import module_development_system

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint 생성
module_dev_api_bp = Blueprint('module_dev_api', __name__, url_prefix='/api/module-development')

@module_dev_api_bp.route('/projects', methods=['GET'])
@login_required
def get_projects():
    """개발 프로젝트 목록 조회"""
    try:
        projects = module_development_system.get_development_projects(current_user.id)
        
        return jsonify({
            "success": True,
            "data": projects
        })
        
    except Exception as e:
        logger.error(f"개발 프로젝트 목록 조회 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@module_dev_api_bp.route('/projects', methods=['POST'])
@login_required
def create_project():
    """개발 프로젝트 생성"""
    try:
        data = request.get_json()
        module_id = data.get('module_id')
        project_name = data.get('project_name')
        description = data.get('description', '')
        
        if not module_id or not project_name:
            return jsonify({
                "success": False,
                "error": "모듈 ID와 프로젝트 이름은 필수입니다."
            }), 400
        
        result = module_development_system.create_development_project(
            module_id, project_name, description, current_user.id
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"개발 프로젝트 생성 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@module_dev_api_bp.route('/projects/<project_id>', methods=['GET'])
@login_required
def get_project_details(project_id):
    """프로젝트 상세 정보 조회"""
    try:
        project_details = module_development_system.get_project_details(project_id)
        
        if not project_details:
            return jsonify({
                "success": False,
                "error": "프로젝트를 찾을 수 없습니다."
            }), 404
        
        return jsonify({
            "success": True,
            "data": project_details
        })
        
    except Exception as e:
        logger.error(f"프로젝트 상세 정보 조회 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@module_dev_api_bp.route('/projects/<project_id>/pages', methods=['POST'])
@login_required
def create_page(project_id):
    """페이지 생성"""
    try:
        data = request.get_json()
        page_name = data.get('page_name')
        page_type = data.get('page_type', 'page')
        
        if not page_name:
            return jsonify({
                "success": False,
                "error": "페이지 이름은 필수입니다."
            }), 400
        
        result = module_development_system.create_page(project_id, page_name, page_type)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"페이지 생성 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@module_dev_api_bp.route('/projects/<project_id>/pages/<page_id>/content', methods=['PUT'])
@login_required
def update_page_content(project_id, page_id):
    """페이지 내용 업데이트"""
    try:
        data = request.get_json()
        content = data.get('content')
        
        if not content:
            return jsonify({
                "success": False,
                "error": "페이지 내용은 필수입니다."
            }), 400
        
        result = module_development_system.update_page_content(project_id, page_id, content)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"페이지 내용 업데이트 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@module_dev_api_bp.route('/projects/<project_id>/components', methods=['POST'])
@login_required
def create_component(project_id):
    """컴포넌트 생성"""
    try:
        data = request.get_json()
        component_name = data.get('component_name')
        component_type = data.get('component_type')
        
        if not component_name or not component_type:
            return jsonify({
                "success": False,
                "error": "컴포넌트 이름과 타입은 필수입니다."
            }), 400
        
        result = module_development_system.create_component(project_id, component_name, component_type)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"컴포넌트 생성 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@module_dev_api_bp.route('/projects/<project_id>/apis', methods=['POST'])
@login_required
def create_api_endpoint(project_id):
    """API 엔드포인트 생성"""
    try:
        data = request.get_json()
        endpoint = data.get('endpoint')
        method = data.get('method', 'GET')
        
        if not endpoint:
            return jsonify({
                "success": False,
                "error": "엔드포인트는 필수입니다."
            }), 400
        
        result = module_development_system.create_api_endpoint(project_id, endpoint, method)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API 엔드포인트 생성 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@module_dev_api_bp.route('/projects/<project_id>/versions', methods=['POST'])
@login_required
def create_version(project_id):
    """버전 스냅샷 생성"""
    try:
        data = request.get_json()
        version_name = data.get('version_name', f'버전 {datetime.now().strftime("%Y%m%d_%H%M%S")}')
        
        result = module_development_system.create_version_snapshot(
            project_id, version_name, current_user.id
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"버전 스냅샷 생성 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@module_dev_api_bp.route('/projects/<project_id>/versions/<version_id>/rollback', methods=['POST'])
@login_required
def rollback_version(project_id, version_id):
    """버전 롤백"""
    try:
        result = module_development_system.rollback_to_version(project_id, version_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"버전 롤백 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@module_dev_api_bp.route('/projects/<project_id>/deploy', methods=['POST'])
@login_required
def deploy_project(project_id):
    """프로젝트 배포"""
    try:
        data = request.get_json()
        target_environment = data.get('target_environment', 'marketplace')
        
        result = module_development_system.deploy_project(project_id, target_environment)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"프로젝트 배포 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@module_dev_api_bp.route('/preview/<project_id>', methods=['GET'])
@login_required
def get_project_preview(project_id):
    """프로젝트 미리보기 데이터 조회"""
    try:
        project_details = module_development_system.get_project_details(project_id)
        
        if not project_details:
            return jsonify({
                "success": False,
                "error": "프로젝트를 찾을 수 없습니다."
            }), 404
        
        # 미리보기용 데이터 구성
        preview_data = {
            "project": project_details.get("project", {}),
            "pages": project_details.get("pages", []),
            "components": project_details.get("components", []),
            "apis": project_details.get("apis", []),
            "test_data": project_details.get("test_data", [])
        }
        
        return jsonify({
            "success": True,
            "data": preview_data
        })
        
    except Exception as e:
        logger.error(f"프로젝트 미리보기 조회 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@module_dev_api_bp.route('/test-data/<project_id>/reset', methods=['POST'])
@login_required
def reset_test_data(project_id):
    """테스트 데이터 리셋"""
    try:
        data = request.get_json()
        data_type = data.get('data_type', 'basic')
        
        # 테스트 데이터 재생성
        with sqlite3.connect(module_development_system.dev_db_path) as conn:
            cursor = conn.cursor()
            
            # 기존 테스트 데이터 비활성화
            cursor.execute("""
                UPDATE development_test_data 
                SET is_active = 0 
                WHERE project_id = ?
            """, (project_id,))
            
            # 새 테스트 데이터 생성
            project_details = module_development_system.get_project_details(project_id)
            module_id = project_details.get("project", {}).get("module_id", "")
            
            test_data_content = module_development_system._get_test_data_content(data_type, module_id)
            
            cursor.execute("""
                INSERT INTO development_test_data 
                (project_id, data_set_name, data_type, data_content, is_active)
                VALUES (?, ?, ?, ?, 1)
            """, (
                project_id, f"{data_type} 테스트 데이터", data_type,
                json.dumps(test_data_content)
            ))
            
            conn.commit()
        
        return jsonify({
            "success": True,
            "message": "테스트 데이터가 리셋되었습니다."
        })
        
    except Exception as e:
        logger.error(f"테스트 데이터 리셋 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@module_dev_api_bp.route('/available-modules', methods=['GET'])
@login_required
def get_available_modules():
    """사용 가능한 모듈 목록 조회"""
    try:
        # 마켓플레이스에서 모듈 목록 조회
        with open('marketplace/modules.json', 'r', encoding='utf-8') as f:
            modules = json.load(f)
        
        # 개발 가능한 모듈만 필터링
        available_modules = []
        for module_id, module_info in modules.items():
            if module_info.get('status') == 'active':
                available_modules.append({
                    "id": module_id,
                    "name": module_info.get('name', ''),
                    "description": module_info.get('description', ''),
                    "category": module_info.get('category', ''),
                    "version": module_info.get('version', '1.0.0')
                })
        
        return jsonify({
            "success": True,
            "data": available_modules
        })
        
    except Exception as e:
        logger.error(f"사용 가능한 모듈 목록 조회 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500 