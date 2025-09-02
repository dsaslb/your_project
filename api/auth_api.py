from flask import Blueprint, jsonify, request, g
from utils.auth_manager import AuthManager, AuthConfig
from .utils import APIResponse, InputValidator, api_error_handler, log_api_request, validate_json_input, get_client_ip, get_user_agent
import os
import logging

# 로거 설정
logger = logging.getLogger(__name__)

# 인증 Blueprint 생성
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# 인증 관리자 초기화
config = AuthConfig(
    secret_key=os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production'),
    token_expiry_hours=24,
    refresh_token_expiry_days=7,
    max_login_attempts=5,
    lockout_duration_minutes=30,
    password_min_length=8,
    require_special_chars=True,
    require_numbers=True,
    require_uppercase=True,
    session_timeout_minutes=60
)

auth_manager = AuthManager(config)

def require_auth(f):
    """인증이 필요한 엔드포인트 데코레이터"""
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return APIResponse.error('인증 토큰이 필요합니다', 401)
        
        token = auth_header.split(' ')[1]
        user_data = auth_manager.validate_token(token)
        
        if not user_data:
            return APIResponse.error('유효하지 않은 토큰입니다', 401)
        
        g.current_user = user_data
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

def require_permission(permission_name):
    """특정 권한이 필요한 엔드포인트 데코레이터"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'current_user'):
                return APIResponse.error('인증이 필요합니다', 401)
            
            user_id = g.current_user.get('user_id')
            if not auth_manager.check_permission(user_id, permission_name):
                return APIResponse.error('권한이 없습니다', 403)
            
            return f(*args, **kwargs)
        
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['POST'])
@api_error_handler
@log_api_request
@validate_json_input(required_fields=['username', 'password'])
def login():
    """사용자 로그인"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # IP 주소와 User-Agent 가져오기
        ip_address = get_client_ip()
        user_agent = get_user_agent()
        
        # 사용자 인증
        auth_result = auth_manager.authenticate_user(username, password, ip_address, user_agent)
        
        if not auth_result:
            return APIResponse.error('잘못된 사용자명 또는 비밀번호입니다', 401)
        
        return APIResponse.success({
                'message': '로그인이 성공했습니다',
                'data': auth_result
            }), 200
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'로그인 오류: {str(e)}'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """사용자 로그아웃"""
    try:
        user_id = g.current_user.get('user_id')
        session_id = request.headers.get('X-Session-ID')
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        auth_manager.logout(user_id, session_id, ip_address, user_agent)
        
        return jsonify({
            'status': 'success',
            'message': '로그아웃이 완료되었습니다'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'로그아웃 오류: {str(e)}'
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """토큰 갱신"""
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return jsonify({
                'status': 'error',
                'message': '리프레시 토큰이 필요합니다'
            }), 400
        
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # 토큰 갱신
        refresh_result = auth_manager.refresh_token(refresh_token, ip_address, user_agent)
        
        if not refresh_result:
            return jsonify({
                'status': 'error',
                'message': '유효하지 않은 리프레시 토큰입니다'
            }), 401
        
        return jsonify({
            'status': 'success',
            'message': '토큰이 갱신되었습니다',
            'data': refresh_result
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'토큰 갱신 오류: {str(e)}'
        }), 500

@auth_bp.route('/validate', methods=['GET'])
@require_auth
def validate_token():
    """토큰 검증"""
    try:
        return jsonify({
            'status': 'success',
            'message': '토큰이 유효합니다',
            'data': {
                'user_id': g.current_user.get('user_id'),
                'username': g.current_user.get('username'),
                'role': g.current_user.get('role'),
                'permissions': g.current_user.get('permissions', [])
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'토큰 검증 오류: {str(e)}'
        }), 500

@auth_bp.route('/change-password', methods=['POST'])
@require_auth
def change_password():
    """비밀번호 변경"""
    try:
        user_id = g.current_user.get('user_id')
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({
                'status': 'error',
                'message': '현재 비밀번호와 새 비밀번호가 필요합니다'
            }), 400
        
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # 비밀번호 변경
        success = auth_manager.change_password(user_id, current_password, new_password, ip_address, user_agent)
        
        if not success:
            return jsonify({
                'status': 'error',
                'message': '비밀번호 변경에 실패했습니다'
            }), 400
        
        return jsonify({
            'status': 'success',
            'message': '비밀번호가 변경되었습니다'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'비밀번호 변경 오류: {str(e)}'
        }), 500

@auth_bp.route('/validate-password', methods=['POST'])
def validate_password():
    """비밀번호 정책 검증"""
    try:
        data = request.get_json()
        password = data.get('password')
        
        if not password:
            return jsonify({
                'status': 'error',
                'message': '비밀번호가 필요합니다'
            }), 400
        
        # 비밀번호 검증
        validation_result = auth_manager.validate_password(password)
        
        return jsonify({
            'status': 'success',
            'data': validation_result
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'비밀번호 검증 오류: {str(e)}'
        }), 500

@auth_bp.route('/users', methods=['GET'])
@require_auth
@require_permission('users_manage')
def get_users():
    """사용자 목록 조회"""
    try:
        users = auth_manager.get_all_users()
        
        user_list = []
        for user in users:
            user_dict = {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'is_active': user.is_active,
                'is_locked': user.is_locked,
                'failed_login_attempts': user.failed_login_attempts,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            }
            user_list.append(user_dict)
        
        return jsonify({
            'status': 'success',
            'data': user_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'사용자 조회 오류: {str(e)}'
        }), 500

@auth_bp.route('/users', methods=['POST'])
@require_auth
@require_permission('users_manage')
def create_user():
    """사용자 생성"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        role = data.get('role')
        
        if not all([username, email, password, full_name, role]):
            return jsonify({
                'status': 'error',
                'message': '모든 필수 필드가 필요합니다'
            }), 400
        
        # 사용자 생성
        user_id = auth_manager.create_user(username, email, password, full_name, role)
        
        return jsonify({
            'status': 'success',
            'message': '사용자가 생성되었습니다',
            'data': {'user_id': user_id}
        }), 201
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'사용자 생성 오류: {str(e)}'
        }), 500

@auth_bp.route('/users/<user_id>/unlock', methods=['POST'])
@require_auth
@require_permission('users_manage')
def unlock_user(user_id):
    """사용자 계정 잠금 해제"""
    try:
        success = auth_manager.unlock_account(user_id)
        
        if not success:
            return jsonify({
                'status': 'error',
                'message': '사용자를 찾을 수 없습니다'
            }), 404
        
        return jsonify({
            'status': 'success',
            'message': '계정 잠금이 해제되었습니다'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'계정 잠금 해제 오류: {str(e)}'
        }), 500

@auth_bp.route('/roles', methods=['GET'])
@require_auth
@require_permission('users_manage')
def get_roles():
    """역할 목록 조회"""
    try:
        roles = auth_manager.get_all_roles()
        
        role_list = []
        for role in roles:
            role_dict = {
                'role_id': role.role_id,
                'name': role.name,
                'description': role.description,
                'permissions': role.permissions,
                'is_active': role.is_active,
                'created_at': role.created_at.isoformat() if role.created_at else None
            }
            role_list.append(role_dict)
        
        return jsonify({
            'status': 'success',
            'data': role_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'역할 조회 오류: {str(e)}'
        }), 500

@auth_bp.route('/permissions', methods=['GET'])
@require_auth
@require_permission('users_manage')
def get_permissions():
    """권한 목록 조회"""
    try:
        permissions = list(auth_manager.permissions.values())
        
        permission_list = []
        for permission in permissions:
            permission_dict = {
                'permission_id': permission.permission_id,
                'name': permission.name,
                'description': permission.description,
                'resource': permission.resource,
                'action': permission.action,
                'is_active': permission.is_active
            }
            permission_list.append(permission_dict)
        
        return jsonify({
            'status': 'success',
            'data': permission_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'권한 조회 오류: {str(e)}'
        }), 500

@auth_bp.route('/security-events', methods=['GET'])
@require_auth
@require_permission('users_manage')
def get_security_events():
    """보안 이벤트 조회"""
    try:
        user_id = request.args.get('user_id')
        limit = int(request.args.get('limit', 100))
        
        events = auth_manager.get_security_events(user_id, limit)
        
        event_list = []
        for event in events:
            event_dict = {
                'event_id': event.event_id,
                'user_id': event.user_id,
                'event_type': event.event_type,
                'ip_address': event.ip_address,
                'user_agent': event.user_agent,
                'details': event.details,
                'timestamp': event.timestamp.isoformat(),
                'severity': event.severity
            }
            event_list.append(event_dict)
        
        return jsonify({
            'status': 'success',
            'data': event_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'보안 이벤트 조회 오류: {str(e)}'
        }), 500

@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """현재 사용자 프로필 조회"""
    try:
        user_id = g.current_user.get('user_id')
        user = auth_manager.get_user_by_id(user_id)
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': '사용자를 찾을 수 없습니다'
            }), 404
        
        profile = {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
            'is_active': user.is_active,
            'is_locked': user.is_locked,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'permissions': auth_manager.get_user_permissions(user_id)
        }
        
        return jsonify({
            'status': 'success',
            'data': profile
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'프로필 조회 오류: {str(e)}'
        }), 500

@auth_bp.route('/health', methods=['GET'])
def health_check():
    """인증 시스템 상태 확인"""
    try:
        return jsonify({
            'status': 'healthy',
            'message': '인증 시스템이 정상적으로 작동 중입니다',
            'data': {
                'total_users': len(auth_manager.users),
                'total_roles': len(auth_manager.roles),
                'total_permissions': len(auth_manager.permissions),
                'active_sessions': len([s for s in auth_manager.sessions.values() if s.is_active])
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'인증 시스템 오류: {str(e)}'
        }), 500 