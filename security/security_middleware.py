"""
보안 미들웨어
CORS, CSRF, Rate Limiting, 보안 헤더 기능 제공
"""

import time
import logging
import hashlib
import secrets
from typing import Dict, List, Optional, Callable
from functools import wraps
from flask import request, jsonify, current_app, g
from collections import defaultdict
import redis

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """보안 미들웨어 관리자"""
    
    def __init__(self, app=None):
        self.app = app
        self.redis_client = None
        self.rate_limit_storage = defaultdict(list)
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Flask 앱에 보안 미들웨어 초기화"""
        self.app = app
        
        # Redis 연결 (Rate Limiting용)
        try:
            redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/1')
            self.redis_client = redis.from_url(redis_url)
            logger.info("보안 미들웨어 Redis 연결 성공")
        except Exception as e:
            logger.warning(f"보안 미들웨어 Redis 연결 실패: {e}")
        
        # 보안 헤더 설정
        self._setup_security_headers(app)
        
        # CORS 설정
        self._setup_cors(app)
        
        # CSRF 보호 설정
        self._setup_csrf_protection(app)
        
        # Rate Limiting 설정
        self._setup_rate_limiting(app)
        
        logger.info("보안 미들웨어 초기화 완료")
    
    def _setup_security_headers(self, app):
        """보안 헤더 설정"""
        @app.after_request
        def add_security_headers(response):
            # XSS 보호
            response.headers['X-XSS-Protection'] = '1; mode=block'
            
            # 클릭재킹 방지
            response.headers['X-Frame-Options'] = 'DENY'
            
            # MIME 타입 스니핑 방지
            response.headers['X-Content-Type-Options'] = 'nosniff'
            
            # HSTS (HTTPS 강제)
            if request.is_secure:
                response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            # Content Security Policy
            csp_policy = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
                "img-src 'self' data: https:",
                "font-src 'self' https://cdn.jsdelivr.net",
                "connect-src 'self' ws: wss:",
                "frame-ancestors 'none'"
            ]
            response.headers['Content-Security-Policy'] = '; '.join(csp_policy)
            
            # Referrer Policy
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Permissions Policy
            response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
            
            return response
    
    def _setup_cors(self, app):
        """CORS 설정"""
        @app.after_request
        def add_cors_headers(response):
            # 허용된 도메인 목록
            allowed_origins = [
                'http://localhost:3000',
                'http://localhost:5000',
                'https://your-domain.com'
            ]
            
            origin = request.headers.get('Origin')
            if origin in allowed_origins:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            
            return response
    
    def _setup_csrf_protection(self, app):
        """CSRF 보호 설정"""
        @app.before_request
        def csrf_protection():
            # CSRF 보호가 필요한 요청만 체크
            if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                # API 요청은 JWT 토큰으로 보호되므로 CSRF 체크 생략
                if request.path.startswith('/api/'):
                    return
                
                # 폼 요청에 대해서만 CSRF 체크
                if request.content_type and 'application/json' not in request.content_type:
                    csrf_token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
                    session_token = session.get('csrf_token')
                    
                    if not csrf_token or not session_token or csrf_token != session_token:
                        return jsonify({'error': 'CSRF 토큰이 유효하지 않습니다'}), 403
    
    def _setup_rate_limiting(self, app):
        """Rate Limiting 설정"""
        @app.before_request
        def rate_limiting():
            # Rate Limiting이 적용되지 않는 경로
            exempt_paths = ['/health', '/metrics', '/static/']
            
            if any(request.path.startswith(path) for path in exempt_paths):
                return
            
            # 클라이언트 식별자 생성
            client_id = self._get_client_id()
            
            # Rate Limiting 체크
            if not self._check_rate_limit(client_id, request.path):
                return jsonify({'error': '요청이 너무 많습니다. 잠시 후 다시 시도해주세요.'}), 429
    
    def _get_client_id(self) -> str:
        """클라이언트 식별자 생성"""
        # IP 주소 기반
        client_ip = request.remote_addr
        
        # 사용자 ID가 있으면 포함
        user_id = getattr(g, 'user_id', None)
        if user_id:
            return f"{client_ip}:{user_id}"
        
        return client_ip
    
    def _check_rate_limit(self, client_id: str, endpoint: str) -> bool:
        """Rate Limiting 체크"""
        try:
            # Redis를 사용한 Rate Limiting
            if self.redis_client:
                return self._check_redis_rate_limit(client_id, endpoint)
            else:
                # 메모리 기반 Rate Limiting
                return self._check_memory_rate_limit(client_id, endpoint)
        except Exception as e:
            logger.error(f"Rate Limiting 체크 실패: {e}")
            return True  # 오류 시 허용
    
    def _check_redis_rate_limit(self, client_id: str, endpoint: str) -> bool:
        """Redis 기반 Rate Limiting"""
        key = f"rate_limit:{client_id}:{endpoint}"
        current_time = int(time.time())
        window_size = 60  # 1분 윈도우
        max_requests = 100  # 최대 요청 수
        
        # 현재 윈도우의 요청 수 확인
        pipe = self.redis_client.pipeline()
        pipe.zremrangebyscore(key, 0, current_time - window_size)
        pipe.zadd(key, {str(current_time): current_time})
        pipe.zcard(key)
        pipe.expire(key, window_size)
        results = pipe.execute()
        
        current_requests = results[2]
        return current_requests <= max_requests
    
    def _check_memory_rate_limit(self, client_id: str, endpoint: str) -> bool:
        """메모리 기반 Rate Limiting"""
        key = f"{client_id}:{endpoint}"
        current_time = time.time()
        window_size = 60  # 1분 윈도우
        max_requests = 100  # 최대 요청 수
        
        # 오래된 요청 제거
        self.rate_limit_storage[key] = [
            req_time for req_time in self.rate_limit_storage[key]
            if current_time - req_time < window_size
        ]
        
        # 현재 요청 수 확인
        if len(self.rate_limit_storage[key]) >= max_requests:
            return False
        
        # 새 요청 추가
        self.rate_limit_storage[key].append(current_time)
        return True
    
    def generate_csrf_token(self) -> str:
        """CSRF 토큰 생성"""
        token = secrets.token_hex(32)
        return token
    
    def validate_csrf_token(self, token: str, session_token: str) -> bool:
        """CSRF 토큰 검증"""
        return token == session_token
    
    def sanitize_input(self, data: str) -> str:
        """입력 데이터 정제"""
        import html
        
        # HTML 엔티티 이스케이프
        sanitized = html.escape(data)
        
        # SQL 인젝션 방지를 위한 특수 문자 제거
        dangerous_chars = ["'", '"', ';', '--', '/*', '*/']
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized
    
    def validate_password_strength(self, password: str) -> Dict[str, any]:
        """비밀번호 강도 검증"""
        errors = []
        warnings = []
        
        if len(password) < 8:
            errors.append("비밀번호는 최소 8자 이상이어야 합니다")
        elif len(password) < 12:
            warnings.append("비밀번호를 12자 이상으로 설정하는 것을 권장합니다")
        
        if not any(c.isupper() for c in password):
            errors.append("대문자를 포함해야 합니다")
        
        if not any(c.islower() for c in password):
            errors.append("소문자를 포함해야 합니다")
        
        if not any(c.isdigit() for c in password):
            errors.append("숫자를 포함해야 합니다")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            warnings.append("특수문자를 포함하는 것을 권장합니다")
        
        # 연속된 문자 체크
        for i in range(len(password) - 2):
            if password[i] == password[i+1] == password[i+2]:
                warnings.append("연속된 동일한 문자 사용을 피하세요")
                break
        
        # 일반적인 비밀번호 체크
        common_passwords = ['password', '123456', 'qwerty', 'admin']
        if password.lower() in common_passwords:
            errors.append("일반적인 비밀번호는 사용할 수 없습니다")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'score': self._calculate_password_score(password)
        }
    
    def _calculate_password_score(self, password: str) -> int:
        """비밀번호 강도 점수 계산 (0-100)"""
        score = 0
        
        # 길이 점수
        score += min(len(password) * 4, 40)
        
        # 문자 종류 점수
        if any(c.isupper() for c in password):
            score += 10
        if any(c.islower() for c in password):
            score += 10
        if any(c.isdigit() for c in password):
            score += 10
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 20
        
        # 복잡성 점수
        unique_chars = len(set(password))
        score += min(unique_chars * 2, 20)
        
        return min(score, 100)
    
    def log_security_event(self, event_type: str, details: Dict[str, any]):
        """보안 이벤트 로깅"""
        log_data = {
            'timestamp': time.time(),
            'event_type': event_type,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'path': request.path,
            'method': request.method,
            'details': details
        }
        
        logger.warning(f"보안 이벤트: {event_type} - {details}")
        
        # 보안 이벤트를 Redis에 저장 (선택사항)
        if self.redis_client:
            try:
                self.redis_client.lpush('security_events', str(log_data))
                self.redis_client.ltrim('security_events', 0, 999)  # 최근 1000개만 유지
            except Exception as e:
                logger.error(f"보안 이벤트 저장 실패: {e}")

# 전역 보안 미들웨어 인스턴스
security_middleware = SecurityMiddleware()

# 데코레이터들
def require_https(f):
    """HTTPS 요구 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_secure and not current_app.debug:
            return jsonify({'error': 'HTTPS가 필요합니다'}), 403
        return f(*args, **kwargs)
    return decorated_function

def validate_input(f):
    """입력 검증 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # JSON 데이터 정제
        if request.is_json:
            data = request.get_json()
            if data:
                sanitized_data = {}
                for key, value in data.items():
                    if isinstance(value, str):
                        sanitized_data[key] = security_middleware.sanitize_input(value)
                    else:
                        sanitized_data[key] = value
                request._json = sanitized_data
        
        # 폼 데이터 정제
        if request.form:
            for key in request.form:
                if isinstance(request.form[key], str):
                    request.form[key] = security_middleware.sanitize_input(request.form[key])
        
        return f(*args, **kwargs)
    return decorated_function 