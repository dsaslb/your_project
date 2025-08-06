"""
보안 미들웨어
HTTP 보안 헤더, CORS, 요청 검증 등을 제공
"""

import logging
import re
from functools import wraps
from flask import request, g, current_app
from typing import Dict, Any, Optional, List
import time
import hashlib

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """보안 미들웨어 클래스"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Flask 앱에 미들웨어 등록"""
        
        @app.before_request
        def before_request():
            """요청 전 보안 검사"""
            self._validate_request()
            self._check_rate_limit()
            self._log_request()
        
        @app.after_request
        def after_request(response):
            """응답 후 보안 헤더 추가"""
            return self._add_security_headers(response)
        
        @app.errorhandler(413)
        def request_entity_too_large(error):
            """파일 크기 초과 에러 처리"""
            return {
                'status': 'error',
                'message': '업로드된 파일이 너무 큽니다',
                'code': 413
            }, 413
        
        @app.errorhandler(400)
        def bad_request(error):
            """잘못된 요청 처리"""
            return {
                'status': 'error',
                'message': '잘못된 요청입니다',
                'code': 400
            }, 400
    
    def _validate_request(self):
        """요청 유효성 검사"""
        # Content-Type 검증
        if request.method in ['POST', 'PUT', 'PATCH']:
            if request.is_json and not request.content_type.startswith('application/json'):
                return {'status': 'error', 'message': '잘못된 Content-Type'}, 400
        
        # 파일 업로드 검증
        if request.files:
            for file in request.files.values():
                if file and file.filename:
                    if not self._is_allowed_file(file.filename):
                        return {'status': 'error', 'message': '허용되지 않는 파일 형식'}, 400
        
        # 요청 크기 검증
        if request.content_length and request.content_length > current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024):
            return {'status': 'error', 'message': '요청 크기가 너무 큽니다'}, 413
    
    def _is_allowed_file(self, filename: str) -> bool:
        """허용된 파일 확장자 검증"""
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', set())
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    def _check_rate_limit(self):
        """Rate limiting 검사 (기본 구현)"""
        # 실제 구현에서는 Flask-Limiter와 연동
        pass
    
    def _log_request(self):
        """요청 로깅"""
        if current_app.config.get('LOG_IP_ADDRESSES', True):
            client_ip = self._get_client_ip()
            logger.info(f"Request: {request.method} {request.url} from {client_ip}")
    
    def _get_client_ip(self) -> str:
        """클라이언트 IP 주소 가져오기"""
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr
    
    def _add_security_headers(self, response):
        """보안 헤더 추가"""
        security_headers = current_app.config.get('SECURITY_HEADERS', {})
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        # 추가 보안 헤더
        response.headers['Server'] = 'Your Program Server'
        response.headers['X-Powered-By'] = 'Your Program'
        
        return response

class InputSanitizer:
    """입력 데이터 정제 클래스"""
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """문자열 정제"""
        if not value:
            return value
        
        # HTML 태그 제거
        import html
        value = html.escape(value)
        
        # SQL 인젝션 방지 (기본적인 패턴)
        sql_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
            r'(\b(OR|AND)\b\s+\d+\s*=\s*\d+)',
            r'(\b(OR|AND)\b\s+\'[^\']*\'\s*=\s*\'[^\']*\')',
        ]
        
        for pattern in sql_patterns:
            value = re.sub(pattern, '', value, flags=re.IGNORECASE)
        
        return value.strip()
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """딕셔너리 정제"""
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = InputSanitizer.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[key] = InputSanitizer.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = InputSanitizer.sanitize_list(value)
            else:
                sanitized[key] = value
        return sanitized
    
    @staticmethod
    def sanitize_list(data: List[Any]) -> List[Any]:
        """리스트 정제"""
        sanitized = []
        for item in data:
            if isinstance(item, str):
                sanitized.append(InputSanitizer.sanitize_string(item))
            elif isinstance(item, dict):
                sanitized.append(InputSanitizer.sanitize_dict(item))
            elif isinstance(item, list):
                sanitized.append(InputSanitizer.sanitize_list(item))
            else:
                sanitized.append(item)
        return sanitized

def sanitize_input(f):
    """입력 정제 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # JSON 데이터 정제
        if request.is_json:
            data = request.get_json()
            if data:
                sanitized_data = InputSanitizer.sanitize_dict(data)
                request._cached_json = sanitized_data
        
        # 폼 데이터 정제
        if request.form:
            sanitized_form = InputSanitizer.sanitize_dict(request.form.to_dict())
            request.form = type(request.form)(sanitized_form)
        
        # 쿼리 파라미터 정제
        if request.args:
            sanitized_args = InputSanitizer.sanitize_dict(request.args.to_dict())
            request.args = type(request.args)(sanitized_args)
        
        return f(*args, **kwargs)
    return decorated_function

class RequestValidator:
    """요청 검증 클래스"""
    
    @staticmethod
    def validate_api_version(required_version: str = "v1"):
        """API 버전 검증"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                api_version = request.headers.get('X-API-Version', 'v1')
                if api_version != required_version:
                    return {
                        'status': 'error',
                        'message': f'API 버전 {required_version}이 필요합니다',
                        'code': 400
                    }, 400
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def validate_content_type(content_type: str = "application/json"):
        """Content-Type 검증"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not request.content_type or not request.content_type.startswith(content_type):
                    return {
                        'status': 'error',
                        'message': f'{content_type} Content-Type이 필요합니다',
                        'code': 400
                    }, 400
                return f(*args, **kwargs)
            return decorated_function
        return decorator

class CSRFProtection:
    """CSRF 보호 강화 클래스"""
    
    @staticmethod
    def validate_csrf_token():
        """CSRF 토큰 검증"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                    token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
                    if not token:
                        return {
                            'status': 'error',
                            'message': 'CSRF 토큰이 필요합니다',
                            'code': 403
                        }, 403
                    
                    # 실제 CSRF 토큰 검증 로직 구현 필요
                    # if not validate_csrf_token(token):
                    #     return {'status': 'error', 'message': '유효하지 않은 CSRF 토큰'}, 403
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator

# 전역 보안 미들웨어 인스턴스
security_middleware = SecurityMiddleware() 