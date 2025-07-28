"""
에러 처리 및 로깅 시스템
- 구조화된 에러 처리
- 상세한 로깅
- 사용자 친화적 에러 메시지
- 에러 추적 및 분석
"""

import logging
import traceback
import json
from datetime import datetime
from typing import Dict, Any, Optional, Union
from functools import wraps
from flask import request, jsonify, current_app, g
from werkzeug.exceptions import HTTPException


class ErrorHandler:
    """에러 처리 클래스"""
    
    def __init__(self, app=None):
        self.app = app
        self.error_logger = logging.getLogger('error_handler')
        self.performance_logger = logging.getLogger('performance')
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Flask 앱 초기화"""
        self.app = app
        
        # 에러 핸들러 등록
        app.register_error_handler(400, self.handle_bad_request)
        app.register_error_handler(401, self.handle_unauthorized)
        app.register_error_handler(403, self.handle_forbidden)
        app.register_error_handler(404, self.handle_not_found)
        app.register_error_handler(500, self.handle_internal_error)
        app.register_error_handler(Exception, self.handle_generic_error)
        
        # 요청 전후 처리
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)
    
    def before_request(self):
        """요청 전 처리"""
        g.start_time = datetime.now()
        g.request_id = self._generate_request_id()
        
        # 요청 로깅
        self.performance_logger.info(
            f"Request started: {g.request_id} - {request.method} {request.path}",
            extra={
                'request_id': g.request_id,
                'method': request.method,
                'path': request.path,
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', '')
            }
        )
    
    def after_request(self, response):
        """요청 후 처리"""
        if hasattr(g, 'start_time'):
            duration = (datetime.now() - g.start_time).total_seconds()
            
            # 응답 로깅
            self.performance_logger.info(
                f"Request completed: {g.request_id} - {response.status_code} ({duration:.3f}s)",
                extra={
                    'request_id': g.request_id,
                    'status_code': response.status_code,
                    'duration': duration
                }
            )
        
        return response
    
    def teardown_request(self, exception=None):
        """요청 종료 처리"""
        if exception:
            self.log_error(exception, "Request teardown error")
    
    def _generate_request_id(self) -> str:
        """요청 ID 생성"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def log_error(self, error: Exception, context: str = "", extra_data: Dict = None):
        """에러 로깅"""
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'traceback': traceback.format_exc(),
            'request_id': getattr(g, 'request_id', 'unknown'),
            'method': getattr(request, 'method', 'unknown'),
            'path': getattr(request, 'path', 'unknown'),
            'ip': getattr(request, 'remote_addr', 'unknown'),
            'user_agent': getattr(request, 'headers', {}).get('User-Agent', 'unknown'),
            'extra_data': extra_data or {}
        }
        
        # 에러 로깅
        self.error_logger.error(
            f"Error in {context}: {error}",
            extra=error_data
        )
        
        # 성능 모니터링에 에러 기록
        try:
            from utils.performance_monitor import performance_monitor
            performance_monitor.record_error(
                error_type=type(error).__name__,
                error_message=str(error),
                endpoint=getattr(request, 'path', 'unknown')
            )
        except Exception as e:
            self.error_logger.error(f"Failed to record error in performance monitor: {e}")
    
    def handle_bad_request(self, error):
        """400 에러 처리"""
        self.log_error(error, "Bad Request")
        return self._create_error_response(
            "잘못된 요청입니다.",
            "요청 형식이나 데이터가 올바르지 않습니다.",
            400,
            error
        )
    
    def handle_unauthorized(self, error):
        """401 에러 처리"""
        self.log_error(error, "Unauthorized")
        return self._create_error_response(
            "인증이 필요합니다.",
            "로그인이 필요하거나 인증 정보가 유효하지 않습니다.",
            401,
            error
        )
    
    def handle_forbidden(self, error):
        """403 에러 처리"""
        self.log_error(error, "Forbidden")
        return self._create_error_response(
            "접근이 거부되었습니다.",
            "이 리소스에 접근할 권한이 없습니다.",
            403,
            error
        )
    
    def handle_not_found(self, error):
        """404 에러 처리"""
        self.log_error(error, "Not Found")
        return self._create_error_response(
            "페이지를 찾을 수 없습니다.",
            "요청하신 페이지나 리소스가 존재하지 않습니다.",
            404,
            error
        )
    
    def handle_internal_error(self, error):
        """500 에러 처리"""
        self.log_error(error, "Internal Server Error")
        return self._create_error_response(
            "서버 오류가 발생했습니다.",
            "일시적인 서버 오류입니다. 잠시 후 다시 시도해주세요.",
            500,
            error
        )
    
    def handle_generic_error(self, error):
        """일반 에러 처리"""
        if isinstance(error, HTTPException):
            return error
        
        self.log_error(error, "Generic Error")
        return self._create_error_response(
            "오류가 발생했습니다.",
            "예상치 못한 오류가 발생했습니다. 관리자에게 문의해주세요.",
            500,
            error
        )
    
    def _create_error_response(self, title: str, message: str, status_code: int, error: Exception = None) -> tuple:
        """에러 응답 생성"""
        error_data = {
            'error': {
                'title': title,
                'message': message,
                'status_code': status_code,
                'timestamp': datetime.now().isoformat(),
                'request_id': getattr(g, 'request_id', 'unknown')
            }
        }
        
        # 개발 환경에서는 추가 정보 제공
        if current_app.config.get('DEBUG', False) and error:
            error_data['error']['debug'] = {
                'error_type': type(error).__name__,
                'error_message': str(error),
                'traceback': traceback.format_exc()
            }
        
        # API 요청인지 확인
        if request.path.startswith('/api/'):
            return jsonify(error_data), status_code
        else:
            # HTML 페이지 요청인 경우 템플릿 렌더링
            from flask import render_template
            return render_template('errors/error.html', error_data=error_data), status_code


# 전역 에러 핸들러 인스턴스
error_handler = ErrorHandler()


# 데코레이터들
def handle_errors(func):
    """에러 처리 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_handler.log_error(e, f"Function error: {func.__name__}")
            raise
    return wrapper


def validate_input(required_fields: list = None, optional_fields: list = None):
    """입력 검증 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # JSON 데이터 검증
                if request.is_json:
                    data = request.get_json()
                    
                    # 필수 필드 검증
                    if required_fields:
                        missing_fields = [field for field in required_fields if field not in data]
                        if missing_fields:
                            raise ValueError(f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}")
                    
                    # 허용된 필드만 추출
                    allowed_fields = (required_fields or []) + (optional_fields or [])
                    if allowed_fields:
                        filtered_data = {k: v for k, v in data.items() if k in allowed_fields}
                        request._json = filtered_data
                
                return func(*args, **kwargs)
            except ValueError as e:
                return jsonify({
                    'error': {
                        'title': '입력 검증 오류',
                        'message': str(e),
                        'status_code': 400
                    }
                }), 400
            except Exception as e:
                error_handler.log_error(e, f"Input validation error in {func.__name__}")
                raise
        return wrapper
    return decorator


def log_operation(operation: str):
    """작업 로깅 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            
            try:
                result = func(*args, **kwargs)
                
                # 성공 로깅
                duration = (datetime.now() - start_time).total_seconds()
                logging.getLogger('operations').info(
                    f"Operation completed: {operation}",
                    extra={
                        'operation': operation,
                        'function': func.__name__,
                        'duration': duration,
                        'status': 'success',
                        'request_id': getattr(g, 'request_id', 'unknown')
                    }
                )
                
                return result
            except Exception as e:
                # 실패 로깅
                duration = (datetime.now() - start_time).total_seconds()
                logging.getLogger('operations').error(
                    f"Operation failed: {operation}",
                    extra={
                        'operation': operation,
                        'function': func.__name__,
                        'duration': duration,
                        'status': 'failed',
                        'error': str(e),
                        'request_id': getattr(g, 'request_id', 'unknown')
                    }
                )
                raise
        return wrapper
    return decorator


# 유틸리티 함수들
def create_error_response(title: str, message: str, status_code: int = 400, extra_data: Dict = None) -> tuple:
    """에러 응답 생성 유틸리티"""
    error_data = {
        'error': {
            'title': title,
            'message': message,
            'status_code': status_code,
            'timestamp': datetime.now().isoformat(),
            'request_id': getattr(g, 'request_id', 'unknown')
        }
    }
    
    if extra_data:
        error_data['error']['extra'] = extra_data
    
    return jsonify(error_data), status_code


def create_success_response(data: Any, message: str = "성공적으로 처리되었습니다.") -> tuple:
    """성공 응답 생성 유틸리티"""
    response_data = {
        'success': True,
        'message': message,
        'data': data,
        'timestamp': datetime.now().isoformat(),
        'request_id': getattr(g, 'request_id', 'unknown')
    }
    
    return jsonify(response_data), 200


def safe_json_loads(data: str, default: Any = None) -> Any:
    """안전한 JSON 파싱"""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default


def validate_email(email: str) -> bool:
    """이메일 유효성 검사"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """전화번호 유효성 검사"""
    import re
    # 한국 전화번호 형식 (010-1234-5678, 02-123-4567 등)
    pattern = r'^(\d{2,3})-?(\d{3,4})-?(\d{4})$'
    return re.match(pattern, phone) is not None


def sanitize_input(text: str) -> str:
    """입력 데이터 정제"""
    if not text:
        return ""
    
    # HTML 태그 제거
    import re
    text = re.sub(r'<[^>]+>', '', text)
    
    # 특수 문자 이스케이프
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    
    return text.strip()


def format_error_message(error: Exception) -> str:
    """에러 메시지 포맷팅"""
    error_type = type(error).__name__
    error_message = str(error)
    
    # 일반적인 에러 메시지 매핑
    error_messages = {
        'ValidationError': '입력 데이터가 올바르지 않습니다.',
        'IntegrityError': '데이터 무결성 오류가 발생했습니다.',
        'ConnectionError': '데이터베이스 연결에 실패했습니다.',
        'TimeoutError': '요청 시간이 초과되었습니다.',
        'PermissionError': '권한이 없습니다.',
        'FileNotFoundError': '파일을 찾을 수 없습니다.',
        'ValueError': '잘못된 값이 입력되었습니다.',
        'TypeError': '잘못된 데이터 타입입니다.',
        'KeyError': '필수 키가 누락되었습니다.',
        'IndexError': '인덱스 오류가 발생했습니다.'
    }
    
    return error_messages.get(error_type, error_message) 