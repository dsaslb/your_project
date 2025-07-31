# -*- coding: utf-8 -*-
"""
백엔드 개발 요청서 - 데이터 생성/변경/권한 정책 시스템

기본 원칙:
1. 모든 데이터 생성/변경/삭제는 "프론트엔드(권한·정책 적용 UI) → 백엔드 API → DB" 구조로만 진행
2. 실사용자/운영자는 프론트엔드에서만 생성/변경 가능
3. 백엔드는 API·정책·감사로그·알림 등 "서비스 로직"만 담당

예외(최상위 관리자 한정):
- 최상위 관리자(admin/admin123)만 "백엔드 운영툴"에서 데이터 직접 생성·변경 가능
- 모든 액션에 별도의 감사로그 자동 기록 필수
- 예외 권한은 코드 상에 별도 플래그/설정으로만 허용
"""

import os
import logging
import datetime
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Dict, Any, List
from flask import request, jsonify, current_app, g
from flask_login import current_user

# 감사 로그 시스템 import
try:
    from security.audit_logger import AuditLogger, EventType, SecurityLevel, AuditEvent
    AUDIT_LOGGER_AVAILABLE = True
except ImportError:
    AUDIT_LOGGER_AVAILABLE = False
    print("경고: 감사 로그 시스템을 불러올 수 없습니다.")

logger = logging.getLogger(__name__)

# === 권한 정책 설정 ===
SUPER_ADMIN_CREDENTIALS = {
    'username': 'admin',
    'password': 'admin123'
}

# 예외 권한 플래그 (최상위 관리자만 백엔드 직접 조작 가능)
SUPER_ADMIN_BACKEND_ACCESS = True  # 최상위 관리자 백엔드 접근 허용
SUPER_ADMIN_AUDIT_REQUIRED = True  # 최상위 관리자 액션 감사로그 필수

# 프론트엔드 도메인 설정
FRONTEND_DOMAINS = [
    'http://localhost:3000',
    'http://192.168.45.44:3000',
    'https://your-frontend-domain.com'  # 실제 프론트엔드 도메인으로 변경
]

# 감사 로그 시스템 초기화
audit_logger = AuditLogger() if AUDIT_LOGGER_AVAILABLE else None

class AuthorizationPolicy:
    """권한 정책 관리 클래스"""
    
    def __init__(self):
        self.super_admin_credentials = SUPER_ADMIN_CREDENTIALS
        self.super_admin_backend_access = SUPER_ADMIN_BACKEND_ACCESS
        self.super_admin_audit_required = SUPER_ADMIN_AUDIT_REQUIRED
        self.frontend_domains = FRONTEND_DOMAINS
        self.audit_logger = audit_logger
    
    def is_super_admin(self, user) -> bool:
        """최상위 관리자 확인"""
        if not user or not user.is_authenticated:
            return False
        return (user.username == self.super_admin_credentials['username'] and 
                user.role == 'admin')
    
    def validate_frontend_request(self) -> bool:
        """프론트엔드 요청 검증"""
        # 최상위 관리자는 백엔드 직접 접근 가능
        if self.is_super_admin(current_user):
            return True
        
        # 일반 사용자는 프론트엔드를 통해서만 접근 가능
        referer = request.headers.get('Referer', '')
        origin = request.headers.get('Origin', '')
        
        is_frontend_request = any(
            domain in referer or domain in origin 
            for domain in self.frontend_domains
        )
        
        if not is_frontend_request:
            self._log_access_denied(
                "프론트엔드를 통하지 않은 백엔드 직접 접근 시도",
                {
                    "referer": referer,
                    "origin": origin,
                    "user_role": current_user.role if current_user.is_authenticated else "anonymous"
                }
            )
            return False
        
        return True
    
    def audit_data_operation(self, operation_type: str, model_name: str, 
                           object_id: Optional[int] = None, details: Optional[Dict] = None):
        """데이터 작업 감사 로그 기록"""
        if not current_user.is_authenticated or not self.audit_logger:
            return
        
        event_type_map = {
            'create': EventType.DATA_MODIFIED,
            'update': EventType.DATA_MODIFIED,
            'delete': EventType.DATA_DELETED,
            'access': EventType.DATA_ACCESSED
        }
        
        security_level = SecurityLevel.HIGH if self.is_super_admin(current_user) else SecurityLevel.MEDIUM
        
        self.audit_logger.log_event(
            event_type=event_type_map.get(operation_type, EventType.DATA_MODIFIED),
            security_level=security_level,
            user_id=current_user.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            resource=f"{model_name}:{object_id}" if object_id else model_name,
            action=operation_type,
            details={
                "operation_type": operation_type,
                "model_name": model_name,
                "object_id": object_id,
                "is_super_admin": self.is_super_admin(current_user),
                "request_data": request.get_json() if request.is_json else None,
                **(details or {})
            },
            success=True
        )
    
    def _log_access_denied(self, message: str, details: Optional[Dict] = None):
        """접근 거부 로그 기록"""
        if not self.audit_logger:
            return
        
        self.audit_logger.log_event(
            event_type=EventType.ACCESS_DENIED,
            security_level=SecurityLevel.MEDIUM,
            user_id=current_user.id if current_user.is_authenticated else None,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            resource=request.endpoint,
            action="backend_direct_access_attempt",
            details={
                "message": message,
                "user_role": current_user.role if current_user.is_authenticated else "anonymous",
                **(details or {})
            },
            success=False
        )

# 전역 권한 정책 인스턴스
auth_policy = AuthorizationPolicy()

# === 데코레이터 함수들 ===

def require_super_admin(f):
    """최상위 관리자 권한 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not auth_policy.is_super_admin(current_user):
            # 감사 로그 기록
            auth_policy._log_access_denied(
                "최상위 관리자 권한이 필요한 작업 시도",
                {
                    "request_data": request.get_json() if request.is_json else None
                }
            )
            return jsonify({"error": "최상위 관리자 권한이 필요합니다."}), 403
        return f(*args, **kwargs)
    return decorated_function

def require_frontend_request(f):
    """프론트엔드 요청 검증 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not auth_policy.validate_frontend_request():
            return jsonify({"error": "프론트엔드를 통한 접근이 필요합니다."}), 403
        return f(*args, **kwargs)
    return decorated_function

def audit_operation(operation_type: str, model_name: str):
    """데이터 작업 감사 로그 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 함수 실행 전
            result = f(*args, **kwargs)
            
            # 함수 실행 후 감사 로그 기록
            try:
                # 응답에서 생성된 객체 ID 추출 시도
                object_id = None
                if hasattr(result, 'json') and callable(result.json):
                    response_data = result.json
                    if isinstance(response_data, dict):
                        object_id = response_data.get('id') or response_data.get('object_id')
                
                auth_policy.audit_data_operation(
                    operation_type=operation_type,
                    model_name=model_name,
                    object_id=object_id,
                    details={
                        "endpoint": request.endpoint,
                        "method": request.method,
                        "user_id": current_user.id if current_user.is_authenticated else None
                    }
                )
            except Exception as e:
                logger.error(f"감사 로그 기록 실패: {e}")
            
            return result
        return decorated_function
    return decorator

# === API 엔드포인트 보호 함수들 ===

def protect_data_creation_endpoint(model_name: str):
    """데이터 생성 엔드포인트 보호"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 최상위 관리자이거나 프론트엔드 요청인지 확인
            if not (auth_policy.is_super_admin(current_user) or 
                   auth_policy.validate_frontend_request()):
                return jsonify({"error": "권한이 없습니다."}), 403
            
            # 감사 로그 기록
            auth_policy.audit_data_operation(
                operation_type='create',
                model_name=model_name,
                details={
                    "endpoint": request.endpoint,
                    "method": request.method
                }
            )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def protect_data_modification_endpoint(model_name: str):
    """데이터 수정 엔드포인트 보호"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 최상위 관리자이거나 프론트엔드 요청인지 확인
            if not (auth_policy.is_super_admin(current_user) or 
                   auth_policy.validate_frontend_request()):
                return jsonify({"error": "권한이 없습니다."}), 403
            
            # 감사 로그 기록
            object_id = kwargs.get('id') or kwargs.get('object_id')
            auth_policy.audit_data_operation(
                operation_type='update',
                model_name=model_name,
                object_id=object_id,
                details={
                    "endpoint": request.endpoint,
                    "method": request.method
                }
            )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def protect_data_deletion_endpoint(model_name: str):
    """데이터 삭제 엔드포인트 보호"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 최상위 관리자이거나 프론트엔드 요청인지 확인
            if not (auth_policy.is_super_admin(current_user) or 
                   auth_policy.validate_frontend_request()):
                return jsonify({"error": "권한이 없습니다."}), 403
            
            # 감사 로그 기록
            object_id = kwargs.get('id') or kwargs.get('object_id')
            auth_policy.audit_data_operation(
                operation_type='delete',
                model_name=model_name,
                object_id=object_id,
                details={
                    "endpoint": request.endpoint,
                    "method": request.method
                }
            )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# === 유틸리티 함수들 ===

def get_audit_summary(days: int = 30) -> Dict[str, Any]:
    """감사 로그 요약 정보 반환"""
    if not auth_policy.audit_logger:
        return {"error": "감사 로그 시스템이 사용할 수 없습니다."}
    
    try:
        return auth_policy.audit_logger.get_security_summary(days=days)
    except Exception as e:
        logger.error(f"감사 로그 요약 조회 실패: {e}")
        return {"error": "감사 로그 요약 조회에 실패했습니다."}

def cleanup_old_audit_logs(days: int = 90):
    """오래된 감사 로그 정리"""
    if not auth_policy.audit_logger:
        return
    
    try:
        auth_policy.audit_logger.cleanup_old_logs(days=days)
        logger.info(f"{days}일 이전 감사 로그 정리 완료")
    except Exception as e:
        logger.error(f"감사 로그 정리 실패: {e}")

# === 설정 검증 함수 ===

def validate_policy_configuration() -> Dict[str, Any]:
    """권한 정책 설정 검증"""
    config_status = {
        "super_admin_backend_access": auth_policy.super_admin_backend_access,
        "super_admin_audit_required": auth_policy.super_admin_audit_required,
        "audit_logger_available": AUDIT_LOGGER_AVAILABLE,
        "frontend_domains": auth_policy.frontend_domains,
        "super_admin_credentials": {
            "username": auth_policy.super_admin_credentials['username'],
            "password_set": bool(auth_policy.super_admin_credentials['password'])
        }
    }
    
    # 설정 검증
    warnings = []
    if not AUDIT_LOGGER_AVAILABLE:
        warnings.append("감사 로그 시스템이 사용할 수 없습니다.")
    
    if not auth_policy.frontend_domains:
        warnings.append("프론트엔드 도메인이 설정되지 않았습니다.")
    
    config_status["warnings"] = warnings
    config_status["valid"] = len(warnings) == 0
    
    return config_status 