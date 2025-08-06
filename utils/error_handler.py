"""
통합 에러 처리 시스템
애플리케이션 전체의 에러 처리 및 로깅
"""

import logging
import traceback
import json
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from flask import Flask, request, jsonify, current_app
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from extensions import db

logger = logging.getLogger(__name__)


class ErrorHandler:
    """통합 에러 처리기"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.error_log = []
        self.custom_handlers = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Flask 앱에 에러 핸들러 등록"""
        self.app = app
        
        # HTTP 에러 핸들러
        app.register_error_handler(400, self.handle_bad_request)
        app.register_error_handler(401, self.handle_unauthorized)
        app.register_error_handler(403, self.handle_forbidden)
        app.register_error_handler(404, self.handle_not_found)
        app.register_error_handler(405, self.handle_method_not_allowed)
        app.register_error_handler(422, self.handle_unprocessable_entity)
        app.register_error_handler(429, self.handle_too_many_requests)
        app.register_error_handler(500, self.handle_internal_server_error)
        
        # 데이터베이스 에러 핸들러
        app.register_error_handler(SQLAlchemyError, self.handle_database_error)
        
        # 일반 예외 핸들러
        app.register_error_handler(Exception, self.handle_generic_error)
        
        logger.info("에러 핸들러 초기화 완료")
    
    def handle_bad_request(self, error):
        """400 Bad Request 처리"""
        return self._create_error_response(
            error_code="BAD_REQUEST",
            message="잘못된 요청입니다.",
            details=str(error),
            status_code=400
        )
    
    def handle_unauthorized(self, error):
        """401 Unauthorized 처리"""
        return self._create_error_response(
            error_code="UNAUTHORIZED",
            message="인증이 필요합니다.",
            details="로그인이 필요하거나 인증 토큰이 유효하지 않습니다.",
            status_code=401
        )
    
    def handle_forbidden(self, error):
        """403 Forbidden 처리"""
        return self._create_error_response(
            error_code="FORBIDDEN",
            message="접근 권한이 없습니다.",
            details="해당 리소스에 접근할 권한이 없습니다.",
            status_code=403
        )
    
    def handle_not_found(self, error):
        """404 Not Found 처리"""
        return self._create_error_response(
            error_code="NOT_FOUND",
            message="요청한 리소스를 찾을 수 없습니다.",
            details=f"경로: {request.path}",
            status_code=404
        )
    
    def handle_method_not_allowed(self, error):
        """405 Method Not Allowed 처리"""
        return self._create_error_response(
            error_code="METHOD_NOT_ALLOWED",
            message="허용되지 않는 HTTP 메서드입니다.",
            details=f"허용된 메서드: {error.valid_methods}",
            status_code=405
        )
    
    def handle_unprocessable_entity(self, error):
        """422 Unprocessable Entity 처리"""
        return self._create_error_response(
            error_code="UNPROCESSABLE_ENTITY",
            message="요청 데이터를 처리할 수 없습니다.",
            details=str(error),
            status_code=422
        )
    
    def handle_too_many_requests(self, error):
        """429 Too Many Requests 처리"""
        return self._create_error_response(
            error_code="TOO_MANY_REQUESTS",
            message="요청이 너무 많습니다.",
            details="잠시 후 다시 시도해주세요.",
            status_code=429
        )
    
    def handle_database_error(self, error):
        """데이터베이스 에러 처리"""
        # 데이터베이스 롤백
        try:
            db.session.rollback()
        except:
            pass
        
        error_message = "데이터베이스 오류가 발생했습니다."
        error_details = str(error)
        
        # 개발 환경에서는 상세 에러 정보 제공
        if current_app.config.get('DEBUG', False):
            error_details = traceback.format_exc()
        
        return self._create_error_response(
            error_code="DATABASE_ERROR",
            message=error_message,
            details=error_details,
            status_code=500
        )
    
    def handle_internal_server_error(self, error):
        """500 Internal Server Error 처리"""
        return self._create_error_response(
            error_code="INTERNAL_SERVER_ERROR",
            message="서버 내부 오류가 발생했습니다.",
            details="관리자에게 문의해주세요.",
            status_code=500
        )
    
    def handle_generic_error(self, error):
        """일반 예외 처리"""
        # 에러 로깅
        self._log_error(error)
        
        # 개발 환경에서는 상세 에러 정보 제공
        if current_app.config.get('DEBUG', False):
            error_details = traceback.format_exc()
        else:
            error_details = "알 수 없는 오류가 발생했습니다."
        
        return self._create_error_response(
            error_code="GENERIC_ERROR",
            message="오류가 발생했습니다.",
            details=error_details,
            status_code=500
        )
    
    def _create_error_response(self, error_code: str, message: str, 
                             details: str, status_code: int) -> tuple:
        """에러 응답 생성"""
        error_data = {
            'error': {
                'code': error_code,
                'message': message,
                'details': details,
                'timestamp': datetime.utcnow().isoformat(),
                'path': request.path,
                'method': request.method
            }
        }
        
        # 에러 로그에 추가
        self.error_log.append({
            'timestamp': datetime.utcnow(),
            'error_code': error_code,
            'message': message,
            'details': details,
            'status_code': status_code,
            'path': request.path,
            'method': request.method,
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.remote_addr
        })
        
        # 로그 파일에 기록
        logger.error(f"Error {status_code}: {error_code} - {message} - {details}")
        
        return jsonify(error_data), status_code
    
    def _log_error(self, error: Exception):
        """에러 로깅"""
        error_info = {
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'request_path': request.path,
            'request_method': request.method,
            'request_headers': dict(request.headers),
            'request_data': self._get_request_data()
        }
        
        logger.error(f"Unhandled error: {json.dumps(error_info, indent=2)}")
    
    def _get_request_data(self) -> Dict[str, Any]:
        """요청 데이터 수집"""
        data = {
            'args': dict(request.args),
            'form': dict(request.form),
            'json': request.get_json(silent=True),
            'files': list(request.files.keys()) if request.files else []
        }
        
        # 민감한 정보 제거
        sensitive_fields = ['password', 'token', 'secret', 'key']
        for field in sensitive_fields:
            if field in data['form']:
                data['form'][field] = '***REDACTED***'
            if field in data['json']:
                data['json'][field] = '***REDACTED***'
        
        return data
    
    def register_custom_handler(self, error_type: type, handler: Callable):
        """커스텀 에러 핸들러 등록"""
        self.custom_handlers[error_type] = handler
    
    def get_error_log(self, limit: int = 100) -> list:
        """에러 로그 조회"""
        return self.error_log[-limit:] if limit else self.error_log
    
    def clear_error_log(self):
        """에러 로그 정리"""
        self.error_log.clear()
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """에러 통계 생성"""
        if not self.error_log:
            return {}
        
        stats = {
            'total_errors': len(self.error_log),
            'error_codes': {},
            'status_codes': {},
            'paths': {},
            'recent_errors': []
        }
        
        # 최근 24시간 에러만 필터링
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        recent_errors = [e for e in self.error_log if e['timestamp'] > cutoff_time]
        
        for error in recent_errors:
            # 에러 코드별 통계
            error_code = error['error_code']
            stats['error_codes'][error_code] = stats['error_codes'].get(error_code, 0) + 1
            
            # 상태 코드별 통계
            status_code = error['status_code']
            stats['status_codes'][status_code] = stats['status_codes'].get(status_code, 0) + 1
            
            # 경로별 통계
            path = error['path']
            stats['paths'][path] = stats['paths'].get(path, 0) + 1
        
        # 최근 에러 목록
        stats['recent_errors'] = recent_errors[-10:]  # 최근 10개
        
        return stats


# 전역 에러 핸들러 인스턴스
error_handler = ErrorHandler()


def handle_api_error(func: Callable) -> Callable:
    """API 에러 처리 데코레이터"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"API 에러 발생: {func.__name__} - {str(e)}")
            return error_handler.handle_generic_error(e)
    return wrapper


def validate_request_data(required_fields: list = None, optional_fields: list = None):
    """요청 데이터 검증 데코레이터"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            try:
                data = request.get_json() or request.form.to_dict()
                
                # 필수 필드 검증
                if required_fields:
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        return error_handler.handle_bad_request(
                            Exception(f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}")
                        )
                
                # 선택적 필드 검증
                if optional_fields:
                    invalid_fields = [field for field in data if field not in required_fields + optional_fields]
                    if invalid_fields:
                        return error_handler.handle_bad_request(
                            Exception(f"유효하지 않은 필드입니다: {', '.join(invalid_fields)}")
                        )
                
                return func(*args, **kwargs)
            except Exception as e:
                return error_handler.handle_generic_error(e)
        return wrapper
    return decorator 