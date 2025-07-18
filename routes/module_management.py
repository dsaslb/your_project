from utils.auth_decorators import admin_required, manager_required  # pyright: ignore
from typing import Dict, List, Any
import logging
import os
import json
from datetime import datetime
from flask_login import login_required, current_user
from flask import Blueprint, jsonify, request, current_app
form = None  # pyright: ignore
"""
모듈 관리 API
사용자가 설치한 모듈을 관리하는 시스템
"""


# 데코레이터 import

logger = logging.getLogger(__name__)

module_management_bp = Blueprint('module_management', __name__)

# 사용자별 설치된 모듈 (실제로는 데이터베이스에서 관리)
user_installed_modules = {
    'admin': ['attendance_management', 'inventory_management', 'customer_feedback']
}

# 모듈 설정 데이터 (실제로는 데이터베이스에서 관리)
module_settings: Dict[str, Dict[str, Any] if Dict is not None else None] = {
    'admin_attendance_management': {
        'is_active': True,
        'auto_backup': True,
        'notification_enabled': True,
        'work_hours': {'start': '09:00', 'end': '18:00'},
        'break_time': 60
    },
    'admin_inventory_management': {
        'is_active': True,
        'low_stock_threshold': 10,
        'auto_reorder': True,
        'notification_enabled': True
    },
    'admin_customer_feedback': {
        'is_active': False,
        'auto_response': True,
        'rating_threshold': 3,
        'notification_enabled': True
    }
}


@module_management_bp.route('/api/modules/installed', methods=['GET'])
def get_installed_modules():
    """설치된 모듈 목록 조회"""
    try:
        # 로그인 상태 확인
        if not current_user.is_authenticated:
            return jsonify({'error': '로그인이 필요합니다.'}), 401

        user_id = getattr(current_user, 'id', None)
        if not user_id:
            return jsonify({'error': '사용자 정보를 찾을 수 없습니다.'}), 400

        user_modules = user_installed_modules.get(user_id, [])
        installed_modules = []

        # 마켓플레이스에서 모듈 정보 가져오기
        from routes.module_marketplace import marketplace_modules

        for module_id in user_modules:
            if module_id in marketplace_modules:
                module = marketplace_modules[module_id].copy()
                module['installed_at'] = datetime.now().isoformat()  # 실제로는 설치 시간 저장
                module['is_active'] = module_settings.get(
                    f"{user_id}_{module_id}", {}).get('is_active', True)
                module['settings'] = module_settings.get(f"{user_id}_{module_id}", {})
                installed_modules.append(module)

        return jsonify({
            'success': True,
            'modules': installed_modules,
            'total_installed': len(installed_modules)
        })

    except Exception as e:
        logger.error(f"설치된 모듈 목록 조회 실패: {e}")
        return jsonify({'error': '설치된 모듈 목록 조회에 실패했습니다.'}), 500


@module_management_bp.route('/api/modules/<module_id>/activate', methods=['POST'])
def activate_module(module_id: str):
    """모듈 활성화"""
    try:
        # 설치된 모듈인지 확인
        user_modules = user_installed_modules.get(current_user.id, [])
        if module_id not in user_modules:
            return jsonify({'error': '설치되지 않은 모듈입니다.'}), 400

        # 모듈 활성화
        setting_key = f"{current_user.id}_{module_id}"
        if setting_key not in module_settings:
            module_settings[setting_key] = {}

        module_settings[setting_key]['is_active'] = True
        module_settings[setting_key]['activated_at'] = datetime.now().isoformat()

        logger.info(f"모듈 활성화: {current_user.username} -> {module_id}")

        return jsonify({
            'success': True,
            'message': '모듈이 활성화되었습니다.'
        })

    except Exception as e:
        logger.error(f"모듈 활성화 실패: {e}")
        return jsonify({'error': '모듈 활성화에 실패했습니다.'}), 500


@module_management_bp.route('/api/modules/<module_id>/deactivate', methods=['POST'])
def deactivate_module(module_id: str):
    """모듈 비활성화"""
    try:
        # 설치된 모듈인지 확인
        user_modules = user_installed_modules.get(current_user.id, [])
        if module_id not in user_modules:
            return jsonify({'error': '설치되지 않은 모듈입니다.'}), 400

        # 모듈 비활성화
        setting_key = f"{current_user.id}_{module_id}"
        if setting_key not in module_settings:
            module_settings[setting_key] = {}

        module_settings[setting_key]['is_active'] = False
        module_settings[setting_key]['deactivated_at'] = datetime.now().isoformat()

        logger.info(f"모듈 비활성화: {current_user.username} -> {module_id}")

        return jsonify({
            'success': True,
            'message': '모듈이 비활성화되었습니다.'
        })

    except Exception as e:
        logger.error(f"모듈 비활성화 실패: {e}")
        return jsonify({'error': '모듈 비활성화에 실패했습니다.'}), 500


@module_management_bp.route('/api/modules/<module_id>/settings', methods=['GET'])
def get_module_settings(module_id: str):
    """모듈 설정 조회"""
    try:
        # 로그인 상태 확인
        if not current_user.is_authenticated:
            return jsonify({'error': '로그인이 필요합니다.'}), 401

        user_id = getattr(current_user, 'id', None)
        if not user_id:
            return jsonify({'error': '사용자 정보를 찾을 수 없습니다.'}), 400

        # 설치된 모듈인지 확인
        user_modules = user_installed_modules.get(current_user.id, [])
        if module_id not in user_modules:
            return jsonify({'error': '설치되지 않은 모듈입니다.'}), 400

        # 모듈 설정 조회
        setting_key = f"{user_id}_{module_id}"
        settings = module_settings.get(setting_key, {})

        # 마켓플레이스에서 모듈 정보 가져오기
        from routes.module_marketplace import marketplace_modules
        module_info = marketplace_modules.get(module_id, {})

        return jsonify({
            'success': True,
            'module_id': module_id,
            'module_name': module_info.get('name', ''),
            'settings': settings,
            'default_settings': get_default_settings(module_id)
        })

    except Exception as e:
        logger.error(f"모듈 설정 조회 실패: {e}")
        return jsonify({'error': '모듈 설정 조회에 실패했습니다.'}), 500


@module_management_bp.route('/api/modules/<module_id>/settings', methods=['PUT'])
def update_module_settings(module_id: str):
    """모듈 설정 업데이트"""
    try:
        # 설치된 모듈인지 확인
        user_modules = user_installed_modules.get(current_user.id, [])
        if module_id not in user_modules:
            return jsonify({'error': '설치되지 않은 모듈입니다.'}), 400

        data = request.get_json()
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400

        # 모듈 설정 업데이트
        setting_key = f"{current_user.id}_{module_id}"
        if setting_key not in module_settings:
            module_settings[setting_key] = {}

        module_settings[setting_key].update(data)
        module_settings[setting_key]['updated_at'] = datetime.now().isoformat()

        logger.info(f"모듈 설정 업데이트: {current_user.username} -> {module_id}")

        return jsonify({
            'success': True,
            'message': '모듈 설정이 업데이트되었습니다.',
            'settings': module_settings[setting_key]
        })

    except Exception as e:
        logger.error(f"모듈 설정 업데이트 실패: {e}")
        return jsonify({'error': '모듈 설정 업데이트에 실패했습니다.'}), 500


@module_management_bp.route('/api/modules/<module_id>/uninstall', methods=['POST'])
def uninstall_module(module_id: str):
    """모듈 제거"""
    try:
        # 설치된 모듈인지 확인
        user_modules = user_installed_modules.get(current_user.id, [])
        if module_id not in user_modules:
            return jsonify({'error': '설치되지 않은 모듈입니다.'}), 400

        # 모듈 제거
        user_installed_modules[current_user.id].remove(module_id)

        # 설정도 제거
        setting_key = f"{current_user.id}_{module_id}"
        if setting_key in module_settings:
            del module_settings[setting_key]

        logger.info(f"모듈 제거: {current_user.username} -> {module_id}")

        return jsonify({
            'success': True,
            'message': '모듈이 제거되었습니다.'
        })

    except Exception as e:
        logger.error(f"모듈 제거 실패: {e}")
        return jsonify({'error': '모듈 제거에 실패했습니다.'}), 500


@module_management_bp.route('/api/modules/<module_id>/update', methods=['POST'])
def update_module(module_id: str):
    """모듈 업데이트"""
    try:
        # 설치된 모듈인지 확인
        user_modules = user_installed_modules.get(current_user.id, [])
        if module_id not in user_modules:
            return jsonify({'error': '설치되지 않은 모듈입니다.'}), 400

        # 마켓플레이스에서 최신 버전 확인
        from routes.module_marketplace import marketplace_modules
        module_info = marketplace_modules.get(module_id, {})

        if not module_info:
            return jsonify({'error': '모듈 정보를 찾을 수 없습니다.'}), 404

        # 업데이트 로그 기록
        logger.info(f"모듈 업데이트: {current_user.username} -> {module_id}")

        return jsonify({
            'success': True,
            'message': f"{module_info.get('name', '')}이(가) 최신 버전으로 업데이트되었습니다.",
            'current_version': module_info.get('version', '')
        })

    except Exception as e:
        logger.error(f"모듈 업데이트 실패: {e}")
        return jsonify({'error': '모듈 업데이트에 실패했습니다.'}), 500


@module_management_bp.route('/api/modules/statistics', methods=['GET'])
def get_module_statistics():
    """모듈 사용 통계"""
    try:
        user_modules = user_installed_modules.get(current_user.id, [])

        # 마켓플레이스에서 모듈 정보 가져오기
        from routes.module_marketplace import marketplace_modules

        active_modules = 0
        total_downloads = 0
        avg_rating = 0

        for module_id in user_modules:
            if module_id in marketplace_modules:
                module = marketplace_modules[module_id]
                # 안전한 float 변환을 위한 타입 체크
                downloads = module.get('downloads', 0)
                rating = module.get('rating', 0)

                # downloads가 숫자 타입인지 확인
                if isinstance(downloads, (int, float)):
                    total_downloads += float(downloads)
                else:
                    total_downloads += 0.0  # pyright: ignore

                # rating이 숫자 타입인지 확인
                if isinstance(rating, (int, float)):
                    avg_rating += float(rating)
                else:
                    avg_rating += 0.0  # pyright: ignore

                # 활성화된 모듈 수 계산
                setting_key = f"{current_user.id}_{module_id}"
                if module_settings.get(setting_key, {}).get('is_active', True):
                    active_modules += 1

        if user_modules:
            avg_rating = avg_rating / len(user_modules)

        return jsonify({
            'success': True,
            'statistics': {
                'total_installed': len(user_modules),
                'active_modules': active_modules,
                'inactive_modules': len(user_modules) - active_modules,
                'total_downloads': total_downloads,
                'average_rating': round(avg_rating, 1)
            }
        })

    except Exception as e:
        logger.error(f"모듈 통계 조회 실패: {e}")
        return jsonify({'error': '모듈 통계 조회에 실패했습니다.'}), 500


def get_default_settings(module_id: str) -> Dict[str, Any] if Dict is not None else None:
    """모듈별 기본 설정 반환"""
    default_settings = {
        'qsc_system': {
            'auto_notification': True,
            'notification_interval': 24,  # 시간
            'report_frequency': 'weekly',
            'score_threshold': 80
        },
        'checklist_system': {
            'auto_reminder': True,
            'reminder_time': '09:00',
            'completion_threshold': 90,
            'team_notification': True
        },
        'cooktime_system': {
            'prediction_accuracy': 0.9,
            'update_frequency': 'daily',
            'alert_threshold': 120,  # 분
            'auto_adjustment': True
        },
        'kitchen_monitor': {
            'monitoring_interval': 5,  # 분
            'alert_temperature': 80,  # 섭씨
            'maintenance_reminder': True,
            'auto_shutdown': False
        },
        'ai_diagnosis': {
            'analysis_frequency': 'daily',
            'prediction_horizon': 30,  # 일
            'confidence_threshold': 0.8,
            'auto_optimization': True
        },
        'plugin_registration': {
            'auto_validation': True,
            'security_scan': True,
            'backup_enabled': True,
            'update_check': True
        },
        'attendance_management': {
            'work_start_time': '09:00',
            'work_end_time': '18:00',
            'late_threshold_minutes': 10,
            'overtime_threshold_hours': 8,
            'auto_notification': True,
            'notification_interval': 5,
            'work_types': ['정규', '시급', '파트타임', '인턴']
        }
    }

    return default_settings.get(module_id, {})
