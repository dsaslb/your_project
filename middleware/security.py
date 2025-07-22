"""
보안 미들웨어
"""

import time
import logging
from typing import Dict, List, Optional
from flask import request, g, jsonify, current_app
from functools import wraps
import jwt
from datetime import datetime, timedelta
import hashlib
import secrets

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate Limiting 구현"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # 실제로는 Redis를 사용해야 함
    
    def is_allowed(self, client_ip: str) -> bool:
        """요청이 허용되는지 확인"""
        now = time.time()
        
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # 윈도우 시간을 벗어난 요청 제거
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < self.window_seconds
        ]
        
        # 요청 수 확인
        if len(self.requests[client_ip]) >= self.max_requests:
            return False
        
        # 새 요청 추가
        self.requests[client_ip].append(now)
        return True

class SecurityMiddleware:
    """보안 미들웨어 클래스"""
    
    def __init__(self, app=None):
        self.app = app
        self.rate_limiter = RateLimiter()
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Flask 앱 초기화"""
        self.app = app
        
        # 보안 헤더 설정
        @app.after_request
        def add_security_headers(response):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
            return response
        
        # CORS 설정
        @app.after_request
        def add_cors_headers(response):
            origin = request.headers.get('Origin')
            if origin and origin in app.config.get('SECURITY_CONFIG').cors_origins:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response
        
        # 요청 로깅
        @app.before_request
        def log_request():
            g.start_time = time.time()
            logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")
        
        @app.after_request
        def log_response(response):
            if hasattr(g, 'start_time'):
                duration = time.time() - g.start_time
                logger.info(f"Response: {response.status_code} in {duration:.3f}s")
            return response

def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """Rate Limiting 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            rate_limiter = RateLimiter(max_requests, window_seconds)
            
            if not rate_limiter.is_allowed(client_ip):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Limit: {max_requests} per {window_seconds} seconds'
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_auth(f):
    """인증 필요 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Authorization 헤더에서 토큰 추출
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid authorization header'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # JWT 토큰 검증
            secret_key = current_app.config.get('SECURITY_CONFIG').jwt_secret
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            g.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def require_role(required_roles: List[str]):
    """역할 기반 권한 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            user_role = g.user.get('role')
            if user_role not in required_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sanitize_input(data: str) -> str:
    """입력 데이터 정제"""
    if not isinstance(data, str):
        return data
    
    # XSS 방지를 위한 특수문자 이스케이프
    dangerous_chars = {
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '&': '&amp;'
    }
    
    for char, replacement in dangerous_chars.items():
        data = data.replace(char, replacement)
    
    return data

def validate_file_upload(file, allowed_extensions: set, max_size: int) -> bool:
    """파일 업로드 검증"""
    if not file:
        return False
    
    # 파일 확장자 검증
    filename = file.filename
    if not filename or '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    if extension not in allowed_extensions:
        return False
    
    # 파일 크기 검증
    file.seek(0, 2)  # 파일 끝으로 이동
    size = file.tell()
    file.seek(0)  # 파일 시작으로 복귀
    
    if size > max_size:
        return False
    
    return True

def generate_csrf_token() -> str:
    """CSRF 토큰 생성"""
    return secrets.token_urlsafe(32)

def verify_csrf_token(token: str, stored_token: str) -> bool:
    """CSRF 토큰 검증"""
    return secrets.compare_digest(token, stored_token)

def hash_password(password: str) -> str:
    """비밀번호 해싱"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}${hash_obj.hex()}"

def verify_password(password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    try:
        salt, hash_hex = hashed_password.split('$')
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return secrets.compare_digest(hash_obj.hex(), hash_hex)
    except (ValueError, AttributeError):
        return False

def generate_jwt_token(user_data: Dict, expiration_hours: int = 24) -> str:
    """JWT 토큰 생성"""
    payload = {
        'user_id': user_data.get('id'),
        'username': user_data.get('username'),
        'role': user_data.get('role'),
        'exp': datetime.utcnow() + timedelta(hours=expiration_hours),
        'iat': datetime.utcnow()
    }
    
    secret_key = current_app.config.get('SECURITY_CONFIG').jwt_secret
    return jwt.encode(payload, secret_key, algorithm='HS256')

def validate_email(email: str) -> bool:
    """이메일 형식 검증"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """전화번호 형식 검증"""
    import re
    pattern = r'^[0-9-+\s()]{10,15}$'
    return re.match(pattern, phone) is not None

def sanitize_sql_input(data: str) -> str:
    """SQL 인젝션 방지를 위한 입력 정제"""
    if not isinstance(data, str):
        return data
    
    # SQL 인젝션 위험 문자 제거
    dangerous_patterns = [
        ';', '--', '/*', '*/', 'xp_', 'sp_', 'exec', 'execute',
        'union', 'select', 'insert', 'update', 'delete', 'drop',
        'create', 'alter', 'script', 'javascript'
    ]
    
    data_lower = data.lower()
    for pattern in dangerous_patterns:
        if pattern in data_lower:
            return ''
    
    return data 