"""
플러그인 관리 API
플러그인의 등록, 활성화, 비활성화, 설정 관리를 위한 API
"""

from flask import Blueprint, jsonify, request, current_app
from datetime import datetime, timedelta
import os
import json
import logging
from typing import Dict, List, Optional, Any
import zipfile
import tempfile
import shutil

from core.backend.plugin_interface import plugin_registry
from core.backend.plugin_loader import plugin_loader

# 로깅 설정
logger = logging.getLogger(__name__)

plugin_management_bp = Blueprint('plugin_management', __name__, url_prefix='/api')

# 플러그인 로그 저장소
plugin_logs = {}

# 플러그인 성능 메트릭 저장소
plugin_metrics = {}

# 플러그인 설치 이력
plugin_installation_history = []

@plugin_management_bp.route('/plugins', methods=['GET'])
def get_plugins():
    """플러그인 목록 조회 (개선된 버전)"""
    try:
        plugins = []
        filters = request.args.to_dict()
        
        for plugin_id, plugin in plugin_registry.get_all_plugins().items():
            metadata = plugin.get_metadata()
            health_status = plugin.get_health_status()
            
            # 필터링 적용
            if filters.get('category') and metadata.category != filters['category']:
                continue
            if filters.get('enabled') and str(metadata.enabled).lower() != filters['enabled'].lower():
                continue
            if filters.get('status') and health_status.get('status') != filters['status']:
                continue
            
            # 성능 메트릭 추가
            metrics = plugin_metrics.get(plugin_id, {})
            
            plugin_info = {
                'id': plugin_id,
                'name': metadata.name,
                'version': metadata.version,
                'description': metadata.description,
                'author': metadata.author,
                'category': metadata.category,
                'enabled': metadata.enabled,
                'dependencies': [dep.plugin_id for dep in plugin.get_dependencies()],
                'permissions': metadata.permissions,
                'routes_count': len(plugin.get_routes()),
                'menus_count': len(plugin.get_menus()),
                'health_status': health_status,
                'performance_metrics': {
                    'cpu_usage': metrics.get('cpu_usage', 0),
                    'memory_usage': metrics.get('memory_usage', 0),
                    'response_time': metrics.get('response_time', 0),
                    'error_rate': metrics.get('error_rate', 0),
                    'last_updated': metrics.get('last_updated')
                },
                'installation_info': {
                    'installed_at': metadata.created_at.isoformat() if metadata.created_at else None,
                    'last_updated': metadata.updated_at.isoformat() if metadata.updated_at else None,
                    'update_count': len(plugin_installation_history) if plugin_installation_history else 0
                },
                'created_at': metadata.created_at.isoformat() if metadata.created_at else None,
                'updated_at': metadata.updated_at.isoformat() if metadata.updated_at else None
            }
            plugins.append(plugin_info)
        
        # 정렬 적용
        sort_by = filters.get('sort_by', 'name')
        sort_order = filters.get('sort_order', 'asc')
        
        if sort_by in ['name', 'version', 'category', 'enabled']:
            plugins.sort(key=lambda x: x[sort_by], reverse=(sort_order == 'desc'))
        
        # 페이지네이션 적용
        page = int(filters.get('page', 1))
        per_page = int(filters.get('per_page', 10))
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        paginated_plugins = plugins[start_idx:end_idx]
        
        return jsonify({
            'success': True,
            'plugins': paginated_plugins,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_count': len(plugins),
                'total_pages': (len(plugins) + per_page - 1) // per_page
            },
            'filters': filters
        })
        
    except Exception as e:
        logger.error(f"플러그인 목록 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plugin_management_bp.route('/plugins/register', methods=['POST'])
def register_plugin():
    """플러그인 등록 (새로운 기능)"""
    try:
        # 파일 업로드 확인
        if 'plugin_file' not in request.files:
            return jsonify({
                'success': False,
                'error': '플러그인 파일이 필요합니다'
            }), 400
        
        file = request.files['plugin_file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '파일이 선택되지 않았습니다'
            }), 400
        
        # 메타데이터 확인
        metadata = request.form.get('metadata')
        if not metadata:
            return jsonify({
                'success': False,
                'error': '플러그인 메타데이터가 필요합니다'
            }), 400
        
        try:
            metadata = json.loads(metadata)
        except json.JSONDecodeError:
            return jsonify({
                'success': False,
                'error': '유효하지 않은 메타데이터 형식입니다'
            }), 400
        
        # 임시 디렉토리에 파일 저장
        temp_dir = tempfile.mkdtemp()
        filename = secure_filename(file.filename)
        file_path = os.path.join(temp_dir, filename)
        file.save(file_path)
        
        # ZIP 파일 압축 해제 및 검증
        extract_dir = os.path.join(temp_dir, 'extracted')
        os.makedirs(extract_dir, exist_ok=True)
        
        with zipfile.ZipFile(file_path, 'r') as zipf:
            zipf.extractall(extract_dir)
        
        # 플러그인 검증
        validation_result = validate_plugin_structure(extract_dir, metadata)
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'error': f'플러그인 검증 실패: {validation_result["error"]}'
            }), 400
        
        # 플러그인 등록
        plugin_id = metadata.get('plugin_id')
        if not plugin_id:
            return jsonify({
                'success': False,
                'error': '플러그인 ID가 필요합니다'
            }), 400
        
        # 기존 플러그인 확인
        if plugin_registry.get_plugin(plugin_id):
            return jsonify({
                'success': False,
                'error': '이미 존재하는 플러그인 ID입니다'
            }), 409
        
        # 플러그인 디렉토리로 이동
        plugin_dir = os.path.join(current_app.config.get('PLUGIN_DIR', 'plugins'), plugin_id)
        if os.path.exists(plugin_dir):
            shutil.rmtree(plugin_dir)
        shutil.move(extract_dir, plugin_dir)
        
        # 설정 파일 생성
        config = {
            'plugin_id': plugin_id,
            'metadata': metadata,
            'enabled': False,
            'installed_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'version': metadata.get('version', '1.0.0')
        }
        
        config_path = os.path.join(plugin_dir, 'config.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        # 설치 이력 기록
        plugin_installation_history.append({
            'plugin_id': plugin_id,
            'action': 'register',
            'version': metadata.get('version', '1.0.0'),
            'timestamp': datetime.utcnow().isoformat(),
            'metadata': metadata
        })
        
        # 로그 기록
        log_plugin_action(plugin_id, 'register', f'플러그인 등록: {metadata.get("name")}')
        
        # 임시 파일 정리
        shutil.rmtree(temp_dir)
        
        return jsonify({
            'success': True,
            'message': f'플러그인 {plugin_id}이 성공적으로 등록되었습니다',
            'plugin_id': plugin_id,
            'metadata': metadata
        })
        
    except Exception as e:
        logger.error(f"플러그인 등록 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plugin_management_bp.route('/plugins/<plugin_id>', methods=['GET'])
def get_plugin_detail(plugin_id: str):
    """플러그인 상세 정보 조회"""
    try:
        plugin = plugin_registry.get_plugin(plugin_id)
        if not plugin:
            return jsonify({
                'success': False,
                'error': '플러그인을 찾을 수 없습니다'
            }), 404
        
        metadata = plugin.get_metadata()
        health_status = plugin.get_health_status()
        api_docs = plugin.get_api_documentation()
        
        plugin_detail = {
            'id': plugin_id,
            'name': metadata.name,
            'version': metadata.version,
            'description': metadata.description,
            'author': metadata.author,
            'category': metadata.category,
            'enabled': metadata.enabled,
            'dependencies': [
                {
                    'plugin_id': dep.plugin_id,
                    'version': dep.version,
                    'required': dep.required,
                    'description': dep.description
                }
                for dep in plugin.get_dependencies()
            ],
            'permissions': metadata.permissions,
            'routes': [
                {
                    'path': route.path,
                    'methods': route.methods,
                    'description': route.description,
                    'auth_required': route.auth_required,
                    'roles': route.roles,
                    'version': route.version
                }
                for route in plugin.get_routes()
            ],
            'menus': [
                {
                    'title': menu.title,
                    'path': menu.path,
                    'icon': menu.icon,
                    'parent': menu.parent,
                    'roles': menu.roles,
                    'order': menu.order,
                    'badge': menu.badge,
                    'visible': menu.visible
                }
                for menu in plugin.get_menus()
            ],
            'config_schema': [
                {
                    'key': config.key,
                    'type': config.type,
                    'default': config.default,
                    'required': config.required,
                    'description': config.description,
                    'options': config.options,
                    'validation': config.validation
                }
                for config in plugin.get_config_schema()
            ],
            'health_status': health_status,
            'api_documentation': api_docs,
            'created_at': metadata.created_at.isoformat() if metadata.created_at else None,
            'updated_at': metadata.updated_at.isoformat() if metadata.updated_at else None
        }
        
        return jsonify({
            'success': True,
            'plugin': plugin_detail
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plugin_management_bp.route('/plugins/<plugin_id>/enable', methods=['POST'])
def enable_plugin(plugin_id: str):
    """플러그인 활성화"""
    try:
        plugin = plugin_registry.get_plugin(plugin_id)
        if not plugin:
            return jsonify({
                'success': False,
                'error': '플러그인을 찾을 수 없습니다'
            }), 404
        
        # 플러그인 활성화
        if plugin.on_enable():
            # 설정 파일에서 활성화 상태 업데이트
            config = plugin_loader.get_plugin_config(plugin_id)
            if config:
                config['enabled'] = True
                config['updated_at'] = datetime.utcnow().isoformat()
                plugin_loader.save_plugin_config(plugin_id, config)
            
            return jsonify({
                'success': True,
                'message': f'플러그인 {plugin_id}이 활성화되었습니다'
            })
        else:
            return jsonify({
                'success': False,
                'error': '플러그인 활성화에 실패했습니다'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plugin_management_bp.route('/plugins/<plugin_id>/disable', methods=['POST'])
def disable_plugin(plugin_id: str):
    """플러그인 비활성화"""
    try:
        plugin = plugin_registry.get_plugin(plugin_id)
        if not plugin:
            return jsonify({
                'success': False,
                'error': '플러그인을 찾을 수 없습니다'
            }), 404
        
        # 플러그인 비활성화
        if plugin.on_disable():
            # 설정 파일에서 비활성화 상태 업데이트
            config = plugin_loader.get_plugin_config(plugin_id)
            if config:
                config['enabled'] = False
                config['updated_at'] = datetime.utcnow().isoformat()
                plugin_loader.save_plugin_config(plugin_id, config)
            
            return jsonify({
                'success': True,
                'message': f'플러그인 {plugin_id}이 비활성화되었습니다'
            })
        else:
            return jsonify({
                'success': False,
                'error': '플러그인 비활성화에 실패했습니다'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plugin_management_bp.route('/plugins/<plugin_id>/reload', methods=['POST'])
def reload_plugin(plugin_id: str):
    """플러그인 재로드"""
    try:
        # 플러그인 재로드
        reloaded_plugin = plugin_loader.reload_plugin(plugin_id)
        
        if reloaded_plugin:
            return jsonify({
                'success': True,
                'message': f'플러그인 {plugin_id}이 재로드되었습니다'
            })
        else:
            return jsonify({
                'success': False,
                'error': '플러그인 재로드에 실패했습니다'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plugin_management_bp.route('/plugins/<plugin_id>/config', methods=['GET'])
def get_plugin_config(plugin_id: str):
    """플러그인 설정 조회"""
    try:
        config = plugin_loader.get_plugin_config(plugin_id)
        
        if not config:
            return jsonify({
                'success': False,
                'error': '플러그인 설정을 찾을 수 없습니다'
            }), 404
        
        return jsonify({
            'success': True,
            'config': config
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plugin_management_bp.route('/plugins/<plugin_id>/config', methods=['PUT'])
def update_plugin_config(plugin_id: str):
    """플러그인 설정 업데이트"""
    try:
        plugin = plugin_registry.get_plugin(plugin_id)
        if not plugin:
            return jsonify({
                'success': False,
                'error': '플러그인을 찾을 수 없습니다'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '설정 데이터가 필요합니다'
            }), 400
        
        # 기존 설정 가져오기
        old_config = plugin_loader.get_plugin_config(plugin_id) or {}
        
        # 새 설정으로 업데이트
        new_config = {**old_config, **data}
        new_config['updated_at'] = datetime.utcnow().isoformat()
        
        # 설정 유효성 검사
        if not plugin.validate_config(new_config.get('config', {})):
            return jsonify({
                'success': False,
                'error': '설정이 유효하지 않습니다'
            }), 400
        
        # 설정 저장
        if plugin_loader.save_plugin_config(plugin_id, new_config):
            # 플러그인에 설정 변경 알림
            plugin.on_config_change(
                old_config.get('config', {}),
                new_config.get('config', {})
            )
            
            return jsonify({
                'success': True,
                'message': '플러그인 설정이 업데이트되었습니다',
                'config': new_config
            })
        else:
            return jsonify({
                'success': False,
                'error': '설정 저장에 실패했습니다'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plugin_management_bp.route('/plugins/scan', methods=['POST'])
def scan_plugins():
    """플러그인 스캔 및 로드"""
    try:
        # 플러그인 스캔
        discovered_plugins = plugin_loader.scan_plugins()
        
        # 플러그인 로드
        loaded_plugins = plugin_loader.load_all_plugins()
        
        return jsonify({
            'success': True,
            'message': f'{len(loaded_plugins)}개 플러그인이 로드되었습니다',
            'discovered_count': len(discovered_plugins),
            'loaded_count': len(loaded_plugins),
            'loaded_plugins': list(loaded_plugins.keys())
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plugin_management_bp.route('/plugins/status', methods=['GET'])
def get_plugins_status():
    """플러그인 전체 상태 조회"""
    try:
        status = {
            'total_plugins': len(plugin_registry.get_all_plugins()),
            'enabled_plugins': 0,
            'disabled_plugins': 0,
            'plugins_by_category': {},
            'dependency_order': plugin_registry.get_dependency_order(),
            'health_summary': {
                'healthy': 0,
                'warning': 0,
                'error': 0
            }
        }
        
        # 카테고리별 플러그인 수집
        for plugin_id, plugin in plugin_registry.get_all_plugins().items():
            metadata = plugin.get_metadata()
            health_status = plugin.get_health_status()
            
            # 활성화/비활성화 카운트
            if metadata.enabled:
                status['enabled_plugins'] += 1
            else:
                status['disabled_plugins'] += 1
            
            # 카테고리별 카운트
            category = metadata.category
            if category not in status['plugins_by_category']:
                status['plugins_by_category'][category] = []
            status['plugins_by_category'][category].append({
                'id': plugin_id,
                'name': metadata.name,
                'enabled': metadata.enabled,
                'health': health_status
            })
            
            # 헬스 상태 카운트
            if health_status.get('initialized', False):
                status['health_summary']['healthy'] += 1
            else:
                status['health_summary']['error'] += 1
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plugin_management_bp.route('/plugins/<plugin_id>/api-docs', methods=['GET'])
def get_plugin_api_docs(plugin_id: str):
    """플러그인 API 문서 조회"""
    try:
        plugin = plugin_registry.get_plugin(plugin_id)
        if not plugin:
            return jsonify({
                'success': False,
                'error': '플러그인을 찾을 수 없습니다'
            }), 404
        
        api_docs = plugin.get_api_documentation()
        
        return jsonify({
            'success': True,
            'api_documentation': api_docs
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 

@plugin_management_bp.route('/plugins/<plugin_id>/schema', methods=['GET'])
def get_plugin_schema(plugin_id: str):
    """플러그인 동적 필드/스키마 조회"""
    try:
        plugin = plugin_registry.get_plugin(plugin_id)
        if not plugin:
            return jsonify({'success': False, 'error': '플러그인을 찾을 수 없습니다'}), 404
        schema = [
            {
                'key': config.key,
                'type': config.type,
                'default': config.default,
                'required': config.required,
                'description': config.description,
                'options': config.options,
                'validation': config.validation
            }
            for config in plugin.get_config_schema()
        ]
        return jsonify({'success': True, 'schema': schema})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@plugin_management_bp.route('/plugins/<plugin_id>/schema', methods=['PUT'])
def update_plugin_schema(plugin_id: str):
    """플러그인 동적 필드/스키마 수정"""
    try:
        plugin = plugin_registry.get_plugin(plugin_id)
        if not plugin:
            return jsonify({'success': False, 'error': '플러그인을 찾을 수 없습니다'}), 404
        data = request.get_json()
        if not data or 'schema' not in data:
            return jsonify({'success': False, 'error': '스키마 데이터가 필요합니다'}), 400
        # 기존 설정 가져오기
        config = plugin_loader.get_plugin_config(plugin_id) or {}
        config['config_schema'] = data['schema']
        config['updated_at'] = datetime.utcnow().isoformat()
        # 저장
        if plugin_loader.save_plugin_config(plugin_id, config):
            return jsonify({'success': True, 'message': '스키마가 업데이트되었습니다', 'schema': data['schema']})
        else:
            return jsonify({'success': False, 'error': '스키마 저장에 실패했습니다'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500 

@plugin_management_bp.route('/plugins/market', methods=['GET'])
def get_plugin_market():
    """플러그인 마켓 목록 조회"""
    try:
        # 실제로는 외부 플러그인 저장소에서 가져와야 함
        # 현재는 로컬 플러그인을 마켓 형태로 제공
        market_plugins = []
        
        for plugin_id, plugin in plugin_registry.get_all_plugins().items():
            metadata = plugin.get_metadata()
            health_status = plugin.get_health_status()
            
            market_plugin = {
                'id': plugin_id,
                'name': metadata.name,
                'version': metadata.version,
                'description': metadata.description,
                'author': metadata.author,
                'category': metadata.category,
                'installed': True,
                'installed_version': metadata.version,
                'latest_version': metadata.version,
                'rating': 4.5,  # 더미 데이터
                'downloads': 100,  # 더미 데이터
                'price': 0,  # 무료
                'tags': [metadata.category],
                'screenshots': [],
                'dependencies': [dep.plugin_id for dep in plugin.get_dependencies()],
                'health_status': health_status
            }
            market_plugins.append(market_plugin)
        
        return jsonify({
            'success': True,
            'plugins': market_plugins,
            'total_count': len(market_plugins)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plugin_management_bp.route('/plugins/<plugin_id>/install', methods=['POST'])
def install_plugin(plugin_id: str):
    """플러그인 설치 (개선된 버전)"""
    try:
        data = request.get_json() or {}
        install_options = data.get('options', {})
        
        plugin = plugin_registry.get_plugin(plugin_id)
        if not plugin:
            return jsonify({
                'success': False,
                'error': '플러그인을 찾을 수 없습니다'
            }), 404
        
        # 의존성 검사
        dependencies = plugin.get_dependencies()
        missing_deps = []
        for dep in dependencies:
            if not plugin_registry.get_plugin(dep.plugin_id):
                missing_deps.append(dep.plugin_id)
        
        if missing_deps:
            return jsonify({
                'success': False,
                'error': f'필수 의존성 플러그인이 없습니다: {", ".join(missing_deps)}'
            }), 400
        
        # 버전 호환성 검사
        compatibility_check = check_plugin_compatibility(plugin_id, install_options.get('version'))
        if not compatibility_check['compatible']:
            return jsonify({
                'success': False,
                'error': f'버전 호환성 문제: {compatibility_check["error"]}'
            }), 400
        
        # 플러그인 활성화
        if plugin.on_enable():
            config = plugin_loader.get_plugin_config(plugin_id) or {}
            config['enabled'] = True
            config['installed_at'] = datetime.utcnow().isoformat()
            config['updated_at'] = datetime.utcnow().isoformat()
            config['install_options'] = install_options
            
            if plugin_loader.save_plugin_config(plugin_id, config):
                # 설치 이력 기록
                plugin_installation_history.append({
                    'plugin_id': plugin_id,
                    'action': 'install',
                    'version': config.get('version', '1.0.0'),
                    'timestamp': datetime.utcnow().isoformat(),
                    'options': install_options
                })
                
                # 로그 기록
                log_plugin_action(plugin_id, 'install', f'플러그인 설치 완료')
                
                # 성능 메트릭 초기화
                plugin_metrics[plugin_id] = {
                    'cpu_usage': 0,
                    'memory_usage': 0,
                    'response_time': 0,
                    'error_rate': 0,
                    'last_updated': datetime.utcnow().isoformat()
                }
                
                return jsonify({
                    'success': True,
                    'message': f'플러그인 {plugin_id}이 설치되었습니다',
                    'install_info': {
                        'plugin_id': plugin_id,
                        'version': config.get('version'),
                        'installed_at': config['installed_at'],
                        'dependencies': [dep.plugin_id for dep in dependencies]
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '설정 저장에 실패했습니다'
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': '플러그인 설치에 실패했습니다'
            }), 500
        
    except Exception as e:
        logger.error(f"플러그인 설치 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plugin_management_bp.route('/plugins/<plugin_id>/uninstall', methods=['POST'])
def uninstall_plugin(plugin_id: str):
    """플러그인 제거 (개선된 버전)"""
    try:
        data = request.get_json() or {}
        uninstall_options = data.get('options', {})
        
        plugin = plugin_registry.get_plugin(plugin_id)
        if not plugin:
            return jsonify({
                'success': False,
                'error': '플러그인을 찾을 수 없습니다'
            }), 404
        
        # 의존하는 플러그인 확인
        dependent_plugins = []
        for other_id, other_plugin in plugin_registry.get_all_plugins().items():
            if other_id != plugin_id:
                for dep in other_plugin.get_dependencies():
                    if dep.plugin_id == plugin_id:
                        dependent_plugins.append(other_id)
        
        if dependent_plugins and not uninstall_options.get('force', False):
            return jsonify({
                'success': False,
                'error': f'다른 플러그인이 의존하고 있습니다: {", ".join(dependent_plugins)}. 강제 제거하려면 force=true를 설정하세요.'
            }), 400
        
        # 플러그인 비활성화
        if plugin.on_disable():
            config = plugin_loader.get_plugin_config(plugin_id) or {}
            config['enabled'] = False
            config['uninstalled_at'] = datetime.utcnow().isoformat()
            config['updated_at'] = datetime.utcnow().isoformat()
            config['uninstall_options'] = uninstall_options
            
            if plugin_loader.save_plugin_config(plugin_id, config):
                # 설치 이력 기록
                plugin_installation_history.append({
                    'plugin_id': plugin_id,
                    'action': 'uninstall',
                    'version': config.get('version', '1.0.0'),
                    'timestamp': datetime.utcnow().isoformat(),
                    'options': uninstall_options
                })
                
                # 로그 기록
                log_plugin_action(plugin_id, 'uninstall', f'플러그인 제거 완료')
                
                # 성능 메트릭 제거
                if plugin_id in plugin_metrics:
                    del plugin_metrics[plugin_id]
                
                return jsonify({
                    'success': True,
                    'message': f'플러그인 {plugin_id}이 제거되었습니다',
                    'uninstall_info': {
                        'plugin_id': plugin_id,
                        'uninstalled_at': config['uninstalled_at'],
                        'dependent_plugins': dependent_plugins
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '설정 저장에 실패했습니다'
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': '플러그인 제거에 실패했습니다'
            }), 500
        
    except Exception as e:
        logger.error(f"플러그인 제거 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plugin_management_bp.route('/plugins/<plugin_id>/update', methods=['POST'])
def update_plugin(plugin_id: str):
    """플러그인 업데이트"""
    try:
        data = request.get_json()
        new_version = data.get('version') if data else None
        
        plugin = plugin_registry.get_plugin(plugin_id)
        if not plugin:
            return jsonify({
                'success': False,
                'error': '플러그인을 찾을 수 없습니다'
            }), 404
        
        # 실제로는 새 버전 다운로드 및 설치
        # 현재는 버전 정보만 업데이트
        config = plugin_loader.get_plugin_config(plugin_id) or {}
        old_version = config.get('version', '1.0.0')
        
        if new_version:
            config['version'] = new_version
        config['updated_at'] = datetime.utcnow().isoformat()
        config['update_history'] = config.get('update_history', [])
        config['update_history'].append({
            'from_version': old_version,
            'to_version': new_version or old_version,
            'updated_at': datetime.utcnow().isoformat()
        })
        
        if plugin_loader.save_plugin_config(plugin_id, config):
            return jsonify({
                'success': True,
                'message': f'플러그인 {plugin_id}이 업데이트되었습니다',
                'old_version': old_version,
                'new_version': new_version or old_version
            })
        else:
            return jsonify({
                'success': False,
                'error': '플러그인 업데이트에 실패했습니다'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plugin_management_bp.route('/plugins/<plugin_id>/rollback', methods=['POST'])
def rollback_plugin(plugin_id: str):
    """플러그인 롤백"""
    try:
        data = request.get_json()
        target_version = data.get('version') if data else None
        
        if not target_version:
            return jsonify({
                'success': False,
                'error': '롤백할 버전을 지정해주세요'
            }), 400
        
        plugin = plugin_registry.get_plugin(plugin_id)
        if not plugin:
            return jsonify({
                'success': False,
                'error': '플러그인을 찾을 수 없습니다'
            }), 404
        
        # 실제로는 이전 버전으로 복원
        # 현재는 버전 정보만 변경
        config = plugin_loader.get_plugin_config(plugin_id) or {}
        current_version = config.get('version', '1.0.0')
        
        config['version'] = target_version
        config['updated_at'] = datetime.utcnow().isoformat()
        config['rollback_history'] = config.get('rollback_history', [])
        config['rollback_history'].append({
            'from_version': current_version,
            'to_version': target_version,
            'rolled_back_at': datetime.utcnow().isoformat()
        })
        
        if plugin_loader.save_plugin_config(plugin_id, config):
            return jsonify({
                'success': True,
                'message': f'플러그인 {plugin_id}이 {target_version}으로 롤백되었습니다',
                'from_version': current_version,
                'to_version': target_version
            })
        else:
            return jsonify({
                'success': False,
                'error': '플러그인 롤백에 실패했습니다'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plugin_management_bp.route('/plugins/<plugin_id>/versions', methods=['GET'])
def get_plugin_versions(plugin_id: str):
    """플러그인 버전 히스토리 조회"""
    try:
        config = plugin_loader.get_plugin_config(plugin_id)
        if not config:
            return jsonify({
                'success': False,
                'error': '플러그인을 찾을 수 없습니다'
            }), 404
        
        versions = {
            'current_version': config.get('version', '1.0.0'),
            'update_history': config.get('update_history', []),
            'rollback_history': config.get('rollback_history', []),
            'available_versions': [
                '1.0.0',
                '1.1.0',
                '1.2.0',
                '2.0.0'
            ]  # 더미 데이터
        }
        
        return jsonify({
            'success': True,
            'versions': versions
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 

@plugin_management_bp.route('/plugins/<plugin_id>/logs', methods=['GET'])
def get_plugin_logs(plugin_id: str):
    """플러그인 로그 조회 (새로운 기능)"""
    try:
        logs = plugin_logs.get(plugin_id, [])
        
        # 필터링 적용
        filters = request.args.to_dict()
        filtered_logs = logs
        
        if filters.get('level'):
            filtered_logs = [log for log in filtered_logs if log.get('level') == filters['level']]
        
        if filters.get('action'):
            filtered_logs = [log for log in filtered_logs if log.get('action') == filters['action']]
        
        # 시간 범위 필터링
        if filters.get('start_time'):
            start_time = datetime.fromisoformat(filters['start_time'])
            filtered_logs = [log for log in filtered_logs 
                           if datetime.fromisoformat(log['timestamp']) >= start_time]
        
        if filters.get('end_time'):
            end_time = datetime.fromisoformat(filters['end_time'])
            filtered_logs = [log for log in filtered_logs 
                           if datetime.fromisoformat(log['timestamp']) <= end_time]
        
        # 정렬
        sort_order = filters.get('sort_order', 'desc')
        filtered_logs.sort(key=lambda x: x['timestamp'], reverse=(sort_order == 'desc'))
        
        # 페이지네이션
        page = int(filters.get('page', 1))
        per_page = int(filters.get('per_page', 50))
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        paginated_logs = filtered_logs[start_idx:end_idx]
        
        return jsonify({
            'success': True,
            'logs': paginated_logs,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_count': len(filtered_logs),
                'total_pages': (len(filtered_logs) + per_page - 1) // per_page
            },
            'summary': {
                'total_logs': len(logs),
                'error_count': len([log for log in logs if log.get('level') == 'error']),
                'warning_count': len([log for log in logs if log.get('level') == 'warning']),
                'info_count': len([log for log in logs if log.get('level') == 'info'])
            }
        })
        
    except Exception as e:
        logger.error(f"플러그인 로그 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plugin_management_bp.route('/plugins/<plugin_id>/metrics', methods=['GET'])
def get_plugin_metrics(plugin_id: str):
    """플러그인 성능 메트릭 조회 (새로운 기능)"""
    try:
        metrics = plugin_metrics.get(plugin_id, {})
        
        # 시간 범위 필터링
        filters = request.args.to_dict()
        time_range = filters.get('time_range', '24h')
        
        # 더미 메트릭 데이터 생성 (실제로는 실제 메트릭 수집 시스템과 연동)
        if not metrics:
            metrics = generate_dummy_metrics(plugin_id, time_range)
        
        return jsonify({
            'success': True,
            'metrics': metrics,
            'time_range': time_range,
            'last_updated': metrics.get('last_updated')
        })
        
    except Exception as e:
        logger.error(f"플러그인 메트릭 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plugin_management_bp.route('/plugins/history', methods=['GET'])
def get_installation_history():
    """플러그인 설치 이력 조회 (새로운 기능)"""
    try:
        filters = request.args.to_dict()
        filtered_history = plugin_installation_history
        
        # 필터링 적용
        if filters.get('plugin_id'):
            filtered_history = [h for h in filtered_history if h['plugin_id'] == filters['plugin_id']]
        
        if filters.get('action'):
            filtered_history = [h for h in filtered_history if h['action'] == filters['action']]
        
        # 시간 범위 필터링
        if filters.get('start_time'):
            start_time = datetime.fromisoformat(filters['start_time'])
            filtered_history = [h for h in filtered_history 
                              if datetime.fromisoformat(h['timestamp']) >= start_time]
        
        if filters.get('end_time'):
            end_time = datetime.fromisoformat(filters['end_time'])
            filtered_history = [h for h in filtered_history 
                              if datetime.fromisoformat(h['timestamp']) <= end_time]
        
        # 정렬
        sort_order = filters.get('sort_order', 'desc')
        filtered_history.sort(key=lambda x: x['timestamp'], reverse=(sort_order == 'desc'))
        
        # 페이지네이션
        page = int(filters.get('page', 1))
        per_page = int(filters.get('per_page', 20))
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        paginated_history = filtered_history[start_idx:end_idx]
        
        return jsonify({
            'success': True,
            'history': paginated_history,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_count': len(filtered_history),
                'total_pages': (len(filtered_history) + per_page - 1) // per_page
            },
            'summary': {
                'total_actions': len(plugin_installation_history),
                'install_count': len([h for h in plugin_installation_history if h['action'] == 'install']),
                'uninstall_count': len([h for h in plugin_installation_history if h['action'] == 'uninstall']),
                'update_count': len([h for h in plugin_installation_history if h['action'] == 'update'])
            }
        })
        
    except Exception as e:
        logger.error(f"설치 이력 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 헬퍼 함수들
def secure_filename(filename):
    """안전한 파일명 생성"""
    import re
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    return filename

def validate_plugin_structure(plugin_dir: str, metadata: dict) -> dict:
    """플러그인 구조 검증"""
    required_files = ['__init__.py', 'plugin.py']
    required_metadata_fields = ['plugin_id', 'name', 'version', 'description']
    
    # 필수 파일 확인
    for file in required_files:
        if not os.path.exists(os.path.join(plugin_dir, file)):
            return {'valid': False, 'error': f'필수 파일이 없습니다: {file}'}
    
    # 메타데이터 필드 확인
    for field in required_metadata_fields:
        if field not in metadata:
            return {'valid': False, 'error': f'필수 메타데이터 필드가 없습니다: {field}'}
    
    return {'valid': True}

def check_plugin_compatibility(plugin_id: str, version: str = None) -> dict:
    """플러그인 호환성 검사"""
    # 실제로는 더 복잡한 호환성 검사 로직이 필요
    return {'compatible': True}

def log_plugin_action(plugin_id: str, action: str, message: str, level: str = 'info'):
    """플러그인 액션 로그 기록"""
    if plugin_id not in plugin_logs:
        plugin_logs[plugin_id] = []
    
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'action': action,
        'message': message,
        'level': level
    }
    
    plugin_logs[plugin_id].append(log_entry)
    
    # 로그 개수 제한 (최근 1000개만 유지)
    if len(plugin_logs[plugin_id]) > 1000:
        plugin_logs[plugin_id] = plugin_logs[plugin_id][-1000:]

def generate_dummy_metrics(plugin_id: str, time_range: str) -> dict:
    """더미 메트릭 데이터 생성"""
    import random
    
    # 시간 범위에 따른 데이터 포인트 수 계산
    if time_range == '1h':
        points = 60
    elif time_range == '24h':
        points = 1440
    elif time_range == '7d':
        points = 10080
    else:
        points = 1440
    
    # 더미 데이터 생성
    cpu_data = [random.uniform(0, 100) for _ in range(points)]
    memory_data = [random.uniform(0, 512) for _ in range(points)]
    response_time_data = [random.uniform(0, 1000) for _ in range(points)]
    
    return {
        'cpu_usage': {
            'current': cpu_data[-1],
            'average': sum(cpu_data) / len(cpu_data),
            'max': max(cpu_data),
            'min': min(cpu_data),
            'history': cpu_data
        },
        'memory_usage': {
            'current': memory_data[-1],
            'average': sum(memory_data) / len(memory_data),
            'max': max(memory_data),
            'min': min(memory_data),
            'history': memory_data
        },
        'response_time': {
            'current': response_time_data[-1],
            'average': sum(response_time_data) / len(response_time_data),
            'max': max(response_time_data),
            'min': min(response_time_data),
            'history': response_time_data
        },
        'error_rate': random.uniform(0, 5),
        'last_updated': datetime.utcnow().isoformat()
    } 