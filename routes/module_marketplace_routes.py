"""
모듈 마켓플레이스 라우트
HTML 템플릿을 렌더링하는 라우트
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 블루프린트 생성
module_marketplace_routes_bp = Blueprint('module_marketplace_routes', __name__)

@module_marketplace_routes_bp.route('/module-marketplace')
@login_required
def module_marketplace():
    """모듈 마켓플레이스 페이지"""
    try:
        # 사용자 권한 확인
        if not current_user.has_permission('module_management', 'view'):
            flash('모듈 마켓플레이스에 접근할 권한이 없습니다.', 'error')
            return redirect(url_for('dashboard'))
        
        return render_template('module_marketplace.html')
        
    except Exception as e:
        logger.error(f"모듈 마켓플레이스 페이지 로드 실패: {e}")
        flash('페이지를 불러오는데 실패했습니다.', 'error')
        return redirect(url_for('dashboard'))

@module_marketplace_routes_bp.route('/module-marketplace/installed')
@login_required
def installed_modules():
    """설치된 모듈 관리 페이지"""
    try:
        # 사용자 권한 확인
        if not current_user.has_permission('module_management', 'view'):
            flash('설치된 모듈 관리에 접근할 권한이 없습니다.', 'error')
            return redirect(url_for('dashboard'))
        
        return render_template('installed_modules.html')
        
    except Exception as e:
        logger.error(f"설치된 모듈 관리 페이지 로드 실패: {e}")
        flash('페이지를 불러오는데 실패했습니다.', 'error')
        return redirect(url_for('dashboard'))

@module_marketplace_routes_bp.route('/module-marketplace/statistics')
@login_required
def module_statistics():
    """모듈 통계 페이지"""
    try:
        # 사용자 권한 확인
        if not current_user.has_permission('module_management', 'view'):
            flash('모듈 통계에 접근할 권한이 없습니다.', 'error')
            return redirect(url_for('dashboard'))
        
        return render_template('module_statistics.html')
        
    except Exception as e:
        logger.error(f"모듈 통계 페이지 로드 실패: {e}")
        flash('페이지를 불러오는데 실패했습니다.', 'error')
        return redirect(url_for('dashboard')) 