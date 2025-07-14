"""
메뉴 API
사용자별 메뉴를 제공하는 API
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import logging

from core.backend.menu_integration_system import menu_integration_system

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint 생성
menu_api_bp = Blueprint('menu_api', __name__, url_prefix='/api/menu')

@menu_api_bp.route('/user-menus')
@login_required
def get_user_menus():
    """사용자별 메뉴 조회"""
    try:
        # 사용자 정보 확인
        user_role = current_user.role
        user_branch_id = getattr(current_user, 'branch_id', None)
        user_brand_id = getattr(current_user, 'brand_id', None)
        
        if not user_branch_id and not user_brand_id:
            return jsonify({
                "success": False,
                "error": "브랜드 또는 매장 정보가 없습니다."
            }), 400
        
        # 메뉴 조회 대상 결정
        if user_role in ['system_admin', 'brand_admin'] and user_brand_id:
            installed_for_type = 'brand'
            installed_for_id = user_brand_id
        elif user_role in ['branch_admin', 'store_manager'] and user_branch_id:
            installed_for_type = 'branch'
            installed_for_id = user_branch_id
        else:
            return jsonify({
                "success": False,
                "error": "메뉴 조회 권한이 없습니다."
            }), 403
        
        # 사용자 메뉴 조회
        menus = menu_integration_system.get_user_menus(
            current_user.id, user_role, installed_for_type, installed_for_id
        )
        
        return jsonify({
            "success": True,
            "data": menus
        })
        
    except Exception as e:
        logger.error(f"사용자 메뉴 조회 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@menu_api_bp.route('/menu-access/<int:menu_id>', methods=['POST'])
@login_required
def record_menu_access(menu_id):
    """메뉴 접근 기록"""
    try:
        # 메뉴 접근 통계 업데이트
        menu_integration_system.update_menu_access(menu_id, current_user.id)
        
        return jsonify({
            "success": True,
            "message": "메뉴 접근이 기록되었습니다."
        })
        
    except Exception as e:
        logger.error(f"메뉴 접근 기록 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@menu_api_bp.route('/statistics')
@login_required
def get_menu_statistics():
    """메뉴 통계 조회"""
    try:
        # 사용자 정보 확인
        user_role = current_user.role
        user_branch_id = getattr(current_user, 'branch_id', None)
        user_brand_id = getattr(current_user, 'brand_id', None)
        
        if not user_branch_id and not user_brand_id:
            return jsonify({
                "success": False,
                "error": "브랜드 또는 매장 정보가 없습니다."
            }), 400
        
        # 통계 조회 대상 결정
        if user_role in ['system_admin', 'brand_admin'] and user_brand_id:
            installed_for_type = 'brand'
            installed_for_id = user_brand_id
        elif user_role in ['branch_admin', 'store_manager'] and user_branch_id:
            installed_for_type = 'branch'
            installed_for_id = user_branch_id
        else:
            return jsonify({
                "success": False,
                "error": "통계 조회 권한이 없습니다."
            }), 403
        
        # 메뉴 통계 조회
        statistics = menu_integration_system.get_menu_statistics(
            installed_for_type, installed_for_id
        )
        
        return jsonify({
            "success": True,
            "data": statistics
        })
        
    except Exception as e:
        logger.error(f"메뉴 통계 조회 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500 