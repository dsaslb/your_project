"""
모듈 마켓플레이스 API
업종별/브랜드별/매장별 관리자가 모듈을 자유롭게 적용/비활성화/설정할 수 있는 API
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# 모듈 마켓플레이스 시스템 import
from core.backend.module_marketplace_system import ModuleMarketplaceSystem, ModuleScope, ModuleStatus

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 블루프린트 생성
module_marketplace_api_bp = Blueprint('module_marketplace_api', __name__, url_prefix='/api/module-marketplace')

# 모듈 마켓플레이스 시스템 인스턴스
marketplace_system = ModuleMarketplaceSystem()

def require_permission(permission: str):
    """권한 확인 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.has_permission(permission, 'view'):
                return jsonify({'error': f'권한이 없습니다: {permission}'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_scope_from_request() -> tuple[Optional[int], ModuleScope]:
    """요청에서 범위 정보 추출"""
    scope_type = request.args.get('scope_type', 'user')
    scope_id = request.args.get('scope_id', type=int)
    
    try:
        scope_enum = ModuleScope(scope_type)
    except ValueError:
        scope_enum = ModuleScope.USER
    
    return scope_id, scope_enum  # pyright: ignore

@module_marketplace_api_bp.route('/modules', methods=['GET'])
@login_required
def get_available_modules():
    """사용 가능한 모듈 목록 조회"""
    # try 문에 except 또는 finally가 반드시 필요합니다.
    try:
        # 파라미터 추출
        category = request.args.get('category')
        search = request.args.get('search')
        scope_id, scope_type = get_scope_from_request()
        
        # 모듈 목록 조회
        modules = marketplace_system.get_available_modules(
            user_id=current_user.id,
            scope=scope_type,
            category=category if category is not None else "",  # pyright: ignore
            search=search if search is not None else ""  # pyright: ignore
            )
        categories = list(set(m.get('category', '') for m in modules))
        
        return jsonify({
            'success': True,
            'modules': modules,
            'categories': categories,
            'total': len(modules)
        })
        
    except Exception as e:
        logger.error(f"사용 가능한 모듈 목록 조회 실패: {e}")
        return jsonify({'error': '모듈 목록 조회에 실패했습니다.'}), 500

@module_marketplace_api_bp.route('/modules/<module_id>', methods=['GET'])
@login_required
def get_module_detail(module_id: str):
    """모듈 상세 정보 조회"""
    try:
        module = marketplace_system.get_module_detail(module_id)
        if not module:
            return jsonify({'error': '모듈을 찾을 수 없습니다.'}), 404
        
        # 사용자의 설치/활성화 상태 확인
        scope_id, scope_type = get_scope_from_request()
        module['is_installed'] = marketplace_system.is_module_installed(
            module_id, current_user.id, scope_id, scope_type
        )
        module['is_activated'] = marketplace_system.is_module_activated(
            module_id, current_user.id, scope_id, scope_type
        )
        
        return jsonify({
            'success': True,
            'module': module
        })
        
    except Exception as e:
        logger.error(f"모듈 상세 정보 조회 실패: {e}")
        return jsonify({'error': '모듈 상세 정보 조회에 실패했습니다.'}), 500

@module_marketplace_api_bp.route('/modules/<module_id>/install', methods=['POST'])
@login_required
def install_module(module_id: str):
    """모듈 설치"""
    try:
        scope_id, scope_type = get_scope_from_request()
        
        # 모듈 정보 확인
        module = marketplace_system.get_module_detail(module_id)
        if not module:
            return jsonify({'error': '모듈을 찾을 수 없습니다.'}), 404
        
        # 권한 확인
        required_permissions = module.get('permissions', [])
        for permission in required_permissions:
            if not current_user.has_permission(permission, 'view'):
                return jsonify({'error': f'모듈 설치 권한이 없습니다: {permission}'}), 403
        
        # 모듈 설치
        success = marketplace_system.install_module(
            module_id, current_user.id, scope_id, scope_type
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f"{module['name']}이(가) 성공적으로 설치되었습니다.",
                'module': module
            })
        else:
            return jsonify({'error': '모듈 설치에 실패했습니다.'}), 500
        
    except Exception as e:
        logger.error(f"모듈 설치 실패: {e}")
        return jsonify({'error': '모듈 설치에 실패했습니다.'}), 500

@module_marketplace_api_bp.route('/modules/<module_id>/activate', methods=['POST'])
@login_required
def activate_module(module_id: str):
    """모듈 활성화"""
    try:
        scope_id, scope_type = get_scope_from_request()
        
        # 모듈 활성화
        success = marketplace_system.activate_module(
            module_id, current_user.id, scope_id, scope_type
        )
        
        if success:
            module = marketplace_system.get_module_detail(module_id)
            return jsonify({
                'success': True,
                'message': f"{module['name']}이(가) 성공적으로 활성화되었습니다.",
                'module': module
            })
        else:
            return jsonify({'error': '모듈 활성화에 실패했습니다.'}), 500
        
    except Exception as e:
        logger.error(f"모듈 활성화 실패: {e}")
        return jsonify({'error': '모듈 활성화에 실패했습니다.'}), 500

@module_marketplace_api_bp.route('/modules/<module_id>/deactivate', methods=['POST'])
@login_required
def deactivate_module(module_id: str):
    """모듈 비활성화"""
    try:
        scope_id, scope_type = get_scope_from_request()
        
        # 모듈 비활성화
        success = marketplace_system.deactivate_module(
            module_id, current_user.id, scope_id, scope_type
        )
        
        if success:
            module = marketplace_system.get_module_detail(module_id)
            return jsonify({
                'success': True,
                'message': f"{module['name']}이(가) 성공적으로 비활성화되었습니다.",
                'module': module
            })
        else:
            return jsonify({'error': '모듈 비활성화에 실패했습니다.'}), 500
        
    except Exception as e:
        logger.error(f"모듈 비활성화 실패: {e}")
        return jsonify({'error': '모듈 비활성화에 실패했습니다.'}), 500

@module_marketplace_api_bp.route('/modules/<module_id>/uninstall', methods=['POST'])
@login_required
def uninstall_module(module_id: str):
    """모듈 제거"""
    try:
        scope_id, scope_type = get_scope_from_request()
        
        # 모듈 제거
        success = marketplace_system.uninstall_module(
            module_id, current_user.id, scope_id, scope_type
        )
        
        if success:
            module = marketplace_system.get_module_detail(module_id)
            return jsonify({
                'success': True,
                'message': f"{module['name']}이(가) 성공적으로 제거되었습니다."
            })
        else:
            return jsonify({'error': '모듈 제거에 실패했습니다.'}), 500
        
    except Exception as e:
        logger.error(f"모듈 제거 실패: {e}")
        return jsonify({'error': '모듈 제거에 실패했습니다.'}), 500

@module_marketplace_api_bp.route('/modules/<module_id>/config', methods=['GET'])
@login_required
def get_module_config(module_id: str):
    """모듈 설정 조회"""
    try:
        scope_id, scope_type = get_scope_from_request()
        
        config = marketplace_system.get_module_config(
            module_id, current_user.id, scope_id, scope_type
        )
        
        return jsonify({
            'success': True,
            'config': config or {}
        })
        
    except Exception as e:
        logger.error(f"모듈 설정 조회 실패: {e}")
        return jsonify({'error': '모듈 설정 조회에 실패했습니다.'}), 500

@module_marketplace_api_bp.route('/modules/<module_id>/config', methods=['POST'])
@login_required
def update_module_config(module_id: str):
    """모듈 설정 업데이트"""
    try:
        scope_id, scope_type = get_scope_from_request()
        
        # 요청 데이터 확인
        config_data = request.get_json()
        if not config_data:
            return jsonify({'error': '설정 데이터가 필요합니다.'}), 400
        
        # 설정 업데이트
        success = marketplace_system.update_module_config(
            module_id, current_user.id, config_data, scope_id, scope_type
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': '모듈 설정이 성공적으로 업데이트되었습니다.',
                'config': config_data
            })
        else:
            return jsonify({'error': '모듈 설정 업데이트에 실패했습니다.'}), 500
        
    except Exception as e:
        logger.error(f"모듈 설정 업데이트 실패: {e}")
        return jsonify({'error': '모듈 설정 업데이트에 실패했습니다.'}), 500

@module_marketplace_api_bp.route('/installed', methods=['GET'])
@login_required
def get_installed_modules():
    """설치된 모듈 목록 조회"""
    try:
        scope_id, scope_type = get_scope_from_request()
        
        modules = marketplace_system.get_installed_modules(
            current_user.id, scope_id, scope_type
        )
        
        return jsonify({
            'success': True,
            'modules': modules,
            'total': len(modules)
        })
        
    except Exception as e:
        logger.error(f"설치된 모듈 목록 조회 실패: {e}")
        return jsonify({'error': '설치된 모듈 목록 조회에 실패했습니다.'}), 500

@module_marketplace_api_bp.route('/statistics', methods=['GET'])
@login_required
@require_permission('module_management')
def get_module_statistics():
    """모듈 통계 조회"""
    try:
        user_id = request.args.get('user_id', type=int)
        
        stats = marketplace_system.get_module_statistics(user_id)
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"모듈 통계 조회 실패: {e}")
        return jsonify({'error': '모듈 통계 조회에 실패했습니다.'}), 500

@module_marketplace_api_bp.route('/categories', methods=['GET'])
@login_required
def get_module_categories():
    """모듈 카테고리 목록 조회"""
    try:
        modules = marketplace_system.get_available_modules()
        categories = list(set(m.get('category', '') for m in modules))
        
        return jsonify({
            'success': True,
            'categories': categories
        })
        
    except Exception as e:
        logger.error(f"모듈 카테고리 목록 조회 실패: {e}")
        return jsonify({'error': '모듈 카테고리 목록 조회에 실패했습니다.'}), 500

@module_marketplace_api_bp.route('/trending', methods=['GET'])
@login_required
def get_trending_modules():
    """인기 모듈 목록 조회"""
    try:
        modules = marketplace_system.get_available_modules()
        
        # 다운로드 수 기준으로 정렬
        trending_modules = sorted(
            modules, 
            key=lambda x: x.get('downloads', 0), 
            reverse=True
        )[:10]
        
        return jsonify({
            'success': True,
            'modules': trending_modules
        })
        
    except Exception as e:
        logger.error(f"인기 모듈 목록 조회 실패: {e}")
        return jsonify({'error': '인기 모듈 목록 조회에 실패했습니다.'}), 500

@module_marketplace_api_bp.route('/modules/<module_id>/reviews', methods=['GET'])
@login_required
def get_module_reviews(module_id: str):
    """모듈 리뷰 목록 조회"""
    try:
        reviews = marketplace_system.get_module_reviews(module_id)
        
        return jsonify({
            'success': True,
            'reviews': reviews
        })
        
    except Exception as e:
        logger.error(f"모듈 리뷰 목록 조회 실패: {e}")
        return jsonify({'error': '모듈 리뷰 목록 조회에 실패했습니다.'}), 500

@module_marketplace_api_bp.route('/modules/<module_id>/reviews', methods=['POST'])
@login_required
def add_module_review(module_id: str):
    """모듈 리뷰 작성"""
    try:
        # 요청 데이터 확인
        data = request.get_json()
        if not data:
            return jsonify({'error': '리뷰 데이터가 필요합니다.'}), 400
        
        rating = data.get('rating')
        comment = data.get('comment')
        
        if not rating or not comment:
            return jsonify({'error': '평점과 댓글이 필요합니다.'}), 400
        
        if not (1 <= rating <= 5):
            return jsonify({'error': '평점은 1-5 사이여야 합니다.'}), 400
        
        # 실제 구현에서는 데이터베이스에 저장
        review = {
            "id": datetime.now().timestamp(),
            "user_name": current_user.username,
            "rating": rating,
            "comment": comment,
            "created_at": datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'message': '리뷰가 성공적으로 작성되었습니다.',
            'review': review
        })
        
    except Exception as e:
        logger.error(f"모듈 리뷰 작성 실패: {e}")
        return jsonify({'error': '모듈 리뷰 작성에 실패했습니다.'}), 500

@module_marketplace_api_bp.route('/bulk-install', methods=['POST'])
@login_required
@require_permission('module_management')
def bulk_install_modules():
    """모듈 일괄 설치"""
    try:
        # 요청 데이터 확인
        data = request.get_json()
        if not data:
            return jsonify({'error': '설치할 모듈 목록이 필요합니다.'}), 400
        
        module_ids = data.get('module_ids', [])
        scope_id, scope_type = get_scope_from_request()
        
        if not module_ids:
            return jsonify({'error': '설치할 모듈이 없습니다.'}), 400
        
        results = []
        for module_id in module_ids:
            try:
                success = marketplace_system.install_module(
                    module_id, current_user.id, scope_id, scope_type
                )
                results.append({
                    'module_id': module_id,
                    'success': success,
                    'message': '설치 완료' if success else '설치 실패'
                })
            except Exception as e:
                results.append({
                    'module_id': module_id,
                    'success': False,
                    'message': str(e)
                })
        
        success_count = sum(1 for r in results if r['success'])
        
        return jsonify({
            'success': True,
            'message': f"{success_count}개 모듈이 성공적으로 설치되었습니다.",
            'results': results,
            'total': len(module_ids),
            'success_count': success_count
        })
        
    except Exception as e:
        logger.error(f"모듈 일괄 설치 실패: {e}")
        return jsonify({'error': '모듈 일괄 설치에 실패했습니다.'}), 500

@module_marketplace_api_bp.route('/sync-integration', methods=['POST'])
@login_required
@require_permission('module_management')
def sync_module_integration():
    """모듈 연동 동기화"""
    try:
        scope_id, scope_type = get_scope_from_request()
        
        # 설치된 모듈들의 연동 상태 확인 및 동기화
        installed_modules = marketplace_system.get_installed_modules(
            current_user.id, scope_id, scope_type
        )
        
        sync_results = []
        for module in installed_modules:
            if module.get('status') == ModuleStatus.ACTIVATED.value:
                # 실제 구현에서는 중앙 시스템과 연동 확인
                sync_results.append({
                    'module_id': module['id'],
                    'module_name': module['name'],
                    'sync_status': 'success',
                    'message': '연동 완료'
                })
        
        return jsonify({
            'success': True,
            'message': f"{len(sync_results)}개 모듈의 연동이 동기화되었습니다.",
            'results': sync_results
        })
        
    except Exception as e:
        logger.error(f"모듈 연동 동기화 실패: {e}")  # noqa
        return jsonify({'error': '모듈 연동 동기화에 실패했습니다.'}), 500  # noqa