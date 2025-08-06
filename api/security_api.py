"""
보안 API 엔드포인트
엔터프라이즈급 보안 기능을 위한 REST API
"""

from flask import Blueprint, request, jsonify, g
from flask_cors import cross_origin
from datetime import datetime, timedelta
import logging
import traceback
import secrets
import json
from typing import Dict, Any, Optional, List

# 보안 모듈 임포트
from security.multi_factor_auth import MultiFactorAuth, BiometricAuth
from security.encryption_manager import KeyManager, EncryptionManager
from security.audit_system import AuditSystem, AuditEvent, EventType, SecurityLevel
from security.security_manager import SecurityManager, SecurityConfig, UserSession, SecurityEvent

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 블루프린트 생성
security_bp = Blueprint('security', __name__, url_prefix='/api/security')

# 전역 보안 시스템 인스턴스
mfa_system = None
key_manager = None
encryption_manager = None
audit_system = None
biometric_auth = None

# 보안 관리자 초기화
security_config = SecurityConfig(
    jwt_secret="your-super-secret-key-change-this-in-production",
    jwt_algorithm="HS256",
    jwt_expiration_hours=24,
    password_min_length=8,
    max_login_attempts=5,
    lockout_duration_minutes=30,
    session_timeout_minutes=60
)

security_manager = SecurityManager(security_config)

def init_security_systems():
    """보안 시스템 초기화"""
    global mfa_system, key_manager, encryption_manager, audit_system, biometric_auth
    
    try:
        # MFA 시스템 초기화
        mfa_config = {
            'totp_issuer': 'Your Program',
            'totp_digits': 6,
            'totp_interval': 30,
            'max_attempts': 3,
            'session_timeout': 300,
            'backup_codes_count': 10,
            'smtp': {
                'host': 'smtp.gmail.com',
                'port': 587,
                'username': 'your-email@gmail.com',
                'password': 'your-password',
                'from_email': 'noreply@yourprogram.com'
            }
        }
        mfa_system = MultiFactorAuth(mfa_config)
        
        # 키 관리자 초기화
        key_manager = KeyManager()
        
        # 암호화 관리자 초기화
        encryption_manager = EncryptionManager(key_manager)
        
        # 감사 시스템 초기화
        audit_system = AuditSystem()
        
        # 생체 인증 초기화
        biometric_auth = BiometricAuth()
        
        logger.info("보안 시스템 초기화 완료")
        
    except Exception as e:
        logger.error(f"보안 시스템 초기화 오류: {e}")
        logger.error(traceback.format_exc())

def log_security_event(event_type: EventType, user_id: Optional[str] = None, 
                      success: bool = True, details: Dict[str, Any] = None):
    """보안 이벤트 로깅"""
    try:
        if audit_system:
            event = AuditEvent(
                event_id=f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}",
                event_type=event_type,
                user_id=user_id,
                session_id=request.headers.get('X-Session-ID'),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                timestamp=datetime.now(),
                security_level=SecurityLevel.MEDIUM,
                description=f"{event_type.value} 이벤트",
                details=details or {},
                success=success,
                metadata={'endpoint': request.endpoint}
            )
            audit_system.log_event(event)
    except Exception as e:
        logger.error(f"보안 이벤트 로깅 오류: {e}")

# 인증 데코레이터
def require_auth(f):
    """인증이 필요한 엔드포인트용 데코레이터"""
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': '인증 토큰이 필요합니다'}), 401
        
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': '유효하지 않은 토큰 형식입니다'}), 401
        
        token = auth_header[7:]  # 'Bearer ' 제거
        payload = security_manager.verify_jwt_token(token)
        
        if not payload:
            return jsonify({'error': '유효하지 않은 토큰입니다'}), 401
        
        g.user_id = payload['user_id']
        g.user_roles = payload.get('roles', [])
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

# 권한 검증 데코레이터
def require_role(required_role: str):
    """특정 역할이 필요한 엔드포인트용 데코레이터"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'user_roles'):
                return jsonify({'error': '인증이 필요합니다'}), 401
            
            if required_role not in g.user_roles:
                return jsonify({'error': '권한이 부족합니다'}), 403
            
            return f(*args, **kwargs)
        
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

@security_bp.route('/login', methods=['POST'])
def login():
    """사용자 로그인"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': '사용자명과 비밀번호가 필요합니다'}), 400
        
        # IP 주소 가져오기
        ip_address = request.remote_addr
        
        # 계정 잠금 확인
        if security_manager.is_account_locked(username):
            return jsonify({
                'error': '계정이 잠겼습니다. 잠시 후 다시 시도해주세요',
                'locked': True
            }), 423
        
        # 실제 구현에서는 데이터베이스에서 사용자 정보를 조회해야 함
        # 여기서는 예시 데이터 사용
        mock_users = {
            'admin': {
                'password_hash': security_manager.hash_password('admin123'),
                'roles': ['admin', 'user'],
                'user_id': 'admin'
            },
            'user': {
                'password_hash': security_manager.hash_password('user123'),
                'roles': ['user'],
                'user_id': 'user'
            }
        }
        
        if username not in mock_users:
            security_manager.track_login_attempt(username, ip_address, False)
            return jsonify({'error': '잘못된 사용자명 또는 비밀번호입니다'}), 401
        
        user = mock_users[username]
        
        # 비밀번호 검증
        if not security_manager.verify_password(password, user['password_hash']):
            security_manager.track_login_attempt(username, ip_address, False)
            return jsonify({'error': '잘못된 사용자명 또는 비밀번호입니다'}), 401
        
        # 로그인 성공
        security_manager.track_login_attempt(username, ip_address, True)
        
        # JWT 토큰 생성
        token = security_manager.generate_jwt_token(user['user_id'], user['roles'])
        
        # 세션 생성
        session_id = security_manager.create_session(
            user['user_id'], 
            ip_address, 
            request.headers.get('User-Agent', '')
        )
        
        return jsonify({
            'message': '로그인 성공',
            'token': token,
            'session_id': session_id,
            'user': {
                'user_id': user['user_id'],
                'roles': user['roles']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"로그인 오류: {e}")
        return jsonify({'error': '로그인 중 오류가 발생했습니다'}), 500

@security_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """사용자 로그아웃"""
    try:
        session_id = request.headers.get('X-Session-ID')
        if session_id:
            security_manager.invalidate_session(session_id)
        
        return jsonify({'message': '로그아웃 성공'}), 200
        
    except Exception as e:
        logger.error(f"로그아웃 오류: {e}")
        return jsonify({'error': '로그아웃 중 오류가 발생했습니다'}), 500

@security_bp.route('/validate-token', methods=['POST'])
def validate_token():
    """토큰 유효성 검증"""
    try:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'valid': False, 'error': '유효하지 않은 토큰 형식입니다'}), 401
        
        token = auth_header[7:]
        payload = security_manager.verify_jwt_token(token)
        
        if not payload:
            return jsonify({'valid': False, 'error': '유효하지 않은 토큰입니다'}), 401
        
        return jsonify({
            'valid': True,
            'user_id': payload['user_id'],
            'roles': payload.get('roles', [])
        }), 200
        
    except Exception as e:
        logger.error(f"토큰 검증 오류: {e}")
        return jsonify({'valid': False, 'error': '토큰 검증 중 오류가 발생했습니다'}), 500

@security_bp.route('/change-password', methods=['POST'])
@require_auth
def change_password():
    """비밀번호 변경"""
    try:
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': '현재 비밀번호와 새 비밀번호가 필요합니다'}), 400
        
        # 비밀번호 강도 검증
        password_validation = security_manager.validate_password_strength(new_password)
        if not password_validation['is_valid']:
            return jsonify({
                'error': '비밀번호가 요구사항을 충족하지 않습니다',
                'errors': password_validation['errors'],
                'warnings': password_validation['warnings']
            }), 400
        
        # 실제 구현에서는 데이터베이스에서 현재 비밀번호를 확인해야 함
        # 여기서는 예시로 간단히 처리
        mock_users = {
            'admin': {'password_hash': security_manager.hash_password('admin123')},
            'user': {'password_hash': security_manager.hash_password('user123')}
        }
        
        if g.user_id not in mock_users:
            return jsonify({'error': '사용자를 찾을 수 없습니다'}), 404
        
        user = mock_users[g.user_id]
        
        # 현재 비밀번호 확인
        if not security_manager.verify_password(current_password, user['password_hash']):
            return jsonify({'error': '현재 비밀번호가 올바르지 않습니다'}), 400
        
        # 새 비밀번호 해시화 (실제로는 데이터베이스에 저장)
        new_password_hash = security_manager.hash_password(new_password)
        
        # 보안 이벤트 기록
        security_manager.log_security_event(
            user_id=g.user_id,
            event_type='password_changed',
            description=f'비밀번호 변경: {g.user_id}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            severity='medium'
        )
        
        return jsonify({
            'message': '비밀번호가 성공적으로 변경되었습니다',
            'password_score': password_validation['score']
        }), 200
        
    except Exception as e:
        logger.error(f"비밀번호 변경 오류: {e}")
        return jsonify({'error': '비밀번호 변경 중 오류가 발생했습니다'}), 500

@security_bp.route('/validate-password', methods=['POST'])
def validate_password():
    """비밀번호 강도 검증"""
    try:
        data = request.get_json()
        password = data.get('password')
        
        if not password:
            return jsonify({'error': '비밀번호가 필요합니다'}), 400
        
        validation_result = security_manager.validate_password_strength(password)
        
        return jsonify({
            'is_valid': validation_result['is_valid'],
            'score': validation_result['score'],
            'errors': validation_result['errors'],
            'warnings': validation_result['warnings']
        }), 200
        
    except Exception as e:
        logger.error(f"비밀번호 검증 오류: {e}")
        return jsonify({'error': '비밀번호 검증 중 오류가 발생했습니다'}), 500

@security_bp.route('/sessions', methods=['GET'])
@require_auth
@require_role('admin')
def get_sessions():
    """활성 세션 조회 (관리자만)"""
    try:
        sessions = []
        for session_id, session in security_manager.active_sessions.items():
            sessions.append({
                'session_id': session.session_id,
                'user_id': session.user_id,
                'created_at': session.created_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'ip_address': session.ip_address,
                'user_agent': session.user_agent,
                'is_active': session.is_active
            })
        
        return jsonify({
            'sessions': sessions,
            'total_count': len(sessions)
        }), 200
        
    except Exception as e:
        logger.error(f"세션 조회 오류: {e}")
        return jsonify({'error': '세션 조회 중 오류가 발생했습니다'}), 500

@security_bp.route('/sessions/<session_id>', methods=['DELETE'])
@require_auth
@require_role('admin')
def invalidate_session(session_id):
    """세션 무효화 (관리자만)"""
    try:
        security_manager.invalidate_session(session_id)
        
        return jsonify({'message': '세션이 무효화되었습니다'}), 200
        
    except Exception as e:
        logger.error(f"세션 무효화 오류: {e}")
        return jsonify({'error': '세션 무효화 중 오류가 발생했습니다'}), 500

@security_bp.route('/events', methods=['GET'])
@require_auth
@require_role('admin')
def get_security_events():
    """보안 이벤트 조회 (관리자만)"""
    try:
        # 쿼리 파라미터
        user_id = request.args.get('user_id')
        event_type = request.args.get('event_type')
        severity = request.args.get('severity')
        limit = int(request.args.get('limit', 100))
        
        events = security_manager.get_security_events(
            user_id=user_id,
            event_type=event_type,
            severity=severity,
            limit=limit
        )
        
        event_list = []
        for event in events:
            event_list.append({
                'event_id': event.event_id,
                'user_id': event.user_id,
                'event_type': event.event_type,
                'description': event.description,
                'ip_address': event.ip_address,
                'user_agent': event.user_agent,
                'timestamp': event.timestamp.isoformat(),
                'severity': event.severity,
                'status': event.status
            })
        
        return jsonify({
            'events': event_list,
            'total_count': len(event_list)
        }), 200
        
    except Exception as e:
        logger.error(f"보안 이벤트 조회 오류: {e}")
        return jsonify({'error': '보안 이벤트 조회 중 오류가 발생했습니다'}), 500

@security_bp.route('/events/<event_id>/status', methods=['PUT'])
@require_auth
@require_role('admin')
def update_event_status(event_id):
    """보안 이벤트 상태 업데이트 (관리자만)"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['pending', 'reviewed', 'resolved']:
            return jsonify({'error': '유효하지 않은 상태입니다'}), 400
        
        # 이벤트 찾기 및 상태 업데이트
        for event in security_manager.security_events:
            if event.event_id == event_id:
                event.status = new_status
                return jsonify({'message': '이벤트 상태가 업데이트되었습니다'}), 200
        
        return jsonify({'error': '이벤트를 찾을 수 없습니다'}), 404
        
    except Exception as e:
        logger.error(f"이벤트 상태 업데이트 오류: {e}")
        return jsonify({'error': '이벤트 상태 업데이트 중 오류가 발생했습니다'}), 500

@security_bp.route('/stats', methods=['GET'])
@require_auth
@require_role('admin')
def get_security_stats():
    """보안 통계 조회 (관리자만)"""
    try:
        stats = security_manager.get_security_stats()
        
        return jsonify({
            'active_sessions': stats['active_sessions'],
            'total_events_24h': stats['total_events_24h'],
            'failed_logins_24h': stats['failed_logins_24h'],
            'locked_accounts': stats['locked_accounts'],
            'security_score': stats['security_score']
        }), 200
        
    except Exception as e:
        logger.error(f"보안 통계 조회 오류: {e}")
        return jsonify({'error': '보안 통계 조회 중 오류가 발생했습니다'}), 500

@security_bp.route('/cleanup', methods=['POST'])
@require_auth
@require_role('admin')
def cleanup_sessions():
    """만료된 세션 정리 (관리자만)"""
    try:
        security_manager.cleanup_expired_sessions()
        
        return jsonify({'message': '만료된 세션이 정리되었습니다'}), 200
        
    except Exception as e:
        logger.error(f"세션 정리 오류: {e}")
        return jsonify({'error': '세션 정리 중 오류가 발생했습니다'}), 500

@security_bp.route('/health', methods=['GET'])
def health_check():
    """보안 시스템 상태 확인"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'security_manager': 'active'
        }), 200
        
    except Exception as e:
        logger.error(f"상태 확인 오류: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# MFA 관련 엔드포인트
@security_bp.route('/mfa/setup/totp', methods=['POST'])
@cross_origin()
def setup_totp():
    """TOTP 설정"""
    try:
        data = request.get_json()
        if not data or 'user_id' not in data or 'email' not in data:
            return jsonify({'error': '사용자 ID와 이메일이 필요합니다'}), 400
        
        user_id = data['user_id']
        email = data['email']
        
        if not mfa_system:
            return jsonify({'error': 'MFA 시스템이 초기화되지 않았습니다'}), 500
        
        # TOTP 설정
        totp_setup = mfa_system.setup_totp(user_id, email)
        
        log_security_event(EventType.MFA_ENABLED, user_id, True, {'method': 'totp'})
        
        return jsonify({
            'status': 'success',
            'message': 'TOTP 설정 완료',
            'data': {
                'secret': totp_setup['secret'],
                'qr_code': totp_setup['qr_code'],
                'backup_codes': totp_setup['backup_codes']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"TOTP 설정 오류: {e}")
        log_security_event(EventType.MFA_ENABLED, data.get('user_id') if data else None, False)
        return jsonify({'error': 'TOTP 설정 중 오류가 발생했습니다'}), 500

@security_bp.route('/mfa/setup/email', methods=['POST'])
@cross_origin()
def setup_email_mfa():
    """이메일 MFA 설정"""
    try:
        data = request.get_json()
        if not data or 'user_id' not in data or 'email' not in data:
            return jsonify({'error': '사용자 ID와 이메일이 필요합니다'}), 400
        
        user_id = data['user_id']
        email = data['email']
        
        if not mfa_system:
            return jsonify({'error': 'MFA 시스템이 초기화되지 않았습니다'}), 500
        
        # 이메일 MFA 설정
        success = mfa_system.setup_email_mfa(user_id, email)
        
        if success:
            log_security_event(EventType.MFA_ENABLED, user_id, True, {'method': 'email'})
            return jsonify({'status': 'success', 'message': '이메일 MFA 설정 완료'}), 200
        else:
            log_security_event(EventType.MFA_ENABLED, user_id, False, {'method': 'email'})
            return jsonify({'error': '이메일 MFA 설정에 실패했습니다'}), 500
        
    except Exception as e:
        logger.error(f"이메일 MFA 설정 오류: {e}")
        log_security_event(EventType.MFA_ENABLED, data.get('user_id') if data else None, False)
        return jsonify({'error': '이메일 MFA 설정 중 오류가 발생했습니다'}), 500

@security_bp.route('/mfa/initiate', methods=['POST'])
@cross_origin()
def initiate_mfa():
    """MFA 시작"""
    try:
        data = request.get_json()
        if not data or 'user_id' not in data or 'method_type' not in data:
            return jsonify({'error': '사용자 ID와 방법 타입이 필요합니다'}), 400
        
        user_id = data['user_id']
        method_type = data['method_type']
        
        if not mfa_system:
            return jsonify({'error': 'MFA 시스템이 초기화되지 않았습니다'}), 500
        
        # MFA 시작
        session_id, code = mfa_system.initiate_mfa(user_id, method_type)
        
        log_security_event(EventType.MFA_ENABLED, user_id, True, {'method': method_type})
        
        return jsonify({
            'status': 'success',
            'message': 'MFA 시작 완료',
            'data': {
                'session_id': session_id,
                'code': code if method_type in ['email', 'sms'] else None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"MFA 시작 오류: {e}")
        log_security_event(EventType.MFA_ENABLED, data.get('user_id') if data else None, False)
        return jsonify({'error': 'MFA 시작 중 오류가 발생했습니다'}), 500

@security_bp.route('/mfa/verify', methods=['POST'])
@cross_origin()
def verify_mfa():
    """MFA 검증"""
    try:
        data = request.get_json()
        if not data or 'session_id' not in data or 'token' not in data:
            return jsonify({'error': '세션 ID와 토큰이 필요합니다'}), 400
        
        session_id = data['session_id']
        token = data['token']
        
        if not mfa_system:
            return jsonify({'error': 'MFA 시스템이 초기화되지 않았습니다'}), 500
        
        # MFA 검증
        verified = mfa_system.verify_mfa_session(session_id, token)
        
        if verified:
            log_security_event(EventType.MFA_ENABLED, None, True, {'session_id': session_id})
            return jsonify({'status': 'success', 'message': 'MFA 검증 성공'}), 200
        else:
            log_security_event(EventType.MFA_FAILED, None, False, {'session_id': session_id})
            return jsonify({'error': 'MFA 검증 실패'}), 401
        
    except Exception as e:
        logger.error(f"MFA 검증 오류: {e}")
        log_security_event(EventType.MFA_FAILED, None, False)
        return jsonify({'error': 'MFA 검증 중 오류가 발생했습니다'}), 500

# 암호화 관련 엔드포인트
@security_bp.route('/encryption/keys/generate', methods=['POST'])
@cross_origin()
def generate_keys():
    """키 생성"""
    try:
        data = request.get_json()
        if not data or 'key_type' not in data:
            return jsonify({'error': '키 타입이 필요합니다'}), 400
        
        key_type = data['key_type']
        key_size = data.get('key_size', 256)
        
        if not key_manager:
            return jsonify({'error': '키 관리자가 초기화되지 않았습니다'}), 500
        
        if key_type == 'symmetric':
            key_id = key_manager.generate_symmetric_key(key_size)
        elif key_type == 'asymmetric':
            private_key_id, public_key_id = key_manager.generate_asymmetric_key_pair(key_size)
            key_id = {'private_key_id': private_key_id, 'public_key_id': public_key_id}
        else:
            return jsonify({'error': '지원하지 않는 키 타입입니다'}), 400
        
        log_security_event(EventType.SYSTEM_ERROR, None, True, {'action': 'key_generation', 'type': key_type})
        
        return jsonify({
            'status': 'success',
            'message': '키 생성 완료',
            'data': {'key_id': key_id}
        }), 200
        
    except Exception as e:
        logger.error(f"키 생성 오류: {e}")
        log_security_event(EventType.SYSTEM_ERROR, None, False, {'action': 'key_generation'})
        return jsonify({'error': '키 생성 중 오류가 발생했습니다'}), 500

@security_bp.route('/encryption/encrypt', methods=['POST'])
@cross_origin()
def encrypt_data():
    """데이터 암호화"""
    try:
        data = request.get_json()
        if not data or 'data' not in data or 'key_id' not in data:
            return jsonify({'error': '데이터와 키 ID가 필요합니다'}), 400
        
        plain_data = data['data']
        key_id = data['key_id']
        encryption_type = data.get('type', 'symmetric')
        
        if not encryption_manager:
            return jsonify({'error': '암호화 관리자가 초기화되지 않았습니다'}), 500
        
        if encryption_type == 'symmetric':
            encrypted_data = encryption_manager.encrypt_symmetric(plain_data, key_id)
        elif encryption_type == 'asymmetric':
            encrypted_data = encryption_manager.encrypt_asymmetric(plain_data, key_id)
        else:
            return jsonify({'error': '지원하지 않는 암호화 타입입니다'}), 400
        
        log_security_event(EventType.DATA_EXPORT, None, True, {'action': 'encryption', 'type': encryption_type})
        
        return jsonify({
            'status': 'success',
            'message': '암호화 완료',
            'data': {
                'encrypted_data': encrypted_data.data.decode('latin1'),
                'algorithm': encrypted_data.algorithm
            }
        }), 200
        
    except Exception as e:
        logger.error(f"암호화 오류: {e}")
        log_security_event(EventType.DATA_EXPORT, None, False, {'action': 'encryption'})
        return jsonify({'error': '암호화 중 오류가 발생했습니다'}), 500

@security_bp.route('/encryption/decrypt', methods=['POST'])
@cross_origin()
def decrypt_data():
    """데이터 복호화"""
    try:
        data = request.get_json()
        if not data or 'encrypted_data' not in data or 'key_id' not in data:
            return jsonify({'error': '암호화된 데이터와 키 ID가 필요합니다'}), 400
        
        encrypted_data_str = data['encrypted_data']
        key_id = data['key_id']
        decryption_type = data.get('type', 'symmetric')
        
        if not encryption_manager:
            return jsonify({'error': '암호화 관리자가 초기화되지 않았습니다'}), 500
        
        # EncryptedData 객체 생성
        from security.encryption_manager import EncryptedData
        encrypted_data = EncryptedData(
            data=encrypted_data_str.encode('latin1'),
            key_id=key_id,
            algorithm='AES-256-GCM' if decryption_type == 'symmetric' else 'RSA-OAEP'
        )
        
        if decryption_type == 'symmetric':
            decrypted_data = encryption_manager.decrypt_symmetric(encrypted_data)
        elif decryption_type == 'asymmetric':
            decrypted_data = encryption_manager.decrypt_asymmetric(encrypted_data, key_id)
        else:
            return jsonify({'error': '지원하지 않는 복호화 타입입니다'}), 400
        
        log_security_event(EventType.DATA_IMPORT, None, True, {'action': 'decryption', 'type': decryption_type})
        
        return jsonify({
            'status': 'success',
            'message': '복호화 완료',
            'data': {'decrypted_data': decrypted_data.decode('utf-8')}
        }), 200
        
    except Exception as e:
        logger.error(f"복호화 오류: {e}")
        log_security_event(EventType.DATA_IMPORT, None, False, {'action': 'decryption'})
        return jsonify({'error': '복호화 중 오류가 발생했습니다'}), 500

# 생체 인증 관련 엔드포인트
@security_bp.route('/biometric/enroll', methods=['POST'])
@cross_origin()
def enroll_biometric():
    """생체 인증 등록"""
    try:
        data = request.get_json()
        if not data or 'user_id' not in data or 'method' not in data or 'biometric_data' not in data:
            return jsonify({'error': '사용자 ID, 방법, 생체 데이터가 필요합니다'}), 400
        
        user_id = data['user_id']
        method = data['method']
        biometric_data = data['biometric_data']
        
        if not biometric_auth:
            return jsonify({'error': '생체 인증 시스템이 초기화되지 않았습니다'}), 500
        
        # 생체 인증 등록
        success = biometric_auth.enroll_biometric(user_id, method, biometric_data)
        
        if success:
            log_security_event(EventType.MFA_ENABLED, user_id, True, {'method': f'biometric_{method}'})
            return jsonify({'status': 'success', 'message': '생체 인증 등록 완료'}), 200
        else:
            log_security_event(EventType.MFA_ENABLED, user_id, False, {'method': f'biometric_{method}'})
            return jsonify({'error': '생체 인증 등록에 실패했습니다'}), 500
        
    except Exception as e:
        logger.error(f"생체 인증 등록 오류: {e}")
        log_security_event(EventType.MFA_ENABLED, data.get('user_id') if data else None, False)
        return jsonify({'error': '생체 인증 등록 중 오류가 발생했습니다'}), 500

@security_bp.route('/biometric/verify', methods=['POST'])
@cross_origin()
def verify_biometric():
    """생체 인증 검증"""
    try:
        data = request.get_json()
        if not data or 'user_id' not in data or 'method' not in data or 'biometric_data' not in data:
            return jsonify({'error': '사용자 ID, 방법, 생체 데이터가 필요합니다'}), 400
        
        user_id = data['user_id']
        method = data['method']
        biometric_data = data['biometric_data']
        
        if not biometric_auth:
            return jsonify({'error': '생체 인증 시스템이 초기화되지 않았습니다'}), 500
        
        # 생체 인증 검증
        verified = biometric_auth.verify_biometric(user_id, method, biometric_data)
        
        if verified:
            log_security_event(EventType.MFA_ENABLED, user_id, True, {'method': f'biometric_{method}'})
            return jsonify({'status': 'success', 'message': '생체 인증 검증 성공'}), 200
        else:
            log_security_event(EventType.MFA_FAILED, user_id, False, {'method': f'biometric_{method}'})
            return jsonify({'error': '생체 인증 검증 실패'}), 401
        
    except Exception as e:
        logger.error(f"생체 인증 검증 오류: {e}")
        log_security_event(EventType.MFA_FAILED, data.get('user_id') if data else None, False)
        return jsonify({'error': '생체 인증 검증 중 오류가 발생했습니다'}), 500

# 감사 및 모니터링 엔드포인트
@security_bp.route('/audit/events', methods=['GET'])
@cross_origin()
def get_audit_events():
    """감사 이벤트 조회"""
    try:
        hours = request.args.get('hours', 24, type=int)
        event_type = request.args.get('event_type')
        user_id = request.args.get('user_id')
        ip_address = request.args.get('ip_address')
        
        if not audit_system:
            return jsonify({'error': '감사 시스템이 초기화되지 않았습니다'}), 500
        
        events = audit_system.get_recent_events(
            minutes=hours * 60,
            event_type=EventType(event_type) if event_type else None,
            user_id=user_id,
            ip_address=ip_address
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'events': [asdict(event) for event in events],
                'total_count': len(events)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"감사 이벤트 조회 오류: {e}")
        return jsonify({'error': '감사 이벤트 조회 중 오류가 발생했습니다'}), 500

@security_bp.route('/audit/alerts', methods=['GET'])
@cross_origin()
def get_security_alerts():
    """보안 알림 조회"""
    try:
        hours = request.args.get('hours', 24, type=int)
        resolved = request.args.get('resolved')
        severity = request.args.get('severity')
        
        if not audit_system:
            return jsonify({'error': '감사 시스템이 초기화되지 않았습니다'}), 500
        
        alerts = audit_system.get_security_alerts(
            hours=hours,
            resolved=bool(resolved) if resolved is not None else None,
            severity=SecurityLevel(severity) if severity else None
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'alerts': [asdict(alert) for alert in alerts],
                'total_count': len(alerts)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"보안 알림 조회 오류: {e}")
        return jsonify({'error': '보안 알림 조회 중 오류가 발생했습니다'}), 500

@security_bp.route('/audit/report', methods=['GET'])
@cross_origin()
def get_security_report():
    """보안 리포트 생성"""
    try:
        hours = request.args.get('hours', 24, type=int)
        
        if not audit_system:
            return jsonify({'error': '감사 시스템이 초기화되지 않았습니다'}), 500
        
        report = audit_system.generate_security_report(hours=hours)
        
        return jsonify({
            'status': 'success',
            'data': report
        }), 200
        
    except Exception as e:
        logger.error(f"보안 리포트 생성 오류: {e}")
        return jsonify({'error': '보안 리포트 생성 중 오류가 발생했습니다'}), 500

@security_bp.route('/audit/alerts/<alert_id>/resolve', methods=['POST'])
@cross_origin()
def resolve_alert(alert_id):
    """알림 해결"""
    try:
        data = request.get_json()
        resolution_notes = data.get('resolution_notes', '') if data else ''
        
        if not audit_system:
            return jsonify({'error': '감사 시스템이 초기화되지 않았습니다'}), 500
        
        success = audit_system.resolve_alert(alert_id, resolution_notes)
        
        if success:
            return jsonify({'status': 'success', 'message': '알림 해결 완료'}), 200
        else:
            return jsonify({'error': '알림 해결에 실패했습니다'}), 500
        
    except Exception as e:
        logger.error(f"알림 해결 오류: {e}")
        return jsonify({'error': '알림 해결 중 오류가 발생했습니다'}), 500

# 시스템 상태 엔드포인트
@security_bp.route('/health', methods=['GET'])
@cross_origin()
def security_health():
    """보안 시스템 상태 확인"""
    try:
        health_status = {
            'mfa_system': mfa_system is not None,
            'key_manager': key_manager is not None,
            'encryption_manager': encryption_manager is not None,
            'audit_system': audit_system is not None,
            'biometric_auth': biometric_auth is not None,
            'timestamp': datetime.now().isoformat()
        }
        
        all_systems_healthy = all(health_status.values()[:-1])  # timestamp 제외
        
        return jsonify({
            'status': 'healthy' if all_systems_healthy else 'unhealthy',
            'data': health_status
        }), 200 if all_systems_healthy else 503
        
    except Exception as e:
        logger.error(f"보안 시스템 상태 확인 오류: {e}")
        return jsonify({'error': '시스템 상태 확인 중 오류가 발생했습니다'}), 500

# 초기화
init_security_systems()
