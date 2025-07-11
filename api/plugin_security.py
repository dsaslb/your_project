from flask import Blueprint, request, jsonify
from core.backend.plugin_security_system import PluginSecuritySystem, PermissionType, SecurityLevel
from utils.auth_decorators import admin_required, login_required
import logging
from typing import Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 블루프린트 생성
plugin_security_bp = Blueprint('plugin_security', __name__, url_prefix='/api/plugin-security')

# 보안 시스템 인스턴스
security_system = PluginSecuritySystem()

def safe_str(val: Optional[str]) -> str:
    return val if val is not None else ''

@plugin_security_bp.route('/policies', methods=['GET'])
@admin_required
def get_security_policies():
    """보안 정책 목록 조회"""
    try:
        plugin_id = request.args.get('plugin_id')
        
        if plugin_id:
            policy = security_system.get_security_policy(plugin_id)
            if policy:
                return jsonify({
                    'success': True,
                    'data': policy
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '보안 정책을 찾을 수 없습니다'
                }), 404
        else:
            # 모든 정책 조회 (실제로는 전체 목록 API 필요)
            return jsonify({
                'success': True,
                'data': []
            })
            
    except Exception as e:
        logger.error(f"보안 정책 조회 실패: {e}")
        return jsonify({
            'success': False,
            'message': '보안 정책 조회 중 오류가 발생했습니다'
        }), 500

@plugin_security_bp.route('/policies', methods=['POST'])
@admin_required
def create_security_policy():
    """보안 정책 생성"""
    try:
        data = request.get_json()
        
        if not data or 'plugin_id' not in data:
            return jsonify({
                'success': False,
                'message': '필수 필드가 누락되었습니다'
            }), 400
        
        plugin_id = data['plugin_id']
        policy_data = {
            'security_level': data.get('security_level', 'medium'),
            'allowed_ips': data.get('allowed_ips', []),
            'allowed_domains': data.get('allowed_domains', []),
            'max_requests_per_minute': data.get('max_requests_per_minute', 100),
            'require_authentication': data.get('require_authentication', True),
            'require_authorization': data.get('require_authorization', True),
            'allowed_permissions': data.get('allowed_permissions', ['read'])
        }
        
        success = security_system.create_security_policy(plugin_id, policy_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': '보안 정책이 생성되었습니다'
            })
        else:
            return jsonify({
                'success': False,
                'message': '보안 정책 생성에 실패했습니다'
            }), 400
            
    except Exception as e:
        logger.error(f"보안 정책 생성 실패: {e}")
        return jsonify({
            'success': False,
            'message': '보안 정책 생성 중 오류가 발생했습니다'
        }), 500

@plugin_security_bp.route('/policies/<plugin_id>', methods=['PUT'])
@admin_required
def update_security_policy(plugin_id):
    """보안 정책 업데이트"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '업데이트할 데이터가 없습니다'
            }), 400
        
        success = security_system.update_security_policy(plugin_id, data)
        
        if success:
            return jsonify({
                'success': True,
                'message': '보안 정책이 업데이트되었습니다'
            })
        else:
            return jsonify({
                'success': False,
                'message': '보안 정책 업데이트에 실패했습니다'
            }), 400
            
    except Exception as e:
        logger.error(f"보안 정책 업데이트 실패: {e}")
        return jsonify({
            'success': False,
            'message': '보안 정책 업데이트 중 오류가 발생했습니다'
        }), 500

@plugin_security_bp.route('/policies/<plugin_id>', methods=['DELETE'])
@admin_required
def delete_security_policy(plugin_id):
    """보안 정책 삭제"""
    try:
        success = security_system.delete_security_policy(plugin_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': '보안 정책이 삭제되었습니다'
            })
        else:
            return jsonify({
                'success': False,
                'message': '보안 정책 삭제에 실패했습니다'
            }), 400
            
    except Exception as e:
        logger.error(f"보안 정책 삭제 실패: {e}")
        return jsonify({
            'success': False,
            'message': '보안 정책 삭제 중 오류가 발생했습니다'
        }), 500

@plugin_security_bp.route('/api-keys', methods=['GET'])
@admin_required
def get_api_keys():
    """API 키 목록 조회"""
    try:
        plugin_id = request.args.get('plugin_id')
        api_keys = security_system.get_api_keys(safe_str(plugin_id))
        
        return jsonify({
            'success': True,
            'data': api_keys
        })
        
    except Exception as e:
        logger.error(f"API 키 조회 실패: {e}")
        return jsonify({
            'success': False,
            'message': 'API 키 조회 중 오류가 발생했습니다'
        }), 500

@plugin_security_bp.route('/api-keys', methods=['POST'])
@admin_required
def generate_api_key():
    """API 키 생성"""
    try:
        data = request.get_json()
        
        if not data or 'plugin_id' not in data or 'name' not in data:
            return jsonify({
                'success': False,
                'message': '필수 필드가 누락되었습니다'
            }), 400
        
        plugin_id = data['plugin_id']
        name = data['name']
        permissions = data.get('permissions', ['read'])
        expires_in_days = data.get('expires_in_days')
        
        api_key = security_system.generate_api_key(plugin_id, name, permissions, expires_in_days)
        
        if api_key:
            return jsonify({
                'success': True,
                'data': {
                    'api_key': api_key,
                    'name': name,
                    'plugin_id': plugin_id,
                    'permissions': permissions
                },
                'message': 'API 키가 생성되었습니다'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'API 키 생성에 실패했습니다'
            }), 400
            
    except Exception as e:
        logger.error(f"API 키 생성 실패: {e}")
        return jsonify({
            'success': False,
            'message': 'API 키 생성 중 오류가 발생했습니다'
        }), 500

@plugin_security_bp.route('/api-keys/<key_id>/revoke', methods=['POST'])
@admin_required
def revoke_api_key(key_id):
    """API 키 폐기"""
    try:
        success = security_system.revoke_api_key(key_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'API 키가 폐기되었습니다'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'API 키 폐기에 실패했습니다'
            }), 400
            
    except Exception as e:
        logger.error(f"API 키 폐기 실패: {e}")
        return jsonify({
            'success': False,
            'message': 'API 키 폐기 중 오류가 발생했습니다'
        }), 500

@plugin_security_bp.route('/validate-api-key', methods=['POST'])
def validate_api_key():
    """API 키 검증"""
    try:
        data = request.get_json()
        
        if not data or 'api_key' not in data or 'plugin_id' not in data:
            return jsonify({
                'success': False,
                'message': '필수 필드가 누락되었습니다'
            }), 400
        
        api_key = data['api_key']
        plugin_id = data['plugin_id']
        required_permission = PermissionType(data.get('permission', 'read'))
        
        validation_result = security_system.validate_api_key(api_key, plugin_id, required_permission)
        
        if validation_result:
            return jsonify({
                'success': True,
                'data': validation_result,
                'message': 'API 키가 유효합니다'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'API 키가 유효하지 않습니다'
            }), 401
            
    except Exception as e:
        logger.error(f"API 키 검증 실패: {e}")
        return jsonify({
            'success': False,
            'message': 'API 키 검증 중 오류가 발생했습니다'
        }), 500

@plugin_security_bp.route('/audit-logs', methods=['GET'])
@admin_required
def get_audit_logs():
    """감사 로그 조회"""
    try:
        plugin_id = request.args.get('plugin_id')
        user_id = request.args.get('user_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 100))
        
        audit_logs = security_system.get_audit_logs(
            plugin_id=safe_str(plugin_id),
            user_id=safe_str(user_id),
            start_date=safe_str(start_date),
            end_date=safe_str(end_date),
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'data': audit_logs
        })
        
    except Exception as e:
        logger.error(f"감사 로그 조회 실패: {e}")
        return jsonify({
            'success': False,
            'message': '감사 로그 조회 중 오류가 발생했습니다'
        }), 500

@plugin_security_bp.route('/vulnerabilities', methods=['GET'])
@admin_required
def get_vulnerabilities():
    """취약점 보고서 조회"""
    try:
        plugin_id = request.args.get('plugin_id')
        severity = request.args.get('severity')
        status = request.args.get('status')
        
        vulnerabilities = security_system.get_vulnerabilities(
            plugin_id=safe_str(plugin_id),
            severity=safe_str(severity),
            status=safe_str(status)
        )
        
        return jsonify({
            'success': True,
            'data': vulnerabilities
        })
        
    except Exception as e:
        logger.error(f"취약점 보고서 조회 실패: {e}")
        return jsonify({
            'success': False,
            'message': '취약점 보고서 조회 중 오류가 발생했습니다'
        }), 500

@plugin_security_bp.route('/vulnerabilities/scan/<plugin_id>', methods=['POST'])
@admin_required
def scan_vulnerabilities(plugin_id):
    """플러그인 취약점 스캔"""
    try:
        vulnerabilities = security_system.scan_plugin_vulnerabilities(plugin_id)
        
        return jsonify({
            'success': True,
            'data': {
                'plugin_id': plugin_id,
                'vulnerabilities': vulnerabilities,
                'total_count': len(vulnerabilities),
                'critical_count': len([v for v in vulnerabilities if v['severity'] == 'critical']),
                'high_count': len([v for v in vulnerabilities if v['severity'] == 'high']),
                'medium_count': len([v for v in vulnerabilities if v['severity'] == 'medium']),
                'low_count': len([v for v in vulnerabilities if v['severity'] == 'low'])
            },
            'message': f'{len(vulnerabilities)}개의 취약점이 발견되었습니다'
        })
        
    except Exception as e:
        logger.error(f"취약점 스캔 실패: {e}")
        return jsonify({
            'success': False,
            'message': '취약점 스캔 중 오류가 발생했습니다'
        }), 500

@plugin_security_bp.route('/vulnerabilities/<report_id>/status', methods=['PUT'])
@admin_required
def update_vulnerability_status(report_id):
    """취약점 상태 업데이트"""
    try:
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({
                'success': False,
                'message': '상태 정보가 누락되었습니다'
            }), 400
        
        status = data['status']
        success = security_system.update_vulnerability_status(report_id, status)
        
        if success:
            return jsonify({
                'success': True,
                'message': '취약점 상태가 업데이트되었습니다'
            })
        else:
            return jsonify({
                'success': False,
                'message': '취약점 상태 업데이트에 실패했습니다'
            }), 400
            
    except Exception as e:
        logger.error(f"취약점 상태 업데이트 실패: {e}")
        return jsonify({
            'success': False,
            'message': '취약점 상태 업데이트 중 오류가 발생했습니다'
        }), 500

@plugin_security_bp.route('/permissions/check', methods=['POST'])
@login_required
def check_permission():
    """권한 확인"""
    try:
        data = request.get_json()
        
        if not data or 'plugin_id' not in data or 'permission' not in data:
            return jsonify({
                'success': False,
                'message': '필수 필드가 누락되었습니다'
            }), 400
        
        plugin_id = data['plugin_id']
        permission = PermissionType(data['permission'])
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            user_id = data.get('user_id', '')
        
        has_permission = security_system.check_permission(plugin_id, user_id, permission)
        
        return jsonify({
            'success': True,
            'data': {
                'has_permission': has_permission,
                'plugin_id': plugin_id,
                'permission': permission.value,
                'user_id': user_id
            }
        })
        
    except Exception as e:
        logger.error(f"권한 확인 실패: {e}")
        return jsonify({
            'success': False,
            'message': '권한 확인 중 오류가 발생했습니다'
        }), 500

@plugin_security_bp.route('/security-levels', methods=['GET'])
def get_security_levels():
    """보안 레벨 목록 조회"""
    try:
        security_levels = [level.value for level in SecurityLevel]
        
        return jsonify({
            'success': True,
            'data': security_levels
        })
        
    except Exception as e:
        logger.error(f"보안 레벨 조회 실패: {e}")
        return jsonify({
            'success': False,
            'message': '보안 레벨 조회 중 오류가 발생했습니다'
        }), 500

@plugin_security_bp.route('/permission-types', methods=['GET'])
def get_permission_types():
    """권한 유형 목록 조회"""
    try:
        permission_types = [perm.value for perm in PermissionType]
        
        return jsonify({
            'success': True,
            'data': permission_types
        })
        
    except Exception as e:
        logger.error(f"권한 유형 조회 실패: {e}")
        return jsonify({
            'success': False,
            'message': '권한 유형 조회 중 오류가 발생했습니다'
        }), 500 