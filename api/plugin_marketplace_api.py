#!/usr/bin/env python3
"""
플러그인 마켓플레이스 API
플러그인 등록, 검색, 다운로드, 배포 관리 API 엔드포인트
"""

from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import json

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 블루프린트 생성
plugin_marketplace_bp = Blueprint('plugin_marketplace', __name__, url_prefix='/api/marketplace')

# 더미 데코레이터 (실제 구현에서는 utils.auth_decorators 사용)
def admin_required(f):
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def login_required(f):
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# 마켓플레이스 시스템 import
try:
    from core.backend.plugin_marketplace_system import marketplace, deployment_system
except ImportError:
    logger.warning("플러그인 마켓플레이스 시스템을 import할 수 없습니다. 더미 데이터를 사용합니다.")
    
    # 더미 마켓플레이스 데이터
    class DummyMarketplace:
        def search_plugins(self, query="", category="", status="published"):
            return [
                {
                    'plugin_id': 'your_program_management',
                    'name': '레스토랑 관리 플러그인',
                    'description': '레스토랑 운영을 위한 종합 관리 플러그인',
                    'author': 'Admin',
                    'version': '1.0.0',
                    'category': 'business',
                    'status': 'published',
                    'downloads': 150,
                    'rating': 4.5,
                    'rating_count': 25
                },
                {
                    'plugin_id': 'analytics_plugin',
                    'name': '분석 플러그인',
                    'description': '데이터 분석 및 리포트 생성 플러그인',
                    'author': 'Analytics Team',
                    'version': '2.1.0',
                    'category': 'analytics',
                    'status': 'published',
                    'downloads': 89,
                    'rating': 4.2,
                    'rating_count': 18
                }
            ]
        
        def get_plugin_statistics(self):
            return {
                'total_plugins': 2,
                'total_downloads': 239,
                'total_ratings': 43,
                'category_statistics': {
                    'business': {'count': 1, 'downloads': 150, 'avg_rating': 4.5},
                    'analytics': {'count': 1, 'downloads': 89, 'avg_rating': 4.2}
                }
            }
    
    class DummyDeploymentSystem:
        def get_deployment_status(self, plugin_id=None):
            return {
                'your_program_management': {
                    'plugin_id': 'your_program_management',
                    'environment': 'production',
                    'status': 'deployed',
                    'deployed_at': '2024-01-15T10:30:00'
                }
            }
    
    marketplace = DummyMarketplace()
    deployment_system = DummyDeploymentSystem()

@plugin_marketplace_bp.route('/plugins', methods=['GET'])
@login_required
def search_plugins():
    """플러그인 검색 API"""
    try:
        query = request.args.get('query', '')
        category = request.args.get('category', '')
        status = request.args.get('status', 'published')
        limit = int(request.args.get('limit', 20))
        
        plugins = marketplace.search_plugins(query, category, status)
        
        # 제한 적용
        if limit > 0:
            plugins = plugins[:limit]
        
        return jsonify({
            'success': True,
            'data': {
                'plugins': plugins,
                'total': len(plugins),
                'query': query,
                'category': category,
                'status': status
            }
        })
        
    except Exception as e:
        logger.error(f"플러그인 검색 실패: {e}")
        return jsonify({
            'success': False,
            'error': '플러그인 검색 중 오류가 발생했습니다.'
        }), 500

@plugin_marketplace_bp.route('/plugins/<plugin_id>', methods=['GET'])
@login_required
def get_plugin_details(plugin_id: str):
    """플러그인 상세 정보 조회 API"""
    try:
        plugins = marketplace.search_plugins()
        plugin = next((p for p in plugins if p.get('plugin_id') == plugin_id), None)
        
        if not plugin:
            return jsonify({
                'success': False,
                'error': '플러그인을 찾을 수 없습니다.'
            }), 404
        
        # 배포 상태 추가
        deployment_status = deployment_system.get_deployment_status(plugin_id)
        plugin['deployment_status'] = deployment_status
        
        return jsonify({
            'success': True,
            'data': plugin
        })
        
    except Exception as e:
        logger.error(f"플러그인 상세 정보 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': '플러그인 상세 정보 조회 중 오류가 발생했습니다.'
        }), 500

@plugin_marketplace_bp.route('/plugins/<plugin_id>/download', methods=['POST'])
@login_required
def download_plugin(plugin_id: str):
    """플러그인 다운로드 API"""
    try:
        data = request.get_json() or {}
        target_dir = data.get('target_dir', 'plugins/downloaded')
        
        # 임시 디렉토리에 다운로드
        temp_dir = tempfile.mkdtemp()
        
        success = marketplace.download_plugin(plugin_id, temp_dir)
        
        if not success:
            return jsonify({
                'success': False,
                'error': '플러그인 다운로드에 실패했습니다.'
            }), 400
        
        return jsonify({
            'success': True,
            'data': {
                'plugin_id': plugin_id,
                'download_path': temp_dir,
                'message': '플러그인이 성공적으로 다운로드되었습니다.'
            }
        })
        
    except Exception as e:
        logger.error(f"플러그인 다운로드 실패: {e}")
        return jsonify({
            'success': False,
            'error': '플러그인 다운로드 중 오류가 발생했습니다.'
        }), 500

@plugin_marketplace_bp.route('/plugins/<plugin_id>/rate', methods=['POST'])
@login_required
def rate_plugin(plugin_id: str):
    """플러그인 평점 API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '평점 데이터가 필요합니다.'
            }), 400
        
        rating = data.get('rating')
        user_id = getattr(request, 'user_id', 'anonymous')
        
        if not rating or not isinstance(rating, (int, float)):
            return jsonify({
                'success': False,
                'error': '유효한 평점이 필요합니다.'
            }), 400
        
        success = marketplace.rate_plugin(plugin_id, float(rating), user_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': '평점 등록에 실패했습니다.'
            }), 400
        
        return jsonify({
            'success': True,
            'data': {
                'plugin_id': plugin_id,
                'rating': rating,
                'message': '평점이 성공적으로 등록되었습니다.'
            }
        })
        
    except Exception as e:
        logger.error(f"플러그인 평점 실패: {e}")
        return jsonify({
            'success': False,
            'error': '평점 등록 중 오류가 발생했습니다.'
        }), 500

@plugin_marketplace_bp.route('/plugins/register', methods=['POST'])
@admin_required
def register_plugin():
    """플러그인 등록 API"""
    try:
        # 파일 업로드 확인
        if 'plugin_file' not in request.files:
            return jsonify({
                'success': False,
                'error': '플러그인 파일이 필요합니다.'
            }), 400
        
        file = request.files['plugin_file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '파일이 선택되지 않았습니다.'
            }), 400
        
        # 메타데이터 확인
        metadata = request.form.get('metadata')
        if not metadata:
            return jsonify({
                'success': False,
                'error': '플러그인 메타데이터가 필요합니다.'
            }), 400
        
        try:
            metadata = json.loads(metadata)
        except json.JSONDecodeError:
            return jsonify({
                'success': False,
                'error': '유효하지 않은 메타데이터 형식입니다.'
            }), 400
        
        # 임시 디렉토리에 파일 저장
        temp_dir = tempfile.mkdtemp()
        filename = secure_filename(file.filename)
        file_path = os.path.join(temp_dir, filename)
        file.save(file_path)
        
        # ZIP 파일 압축 해제
        import zipfile
        extract_dir = os.path.join(temp_dir, 'extracted')
        os.makedirs(extract_dir, exist_ok=True)
        
        with zipfile.ZipFile(file_path, 'r') as zipf:
            zipf.extractall(extract_dir)
        
        # 플러그인 등록
        success = marketplace.register_plugin(extract_dir, metadata)
        
        if not success:
            return jsonify({
                'success': False,
                'error': '플러그인 등록에 실패했습니다.'
            }), 400
        
        return jsonify({
            'success': True,
            'data': {
                'plugin_id': metadata.get('plugin_id'),
                'message': '플러그인이 성공적으로 등록되었습니다.'
            }
        })
        
    except Exception as e:
        logger.error(f"플러그인 등록 실패: {e}")
        return jsonify({
            'success': False,
            'error': '플러그인 등록 중 오류가 발생했습니다.'
        }), 500

@plugin_marketplace_bp.route('/plugins/<plugin_id>/approve', methods=['POST'])
@admin_required
def approve_plugin(plugin_id: str):
    """플러그인 승인 API"""
    try:
        success = marketplace.approve_plugin(plugin_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': '플러그인 승인에 실패했습니다.'
            }), 400
        
        return jsonify({
            'success': True,
            'data': {
                'plugin_id': plugin_id,
                'message': '플러그인이 성공적으로 승인되었습니다.'
            }
        })
        
    except Exception as e:
        logger.error(f"플러그인 승인 실패: {e}")
        return jsonify({
            'success': False,
            'error': '플러그인 승인 중 오류가 발생했습니다.'
        }), 500

@plugin_marketplace_bp.route('/plugins/<plugin_id>/reject', methods=['POST'])
@admin_required
def reject_plugin(plugin_id: str):
    """플러그인 거부 API"""
    try:
        data = request.get_json() or {}
        reason = data.get('reason', '승인 기준에 맞지 않습니다.')
        
        success = marketplace.reject_plugin(plugin_id, reason)
        
        if not success:
            return jsonify({
                'success': False,
                'error': '플러그인 거부에 실패했습니다.'
            }), 400
        
        return jsonify({
            'success': True,
            'data': {
                'plugin_id': plugin_id,
                'reason': reason,
                'message': '플러그인이 거부되었습니다.'
            }
        })
        
    except Exception as e:
        logger.error(f"플러그인 거부 실패: {e}")
        return jsonify({
            'success': False,
            'error': '플러그인 거부 중 오류가 발생했습니다.'
        }), 500

@plugin_marketplace_bp.route('/statistics', methods=['GET'])
@login_required
def get_marketplace_statistics():
    """마켓플레이스 통계 API"""
    try:
        stats = marketplace.get_plugin_statistics()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"마켓플레이스 통계 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': '통계 조회 중 오류가 발생했습니다.'
        }), 500

@plugin_marketplace_bp.route('/deployments', methods=['GET'])
@admin_required
def get_deployment_status():
    """배포 상태 조회 API"""
    try:
        plugin_id = request.args.get('plugin_id')
        status = deployment_system.get_deployment_status(plugin_id)
        
        return jsonify({
            'success': True,
            'data': status
        })
        
    except Exception as e:
        logger.error(f"배포 상태 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': '배포 상태 조회 중 오류가 발생했습니다.'
        }), 500

@plugin_marketplace_bp.route('/deployments/<plugin_id>/deploy', methods=['POST'])
@admin_required
def deploy_plugin(plugin_id: str):
    """플러그인 배포 API"""
    try:
        data = request.get_json() or {}
        environment = data.get('environment', 'production')
        plugin_path = data.get('plugin_path')
        
        if not plugin_path:
            return jsonify({
                'success': False,
                'error': '플러그인 경로가 필요합니다.'
            }), 400
        
        success = deployment_system.deploy_plugin(plugin_id, plugin_path, environment)
        
        if not success:
            return jsonify({
                'success': False,
                'error': '플러그인 배포에 실패했습니다.'
            }), 400
        
        return jsonify({
            'success': True,
            'data': {
                'plugin_id': plugin_id,
                'environment': environment,
                'message': '플러그인이 성공적으로 배포되었습니다.'
            }
        })
        
    except Exception as e:
        logger.error(f"플러그인 배포 실패: {e}")
        return jsonify({
            'success': False,
            'error': '플러그인 배포 중 오류가 발생했습니다.'
        }), 500

@plugin_marketplace_bp.route('/deployments/<plugin_id>/undeploy', methods=['POST'])
@admin_required
def undeploy_plugin(plugin_id: str):
    """플러그인 배포 해제 API"""
    try:
        data = request.get_json() or {}
        environment = data.get('environment', 'production')
        
        success = deployment_system.undeploy_plugin(plugin_id, environment)
        
        if not success:
            return jsonify({
                'success': False,
                'error': '플러그인 배포 해제에 실패했습니다.'
            }), 400
        
        return jsonify({
            'success': True,
            'data': {
                'plugin_id': plugin_id,
                'environment': environment,
                'message': '플러그인 배포가 해제되었습니다.'
            }
        })
        
    except Exception as e:
        logger.error(f"플러그인 배포 해제 실패: {e}")
        return jsonify({
            'success': False,
            'error': '플러그인 배포 해제 중 오류가 발생했습니다.'
        }), 500

@plugin_marketplace_bp.route('/deployments/history', methods=['GET'])
@admin_required
def get_deployment_history():
    """배포 히스토리 조회 API"""
    try:
        plugin_id = request.args.get('plugin_id')
        limit = int(request.args.get('limit', 50))
        
        history = deployment_system.get_deployment_history(plugin_id, limit)
        
        return jsonify({
            'success': True,
            'data': {
                'history': history,
                'total': len(history)
            }
        })
        
    except Exception as e:
        logger.error(f"배포 히스토리 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': '배포 히스토리 조회 중 오류가 발생했습니다.'
        }), 500

@plugin_marketplace_bp.route('/categories', methods=['GET'])
@login_required
def get_categories():
    """카테고리 목록 조회 API"""
    try:
        categories = [
            {'id': 'business', 'name': '비즈니스', 'description': '비즈니스 관리 플러그인'},
            {'id': 'analytics', 'name': '분석', 'description': '데이터 분석 플러그인'},
            {'id': 'communication', 'name': '커뮤니케이션', 'description': '소통 및 알림 플러그인'},
            {'id': 'security', 'name': '보안', 'description': '보안 및 인증 플러그인'},
            {'id': 'integration', 'name': '통합', 'description': '외부 시스템 연동 플러그인'},
            {'id': 'utility', 'name': '유틸리티', 'description': '편의 기능 플러그인'}
        ]
        
        return jsonify({
            'success': True,
            'data': categories
        })
        
    except Exception as e:
        logger.error(f"카테고리 목록 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': '카테고리 목록 조회 중 오류가 발생했습니다.'
        }), 500 
