from flask import Blueprint, render_template
from flask_login import login_required, current_user

staff_bp = Blueprint("routes_staff", __name__)


@staff_bp.route("/staff")
@login_required
def staff():
    """직원 관리 메인 페이지"""
    return render_template("staff.html", user=current_user)
