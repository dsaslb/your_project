"""
플러그인 관리 API
플러그인의 등록, 활성화, 비활성화, 설정 관리를 위한 API
"""

from flask import Blueprint, jsonify, request
from datetime import datetime

from core.backend.plugin_interface import plugin_registry
from core.backend.plugin_loader import plugin_loader

plugin_management_bp = Blueprint('plugin_management', __name__)

@plugin_management_bp.route('/plugins', methods=['GET'])
def get_plugins():
    """플러그인 목록 조회"""
    try:
        plugins = []
        
        for plugin_id, plugin in plugin_registry.get_all_plugins().items():
            metadata = plugin.get_metadata()
            health_status = plugin.get_health_status()
            
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
                'created_at': metadata.created_at.isoformat() if metadata.created_at else None,
                'updated_at': metadata.updated_at.isoformat() if metadata.updated_at else None
            }
            plugins.append(plugin_info)
        
        return jsonify({
            'success': True,
            'plugins': plugins,
            'total_count': len(plugins)
        })
        
    except Exception as e:
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
    """플러그인 설치"""
    try:
        # 실제로는 외부 저장소에서 다운로드하여 설치
        # 현재는 로컬 플러그인을 활성화하는 것으로 시뮬레이션
        plugin = plugin_registry.get_plugin(plugin_id)
        if not plugin:
            return jsonify({
                'success': False,
                'error': '플러그인을 찾을 수 없습니다'
            }), 404
        
        # 플러그인 활성화
        if plugin.on_enable():
            config = plugin_loader.get_plugin_config(plugin_id) or {}
            config['enabled'] = True
            config['installed_at'] = datetime.utcnow().isoformat()
            config['updated_at'] = datetime.utcnow().isoformat()
            plugin_loader.save_plugin_config(plugin_id, config)
            
            return jsonify({
                'success': True,
                'message': f'플러그인 {plugin_id}이 설치되었습니다'
            })
        else:
            return jsonify({
                'success': False,
                'error': '플러그인 설치에 실패했습니다'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plugin_management_bp.route('/plugins/<plugin_id>/uninstall', methods=['POST'])
def uninstall_plugin(plugin_id: str):
    """플러그인 제거"""
    try:
        plugin = plugin_registry.get_plugin(plugin_id)
        if not plugin:
            return jsonify({
                'success': False,
                'error': '플러그인을 찾을 수 없습니다'
            }), 404
        
        # 플러그인 비활성화
        if plugin.on_disable():
            config = plugin_loader.get_plugin_config(plugin_id) or {}
            config['enabled'] = False
            config['uninstalled_at'] = datetime.utcnow().isoformat()
            config['updated_at'] = datetime.utcnow().isoformat()
            plugin_loader.save_plugin_config(plugin_id, config)
            
            return jsonify({
                'success': True,
                'message': f'플러그인 {plugin_id}이 제거되었습니다'
            })
        else:
            return jsonify({
                'success': False,
                'error': '플러그인 제거에 실패했습니다'
            }), 500
        
    except Exception as e:
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