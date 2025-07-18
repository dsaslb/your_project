from models_main import Brand, BrandOnboarding
from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, redirect, url_for, flash
args = None  # pyright: ignore
query = None  # pyright: ignore
"""
브랜드 온보딩 페이지 라우트
"""


brand_onboarding_routes_bp = Blueprint('brand_onboarding_routes', __name__)


@brand_onboarding_routes_bp.route('/admin/brand-onboarding')
@login_required
def brand_onboarding_page():
    """브랜드 온보딩 페이지"""
    try:
        # 브랜드 ID 확인
        brand_id = request.args.get('brand_id', type=int)
        if not brand_id:
            flash('브랜드 ID가 필요합니다.', 'error')
            return redirect(url_for('admin.dashboard'))

        # 브랜드 확인
        brand = Brand.query.get_or_404(brand_id)

        # 권한 확인
        if not current_user.has_permission('brand_management', 'manage') and current_user.brand_id != brand_id:
            flash('권한이 없습니다.', 'error')
            return redirect(url_for('admin.dashboard'))

        # 온보딩 상태 확인
        onboarding = BrandOnboarding.query.filter_by(
            brand_id=brand_id,
            user_id=current_user.id
        ).first()

        return render_template('admin/brand_onboarding.html',
                               brand=brand,
                               onboarding=onboarding)

    except Exception as e:
        flash(f'온보딩 페이지 로드 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))


@brand_onboarding_routes_bp.route('/admin/brand-onboarding/redirect')
@login_required
def redirect_to_onboarding():
    """브랜드 생성 후 온보딩 페이지로 리다이렉트"""
    try:
        brand_id = request.args.get('brand_id', type=int)
        if not brand_id:
            flash('브랜드 ID가 필요합니다.', 'error')
            return redirect(url_for('admin.dashboard'))

        return redirect(url_for('brand_onboarding_routes.brand_onboarding_page', brand_id=brand_id))

    except Exception as e:
        flash(f'리다이렉트 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))
