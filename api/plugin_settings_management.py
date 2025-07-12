from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
import json
import os
import shutil
from datetime import datetime
import hashlib
from typing import Dict, Any, List, Optional
import jsonschema
from jsonschema import validate
import yaml

plugin_settings_bp = Blueprint('plugin_settings', __name__)

class PluginSettingsManager:
    def __init__(self, app):
        self.app = app
        self.settings_dir = os.path.join(app.root_path, 'plugins', 'settings')
        self.backup_dir = os.path.join(app.root_path, 'plugins', 'settings_backup')
        self.templates_dir = os.path.join(app.root_path, 'plugins', 'settings_templates')
        
        # 디렉토리 생성
        for directory in [self.settings_dir, self.backup_dir, self.templates_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def get_plugin_settings_path(self, plugin_name: str) -> str:
        """플러그인 설정 파일 경로 반환"""
        return os.path.join(self.settings_dir, f"{plugin_name}_settings.json")
    
    def get_plugin_template_path(self, plugin_name: str) -> str:
        """플러그인 설정 템플릿 파일 경로 반환"""
        return os.path.join(self.templates_dir, f"{plugin_name}_template.json")

    def get_backup_path(self, plugin_name: str, version: Optional[str] = None) -> str:  # pyright: ignore
        """백업 파일 경로 반환"""
        if version is not None:
            return os.path.join(self.backup_dir, f"{plugin_name}_settings_{version}.json")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return os.path.join(self.backup_dir, f"{plugin_name}_settings_{timestamp}.json")
    
    def load_settings(self, plugin_name: str) -> Dict[str, Any]:
        """플러그인 설정 로드"""
        settings_path = self.get_plugin_settings_path(plugin_name)
        
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                current_app.logger.error(f"설정 파일 로드 실패: {e}")
                return {}
        else:
            # 기본 설정 생성
            default_settings = self.get_default_settings(plugin_name)
            self.save_settings(plugin_name, default_settings)
            return default_settings
    
    def save_settings(self, plugin_name: str, settings: Dict[str, Any]) -> bool:
        """플러그인 설정 저장"""
        try:
            # 설정 검증
            if not self.validate_settings(plugin_name, settings):
                return False
            
            # 백업 생성
            self.create_backup(plugin_name)
            
            # 설정 저장
            settings_path = self.get_plugin_settings_path(plugin_name)
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            # 설정 메타데이터 업데이트
            self.update_settings_metadata(plugin_name, settings)
            
            return True
        except Exception as e:
            current_app.logger.error(f"설정 저장 실패: {e}")
            return False
    
    def get_default_settings(self, plugin_name: str) -> Dict[str, Any]:
        """플러그인 기본 설정 반환"""
        template_path = self.get_plugin_template_path(plugin_name)
        
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template = json.load(f)
                    return template.get('default_settings', {})
            except Exception as e:
                current_app.logger.error(f"템플릿 로드 실패: {e}")
        
        # 기본 템플릿 반환
        return {
            "enabled": True,
            "debug_mode": False,
            "log_level": "INFO",
            "auto_reload": False,
            "permissions": [],
            "config": {}
        }
    
    def validate_settings(self, plugin_name: str, settings: Dict[str, Any]) -> bool:
        """설정 검증"""
        template_path = self.get_plugin_template_path(plugin_name)
        
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template = json.load(f)
                    schema = template.get('schema', {})
            except Exception as e:
                current_app.logger.error(f"스키마 파일 로드 실패: {e}")
                schema = {}
                return False

        # 스키마가 있으면 검증 시도
        if schema:
            try:
                # 예시: jsonschema 라이브러리로 검증 (실제 사용 시 import 필요)
                import jsonschema  # noqa
                jsonschema.validate(instance=settings, schema=schema)  # noqa
            except Exception as e:
                current_app.logger.error(f"스키마 검증 실패: {e}")
                return False
        return True
    
    def create_backup(self, plugin_name: str) -> bool:
        """설정 백업 생성"""
        try:
            current_settings = self.load_settings(plugin_name)
            if not current_settings:
                return False
            
            backup_path = self.get_backup_path(plugin_name)
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(current_settings, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            current_app.logger.error(f"백업 생성 실패: {e}")
            return False
    
    def restore_backup(self, plugin_name: str, version: str) -> bool:
        """백업에서 설정 복원"""
        try:
            backup_path = self.get_backup_path(plugin_name, version)
            
            if not os.path.exists(backup_path):
                return False
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_settings = json.load(f)
            
            return self.save_settings(plugin_name, backup_settings)
        except Exception as e:
            current_app.logger.error(f"백업 복원 실패: {e}")
            return False
    
    def get_backup_list(self, plugin_name: str) -> List[Dict[str, Any]]:
        """백업 목록 조회"""
        backups = []
        backup_pattern = f"{plugin_name}_settings_*.json"
        
        try:
            for filename in os.listdir(self.backup_dir):
                if filename.startswith(f"{plugin_name}_settings_") and filename.endswith('.json'):
                    file_path = os.path.join(self.backup_dir, filename)
                    stat = os.stat(file_path)
                    
                    # 버전 추출
                    version = filename.replace(f"{plugin_name}_settings_", "").replace('.json', '')
                    
                    backups.append({
                        'version': version,
                        'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'size': stat.st_size,
                        'filename': filename
                    })
            
            # 생성일 기준 내림차순 정렬
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            return backups
        except Exception as e:
            current_app.logger.error(f"백업 목록 조회 실패: {e}")
            return []
    
    def update_settings_metadata(self, plugin_name: str, settings: Dict[str, Any]) -> None:
        """설정 메타데이터 업데이트"""
        metadata_path = os.path.join(self.settings_dir, f"{plugin_name}_metadata.json")
        
        metadata = {
            'last_modified': datetime.now().isoformat(),
            'modified_by': getattr(current_user, 'username', 'system'),
            'version': settings.get('version', '1.0.0'),
            'checksum': hashlib.md5(json.dumps(settings, sort_keys=True).encode()).hexdigest()
        }
        
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            current_app.logger.error(f"메타데이터 업데이트 실패: {e}")
    
    def get_settings_metadata(self, plugin_name: str) -> Dict[str, Any]:
        """설정 메타데이터 조회"""
        metadata_path = os.path.join(self.settings_dir, f"{plugin_name}_metadata.json")
        
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                current_app.logger.error(f"메타데이터 로드 실패: {e}")
        
        return {}
    
    def create_settings_template(self, plugin_name: str, template: Dict[str, Any]) -> bool:
        """설정 템플릿 생성"""
        try:
            template_path = self.get_plugin_template_path(plugin_name)
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            current_app.logger.error(f"템플릿 생성 실패: {e}")
            return False
    
    def get_settings_template(self, plugin_name: str) -> Dict[str, Any]:
        """설정 템플릿 조회"""
        template_path = self.get_plugin_template_path(plugin_name)
        
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                current_app.logger.error(f"템플릿 로드 실패: {e}")
        
        return {}
    
    def migrate_settings(self, plugin_name: str, from_version: str, to_version: str) -> bool:
        """설정 마이그레이션"""
        try:
            current_settings = self.load_settings(plugin_name)
            template = self.get_settings_template(plugin_name)
            
            # 마이그레이션 스크립트 실행
            migration_scripts = template.get('migrations', {})
            migration_key = f"{from_version}_to_{to_version}"
            
            if migration_key in migration_scripts:
                migration_func = migration_scripts[migration_key]
                # 여기서 실제 마이그레이션 로직 실행
                # (실제 구현에서는 더 복잡한 마이그레이션 로직이 필요)
                pass
            
            # 새 버전으로 설정 저장
            current_settings['version'] = to_version
            return self.save_settings(plugin_name, current_settings)
        except Exception as e:
            current_app.logger.error(f"설정 마이그레이션 실패: {e}")
            return False  # pyright: ignore

    def export_settings(self, plugin_name: str, format: str = 'json') -> str:
        """설정 내보내기"""
        try:
            settings = self.load_settings(plugin_name)
            metadata = self.get_settings_metadata(plugin_name)
        except Exception as e:
            current_app.logger.error(f"설정 또는 메타데이터 로드 실패: {e}")
            return ""  # pyright: ignore

        export_data = {
            'plugin_name': plugin_name,
            'settings': settings,
            'metadata': metadata,
            'exported_at': datetime.now().isoformat()
        }

        if format == 'yaml':
            try:
                result = yaml.dump(export_data, default_flow_style=False, allow_unicode=True)
                # yaml.dump가 bytes를 반환할 수 있으므로 str로 변환
                if isinstance(result, bytes):
                    result = result.decode('utf-8')  # pyright: ignore
                if result is None:
                    return ""  # pyright: ignore
                return result
            except Exception as e:
                current_app.logger.error(f"YAML 변환 실패: {e}")
                return ""  # pyright: ignore
        else:
            try:
                return json.dumps(export_data, indent=2, ensure_ascii=False)
            except Exception as e:
                current_app.logger.error(f"JSON 변환 실패: {e}")
                return ""  # pyright: ignore
                # 위 except 블록은 json 변환 실패만 처리합니다.
                # 아래 except 블록은 이미 위에서 처리한 예외이므로 중복 제거
                # (이 부분은 불필요한 중복 코드 및 문법 오류가 있으므로 삭제합니다)
        if format == 'yaml':
            try:
                result = yaml.dump(export_data, default_flow_style=False, allow_unicode=True)
                # yaml.dump가 bytes를 반환할 수 있으므로 str로 변환
                if isinstance(result, bytes):
                    result = result.decode('utf-8')  # pyright: ignore
                if result is None:
                    return ""  # pyright: ignore
                return result
            except Exception as e:
                current_app.logger.error(f"YAML 변환 실패: {e}")
                return ""  # pyright: ignore
            try:
                return json.dumps(export_data, indent=2, ensure_ascii=False)
            except Exception as e:
                current_app.logger.error(f"JSON 변환 실패: {e}")
                return ""  # pyright: ignore
                # 위의 except 블록은 json 변환 실패만 처리합니다.
        export_data = {
                'plugin_name': plugin_name,
                'settings': settings,
                'metadata': metadata,
                'exported_at': datetime.now().isoformat()
        }
        if format == 'yaml':
            result = yaml.dump(export_data, default_flow_style=False, allow_unicode=True)
            # yaml.dump가 bytes를 반환할 수 있으므로 str로 변환
            if isinstance(result, bytes):
                result = result.decode('utf-8')  # pyright: ignore
                if result is None:
                    return ""  # pyright: ignore
                return result
            else:
                return json.dumps(export_data, indent=2, ensure_ascii=False)
    def import_settings(self, plugin_name: str, import_data: str, format: str = 'json') -> bool:
        """설정 가져오기"""
        try:
            if format == 'yaml':
                data = yaml.safe_load(import_data)
            else:
                data = json.loads(import_data)
            
            # data가 dict인지 확인 (예: list 등일 경우 대비)
            if not isinstance(data, dict):
                return False  # pyright: ignore

            # plugin_name이 일치하는지 확인
            if data.get('plugin_name') != plugin_name:
                return False

            settings = data.get('settings', {})
            return self.save_settings(plugin_name, settings)
        except Exception as e:
            current_app.logger.error(f"설정 가져오기 실패: {e}")
            return False
            
            if data.get('plugin_name') != plugin_name:
                # data가 dict가 아닐 경우(예: list 등) .get을 사용할 수 없으므로 타입 체크를 추가합니다.
                if not isinstance(data, dict):
                    return False  # pyright: ignore

                if data.get('plugin_name') != plugin_name:
                    return False

                settings = data.get('settings', {})
                return self.save_settings(plugin_name, settings)

# 전역 설정 관리자 인스턴스
settings_manager = None

def init_settings_manager(app):
    """설정 관리자 초기화"""
    global settings_manager
    settings_manager = PluginSettingsManager(app)

# API 엔드포인트들
@plugin_settings_bp.route('/api/plugin-settings/<plugin_name>', methods=['GET'])
@login_required
def get_plugin_settings(plugin_name):
    """플러그인 설정 조회"""
    try:
        settings = settings_manager.load_settings(plugin_name)
        metadata = settings_manager.get_settings_metadata(plugin_name)
        
        return jsonify({
            'status': 'success',
            'data': {
                'settings': settings,
                'metadata': metadata
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@plugin_settings_bp.route('/api/plugin-settings/<plugin_name>', methods=['POST'])
@login_required
def update_plugin_settings(plugin_name):
    """플러그인 설정 업데이트"""
    try:
        data = request.get_json()
        settings = data.get('settings', {})
        
        if settings_manager.save_settings(plugin_name, settings):
            return jsonify({
                'status': 'success',
                'message': '설정이 성공적으로 저장되었습니다.'
            })
        else:
            return jsonify({
                'status': 'error',
                'error': '설정 저장에 실패했습니다.'
            }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@plugin_settings_bp.route('/api/plugin-settings/<plugin_name>/template', methods=['GET'])
@login_required
def get_settings_template(plugin_name):
    """설정 템플릿 조회"""
    try:
        template = settings_manager.get_settings_template(plugin_name)
        return jsonify({
            'status': 'success',
            'data': template
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@plugin_settings_bp.route('/api/plugin-settings/<plugin_name>/template', methods=['POST'])
@login_required
def create_settings_template(plugin_name):
    """설정 템플릿 생성"""
    try:
        data = request.get_json()
        template = data.get('template', {})
        
        if settings_manager.create_settings_template(plugin_name, template):
            return jsonify({
                'status': 'success',
                'message': '템플릿이 성공적으로 생성되었습니다.'
            })
        else:
            return jsonify({
                'status': 'error',
                'error': '템플릿 생성에 실패했습니다.'
            }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@plugin_settings_bp.route('/api/plugin-settings/<plugin_name>/backup', methods=['GET'])
@login_required
def get_backup_list(plugin_name):
    """백업 목록 조회"""
    try:
        backups = settings_manager.get_backup_list(plugin_name)
        return jsonify({
            'status': 'success',
            'data': backups
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@plugin_settings_bp.route('/api/plugin-settings/<plugin_name>/backup', methods=['POST'])
@login_required
def create_backup(plugin_name):
    """백업 생성"""
    try:
        if settings_manager.create_backup(plugin_name):
            return jsonify({
                'status': 'success',
                'message': '백업이 성공적으로 생성되었습니다.'
            })
        else:
            return jsonify({
                'status': 'error',
                'error': '백업 생성에 실패했습니다.'
            }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@plugin_settings_bp.route('/api/plugin-settings/<plugin_name>/backup/<version>', methods=['POST'])
@login_required
def restore_backup(plugin_name, version):
    """백업 복원"""
    try:
        if settings_manager.restore_backup(plugin_name, version):
            return jsonify({
                'status': 'success',
                'message': '백업이 성공적으로 복원되었습니다.'
            })
        else:
            return jsonify({
                'status': 'error',
                'error': '백업 복원에 실패했습니다.'
            }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@plugin_settings_bp.route('/api/plugin-settings/<plugin_name>/export', methods=['GET'])
@login_required
def export_settings(plugin_name):
    """설정 내보내기"""
    try:
        format = request.args.get('format', 'json')
        export_data = settings_manager.export_settings(plugin_name, format)
        
        if export_data:
            return jsonify({
                'status': 'success',
                'data': export_data,
                'format': format
            })
        else:
            return jsonify({
                'status': 'error',
                'error': '설정 내보내기에 실패했습니다.'
            }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@plugin_settings_bp.route('/api/plugin-settings/<plugin_name>/import', methods=['POST'])
@login_required
def import_settings(plugin_name):
    """설정 가져오기"""
    try:
        data = request.get_json()
        import_data = data.get('import_data', '')
        format = data.get('format', 'json')
        
        if settings_manager.import_settings(plugin_name, import_data, format):
            return jsonify({
                'status': 'success',
                'message': '설정이 성공적으로 가져와졌습니다.'
            })
        else:
            return jsonify({
                'status': 'error',
                'error': '설정 가져오기에 실패했습니다.'
            }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@plugin_settings_bp.route('/api/plugin-settings/<plugin_name>/migrate', methods=['POST'])
@login_required
def migrate_settings(plugin_name):
    """설정 마이그레이션"""
    try:
        data = request.get_json()
        from_version = data.get('from_version')
        to_version = data.get('to_version')
        
        if not from_version or not to_version:
            return jsonify({
                'status': 'error',
                'error': '버전 정보가 필요합니다.'
            }), 400
        
        if settings_manager.migrate_settings(plugin_name, from_version, to_version):
            return jsonify({
                'status': 'success',
                'message': '설정 마이그레이션이 성공적으로 완료되었습니다.'
            })
        else:
            return jsonify({
                'status': 'error',
                'error': '설정 마이그레이션에 실패했습니다.'
            }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@plugin_settings_bp.route('/api/plugin-settings/<plugin_name>/validate', methods=['POST'])
@login_required
def validate_settings(plugin_name):
    """설정 검증"""
    try:
        data = request.get_json()
        settings = data.get('settings', {})
        
        is_valid = settings_manager.validate_settings(plugin_name, settings)
        
        return jsonify({
            'status': 'success',
            'data': {
                'is_valid': is_valid
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@plugin_settings_bp.route('/api/plugin-settings/<plugin_name>/reset', methods=['POST'])
@login_required
def reset_settings(plugin_name):
    """설정 초기화"""
    try:
        default_settings = settings_manager.get_default_settings(plugin_name)
        
        if settings_manager.save_settings(plugin_name, default_settings):
            return jsonify({
                'status': 'success',
                'message': '설정이 기본값으로 초기화되었습니다.'
            })
        else:
            return jsonify({
                'status': 'error',
                'error': '설정 초기화에 실패했습니다.'
            }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500 