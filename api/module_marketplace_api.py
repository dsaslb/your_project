"""
모듈 마켓플레이스 API
모듈 설치, 활성화, 설정을 관리하는 API
"""

from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
import json
import logging
from datetime import datetime

from core.backend.module_installation_system import module_installation_system
from utils.auth_utils import admin_required, permission_required  # pyright: ignore

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint 생성
module_marketplace_api_bp = Blueprint('module_marketplace_api', __name__, url_prefix='/api/marketplace')

@module_marketplace_api_bp.route('/modules')
@login_required
def get_available_modules():
    """사용 가능한 모듈 목록 조회"""
    try:
        # 마켓플레이스 모듈 목록 조회
        with open('marketplace/modules.json', 'r', encoding='utf-8') as f:
            modules = json.load(f)
        
        # 사용자 권한에 따른 필터링
        user_role = current_user.role
        user_branch_id = getattr(current_user, 'branch_id', None)
        user_brand_id = getattr(current_user, 'brand_id', None)
        
        filtered_modules = []
        for module_id, module_info in modules.items():
            # 권한 확인
            hierarchy_levels = module_info.get('hierarchy_levels', {})
            if user_role in hierarchy_levels:
                # 설치 상태 확인
                if user_branch_id:
                    installation = module_installation_system.get_installation(
                        module_id, 'branch', user_branch_id
                    )
                elif user_brand_id:
                    installation = module_installation_system.get_installation(
                        module_id, 'brand', user_brand_id
                    )
                else:
                    installation = None
                
                module_info['installation_status'] = installation['status'] if installation else None
                module_info['can_install'] = True
                module_info['can_activate'] = installation and installation['status'] == 'installed'
                module_info['can_deactivate'] = installation and installation['status'] == 'activated'
                module_info['can_uninstall'] = installation and installation['status'] != 'activated'
                
                filtered_modules.append({
                    'id': module_id,
                    **module_info
                })
        
        return jsonify({
            "success": True,
            "data": filtered_modules
        })
        
    except Exception as e:
        logger.error(f"모듈 목록 조회 실패: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@module_marketplace_api_bp.route('/modules/<module_id>/install', methods=['POST'])
@login_required
def install_module(module_id):
    """모듈 설치"""
    try:
        # 사용자 권한 확인
        user_role = current_user.role
        user_branch_id = getattr(current_user, 'branch_id', None)
        user_brand_id = getattr(current_user, 'brand_id', None)
        
        if not user_branch_id and not user_brand_id:
            return jsonify({"success": False, "error": "브랜드 또는 매장 정보가 없습니다."}), 400
        
        # 설치 대상 결정
        if user_role in ['system_admin', 'brand_admin'] and user_brand_id:
            installed_for_type = 'brand'
            installed_for_id = user_brand_id
        elif user_role in ['branch_admin', 'store_manager'] and user_branch_id:
            installed_for_type = 'branch'
            installed_for_id = user_branch_id
        else:
            return jsonify({"success": False, "error": "설치 권한이 없습니다."}), 403
        
        # 모듈 설치
        result = module_installation_system.install_module(
            module_id=module_id,
            installed_by=current_user.id,
            installed_for_type=installed_for_type,
            installed_for_id=installed_for_id
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"모듈 설치 실패: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@module_marketplace_api_bp.route('/modules/<module_id>/activate', methods=['POST'])
@login_required
def activate_module(module_id):
    """모듈 활성화"""
    try:
        # 사용자 권한 확인
        user_role = current_user.role
        user_branch_id = getattr(current_user, 'branch_id', None)
        user_brand_id = getattr(current_user, 'brand_id', None)
        
        if not user_branch_id and not user_brand_id:
            return jsonify({"success": False, "error": "브랜드 또는 매장 정보가 없습니다."}), 400
        
        # 활성화 대상 결정
        if user_role in ['system_admin', 'brand_admin'] and user_brand_id:
            installed_for_type = 'brand'
            installed_for_id = user_brand_id
        elif user_role in ['branch_admin', 'store_manager'] and user_branch_id:
            installed_for_type = 'branch'
            installed_for_id = user_branch_id
        else:
            return jsonify({"success": False, "error": "활성화 권한이 없습니다."}), 403
        
        # 모듈 활성화
        result = module_installation_system.activate_module(
            module_id=module_id,
            installed_for_type=installed_for_type,
            installed_for_id=installed_for_id,
            activated_by=current_user.id
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"모듈 활성화 실패: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@module_marketplace_api_bp.route('/modules/<module_id>/deactivate', methods=['POST'])
@login_required
def deactivate_module(module_id):
    """모듈 비활성화"""
    try:
        # 사용자 권한 확인
        user_role = current_user.role
        user_branch_id = getattr(current_user, 'branch_id', None)
        user_brand_id = getattr(current_user, 'brand_id', None)
        
        if not user_branch_id and not user_brand_id:
            return jsonify({"success": False, "error": "브랜드 또는 매장 정보가 없습니다."}), 400
        
        # 비활성화 대상 결정
        if user_role in ['system_admin', 'brand_admin'] and user_brand_id:
            installed_for_type = 'brand'
            installed_for_id = user_brand_id
        elif user_role in ['branch_admin', 'store_manager'] and user_branch_id:
            installed_for_type = 'branch'
            installed_for_id = user_branch_id
        else:
            return jsonify({"success": False, "error": "비활성화 권한이 없습니다."}), 403
        
        # 모듈 비활성화
        result = module_installation_system.deactivate_module(
            module_id=module_id,
            installed_for_type=installed_for_type,
            installed_for_id=installed_for_id,
            deactivated_by=current_user.id
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"모듈 비활성화 실패: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@module_marketplace_api_bp.route('/modules/<module_id>/uninstall', methods=['POST'])
@login_required
def uninstall_module(module_id):
    """모듈 제거"""
    try:
        # 사용자 권한 확인
        user_role = current_user.role
        user_branch_id = getattr(current_user, 'branch_id', None)
        user_brand_id = getattr(current_user, 'brand_id', None)
        
        if not user_branch_id and not user_brand_id:
            return jsonify({"success": False, "error": "브랜드 또는 매장 정보가 없습니다."}), 400
        
        # 제거 대상 결정
        if user_role in ['system_admin', 'brand_admin'] and user_brand_id:
            installed_for_type = 'brand'
            installed_for_id = user_brand_id
        elif user_role in ['branch_admin', 'store_manager'] and user_branch_id:
            installed_for_type = 'branch'
            installed_for_id = user_branch_id
        else:
            return jsonify({"success": False, "error": "제거 권한이 없습니다."}), 403
        
        # 모듈 제거
        result = module_installation_system.uninstall_module(
            module_id=module_id,
            installed_for_type=installed_for_type,
            installed_for_id=installed_for_id,
            uninstalled_by=current_user.id
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"모듈 제거 실패: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@module_marketplace_api_bp.route('/modules/<module_id>/settings', methods=['GET'])
@login_required
def get_module_settings(module_id):
    """모듈 설정 조회"""
    try:
        # 사용자 권한 확인
        user_role = current_user.role
        user_branch_id = getattr(current_user, 'branch_id', None)
        user_brand_id = getattr(current_user, 'brand_id', None)
        
        if not user_branch_id and not user_brand_id:
            return jsonify({"success": False, "error": "브랜드 또는 매장 정보가 없습니다."}), 400
        
        # 설정 조회 대상 결정
        if user_role in ['system_admin', 'brand_admin'] and user_brand_id:
            installed_for_type = 'brand'
            installed_for_id = user_brand_id
        elif user_role in ['branch_admin', 'store_manager'] and user_branch_id:
            installed_for_type = 'branch'
            installed_for_id = user_branch_id
        else:
            return jsonify({"success": False, "error": "설정 조회 권한이 없습니다."}), 403
        
        # 모듈 설정 조회
        settings = module_installation_system.get_module_settings(
            module_id=module_id,
            installed_for_type=installed_for_type,
            installed_for_id=installed_for_id
        )
        
        return jsonify({
            "success": True,
            "data": settings
        })
        
    except Exception as e:
        logger.error(f"모듈 설정 조회 실패: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@module_marketplace_api_bp.route('/modules/<module_id>/settings', methods=['POST'])
@login_required
def update_module_settings(module_id):
    """모듈 설정 업데이트"""
    try:
        # 사용자 권한 확인
        user_role = current_user.role
        user_branch_id = getattr(current_user, 'branch_id', None)
        user_brand_id = getattr(current_user, 'brand_id', None)
        
        if not user_branch_id and not user_brand_id:
            return jsonify({"success": False, "error": "브랜드 또는 매장 정보가 없습니다."}), 400
        
        # 설정 업데이트 대상 결정
        if user_role in ['system_admin', 'brand_admin'] and user_brand_id:
            installed_for_type = 'brand'
            installed_for_id = user_brand_id
        elif user_role in ['branch_admin', 'store_manager'] and user_branch_id:
            installed_for_type = 'branch'
            installed_for_id = user_branch_id
        else:
            return jsonify({"success": False, "error": "설정 업데이트 권한이 없습니다."}), 403
        
        # 요청 데이터 파싱
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "설정 데이터가 없습니다."}), 400
        
        # 모듈 설정 업데이트
        result = module_installation_system.update_module_settings(
            module_id=module_id,
            installed_for_type=installed_for_type,
            installed_for_id=installed_for_id,
            settings=data
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"모듈 설정 업데이트 실패: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@module_marketplace_api_bp.route('/modules/installed')
@login_required
def get_installed_modules():
    """설치된 모듈 목록 조회"""
    try:
        # 사용자 권한 확인
        user_role = current_user.role
        user_branch_id = getattr(current_user, 'branch_id', None)
        user_brand_id = getattr(current_user, 'brand_id', None)
        
        if not user_branch_id and not user_brand_id:
            return jsonify({"success": False, "error": "브랜드 또는 매장 정보가 없습니다."}), 400
        
        # 설치된 모듈 조회 대상 결정
        if user_role in ['system_admin', 'brand_admin'] and user_brand_id:
            installed_for_type = 'brand'
            installed_for_id = user_brand_id
        elif user_role in ['branch_admin', 'store_manager'] and user_branch_id:
            installed_for_type = 'branch'
            installed_for_id = user_branch_id
        else:
            return jsonify({"success": False, "error": "설치된 모듈 조회 권한이 없습니다."}), 403
        
        # 설치된 모듈 목록 조회
        installations = module_installation_system.get_installations(
            installed_for_type=installed_for_type,
            installed_for_id=installed_for_id
        )
        
        # 마켓플레이스 정보와 결합
        with open('marketplace/modules.json', 'r', encoding='utf-8') as f:
            modules = json.load(f)
        
        for installation in installations:
            if installation['module_id'] in modules:
                installation['module_info'] = modules[installation['module_id']]
        
        return jsonify({
            "success": True,
            "data": installations
        })
        
    except Exception as e:
        logger.error(f"설치된 모듈 목록 조회 실패: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@module_marketplace_api_bp.route('/modules/activated')
@login_required
def get_activated_modules():
    """활성화된 모듈 목록 조회"""
    try:
        # 사용자 권한 확인
        user_role = current_user.role
        user_branch_id = getattr(current_user, 'branch_id', None)
        user_brand_id = getattr(current_user, 'brand_id', None)
        
        if not user_branch_id and not user_brand_id:
            return jsonify({"success": False, "error": "브랜드 또는 매장 정보가 없습니다."}), 400
        
        # 활성화된 모듈 조회 대상 결정
        if user_role in ['system_admin', 'brand_admin'] and user_brand_id:
            installed_for_type = 'brand'
            installed_for_id = user_brand_id
        elif user_role in ['branch_admin', 'store_manager'] and user_branch_id:
            installed_for_type = 'branch'
            installed_for_id = user_branch_id
        else:
            return jsonify({"success": False, "error": "활성화된 모듈 조회 권한이 없습니다."}), 403
        
        # 활성화된 모듈 목록 조회
        activated_modules = module_installation_system.get_activated_modules(
            installed_for_type=installed_for_type,
            installed_for_id=installed_for_id
        )
        
        # 마켓플레이스 정보와 결합
        with open('marketplace/modules.json', 'r', encoding='utf-8') as f:
            modules = json.load(f)
        
        for module in activated_modules:
            if module['module_id'] in modules:
                module['module_info'] = modules[module['module_id']]
        
        return jsonify({
            "success": True,
            "data": activated_modules
        })
        
    except Exception as e:
        logger.error(f"활성화된 모듈 목록 조회 실패: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@module_marketplace_api_bp.route('/modules/statistics')
@login_required
def get_module_statistics():
    """모듈 통계 조회"""
    try:
        # 사용자 권한 확인
        user_role = current_user.role
        user_branch_id = getattr(current_user, 'branch_id', None)
        user_brand_id = getattr(current_user, 'brand_id', None)
        
        if not user_branch_id and not user_brand_id:
            return jsonify({"success": False, "error": "브랜드 또는 매장 정보가 없습니다."}), 400
        
        # 통계 조회 대상 결정
        if user_role in ['system_admin', 'brand_admin'] and user_brand_id:
            installed_for_type = 'brand'
            installed_for_id = user_brand_id
        elif user_role in ['branch_admin', 'store_manager'] and user_branch_id:
            installed_for_type = 'branch'
            installed_for_id = user_branch_id
        else:
            return jsonify({"success": False, "error": "통계 조회 권한이 없습니다."}), 403
        
        # 모듈 통계 조회
        statistics = module_installation_system.get_installation_statistics(
            installed_for_type=installed_for_type,
            installed_for_id=installed_for_id
        )
        
        return jsonify({
            "success": True,
            "data": statistics
        })
        
    except Exception as e:
        logger.error(f"모듈 통계 조회 실패: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@module_marketplace_api_bp.route('/modules/<module_id>/demo')
@login_required
def run_module_demo(module_id):
    """모듈 데모 실행"""
    try:
        # 사용자 권한 확인
        user_role = current_user.role
        user_branch_id = getattr(current_user, 'branch_id', None)
        user_brand_id = getattr(current_user, 'brand_id', None)
        
        if not user_branch_id and not user_brand_id:
            return jsonify({"success": False, "error": "브랜드 또는 매장 정보가 없습니다."}), 400
        
        # 데모 실행 대상 결정
        if user_role in ['system_admin', 'brand_admin'] and user_brand_id:
            installed_for_type = 'brand'
            installed_for_id = user_brand_id
        elif user_role in ['branch_admin', 'store_manager'] and user_branch_id:
            installed_for_type = 'branch'
            installed_for_id = user_branch_id
        else:
            return jsonify({"success": False, "error": "데모 실행 권한이 없습니다."}), 403
        
        # 모듈 설치 상태 확인
        installation = module_installation_system.get_installation(
            module_id, installed_for_type, installed_for_id
        )
        
        if not installation:
            return jsonify({"success": False, "error": "모듈이 설치되지 않았습니다."}), 400
        
        # 데모 실행
        if module_id == 'integrated_module_system':
            # 통합 연동 시스템 데모
            from api.integrated_module_api import integrated_api_bp
            # 데모 실행 로직
            demo_result = {
                "success": True,
                "message": "통합 연동 시스템 데모가 실행되었습니다.",
                "demo_data": {
                    "scenario": "출퇴근 → 매출 → 급여 → 분석 → 알림",
                    "status": "completed"
                }
            }
        else:
            # 일반 모듈 데모
            demo_result = {
                "success": True,
                "message": f"{module_id} 모듈 데모가 실행되었습니다.",
                "demo_data": {
                    "module_id": module_id,
                    "status": "demo_running"
                }
            }
        
        return jsonify(demo_result)
        
    except Exception as e:
        logger.error(f"모듈 데모 실행 실패: {e}")
        return jsonify({"success": False, "error": str(e)}), 500