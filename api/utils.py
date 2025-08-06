"""
API 공통 유틸리티 함수들
표준화된 응답 형식, 에러 처리, 로깅, 입력 검증을 제공
"""

import logging
import traceback
from functools import wraps
from flask import jsonify, request, g
from typing import Dict, Any, Optional, Union, List
import re
import json
from datetime import datetime

# 로거 설정
logger = logging.getLogger(__name__)

class APIResponse:
    """표준화된 API 응답 클래스"""
    
    @staticmethod
    def success(data: Any = None, message: str = "성공", code: int = 200) -> tuple:
        """성공 응답"""
        response = {
            "status": "success",
            "message": message,
            "code": code,
            "timestamp": datetime.now().isoformat()
        }
        if data is not None:
            response["data"] = data
        return jsonify(response), code
    
    @staticmethod
    def error(message: str, code: int = 400, details: Any = None) -> tuple:
        """에러 응답"""
        response = {
            "status": "error",
            "message": message,
            "code": code,
            "timestamp": datetime.now().isoformat()
        }
        if details is not None:
            response["details"] = details
        return jsonify(response), code
    
    @staticmethod
    def validation_error(errors: List[str], code: int = 422) -> tuple:
        """검증 에러 응답"""
        return APIResponse.error(
            message="입력 데이터 검증 실패",
            code=code,
            details={"validation_errors": errors}
        )

class InputValidator:
    """입력 데이터 검증 클래스"""
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """필수 필드 검증"""
        errors = []
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                errors.append(f"필수 필드 '{field}'가 누락되었습니다")
        return errors
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """이메일 형식 검증"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """전화번호 형식 검증"""
        pattern = r'^[0-9-+\s()]{10,15}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_password(password: str, min_length: int = 8) -> List[str]:
        """비밀번호 강도 검증"""
        errors = []
        if len(password) < min_length:
            errors.append(f"비밀번호는 최소 {min_length}자 이상이어야 합니다")
        if not re.search(r'[A-Z]', password):
            errors.append("비밀번호에 대문자가 포함되어야 합니다")
        if not re.search(r'[a-z]', password):
            errors.append("비밀번호에 소문자가 포함되어야 합니다")
        if not re.search(r'\d', password):
            errors.append("비밀번호에 숫자가 포함되어야 합니다")
        return errors
    
    @staticmethod
    def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
        """JSON 스키마 검증"""
        errors = []
        for field, rules in schema.items():
            if field in data:
                value = data[field]
                if 'type' in rules:
                    if not isinstance(value, rules['type']):
                        errors.append(f"'{field}' 필드의 타입이 올바르지 않습니다")
                if 'min_length' in rules and isinstance(value, str):
                    if len(value) < rules['min_length']:
                        errors.append(f"'{field}' 필드는 최소 {rules['min_length']}자 이상이어야 합니다")
                if 'max_length' in rules and isinstance(value, str):
                    if len(value) > rules['max_length']:
                        errors.append(f"'{field}' 필드는 최대 {rules['max_length']}자까지 가능합니다")
                if 'pattern' in rules and isinstance(value, str):
                    if not re.match(rules['pattern'], value):
                        errors.append(f"'{field}' 필드의 형식이 올바르지 않습니다")
        return errors

def api_error_handler(f):
    """API 에러 처리 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"Validation error in {f.__name__}: {str(e)}")
            return APIResponse.error(str(e), 400)
        except PermissionError as e:
            logger.warning(f"Permission error in {f.__name__}: {str(e)}")
            return APIResponse.error("권한이 없습니다", 403)
        except FileNotFoundError as e:
            logger.warning(f"Resource not found in {f.__name__}: {str(e)}")
            return APIResponse.error("리소스를 찾을 수 없습니다", 404)
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            return APIResponse.error("서버 내부 오류가 발생했습니다", 500)
    return decorated_function

def log_api_request(f):
    """API 요청 로깅 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = datetime.now()
        user_id = getattr(g, 'current_user', {}).get('user_id', 'anonymous')
        
        logger.info(f"API Request: {request.method} {request.url} by user {user_id}")
        logger.debug(f"Request headers: {dict(request.headers)}")
        
        try:
            result = f(*args, **kwargs)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"API Response: {request.method} {request.url} - {result[1]} ({duration:.3f}s)")
            return result
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.error(f"API Error: {request.method} {request.url} - {str(e)} ({duration:.3f}s)")
            raise
    return decorated_function

def validate_json_input(schema: Optional[Dict[str, Any]] = None, required_fields: Optional[List[str]] = None):
    """JSON 입력 검증 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return APIResponse.error("JSON 형식의 데이터가 필요합니다", 400)
            
            data = request.get_json()
            if data is None:
                return APIResponse.error("유효하지 않은 JSON 데이터입니다", 400)
            
            errors = []
            
            # 필수 필드 검증
            if required_fields:
                errors.extend(InputValidator.validate_required_fields(data, required_fields))
            
            # 스키마 검증
            if schema:
                errors.extend(InputValidator.validate_json_schema(data, schema))
            
            if errors:
                return APIResponse.validation_error(errors)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def paginate_response(data: List[Any], page: int = 1, per_page: int = 20) -> Dict[str, Any]:
    """페이지네이션 응답 생성"""
    total = len(data)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    paginated_data = data[start_idx:end_idx]
    
    return {
        "items": paginated_data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
            "has_next": end_idx < total,
            "has_prev": page > 1
        }
    }

def sanitize_input(data: Union[str, Dict[str, Any]]) -> Union[str, Dict[str, Any]]:
    """입력 데이터 정제 (XSS 방지)"""
    if isinstance(data, str):
        # HTML 태그 제거
        import html
        return html.escape(data.strip())
    elif isinstance(data, dict):
        return {key: sanitize_input(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    else:
        return data

def get_client_ip() -> str:
    """클라이언트 IP 주소 가져오기"""
    # 프록시 환경 고려
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def get_user_agent() -> str:
    """사용자 에이전트 가져오기"""
    return request.headers.get('User-Agent', 'Unknown')

def rate_limit_key() -> str:
    """Rate limiting을 위한 키 생성"""
    user_id = getattr(g, 'current_user', {}).get('user_id', 'anonymous')
    return f"{user_id}:{get_client_ip()}:{request.endpoint}"

# 기존 함수들 유지
def get_user_info():
    """사용자 정보 가져오기"""
    return g.current_user if hasattr(g, 'current_user') else None

def require_auth(f):
    """인증 필요 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_user'):
            return APIResponse.error("인증이 필요합니다", 401)
        return f(*args, **kwargs)
    return decorated_function

def require_permission(permission_name: str):
    """권한 필요 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_info = get_user_info()
            if not user_info:
                return APIResponse.error("인증이 필요합니다", 401)
            
            # 권한 검증 로직 (실제 구현에 맞게 수정 필요)
            permissions = user_info.get('permissions', {})
            if not permissions.get(permission_name, {}).get('view', False):
                return APIResponse.error("권한이 없습니다", 403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
