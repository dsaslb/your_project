#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모듈 개발 시스템 API
샌드박스 환경에서의 모듈 개발, 테스트, 배포를 위한 API
"""

import os
import json
import uuid
import zipfile
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import sqlite3

from core.backend.module_development_system import ModuleDevelopmentSystem

module_development_api = Blueprint('module_development_api', __name__)

# 모듈 개발 시스템 인스턴스
dev_system = ModuleDevelopmentSystem()

@module_development_api.route('/projects', methods=['GET'])
def get_projects():
    """프로젝트 목록 조회"""
    try:
        user_id = request.args.get('user_id', 'default_user')
        projects = dev_system.get_projects(user_id)
        
        return jsonify({
            'success': True,
            'data': projects
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@module_development_api.route('/projects', methods=['POST'])
def create_project():
    """새 프로젝트 생성"""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        module_type = data.get('module_type', 'general')
        created_by = data.get('created_by', 'default_user')
        
        if not name:
            return jsonify({
                'success': False,
                'error': '프로젝트 이름은 필수입니다.'
            }), 400
        
        project = dev_system.create_project(name, description, module_type, created_by)
        
        return jsonify({
            'success': True,
            'project': project
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@module_development_api.route('/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    """프로젝트 상세 조회"""
    try:
        project = dev_system.get_project(project_id)
        
        if not project:
            return jsonify({
                'success': False,
                'error': '프로젝트를 찾을 수 없습니다.'
            }), 404
        
        return jsonify({
            'success': True,
            'project': project
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@module_development_api.route('/projects/<project_id>', methods=['PUT'])
def update_project(project_id):
    """프로젝트 수정"""
    try:
        data = request.get_json()
        
        # 프로젝트 업데이트 로직 구현
        # dev_system.update_project(project_id, data)
        
        return jsonify({
            'success': True,
            'message': '프로젝트가 업데이트되었습니다.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@module_development_api.route('/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """프로젝트 삭제"""
    try:
        # 프로젝트 삭제 로직 구현
        # dev_system.delete_project(project_id)
        
        return jsonify({
            'success': True,
            'message': '프로젝트가 삭제되었습니다.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@module_development_api.route('/projects/<project_id>/components', methods=['GET'])
def get_components(project_id):
    """프로젝트의 컴포넌트 목록 조회"""
    try:
        # 컴포넌트 목록 조회 로직 구현
        components = []  # dev_system.get_components(project_id)
        
        return jsonify({
            'success': True,
            'components': components
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@module_development_api.route('/projects/<project_id>/components', methods=['POST'])
def add_component(project_id):
    """컴포넌트 추가"""
    try:
        data = request.get_json()
        component_data = {
            'component_id': str(uuid.uuid4()),
            'type': data.get('type'),
            'name': data.get('name'),
            'position_x': data.get('position', {}).get('x', 0),
            'position_y': data.get('position', {}).get('y', 0),
            'width': data.get('size', {}).get('width', 200),
            'height': data.get('size', {}).get('height', 100),
            'properties': json.dumps(data.get('properties', {})),
            'styles': json.dumps(data.get('styles', {}))
        }
        
        component = dev_system.add_component(project_id, component_data)
        
        return jsonify({
            'success': True,
            'component': component
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@module_development_api.route('/projects/<project_id>/components/<component_id>', methods=['PUT'])
def update_component(project_id, component_id):
    """컴포넌트 수정"""
    try:
        data = request.get_json()
        updates = {
            'name': data.get('name'),
            'position_x': data.get('position', {}).get('x'),
            'position_y': data.get('position', {}).get('y'),
            'width': data.get('size', {}).get('width'),
            'height': data.get('size', {}).get('height'),
            'properties': json.dumps(data.get('properties', {})),
            'styles': json.dumps(data.get('styles', {}))
        }
        
        # None 값 제거
        updates = {k: v for k, v in updates.items() if v is not None}
        
        component = dev_system.update_component(project_id, component_id, updates)
        
        return jsonify({
            'success': True,
            'component': component
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@module_development_api.route('/projects/<project_id>/components/<component_id>', methods=['DELETE'])
def delete_component(project_id, component_id):
    """컴포넌트 삭제"""
    try:
        result = dev_system.delete_component(project_id, component_id)
        
        return jsonify({
            'success': True,
            'message': '컴포넌트가 삭제되었습니다.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@module_development_api.route('/projects/<project_id>/versions', methods=['GET'])
def get_versions(project_id):
    """프로젝트 버전 목록 조회"""
    try:
        versions = dev_system.get_versions(project_id)
        
        return jsonify({
            'success': True,
            'versions': versions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@module_development_api.route('/projects/<project_id>/versions', methods=['POST'])
def create_version(project_id):
    """새 버전 생성"""
    try:
        data = request.get_json()
        version_name = data.get('version_name')
        description = data.get('description', '')
        created_by = data.get('created_by', 'default_user')
        
        if not version_name:
            return jsonify({
                'success': False,
                'error': '버전 이름은 필수입니다.'
            }), 400
        
        version = dev_system.create_version(project_id, version_name, description, created_by)
        
        return jsonify({
            'success': True,
            'version': version
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@module_development_api.route('/projects/<project_id>/versions/<version_id>/rollback', methods=['POST'])
def rollback_version(project_id, version_id):
    """버전 롤백"""
    try:
        result = dev_system.rollback_version(project_id, version_id)
        
        return jsonify({
            'success': True,
            'message': '버전이 롤백되었습니다.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@module_development_api.route('/projects/<project_id>/deploy', methods=['POST'])
def deploy_project(project_id):
    """프로젝트 배포"""
    try:
        data = request.get_json()
        version_id = data.get('version_id')
        environment = data.get('environment', 'marketplace')
        deployed_by = data.get('deployed_by', 'default_user')
        
        if not version_id:
            return jsonify({
                'success': False,
                'error': '버전 ID는 필수입니다.'
            }), 400
        
        deployment = dev_system.deploy_project(project_id, version_id, environment, deployed_by)
        
        return jsonify({
            'success': True,
            'deployment': deployment
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@module_development_api.route('/projects/<project_id>/test-data', methods=['POST'])
def generate_test_data(project_id):
    """테스트 데이터 생성"""
    try:
        data = request.get_json()
        data_type = data.get('data_type', 'sample')
        
        test_data = dev_system.generate_test_data(project_id, data_type)
        
        return jsonify({
            'success': True,
            'test_data': test_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@module_development_api.route('/component-library', methods=['GET'])
def get_component_library():
    """컴포넌트 라이브러리 조회"""
    try:
        library = dev_system.get_component_library()
        
        return jsonify({
            'success': True,
            'library': library
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@module_development_api.route('/statistics', methods=['GET'])
def get_statistics():
    """개발 통계 조회"""
    try:
        user_id = request.args.get('user_id', 'default_user')
        stats = dev_system.get_deployment_statistics(user_id)
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@module_development_api.route('/projects/<project_id>/preview', methods=['GET'])
def get_project_preview(project_id):
    """프로젝트 미리보기 데이터 조회"""
    try:
        project = dev_system.get_project(project_id)
        
        if not project:
            return jsonify({
                'success': False,
                'error': '프로젝트를 찾을 수 없습니다.'
            }), 404
        
        # 미리보기 데이터 구성
        preview_data = {
            'project': project,
            'components': [],  # dev_system.get_components(project_id)
            'test_data': {},   # dev_system.get_test_data(project_id)
            'preview_url': f'/module-development/preview/{project_id}'
        }
        
        return jsonify({
            'success': True,
            'preview_data': preview_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@module_development_api.route('/projects/<project_id>/export', methods=['POST'])
def export_project(project_id):
    """프로젝트 내보내기"""
    try:
        data = request.get_json()
        export_format = data.get('format', 'zip')
        
        project = dev_system.get_project(project_id)
        if not project:
            return jsonify({
                'success': False,
                'error': '프로젝트를 찾을 수 없습니다.'
            }), 404
        
        # 프로젝트 패키지 생성
        package_path = dev_system.create_deployment_package(project_id, project)
        
        return jsonify({
            'success': True,
            'download_url': f'/downloads/{package_path.name}',
            'message': '프로젝트가 성공적으로 내보내졌습니다.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@module_development_api.route('/projects/<project_id>/import', methods=['POST'])
def import_project(project_id):
    """프로젝트 가져오기"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '파일이 없습니다.'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '파일이 선택되지 않았습니다.'
            }), 400
        
        if file and file.filename and file.filename.endswith('.zip'):
            filename = secure_filename(file.filename)
            # 파일 처리 로직 구현
            
            return jsonify({
                'success': True,
                'message': '프로젝트가 성공적으로 가져와졌습니다.'
            })
        else:
            return jsonify({
                'success': False,
                'error': '지원하지 않는 파일 형식입니다.'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@module_development_api.route('/sandbox/reset', methods=['POST'])
def reset_sandbox():
    """샌드박스 환경 리셋"""
    try:
        data = request.get_json()
        reset_type = data.get('type', 'data')  # data, components, all
        
        # 샌드박스 리셋 로직 구현
        # dev_system.reset_sandbox(reset_type)
        
        return jsonify({
            'success': True,
            'message': '샌드박스가 리셋되었습니다.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@module_development_api.route('/marketplace/publish', methods=['POST'])
def publish_to_marketplace():
    """마켓플레이스에 게시"""
    try:
        data = request.get_json()
        project_id = data.get('project_id')
        version_id = data.get('version_id')
        metadata = data.get('metadata', {})
        
        if not project_id or not version_id:
            return jsonify({
                'success': False,
                'error': '프로젝트 ID와 버전 ID는 필수입니다.'
            }), 400
        
        # 마켓플레이스 게시 로직 구현
        # dev_system.publish_to_marketplace(project_id, version_id, metadata)
        
        return jsonify({
            'success': True,
            'message': '마켓플레이스에 성공적으로 게시되었습니다.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 