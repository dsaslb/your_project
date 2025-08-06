from flask import Blueprint, request, jsonify, g
from settings.settings_manager import SettingsManager, SettingsConfig, SettingItem
import os
import json
from datetime import datetime

# 설정 관리자 초기화
settings_config = SettingsConfig(
    data_dir="data/settings",
    config_file="config.json",
    env_file=".env",
    backup_dir="backups",
    max_backups=10,
    auto_backup=True,
    validate_on_save=True,
    encrypt_sensitive=True
)

settings_manager = SettingsManager(settings_config)

# Blueprint 생성
settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')

@settings_bp.route('/health', methods=['GET'])
def health_check():
    """설정 시스템 상태 확인"""
    try:
        stats = settings_manager.get_settings_stats()
        return jsonify({
            'status': 'success',
            'message': '설정 시스템이 정상적으로 작동합니다',
            'data': {
                'total_settings': stats['total_settings'],
                'categories': stats['categories'],
                'backups': stats['backups'],
                'changes_today': stats['changes_today']
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'설정 시스템 상태 확인 실패: {str(e)}'
        }), 500

@settings_bp.route('/stats', methods=['GET'])
def get_settings_stats():
    """설정 통계 조회"""
    try:
        stats = settings_manager.get_settings_stats()
        return jsonify({
            'status': 'success',
            'data': stats
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'설정 통계 조회 실패: {str(e)}'
        }), 500

@settings_bp.route('/settings', methods=['GET'])
def get_all_settings():
    """모든 설정 조회"""
    try:
        category = request.args.get('category')
        
        if category:
            settings = settings_manager.get_settings_by_category(category)
            settings_data = []
            for setting in settings:
                setting_dict = {
                    'key': setting.key,
                    'value': '***' if setting.is_sensitive else setting.value,
                    'category': setting.category,
                    'description': setting.description,
                    'data_type': setting.data_type,
                    'is_sensitive': setting.is_sensitive,
                    'is_required': setting.is_required,
                    'default_value': setting.default_value,
                    'validation_rules': setting.validation_rules,
                    'created_at': setting.created_at.isoformat() if setting.created_at else None,
                    'updated_at': setting.updated_at.isoformat() if setting.updated_at else None
                }
                settings_data.append(setting_dict)
        else:
            settings_data = settings_manager.get_all_settings()
        
        return jsonify({
            'status': 'success',
            'data': settings_data
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'설정 조회 실패: {str(e)}'
        }), 500

@settings_bp.route('/settings/<key>', methods=['GET'])
def get_setting(key):
    """특정 설정 조회"""
    try:
        if key not in settings_manager.settings:
            return jsonify({
                'status': 'error',
                'message': f'설정 키를 찾을 수 없습니다: {key}'
            }), 404
        
        setting = settings_manager.settings[key]
        setting_data = {
            'key': setting.key,
            'value': '***' if setting.is_sensitive else setting.value,
            'category': setting.category,
            'description': setting.description,
            'data_type': setting.data_type,
            'is_sensitive': setting.is_sensitive,
            'is_required': setting.is_required,
            'default_value': setting.default_value,
            'validation_rules': setting.validation_rules,
            'created_at': setting.created_at.isoformat() if setting.created_at else None,
            'updated_at': setting.updated_at.isoformat() if setting.updated_at else None
        }
        
        return jsonify({
            'status': 'success',
            'data': setting_data
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'설정 조회 실패: {str(e)}'
        }), 500

@settings_bp.route('/settings/<key>', methods=['PUT'])
def update_setting(key):
    """설정 값 변경"""
    try:
        data = request.get_json()
        
        if not data or 'value' not in data:
            return jsonify({
                'status': 'error',
                'message': 'value 필드가 필요합니다'
            }), 400
        
        value = data['value']
        changed_by = data.get('changed_by', 'system')
        change_reason = data.get('change_reason', '')
        
        success = settings_manager.set_setting(key, value, changed_by, change_reason)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'설정 {key}이(가) 성공적으로 업데이트되었습니다',
                'data': {
                    'key': key,
                    'value': '***' if settings_manager.settings[key].is_sensitive else value
                }
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': f'설정 {key} 업데이트 실패'
            }), 500
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'설정 업데이트 실패: {str(e)}'
        }), 500

@settings_bp.route('/settings', methods=['POST'])
def create_setting():
    """새 설정 생성"""
    try:
        data = request.get_json()
        
        required_fields = ['key', 'value', 'category', 'description', 'data_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'{field} 필드가 필요합니다'
                }), 400
        
        key = data['key']
        value = data['value']
        category = data['category']
        description = data['description']
        data_type = data['data_type']
        is_sensitive = data.get('is_sensitive', False)
        is_required = data.get('is_required', False)
        default_value = data.get('default_value')
        validation_rules = data.get('validation_rules')
        
        setting_key = settings_manager.create_setting(
            key=key,
            value=value,
            category=category,
            description=description,
            data_type=data_type,
            is_sensitive=is_sensitive,
            is_required=is_required,
            default_value=default_value,
            validation_rules=validation_rules
        )
        
        return jsonify({
            'status': 'success',
            'message': f'설정 {key}이(가) 성공적으로 생성되었습니다',
            'data': {
                'key': setting_key
            }
        }), 201
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'설정 생성 실패: {str(e)}'
        }), 500

@settings_bp.route('/settings/<key>/validate', methods=['POST'])
def validate_setting(key):
    """설정 값 검증"""
    try:
        data = request.get_json()
        
        if not data or 'value' not in data:
            return jsonify({
                'status': 'error',
                'message': 'value 필드가 필요합니다'
            }), 400
        
        value = data['value']
        
        if key not in settings_manager.settings:
            return jsonify({
                'status': 'error',
                'message': f'설정 키를 찾을 수 없습니다: {key}'
            }), 404
        
        setting = settings_manager.settings[key]
        validation_result = settings_manager.validate_setting_value(
            key, value, setting.data_type, setting.validation_rules
        )
        
        return jsonify({
            'status': 'success',
            'data': validation_result
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'설정 검증 실패: {str(e)}'
        }), 500

@settings_bp.route('/categories', methods=['GET'])
def get_categories():
    """설정 카테고리 조회"""
    try:
        categories = {}
        for category_name in set([s.category for s in settings_manager.settings.values()]):
            settings = settings_manager.get_settings_by_category(category_name)
            categories[category_name] = {
                'name': category_name,
                'description': f'{category_name} 설정',
                'icon': 'settings',
                'settings_count': len(settings),
                'sensitive_count': len([s for s in settings if s.is_sensitive]),
                'required_count': len([s for s in settings if s.is_required])
            }
        
        return jsonify({
            'status': 'success',
            'data': list(categories.values())
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'카테고리 조회 실패: {str(e)}'
        }), 500

@settings_bp.route('/changes', methods=['GET'])
def get_changes():
    """설정 변경 이력 조회"""
    try:
        limit = request.args.get('limit', 50, type=int)
        category = request.args.get('category')
        
        changes = settings_manager.get_recent_changes(limit)
        
        if category:
            changes = [c for c in changes if c.category == category]
        
        changes_data = []
        for change in changes:
            change_dict = {
                'change_id': change.change_id,
                'setting_key': change.setting_key,
                'old_value': change.old_value,
                'new_value': change.new_value,
                'changed_by': change.changed_by,
                'change_reason': change.change_reason,
                'timestamp': change.timestamp.isoformat(),
                'category': change.category
            }
            changes_data.append(change_dict)
        
        return jsonify({
            'status': 'success',
            'data': changes_data
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'변경 이력 조회 실패: {str(e)}'
        }), 500

@settings_bp.route('/export', methods=['GET'])
def export_settings():
    """설정 내보내기"""
    try:
        format_type = request.args.get('format', 'json')
        
        if format_type not in ['json', 'yaml']:
            return jsonify({
                'status': 'error',
                'message': '지원하지 않는 형식입니다. json 또는 yaml을 사용하세요'
            }), 400
        
        exported_data = settings_manager.export_settings(format_type)
        
        return jsonify({
            'status': 'success',
            'data': {
                'format': format_type,
                'content': exported_data,
                'exported_at': datetime.utcnow().isoformat()
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'설정 내보내기 실패: {str(e)}'
        }), 500

@settings_bp.route('/import', methods=['POST'])
def import_settings():
    """설정 가져오기"""
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({
                'status': 'error',
                'message': 'content 필드가 필요합니다'
            }), 400
        
        content = data['content']
        format_type = data.get('format', 'json')
        changed_by = data.get('changed_by', 'system')
        
        if format_type not in ['json', 'yaml']:
            return jsonify({
                'status': 'error',
                'message': '지원하지 않는 형식입니다. json 또는 yaml을 사용하세요'
            }), 400
        
        success = settings_manager.import_settings(content, format_type, changed_by)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': '설정이 성공적으로 가져와졌습니다',
                'data': {
                    'format': format_type,
                    'imported_at': datetime.utcnow().isoformat()
                }
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': '설정 가져오기 실패'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'설정 가져오기 실패: {str(e)}'
        }), 500

@settings_bp.route('/env-file', methods=['GET'])
def generate_env_file():
    """환경 변수 파일 생성"""
    try:
        env_content = settings_manager.generate_env_file()
        
        return jsonify({
            'status': 'success',
            'data': {
                'content': env_content,
                'generated_at': datetime.utcnow().isoformat()
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'환경 변수 파일 생성 실패: {str(e)}'
        }), 500

@settings_bp.route('/backup', methods=['POST'])
def create_backup():
    """설정 백업 생성"""
    try:
        data = request.get_json() or {}
        
        name = data.get('name', f'백업_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}')
        description = data.get('description', '')
        created_by = data.get('created_by', 'system')
        
        backup_id = settings_manager.create_backup(name, description, created_by)
        
        return jsonify({
            'status': 'success',
            'message': f'백업 {name}이(가) 성공적으로 생성되었습니다',
            'data': {
                'backup_id': backup_id,
                'name': name,
                'created_at': datetime.utcnow().isoformat()
            }
        }), 201
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'백업 생성 실패: {str(e)}'
        }), 500

@settings_bp.route('/backup/<backup_id>/restore', methods=['POST'])
def restore_backup(backup_id):
    """설정 백업 복원"""
    try:
        data = request.get_json() or {}
        restore_sensitive = data.get('restore_sensitive', False)
        
        success = settings_manager.restore_backup(backup_id, restore_sensitive)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'백업 {backup_id}이(가) 성공적으로 복원되었습니다',
                'data': {
                    'backup_id': backup_id,
                    'restored_at': datetime.utcnow().isoformat(),
                    'restore_sensitive': restore_sensitive
                }
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': f'백업 {backup_id} 복원 실패'
            }), 500
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'백업 복원 실패: {str(e)}'
        }), 500

@settings_bp.route('/backup', methods=['GET'])
def get_backups():
    """백업 목록 조회"""
    try:
        backups_data = []
        for backup in settings_manager.backups:
            backup_dict = {
                'backup_id': backup.backup_id,
                'name': backup.name,
                'description': backup.description,
                'created_by': backup.created_by,
                'created_at': backup.created_at.isoformat(),
                'file_path': backup.file_path,
                'file_size': backup.file_size,
                'checksum': backup.checksum
            }
            backups_data.append(backup_dict)
        
        # 최신 순으로 정렬
        backups_data.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'data': backups_data
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'백업 목록 조회 실패: {str(e)}'
        }), 500 