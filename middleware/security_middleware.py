"""
보안 강화 미들웨어
CORS, Rate Limiting, Security Headers, JWT 인증 등 보안 기능 제공
"""

import time
import hashlib
import hmac
from functools import wraps
from typing import Optional, Dict, Any, Callable
from flask import request, jsonify, current_app, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import jwt
from datetime import datetime, timedelta

class SecurityMiddleware:
    """보안 미들웨어 클래스"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """앱 초기화"""
        self.app = app
        
        # CORS 설정
        self._setup_cors(app)
        
        # Rate Limiting 설정
        self._setup_rate_limiting(app)
        
        # Security Headers 설정
        self._setup_security_headers(app)
        
        # JWT 설정
        self._setup_jwt(app)
        
        # 요청 로깅 설정
        self._setup_request_logging(app)
        
        # 에러 핸들러 설정
        self._setup_error_handlers(app)
    
    def _setup_cors(self, app):
        """CORS 설정"""
        origins = app.config.get('CORS_ORIGINS', [])
        if isinstance(origins, str):
            origins = [origin.strip() for origin in origins.split(',')]
        
        CORS(app, 
             origins=origins,
             supports_credentials=True,
             methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
             expose_headers=["Content-Type", "Authorization"],
             max_age=86400)
    
    def _setup_rate_limiting(self, app):
        """Rate Limiting 설정"""
        if app.config.get('RATELIMIT_ENABLED', True):
            storage_url = app.config.get('RATELIMIT_STORAGE_URL', 'memory://')
            default_limit = app.config.get('RATELIMIT_DEFAULT', '200 per day;50 per hour;10 per minute')
            
            limiter = Limiter(
                app=app,
                key_func=get_remote_address,
                storage_uri=storage_url,
                default_limits=[default_limit],
                strategy="fixed-window"
            )
            
            # 특정 엔드포인트별 Rate Limit 설정
            @limiter.limit("5 per minute")
            @app.route("/api/security/auth/login", methods=["POST"])
            def login_rate_limit():
                return app.view_functions['api_security_auth_login']()
            
            @limiter.limit("10 per minute")
            @app.route("/api/admin/brands", methods=["POST"])
            def create_brand_rate_limit():
                return app.view_functions['api_admin_create_brand']()
    
    def _setup_security_headers(self, app):
        """Security Headers 설정"""
        @app.after_request
        def add_security_headers(response):
            # XSS Protection
            response.headers['X-XSS-Protection'] = '1; mode=block'
            
            # Content Type Options
            response.headers['X-Content-Type-Options'] = 'nosniff'
            
            # Frame Options
            response.headers['X-Frame-Options'] = 'DENY'
            
            # Referrer Policy
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Content Security Policy
            csp = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' ws: wss:;"
            response.headers['Content-Security-Policy'] = csp
            
            # HSTS (HTTPS에서만)
            if request.is_secure:
                response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            return response
    
    def _setup_jwt(self, app):
        """JWT 설정"""
        app.jwt_secret = app.config.get('JWT_SECRET_KEY', 'default-jwt-secret')
        app.jwt_expiration = app.config.get('JWT_EXPIRATION', 3600)  # 1시간
    
    def _setup_request_logging(self, app):
        """요청 로깅 설정"""
        @app.before_request
        def log_request():
            g.start_time = time.time()
            
            # 민감한 정보 제외하고 로깅
            log_data = {
                'method': request.method,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', ''),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # 인증된 사용자 정보 추가
            if hasattr(g, 'user') and g.user:
                log_data['user_id'] = g.user.id
                log_data['username'] = g.user.username
            
            app.logger.info(f"Request: {log_data}")
        
        @app.after_request
        def log_response(response):
            if hasattr(g, 'start_time'):
                duration = time.time() - g.start_time
                app.logger.info(f"Response: {response.status_code} - {duration:.3f}s")
            return response
    
    def _setup_error_handlers(self, app):
        """에러 핸들러 설정"""
        @app.errorhandler(400)
        def bad_request(error):
            return jsonify({
                'success': False,
                'error': 'Bad Request',
                'message': '잘못된 요청입니다.',
                'code': 'BAD_REQUEST'
            }), 400
        
        @app.errorhandler(401)
        def unauthorized(error):
            return jsonify({
                'success': False,
                'error': 'Unauthorized',
                'message': '인증이 필요합니다.',
                'code': 'UNAUTHORIZED'
            }), 401
        
        @app.errorhandler(403)
        def forbidden(error):
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': '접근 권한이 없습니다.',
                'code': 'FORBIDDEN'
            }), 403
        
        @app.errorhandler(404)
        def not_found(error):
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': 'Not Found',
                    'message': '요청한 리소스를 찾을 수 없습니다.',
                    'code': 'NOT_FOUND'
                }), 404
            return error
        
        @app.errorhandler(429)
        def too_many_requests(error):
            return jsonify({
                'success': False,
                'error': 'Too Many Requests',
                'message': '요청이 너무 많습니다. 잠시 후 다시 시도해주세요.',
                'code': 'RATE_LIMIT_EXCEEDED'
            }), 429
        
        @app.errorhandler(500)
        def internal_error(error):
            app.logger.error(f"Internal Server Error: {error}")
            return jsonify({
                'success': False,
                'error': 'Internal Server Error',
                'message': '서버 내부 오류가 발생했습니다.',
                'code': 'INTERNAL_ERROR'
            }), 500

# JWT 유틸리티 함수들
def generate_jwt_token(user_id: int, username: str, role: str) -> str:
    """JWT 토큰 생성"""
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(seconds=current_app.jwt_expiration),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.jwt_secret, algorithm='HS256')

def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """JWT 토큰 검증"""
    try:
        payload = jwt.decode(token, current_app.jwt_secret, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def jwt_required(f: Callable) -> Callable:
    """JWT 인증 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Authorization 헤더에서 토큰 추출
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Token Missing',
                'message': '인증 토큰이 필요합니다.',
                'code': 'TOKEN_MISSING'
            }), 401
        
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({
                'success': False,
                'error': 'Invalid Token',
                'message': '유효하지 않은 토큰입니다.',
                'code': 'INVALID_TOKEN'
            }), 401
        
        # 사용자 정보를 g 객체에 저장
        g.user_id = payload['user_id']
        g.username = payload['username']
        g.role = payload['role']
        
        return f(*args, **kwargs)
    
    return decorated_function

def role_required(required_role: str) -> Callable:
    """역할 기반 권한 데코레이터"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'role'):
                return jsonify({
                    'success': False,
                    'error': 'Authentication Required',
                    'message': '인증이 필요합니다.',
                    'code': 'AUTH_REQUIRED'
                }), 401
            
            if g.role != required_role and g.role != 'admin':
                return jsonify({
                    'success': False,
                    'error': 'Insufficient Permissions',
                    'message': '권한이 부족합니다.',
                    'code': 'INSUFFICIENT_PERMISSIONS'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# CSRF 보호
def generate_csrf_token() -> str:
    """CSRF 토큰 생성"""
    if 'csrf_token' not in g:
        g.csrf_token = hashlib.sha256(
            f"{time.time()}{current_app.config['SECRET_KEY']}".encode()
        ).hexdigest()
    return g.csrf_token

def verify_csrf_token(token: str) -> bool:
    """CSRF 토큰 검증"""
    expected_token = generate_csrf_token()
    return hmac.compare_digest(token, expected_token)

# 입력 검증
def sanitize_input(data: str) -> str:
    """입력 데이터 정제"""
    import html
    return html.escape(data.strip())

def validate_email(email: str) -> bool:
    """이메일 형식 검증"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> bool:
    """비밀번호 강도 검증"""
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    return True 