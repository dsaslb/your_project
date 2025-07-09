from flask import Blueprint, jsonify, request, current_app, g
from functools import wraps
import jwt
import datetime
import logging
from typing import Dict, Any, Optional

security_bp = Blueprint('security', __name__)

# 보안 로그 설정
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

# JWT 토큰 검증 데코레이터
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 헤더에서 토큰 추출
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': '토큰 형식이 잘못되었습니다'}), 401
        
        if not token:
            return jsonify({'message': '토큰이 필요합니다'}), 401
        
        try:
            # 토큰 검증
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            
            # Flask g 객체에 사용자 정보 저장 (요청별로 안전하게 관리)
            g.user_id = payload['user_id']
            g.user_role = payload['role']
            
            # 보안 로그 기록
            log_security_event('token_validation', 'success', {
                'user_id': payload['user_id'],
                'ip': request.remote_addr,
                'endpoint': request.endpoint
            })
            
        except jwt.ExpiredSignatureError:
            log_security_event('token_validation', 'expired', {
                'ip': request.remote_addr,
                'endpoint': request.endpoint
            })
            return jsonify({'message': '토큰이 만료되었습니다'}), 401
        except jwt.InvalidTokenError:
            log_security_event('token_validation', 'invalid', {
                'ip': request.remote_addr,
                'endpoint': request.endpoint
            })
            return jsonify({'message': '유효하지 않은 토큰입니다'}), 401
        
        return f(*args, **kwargs)
    return decorated

# 권한 검증 데코레이터
def require_role(required_role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(g, 'user_role'):
                return jsonify({'message': '인증이 필요합니다'}), 401
            
            if g.user_role != required_role and g.user_role != 'admin':
                log_security_event('permission_denied', 'insufficient_role', {
                    'user_id': getattr(g, 'user_id', 'unknown'),
                    'user_role': g.user_role,
                    'required_role': required_role,
                    'ip': request.remote_addr,
                    'endpoint': request.endpoint
                })
                return jsonify({'message': '권한이 부족합니다'}), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator

# 보안 이벤트 로깅
def log_security_event(event_type: str, status: str, details: Dict[str, Any]):
    """보안 이벤트를 로그에 기록"""
    log_entry = {
        'timestamp': datetime.datetime.now().isoformat(),
        'event_type': event_type,
        'status': status,
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', ''),
        'details': details
    }
    
    security_logger.info(f"SECURITY_EVENT: {log_entry}")
    
    # TODO: 데이터베이스에 보안 로그 저장
    # save_security_log_to_db(log_entry)

@security_bp.route('/api/security/token/refresh', methods=['POST'])
@require_auth
def refresh_token():
    """JWT 토큰 갱신"""
    try:
        # 새로운 토큰 생성
        new_token = jwt.encode({
            'user_id': g.user_id,
            'role': g.user_role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        log_security_event('token_refresh', 'success', {
            'user_id': g.user_id,
            'ip': request.remote_addr
        })
        
        return jsonify({
            'token': new_token,
            'expires_in': 86400  # 24시간
        })
        
    except Exception as e:
        log_security_event('token_refresh', 'error', {
            'user_id': getattr(g, 'user_id', 'unknown'),
            'error': str(e),
            'ip': request.remote_addr
        })
        return jsonify({'message': '토큰 갱신 실패'}), 500

@security_bp.route('/api/security/logs', methods=['GET'])
@require_auth
@require_role('admin')
def get_security_logs():
    """보안 로그 조회 (관리자만)"""
    try:
        # TODO: 실제 데이터베이스에서 보안 로그 조회
        logs = [
            {
                'id': 1,
                'timestamp': datetime.datetime.now().isoformat(),
                'event_type': 'login',
                'status': 'success',
                'user_id': 'admin',
                'ip_address': '192.168.1.100',
                'details': {'method': 'password'}
            },
            {
                'id': 2,
                'timestamp': (datetime.datetime.now() - datetime.timedelta(hours=1)).isoformat(),
                'event_type': 'permission_denied',
                'status': 'failed',
                'user_id': 'user1',
                'ip_address': '192.168.1.101',
                'details': {'required_role': 'admin'}
            }
        ]
        
        return jsonify({'logs': logs})
        
    except Exception as e:
        return jsonify({'message': '로그 조회 실패'}), 500

@security_bp.route('/api/security/settings', methods=['GET'])
@require_auth
def get_security_settings():
    """보안 설정 조회"""
    settings = {
        'session_timeout': 30,  # 분
        'require_mfa': False,
        'password_policy': {
            'min_length': 8,
            'require_special_char': True,
            'require_number': True,
            'require_uppercase': True,
        },
        'audit_logging': True,
        'max_login_attempts': 5,
        'lockout_duration': 15,  # 분
    }
    
    return jsonify(settings)

@security_bp.route('/api/security/settings', methods=['PUT'])
@require_auth
@require_role('admin')
def update_security_settings():
    """보안 설정 업데이트 (관리자만)"""
    try:
        data = request.get_json()
        
        # TODO: 실제 설정 저장 로직
        log_security_event('settings_update', 'success', {
            'user_id': g.user_id,
            'settings': data,
            'ip': request.remote_addr
        })
        
        return jsonify({'message': '보안 설정이 업데이트되었습니다'})
        
    except Exception as e:
        log_security_event('settings_update', 'error', {
            'user_id': getattr(g, 'user_id', 'unknown'),
            'error': str(e),
            'ip': request.remote_addr
        })
        return jsonify({'message': '설정 업데이트 실패'}), 500

@security_bp.route('/api/security/audit', methods=['GET'])
@require_auth
@require_role('admin')
def get_audit_trail():
    """감사 추적 조회 (관리자만)"""
    try:
        # TODO: 실제 감사 추적 데이터 조회
        audit_trail = [
            {
                'id': 1,
                'timestamp': datetime.datetime.now().isoformat(),
                'user_id': 'admin',
                'action': 'data_export',
                'resource': 'staff_data',
                'ip_address': '192.168.1.100',
                'details': {'record_count': 42}
            },
            {
                'id': 2,
                'timestamp': (datetime.datetime.now() - datetime.timedelta(hours=2)).isoformat(),
                'user_id': 'manager1',
                'action': 'permission_change',
                'resource': 'user_permissions',
                'ip_address': '192.168.1.102',
                'details': {'target_user': 'user1', 'new_role': 'staff'}
            }
        ]
        
        return jsonify({'audit_trail': audit_trail})
        
    except Exception as e:
        return jsonify({'message': '감사 추적 조회 실패'}), 500 