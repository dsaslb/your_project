"""
보안 API 엔드포인트
엔터프라이즈급 보안 기능을 위한 REST API
"""

from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from datetime import datetime, timedelta
import logging
import traceback
import secrets
import json
from typing import Dict, Any, Optional

# 보안 모듈 임포트
from security.multi_factor_auth import MultiFactorAuth, BiometricAuth
from security.encryption_manager import KeyManager, EncryptionManager
from security.audit_system import AuditSystem, AuditEvent, EventType, SecurityLevel

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
