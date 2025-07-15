#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모듈/플러그인 개발 페이지 라우트
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 블루프린트 생성
module_plugin_dev_routes_bp = Blueprint('module_plugin_dev_routes', __name__)

def admin_required(f):
    """관리자 권한 확인 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # JWT 토큰에서 사용자 정보 확인
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({"error": "인증이 필요합니다."}), 401
        
        # TODO: 실제 사용자 권한 확인 로직 구현
        # 현재는 모든 인증된 사용자 허용
        return f(*args, **kwargs)
    return decorated_function

@module_plugin_dev_routes_bp.route('/admin/module-plugin-dev')
@jwt_required()
@admin_required
def module_plugin_dev_dashboard():
    """모듈/플러그인 개발 대시보드 페이지"""
    try:
        # 현재 사용자 정보 (실제로는 DB에서 조회)
        current_user = {
            "username": "관리자",
            "role": "admin"
        }
        
        return render_template('admin/module_plugin_dev_dashboard.html', 
                             current_user=current_user)
    except Exception as e:
        logger.error(f"대시보드 페이지 로드 실패: {e}")
        return render_template('errors/500.html'), 500

@module_plugin_dev_routes_bp.route('/admin/module-plugin-dev/editor')
@jwt_required()
@admin_required
def module_plugin_dev_editor():
    """코드 에디터 페이지"""
    try:
        project_path = request.args.get('path')
        if not project_path:
            return jsonify({"error": "프로젝트 경로가 필요합니다."}), 400
        
        current_user = {
            "username": "관리자",
            "role": "admin"
        }
        
        return render_template('admin/module_plugin_dev_editor.html',
                             current_user=current_user,
                             project_path=project_path)
    except Exception as e:
        logger.error(f"에디터 페이지 로드 실패: {e}")
        return render_template('errors/500.html'), 500

@module_plugin_dev_routes_bp.route('/admin/module-plugin-dev/test')
@jwt_required()
@admin_required
def module_plugin_dev_test():
    """테스트 환경 페이지"""
    try:
        current_user = {
            "username": "관리자",
            "role": "admin"
        }
        
        return render_template('admin/module_plugin_dev_test.html',
                             current_user=current_user)
    except Exception as e:
        logger.error(f"테스트 페이지 로드 실패: {e}")
        return render_template('errors/500.html'), 500

@module_plugin_dev_routes_bp.route('/admin/module-plugin-dev/marketplace')
@jwt_required()
@admin_required
def module_plugin_dev_marketplace():
    """통합 마켓플레이스 페이지"""
    try:
        current_user = {
            "username": "관리자",
            "role": "admin"
        }
        
        return render_template('admin/module_plugin_dev_marketplace.html',
                             current_user=current_user)
    except Exception as e:
        logger.error(f"마켓플레이스 페이지 로드 실패: {e}")
        return render_template('errors/500.html'), 500 