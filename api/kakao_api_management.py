import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.kakao_api_config import get_kakao_config, init_kakao_api  # pyright: ignore
from flask_login import login_required, current_user
from flask import Blueprint, jsonify, request
import logging
config = None  # pyright: ignore
from config.config import config_by_name
#!/usr/bin/env python3
"""
카카오 API 관리 API
"""


logger = logging.getLogger(__name__)

kakao_api_bp = Blueprint('kakao_api', __name__)


@kakao_api_bp.route('/api/admin/kakao-api/config', methods=['GET'])
@login_required
def get_kakao_config_api():
    """카카오 API 설정 조회"""
    try:
        if not current_user.is_admin():
            return jsonify({'error': '권한이 없습니다.'}), 403

        config = get_kakao_config()

        # API 키는 마스킹하여 반환
        masked_config = config.config.copy()
        if masked_config.get('api_key'):
            masked_config['api_key'] = masked_config['api_key'][:8] + '***'
        if masked_config.get('rest_api_key'):
            masked_config['rest_api_key'] = masked_config['rest_api_key'][:8] + '***'
        if masked_config.get('javascript_key'):
            masked_config['javascript_key'] = masked_config['javascript_key'][:8] + '***'
        if masked_config.get('admin_key'):
            masked_config['admin_key'] = masked_config['admin_key'][:8] + '***'

        return jsonify({
            'success': True,
            'config': masked_config,
            'enabled': config.is_enabled()
        })

    except Exception as e:
        logger.error(f"카카오 API 설정 조회 실패: {e}")
        return jsonify({'error': '설정 조회에 실패했습니다.'}), 500


@kakao_api_bp.route('/api/admin/kakao-api/config', methods=['POST'])
@login_required
def update_kakao_config_api():
    """카카오 API 설정 업데이트"""
    try:
        if not current_user.is_admin():
            return jsonify({'error': '권한이 없습니다.'}), 403

        data = request.get_json()
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400

        config = get_kakao_config()

        # 업데이트할 설정
        update_data = {}

        if 'api_key' in data:
            update_data['api_key'] = data['api_key']
        if 'rest_api_key' in data:
            update_data['rest_api_key'] = data['rest_api_key']
        if 'javascript_key' in data:
            update_data['javascript_key'] = data['javascript_key']
        if 'admin_key' in data:
            update_data['admin_key'] = data['admin_key']
        if 'enabled' in data:
            update_data['enabled'] = data['enabled']
        if 'rate_limit' in data:
            update_data['rate_limit'] = data['rate_limit']
        if 'timeout' in data:
            update_data['timeout'] = data['timeout']
        if 'cache_ttl' in data:
            update_data['cache_ttl'] = data['cache_ttl']

        # 설정 업데이트
        if update_data:
            success = config.update_config(**update_data)
            if success:
                # API 재초기화
                init_kakao_api()

                return jsonify({
                    'success': True,
                    'message': '카카오 API 설정이 업데이트되었습니다.'
                })
            else:
                return jsonify({'error': '설정 저장에 실패했습니다.'}), 500

        return jsonify({'error': '업데이트할 설정이 없습니다.'}), 400

    except Exception as e:
        logger.error(f"카카오 API 설정 업데이트 실패: {e}")
        return jsonify({'error': '설정 업데이트에 실패했습니다.'}), 500


@kakao_api_bp.route('/api/admin/kakao-api/test', methods=['POST'])
@login_required
def test_kakao_api():
    """카카오 API 연결 테스트"""
    try:
        if not current_user.is_admin():
            return jsonify({'error': '권한이 없습니다.'}), 403

        config = get_kakao_config()

        if not config.is_enabled():
            return jsonify({
                'success': False,
                'message': '카카오 API가 비활성화되어 있습니다.'
            })

        # API 연결 테스트
        success, message = config.test_connection()

        return jsonify({
            'success': success,
            'message': message
        })

    except Exception as e:
        logger.error(f"카카오 API 테스트 실패: {e}")
        return jsonify({'error': 'API 테스트에 실패했습니다.'}), 500


@kakao_api_bp.route('/api/admin/kakao-api/status', methods=['GET'])
@login_required
def get_kakao_api_status():
    """카카오 API 상태 조회"""
    try:
        if not current_user.is_admin():
            return jsonify({'error': '권한이 없습니다.'}), 403

        config = get_kakao_config()

        status = {
            'enabled': config.is_enabled(),
            'has_api_key': bool(config.get_api_key()),
            'has_rest_api_key': bool(config.get_rest_api_key()),
            'config_file_exists': config.config_file.exists()
        }

        # API 키가 있으면 연결 테스트
        if status['enabled']:
            success, message = config.test_connection()
            status['connection_test'] = {
                'success': success,
                'message': message
            }

        return jsonify({
            'success': True,
            'status': status
        })

    except Exception as e:
        logger.error(f"카카오 API 상태 조회 실패: {e}")
        return jsonify({'error': '상태 조회에 실패했습니다.'}), 500
