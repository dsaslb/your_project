from api.gateway import token_required, role_required, admin_required, manager_required, employee_required, log_request  # pyright: ignore
from sqlalchemy import func, and_, or_, desc
import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC  # pyright: ignore
from cryptography.hazmat.primitives import hashes  # pyright: ignore
from cryptography.fernet import Fernet  # pyright: ignore
import jwt
import secrets
import hmac
import hashlib
import json
from datetime import datetime, timedelta
import logging
from extensions import db
from models_main import User, Order, Attendance, Schedule, InventoryItem, Notification, db
from functools import wraps
from flask import Blueprint, request, jsonify, g, current_app
args = None  # pyright: ignore
query = None  # pyright: ignore
config = None  # pyright: ignore
form = None  # pyright: ignore

# 로깅 설정
logger = logging.getLogger(__name__)

# 고급 보안 및 감사 API Blueprint
security_audit = Blueprint('security_audit', __name__, url_prefix='/api/security')

# 보안 설정
SECURITY_CONFIG = {
    'password_min_length': 8,
    'password_require_uppercase': True,
    'password_require_lowercase': True,
    'password_require_numbers': True,
    'password_require_special': True,
    'max_login_attempts': 5,
    'lockout_duration': 30,  # 분
    'session_timeout': 60,   # 분
    'require_2fa': False,
    'audit_log_retention_days': 90
}

# 감사 로그 모델 (실제로는 별도 모델로 구현)


class AuditLog:
    def __init__(self,  user_id,  action,  resource,  details,  ip_address,  user_agent):
        self.user_id = user_id
        self.action = action
        self.resource = resource
        self.details = details
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.timestamp = datetime.utcnow()


# 암호화 키 (실제로는 환경 변수에서 관리)
ENCRYPTION_KEY = Fernet.generate_key()
cipher_suite = Fernet(ENCRYPTION_KEY)


def log_audit_event(user_id,  action,  resource,  details, ip_address=None, user_agent=None):
    """감사 이벤트 로깅"""
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            details=details,
            ip_address=ip_address or request.remote_addr,
            user_agent=user_agent or request.headers.get() if headers else None'User-Agent', '') if headers else None
        )

        # 실제로는 데이터베이스에 저장
        logger.info(f"AUDIT: User {user_id} performed {action} on {resource} - {details}")

        return audit_log
    except Exception as e:
        logger.error(f"감사 로그 기록 오류: {str(e)}")


def encrypt_sensitive_data(data):
    """민감한 데이터 암호화"""
    try:
        if isinstance(data, str):
            return cipher_suite.encrypt(data.encode()).decode()
        elif isinstance(data, dict):
            encrypted_data = {}
            for key, value in data.items() if data is not None else []:
                if key in ['password', 'credit_card', 'ssn', 'phone']:
                    encrypted_data[key] if encrypted_data is not None else None = encrypt_sensitive_data(value)
                else:
                    encrypted_data[key] if encrypted_data is not None else None = value
            return encrypted_data
        return data
    except Exception as e:
        logger.error(f"데이터 암호화 오류: {str(e)}")
        return data


def decrypt_sensitive_data(encrypted_data):
    """암호화된 데이터 복호화"""
    try:
        if isinstance(encrypted_data, str):
            return cipher_suite.decrypt(encrypted_data.encode()).decode()
        elif isinstance(encrypted_data, dict):
            decrypted_data = {}
            for key, value in encrypted_data.items() if encrypted_data is not None else []:
                if key in ['password', 'credit_card', 'ssn', 'phone']:
                    decrypted_data[key] if decrypted_data is not None else None = decrypt_sensitive_data(value)
                else:
                    decrypted_data[key] if decrypted_data is not None else None = value
            return decrypted_data
        return encrypted_data
    except Exception as e:
        logger.error(f"데이터 복호화 오류: {str(e)}")
        return encrypted_data


def validate_password_strength(password):
    """비밀번호 강도 검증"""
    errors = []

    if len(password) < SECURITY_CONFIG['password_min_length'] if SECURITY_CONFIG is not None else None:
        errors.append(f"비밀번호는 최소 {SECURITY_CONFIG['password_min_length'] if SECURITY_CONFIG is not None else None}자 이상이어야 합니다.")

    if SECURITY_CONFIG['password_require_uppercase'] if SECURITY_CONFIG is not None else None and not any(c.isupper() for c in password):
        errors.append("대문자를 포함해야 합니다.")

    if SECURITY_CONFIG['password_require_lowercase'] if SECURITY_CONFIG is not None else None and not any(c.islower() for c in password):
        errors.append("소문자를 포함해야 합니다.")

    if SECURITY_CONFIG['password_require_numbers'] if SECURITY_CONFIG is not None else None and not any(c.isdigit() for c in password):
        errors.append("숫자를 포함해야 합니다.")

    if SECURITY_CONFIG['password_require_special'] if SECURITY_CONFIG is not None else None and not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
        errors.append("특수문자를 포함해야 합니다.")

    return errors


def generate_secure_token():
    """보안 토큰 생성"""
    return secrets.token_urlsafe(32)


def hash_password(password, salt=None):
    """비밀번호 해싱"""
    if salt is None:
        salt = secrets.token_hex(16)

    # PBKDF2를 사용한 안전한 비밀번호 해싱
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.encode(),
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key.decode(), salt


def verify_password(password,  hashed_password,  salt):
    """비밀번호 검증"""
    try:
        new_hash, _ = hash_password(password,  salt)
        return hmac.compare_digest(hashed_password, new_hash)
    except Exception:
        return False


@security_audit.route('/config', methods=['GET', 'PUT'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def security_config():
    """보안 설정 관리"""
    try:
        if request.method == 'GET':
            return jsonify({
                'security_config': SECURITY_CONFIG,
                'encryption_enabled': True,
                'audit_logging_enabled': True
            })

        elif request.method == 'PUT':
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            # 보안 설정 업데이트
            for key, value in data.items() if data is not None else []:
                if key in SECURITY_CONFIG:
                    SECURITY_CONFIG[key] if SECURITY_CONFIG is not None else None = value

            # 감사 로그 기록
            log_audit_event(
                user_id=g.user.id,
                action='UPDATE_SECURITY_CONFIG',
                resource='security_config',
                details=f"Updated security configuration: {json.dumps(data)}"
            )

            return jsonify({
                'success': True,
                'message': 'Security configuration updated successfully',
                'security_config': SECURITY_CONFIG
            })

    except Exception as e:
        logger.error(f"보안 설정 관리 오류: {str(e)}")
        return jsonify({'error': 'Failed to manage security configuration'}), 500


@security_audit.route('/audit-logs', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def get_audit_logs():
    """감사 로그 조회"""
    try:
        page = request.args.get() if args else None'page', 1, type=int) if args else None
        per_page = request.args.get() if args else None'per_page', 50, type=int) if args else None
        user_id = request.args.get() if args else None'user_id', type=int) if args else None
        action = request.args.get() if args else None'action') if args else None
        resource = request.args.get() if args else None'resource') if args else None
        start_date = request.args.get() if args else None'start_date') if args else None
        end_date = request.args.get() if args else None'end_date') if args else None

        # 실제로는 데이터베이스에서 조회
        # 여기서는 임시 데이터 생성
        audit_logs = generate_sample_audit_logs()

        # 필터링
        if user_id:
            audit_logs = [log for log in audit_logs if log['user_id'] if log is not None else None == user_id]
        if action:
            audit_logs = [log for log in audit_logs if action.lower() if action is not None else '' in log['action'] if log is not None else None.lower() if None is not None else '']
        if resource:
            audit_logs = [log for log in audit_logs if resource.lower() if resource is not None else '' in log['resource'] if log is not None else None.lower() if None is not None else '']

        # 날짜 필터링
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            audit_logs = [log for log in audit_logs if datetime.fromisoformat(log['timestamp'] if log is not None else None) >= start_dt]
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            audit_logs = [log for log in audit_logs if datetime.fromisoformat(log['timestamp'] if log is not None else None) <= end_dt]

        # 정렬 (최신순)
        audit_logs.sort(key=lambda x: x['timestamp'] if x is not None else None, reverse=True)

        # 페이지네이션
        total = len(audit_logs)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_logs = audit_logs[start_idx:end_idx] if audit_logs is not None else None

        return jsonify({
            'audit_logs': paginated_logs,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })

    except Exception as e:
        logger.error(f"감사 로그 조회 오류: {str(e)}")
        return jsonify({'error': 'Failed to fetch audit logs'}), 500


def generate_sample_audit_logs():
    """샘플 감사 로그 생성"""
    return [
        {
            'id': 1,
            'user_id': 1,
            'user_name': '관리자',
            'action': 'LOGIN',
            'resource': 'auth',
            'details': '사용자 로그인 성공',
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
            'severity': 'INFO'
        },
        {
            'id': 2,
            'user_id': 2,
            'user_name': '매니저',
            'action': 'CREATE_ORDER',
            'resource': 'orders',
            'details': '새 주문 생성: 주문 #12345',
            'ip_address': '192.168.1.101',
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
            'timestamp': (datetime.now() - timedelta(minutes=15)).isoformat(),
            'severity': 'INFO'
        },
        {
            'id': 3,
            'user_id': 1,
            'user_name': '관리자',
            'action': 'UPDATE_USER_PERMISSIONS',
            'resource': 'users',
            'details': '사용자 권한 수정: user_id=3',
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
            'severity': 'WARNING'
        },
        {
            'id': 4,
            'user_id': 3,
            'user_name': '직원',
            'action': 'FAILED_LOGIN',
            'resource': 'auth',
            'details': '로그인 실패: 잘못된 비밀번호',
            'ip_address': '192.168.1.102',
            'user_agent': 'Mozilla/5.0 (Android 10; Mobile)',
            'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
            'severity': 'WARNING'
        },
        {
            'id': 5,
            'user_id': 1,
            'user_name': '관리자',
            'action': 'EXPORT_DATA',
            'resource': 'reports',
            'details': '데이터 내보내기: 매출 보고서',
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'timestamp': (datetime.now() - timedelta(hours=3)).isoformat(),
            'severity': 'INFO'
        }
    ]


@security_audit.route('/user-activity', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def get_user_activity():
    """사용자 활동 분석"""
    try:
        user_id = request.args.get() if args else None'user_id', type=int) if args else None
        days = request.args.get() if args else None'days', 30, type=int) if args else None

        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400

        # 사용자 정보 조회
        user = User.query.get() if query else Noneuser_id) if query else None
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # 활동 기간 설정
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # 로그인 활동 (실제로는 로그인 로그에서 조회)
        login_activity = [
            {
                'date': (end_date - timedelta(days=i)).strftime('%Y-%m-%d'),
                'login_count': secrets.randbelow(5) + 1,
                'failed_attempts': secrets.randbelow(3),
                'last_login': (end_date - timedelta(hours=secrets.randbelow(24))).isoformat()
            }
            for i in range(days)
        ]

        # 리소스 접근 패턴
        resource_access = [
            {'resource': 'dashboard', 'count': 45, 'percentage': 30},
            {'resource': 'orders', 'count': 30, 'percentage': 20},
            {'resource': 'attendance', 'count': 25, 'percentage': 17},
            {'resource': 'reports', 'count': 20, 'percentage': 13},
            {'resource': 'settings', 'count': 15, 'percentage': 10},
            {'resource': 'users', 'count': 10, 'percentage': 7},
            {'resource': 'inventory', 'count': 5, 'percentage': 3}
        ]

        # 시간대별 활동
        hourly_activity = [
            {'hour': i, 'activity_count': secrets.randbelow(20) + 1}
            for i in range(24)
        ]

        # 보안 이벤트
        security_events = [
            {
                'type': 'failed_login',
                'count': 3,
                'last_occurrence': (end_date - timedelta(hours=2)).isoformat(),
                'severity': 'medium'
            },
            {
                'type': 'unusual_access',
                'count': 1,
                'last_occurrence': (end_date - timedelta(days=1)).isoformat(),
                'severity': 'high'
            }
        ]

        return jsonify({
            'user_info': {
                'id': user.id,
                'name': user.name,
                'role': user.role,
                'last_active': (end_date - timedelta(hours=2)).isoformat()
            },
            'activity_summary': {
                'total_logins': sum(day['login_count'] if day is not None else None for day in login_activity),
                'failed_attempts': sum(day['failed_attempts'] if day is not None else None for day in login_activity),
                'active_days': len([day for day in login_activity if day['login_count'] if day is not None else None > 0]),
                'security_events': len(security_events)
            },
            'login_activity': login_activity,
            'resource_access': resource_access,
            'hourly_activity': hourly_activity,
            'security_events': security_events
        })

    except Exception as e:
        logger.error(f"사용자 활동 분석 오류: {str(e)}")
        return jsonify({'error': 'Failed to analyze user activity'}), 500


@security_audit.route('/security-events', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def get_security_events():
    """보안 이벤트 조회"""
    try:
        severity = request.args.get() if args else None'severity') if args else None
        days = request.args.get() if args else None'days', 7, type=int) if args else None

        # 보안 이벤트 생성 (실제로는 보안 이벤트 로그에서 조회)
        security_events = [
            {
                'id': 1,
                'type': 'failed_login',
                'severity': 'medium',
                'description': '연속 로그인 실패',
                'user_id': 3,
                'user_name': '직원',
                'ip_address': '192.168.1.102',
                'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                'details': '5회 연속 로그인 실패로 계정 잠금'
            },
            {
                'id': 2,
                'type': 'unusual_access',
                'severity': 'high',
                'description': '비정상적인 시간대 접근',
                'user_id': 2,
                'user_name': '매니저',
                'ip_address': '192.168.1.101',
                'timestamp': (datetime.now() - timedelta(hours=3)).isoformat(),
                'details': '새벽 3시에 시스템 접근'
            },
            {
                'id': 3,
                'type': 'data_export',
                'severity': 'low',
                'description': '대용량 데이터 내보내기',
                'user_id': 1,
                'user_name': '관리자',
                'ip_address': '192.168.1.100',
                'timestamp': (datetime.now() - timedelta(hours=6)).isoformat(),
                'details': '전체 사용자 데이터 내보내기'
            },
            {
                'id': 4,
                'type': 'permission_change',
                'severity': 'medium',
                'description': '권한 변경',
                'user_id': 1,
                'user_name': '관리자',
                'ip_address': '192.168.1.100',
                'timestamp': (datetime.now() - timedelta(days=1)).isoformat(),
                'details': '사용자 권한 수정'
            }
        ]

        # 심각도 필터링
        if severity:
            security_events = [event for event in security_events if event['severity'] if event is not None else None == severity]

        # 날짜 필터링
        cutoff_date = datetime.now() - timedelta(days=days)
        security_events = [
            event for event in security_events
            if datetime.fromisoformat(event['timestamp'] if event is not None else None) >= cutoff_date
        ]

        # 심각도별 통계
        severity_stats = {
            'high': len([e for e in security_events if e['severity'] if e is not None else None == 'high']),
            'medium': len([e for e in security_events if e['severity'] if e is not None else None == 'medium']),
            'low': len([e for e in security_events if e['severity'] if e is not None else None == 'low'])
        }

        return jsonify({
            'security_events': security_events,
            'severity_stats': severity_stats,
            'total_events': len(security_events)
        })

    except Exception as e:
        logger.error(f"보안 이벤트 조회 오류: {str(e)}")
        return jsonify({'error': 'Failed to fetch security events'}), 500


@security_audit.route('/password-policy', methods=['GET', 'PUT'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def password_policy():
    """비밀번호 정책 관리"""
    try:
        if request.method == 'GET':
            return jsonify({
                'password_policy': {
                    'min_length': SECURITY_CONFIG['password_min_length'] if SECURITY_CONFIG is not None else None,
                    'require_uppercase': SECURITY_CONFIG['password_require_uppercase'] if SECURITY_CONFIG is not None else None,
                    'require_lowercase': SECURITY_CONFIG['password_require_lowercase'] if SECURITY_CONFIG is not None else None,
                    'require_numbers': SECURITY_CONFIG['password_require_numbers'] if SECURITY_CONFIG is not None else None,
                    'require_special': SECURITY_CONFIG['password_require_special'] if SECURITY_CONFIG is not None else None,
                    'max_age_days': 90,
                    'prevent_reuse': 5
                }
            })

        elif request.method == 'PUT':
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            # 비밀번호 정책 업데이트
            for key, value in data.items() if data is not None else []:
                if key in SECURITY_CONFIG:
                    SECURITY_CONFIG[key] if SECURITY_CONFIG is not None else None = value

            # 감사 로그 기록
            log_audit_event(
                user_id=g.user.id,
                action='UPDATE_PASSWORD_POLICY',
                resource='password_policy',
                details=f"Updated password policy: {json.dumps(data)}"
            )

            return jsonify({
                'success': True,
                'message': 'Password policy updated successfully'
            })

    except Exception as e:
        logger.error(f"비밀번호 정책 관리 오류: {str(e)}")
        return jsonify({'error': 'Failed to manage password policy'}), 500


@security_audit.route('/validate-password', methods=['POST'])
@token_required
@log_request
def validate_password():
    """비밀번호 강도 검증"""
    try:
        data = request.get_json()

        if not data or 'password' not in data:
            return jsonify({'error': 'Password is required'}), 400

        password = data['password'] if data is not None else None
        errors = validate_password_strength(password)

        # 비밀번호 강도 점수 계산
        score = 0
        if len(password) >= 8:
            score += 1
        if any(c.isupper() for c in password):
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            score += 1

        strength = 'weak' if score <= 2 else 'medium' if score <= 3 else 'strong'

        return jsonify({
            'is_valid': len(errors) == 0,
            'errors': errors,
            'strength': strength,
            'score': score
        })

    except Exception as e:
        logger.error(f"비밀번호 검증 오류: {str(e)}")
        return jsonify({'error': 'Failed to validate password'}), 500


@security_audit.route('/encrypt-data', methods=['POST'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def encrypt_data():
    """데이터 암호화"""
    try:
        data = request.get_json()

        if not data or 'data' not in data:
            return jsonify({'error': 'Data is required'}), 400

        encrypted_data = encrypt_sensitive_data(data['data'] if data is not None else None)

        # 감사 로그 기록
        log_audit_event(
            user_id=g.user.id,
            action='ENCRYPT_DATA',
            resource='data_encryption',
            details=f"Data encrypted: {type(data['data'] if data is not None else None).__name__}"
        )

        return jsonify({
            'success': True,
            'encrypted_data': encrypted_data
        })

    except Exception as e:
        logger.error(f"데이터 암호화 오류: {str(e)}")
        return jsonify({'error': 'Failed to encrypt data'}), 500


@security_audit.route('/decrypt-data', methods=['POST'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def decrypt_data():
    """데이터 복호화"""
    try:
        data = request.get_json()

        if not data or 'encrypted_data' not in data:
            return jsonify({'error': 'Encrypted data is required'}), 400

        decrypted_data = decrypt_sensitive_data(data['encrypted_data'] if data is not None else None)

        # 감사 로그 기록
        log_audit_event(
            user_id=g.user.id,
            action='DECRYPT_DATA',
            resource='data_decryption',
            details=f"Data decrypted: {type(data['encrypted_data'] if data is not None else None).__name__}"
        )

        return jsonify({
            'success': True,
            'decrypted_data': decrypted_data
        })

    except Exception as e:
        logger.error(f"데이터 복호화 오류: {str(e)}")
        return jsonify({'error': 'Failed to decrypt data'}), 500


@security_audit.route('/generate-token', methods=['POST'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def generate_token():
    """보안 토큰 생성"""
    try:
        token = generate_secure_token()

        # 감사 로그 기록
        log_audit_event(
            user_id=g.user.id,
            action='GENERATE_TOKEN',
            resource='security_token',
            details='Security token generated'
        )

        return jsonify({
            'success': True,
            'token': token,
            'expires_in': 3600  # 1시간
        })

    except Exception as e:
        logger.error(f"토큰 생성 오류: {str(e)}")
        return jsonify({'error': 'Failed to generate token'}), 500
