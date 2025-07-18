from functools import wraps
from flask_login import login_required, current_user
from flask import Blueprint, render_template

args = None  # pyright: ignore
"""
플러그인 관리 페이지 라우트
"""


plugin_management_page_bp = Blueprint("plugin_management_page", __name__)


def admin_required(f):
    """관리자 권한 확인 데코레이터"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return render_template("errors/403.html"), 403

        if current_user.role not in ["admin", "super_admin"]:
            return render_template("errors/403.html"), 403

        return f(*args, **kwargs)

    return decorated_function


@plugin_management_page_bp.route("/admin/plugins")
@login_required
@admin_required
def plugin_management():
    """플러그인 관리 페이지"""
    return render_template("admin/plugin_management.html")
