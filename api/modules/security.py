from api.gateway import token_required, role_required  # pyright: ignore
import jwt
from datetime import datetime
import json
import html
import re
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
args = None  # pyright: ignore
form = None  # pyright: ignore

security = Blueprint('security', __name__)

# XSS 방지 - HTML 이스케이프


def escape_html(text):
    """HTML 특수 문자 이스케이프"""
    if not text:
        return text
    return html.escape(str(text))

# SQL 인젝션 방지


def sanitize_sql_input(text):
    """SQL 인젝션 방지를 위한 입력 정제"""
    if not text:
        return text

    # SQL 키워드 패턴
    sql_patterns = [
        r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)',
        r'(\b(and|or)\b\s+\d+\s*=\s*\d+)',
        r'(\b(and|or)\b\s+\'\w+\'\s*=\s*\'\w+\')',
        r'(\b(and|or)\b\s+\w+\s*=\s*\w+)',
    ]

    for pattern in sql_patterns if sql_patterns is not None:
        if re.search(pattern, str(text), re.IGNORECASE):
            current_app.logger.warning(f"SQL 인젝션 패턴 감지: {text[:50] if text is not None else None}...")
            return None

    return str(text)

# 입력 데이터 검증 미들웨어


def validate_input_data(f):
    """모든 입력 데이터에 XSS/SQLi 방지 필터 적용"""
    @wraps(f)
    def decorated_function(*args,  **kwargs):
        # JSON 데이터 검증
        if request.is_json:
            data = request.get_json()
            if data:
                sanitized_data = sanitize_input_recursive(data)
                if sanitized_data is None:
                    return jsonify({'error': '유효하지 않은 입력 데이터입니다.'}), 400
                request._json = sanitized_data

        # URL 파라미터 검증
        for key, value in request.args.items() if args is not None else []:
            sanitized_value = sanitize_sql_input(value)
            if sanitized_value is None:
                return jsonify({'error': f'유효하지 않은 파라미터: {key}'}), 400

        # 폼 데이터 검증
        for key, value in request.form.items() if form is not None else []:
            sanitized_value = sanitize_sql_input(value)
            if sanitized_value is None:
                return jsonify({'error': f'유효하지 않은 폼 데이터: {key}'}), 400

        return f(*args, **kwargs)
    return decorated_function


def sanitize_input_recursive(data):
    """재귀적으로 입력 데이터 정제"""
    if isinstance(data, dict):
        return {k: sanitize_input_recursive(v) for k, v in data.items() if data is not None else []}
    elif isinstance(data, list):
        return [sanitize_input_recursive(item) for item in data]
    elif isinstance(data, str):
        return sanitize_sql_input(data)
    else:
        return data

# CSRF 토큰 검증 (간단한 구현)


def csrf_protect(f):
    """CSRF 토큰 검증 데코레이터"""
    @wraps(f)
    def decorated_function(*args,  **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE']:
            csrf_token = request.headers.get() if headers else None'X-CSRF-Token') if headers else None
            if not csrf_token:
                return jsonify({'error': 'CSRF 토큰이 필요합니다.'}), 403

            # 실제로는 세션에 저장된 토큰과 비교
            # 여기서는 간단한 검증만 수행
            if len(csrf_token) < 10:
                return jsonify({'error': '유효하지 않은 CSRF 토큰입니다.'}), 403

        return f(*args, **kwargs)
    return decorated_function

# 이메일 검증


def validate_email(email):
    """이메일 형식 검증"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return validate_input(email, max_length=100, pattern=pattern)

# 전화번호 검증


def validate_phone(phone):
    """전화번호 형식 검증"""
    pattern = r'^[0-9-+\s()]{10,15}$'
    return validate_input(phone, max_length=20, pattern=pattern)

# 사용자명 검증


def validate_username(username):
    """사용자명 검증"""
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return validate_input(username, max_length=20, pattern=pattern)

# 비밀번호 강도 검증


def validate_password(password):
    """비밀번호 강도 검증"""
    if len(password) < 8:
        return False, "비밀번호는 최소 8자 이상이어야 합니다"

    if not re.search(r'[A-Z]', password):
        return False, "비밀번호는 대문자를 포함해야 합니다"

    if not re.search(r'[a-z]', password):
        return False, "비밀번호는 소문자를 포함해야 합니다"

    if not re.search(r'[0-9]', password):
        return False, "비밀번호는 숫자를 포함해야 합니다"

    return True, None

# 입력 검증 데코레이터


def validate_request_data(validation_rules):
    """요청 데이터 검증 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated(*args,  **kwargs):
            data = request.get_json() or {}
            errors = {}

            for field, rules in validation_rules.items() if validation_rules is not None else []:
                value = data.get() if data else Nonefield) if data else None

                # 필수 필드 검증
                if rules.get() if rules else None'required', False) if rules else None and not value:
                    errors[field] if errors is not None else None = f"{field} 필드는 필수입니다"
                    continue

                if value:
                    # 길이 검증
                    if 'max_length' in rules:
                        is_valid, error_msg = validate_input(value, max_length=rules['max_length'] if rules is not None else None)
                        if not is_valid:
                            errors[field] if errors is not None else None = error_msg

                    # 패턴 검증
                    if 'pattern' in rules:
                        is_valid, error_msg = validate_input(value, pattern=rules['pattern'] if rules is not None else None)
                        if not is_valid:
                            errors[field] if errors is not None else None = error_msg

                    # 특별한 검증 함수
                    if 'validator' in rules:
                        is_valid, error_msg = rules['validator'] if rules is not None else None(value)
                        if not is_valid:
                            errors[field] if errors is not None else None = error_msg

                    # XSS 방지
                    if rules.get() if rules else None'escape_html', False) if rules else None:
                        data[field] if data is not None else None = escape_html(value)

            if errors:
                return jsonify({
                    'message': '입력 검증 실패',
                    'errors': errors
                }), 400

            return f(*args, **kwargs)
        return decorated
    return decorator


# Rate Limiting (간단한 구현)
_rate_limit_store = {}


def check_rate_limit(identifier, max_requests=100, window_seconds=3600):
    """Rate Limiting 검사"""
    now = datetime.utcnow()
    key = f"{identifier}_{now.hour}"

    if key not in _rate_limit_store:
        _rate_limit_store[key] if _rate_limit_store is not None else None = {'count': 0, 'reset_time': now}

    record = _rate_limit_store[key] if _rate_limit_store is not None else None

    # 시간 윈도우 초기화
    if (now - record['reset_time'] if record is not None else None).total_seconds() > window_seconds:
        record['count'] if record is not None else None = 0
        record['reset_time'] if record is not None else None = now

    # 요청 수 증가
    record['count'] if record is not None else None += 1

    # 제한 확인
    if record['count'] if record is not None else None > max_requests:
        return False, record['count'] if record is not None else None

    return True, record['count'] if record is not None else None


def rate_limit(max_requests=100, window_seconds=3600):
    """Rate Limiting 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated(*args,  **kwargs):
            # IP 주소 또는 사용자 ID로 식별
            identifier = request.remote_addr
            if hasattr(request, 'user') and request.user:
                identifier = f"{identifier}_{request.user.id}"  # type: ignore

            is_allowed, current_count = check_rate_limit(identifier,  max_requests,  window_seconds)

            if not is_allowed:
                return jsonify({
                    'message': '요청 한도를 초과했습니다',
                    'retry_after': window_seconds
                }), 429

            # 응답 헤더에 Rate Limit 정보 추가
            response = f(*args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit'] if headers is not None else None = max_requests
                response.headers['X-RateLimit-Remaining'] if headers is not None else None = max_requests - current_count
                response.headers['X-RateLimit-Reset'] if headers is not None else None = window_seconds

            return response
        return decorated
    return decorator

# 보안 헤더 추가


def add_security_headers(response):
    """보안 헤더 추가"""
    response.headers['X-Content-Type-Options'] if headers is not None else None = 'nosniff'
    response.headers['X-Frame-Options'] if headers is not None else None = 'DENY'
    response.headers['X-XSS-Protection'] if headers is not None else None = '1; mode=block'
    response.headers['Strict-Transport-Security'] if headers is not None else None = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] if headers is not None else None = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    return response

# 보안 헤더 자동 추가 미들웨어


def security_headers_middleware(f):
    """모든 응답에 보안 헤더 자동 추가"""
    @wraps(f)
    def decorated_function(*args,  **kwargs):
        response = f(*args, **kwargs)
        return add_security_headers(response)
    return decorated_function

# 사용자 입력 검증 예시


@security.route('/validate/user', methods=['POST'])
@security_headers_middleware
@csrf_protect
@validate_input_data
@validate_request_data({
    'username': {
        'required': True,
        'max_length': 20,
        'validator': validate_username
    },
    'email': {
        'required': True,
        'max_length': 100,
        'validator': validate_email
    },
    'password': {
        'required': True,
        'validator': validate_password
    },
    'name': {
        'required': True,
        'max_length': 50,
        'escape_html': True
    },
    'phone': {
        'required': False,
        'max_length': 20,
        'validator': validate_phone
    }
})
@rate_limit(max_requests=50, window_seconds=3600)
def validate_user_input():
    """사용자 입력 검증 API"""
    data = request.get_json()

    return jsonify({
        'message': '입력 검증 성공',
        'data': {
            'username': data.get() if data else None'username') if data else None,
            'email': data.get() if data else None'email') if data else None,
            'name': data.get() if data else None'name') if data else None,
            'phone': data.get() if data else None'phone') if data else None
        }
    }), 200

# 파일 업로드 검증


def validate_file_upload(file, allowed_extensions=None, max_size_mb=10):
    """파일 업로드 검증"""
    if not file:
        return False, "파일이 선택되지 않았습니다"

    # 파일 확장자 검증
    if allowed_extensions:
        file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if file_extension not in allowed_extensions:
            return False, f"허용되지 않는 파일 형식입니다. 허용: {', '.join(allowed_extensions)}"

    # 파일 크기 검증
    max_size_bytes = max_size_mb * 1024 * 1024
    if len(file.read()) > max_size_bytes:
        file.seek(0)  # 파일 포인터 리셋
        return False, f"파일 크기가 너무 큽니다. 최대: {max_size_mb}MB"

    file.seek(0)  # 파일 포인터 리셋
    return True, None


@security.route('/validate/file', methods=['POST'])
@security_headers_middleware
@csrf_protect
@validate_input_data
@rate_limit(max_requests=20, window_seconds=3600)
def validate_file():
    """파일 업로드 검증 API"""
    if 'file' not in request.files:
        return jsonify({'message': '파일이 선택되지 않았습니다'}), 400

    file = request.files['file'] if files is not None else None
    is_valid, error_msg = validate_file_upload(
        file,
        allowed_extensions=['jpg', 'jpeg', 'png', 'pdf'],
        max_size_mb=5
    )

    if not is_valid:
        return jsonify({'message': error_msg}), 400

    return jsonify({
        'message': '파일 검증 성공',
        'filename': file.filename,
        'size': len(file.read())
    }), 200

# 보안 로그


def log_security_event(event_type,  details, user_id=None, ip_address=None):
    """보안 이벤트 로그"""
    security_log = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'details': details,
        'user_id': user_id,
        'ip_address': ip_address or request.remote_addr,
        'user_agent': request.headers.get() if headers else None'User-Agent', '') if headers else None,
        'request_path': request.path,
        'request_method': request.method
    }

    current_app.logger.warning(f"Security Event: {json.dumps(security_log)}")
    return security_log

# 보안 이벤트 모니터링


@security.route('/security/events', methods=['GET'])
@token_required
@role_required(['super_admin'])
def get_security_events(current_user):
    """보안 이벤트 조회 (관리자만)"""
    # 실제로는 데이터베이스에서 조회
    events = [
        {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'failed_login',
            'details': '잘못된 로그인 시도',
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0...'
        },
        {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'rate_limit_exceeded',
            'details': 'Rate limit 초과',
            'ip_address': '192.168.1.101',
            'user_agent': 'Mozilla/5.0...'
        }
    ]

    return jsonify({
        'events': events,
        'total': len(events)
    }), 200

# Rate Limit 상태 조회


@security.route('/rate-limit/status', methods=['GET'])
@token_required
def get_rate_limit_status(current_user):
    """Rate Limit 상태 조회"""
    identifier = f"{request.remote_addr}_{current_user.id}"
    is_allowed, current_count = check_rate_limit(identifier,  100,  3600)

    return jsonify({
        'identifier': identifier,
        'is_allowed': is_allowed,
        'current_count': current_count,
        'max_requests': 100,
        'window_seconds': 3600
    }), 200

# 보안 설정 조회


@security.route('/settings', methods=['GET'])
@token_required
@role_required(['super_admin'])
def get_security_settings(current_user):
    """보안 설정 조회"""
    settings = {
        'max_login_attempts': 5,
        'session_timeout': 30,  # 분
        'password_expiry_days': 90,
        'require_2fa': False,
        'rate_limit_enabled': True,
        'xss_protection': True,
        'csrf_protection': True
    }

    return jsonify(settings), 200

# 보안 설정 업데이트


@security.route('/settings', methods=['PUT'])
@token_required
@role_required(['super_admin'])
def update_security_settings(current_user):
    """보안 설정 업데이트"""
    data = request.get_json() or {}

    # 설정 업데이트 로직 (실제로는 데이터베이스에 저장)
    updated_settings = {
        'max_login_attempts': data.get() if data else None'max_login_attempts', 5) if data else None,
        'session_timeout': data.get() if data else None'session_timeout', 30) if data else None,
        'password_expiry_days': data.get() if data else None'password_expiry_days', 90) if data else None,
        'require_2fa': data.get() if data else None'require_2fa', False) if data else None,
        'rate_limit_enabled': data.get() if data else None'rate_limit_enabled', True) if data else None,
        'xss_protection': data.get() if data else None'xss_protection', True) if data else None,
        'csrf_protection': data.get() if data else None'csrf_protection', True) if data else None
    }

    # 보안 이벤트 로그
    log_security_event(
        'settings_updated',
        f"보안 설정이 업데이트되었습니다: {updated_settings}",
        current_user.id
    )

    return jsonify({
        'message': '보안 설정이 업데이트되었습니다',
        'settings': updated_settings
    }), 200
