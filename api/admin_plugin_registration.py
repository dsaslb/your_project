from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from datetime import datetime
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# Blueprint 생성
admin_plugin_registration_bp = Blueprint('admin_plugin_registration', __name__)

@admin_plugin_registration_bp.route('/api/admin/plugin/register', methods=['POST'])
@cross_origin()
def register_plugin():
    """관리자용 플러그인 등록 API"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['name', 'display_name', 'description', 'version', 'author', 'category', 'file_path']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'필수 필드가 누락되었습니다: {field}'
                }), 400
        
        # 플러그인 ID 형식 검증 (영문 소문자, 언더스코어만 허용)
        import re
        if not re.match(r'^[a-z_]+$', data['name']):
            return jsonify({
                'success': False,
                'error': '플러그인 ID는 영문 소문자와 언더스코어만 사용 가능합니다.'
            }), 400
        
        # 버전 형식 검증
        if not re.match(r'^\d+\.\d+\.\d+$', data['version']):
            return jsonify({
                'success': False,
                'error': '버전은 x.y.z 형식이어야 합니다.'
            }), 400
        
        # UI 스키마 검증
        ui_schema = data.get('ui_schema', {})
        if not isinstance(ui_schema, dict):
            return jsonify({
                'success': False,
                'error': 'UI 스키마가 올바르지 않습니다.'
            }), 400
        
        # 플러그인 데이터 구성
        plugin_data = {
            'name': data['name'],
            'display_name': data['display_name'],
            'description': data['description'],
            'version': data['version'],
            'author': data['author'],
            'category': data['category'],
            'tags': data.get('tags', []),
            'icon': data.get('icon', ''),
            'file_path': data['file_path'],
            'ui_schema': ui_schema,
            'is_active': True,
            'is_installed': False,
            'download_count': 0,
            'rating': 0.0,
            'review_count': 0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # 실제 DB 연동 시에는 여기서 Plugin 모델에 저장
        # 현재는 임시로 성공 응답만 반환
        logger.info(f"새 플러그인 등록 요청: {plugin_data['name']}")
        
        return jsonify({
            'success': True,
            'message': '플러그인이 성공적으로 등록되었습니다.',
            'data': {
                'plugin_id': f'plugin_{len(str(hash(data["name"])))}',
                'name': plugin_data['name'],
                'display_name': plugin_data['display_name']
            }
        })
        
    except Exception as e:
        logger.error(f"플러그인 등록 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '플러그인 등록 중 오류가 발생했습니다.',
            'details': str(e)
        }), 500

@admin_plugin_registration_bp.route('/api/admin/plugin/validate', methods=['POST'])
@cross_origin()
def validate_plugin():
    """플러그인 데이터 검증 API"""
    try:
        data = request.get_json()
        
        validation_errors = []
        
        # 플러그인 ID 중복 검사 (실제로는 DB에서 확인)
        if data.get('name'):
            # 임시로 더미 데이터와 비교
            existing_plugins = ['ai_schedule_optimizer', 'review_auto_summary', 'qsc_auto_analyzer']
            if data['name'] in existing_plugins:
                validation_errors.append('이미 존재하는 플러그인 ID입니다.')
        
        # 버전 형식 검증
        import re
        if data.get('version') and not re.match(r'^\d+\.\d+\.\d+$', data['version']):
            validation_errors.append('버전은 x.y.z 형식이어야 합니다.')
        
        # 파일 경로 검증
        if data.get('file_path'):
            if not data['file_path'].startswith('/plugins/'):
                validation_errors.append('파일 경로는 /plugins/로 시작해야 합니다.')
        
        return jsonify({
            'success': len(validation_errors) == 0,
            'errors': validation_errors,
            'message': '검증이 완료되었습니다.' if len(validation_errors) == 0 else '검증 오류가 발견되었습니다.'
        })
        
    except Exception as e:
        logger.error(f"플러그인 검증 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '플러그인 검증 중 오류가 발생했습니다.',
            'details': str(e)
        }), 500

@admin_plugin_registration_bp.route('/api/admin/plugin/templates', methods=['GET'])
@cross_origin()
def get_plugin_templates():
    """플러그인 템플릿 목록 조회"""
    try:
        templates = [
            {
                'id': 'ai_plugin',
                'name': 'AI 플러그인 템플릿',
                'description': 'AI/머신러닝 기반 플러그인을 위한 템플릿',
                'category': 'ai',
                'ui_schema': {
                    'menu': {
                        'title': 'AI 분석',
                        'icon': 'brain',
                        'position': 1
                    },
                    'dashboard': {
                        'type': 'chart',
                        'size': 'large',
                        'component': 'AIAnalysisChart'
                    }
                }
            },
            {
                'id': 'analytics_plugin',
                'name': '분석 플러그인 템플릿',
                'description': '데이터 분석 및 리포팅 플러그인을 위한 템플릿',
                'category': 'analytics',
                'ui_schema': {
                    'menu': {
                        'title': '데이터 분석',
                        'icon': 'bar-chart-3',
                        'position': 2
                    },
                    'dashboard': {
                        'type': 'table',
                        'size': 'large',
                        'component': 'AnalyticsTable'
                    }
                }
            },
            {
                'id': 'management_plugin',
                'name': '관리 플러그인 템플릿',
                'description': '업무 관리 및 자동화 플러그인을 위한 템플릿',
                'category': 'management',
                'ui_schema': {
                    'menu': {
                        'title': '업무 관리',
                        'icon': 'settings',
                        'position': 3
                    },
                    'dashboard': {
                        'type': 'card',
                        'size': 'medium',
                        'component': 'ManagementCard'
                    }
                }
            }
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'templates': templates
            }
        })
        
    except Exception as e:
        logger.error(f"플러그인 템플릿 조회 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '플러그인 템플릿 조회 중 오류가 발생했습니다.',
            'details': str(e)
        }), 500 