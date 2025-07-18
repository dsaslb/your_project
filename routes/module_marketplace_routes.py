import json
import logging
from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
form = None  # pyright: ignore
"""
모듈 마켓플레이스 라우트
HTML 템플릿을 렌더링하는 라우트
"""


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 블루프린트 생성
module_marketplace_routes_bp = Blueprint('module_marketplace_routes', __name__)


@module_marketplace_routes_bp.route('/module-marketplace')
@login_required
def module_marketplace():
    """모듈 마켓플레이스 페이지"""
    try:
        # 사용자 권한 확인
        if not current_user.has_permission('module_management', 'view'):
            flash('모듈 마켓플레이스에 접근할 권한이 없습니다.', 'error')
            return redirect(url_for('dashboard'))

        # 모듈 상태 관리자 초기화
        from core.backend.module_status_manager import ModuleStatusManager
        status_manager = ModuleStatusManager()

        # 전체 모듈 성능 요약
        performance_summary = status_manager.get_module_performance_summary()

        # 주의가 필요한 모듈 목록
        attention_modules = status_manager.get_modules_needing_attention()

        return render_template('module_marketplace.html',
                               performance_summary=performance_summary,
                               attention_modules=attention_modules)

    except Exception as e:
        logger.error(f"모듈 마켓플레이스 페이지 로드 실패: {e}")
        flash('페이지를 불러오는데 실패했습니다.', 'error')
        return redirect(url_for('dashboard'))


@module_marketplace_routes_bp.route('/module-marketplace/modules/<module_id>')
@login_required
def module_detail(module_id):
    """모듈 상세 페이지"""
    try:
        # 사용자 권한 확인
        if not current_user.has_permission('module_management', 'view'):
            flash('모듈 상세 정보에 접근할 권한이 없습니다.', 'error')
            return redirect(url_for('module_marketplace_routes.module_marketplace'))

        # 모듈 마켓플레이스 시스템 초기화
        from core.backend.module_marketplace_system import ModuleMarketplaceSystem
        marketplace_system = ModuleMarketplaceSystem()

        # 모듈 정보 조회
        module_info = marketplace_system.get_module_detail(module_id)
        if not module_info:
            flash('모듈을 찾을 수 없습니다.', 'error')
            return redirect(url_for('module_marketplace_routes.module_marketplace'))

        # 설치 상태 확인
        is_installed = marketplace_system.is_module_installed(module_id, current_user.id)
        is_activated = marketplace_system.is_module_activated(module_id, current_user.id)

        # 모듈 상태 정보 조회
        from core.backend.module_status_manager import ModuleStatusManager
        status_manager = ModuleStatusManager()
        module_status = status_manager.get_module_status(module_id, current_user.id)

        # 의존성 상태 확인
        dependencies_status = status_manager.check_module_dependencies(module_id)

        # 데모 데이터 확인
        demo_available = module_id in ['attendance_management', 'sales_management', 'inventory_management']

        return render_template('module_details.html',
                               module=module_info,
                               is_installed=is_installed,
                               is_activated=is_activated,
                               module_status=module_status,
                               dependencies_status=dependencies_status,
                               demo_available=demo_available)

    except Exception as e:
        logger.error(f"모듈 상세 페이지 로드 실패: {e}")
        flash(f'모듈 정보를 불러오는 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('module_marketplace_routes.module_marketplace'))


@module_marketplace_routes_bp.route('/module-marketplace/modules/<module_id>/settings')
@login_required
def module_settings(module_id):
    """모듈 설정 페이지"""
    try:
        # 사용자 권한 확인
        if not current_user.has_permission('module_management', 'view'):
            flash('모듈 설정에 접근할 권한이 없습니다.', 'error')
            return redirect(url_for('module_marketplace_routes.module_marketplace'))

        # 마켓플레이스에서 모듈 정보 조회
        with open('marketplace/modules.json', 'r', encoding='utf-8') as f:
            modules = json.load(f)

        if module_id not in modules:
            flash('모듈을 찾을 수 없습니다.', 'error')
            return redirect(url_for('module_marketplace_routes.module_marketplace'))

        module_info = modules[module_id] if modules is not None else None

        # 사용자 권한 확인
        user_role = current_user.role
        user_branch_id = getattr(current_user, 'branch_id', None)
        user_brand_id = getattr(current_user, 'brand_id', None)

        if not user_branch_id and not user_brand_id:
            flash('브랜드 또는 매장 정보가 없습니다.', 'error')
            return redirect(url_for('module_marketplace_routes.module_marketplace'))

        # 설치 상태 확인
        if user_role in ['system_admin', 'brand_admin'] and user_brand_id:
            installed_for_type = 'brand'
            installed_for_id = user_brand_id
        elif user_role in ['branch_admin', 'store_manager'] and user_branch_id:
            installed_for_type = 'branch'
            installed_for_id = user_branch_id
        else:
            flash('설정 권한이 없습니다.', 'error')
            return redirect(url_for('module_marketplace_routes.module_marketplace'))

        # 모듈 설치 시스템에서 설치 정보 조회
        from core.backend.module_installation_system import module_installation_system
        installation = module_installation_system.get_installation(
            module_id, installed_for_type, installed_for_id
        )

        if not installation:
            flash('모듈이 설치되지 않았습니다.', 'error')
            return redirect(url_for('module_marketplace_routes.module_marketplace'))

        # 모듈 설정 조회
        settings = module_installation_system.get_module_settings(
            module_id, installed_for_type, installed_for_id
        )

        return render_template('module_settings.html',
                               module_id=module_id,
                               module_name=module_info['name'] if module_info is not None else None,
                               module_version=module_info['version'] if module_info is not None else None,
                               module_status=installation['status'] if installation is not None else None,
                               module_installed_at=installation['created_at'] if installation is not None else None,
                               module_activated_at=installation.get('activated_at') if installation else None,
                               settings=settings)

    except Exception as e:
        logger.error(f"모듈 설정 페이지 로드 실패: {e}")
        flash('모듈 설정을 불러오는데 실패했습니다.', 'error')
        return redirect(url_for('module_marketplace_routes.module_marketplace'))


@module_marketplace_routes_bp.route('/module-marketplace/modules/<module_id>/onboarding')
@login_required
def module_onboarding(module_id):
    """모듈 온보딩 페이지"""
    try:
        # 사용자 권한 확인
        if not current_user.has_permission('module_management', 'view'):
            flash('모듈 온보딩에 접근할 권한이 없습니다.', 'error')
            return redirect(url_for('module_marketplace_routes.module_marketplace'))

        # 마켓플레이스에서 모듈 정보 조회
        with open('marketplace/modules.json', 'r', encoding='utf-8') as f:
            modules = json.load(f)

        if module_id not in modules:
            flash('모듈을 찾을 수 없습니다.', 'error')
            return redirect(url_for('module_marketplace_routes.module_marketplace'))

        module_info = modules[module_id] if modules is not None else None

        # 사용자 권한 확인
        user_role = current_user.role
        user_branch_id = getattr(current_user, 'branch_id', None)
        user_brand_id = getattr(current_user, 'brand_id', None)

        if not user_branch_id and not user_brand_id:
            flash('브랜드 또는 매장 정보가 없습니다.', 'error')
            return redirect(url_for('module_marketplace_routes.module_marketplace'))

        # 설치 상태 확인
        if user_role in ['system_admin', 'brand_admin'] and user_brand_id:
            installed_for_type = 'brand'
            installed_for_id = user_brand_id
        elif user_role in ['branch_admin', 'store_manager'] and user_branch_id:
            installed_for_type = 'branch'
            installed_for_id = user_branch_id
        else:
            flash('온보딩 권한이 없습니다.', 'error')
            return redirect(url_for('module_marketplace_routes.module_marketplace'))

        # 모듈 설치 시스템에서 설치 정보 조회
        from core.backend.module_installation_system import module_installation_system
        installation = module_installation_system.get_installation(
            module_id, installed_for_type, installed_for_id
        )

        if not installation:
            flash('모듈이 설치되지 않았습니다. 먼저 모듈을 설치해주세요.', 'error')
            return redirect(url_for('module_marketplace_routes.module_detail', module_id=module_id))

        return render_template('module_onboarding.html',
                               module_id=module_id,
                               module_name=module_info['name'] if module_info is not None else None)

    except Exception as e:
        logger.error(f"모듈 온보딩 페이지 로드 실패: {e}")
        flash('모듈 온보딩을 불러오는데 실패했습니다.', 'error')
        return redirect(url_for('module_marketplace_routes.module_marketplace'))


@module_marketplace_routes_bp.route('/module-marketplace/demo/<module_id>')
@login_required
def module_demo(module_id):
    """모듈 데모 페이지"""
    try:
        # 사용자 권한 확인
        if not current_user.has_permission('module_management', 'view'):
            flash('모듈 데모에 접근할 권한이 없습니다.', 'error')
            return redirect(url_for('module_marketplace_routes.module_marketplace'))

        # 데모 가능한 모듈인지 확인
        demo_modules = ['attendance_management', 'sales_management', 'inventory_management', 'integrated_module_system']
        if module_id not in demo_modules:
            flash('이 모듈은 데모를 지원하지 않습니다.', 'error')
            return redirect(url_for('module_marketplace_routes.module_detail', module_id=module_id))

        # 모듈 정보 조회
        from core.backend.module_marketplace_system import ModuleMarketplaceSystem
        marketplace_system = ModuleMarketplaceSystem()
        module_info = marketplace_system.get_module_detail(module_id)

        if module_id == 'attendance_management':
            return redirect(url_for('attendance_demo.demo_dashboard'))
        elif module_id == 'integrated_module_system':
            return render_template('marketplace/demo_integrated.html', module=module_info)
        else:
            flash('데모 페이지가 준비 중입니다.', 'info')
            return redirect(url_for('module_marketplace_routes.module_detail', module_id=module_id))

    except Exception as e:
        logger.error(f"모듈 데모 페이지 로드 실패: {e}")
        flash('데모 페이지를 불러오는데 실패했습니다.', 'error')
        return redirect(url_for('module_marketplace_routes.module_marketplace'))


@module_marketplace_routes_bp.route('/module-marketplace/installed')
@login_required
def installed_modules():
    """설치된 모듈 관리 페이지"""
    try:
        # 사용자 권한 확인
        if not current_user.has_permission('module_management', 'view'):
            flash('설치된 모듈 관리에 접근할 권한이 없습니다.', 'error')
            return redirect(url_for('dashboard'))

        # 설치된 모듈 목록 조회
        from core.backend.module_marketplace_system import ModuleMarketplaceSystem
        marketplace_system = ModuleMarketplaceSystem()
        installed_modules = marketplace_system.get_installed_modules(current_user.id)

        # 모듈 상태 정보 조회
        from core.backend.module_status_manager import ModuleStatusManager
        status_manager = ModuleStatusManager()

        if installed_modules is not None:
            for module in installed_modules:
                module['status_info'] = status_manager.get_module_status(module['id'] if module is not None else None, current_user.id)

        return render_template('installed_modules.html', modules=installed_modules)

    except Exception as e:
        logger.error(f"설치된 모듈 관리 페이지 로드 실패: {e}")
        flash('페이지를 불러오는데 실패했습니다.', 'error')
        return redirect(url_for('dashboard'))


@module_marketplace_routes_bp.route('/module-marketplace/statistics')
@login_required
def module_statistics():
    """모듈 통계 페이지"""
    try:
        # 사용자 권한 확인
        if not current_user.has_permission('module_management', 'view'):
            flash('모듈 통계에 접근할 권한이 없습니다.', 'error')
            return redirect(url_for('dashboard'))

        # 모듈 상태 관리자 초기화
        from core.backend.module_status_manager import ModuleStatusManager
        status_manager = ModuleStatusManager()

        # 성능 요약
        performance_summary = status_manager.get_module_performance_summary()

        # 상태별 모듈 목록
        from core.backend.module_status_manager import ModuleStatus, ModuleHealthStatus
        active_modules = status_manager.get_modules_by_status(ModuleStatus.ACTIVATED)
        error_modules = status_manager.get_modules_by_status(ModuleStatus.ERROR)
        maintenance_modules = status_manager.get_modules_by_status(ModuleStatus.MAINTENANCE)

        return render_template('module_statistics.html',
                               performance_summary=performance_summary,
                               active_modules=active_modules,
                               error_modules=error_modules,
                               maintenance_modules=maintenance_modules)

    except Exception as e:
        logger.error(f"모듈 통계 페이지 로드 실패: {e}")
        flash('페이지를 불러오는데 실패했습니다.', 'error')
        return redirect(url_for('dashboard'))


@module_marketplace_routes_bp.route('/module-marketplace/api/status/<module_id>')
@login_required
def get_module_status_api(module_id):
    """모듈 상태 API"""
    try:
        from core.backend.module_status_manager import ModuleStatusManager
        status_manager = ModuleStatusManager()

        status = status_manager.get_module_status(module_id, current_user.id)

        return jsonify({
            'success': True,
            'status': status
        })

    except Exception as e:
        logger.error(f"모듈 상태 API 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@module_marketplace_routes_bp.route('/module-marketplace/api/status/<module_id>', methods=['POST'])
@login_required
def update_module_status_api(module_id):
    """모듈 상태 업데이트 API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '데이터가 없습니다.'}), 400

        new_status = data.get('status') if data else None
        if not new_status:
            return jsonify({'success': False, 'error': '상태 정보가 없습니다.'}), 400

        from core.backend.module_status_manager import ModuleStatusManager
        status_manager = ModuleStatusManager()

        success = status_manager.update_module_status(module_id, current_user.id, new_status)

        if success:
            return jsonify({
                'success': True,
                'message': '모듈 상태가 업데이트되었습니다.'
            })
        else:
            return jsonify({
                'success': False,
                'error': '모듈 상태 업데이트에 실패했습니다.'
            }), 500

    except Exception as e:
        logger.error(f"모듈 상태 업데이트 API 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@module_marketplace_routes_bp.route('/module-marketplace/api/performance')
@login_required
def get_performance_summary_api():
    """모듈 성능 요약 API"""
    try:
        from core.backend.module_status_manager import ModuleStatusManager
        status_manager = ModuleStatusManager()

        performance_summary = status_manager.get_module_performance_summary()

        return jsonify({
            'success': True,
            'performance_summary': performance_summary
        })

    except Exception as e:
        logger.error(f"모듈 성능 요약 API 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
