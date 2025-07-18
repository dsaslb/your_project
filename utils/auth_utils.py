#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import wraps
from flask import request, jsonify, g
from flask_login import current_user
import logging

logger = logging.getLogger(__name__)

def admin_required(f):
    """관리자 권한이 필요한 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': '로그인이 필요합니다'}), 401
        
        if not hasattr(current_user, 'role') or current_user.role not in ['admin', 'super_admin']:
            return jsonify({'error': '관리자 권한이 필요합니다'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission):
    """특정 권한이 필요한 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': '로그인이 필요합니다'}), 401
            
            if not hasattr(current_user, 'role'):
                return jsonify({'error': '권한이 없습니다'}), 403
            
            # 권한 체크 로직
            if current_user.role == 'super_admin':
                return f(*args, **kwargs)
            
            if current_user.role == 'admin' and permission in ['admin', 'manager', 'employee']:
                return f(*args, **kwargs)
            
            if current_user.role == 'manager' and permission in ['manager', 'employee']:
                return f(*args, **kwargs)
            
            if current_user.role == 'employee' and permission == 'employee':
                return f(*args, **kwargs)
            
            return jsonify({'error': '권한이 없습니다'}), 403
        
        return decorated_function
    return decorator

def brand_manager_required(f):
    """브랜드 매니저 권한이 필요한 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': '로그인이 필요합니다'}), 401
        
        if not hasattr(current_user, 'role') or current_user.role not in ['brand_manager', 'admin', 'super_admin']:
            return jsonify({'error': '브랜드 매니저 권한이 필요합니다'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def store_manager_required(f):
    """매장 매니저 권한이 필요한 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': '로그인이 필요합니다'}), 401
        
        if not hasattr(current_user, 'role') or current_user.role not in ['store_manager', 'brand_manager', 'admin', 'super_admin']:
            return jsonify({'error': '매장 매니저 권한이 필요합니다'}), 403
        
        return f(*args, **kwargs)
    return decorated_function 