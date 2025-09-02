#!/usr/bin/env python3
"""
인증 관련 유틸리티
"""

from functools import wraps
from flask import request, jsonify, current_app
from models import User

def auth_required(f):
    """사용자 인증이 필요한 엔드포인트용 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 실제 구현에서는 JWT 토큰 검증 등을 수행
        # 현재는 테스트용으로 간단한 구현
        
        # Authorization 헤더에서 토큰 추출
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                "error": "Missing Authorization header",
                "message": "인증 헤더가 필요합니다."
            }), 401
        
        # Bearer 토큰 형식 확인
        if not auth_header.startswith('Bearer '):
            return jsonify({
                "error": "Invalid Authorization format",
                "message": "올바른 인증 형식이 아닙니다."
            }), 401
        
        token = auth_header.split(' ')[1]
        
        # 간단한 토큰 검증 (실제로는 JWT 검증 필요)
        if not token or token == 'invalid':
            return jsonify({
                "error": "Invalid token",
                "message": "유효하지 않은 토큰입니다."
            }), 401
        
        # 테스트용 사용자 ID 설정 (실제로는 토큰에서 추출)
        request.user_id = 1  # 테스트용 고정 값
        
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """관리자 권한이 필요한 엔드포인트용 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 먼저 인증 확인
        auth_result = auth_required(lambda: None)()
        if hasattr(auth_result, 'status_code') and auth_result.status_code == 401:
            return auth_result
        
        # 관리자 권한 확인
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return jsonify({
                "error": "User not authenticated",
                "message": "사용자 인증이 필요합니다."
            }), 401
        
        # 사용자 정보 조회 (실제로는 캐시나 세션에서 가져옴)
        # 현재는 테스트용으로 간단하게 처리
        request.user_role = 'admin'  # 테스트용 고정 값
        
        return f(*args, **kwargs)
    
    return decorated_function

def get_current_user():
    """현재 인증된 사용자 정보 반환"""
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        return None
    
    # 실제로는 데이터베이스에서 사용자 정보 조회
    # 현재는 테스트용으로 간단하게 처리
    return {
        'id': user_id,
        'role': getattr(request, 'user_role', 'user')
    }
