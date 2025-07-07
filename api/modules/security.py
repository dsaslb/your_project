from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import re
import html
import json
from datetime import datetime
import jwt
from api.gateway import token_required, role_required

security = Blueprint('security', __name__)

# XSS 방지 - HTML 이스케이프
def escape_html(text):
    """HTML 특수 문자 이스케이프"""
    if not text:
        return text
    return html.escape(str(text))

# SQL 인젝션 방지 - 입력 검증
def validate_input(text, max_length=255, pattern=None):
    """입력 검증"""
    if not text:
        return False, "입력값이 비어있습니다"
    
    if len(str(text)) > max_length:
        return False, f"입력값이 너무 깁니다 (최대 {max_length}자)"
    
    if pattern and not re.match(pattern, str(text)):
        return False, "입력 형식이 올바르지 않습니다"
    
    return True, None

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
        def decorated(*args, **kwargs):
            data = request.get_json() or {}
            errors = {}
            
            for field, rules in validation_rules.items():
                value = data.get(field)
                
                # 필수 필드 검증
                if rules.get('required', False) and not value:
                    errors[field] = f"{field} 필드는 필수입니다"
                    continue
                
                if value:
                    # 길이 검증
                    if 'max_length' in rules:
                        is_valid, error_msg = validate_input(value, max_length=rules['max_length'])
                        if not is_valid:
                            errors[field] = error_msg
                    
                    # 패턴 검증
                    if 'pattern' in rules:
                        is_valid, error_msg = validate_input(value, pattern=rules['pattern'])
                        if not is_valid:
                            errors[field] = error_msg
                    
                    # 특별한 검증 함수
                    if 'validator' in rules:
                        is_valid, error_msg = rules['validator'](value)
                        if not is_valid:
                            errors[field] = error_msg
                    
                    # XSS 방지
                    if rules.get('escape_html', False):
                        data[field] = escape_html(value)
            
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
        _rate_limit_store[key] = {'count': 0, 'reset_time': now}
    
    record = _rate_limit_store[key]
    
    # 시간 윈도우 초기화
    if (now - record['reset_time']).total_seconds() > window_seconds:
        record['count'] = 0
        record['reset_time'] = now
    
    # 요청 수 증가
    record['count'] += 1
    
    # 제한 확인
    if record['count'] > max_requests:
        return False, record['count']
    
    return True, record['count']

def rate_limit(max_requests=100, window_seconds=3600):
    """Rate Limiting 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # IP 주소 또는 사용자 ID로 식별
            identifier = request.remote_addr
            if hasattr(request, 'user') and request.user:
                identifier = f"{identifier}_{request.user.id}"  # type: ignore
            
            is_allowed, current_count = check_rate_limit(identifier, max_requests, window_seconds)
            
            if not is_allowed:
                return jsonify({
                    'message': '요청 한도를 초과했습니다',
                    'retry_after': window_seconds
                }), 429
            
            # 응답 헤더에 Rate Limit 정보 추가
            response = f(*args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit'] = max_requests
                response.headers['X-RateLimit-Remaining'] = max_requests - current_count
                response.headers['X-RateLimit-Reset'] = window_seconds
            
            return response
        return decorated
    return decorator

# 보안 헤더 추가
def add_security_headers(response):
    """보안 헤더 추가"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    return response

# 보안 헤더 데코레이터
def security_headers(f):
    """보안 헤더 추가 데코레이터"""
    @wraps(f)
    def decorated(*args, **kwargs):
        response = f(*args, **kwargs)
        return add_security_headers(response)
    return decorated

# 사용자 입력 검증 예시
@security.route('/validate/user', methods=['POST'])
@security_headers
@rate_limit(max_requests=50, window_seconds=3600)
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
def validate_user_input():
    """사용자 입력 검증 API"""
    data = request.get_json()
    
    return jsonify({
        'message': '입력 검증 성공',
        'data': {
            'username': data.get('username'),
            'email': data.get('email'),
            'name': data.get('name'),
            'phone': data.get('phone')
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
@security_headers
@rate_limit(max_requests=20, window_seconds=3600)
def validate_file():
    """파일 업로드 검증 API"""
    if 'file' not in request.files:
        return jsonify({'message': '파일이 선택되지 않았습니다'}), 400
    
    file = request.files['file']
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
def log_security_event(event_type, details, user_id=None, ip_address=None):
    """보안 이벤트 로그"""
    security_log = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'details': details,
        'user_id': user_id,
        'ip_address': ip_address or request.remote_addr,
        'user_agent': request.headers.get('User-Agent', ''),
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
    is_allowed, current_count = check_rate_limit(identifier, 100, 3600)
    
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
        'max_login_attempts': data.get('max_login_attempts', 5),
        'session_timeout': data.get('session_timeout', 30),
        'password_expiry_days': data.get('password_expiry_days', 90),
        'require_2fa': data.get('require_2fa', False),
        'rate_limit_enabled': data.get('rate_limit_enabled', True),
        'xss_protection': data.get('xss_protection', True),
        'csrf_protection': data.get('csrf_protection', True)
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