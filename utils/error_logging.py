import logging
import json
from datetime import datetime
from flask import request, g
from functools import wraps

# 로거 설정
error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.ERROR)

# 파일 핸들러 추가
file_handler = logging.FileHandler('logs/errors.log', encoding='utf-8')
file_handler.setLevel(logging.ERROR)

# 포맷터 설정
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)
error_logger.addHandler(file_handler)

def log_error(error_type, message, details=None, user_id=None):
    """에러 로깅 함수"""
    error_data = {
        'timestamp': datetime.now().isoformat(),
        'error_type': error_type,
        'message': message,
        'details': details,
        'user_id': user_id,
        'request_path': request.path if request else None,
        'request_method': request.method if request else None,
        'user_agent': request.headers.get('User-Agent') if request else None
    }
    
    error_logger.error(json.dumps(error_data, ensure_ascii=False))
    return error_data

def log_permission_error(user_id, required_role, actual_role, resource=None):
    """권한 오류 로깅"""
    message = f"권한 오류: 사용자 {user_id}가 {required_role} 권한이 필요한 작업을 시도했으나 {actual_role} 권한을 가짐"
    if resource:
        message += f" (리소스: {resource})"
    
    return log_error('PERMISSION_ERROR', message, {
        'user_id': user_id,
        'required_role': required_role,
        'actual_role': actual_role,
        'resource': resource
    }, user_id)

def log_data_error(operation, table, error_details, user_id=None):
    """데이터 오류 로깅"""
    message = f"데이터 오류: {operation} 작업 중 {table} 테이블에서 오류 발생"
    
    return log_error('DATA_ERROR', message, {
        'operation': operation,
        'table': table,
        'error_details': error_details
    }, user_id)

def log_plugin_error(plugin_name, operation, error_details, user_id=None):
    """플러그인 오류 로깅"""
    message = f"플러그인 오류: {plugin_name} 플러그인의 {operation} 작업 중 오류 발생"
    
    return log_error('PLUGIN_ERROR', message, {
        'plugin_name': plugin_name,
        'operation': operation,
        'error_details': error_details
    }, user_id)

def error_handler(f):
    """에러 핸들링 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # 에러 로깅
            user_id = getattr(g, 'current_user', {}).id if hasattr(g, 'current_user') and g.current_user else None
            log_error('UNEXPECTED_ERROR', str(e), {
                'function': f.__name__,
                'args': str(args),
                'kwargs': str(kwargs)
            }, user_id)
            
            # 에러 응답 반환
            return {'error': '서버 오류가 발생했습니다. 관리자에게 문의하세요.'}, 500
    
    return decorated_function

def validate_required_fields(data, required_fields):
    """필수 필드 검증"""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)
    
    if missing_fields:
        user_id = getattr(g, 'current_user', {}).id if hasattr(g, 'current_user') and g.current_user else None
        log_error('VALIDATION_ERROR', f"필수 필드 누락: {missing_fields}", {
            'required_fields': required_fields,
            'provided_data': data
        }, user_id)
        return False, missing_fields
    
    return True, []

def check_data_integrity(model, record_id, user_id=None):
    """데이터 무결성 검사"""
    try:
        record = model.query.get(record_id)
        if not record:
            log_data_error('조회', model.__name__, f"ID {record_id}의 레코드를 찾을 수 없음", user_id)
            return False, None
        return True, record
    except Exception as e:
        log_data_error('조회', model.__name__, str(e), user_id)
        return False, None 